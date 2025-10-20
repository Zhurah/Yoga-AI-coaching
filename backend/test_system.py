# Script de test pour le système complet
# Combine classification + analyse qualitative

import joblib
import numpy as np
import cv2
import mediapipe as mp
import json
from backend.yoga_quality_analyzer import YogaPoseQualityAnalyzer, analyze_pose_quality

print("="*70)
print("TEST DU SYSTÈME COMPLET DE COACHING YOGA")
print("="*70 + "\n")

# ============================================================================
# 1. CHARGER LES MODÈLES
# ============================================================================

print("Chargement des modèles...")
try:
    model = joblib.load('best_yoga_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
    print("✅ Modèles chargés avec succès\n")
except FileNotFoundError as e:
    print(f"❌ Erreur: {e}")
    print("Assurez-vous d'avoir exécuté best_model.ipynb d'abord.\n")
    exit(1)

# ============================================================================
# 2. FONCTIONS UTILITAIRES
# ============================================================================

def extract_keypoints_from_image(image_path, pose):
    """Extrait les keypoints MediaPipe"""
    image = cv2.imread(image_path)
    if image is None:
        return None
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    
    if results.pose_landmarks:
        keypoints = []
        for landmark in results.pose_landmarks.landmark:
            keypoints.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
        return np.array(keypoints)
    return None

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
    """Feature engineering (simplifié pour le test)"""
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

def complete_yoga_analysis(image_path, confidence_threshold=0.7, user_level="intermediate"):
    """
    Analyse complète: Classification + Qualité
    """
    mp_pose = mp.solutions.pose
    
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        # 1. Extraire keypoints
        keypoints_raw = extract_keypoints_from_image(image_path, pose)
        
        if keypoints_raw is None:
            return {
                "success": False,
                "error": "Aucune pose détectée dans l'image"
            }
        
        # 2. Feature engineering
        features = engineer_features(keypoints_raw)
        
        if features is None:
            return {
                "success": False,
                "error": "Erreur lors de l'extraction des features"
            }
        
        # 3. Classification
        features_reshaped = features.reshape(1, -1)
        features_scaled = scaler.transform(features_reshaped)

        try:
            prediction = model.predict(features_scaled)[0]
            pose_name = label_encoder.inverse_transform([prediction])[0]
            
            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(features_scaled)[0]
                confidence = probabilities[prediction]
                all_probabilities = dict(zip(label_encoder.classes_, probabilities))
            else:
                confidence = 1.0
                all_probabilities = None
        except Exception as e:
            return {
                "success": False,
                "error": f"Erreur lors de la prédiction: {str(e)}"
            }
        
        # 4. Analyse qualitative
        quality_analysis = None
        if confidence >= confidence_threshold:
            landmarks = keypoints_raw.reshape(33, 4)
            analyzer = YogaPoseQualityAnalyzer()
            quality_analysis = analyzer.analyze_pose(pose_name, landmarks)
        
        # 5. Résultat complet
        result = {
            "success": True,
            "classification": {
                "pose": pose_name,
                "confidence": round(confidence * 100, 1),
                "all_probabilities": {
                    k: round(v * 100, 1) for k, v in all_probabilities.items()
                } if all_probabilities else None
            }
        }
        
        if quality_analysis:
            indicators = quality_analysis['indicators']
            overall_score = sum(indicators.values()) / len(indicators)
            
            result["quality_analysis"] = {
                "indicators": quality_analysis['indicators'],
                "overall_score": round(overall_score, 1),
                "feedback": quality_analysis['feedback']
            }
        else:
            result["quality_analysis"] = {
                "message": f"Confiance insuffisante ({confidence:.1%}). Réessayez."
            }
        
        return result

# ============================================================================
# 3. TESTER SUR DES EXEMPLES
# ============================================================================

print("="*70)
print("TEST SUR DES EXEMPLES DU DATASET")
print("="*70 + "\n")

import os
from pathlib import Path

# Tester sur quelques images
test_images = []
for pose_class in ['downdog', 'plank', 'tree']:
    class_dir = Path('DATASET/TEST') / pose_class
    if class_dir.exists():
        images = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
        if images:
            test_images.append((str(images[0]), pose_class))

if not test_images:
    print("⚠️  Aucune image trouvée dans DATASET/TEST/")
    print("Vérifiez que la structure du dataset est correcte.\n")
else:
    for img_path, true_class in test_images:
        print(f"\n{'='*70}")
        print(f"📸 Analyse: {Path(img_path).name}")
        print(f"   Classe réelle: {true_class}")
        print('='*70)
        
        result = complete_yoga_analysis(img_path, user_level="intermediate")
        
        if result["success"]:
            print(f"\n🎯 CLASSIFICATION:")
            print(f"   Pose: {result['classification']['pose']}")
            print(f"   Confiance: {result['classification']['confidence']}%")
            
            if "indicators" in result["quality_analysis"]:
                print(f"\n📊 ANALYSE QUALITATIVE:")
                print(f"   Score global: {result['quality_analysis']['overall_score']}/100")
                print(f"\n   Indicateurs:")
                for indicator, value in result['quality_analysis']['indicators'].items():
                    bar = "█" * int(value / 5)
                    print(f"      {indicator:20s}: {bar:20s} {value:.1f}/100")
                
                print(f"\n💬 FEEDBACK:")
                for feedback in result['quality_analysis']['feedback']:
                    print(f"      {feedback}")
            else:
                print(f"\n⚠️  {result['quality_analysis']['message']}")
            
            # Sauvegarder en JSON
            output_file = f"result_{Path(img_path).stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Résultat sauvegardé: {output_file}")
        else:
            print(f"\n❌ Erreur: {result['error']}")

print("\n" + "="*70)
print("✅ TESTS TERMINÉS")
print("="*70)