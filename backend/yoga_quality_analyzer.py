# Yoga Pose Quality Analyzer - Module d'Analyse Qualitative
# Analyse la qualité d'exécution des poses de yoga et génère un feedback personnalisé

import numpy as np
import json
from typing import Dict, List, Tuple, Optional
import mediapipe as mp
import cv2

# ============================================================================
# 1. FONCTIONS UTILITAIRES DE CALCUL
# ============================================================================

def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """
    Calcule l'angle entre trois points (a-b-c) en degrés
    b est le sommet de l'angle
    """
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)

def calculate_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Calcule la distance euclidienne entre deux points"""
    return np.linalg.norm(a - b)

def calculate_2d_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """
    Calcule l'angle 2D (dans le plan x-y) entre trois points
    Utile pour mesurer les angles par rapport à l'horizontale/verticale
    """
    ba = a[:2] - b[:2]
    bc = c[:2] - b[:2]
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)

def calculate_horizontal_alignment(point1: np.ndarray, point2: np.ndarray) -> float:
    """
    Calcule le degré d'alignement horizontal entre deux points (0-100)
    100 = parfaitement alignés horizontalement
    """
    diff_y = abs(point1[1] - point2[1])
    # Normaliser par rapport à une distance de référence
    max_diff = 0.1  # 10% de l'écran en coordonnées normalisées
    score = max(0, 100 - (diff_y / max_diff * 100))
    return min(100, score)

def calculate_vertical_alignment(point1: np.ndarray, point2: np.ndarray) -> float:
    """
    Calcule le degré d'alignement vertical entre deux points (0-100)
    100 = parfaitement alignés verticalement
    """
    diff_x = abs(point1[0] - point2[0])
    max_diff = 0.1
    score = max(0, 100 - (diff_x / max_diff * 100))
    return min(100, score)

def calculate_symmetry(left_point: np.ndarray, right_point: np.ndarray, 
                       center_point: np.ndarray) -> float:
    """
    Calcule la symétrie entre deux points par rapport à un point central (0-100)
    100 = parfaitement symétrique
    """
    dist_left = calculate_distance(left_point, center_point)
    dist_right = calculate_distance(right_point, center_point)
    
    diff = abs(dist_left - dist_right)
    avg_dist = (dist_left + dist_right) / 2
    
    if avg_dist < 1e-6:
        return 100.0
    
    symmetry_score = max(0, 100 - (diff / avg_dist * 100))
    return min(100, symmetry_score)

# ============================================================================
# 2. CLASSE PRINCIPALE : POSE QUALITY ANALYZER
# ============================================================================

class YogaPoseQualityAnalyzer:
    """
    Analyse la qualité d'exécution d'une pose de yoga à partir des keypoints MediaPipe
    """
    
    def __init__(self):
        self.pose_analyzers = {
            'downdog': self._analyze_downdog,
            'plank': self._analyze_plank,
            'tree': self._analyze_tree,
            'warrior2': self._analyze_warrior2,
            'goddess': self._analyze_goddess
        }
    
    def analyze_pose(self, pose_name: str, landmarks: np.ndarray,
                     temporal_data: Optional[List[np.ndarray]] = None,
                     include_global_score: bool = True) -> Dict:
        """
        Analyse complète d'une pose

        Args:
            pose_name: Nom de la pose détectée
            landmarks: Array de shape (33, 4) avec les keypoints MediaPipe
            temporal_data: Liste optionnelle de landmarks sur plusieurs frames pour analyser la stabilité
            include_global_score: Si True, ajoute le score global, priorité, et niveau

        Returns:
            Dict avec les indicateurs et le feedback
        """
        if pose_name not in self.pose_analyzers:
            return {
                "pose": pose_name,
                "error": "Pose non supportée pour l'analyse qualitative"
            }

        # Appeler l'analyseur spécifique à la pose
        analysis = self.pose_analyzers[pose_name](landmarks)

        # Ajouter l'analyse de stabilité si données temporelles disponibles
        if temporal_data and len(temporal_data) > 1:
            stability = self._analyze_stability(temporal_data)
            analysis['indicators']['stability'] = stability

            # Ajouter feedback sur stabilité
            if stability < 60:
                analysis['feedback'].append("⚠️ Posture instable. Travaillez votre gainage.")
            elif stability < 80:
                analysis['feedback'].append("✓ Bonne stabilité, continuez ainsi.")
            else:
                analysis['feedback'].append("✓✓ Excellente stabilité !")

        # Ajouter les nouvelles métriques globales
        if include_global_score and 'indicators' in analysis:
            indicators = analysis['indicators']

            # Calculer le score global
            global_score = self.calculate_global_score(indicators)
            analysis['global_score'] = global_score

            # Identifier l'indicateur prioritaire (le plus faible)
            priority = self.identify_priority_indicator(indicators)
            analysis['priority_indicator'] = priority

            # Déterminer le niveau de compétence
            skill_level = self.determine_skill_level(global_score)
            analysis['skill_level'] = skill_level

        return analysis

    def calculate_global_score(self, indicators: Dict[str, float]) -> float:
        """
        Calcule un score global à partir des indicateurs

        Args:
            indicators: Dictionnaire des scores d'indicateurs

        Returns:
            Score global sur 100
        """
        if not indicators:
            return 0.0

        # Calculer la moyenne des indicateurs
        scores = list(indicators.values())
        global_score = sum(scores) / len(scores)

        return round(global_score, 1)

    def identify_priority_indicator(self, indicators: Dict[str, float]) -> Dict:
        """
        Identifie l'indicateur le plus faible (priorité d'amélioration)

        Args:
            indicators: Dictionnaire des scores d'indicateurs

        Returns:
            Dict avec le nom et le score du plus faible indicateur
        """
        if not indicators:
            return {"name": None, "score": None, "improvement_needed": None}

        # Trouver l'indicateur avec le score le plus bas
        min_indicator = min(indicators.items(), key=lambda x: x[1])
        indicator_name, score = min_indicator

        # Déterminer le niveau d'amélioration nécessaire
        if score >= 85:
            improvement_level = "minimal"
        elif score >= 70:
            improvement_level = "modéré"
        elif score >= 50:
            improvement_level = "important"
        else:
            improvement_level = "critique"

        return {
            "name": indicator_name,
            "score": score,
            "improvement_needed": improvement_level
        }

    def determine_skill_level(self, global_score: float) -> str:
        """
        Détermine le niveau de compétence basé sur le score global

        Args:
            global_score: Score global sur 100

        Returns:
            Niveau: 'beginner', 'intermediate', 'advanced', ou 'expert'
        """
        if global_score >= 90:
            return "expert"
        elif global_score >= 80:
            return "advanced"
        elif global_score >= 60:
            return "intermediate"
        else:
            return "beginner"
    
    # ========================================================================
    # ANALYSEURS SPÉCIFIQUES PAR POSE
    # ========================================================================
    
    def _analyze_downdog(self, landmarks: np.ndarray) -> Dict:
        """
        Analyse du Chien Tête en Bas (Downward-Facing Dog)
        
        Critères clés:
        - Alignement bras-dos-jambes (forme de V inversé)
        - Ouverture des épaules
        - Extension des jambes
        - Position de la tête
        """
        # Points clés
        nose = landmarks[0, :3]
        left_shoulder = landmarks[11, :3]
        right_shoulder = landmarks[12, :3]
        left_elbow = landmarks[13, :3]
        right_elbow = landmarks[14, :3]
        left_wrist = landmarks[15, :3]
        right_wrist = landmarks[16, :3]
        left_hip = landmarks[23, :3]
        right_hip = landmarks[24, :3]
        left_knee = landmarks[25, :3]
        right_knee = landmarks[26, :3]
        left_ankle = landmarks[27, :3]
        right_ankle = landmarks[28, :3]
        
        mid_shoulder = (left_shoulder + right_shoulder) / 2
        mid_hip = (left_hip + right_hip) / 2
        mid_wrist = (left_wrist + right_wrist) / 2
        mid_ankle = (left_ankle + right_ankle) / 2
        
        indicators = {}
        feedback = []
        
        # 1. ALIGNEMENT GÉNÉRAL (bras-dos-jambes forment un V inversé)
        # Angle au niveau des hanches
        hip_angle = calculate_angle(mid_shoulder, mid_hip, mid_ankle)
        
        # Idéalement entre 90-120 degrés
        if 90 <= hip_angle <= 120:
            alignment_score = 100
            feedback.append("✓✓ Excellent alignement du dos et des jambes.")
        elif 80 <= hip_angle < 90 or 120 < hip_angle <= 140:
            alignment_score = 75
            feedback.append("✓ Bon alignement général, continuez.")
        else:
            alignment_score = 50
            if hip_angle < 80:
                feedback.append("⚠️ Hanches trop basses. Poussez davantage vers le haut.")
            else:
                feedback.append("⚠️ Hanches trop hautes ou dos trop arrondi.")
        
        indicators['alignment'] = round(alignment_score, 1)
        
        # 2. OUVERTURE DES ÉPAULES
        # Mesurer l'angle coude pour vérifier l'extension des bras
        left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        avg_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2
        
        # Bras tendus = angle proche de 180°
        if avg_elbow_angle >= 160:
            shoulder_opening = 100
            feedback.append("✓✓ Bras bien tendus, épaules ouvertes.")
        elif avg_elbow_angle >= 140:
            shoulder_opening = 75
            feedback.append("✓ Bras presque tendus. Poussez un peu plus dans les mains.")
        else:
            shoulder_opening = 50
            feedback.append("⚠️ Bras pliés. Tendez les coudes et poussez le sol.")
        
        indicators['shoulder_opening'] = round(shoulder_opening, 1)
        
        # 3. EXTENSION DES JAMBES
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
        
        if avg_knee_angle >= 160:
            leg_extension = 100
            feedback.append("✓✓ Jambes bien tendues.")
        elif avg_knee_angle >= 140:
            leg_extension = 75
            feedback.append("✓ Jambes presque tendues. C'est déjà très bien !")
        else:
            leg_extension = 60
            feedback.append("💡 Genoux pliés : c'est normal au début. Concentrez-vous d'abord sur le dos.")
        
        indicators['leg_extension'] = round(leg_extension, 1)
        
        # 4. SYMÉTRIE GAUCHE-DROITE
        symmetry = calculate_symmetry(left_wrist, right_wrist, mid_shoulder)
        indicators['symmetry'] = round(symmetry, 1)
        
        if symmetry < 70:
            feedback.append("⚠️ Asymétrie détectée. Vérifiez que vos mains sont à égale distance.")
        
        # 5. POSITION DE LA TÊTE
        # La tête doit être entre les bras, regard vers les pieds
        head_position_score = 100 - abs(nose[1] - mid_shoulder[1]) * 200
        head_position_score = max(0, min(100, head_position_score))
        indicators['head_position'] = round(head_position_score, 1)
        
        if head_position_score < 60:
            feedback.append("💡 Détendez la nuque, laissez la tête pendre naturellement.")
        
        return {
            "pose": "downdog",
            "indicators": indicators,
            "feedback": feedback
        }
    
    def _analyze_plank(self, landmarks: np.ndarray) -> Dict:
        """
        Analyse de la Planche (Plank)
        
        Critères clés:
        - Alignement épaules-hanches-chevilles (ligne droite)
        - Gainage du corps
        - Position des coudes (pas de genoux au sol)
        - Engagement du core
        """
        nose = landmarks[0, :3]
        left_shoulder = landmarks[11, :3]
        right_shoulder = landmarks[12, :3]
        left_wrist = landmarks[15, :3]
        right_wrist = landmarks[16, :3]
        left_hip = landmarks[23, :3]
        right_hip = landmarks[24, :3]
        left_knee = landmarks[25, :3]
        right_knee = landmarks[26, :3]
        left_ankle = landmarks[27, :3]
        right_ankle = landmarks[28, :3]
        
        mid_shoulder = (left_shoulder + right_shoulder) / 2
        mid_hip = (left_hip + right_hip) / 2
        mid_ankle = (left_ankle + right_ankle) / 2
        mid_knee = (left_knee + right_knee) / 2
        
        indicators = {}
        feedback = []
        
        # 1. ALIGNEMENT GÉNÉRAL (épaules-hanches-chevilles)
        # Calculer la déviation par rapport à une ligne droite
        # Vecteur de référence: épaules vers chevilles
        ref_vector = mid_ankle - mid_shoulder
        ref_vector_norm = ref_vector / (np.linalg.norm(ref_vector) + 1e-6)
        
        # Projection des hanches sur cette ligne
        hip_vector = mid_hip - mid_shoulder
        projection = np.dot(hip_vector, ref_vector_norm) * ref_vector_norm
        deviation = np.linalg.norm(hip_vector - projection)
        
        # Score basé sur la déviation (plus c'est petit, mieux c'est)
        alignment_score = max(0, 100 - deviation * 300)
        indicators['alignment'] = round(alignment_score, 1)
        
        if alignment_score >= 85:
            feedback.append("✓✓ Alignement parfait ! Corps bien droit.")
        elif alignment_score >= 70:
            feedback.append("✓ Bon alignement général.")
        else:
            # Déterminer si hanches trop hautes ou trop basses
            if mid_hip[1] < mid_shoulder[1]:
                feedback.append("⚠️ Hanches trop hautes. Engagez le core et descendez un peu.")
            else:
                feedback.append("⚠️ Hanches qui s'affaissent. Contractez les abdominaux !")
        
        # 2. FORCE DU CORE (détection genoux au sol)
        # Si les genoux sont proches du sol, c'est une planche modifiée
        knee_height = (left_knee[1] + right_knee[1]) / 2
        ankle_height = (left_ankle[1] + right_ankle[1]) / 2
        
        knee_to_ankle_dist = abs(knee_height - ankle_height)
        
        if knee_to_ankle_dist < 0.05:  # Genoux très proches des chevilles = genoux au sol
            core_strength = 40
            feedback.append("💡 Genoux au sol détectés. Planche modifiée - c'est un bon début !")
            feedback.append("💪 Pour progresser: essayez 10 secondes sur les pieds.")
        else:
            core_strength = 100
            feedback.append("✓✓ Planche complète ! Excellente force du core.")
        
        indicators['core_strength'] = core_strength
        
        # 3. SYMÉTRIE
        symmetry = calculate_symmetry(left_shoulder, right_shoulder, mid_hip)
        indicators['symmetry'] = round(symmetry, 1)
        
        if symmetry < 80:
            feedback.append("⚠️ Asymétrie détectée. Répartissez le poids équitablement.")
        
        # 4. POSITION DES ÉPAULES (au-dessus des poignets)
        shoulder_wrist_alignment = calculate_vertical_alignment(mid_shoulder, 
                                                                (left_wrist + right_wrist) / 2)
        indicators['shoulder_position'] = round(shoulder_wrist_alignment, 1)
        
        if shoulder_wrist_alignment < 70:
            feedback.append("💡 Épaules pas alignées avec les poignets. Ajustez votre position.")
        
        return {
            "pose": "plank",
            "indicators": indicators,
            "feedback": feedback
        }
    
    def _analyze_tree(self, landmarks: np.ndarray) -> Dict:
        """
        Analyse de l'Arbre (Tree Pose / Vrksasana)
        
        Critères clés:
        - Équilibre sur une jambe
        - Alignement vertical du corps
        - Position du pied levé (hauteur sur la cuisse)
        - Ouverture de la hanche
        """
        nose = landmarks[0, :3]
        left_shoulder = landmarks[11, :3]
        right_shoulder = landmarks[12, :3]
        left_hip = landmarks[23, :3]
        right_hip = landmarks[24, :3]
        left_knee = landmarks[25, :3]
        right_knee = landmarks[26, :3]
        left_ankle = landmarks[27, :3]
        right_ankle = landmarks[28, :3]
        
        mid_shoulder = (left_shoulder + right_shoulder) / 2
        mid_hip = (left_hip + right_hip) / 2
        
        indicators = {}
        feedback = []
        
        # Déterminer quelle jambe est levée (celle avec le genou le plus écarté latéralement)
        left_knee_spread = abs(left_knee[0] - left_hip[0])
        right_knee_spread = abs(right_knee[0] - right_hip[0])
        
        if left_knee_spread > right_knee_spread:
            # Jambe gauche levée
            standing_leg = "right"
            raised_knee = left_knee
            raised_ankle = left_ankle
            standing_hip = right_hip
            standing_ankle = right_ankle
        else:
            # Jambe droite levée
            standing_leg = "left"
            raised_knee = right_knee
            raised_ankle = right_ankle
            standing_hip = left_hip
            standing_ankle = left_ankle
        
        # 1. ALIGNEMENT VERTICAL (équilibre)
        vertical_alignment = calculate_vertical_alignment(nose, mid_hip)
        vertical_alignment_hip_ankle = calculate_vertical_alignment(standing_hip, standing_ankle)
        
        alignment_score = (vertical_alignment + vertical_alignment_hip_ankle) / 2
        indicators['alignment'] = round(alignment_score, 1)
        
        if alignment_score >= 80:
            feedback.append("✓✓ Excellent alignement vertical ! Parfait équilibre.")
        elif alignment_score >= 65:
            feedback.append("✓ Bon équilibre, corps presque aligné.")
        else:
            feedback.append("⚠️ Corps déséquilibré. Fixez un point et engagez le core.")
        
        # 2. HAUTEUR DU PIED LEVÉ
        # Mesurer la position du pied levé par rapport à la hanche d'appui
        foot_height = abs(raised_ankle[1] - standing_hip[1])
        
        if foot_height < 0.15:  # Pied haut (près de la cuisse)
            foot_position_score = 100
            feedback.append("✓✓ Pied bien placé en haut de la cuisse.")
        elif foot_height < 0.25:  # Pied au mollet
            foot_position_score = 75
            feedback.append("✓ Pied au mollet - c'est déjà très bien !")
        else:  # Pied bas (cheville ou sol)
            foot_position_score = 50
            feedback.append("💡 Pied au sol : essayez de le monter progressivement.")
        
        indicators['foot_height'] = round(foot_position_score, 1)
        
        # 3. OUVERTURE DE LA HANCHE
        # Angle entre le genou levé et l'axe du corps
        hip_opening = abs(raised_knee[0] - standing_hip[0]) * 200
        hip_opening = min(100, hip_opening)
        indicators['hip_opening'] = round(hip_opening, 1)
        
        if hip_opening < 50:
            feedback.append("💡 Ouvrez davantage la hanche pour plus de stabilité.")
        elif hip_opening >= 80:
            feedback.append("✓✓ Excellente ouverture de hanche !")
        
        # 4. SYMÉTRIE DES ÉPAULES
        shoulder_symmetry = calculate_horizontal_alignment(left_shoulder, right_shoulder)
        indicators['shoulder_level'] = round(shoulder_symmetry, 1)
        
        if shoulder_symmetry < 70:
            feedback.append("⚠️ Épaules déséquilibrées. Gardez-les au même niveau.")
        
        return {
            "pose": "tree",
            "indicators": indicators,
            "feedback": feedback
        }
    
    def _analyze_warrior2(self, landmarks: np.ndarray) -> Dict:
        """
        Analyse du Guerrier 2 (Warrior II / Virabhadrasana II)
        
        Critères clés:
        - Alignement des bras (ligne horizontale)
        - Flexion du genou avant (angle 90°)
        - Position du bassin (ouvert sur le côté)
        - Regard vers l'avant
        """
        nose = landmarks[0, :3]
        left_shoulder = landmarks[11, :3]
        right_shoulder = landmarks[12, :3]
        left_elbow = landmarks[13, :3]
        right_elbow = landmarks[14, :3]
        left_wrist = landmarks[15, :3]
        right_wrist = landmarks[16, :3]
        left_hip = landmarks[23, :3]
        right_hip = landmarks[24, :3]
        left_knee = landmarks[25, :3]
        right_knee = landmarks[26, :3]
        left_ankle = landmarks[27, :3]
        right_ankle = landmarks[28, :3]
        
        indicators = {}
        feedback = []
        
        # Déterminer quelle jambe est devant (celle avec le genou le plus plié)
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        if left_knee_angle < right_knee_angle:
            front_leg = "left"
            front_knee_angle = left_knee_angle
            front_hip = left_hip
            front_knee = left_knee
            front_ankle = left_ankle
        else:
            front_leg = "right"
            front_knee_angle = right_knee_angle
            front_hip = right_hip
            front_knee = right_knee
            front_ankle = right_ankle
        
        # 1. ALIGNEMENT DES BRAS (horizontale)
        arms_horizontal_alignment = calculate_horizontal_alignment(left_wrist, right_wrist)
        indicators['arms_alignment'] = round(arms_horizontal_alignment, 1)
        
        # Vérifier extension des bras
        left_arm_extension = calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_arm_extension = calculate_angle(right_shoulder, right_elbow, right_wrist)
        avg_arm_extension = (left_arm_extension + right_arm_extension) / 2
        
        if arms_horizontal_alignment >= 85 and avg_arm_extension >= 160:
            feedback.append("✓✓ Bras parfaitement alignés et tendus !")
        elif arms_horizontal_alignment >= 70:
            feedback.append("✓ Bras bien tendus sur les côtés.")
        else:
            feedback.append("⚠️ Alignez les bras à l'horizontale, tendus sur les côtés.")
        
        # 2. FLEXION DU GENOU AVANT (angle idéal: 90°)
        knee_flexion_score = 100 - abs(90 - front_knee_angle)
        knee_flexion_score = max(0, knee_flexion_score)
        indicators['front_knee_angle'] = round(front_knee_angle, 1)
        indicators['knee_flexion_quality'] = round(knee_flexion_score, 1)
        
        if 85 <= front_knee_angle <= 95:
            feedback.append("✓✓ Genou avant parfaitement fléchi à 90° !")
        elif 75 <= front_knee_angle < 85:
            feedback.append("💪 Genou bien fléchi ! Vous pouvez descendre un peu plus.")
        elif front_knee_angle < 75:
            feedback.append("⚠️ Attention : genou trop fléchi, remontez légèrement.")
        else:
            feedback.append("💡 Fléchissez davantage le genou avant (objectif: 90°).")
        
        # 3. ALIGNEMENT GENOU-CHEVILLE
        # Le genou ne doit pas dépasser la cheville
        knee_ankle_alignment = calculate_vertical_alignment(front_knee, front_ankle)
        indicators['knee_ankle_alignment'] = round(knee_ankle_alignment, 1)
        
        if knee_ankle_alignment < 60:
            feedback.append("⚠️ Genou dépasse la cheville. Reculez un peu le pied arrière.")
        
        # 4. OUVERTURE DES HANCHES
        hip_opening = abs(left_hip[0] - right_hip[0]) * 200
        hip_opening = min(100, hip_opening)
        indicators['hip_opening'] = round(hip_opening, 1)
        
        if hip_opening < 60:
            feedback.append("💡 Ouvrez davantage les hanches sur le côté.")
        elif hip_opening >= 80:
            feedback.append("✓✓ Excellente ouverture de hanches !")
        
        # 5. SYMÉTRIE DES ÉPAULES
        shoulder_symmetry = calculate_horizontal_alignment(left_shoulder, right_shoulder)
        indicators['shoulder_level'] = round(shoulder_symmetry, 1)
        
        if shoulder_symmetry < 75:
            feedback.append("⚠️ Gardez les épaules au même niveau.")
        
        return {
            "pose": "warrior2",
            "indicators": indicators,
            "feedback": feedback
        }
    
    def _analyze_goddess(self, landmarks: np.ndarray) -> Dict:
        """
        Analyse de la Déesse (Goddess Pose / Utkata Konasana)
        
        Critères clés:
        - Écartement des jambes
        - Flexion des genoux (squats position)
        - Alignement des genoux avec les pieds
        - Position du dos (droit)
        """
        nose = landmarks[0, :3]
        left_shoulder = landmarks[11, :3]
        right_shoulder = landmarks[12, :3]
        left_hip = landmarks[23, :3]
        right_hip = landmarks[24, :3]
        left_knee = landmarks[25, :3]
        right_knee = landmarks[26, :3]
        left_ankle = landmarks[27, :3]
        right_ankle = landmarks[28, :3]
        
        mid_shoulder = (left_shoulder + right_shoulder) / 2
        mid_hip = (left_hip + right_hip) / 2
        
        indicators = {}
        feedback = []
        
        # 1. ÉCARTEMENT DES JAMBES
        feet_distance = calculate_distance(left_ankle, right_ankle)
        # Normaliser par rapport à la largeur des hanches
        hip_width = calculate_distance(left_hip, right_hip)
        
        stance_width_ratio = feet_distance / (hip_width + 1e-6)
        
        if stance_width_ratio >= 2.5:
            stance_score = 100
            feedback.append("✓✓ Écartement parfait des jambes !")
        elif stance_width_ratio >= 2.0:
            stance_score = 80
            feedback.append("✓ Bon écartement, vous pouvez élargir un peu plus.")
        else:
            stance_score = 60
            feedback.append("💡 Écartez davantage les jambes (largeur > épaules).")
        
        indicators['stance_width'] = round(stance_score, 1)
        
        # 2. PROFONDEUR DU SQUAT
        left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
        
        # Angle idéal: environ 90°
        squat_depth_score = 100 - abs(90 - avg_knee_angle)
        squat_depth_score = max(0, squat_depth_score)
        indicators['squat_depth'] = round(squat_depth_score, 1)
        indicators['knee_angle'] = round(avg_knee_angle, 1)
        
        if 85 <= avg_knee_angle <= 95:
            feedback.append("✓✓ Profondeur de squat parfaite !")
        elif avg_knee_angle > 120:
            feedback.append("💪 Descendez davantage ! Objectif: cuisses parallèles au sol.")
        else:
            feedback.append("✓ Bonne profondeur de squat.")
        
        # 3. ALIGNEMENT GENOUX-PIEDS
        # Les genoux doivent être alignés avec les pieds (pas vers l'intérieur)
        left_knee_ankle_align = abs(left_knee[0] - left_ankle[0])
        right_knee_ankle_align = abs(right_knee[0] - right_ankle[0])
        avg_knee_align = (left_knee_ankle_align + right_knee_ankle_align) / 2
        
        knee_alignment_score = max(0, 100 - avg_knee_align * 300)
        indicators['knee_alignment'] = round(knee_alignment_score, 1)
        
        if knee_alignment_score < 70:
            feedback.append("⚠️ Genoux vers l'intérieur. Poussez-les vers l'extérieur, alignés avec les pieds.")
        else:
            feedback.append("✓ Bonne position des genoux.")
        
        # 4. POSITION DU DOS (vertical)
        back_vertical = calculate_vertical_alignment(nose, mid_hip)
        indicators['back_position'] = round(back_vertical, 1)
        
        if back_vertical >= 80:
            feedback.append("✓✓ Dos bien droit !")
        elif back_vertical >= 65:
            feedback.append("✓ Dos relativement droit, c'est bien.")
        else:
            feedback.append("💡 Redressez le dos, poitrine ouverte.")
        
        # 5. SYMÉTRIE GAUCHE-DROITE
        symmetry = calculate_symmetry(left_knee, right_knee, mid_hip)
        indicators['symmetry'] = round(symmetry, 1)
        
        if symmetry < 75:
            feedback.append("⚠️ Asymétrie détectée. Équilibrez le poids sur les deux jambes.")
        
        return {
            "pose": "goddess",
            "indicators": indicators,
            "feedback": feedback
        }
    
    def _analyze_stability(self, temporal_landmarks: List[np.ndarray]) -> float:
        """
        Analyse la stabilité d'une pose sur plusieurs frames
        
        Args:
            temporal_landmarks: Liste de landmarks sur plusieurs frames
        
        Returns:
            Score de stabilité (0-100)
        """
        if len(temporal_landmarks) < 2:
            return 100.0
        
        # Calculer la variation des points clés importants entre les frames
        key_indices = [0, 11, 12, 23, 24]  # Nez, épaules, hanches
        
        total_movement = 0
        num_comparisons = 0
        
        for i in range(len(temporal_landmarks) - 1):
            landmarks1 = temporal_landmarks[i]
            landmarks2 = temporal_landmarks[i + 1]
            
            for idx in key_indices:
                point1 = landmarks1[idx, :3]
                point2 = landmarks2[idx, :3]
                movement = calculate_distance(point1, point2)
                total_movement += movement
                num_comparisons += 1
        
        avg_movement = total_movement / num_comparisons if num_comparisons > 0 else 0
        
        # Convertir en score (moins de mouvement = meilleure stabilité)
        stability_score = max(0, 100 - avg_movement * 500)
        
        return stability_score

# ============================================================================
# 3. FONCTION HELPER POUR INTÉGRATION AVEC LE MODÈLE
# ============================================================================

def analyze_pose_quality(image_path: str, pose_name: str, 
                        temporal_images: Optional[List[str]] = None) -> Dict:
    """
    Fonction complète pour analyser la qualité d'une pose à partir d'une image
    
    Args:
        image_path: Chemin vers l'image
        pose_name: Nom de la pose détectée par le modèle
        temporal_images: Liste optionnelle de chemins d'images pour analyse temporelle
    
    Returns:
        Dict avec l'analyse complète au format JSON
    """
    mp_pose = mp.solutions.pose
    
    # Extraire les landmarks de l'image principale
    with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Image non trouvée"}
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return {"error": "Aucune pose détectée dans l'image"}
        
        # Convertir en array numpy
        landmarks = np.array([[lm.x, lm.y, lm.z, lm.visibility] 
                             for lm in results.pose_landmarks.landmark])
        
        # Analyse temporelle si plusieurs images fournies
        temporal_data = None
        if temporal_images and len(temporal_images) > 1:
            temporal_data = []
            for img_path in temporal_images:
                img = cv2.imread(img_path)
                if img is not None:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    res = pose.process(img_rgb)
                    if res.pose_landmarks:
                        temp_landmarks = np.array([[lm.x, lm.y, lm.z, lm.visibility] 
                                                  for lm in res.pose_landmarks.landmark])
                        temporal_data.append(temp_landmarks)
        
        # Analyser la qualité
        analyzer = YogaPoseQualityAnalyzer()
        analysis = analyzer.analyze_pose(pose_name, landmarks, temporal_data)
        
        return analysis

# ============================================================================
# 4. DÉMONSTRATION
# ============================================================================

def demo_usage():
    """
    Démonstration de l'utilisation du module
    """
    print("="*70)
    print("DÉMONSTRATION: YOGA POSE QUALITY ANALYZER")
    print("="*70 + "\n")
    
    # Exemple de résultat structuré
    example_output = {
        "pose": "plank",
        "indicators": {
            "alignment": 92.3,
            "symmetry": 87.5,
            "core_strength": 100.0,
            "shoulder_position": 85.2
        },
        "feedback": [
            "✓✓ Alignement parfait ! Corps bien droit.",
            "✓✓ Planche complète ! Excellente force du core.",
            "✓ Répartissez le poids équitablement."
        ]
    }
    
    print("📊 Exemple de sortie JSON:")
    print(json.dumps(example_output, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("✅ MODULE PRÊT À L'EMPLOI")
    print("="*70)
    print("\n📦 Fonctionnalités:")
    print("   ✓ Analyse de 5 poses (downdog, plank, tree, warrior2, goddess)")
    print("   ✓ Indicateurs spécifiques par pose")
    print("   ✓ Feedback pédagogique personnalisé")
    print("   ✓ Format JSON pour API")
    print("\n💡 Utilisation:")
    print("   from yoga_quality_analyzer import analyze_pose_quality")
    print("   result = analyze_pose_quality('image.jpg', 'plank')")
    print("="*70)

if __name__ == "__main__":
    demo_usage()