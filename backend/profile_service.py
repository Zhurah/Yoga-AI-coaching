"""
Service de Gestion des Profils Utilisateurs
Gère l'historique des sessions et les statistiques agrégées
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from models import db, User, PoseSession, UserProfile
from sqlalchemy import func, desc


class ProfileService:
    """Service pour gérer les profils utilisateurs et l'historique"""

    @staticmethod
    def save_session(user_id: int, pose_name: str, confidence: float,
                    global_score: float, indicators: Dict, feedback: List,
                    priority_indicator: Dict, recommended_exercise: Optional[Dict] = None,
                    duration_seconds: Optional[int] = None) -> PoseSession:
        """
        Enregistre une session d'analyse de pose

        Args:
            user_id: ID de l'utilisateur
            pose_name: Nom de la pose
            confidence: Confiance de la classification
            global_score: Score global de qualité
            indicators: Dict des indicateurs
            feedback: Liste des messages de feedback
            priority_indicator: Dict avec l'indicateur prioritaire
            recommended_exercise: Exercice recommandé (optionnel)
            duration_seconds: Durée de la session

        Returns:
            PoseSession créée
        """
        session = PoseSession(
            user_id=user_id,
            pose_name=pose_name,
            confidence=confidence,
            global_score=global_score,
            priority_indicator=priority_indicator.get('name') if priority_indicator else None,
            duration_seconds=duration_seconds
        )

        session.set_indicators(indicators)
        session.set_feedback(feedback)

        if recommended_exercise:
            session.set_recommended_exercise(recommended_exercise)

        db.session.add(session)
        db.session.commit()

        # Mettre à jour le profil utilisateur
        ProfileService.update_user_profile(user_id)

        return session

    @staticmethod
    def update_user_profile(user_id: int):
        """
        Met à jour le profil agrégé de l'utilisateur basé sur toutes ses sessions

        Args:
            user_id: ID de l'utilisateur
        """
        # Récupérer ou créer le profil
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)

        # Récupérer toutes les sessions
        sessions = PoseSession.query.filter_by(user_id=user_id).all()

        if not sessions:
            db.session.commit()
            return

        # 1. Statistiques globales
        profile.total_sessions = len(sessions)
        profile.average_global_score = sum(s.global_score for s in sessions) / len(sessions)

        # 2. Meilleure et pire pose
        pose_scores = defaultdict(list)
        for session in sessions:
            pose_scores[session.pose_name].append(session.global_score)

        pose_averages = {pose: sum(scores)/len(scores) for pose, scores in pose_scores.items()}

        if pose_averages:
            best_pose = max(pose_averages.items(), key=lambda x: x[1])
            worst_pose = min(pose_averages.items(), key=lambda x: x[1])

            profile.best_pose = best_pose[0]
            profile.best_pose_score = best_pose[1]
            profile.worst_pose = worst_pose[0]
            profile.worst_pose_score = worst_pose[1]

            # 3. Moyennes par pose et par indicateur
            profile.set_pose_averages(ProfileService._calculate_pose_averages(sessions))

        # 4. Forces et faiblesses
        profile.set_strengths_weaknesses(ProfileService._calculate_strengths_weaknesses(sessions))

        # 5. Progression mensuelle
        profile.set_monthly_progression(ProfileService._calculate_monthly_progression(sessions))

        db.session.commit()

    @staticmethod
    def _calculate_pose_averages(sessions: List[PoseSession]) -> Dict:
        """
        Calcule les moyennes des indicateurs pour chaque pose

        Returns:
            Dict: {"pose_name": {"indicator1": avg_score, "indicator2": avg_score, ...}}
        """
        pose_indicators = defaultdict(lambda: defaultdict(list))

        for session in sessions:
            indicators = session.get_indicators()
            for indicator, score in indicators.items():
                pose_indicators[session.pose_name][indicator].append(score)

        # Calculer les moyennes
        result = {}
        for pose, indicators in pose_indicators.items():
            result[pose] = {
                indicator: round(sum(scores) / len(scores), 1)
                for indicator, scores in indicators.items()
            }

        return result

    @staticmethod
    def _calculate_strengths_weaknesses(sessions: List[PoseSession]) -> Dict:
        """
        Identifie les forces et faiblesses globales de l'utilisateur

        Returns:
            Dict: {"strengths": [...], "weaknesses": [...]}
        """
        # Agréger tous les indicateurs de toutes les poses
        all_indicators = defaultdict(list)

        for session in sessions:
            indicators = session.get_indicators()
            for indicator, score in indicators.items():
                all_indicators[indicator].append(score)

        # Calculer les moyennes
        indicator_averages = {
            indicator: sum(scores) / len(scores)
            for indicator, scores in all_indicators.items()
        }

        # Trier par score
        sorted_indicators = sorted(indicator_averages.items(), key=lambda x: x[1], reverse=True)

        # Les 3 meilleures = forces, les 3 pires = faiblesses
        strengths = [ind for ind, score in sorted_indicators[:3] if score >= 70]
        weaknesses = [ind for ind, score in sorted_indicators[-3:] if score < 70]

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "indicator_averages": {k: round(v, 1) for k, v in indicator_averages.items()}
        }

    @staticmethod
    def _calculate_monthly_progression(sessions: List[PoseSession]) -> Dict:
        """
        Calcule la progression mensuelle

        Returns:
            Dict: {"2024-01": {"avg_score": 75.5, "sessions": 10, "poses": {...}}, ...}
        """
        monthly_data = defaultdict(lambda: {"scores": [], "sessions": 0, "poses": defaultdict(int)})

        for session in sessions:
            if not session.created_at:
                continue

            month_key = session.created_at.strftime("%Y-%m")
            monthly_data[month_key]["scores"].append(session.global_score)
            monthly_data[month_key]["sessions"] += 1
            monthly_data[month_key]["poses"][session.pose_name] += 1

        # Calculer les moyennes
        result = {}
        for month, data in monthly_data.items():
            result[month] = {
                "avg_score": round(sum(data["scores"]) / len(data["scores"]), 1),
                "sessions": data["sessions"],
                "poses": dict(data["poses"])
            }

        return result

    @staticmethod
    def get_user_history(user_id: int, limit: int = 20, offset: int = 0,
                        pose_filter: Optional[str] = None) -> List[Dict]:
        """
        Récupère l'historique des sessions d'un utilisateur

        Args:
            user_id: ID de l'utilisateur
            limit: Nombre max de résultats
            offset: Offset pour pagination
            pose_filter: Filtrer par nom de pose (optionnel)

        Returns:
            Liste des sessions
        """
        query = PoseSession.query.filter_by(user_id=user_id)

        if pose_filter:
            query = query.filter_by(pose_name=pose_filter)

        sessions = query.order_by(desc(PoseSession.created_at)).limit(limit).offset(offset).all()

        return [session.to_dict() for session in sessions]

    @staticmethod
    def get_session_statistics(user_id: int, days: int = 30) -> Dict:
        """
        Récupère des statistiques sur une période donnée

        Args:
            user_id: ID de l'utilisateur
            days: Nombre de jours à analyser

        Returns:
            Dict avec les statistiques
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        sessions = PoseSession.query.filter(
            PoseSession.user_id == user_id,
            PoseSession.created_at >= start_date
        ).all()

        if not sessions:
            return {
                "period_days": days,
                "total_sessions": 0,
                "average_score": 0,
                "improvement_trend": "no_data"
            }

        scores = [s.global_score for s in sessions]
        avg_score = sum(scores) / len(scores)

        # Calculer la tendance (première moitié vs deuxième moitié)
        mid_point = len(scores) // 2
        if mid_point > 0:
            first_half_avg = sum(scores[:mid_point]) / mid_point
            second_half_avg = sum(scores[mid_point:]) / (len(scores) - mid_point)
            improvement = second_half_avg - first_half_avg

            if improvement > 5:
                trend = "improving"
            elif improvement < -5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        # Poses pratiquées
        pose_counts = defaultdict(int)
        for session in sessions:
            pose_counts[session.pose_name] += 1

        return {
            "period_days": days,
            "total_sessions": len(sessions),
            "average_score": round(avg_score, 1),
            "improvement_trend": trend,
            "poses_practiced": dict(pose_counts),
            "best_score": round(max(scores), 1),
            "worst_score": round(min(scores), 1)
        }

    @staticmethod
    def get_pose_progress(user_id: int, pose_name: str) -> Dict:
        """
        Récupère la progression pour une pose spécifique

        Args:
            user_id: ID de l'utilisateur
            pose_name: Nom de la pose

        Returns:
            Dict avec la progression
        """
        sessions = PoseSession.query.filter_by(
            user_id=user_id,
            pose_name=pose_name
        ).order_by(PoseSession.created_at).all()

        if not sessions:
            return {
                "pose": pose_name,
                "total_sessions": 0,
                "progression": []
            }

        progression = []
        for session in sessions:
            progression.append({
                "date": session.created_at.isoformat() if session.created_at else None,
                "global_score": session.global_score,
                "indicators": session.get_indicators(),
                "priority_indicator": session.priority_indicator
            })

        # Calculer la tendance
        scores = [s.global_score for s in sessions]
        first_score = scores[0]
        last_score = scores[-1]
        improvement = last_score - first_score

        return {
            "pose": pose_name,
            "total_sessions": len(sessions),
            "first_score": round(first_score, 1),
            "last_score": round(last_score, 1),
            "improvement": round(improvement, 1),
            "progression": progression
        }

    @staticmethod
    def delete_session(session_id: int, user_id: int) -> bool:
        """
        Supprime une session (avec vérification que l'utilisateur en est le propriétaire)

        Args:
            session_id: ID de la session à supprimer
            user_id: ID de l'utilisateur (pour sécurité)

        Returns:
            True si suppression réussie
        """
        session = PoseSession.query.filter_by(id=session_id, user_id=user_id).first()

        if not session:
            return False

        db.session.delete(session)
        db.session.commit()

        # Recalculer le profil
        ProfileService.update_user_profile(user_id)

        return True
