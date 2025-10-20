"""
API Flask v2 pour le système de coaching yoga
Inclut authentification, profils utilisateurs, et recommandations d'exercices
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt_identity
import joblib
import numpy as np
import cv2
import mediapipe as mp
import os
from dotenv import load_dotenv

# Imports des modules personnalisés
from models import db, User, UserProfile, PoseSession, init_db
from auth import jwt, register_auth_routes, get_current_user
from yoga_quality_analyzer import YogaPoseQualityAnalyzer
from exercise_recommender import ExerciseRecommender
from profile_service import ProfileService

# Charger les variables d'environnement
load_dotenv()

# ============================================================================
# CONFIGURATION DE L'APPLICATION
# ============================================================================

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///yoga_coach.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 heure

# Initialiser les extensions
jwt.init_app(app)
init_db(app)

# ============================================================================
# CHARGEMENT DES MODÈLES ML
# ============================================================================

print("="*70)
print("🚀 DÉMARRAGE DE L'API YOGA COACHING V2")
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

# Initialiser les analyseurs
analyzer = YogaPoseQualityAnalyzer()
recommender = ExerciseRecommender()
print("✅ Analyseur de qualité et recommandeur initialisés")

# Initialiser MediaPipe
mp_pose = mp.solutions.pose

# ============================================================================
# FONCTIONS UTILITAIRES (Feature Engineering)
# ============================================================================

def calculate_angle(a, b, c):
    """Calcule l'angle entre trois points"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def calculate_distance(a, b):
    """Calcule la distance entre deux points"""
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
        features_scaled = scaler.transform(features_reshaped)
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

# ============================================================================
# ROUTES API - PUBLIQUES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.0",
        "features": ["authentication", "profiles", "recommendations", "history"],
        "models_loaded": True
    })

@app.route('/api/poses', methods=['GET'])
def get_poses():
    """Retourne la liste des poses disponibles"""
    return jsonify({
        "poses": list(label_encoder.classes_),
        "count": len(label_encoder.classes_)
    })

# ============================================================================
# ROUTES API - ANALYSE (AUTHENTIFIÉES)
# ============================================================================

@app.route('/api/analyze-complete', methods=['POST'])
@jwt_required()
def analyze_complete():
    """
    Analyse complète : Classification + Qualité + Recommandation + Sauvegarde

    Body JSON:
    {
        "landmarks": [[x, y, z, visibility], ...],
        "save_session": true  // optionnel, par défaut true
    }
    """
    try:
        data = request.json
        landmarks_list = data.get('landmarks')
        save_session = data.get('save_session', True)

        user = get_current_user()
        if not user:
            return jsonify({
                "success": False,
                "error": "Utilisateur non trouvé"
            }), 404

        # 1. Classification
        classify_result = classify_pose_internal(landmarks_list)

        if not classify_result['success']:
            return jsonify(classify_result), 400

        pose_name = classify_result['pose']
        confidence = classify_result['confidence']

        # 2. Analyse qualitative si confiance suffisante
        quality_result = None
        recommended_exercise = None

        if confidence >= 0.7:
            landmarks_array = np.array([
                [lm['x'], lm['y'], lm['z'], lm['visibility']]
                for lm in landmarks_list
            ])

            analysis = analyzer.analyze_pose(pose_name, landmarks_array, include_global_score=True)

            if 'error' not in analysis:
                global_score = analysis.get('global_score', 0)
                indicators = analysis.get('indicators', {})
                feedback = analysis.get('feedback', [])
                priority_indicator = analysis.get('priority_indicator', {})
                skill_level = analysis.get('skill_level', user.skill_level)

                # 3. Obtenir une recommandation d'exercice
                recommended_exercise = recommender.get_recommendation(
                    pose_name,
                    priority_indicator,
                    user.skill_level
                )

                quality_result = {
                    "global_score": global_score,
                    "indicators": indicators,
                    "feedback": feedback,
                    "priority_indicator": priority_indicator,
                    "skill_level": skill_level,
                    "recommended_exercise": recommended_exercise
                }

                # 4. Sauvegarder la session si demandé
                if save_session:
                    ProfileService.save_session(
                        user_id=user.id,
                        pose_name=pose_name,
                        confidence=confidence,
                        global_score=global_score,
                        indicators=indicators,
                        feedback=feedback,
                        priority_indicator=priority_indicator,
                        recommended_exercise=recommended_exercise
                    )

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

# ============================================================================
# ROUTES API - PROFIL UTILISATEUR (AUTHENTIFIÉES)
# ============================================================================

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Récupère le profil complet de l'utilisateur"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({
                "success": False,
                "error": "Utilisateur non trouvé"
            }), 404

        profile = UserProfile.query.filter_by(user_id=user.id).first()

        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "profile": profile.to_dict() if profile else None
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/profile/history', methods=['GET'])
@jwt_required()
def get_history():
    """Récupère l'historique des sessions"""
    try:
        user_id = get_jwt_identity()

        # Paramètres de pagination
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        pose_filter = request.args.get('pose', None)

        history = ProfileService.get_user_history(user_id, limit, offset, pose_filter)

        return jsonify({
            "success": True,
            "sessions": history,
            "count": len(history)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/profile/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """Récupère les statistiques sur une période"""
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)

        stats = ProfileService.get_session_statistics(user_id, days)

        return jsonify({
            "success": True,
            "statistics": stats
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/profile/pose-progress/<pose_name>', methods=['GET'])
@jwt_required()
def get_pose_progress(pose_name):
    """Récupère la progression pour une pose spécifique"""
    try:
        user_id = get_jwt_identity()

        progress = ProfileService.get_pose_progress(user_id, pose_name)

        return jsonify({
            "success": True,
            "progress": progress
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/profile/session/<int:session_id>', methods=['DELETE'])
@jwt_required()
def delete_session(session_id):
    """Supprime une session"""
    try:
        user_id = get_jwt_identity()

        success = ProfileService.delete_session(session_id, user_id)

        if success:
            return jsonify({
                "success": True,
                "message": "Session supprimée"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Session non trouvée"
            }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ============================================================================
# ROUTES API - RECOMMANDATIONS
# ============================================================================

@app.route('/api/recommendations', methods=['POST'])
@jwt_required()
def get_recommendations():
    """
    Obtient des recommandations d'exercices basées sur les indicateurs

    Body JSON:
    {
        "pose_name": "plank",
        "indicators": {"alignment": 85, "core_strength": 60, ...},
        "top_n": 3  // optionnel, par défaut 3
    }
    """
    try:
        data = request.json
        pose_name = data.get('pose_name')
        indicators = data.get('indicators')
        top_n = data.get('top_n', 3)

        user = get_current_user()

        if not pose_name or not indicators:
            return jsonify({
                "success": False,
                "error": "pose_name et indicators requis"
            }), 400

        recommendations = recommender.get_multiple_recommendations(
            pose_name,
            indicators,
            top_n,
            user.skill_level if user else "intermediate"
        )

        return jsonify({
            "success": True,
            "recommendations": recommendations
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ============================================================================
# ENREGISTREMENT DES ROUTES D'AUTHENTIFICATION
# ============================================================================

register_auth_routes(app)

# ============================================================================
# DÉMARRAGE
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 API V2 démarrée sur http://localhost:8000")
    print("="*70)
    print("\n📋 Endpoints disponibles:")
    print("\n   🔓 PUBLICS:")
    print("   GET  /api/health")
    print("   GET  /api/poses")
    print("\n   🔐 AUTHENTIFICATION:")
    print("   POST /api/auth/register")
    print("   POST /api/auth/login")
    print("   POST /api/auth/refresh")
    print("   GET  /api/auth/me")
    print("   POST /api/auth/logout")
    print("\n   🧘 ANALYSE (authentifiées):")
    print("   POST /api/analyze-complete")
    print("\n   👤 PROFIL (authentifiées):")
    print("   GET  /api/profile")
    print("   GET  /api/profile/history")
    print("   GET  /api/profile/statistics")
    print("   GET  /api/profile/pose-progress/<pose_name>")
    print("   DELETE /api/profile/session/<session_id>")
    print("\n   💡 RECOMMANDATIONS (authentifiées):")
    print("   POST /api/recommendations")
    print("\n" + "="*70 + "\n")

    app.run(host='0.0.0.0', port=8000, debug=True)
