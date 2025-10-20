# 🚀 Guide de Démarrage Rapide - API V2

Cette version inclut :
- ✅ Authentification JWT complète
- ✅ Profils utilisateurs avec historique
- ✅ Score global et niveau de compétence
- ✅ Identification de l'indicateur prioritaire
- ✅ Recommandations d'exercices personnalisées
- ✅ Base de données SQLite pour la persistance

## Installation

### 1. Installer les nouvelles dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurer les variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Générer une clé secrète JWT sécurisée
python -c "import secrets; print(secrets.token_hex(32))"

# Éditer .env et remplacer JWT_SECRET_KEY avec la clé générée
nano .env  # ou votre éditeur préféré
```

### 3. Initialiser la base de données

La base de données sera créée automatiquement au premier lancement de l'API.

```bash
python api_v2.py
```

La base de données `yoga_coach.db` sera créée dans le dossier `backend/`.

## Lancement de l'API

```bash
cd backend
python api_v2.py
```

L'API sera disponible sur `http://localhost:8000`

## Test des Endpoints

### 1. Inscription d'un utilisateur

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test1234",
    "skill_level": "beginner"
  }'
```

Réponse attendue :
```json
{
  "success": true,
  "message": "Utilisateur créé avec succès",
  "user": {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser",
    "skill_level": "beginner"
  }
}
```

### 2. Connexion

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

Réponse :
```json
{
  "success": true,
  "message": "Connexion réussie",
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer"
  },
  "user": {...}
}
```

**Important** : Copier le `access_token` pour les requêtes suivantes.

### 3. Analyse complète d'une pose (authentifiée)

```bash
curl -X POST http://localhost:8000/api/analyze-complete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN" \
  -d '{
    "landmarks": [...],  // 33 landmarks MediaPipe
    "save_session": true
  }'
```

Réponse :
```json
{
  "success": true,
  "classification": {
    "pose": "plank",
    "confidence": 0.94
  },
  "quality_analysis": {
    "global_score": 81.5,
    "indicators": {
      "alignment": 92.3,
      "core_strength": 100.0,
      "symmetry": 87.5,
      "shoulder_position": 85.2
    },
    "feedback": ["✓✓ Alignement parfait !", ...],
    "priority_indicator": {
      "name": "shoulder_position",
      "score": 85.2,
      "improvement_needed": "modéré"
    },
    "skill_level": "advanced",
    "recommended_exercise": {
      "title": "Renforcement des Épaules en Position Haute",
      "description": "Stabilisez vos épaules...",
      "steps": [...],
      "duration": "4 minutes",
      "benefit": "...",
      "motivation": "..."
    }
  }
}
```

### 4. Récupérer son profil

```bash
curl -X GET http://localhost:8000/api/profile \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN"
```

### 5. Voir l'historique des sessions

```bash
curl -X GET "http://localhost:8000/api/profile/history?limit=10" \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN"
```

### 6. Statistiques sur 30 jours

```bash
curl -X GET "http://localhost:8000/api/profile/statistics?days=30" \
  -H "Authorization: Bearer VOTRE_ACCESS_TOKEN"
```

## Structure de la Base de Données

### Table `users`
- id, email, username, password_hash
- skill_level (beginner/intermediate/advanced/expert)
- created_at, last_login

### Table `pose_sessions`
- id, user_id, pose_name, confidence
- global_score, indicators (JSON), feedback (JSON)
- priority_indicator, recommended_exercise (JSON)
- created_at

### Table `user_profiles`
- id, user_id
- total_sessions, average_global_score
- best_pose, worst_pose
- pose_averages (JSON), strengths_weaknesses (JSON)
- monthly_progression (JSON)

## Sécurité

### Exigences de Mot de Passe
- Au moins 8 caractères
- Au moins une majuscule
- Au moins une minuscule
- Au moins un chiffre

### Tokens JWT
- Access token : valide 1 heure
- Refresh token : valide 30 jours
- Utiliser `/api/auth/refresh` pour obtenir un nouveau access token

## Migration depuis l'API V1

Si vous utilisiez `api.py`, vous pouvez continuer à l'utiliser pour des analyses sans compte utilisateur. Pour bénéficier des nouvelles fonctionnalités (profils, historique, recommandations), utilisez `api_v2.py`.

Les deux APIs peuvent coexister sur des ports différents :
- V1 : port 8000 (ancien)
- V2 : port 8001 (nouveau)

## Dépannage

### "ModuleNotFoundError: No module named 'flask_sqlalchemy'"

```bash
pip install -r requirements.txt
```

### "Error: Table 'users' already exists"

La base de données a déjà été créée. Si vous voulez repartir de zéro :

```bash
rm yoga_coach.db
python api_v2.py  # Recréera automatiquement
```

### "Invalid token" ou "Token expired"

Reconnectez-vous pour obtenir un nouveau token :

```bash
curl -X POST http://localhost:8000/api/auth/login ...
```

## Prochaines Étapes

1. **Frontend React** : Intégrer Recharts pour les graphiques radar
2. **Dashboard** : Créer les composants de visualisation
3. **Progression** : Implémenter le suivi de progression dans l'UI

Voir `CLAUDE.md` pour la documentation complète.
