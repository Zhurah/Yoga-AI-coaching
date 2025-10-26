# Coach Yoga IA : Analyse de Posture en Temps Réel avec Retour Qualitatif

<div align="center">

**Un système intelligent de coaching yoga combinant Vision par Ordinateur, Machine Learning et Traitement Temps Réel pour fournir un retour instantané et personnalisé sur l'exécution des postures.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-green.svg)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg)](https://opencv.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)

[Fonctionnalités](#-fonctionnalités-clés) • [Démonstration](#-démonstration) • [Architecture](#-architecture) • [Installation](#-installation) • [Utilisation](#-utilisation) • [Détails Techniques](#-détails-techniques)

</div>

---

##  Vue d'Ensemble du Projet

Ce projet implémente un système complet de coaching yoga qui analyse la posture corporelle en temps réel grâce à des techniques avancées de vision par ordinateur et d'apprentissage automatique. Il va au-delà de la simple classification de poses pour fournir un **feedback actionnable et contextuel** sur la qualité d'exécution.

### Le Problème

L'apprentissage traditionnel du yoga nécessite :
- Des cours en présentiel (coûteux, contraintes d'horaires)
- Des tutoriels vidéo génériques (pas de retour personnalisé)
- Difficulté à auto-évaluer sa forme correcte

### La Solution

Un système alimenté par l'IA qui :
-  Détecte et classifie 5 postures de yoga avec **haute précision**
-  Analyse la qualité des poses selon **plusieurs dimensions biomécaniques**
-  Fournit un **coaching personnalisé en temps réel**
-  Fonctionne entièrement **en local** (confidentialité garantie, pas de cloud)

---

## 💻 Installation

### Prérequis
- Python 3.8+
- Webcam (pour les fonctionnalités temps réel)
- 4GB+ RAM recommandé

### Configuration

```bash
# Cloner le dépôt
git clone https://github.com/votreusername/ai-yoga-coach.git
cd ai-yoga-coach

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer les dépendances
cd backend
pip install -r requirements.txt
```

### Entraîner le Modèle (Optionnel)

Si vous souhaitez réentraîner avec vos propres données :

```bash
cd backend
jupyter notebook best_model.ipynb
# Exécuter toutes les cellules pour entraîner et exporter les modèles
```

Les modèles pré-entraînés sont inclus : `best_yoga_model.pkl`, `scaler.pkl`, `label_encoder.pkl`

---

## 🎮 Utilisation

### Coaching Temps Réel (Webcam)

```bash
cd backend
python realtime_app.py
```

**Contrôles :**
- Appuyez sur **Q** pour quitter
- Appuyez sur **ESPACE** pour forcer une analyse immédiate

### Analyser des Images Statiques

```python
from backend.yoga_quality_analyzer import analyze_pose_quality

result = analyze_pose_quality(
    image_path='chemin/vers/image.jpg',
    pose_name='plank'  # ou détection auto avec le classifier
)

print(f"Score Global : {result['quality_analysis']['overall_score']}/100")
print("Feedback :", result['quality_analysis']['feedback'])
```

### Tester sur des Échantillons du Dataset

```bash
cd backend
python test_system.py
# Génère des fichiers result_*.json avec analyse détaillée
```

---

##  Fonctionnalités Clés

### 1. Classification Multi-Classes
- **5 Postures Supportées** : Chien tête en bas, Planche, Arbre, Guerrier II, Déesse
- **Haute Précision** : Entraîné sur un dataset diversifié avec évaluation rigoureuse
- **Score de Confiance** : Ne fournit du feedback que si confiance ≥ 70%

### 2. Analyse Qualitative Intelligente
Chaque posture est analysée selon des **métriques spécifiques** :

| Posture | Métriques Clés Analysées |
|---------|--------------------------|
| **Chien Tête en Bas** | Alignement hanches-épaules-chevilles, extension des bras, rectitude des jambes, symétrie |
| **Planche** | Alignement du corps, engagement du core, positionnement des épaules, symétrie |
| **Arbre** | Équilibre vertical, hauteur du pied, ouverture de la hanche, niveau des épaules |
| **Guerrier II** | Alignement des bras, flexion du genou (90°), alignement genou-cheville, ouverture hanches |
| **Déesse** | Largeur de l'écartement, profondeur du squat, alignement genoux-chevilles, posture du dos |

### 3. Système de Feedback Contextuel
- **Niveaux de Sévérité** : Excellent (✓✓), Bon (✓), Attention (⚠️), Conseils (💡), Encouragement (💪)
- **Guidance Actionnable** : "Poussez les genoux vers l'extérieur, alignés avec les pieds" vs. "améliorez la forme" générique
- **Coaching Progressif** : Reconnaît les modifications pour débutants

### 4. Application Webcam Temps Réel
- Détection et analyse de pose en direct
- Overlay visuel avec suivi du squelette
- Fréquence d'analyse configurable (par défaut : intervalles de 3s)
- Latence minimale (<100ms par frame)

---

## 📊 Démonstration

### Sortie d'Analyse Temps Réel

```json
{
  "classification": {
    "pose": "plank",
    "confidence": 94.2
  },
  "quality_analysis": {
    "overall_score": 87.3,
    "indicators": {
      "alignment": 92.3,
      "core_strength": 100.0,
      "symmetry": 87.5,
      "shoulder_position": 85.2
    },
    "feedback": [
      "✓✓ Alignement parfait ! Corps bien droit.",
      "✓✓ Planche complète ! Excellente force du core.",
      "✓ Répartissez le poids équitablement."
    ]
  }
}
```

### Visualisation de l'Analyse

Lorsque vous lancez l'application temps réel, vous verrez :
- **Overlay du squelette** sur votre corps (articulations vertes, connexions rouges)
- **Pose détectée** avec pourcentage de confiance
- **Score de qualité** sur 100
- **Top 3 des indicateurs** avec code couleur selon la performance
- **Feedback instantané** en bas de l'écran

---

## Architecture

### Conception du Système

```
┌─────────────────┐
│  Entrée Vidéo   │ (Webcam / Image)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Estimation de Pose MediaPipe   │ (33 Landmarks 3D)
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Feature Engineering            │ (56 Features)
│  • Angles articulaires (8)      │
│  • Distances (6)                │
│  • Ratios (2)                   │
│  • Métriques de symétrie        │
└────────┬────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
┌────────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Scaler        │  │  Classifier  │  │  Analyseur       │
│  (Normalise)   │→ │  (Modèle ML) │→ │  de Qualité      │
└────────────────┘  └──────────────┘  └──────────────────┘
                            │                  │
                            ▼                  ▼
                    ┌──────────────────────────────────┐
                    │  Pose + Confiance + Feedback     │
                    └──────────────────────────────────┘
```

### Composants Principaux

1. **`best_model.ipynb`** : Pipeline d'entraînement avec optimisation d'hyperparamètres (Random Forest, SVM, XGBoost)
2. **`yoga_quality_analyzer.py`** : Moteur d'analyse qualitative modulaire avec évaluateurs spécifiques par pose
3. **`realtime_app.py`** : Application webcam temps réel avec OpenCV
4. **`test_system.py`** : Framework de test et validation end-to-end

---

## 🔬 Détails Techniques

### Feature Engineering

À partir des 33 landmarks 3D de MediaPipe (132 valeurs), nous extrayons **56 features engineerées** :

**Features Géométriques :**
- 13 positions de landmarks clés (nez, épaules, coudes, poignets, hanches, genoux, chevilles)
- 8 angles articulaires (flexion coudes, extension épaules, flexion hanches, angles genoux)
- 6 métriques de distance (largeur épaules, largeur hanches, envergures des membres)

**Features Dérivées :**
- Proportions corporelles (ratio épaules/hanches)
- Alignement vertical (distance nez-hanches)
- Indicateurs de symétrie (distance chevilles gauche-droite)
- Score de confiance (visibilité moyenne des landmarks)

### Pipeline Machine Learning

1. **Augmentation de Données** : Miroirs horizontaux pour variations gauche-droite
2. **Prétraitement** : Normalisation StandardScaler
3. **Sélection de Modèle** : Grid search sur :
   - Random Forest (tuning `n_estimators`, `max_depth`, `min_samples_split`)
   - SVM avec noyau RBF (tuning `C`, `gamma`)
   - XGBoost (tuning `n_estimators`, `learning_rate`, `max_depth`)
4. **Évaluation** : Validation croisée K-Fold stratifiée, analyse de matrice de confusion
5. **Export** : Meilleur modèle sérialisé avec joblib

### Algorithme d'Analyse Qualitative

Chaque pose dispose d'un **analyseur dédié** implémentant :

1. **Extraction de Landmarks** : Identifier les parties du corps pertinentes pour la pose
2. **Calcul de Métriques** : Calculer les indicateurs spécifiques (ex: angle genou pour Guerrier II)
3. **Seuillage** : Comparer aux plages idéales (ex: 85-95° pour squat parfait)
4. **Génération de Feedback** : Mapper les scores vers du texte actionnable avec marqueurs de sévérité
5. **Agrégation** : Calculer le score de qualité global comme moyenne pondérée

**Exemple : Analyse de la Planche**
```python
def _analyze_plank(self, landmarks):
    # 1. Calculer la déviation par rapport à la ligne droite idéale
    alignment_score = 100 - deviation_from_straight * 300

    # 2. Détecter planche modifiée (genoux) vs complète
    if knee_to_ankle_dist < 0.05:
        core_strength = 40  # Planche modifiée détectée
    else:
        core_strength = 100

    # 3. Vérifier alignement vertical épaules-poignets
    shoulder_position = calculate_vertical_alignment(shoulders, wrists)

    return {
        "indicators": {alignment, core_strength, shoulder_position, ...},
        "feedback": [...]
    }
```

### Caractéristiques de Performance

- **Vitesse d'Inférence** : ~30 FPS sur CPU (Intel i5)
- **Taille Modèle** : <5MB (tous modèles combinés)
- **Latence** : <100ms par frame (estimation pose + classification + analyse qualité)
- **Mémoire** : ~200MB empreinte runtime

---

## 📁 Structure du Projet

```
ai-yoga-coach/
├── backend/
│   ├── best_model.ipynb           # Pipeline d'entraînement
│   ├── yoga_quality_analyzer.py   # Moteur d'analyse qualitative
│   ├── realtime_app.py            # Application webcam
│   ├── test_system.py             # Framework de test
│   ├── requirements.txt           # Dépendances
│   ├── best_yoga_model.pkl        # Classifier entraîné
│   ├── scaler.pkl                 # Scaler de features
│   ├── label_encoder.pkl          # Encodeur de labels
│   └── DATASET/
│       ├── TRAIN/                 # Images d'entraînement
│       │   ├── downdog/
│       │   ├── plank/
│       │   ├── tree/
│       │   ├── warrior2/
│       │   └── goddess/
│       └── TEST/                  # Images de test (même structure)
├── README.md
└── CLAUDE.md                      # Documentation développeur
```

---

## 🎓 Compétences Démontrées

Ce projet met en avant une expertise dans :

### Machine Learning & IA
- Classification multi-classes avec méthodes d'ensemble
- Feature engineering à partir de données capteurs brutes
- Optimisation d'hyperparamètres et sélection de modèles
- Validation croisée et évaluation de performance

### Vision par Ordinateur
- Estimation de pose avec MediaPipe
- Traitement vidéo temps réel avec OpenCV
- Suivi et normalisation de landmarks
- Calculs et transformations géométriques

### Ingénierie Logicielle
- Architecture modulaire et extensible
- Séparation claire des responsabilités (classification vs. analyse)
- Gestion d'erreurs complète
- Structure de code production-ready

### Connaissance du Domaine
- Principes de biomécanique et kinésiologie
- Design d'expérience utilisateur (feedback progressif)
- Optimisation de systèmes temps réel

---

## 🚧 Évolutions Futures

- [ ] **Application Mobile** : Déploiement iOS/Android avec TensorFlow Lite
- [ ] **Plus de Poses** : Expansion à 20+ poses incluant asanas avancées
- [ ] **Analyse Vidéo** : Analyse de sessions complètes avec cohérence temporelle
- [ ] **Personnalisation** : Profils utilisateurs avec suivi de progression
- [ ] **Multi-Personnes** : Support pour cours collectifs
- [ ] **Feedback Vocal** : Guidage audio avec synthèse vocale
- [ ] **API REST** : API pour intégrations tierces

---

## 📝 Dataset

Le modèle est entraîné sur un dataset curé d'images de poses de yoga :
- **5 Classes** : downdog, plank, tree, warrior2, goddess
- **Split Train/Test** : 80/20 stratifié
- **Qualité Images** : Arrière-plans variés, conditions d'éclairage, morphologies diverses
- **Annotations** : MediaPipe extrait automatiquement les landmarks de pose

*Détails sur les sources du dataset et licences disponibles sur demande.*

---

## 🤝 Contribution

Ceci est un projet portfolio, mais les suggestions et retours sont bienvenus ! Si vous êtes recruteur ou client potentiel, n'hésitez pas à me contacter pour discuter de :
- Ajouts de poses personnalisées
- Intégration avec plateformes fitness
- Solutions en marque blanche
- Consulting sur projets similaires CV/ML

---

## 📧 Contact

**Aurélien Anand**
📧 aurelien.anand@gmail.com  
🐙 [GitHub](https://github.com/Zhurah)

---

<div align="center">

**Développé avec ❤️ en utilisant Python, MediaPipe et Machine Learning**

*Accompagner les pratiquants avec un coaching yoga intelligent et accessible*

</div>
