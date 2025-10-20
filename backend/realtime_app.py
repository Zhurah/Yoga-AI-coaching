# Application de coaching yoga en temps réel via webcam

import cv2
import time
import joblib
import numpy as np
import mediapipe as mp
from backend.yoga_quality_analyzer import YogaPoseQualityAnalyzer

print("="*70)
print("🎥 APPLICATION DE COACHING YOGA EN TEMPS RÉEL")
print("="*70 + "\n")

# Charger les modèles
print("Chargement des modèles...")
try:
    model = joblib.load('best_yoga_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
    print("✅ Modèles chargés\n")
except FileNotFoundError as e:
    print(f"❌ Erreur: {e}")
    exit(1)

# Initialiser MediaPipe et l'analyseur
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
analyzer = YogaPoseQualityAnalyzer()

def extract_keypoints_from_frame(frame, pose_processor):
    """Extrait les keypoints d'un frame"""
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose_processor.process(image_rgb)
    
    if results.pose_landmarks:
        keypoints = []
        for landmark in results.pose_landmarks.landmark:
            keypoints.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
        return np.array(keypoints), results.pose_landmarks
    return None, None

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

def calculate_distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def engineer_features(keypoints_raw):
    """Feature engineering simplifié"""
    if keypoints_raw is None or len(keypoints_raw) != 132:
        return None
    
    landmarks = keypoints_raw.reshape(33, 4)
    features = []
    
    key_indices = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
    for idx in key_indices:
        features.extend(landmarks[idx, :3])
    
    # Angles et distances (version simplifiée)
    left_shoulder, left_elbow, left_wrist = landmarks[11, :3], landmarks[13, :3], landmarks[15, :3]
    right_shoulder, right_elbow, right_wrist = landmarks[12, :3], landmarks[14, :3], landmarks[16, :3]
    left_hip, right_hip = landmarks[23, :3], landmarks[24, :3]
    left_knee, right_knee = landmarks[25, :3], landmarks[26, :3]
    left_ankle, right_ankle = landmarks[27, :3], landmarks[28, :3]
    nose = landmarks[0, :3]
    
    features.extend([
        calculate_angle(left_shoulder, left_elbow, left_wrist),
        calculate_angle(right_shoulder, right_elbow, right_wrist),
        calculate_angle(left_hip, left_shoulder, left_elbow),
        calculate_angle(right_hip, right_shoulder, right_elbow),
        calculate_angle(left_hip, left_knee, left_ankle),
        calculate_angle(right_hip, right_knee, right_ankle),
        calculate_angle(left_knee, left_hip, nose),
        calculate_angle(right_knee, right_hip, nose),
        calculate_distance(left_shoulder, right_shoulder),
        calculate_distance(left_hip, right_hip),
        calculate_distance(nose, (left_hip + right_hip) / 2),
        calculate_distance(left_wrist, left_ankle),
        calculate_distance(right_wrist, right_ankle),
        calculate_distance(left_shoulder, right_shoulder) / (calculate_distance(left_hip, right_hip) + 1e-6),
        abs(nose[1] - ((left_hip[1] + right_hip[1]) / 2)),
        calculate_distance(left_ankle, right_ankle),
        np.mean(landmarks[:, 3])
    ])
    
    return np.array(features)

def run_realtime_coaching(camera_id=0):
    """Lance le coaching en temps réel"""
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print("❌ Impossible d'ouvrir la webcam")
        return
    
    print("🎥 Coaching démarré!")
    print("   - Appuyez sur 'q' pour quitter")
    print("   - Appuyez sur 'espace' pour forcer une analyse")
    print("   - Analyse automatique toutes les 3 secondes\n")
    
    last_analysis_time = 0
    analysis_cooldown = 3  # secondes
    current_result = None
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose_detector:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip pour effet miroir
            frame = cv2.flip(frame, 1)
            display_frame = frame.copy()

            # Extraire keypoints et dessiner le squelette
            keypoints_raw, pose_landmarks = extract_keypoints_from_frame(frame, pose_detector)
            
            if pose_landmarks:
                mp_drawing.draw_landmarks(
                    display_frame,
                    pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
            
            # Analyse périodique
            current_time = time.time()
            if keypoints_raw is not None and (current_time - last_analysis_time >= analysis_cooldown):
                features = engineer_features(keypoints_raw)
                
                if features is not None:
                    features_reshaped = features.reshape(1, -1)
                    features_scaled = scaler.transform(features_reshaped)

                    try:
                        prediction = model.predict(features_scaled)[0]
                        pose_name = label_encoder.inverse_transform([prediction])[0]

                        if hasattr(model, 'predict_proba'):
                            probabilities = model.predict_proba(features_scaled)[0]
                            confidence = probabilities[prediction]
                        else:
                            confidence = 1.0
                        
                        # Analyse qualitative
                        landmarks = keypoints_raw.reshape(33, 4)
                        quality = analyzer.analyze_pose(pose_name, landmarks)
                        
                        current_result = {
                            "pose": pose_name,
                            "confidence": confidence,
                            "quality": quality
                        }
                        
                        last_analysis_time = current_time
                    except:
                        pass
            
            # Afficher les résultats
            if current_result:
                pose = current_result["pose"]
                conf = current_result["confidence"]
                quality = current_result["quality"]
                
                # Titre
                cv2.putText(display_frame, f"Pose: {pose.upper()}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2)
                
                cv2.putText(display_frame, f"Confiance: {conf*100:.0f}%", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (255, 255, 255), 2)
                
                # Indicateurs
                if "indicators" in quality:
                    indicators = quality["indicators"]
                    overall = sum(indicators.values()) / len(indicators)
                    
                    cv2.putText(display_frame, f"Score: {overall:.0f}/100", 
                               (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, (0, 255, 255), 2)
                    
                    # Top 3 indicateurs
                    y_pos = 150
                    sorted_ind = sorted(indicators.items(), key=lambda x: x[1], reverse=True)[:3]
                    
                    for indicator, value in sorted_ind:
                        color = (0, 255, 0) if value >= 80 else (0, 165, 255) if value >= 60 else (0, 0, 255)
                        text = f"{indicator}: {value:.0f}"
                        cv2.putText(display_frame, text, 
                                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.6, color, 2)
                        y_pos += 30
                    
                    # Premier feedback
                    if quality["feedback"]:
                        feedback = quality["feedback"][0]
                        if len(feedback) > 50:
                            feedback = feedback[:47] + "..."
                        
                        cv2.putText(display_frame, feedback, 
                                   (10, display_frame.shape[0] - 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 
                                   0.5, (255, 255, 255), 1)
            
            # Instructions
            cv2.putText(display_frame, "Q: Quitter | ESPACE: Analyser", 
                       (10, display_frame.shape[0] - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 
                       0.5, (200, 200, 200), 1)
            
            # Afficher
            cv2.imshow('Yoga Coaching - Temps Reel', display_frame)
            
            # Contrôles
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' ') and keypoints_raw is not None:
                last_analysis_time = 0  # Forcer une analyse
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n🎥 Coaching terminé")

if __name__ == "__main__":
    run_realtime_coaching()