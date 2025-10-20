"""
Script pour créer la base de données SQLite sans démarrer l'API
Usage: python3 create_db.py
"""
from flask import Flask
from models import db, init_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yoga_coaching.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("Création de la base de données...")
init_db(app)
print("✅ Base de données créée : /Users/aurelienanand/yoga_project/backend/yoga_coaching.db")
print("\nVous pouvez maintenant la consulter avec :")
print("  sqlite3 yoga_coaching.db")
print("  sqlite> .tables")
print("  sqlite> .schema users")
print("  sqlite> .quit")
