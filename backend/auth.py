"""
Système d'authentification avec JWT
Gère l'inscription, la connexion et la validation des tokens
"""
from flask import jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import datetime, timedelta
from models import db, User, UserProfile
import re


jwt = JWTManager()

# Configuration JWT
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


def validate_email(email):
    """Valide le format de l'email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Valide la force du mot de passe
    - Au moins 8 caractères
    - Au moins une lettre majuscule
    - Au moins une lettre minuscule
    - Au moins un chiffre
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"

    if not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une lettre majuscule"

    if not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une lettre minuscule"

    if not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"

    return True, "OK"


def register_user(email, username, password, skill_level='beginner'):
    """
    Enregistre un nouvel utilisateur

    Returns:
        tuple: (success: bool, message: str, user_dict: dict or None)
    """
    # Validation email
    if not validate_email(email):
        return False, "Format d'email invalide", None

    # Validation password
    is_valid, msg = validate_password(password)
    if not is_valid:
        return False, msg, None

    # Vérifier si l'email existe déjà
    if User.query.filter_by(email=email).first():
        return False, "Cet email est déjà utilisé", None

    # Vérifier si le username existe déjà
    if User.query.filter_by(username=username).first():
        return False, "Ce nom d'utilisateur est déjà pris", None

    try:
        # Créer l'utilisateur
        user = User(
            email=email,
            username=username,
            skill_level=skill_level
        )
        user.set_password(password)

        db.session.add(user)
        db.session.flush()  # Pour obtenir l'ID

        # Créer le profil utilisateur vide
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)

        db.session.commit()

        return True, "Utilisateur créé avec succès", user.to_dict()

    except Exception as e:
        db.session.rollback()
        return False, f"Erreur lors de la création: {str(e)}", None


def login_user(email, password):
    """
    Connecte un utilisateur et génère les tokens JWT

    Returns:
        tuple: (success: bool, message: str, tokens: dict or None, user: dict or None)
    """
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return False, "Email ou mot de passe incorrect", None, None

    # Mettre à jour last_login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Générer les tokens (identity doit être une chaîne)
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'username': user.username, 'email': user.email}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer'
    }

    return True, "Connexion réussie", tokens, user.to_dict()


def get_current_user_id():
    """Récupère l'ID de l'utilisateur connecté depuis le token JWT (convertit en int)"""
    identity = get_jwt_identity()
    return int(identity) if identity else None


def get_current_user():
    """Récupère l'utilisateur connecté complet"""
    user_id = get_current_user_id()
    return User.query.get(user_id)


# ============================================================================
# ROUTES D'AUTHENTIFICATION
# ============================================================================

def register_auth_routes(app):
    """Enregistre les routes d'authentification"""

    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Route d'inscription"""
        try:
            data = request.json

            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            skill_level = data.get('skill_level', 'beginner')

            if not email or not username or not password:
                return jsonify({
                    'success': False,
                    'error': 'Email, username et password requis'
                }), 400

            success, message, user_dict = register_user(
                email, username, password, skill_level
            )

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'user': user_dict
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 400

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Route de connexion"""
        try:
            data = request.json

            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({
                    'success': False,
                    'error': 'Email et password requis'
                }), 400

            success, message, tokens, user_dict = login_user(email, password)

            if success:
                return jsonify({
                    'success': True,
                    'message': message,
                    'tokens': tokens,
                    'user': user_dict
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 401

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        """Rafraîchit le token d'accès"""
        try:
            user_id = get_current_user_id()
            user = User.query.get(user_id)

            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur introuvable'
                }), 404

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={'username': user.username, 'email': user.email}
            )

            return jsonify({
                'success': True,
                'access_token': access_token
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required()
    def get_me():
        """Récupère les informations de l'utilisateur connecté"""
        try:
            user = get_current_user()

            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Utilisateur introuvable'
                }), 404

            return jsonify({
                'success': True,
                'user': user.to_dict()
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/auth/logout', methods=['POST'])
    @jwt_required()
    def logout():
        """
        Déconnexion (côté client principalement)
        Le token reste valide jusqu'à expiration
        Pour une vraie révocation, il faudrait implémenter une blacklist
        """
        return jsonify({
            'success': True,
            'message': 'Déconnexion réussie'
        }), 200

    print("✅ Routes d'authentification enregistrées")
