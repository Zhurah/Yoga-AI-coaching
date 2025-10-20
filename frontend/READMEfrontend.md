# 🧘 Yoga Coaching AI - Frontend

Application React pour l'analyse de poses de yoga avec MediaPipe et Machine Learning.

## 🚀 Installation
```bash
# Installer les dépendances
npm install

# Démarrer l'application en mode développement
npm start
```

L'application sera disponible sur `http://localhost:3000`

## 🔧 Configuration

Créez un fichier `.env` à la racine du projet frontend :
```bash
REACT_APP_API_URL=http://localhost:5000/api
```

## 📦 Dépendances principales

- **React 18** - Framework UI
- **MediaPipe Pose** - Détection de pose en temps réel
- **Axios** - Requêtes HTTP vers le backend
- **MediaPipe Drawing Utils** - Visualisation des keypoints

## 🏗️ Structure du projet
```
src/
├── components/          # Composants React
│   ├── FileUploader     # Upload de fichiers
│   ├── MediaPipeProcessor  # Traitement MediaPipe
│   ├── WebcamCapture    # Capture webcam
│   └── ResultsPanel     # Affichage des résultats
├── services/            # Services (API, MediaPipe)
├── utils/               # Utilitaires (dessin, calculs)
└── App.jsx              # Composant principal
```

## 🎯 Fonctionnalités

✅ Upload d'images et vidéos  
✅ Capture webcam en temps réel  
✅ Détection de pose avec MediaPipe  
✅ Classification automatique de pose  
✅ Analyse qualitative détaillée  
✅ Feedback pédagogique personnalisé  
✅ Interface responsive  

## 🔗 Connexion au Backend

Assurez-vous que le backend Flask est démarré sur le port 5000 :
```bash
cd ../backend
python api.py
```

## 🧪 Tests
```bash
npm test
```

## 📦 Build Production
```bash
npm run build
```

Crée un dossier `build/` optimisé pour la production.

## 🐛 Dépannage

### Problème : CORS Error
**Solution** : Vérifiez que `flask-cors` est installé dans le backend et que l'URL de l'API est correcte dans `.env`

### Problème : MediaPipe ne charge pas
**Solution** : Vérifiez votre connexion internet (MediaPipe charge depuis un CDN)

### Problème : Webcam ne fonctionne pas
**Solution** : 
- Autorisez l'accès à la caméra dans votre navigateur
- Utilisez HTTPS en production (requis pour getUserMedia)

## 📚 Documentation

- [MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose.html)
- [React Documentation](https://react.dev/)
- [Axios Documentation](https://axios-http.com/)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 📝 License

MIT License