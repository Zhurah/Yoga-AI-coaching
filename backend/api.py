# API Flask pour le système de coaching yoga
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import cv2
import mediapipe as mp
from yoga_quality_analyzer import YogaPoseQualityAnalyzer
import os
from pathlib import Path

# Imports pour l'authentification et le profil
from models import db, init_db, User, PoseSession, UserProfile
from auth import jwt, register_auth_routes, get_current_user_id, JWT_ACCESS_TOKEN_EXPIRES, JWT_REFRESH_TOKEN_EXPIRES
from profile_routes import register_profile_routes
from datetime import timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from jwt.exceptions import InvalidTokenError

app = Flask(__name__)

# ============================================================================
# CONFIGURATION DE L'APPLICATION
# ============================================================================

# Configuration CORS
CORS(app,
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True)

# Configuration Base de Données SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yoga_coaching.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration JWT (Sécurité des tokens)
app.config['JWT_SECRET_KEY'] = 'CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR'  # À changer en production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = JWT_REFRESH_TOKEN_EXPIRES
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Tokens dans les headers HTTP

# Initialiser la base de données et JWT
init_db(app)
jwt.init_app(app)

# Enregistrer les routes d'authentification et de profil
register_auth_routes(app)
register_profile_routes(app)

# Charger les modèles au démarrage
print("="*70)
print("🚀 DÉMARRAGE DE L'API YOGA COACHING")
print("="*70)

try:
    model = joblib.load('best_yoga_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
    print("✅ Modèles ML chargés avec succès")
except FileNotFoundError as e:
    print(f"❌ Erreur: {e}")
    print("Exécutez d'abord best_model.ipynb pour générer les modèles")
    exit(1)

# Initialiser l'analyseur de qualité
analyzer = YogaPoseQualityAnalyzer()
print("✅ Analyseur de qualité initialisé")

# Initialiser MediaPipe
mp_pose = mp.solutions.pose

# Fonctions utilitaires (copier depuis test_system.py)
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def calculate_distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def engineer_features(keypoints_raw):
    """Feature engineering à partir des keypoints bruts"""
    if keypoints_raw is None or len(keypoints_raw) != 132:
        return None
    
    landmarks = keypoints_raw.reshape(33, 4)
    features = []
    
    # Points clés
    key_indices = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    for idx in key_indices:
        features.extend(landmarks[idx, :3])
    
    # Angles
    left_shoulder = landmarks[11, :3]
    left_elbow = landmarks[13, :3]
    left_wrist = landmarks[15, :3]
    features.append(calculate_angle(left_shoulder, left_elbow, left_wrist))
    
    right_shoulder = landmarks[12, :3]
    right_elbow = landmarks[14, :3]
    right_wrist = landmarks[16, :3]
    features.append(calculate_angle(right_shoulder, right_elbow, right_wrist))
    
    left_hip = landmarks[23, :3]
    features.append(calculate_angle(left_hip, left_shoulder, left_elbow))
    
    right_hip = landmarks[24, :3]
    features.append(calculate_angle(right_hip, right_shoulder, right_elbow))
    
    left_knee = landmarks[25, :3]
    left_ankle = landmarks[27, :3]
    features.append(calculate_angle(left_hip, left_knee, left_ankle))
    
    right_knee = landmarks[26, :3]
    right_ankle = landmarks[28, :3]
    features.append(calculate_angle(right_hip, right_knee, right_ankle))
    
    nose = landmarks[0, :3]
    features.append(calculate_angle(left_knee, left_hip, nose))
    features.append(calculate_angle(right_knee, right_hip, nose))
    
    # Distances
    features.append(calculate_distance(left_shoulder, right_shoulder))
    features.append(calculate_distance(left_hip, right_hip))
    
    mid_hip = (landmarks[23, :3] + landmarks[24, :3]) / 2
    features.append(calculate_distance(nose, mid_hip))
    
    features.append(calculate_distance(left_wrist, left_ankle))
    features.append(calculate_distance(right_wrist, right_ankle))
    
    # Ratios
    shoulder_width = calculate_distance(left_shoulder, right_shoulder)
    hip_width = calculate_distance(left_hip, right_hip)
    features.append(shoulder_width / (hip_width + 1e-6))
    features.append(abs(nose[1] - mid_hip[1]))
    features.append(calculate_distance(left_ankle, right_ankle))
    
    # Visibilité
    features.append(np.mean(landmarks[:, 3]))
    
    return np.array(features)

# ============================================================================
# ROUTES API
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0",
        "models_loaded": True
    })

@app.route('/api/poses', methods=['GET'])
def get_poses():
    """Retourne la liste des poses disponibles"""
    return jsonify({
        "poses": list(label_encoder.classes_),
        "count": len(label_encoder.classes_)
    })

@app.route('/api/classify', methods=['POST'])
def classify_pose():
    """
    Classifie une pose à partir des landmarks MediaPipe
    
    Body JSON:
    {
        "landmarks": [[x, y, z, visibility], ...] // 33 landmarks
    }
    """
    try:
        data = request.json
        landmarks_list = data.get('landmarks')
        
        if not landmarks_list or len(landmarks_list) != 33:
            return jsonify({
                "success": False,
                "error": "33 landmarks requis"
            }), 400
        
        # Convertir en numpy array
        landmarks_flat = []
        for lm in landmarks_list:
            landmarks_flat.extend([lm['x'], lm['y'], lm['z'], lm['visibility']])
        
        keypoints_raw = np.array(landmarks_flat)
        
        # Feature engineering
        features = engineer_features(keypoints_raw)
        
        if features is None:
            return jsonify({
                "success": False,
                "error": "Erreur lors de l'extraction des features"
            }), 400
        
        # Prédiction
        features_reshaped = features.reshape(1, -1)
        features_scaled = scaler.transform(features_reshaped)  # ✅ Normalisation!
        prediction = model.predict(features_scaled)[0]
        pose_name = label_encoder.inverse_transform([prediction])[0]

        # Probabilités
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_scaled)[0]
            confidence = float(probabilities[prediction])
            all_probabilities = {
                cls: float(prob) 
                for cls, prob in zip(label_encoder.classes_, probabilities)
            }
        else:
            confidence = 1.0
            all_probabilities = None
        
        return jsonify({
            "success": True,
            "pose": pose_name,
            "confidence": confidence,
            "all_probabilities": all_probabilities
        })
        
    except Exception as e:
        print(f"❌ Erreur classification: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_pose_quality():
    """
    Analyse la qualité d'une pose
    
    Body JSON:
    {
        "landmarks": [[x, y, z, visibility], ...],
        "pose_name": "plank",
        "user_level": "intermediate" // optionnel
    }
    """
    try:
        data = request.json
        landmarks_list = data.get('landmarks')
        pose_name = data.get('pose_name')
        user_level = data.get('user_level', 'intermediate')
        
        if not landmarks_list or not pose_name:
            return jsonify({
                "success": False,
                "error": "landmarks et pose_name requis"
            }), 400
        
        # Convertir en numpy array (33, 4)
        landmarks_array = np.array([
            [lm['x'], lm['y'], lm['z'], lm['visibility']]
            for lm in landmarks_list
        ])
        
        # Analyser la qualité avec calcul du global_score
        analysis = analyzer.analyze_pose(pose_name, landmarks_array, include_global_score=True)

        # Calculer le score global
        if 'indicators' in analysis:
            # Utiliser le global_score calculé par l'analyzer
            global_score = analysis.get('global_score', sum(analysis['indicators'].values()) / len(analysis['indicators']))

            # Encouragement personnalisé
            encouragement = get_encouragement(global_score, user_level)

            return jsonify({
                "success": True,
                "pose": pose_name,
                "indicators": analysis['indicators'],
                "global_score": global_score,
                "skill_level": analysis.get('skill_level'),
                "priority_indicator": analysis.get('priority_indicator'),
                "recommended_exercise": analysis.get('recommended_exercise'),
                "feedback": analysis['feedback'],
                "encouragement": encouragement
            })
        else:
            return jsonify({
                "success": False,
                "error": analysis.get('error', 'Analyse impossible')
            }), 400
        
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/complete-analysis', methods=['POST'])
def complete_analysis():
    """
    Analyse complète : Classification + Qualité
    Enregistre automatiquement la session si l'utilisateur est connecté

    Body JSON:
    {
        "landmarks": [[x, y, z, visibility], ...],
        "user_level": "intermediate"
    }
    """
    try:
        data = request.json
        landmarks_list = data.get('landmarks')
        user_level = data.get('user_level', 'intermediate')

        # Vérifier si l'utilisateur est authentifié (optionnel)
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            identity = get_jwt_identity()
            if identity:
                user_id = int(identity)
        except (InvalidTokenError, Exception):
            pass  # Utilisateur non authentifié, continuer l'analyse

        # 1. Classification
        classify_result = classify_pose_internal(landmarks_list)

        if not classify_result['success']:
            return jsonify(classify_result), 400

        pose_name = classify_result['pose']
        confidence = classify_result['confidence']

        # 2. Analyse qualitative si confiance suffisante
        quality_result = None
        if confidence >= 0.7:
            landmarks_array = np.array([
                [lm['x'], lm['y'], lm['z'], lm['visibility']]
                for lm in landmarks_list
            ])

            analysis = analyzer.analyze_pose(pose_name, landmarks_array, include_global_score=True)

            if 'indicators' in analysis:
                # Utiliser le global_score calculé par l'analyzer
                global_score = analysis.get('global_score', sum(analysis['indicators'].values()) / len(analysis['indicators']))

                quality_result = {
                    "indicators": analysis['indicators'],
                    "global_score": global_score,
                    "skill_level": analysis.get('skill_level'),
                    "priority_indicator": analysis.get('priority_indicator'),
                    "recommended_exercise": analysis.get('recommended_exercise'),
                    "feedback": analysis['feedback'],
                    "encouragement": get_encouragement(global_score, user_level)
                }

                # 3. ENREGISTRER LA SESSION si utilisateur authentifié
                if user_id and quality_result:
                    try:
                        session = PoseSession(
                            user_id=user_id,
                            pose_name=pose_name,
                            confidence=confidence,
                            global_score=global_score
                        )
                        session.set_indicators(analysis['indicators'])
                        session.set_feedback(analysis['feedback'])
                        session.priority_indicator = analysis.get('priority_indicator')
                        session.recommended_exercise = analysis.get('recommended_exercise')

                        db.session.add(session)
                        db.session.commit()

                        # Mettre à jour le profil utilisateur
                        update_user_profile(user_id, pose_name, global_score)

                        print(f"✅ Session enregistrée pour user_id={user_id}, pose={pose_name}, score={global_score:.1f}")

                    except Exception as e:
                        db.session.rollback()
                        print(f"⚠️ Erreur lors de l'enregistrement de la session: {e}")
                        # Ne pas bloquer l'analyse si l'enregistrement échoue

        return jsonify({
            "success": True,
            "classification": {
                "pose": pose_name,
                "confidence": confidence,
                "all_probabilities": classify_result.get('all_probabilities')
            },
            "quality_analysis": quality_result
        })

    except Exception as e:
        print(f"❌ Erreur analyse complète: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def classify_pose_internal(landmarks_list):
    """Fonction interne de classification"""
    try:
        landmarks_flat = []
        for lm in landmarks_list:
            landmarks_flat.extend([lm['x'], lm['y'], lm['z'], lm['visibility']])
        
        keypoints_raw = np.array(landmarks_flat)
        features = engineer_features(keypoints_raw)
        
        if features is None:
            return {"success": False, "error": "Feature extraction failed"}
        
        features_reshaped = features.reshape(1, -1)
        features_scaled = scaler.transform(features_reshaped)  # ✅ Normalisation!
        prediction = model.predict(features_scaled)[0]
        pose_name = label_encoder.inverse_transform([prediction])[0]

        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_scaled)[0]
            confidence = float(probabilities[prediction])
            all_probabilities = {
                cls: float(prob) 
                for cls, prob in zip(label_encoder.classes_, probabilities)
            }
        else:
            confidence = 1.0
            all_probabilities = None
        
        return {
            "success": True,
            "pose": pose_name,
            "confidence": confidence,
            "all_probabilities": all_probabilities
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_encouragement(score, level):
    """Génère un message d'encouragement personnalisé"""
    if level == "beginner":
        if score >= 70:
            return "🌟 Excellent travail pour un débutant ! Continuez comme ça."
        elif score >= 50:
            return "💪 Bon début ! Chaque pratique vous rapproche de la maîtrise."
        else:
            return "🌱 C'est un début. Concentrez-vous sur un point à la fois."
    elif level == "intermediate":
        if score >= 85:
            return "🔥 Très bonne maîtrise ! Affinez les détails."
        elif score >= 70:
            return "✓ Solide exécution. Travaillez les points d'amélioration."
        else:
            return "💡 Revenez aux bases pour consolider la posture."
    else:  # advanced
        if score >= 90:
            return "🏆 Maîtrise parfaite ! Vous pouvez enseigner cette pose."
        elif score >= 80:
            return "⭐ Excellent niveau. Peaufinez les micro-ajustements."
        else:
            return "🎯 Analysez chaque détail pour atteindre la perfection."

def update_user_profile(user_id, pose_name, global_score):
    """
    Met à jour les statistiques du profil utilisateur après une session

    Args:
        user_id: ID de l'utilisateur
        pose_name: Nom de la pose analysée
        global_score: Score global obtenu
    """
    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()

        if not profile:
            # Créer le profil s'il n'existe pas
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)

        # Récupérer toutes les sessions de l'utilisateur
        all_sessions = PoseSession.query.filter_by(user_id=user_id).all()

        # Calculer les statistiques globales
        profile.total_sessions = len(all_sessions)

        if all_sessions:
            # Score moyen global
            profile.average_global_score = sum(s.global_score for s in all_sessions) / len(all_sessions)

            # Statistiques par pose
            pose_scores = {}
            for session in all_sessions:
                if session.pose_name not in pose_scores:
                    pose_scores[session.pose_name] = []
                pose_scores[session.pose_name].append(session.global_score)

            # Calculer la moyenne par pose
            pose_averages = {
                pose: sum(scores) / len(scores)
                for pose, scores in pose_scores.items()
            }

            # Meilleure et pire pose
            if pose_averages:
                best_pose = max(pose_averages.items(), key=lambda x: x[1])
                worst_pose = min(pose_averages.items(), key=lambda x: x[1])

                profile.best_pose = best_pose[0]
                profile.best_pose_score = best_pose[1]
                profile.worst_pose = worst_pose[0]
                profile.worst_pose_score = worst_pose[1]

        db.session.commit()
        print(f"✅ Profil mis à jour: {profile.total_sessions} sessions, score moyen: {profile.average_global_score:.1f}")

    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Erreur mise à jour profil: {e}")
        raise

# ============================================================================
# DÉMARRAGE
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 API démarrée sur http://localhost:8000")
    print("="*70)
    print("\n📋 Endpoints disponibles:")
    print("\n   🔐 AUTHENTIFICATION:")
    print("      POST /api/auth/register")
    print("      POST /api/auth/login")
    print("      POST /api/auth/refresh")
    print("      GET  /api/auth/me")
    print("      POST /api/auth/logout")
    print("\n   👤 PROFIL UTILISATEUR:")
    print("      GET  /api/profile")
    print("      GET  /api/profile/history")
    print("      GET  /api/profile/statistics")
    print("      GET  /api/profile/pose-progress/<pose>")
    print("      DELETE /api/profile/session/<id>")
    print("\n   🧘 ANALYSE DE POSTURE:")
    print("      GET  /api/health")
    print("      GET  /api/poses")
    print("      POST /api/classify")
    print("      POST /api/analyze")
    print("      POST /api/complete-analysis")
    print("\n" + "="*70 + "\n")

    app.run(host='0.0.0.0', port=8000, debug=True)