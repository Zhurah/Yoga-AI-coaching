"""
Routes pour le profil utilisateur et l'historique des sessions
Nécessite une authentification JWT
"""
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, PoseSession, UserProfile
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json


def register_profile_routes(app):
    """Enregistre les routes de profil"""

    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        """
        Récupère le profil complet de l'utilisateur connecté
        Inclut: informations utilisateur + profil postural agrégé
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur introuvable'
                }), 404

            # Récupérer ou créer le profil postural
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                profile = UserProfile(user_id=user_id)
                db.session.add(profile)
                db.session.commit()

            # Construire la réponse
            response = {
                'success': True,
                'profile': {
                    **user.to_dict(),
                    'postural_stats': profile.to_dict() if profile else {}
                }
            }

            return jsonify(response), 200

        except Exception as e:
            print(f"❌ Erreur get_profile: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/profile/history', methods=['GET'])
    @jwt_required()
    def get_history():
        """
        Récupère l'historique des sessions de l'utilisateur
        Query params:
            - page: numéro de page (défaut: 1)
            - per_page: sessions par page (défaut: 20)
        """
        try:
            user_id = get_jwt_identity()
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)

            # Pagination
            pagination = PoseSession.query.filter_by(user_id=user_id)\
                .order_by(desc(PoseSession.created_at))\
                .paginate(page=page, per_page=per_page, error_out=False)

            sessions = [session.to_dict() for session in pagination.items]

            return jsonify({
                'success': True,
                'sessions': sessions,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }), 200

        except Exception as e:
            print(f"❌ Erreur get_history: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/profile/statistics', methods=['GET'])
    @jwt_required()
    def get_statistics():
        """
        Calcule les statistiques sur une période donnée
        Query params:
            - days: nombre de jours à analyser (défaut: 30)
        """
        try:
            user_id = get_jwt_identity()
            days = request.args.get('days', 30, type=int)

            # Date de début
            start_date = datetime.utcnow() - timedelta(days=days)

            # Sessions dans la période
            sessions = PoseSession.query.filter(
                PoseSession.user_id == user_id,
                PoseSession.created_at >= start_date
            ).all()

            if not sessions:
                return jsonify({
                    'success': True,
                    'statistics': {
                        'total_sessions': 0,
                        'average_score': 0,
                        'best_score': 0,
                        'worst_score': 0,
                        'poses_distribution': {},
                        'evolution': []
                    }
                }), 200

            # Calculer les statistiques
            scores = [s.global_score for s in sessions]
            poses_count = {}

            for session in sessions:
                poses_count[session.pose_name] = poses_count.get(session.pose_name, 0) + 1

            # Évolution (groupé par jour)
            evolution = {}
            for session in sessions:
                day_key = session.created_at.strftime('%Y-%m-%d')
                if day_key not in evolution:
                    evolution[day_key] = []
                evolution[day_key].append(session.global_score)

            # Moyennes par jour
            evolution_data = [
                {
                    'date': day,
                    'average_score': sum(scores_list) / len(scores_list),
                    'count': len(scores_list)
                }
                for day, scores_list in sorted(evolution.items())
            ]

            statistics = {
                'total_sessions': len(sessions),
                'average_score': sum(scores) / len(scores),
                'best_score': max(scores),
                'worst_score': min(scores),
                'poses_distribution': poses_count,
                'evolution': evolution_data
            }

            return jsonify({
                'success': True,
                'statistics': statistics
            }), 200

        except Exception as e:
            print(f"❌ Erreur get_statistics: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/profile/pose-progress/<pose_name>', methods=['GET'])
    @jwt_required()
    def get_pose_progress(pose_name):
        """
        Récupère la progression pour une pose spécifique
        """
        try:
            user_id = get_jwt_identity()

            # Toutes les sessions pour cette pose
            sessions = PoseSession.query.filter_by(
                user_id=user_id,
                pose_name=pose_name
            ).order_by(PoseSession.created_at).all()

            if not sessions:
                return jsonify({
                    'success': True,
                    'progress': {
                        'pose_name': pose_name,
                        'total_attempts': 0,
                        'sessions': [],
                        'average_indicators': {}
                    }
                }), 200

            # Calculer les moyennes des indicateurs
            all_indicators = {}
            for session in sessions:
                indicators = session.get_indicators()
                for key, value in indicators.items():
                    if key not in all_indicators:
                        all_indicators[key] = []
                    all_indicators[key].append(value)

            average_indicators = {
                key: sum(values) / len(values)
                for key, values in all_indicators.items()
            }

            progress = {
                'pose_name': pose_name,
                'total_attempts': len(sessions),
                'sessions': [session.to_dict() for session in sessions],
                'average_indicators': average_indicators,
                'best_score': max(s.global_score for s in sessions),
                'latest_score': sessions[-1].global_score
            }

            return jsonify({
                'success': True,
                'progress': progress
            }), 200

        except Exception as e:
            print(f"❌ Erreur get_pose_progress: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/profile/session/<int:session_id>', methods=['DELETE'])
    @jwt_required()
    def delete_session(session_id):
        """
        Supprime une session de l'historique
        """
        try:
            user_id = get_jwt_identity()

            # Vérifier que la session appartient à l'utilisateur
            session = PoseSession.query.filter_by(
                id=session_id,
                user_id=user_id
            ).first()

            if not session:
                return jsonify({
                    'success': False,
                    'error': 'Session introuvable ou accès refusé'
                }), 404

            db.session.delete(session)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Session supprimée avec succès'
            }), 200

        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur delete_session: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    print("✅ Routes de profil enregistrées")
