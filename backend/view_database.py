"""
Script pour visualiser le contenu de la base de données
Usage: python3 view_database.py
"""
from flask import Flask
from models import db, User, PoseSession, UserProfile
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'instance', 'yoga_coaching.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def display_database():
    """Affiche tout le contenu de la base de données"""
    with app.app_context():
        print("\n" + "="*80)
        print("📊 CONTENU DE LA BASE DE DONNÉES YOGA COACHING")
        print("="*80)
        print(f"📂 Fichier : {db_path}")
        print(f"✅ Existe : {os.path.exists(db_path)}")
        print("="*80)

        # ============================================================
        # TABLE USERS
        # ============================================================
        print("\n👤 TABLE USERS (Utilisateurs)")
        print("-"*80)

        users = User.query.all()

        if not users:
            print("⚠️  Aucun utilisateur trouvé")
        else:
            print(f"📊 Total : {len(users)} utilisateur(s)\n")

            for user in users:
                print(f"🆔 ID : {user.id}")
                print(f"   📧 Email : {user.email}")
                print(f"   👤 Username : {user.username}")
                print(f"   🎯 Niveau : {user.skill_level}")
                print(f"   📅 Créé le : {user.created_at.strftime('%d/%m/%Y %H:%M') if user.created_at else 'N/A'}")
                print(f"   🔐 Dernière connexion : {user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Jamais'}")
                print(f"   📊 Nombre de sessions : {len(user.sessions.all())}")
                print("-"*80)

        # ============================================================
        # TABLE POSE_SESSIONS
        # ============================================================
        print("\n🧘 TABLE POSE_SESSIONS (Historique des analyses)")
        print("-"*80)

        sessions = PoseSession.query.all()

        if not sessions:
            print("⚠️  Aucune session trouvée")
            print("💡 Les analyses de pose ne sont pas encore enregistrées automatiquement.")
            print("   Pour implémenter cette fonctionnalité, demandez à Claude !")
        else:
            print(f"📊 Total : {len(sessions)} session(s)\n")

            for session in sessions:
                print(f"🆔 ID : {session.id}")
                print(f"   👤 Utilisateur : {session.user.username} ({session.user.email})")
                print(f"   🧘 Pose : {session.pose_name}")
                print(f"   🎯 Confiance : {session.confidence:.1%}")
                print(f"   ⭐ Score global : {session.global_score:.1f}/100")
                print(f"   📊 Indicateurs : {session.get_indicators()}")
                print(f"   💬 Feedback : {len(session.get_feedback())} message(s)")
                print(f"   📅 Date : {session.created_at.strftime('%d/%m/%Y %H:%M')}")
                print("-"*80)

        # ============================================================
        # TABLE USER_PROFILES
        # ============================================================
        print("\n📈 TABLE USER_PROFILES (Profils posturaux)")
        print("-"*80)

        profiles = UserProfile.query.all()

        if not profiles:
            print("⚠️  Aucun profil trouvé")
        else:
            print(f"📊 Total : {len(profiles)} profil(s)\n")

            for profile in profiles:
                user = User.query.get(profile.user_id)
                print(f"👤 Utilisateur : {user.username}")
                print(f"   📊 Sessions totales : {profile.total_sessions}")
                print(f"   ⭐ Score moyen : {profile.average_global_score:.1f}/100")
                print(f"   🏆 Meilleure pose : {profile.best_pose} ({profile.best_pose_score:.1f})")
                print(f"   ⚠️  Pire pose : {profile.worst_pose} ({profile.worst_pose_score:.1f})")
                print(f"   📅 Mis à jour : {profile.updated_at.strftime('%d/%m/%Y %H:%M') if profile.updated_at else 'N/A'}")
                print("-"*80)

        # ============================================================
        # STATISTIQUES GLOBALES
        # ============================================================
        print("\n📊 STATISTIQUES GLOBALES")
        print("-"*80)
        print(f"👥 Total utilisateurs : {len(users)}")
        print(f"🧘 Total sessions : {len(sessions)}")
        print(f"📈 Total profils : {len(profiles)}")

        if sessions:
            avg_score = sum(s.global_score for s in sessions) / len(sessions)
            print(f"⭐ Score moyen global : {avg_score:.1f}/100")

            # Poses les plus pratiquées
            poses_count = {}
            for s in sessions:
                poses_count[s.pose_name] = poses_count.get(s.pose_name, 0) + 1

            print(f"\n🧘 Poses les plus pratiquées :")
            for pose, count in sorted(poses_count.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {pose} : {count} session(s)")

        print("\n" + "="*80)

if __name__ == '__main__':
    display_database()
