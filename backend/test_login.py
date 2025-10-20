"""
Script de test pour diagnostiquer les problèmes de login
"""
from flask import Flask
from models import db, User
from auth import login_user
import sys

import os

app = Flask(__name__)

# Chemin absolu vers la base de données
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'instance', 'yoga_coaching.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'CHANGE_ME_IN_PRODUCTION_USE_ENV_VAR'

print(f"📂 Chemin de la base de données : {db_path}")
print(f"   Existe ? {os.path.exists(db_path)}\n")

db.init_app(app)

def test_login(email, password):
    """Teste la connexion avec un email et mot de passe"""
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"TEST DE CONNEXION")
        print(f"{'='*60}")
        print(f"Email : {email}")
        print(f"Mot de passe : {password}")
        print(f"{'='*60}\n")

        # 1. Chercher l'utilisateur
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"❌ ERREUR : Aucun utilisateur trouvé avec l'email '{email}'")
            print("\n📋 Utilisateurs disponibles :")
            all_users = User.query.all()
            for u in all_users:
                print(f"   - {u.email} (username: {u.username})")
            return

        print(f"✅ Utilisateur trouvé : {user.username}")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Skill level: {user.skill_level}")

        # 2. Vérifier le mot de passe
        print(f"\n🔐 Test de vérification du mot de passe...")
        password_ok = user.check_password(password)

        if password_ok:
            print(f"✅ Mot de passe CORRECT !")
            print(f"\n🎉 La connexion devrait fonctionner !")
        else:
            print(f"❌ Mot de passe INCORRECT !")
            print(f"\n💡 Suggestions :")
            print(f"   - Vérifiez les majuscules/minuscules")
            print(f"   - Vérifiez les espaces avant/après")
            print(f"   - Hash stocké : {user.password_hash[:50]}...")

            # Test avec des variantes communes
            print(f"\n🔍 Test avec des variantes :")
            variants = [
                password.lower(),
                password.upper(),
                password.strip(),
                password.capitalize()
            ]
            for variant in variants:
                if user.check_password(variant):
                    print(f"   ✅ Trouvé avec : '{variant}'")
                    return

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 test_login.py <email> <password>")
        print("\nExemple:")
        print("  python3 test_login.py aurelien.anand@yahoo.com VotreMotDePasse")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    test_login(email, password)
