"""
Modèles de base de données pour le système de coaching yoga
Utilise SQLAlchemy pour l'ORM et SQLite comme base de données
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class User(db.Model):
    """Modèle utilisateur avec authentification"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Profil utilisateur
    skill_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced, expert
    preferred_poses = db.Column(db.String(255))  # JSON array de poses favorites

    # Relations
    sessions = db.relationship('PoseSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash le mot de passe"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convertit en dictionnaire (sans le password)"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'skill_level': self.skill_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class PoseSession(db.Model):
    """Session d'analyse de pose - stocke chaque analyse effectuée"""
    __tablename__ = 'pose_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Informations de la pose
    pose_name = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)

    # Scores et indicateurs (stockés en JSON)
    global_score = db.Column(db.Float, nullable=False)
    indicators = db.Column(db.Text, nullable=False)  # JSON: {"alignment": 85, "symmetry": 90, ...}
    feedback = db.Column(db.Text)  # JSON: ["message1", "message2", ...]
    priority_indicator = db.Column(db.String(50))  # L'indicateur le plus faible

    # Recommandation
    recommended_exercise = db.Column(db.Text)  # JSON avec détails de l'exercice recommandé

    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    duration_seconds = db.Column(db.Integer)  # Durée de la session si applicable

    def set_indicators(self, indicators_dict):
        """Stocke les indicateurs au format JSON"""
        self.indicators = json.dumps(indicators_dict)

    def get_indicators(self):
        """Récupère les indicateurs depuis JSON"""
        return json.loads(self.indicators) if self.indicators else {}

    def set_feedback(self, feedback_list):
        """Stocke le feedback au format JSON"""
        self.feedback = json.dumps(feedback_list)

    def get_feedback(self):
        """Récupère le feedback depuis JSON"""
        return json.loads(self.feedback) if self.feedback else []

    def set_recommended_exercise(self, exercise_dict):
        """Stocke l'exercice recommandé au format JSON"""
        self.recommended_exercise = json.dumps(exercise_dict)

    def get_recommended_exercise(self):
        """Récupère l'exercice recommandé depuis JSON"""
        return json.loads(self.recommended_exercise) if self.recommended_exercise else None

    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'pose_name': self.pose_name,
            'confidence': self.confidence,
            'global_score': self.global_score,
            'indicators': self.get_indicators(),
            'feedback': self.get_feedback(),
            'priority_indicator': self.priority_indicator,
            'recommended_exercise': self.get_recommended_exercise(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_seconds': self.duration_seconds
        }


class UserProfile(db.Model):
    """Profil postural agrégé de l'utilisateur - statistiques globales"""
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # Statistiques globales
    total_sessions = db.Column(db.Integer, default=0)
    average_global_score = db.Column(db.Float, default=0.0)

    # Meilleure et pire pose
    best_pose = db.Column(db.String(50))
    best_pose_score = db.Column(db.Float, default=0.0)
    worst_pose = db.Column(db.String(50))
    worst_pose_score = db.Column(db.Float, default=100.0)

    # Indicateurs agrégés par pose (JSON)
    # Format: {"downdog": {"alignment": 85, "symmetry": 90, ...}, "plank": {...}, ...}
    pose_averages = db.Column(db.Text)

    # Points forts et faibles (JSON)
    # Format: {"strengths": ["symmetry", "alignment"], "weaknesses": ["flexibility", "stability"]}
    strengths_weaknesses = db.Column(db.Text)

    # Progression (JSON) - optionnel pour suivi temporel
    # Format: {"2024-01": {"avg_score": 75, "sessions": 10}, "2024-02": {...}, ...}
    monthly_progression = db.Column(db.Text)

    # Dernière mise à jour
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_pose_averages(self, averages_dict):
        """Stocke les moyennes par pose"""
        self.pose_averages = json.dumps(averages_dict)

    def get_pose_averages(self):
        """Récupère les moyennes par pose"""
        return json.loads(self.pose_averages) if self.pose_averages else {}

    def set_strengths_weaknesses(self, data_dict):
        """Stocke les forces et faiblesses"""
        self.strengths_weaknesses = json.dumps(data_dict)

    def get_strengths_weaknesses(self):
        """Récupère les forces et faiblesses"""
        return json.loads(self.strengths_weaknesses) if self.strengths_weaknesses else {}

    def set_monthly_progression(self, progression_dict):
        """Stocke la progression mensuelle"""
        self.monthly_progression = json.dumps(progression_dict)

    def get_monthly_progression(self):
        """Récupère la progression mensuelle"""
        return json.loads(self.monthly_progression) if self.monthly_progression else {}

    def to_dict(self):
        """Convertit en dictionnaire"""
        return {
            'user_id': self.user_id,
            'total_sessions': self.total_sessions,
            'average_global_score': self.average_global_score,
            'best_pose': self.best_pose,
            'best_pose_score': self.best_pose_score,
            'worst_pose': self.worst_pose,
            'worst_pose_score': self.worst_pose_score,
            'pose_averages': self.get_pose_averages(),
            'strengths_weaknesses': self.get_strengths_weaknesses(),
            'monthly_progression': self.get_monthly_progression(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


def init_db(app):
    """Initialise la base de données"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("✅ Base de données initialisée")
