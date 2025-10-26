# AI Yoga Coach: Real-Time Posture Analysis with Qualitative Feedback

<div align="center">

**An intelligent yoga coaching system combining Computer Vision, Machine Learning, and Real-Time Processing to provide instant and personalized feedback on pose execution.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.9-green.svg)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg)](https://opencv.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)

[Key Features](#-key-features) • [Demo](#-demo) • [Architecture](#-architecture) • [Installation](#-installation) • [Usage](#-usage) • [Technical Details](#-technical-details)

</div>

---

## 📋 Project Overview

This project implements a complete yoga coaching system that analyzes body posture in real-time using advanced computer vision and machine learning techniques. It goes beyond simple pose classification to provide **actionable and contextual feedback** on execution quality.

### The Problem

Traditional yoga learning requires:
- In-person classes (expensive, time constraints)
- Generic video tutorials (no personalized feedback)
- Difficulty in self-assessing correct form

### The Solution

An AI-powered system that:
- 🎯 Detects and classifies 5 yoga postures with **high accuracy**
- 📊 Analyzes pose quality across **multiple biomechanical dimensions**
- 💬 Provides **real-time personalized coaching**
- 🔒 Operates entirely **locally** (guaranteed privacy, no cloud)

---

## 💻 Installation

### Prerequisites
- Python 3.8+
- Webcam (for real-time features)
- 4GB+ RAM recommended

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-yoga-coach.git
cd ai-yoga-coach

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Train the Model (Optional)

If you want to retrain with your own data:

```bash
cd backend
jupyter notebook best_model.ipynb
# Run all cells to train and export models
```

Pre-trained models are included: `best_yoga_model.pkl`, `scaler.pkl`, `label_encoder.pkl`

---

## 🎮 Usage

### Real-Time Coaching (Webcam)

```bash
cd backend
python realtime_app.py
```

**Controls:**
- Press **Q** to quit
- Press **SPACE** to force immediate analysis

### Analyze Static Images

```python
from backend.yoga_quality_analyzer import analyze_pose_quality

result = analyze_pose_quality(
    image_path='path/to/image.jpg',
    pose_name='plank'  # or auto-detect with classifier
)

print(f"Overall Score: {result['quality_analysis']['overall_score']}/100")
print("Feedback:", result['quality_analysis']['feedback'])
```

### Test on Dataset Samples

```bash
cd backend
python test_system.py
# Generates result_*.json files with detailed analysis
```

---

## ✨ Key Features

### 1. Multi-Class Classification
- **5 Supported Postures**: Downward Dog, Plank, Tree, Warrior II, Goddess
- **High Accuracy**: Trained on a diverse dataset with rigorous evaluation
- **Confidence Score**: Only provides feedback if confidence ≥ 70%

### 2. Intelligent Qualitative Analysis
Each posture is analyzed based on **specific metrics**:

| Posture | Key Metrics Analyzed |
|---------|---------------------|
| **Downward Dog** | Hip-shoulder-ankle alignment, arm extension, leg straightness, symmetry |
| **Plank** | Body alignment, core engagement, shoulder positioning, symmetry |
| **Tree** | Vertical balance, foot height, hip opening, shoulder level |
| **Warrior II** | Arm alignment, knee flexion (90°), knee-ankle alignment, hip opening |
| **Goddess** | Stance width, squat depth, knee-ankle alignment, back posture |

### 3. Contextual Feedback System
- **Severity Levels**: Excellent (✓✓), Good (✓), Warning (⚠️), Tips (💡), Encouragement (💪)
- **Actionable Guidance**: "Push knees outward, aligned with feet" vs. generic "improve form"
- **Progressive Coaching**: Recognizes beginner modifications

### 4. Real-Time Webcam Application
- Live pose detection and analysis
- Visual overlay with skeleton tracking
- Configurable analysis frequency (default: 3s intervals)
- Minimal latency (<100ms per frame)

---

## 📊 Demo

### Real-Time Analysis Output

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
      "✓✓ Perfect alignment! Body well straight.",
      "✓✓ Full plank! Excellent core strength.",
      "✓ Distribute weight evenly."
    ]
  }
}
```

### Analysis Visualization

When you run the real-time application, you'll see:
- **Skeleton overlay** on your body (green joints, red connections)
- **Detected pose** with confidence percentage
- **Quality score** out of 100
- **Top 3 indicators** color-coded by performance
- **Instant feedback** at the bottom of the screen

---

## 🏗️ Architecture

### System Design

```
┌─────────────────┐
│  Video Input    │ (Webcam / Image)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  MediaPipe Pose Estimation      │ (33 3D Landmarks)
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Feature Engineering            │ (56 Features)
│  • Joint angles (8)             │
│  • Distances (6)                │
│  • Ratios (2)                   │
│  • Symmetry metrics             │
└────────┬────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
┌────────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Scaler        │  │  Classifier  │  │  Quality         │
│  (Normalize)   │→ │  (ML Model)  │→ │  Analyzer        │
└────────────────┘  └──────────────┘  └──────────────────┘
                            │                  │
                            ▼                  ▼
                    ┌──────────────────────────────────┐
                    │  Pose + Confidence + Feedback    │
                    └──────────────────────────────────┘
```

### Main Components

1. **`best_model.ipynb`**: Training pipeline with hyperparameter optimization (Random Forest, SVM, XGBoost)
2. **`yoga_quality_analyzer.py`**: Modular qualitative analysis engine with pose-specific evaluators
3. **`realtime_app.py`**: Real-time webcam application with OpenCV
4. **`test_system.py`**: End-to-end testing and validation framework

---

## 🔬 Technical Details

### Feature Engineering

From MediaPipe's 33 3D landmarks (132 values), we extract **56 engineered features**:

**Geometric Features:**
- 13 key landmark positions (nose, shoulders, elbows, wrists, hips, knees, ankles)
- 8 joint angles (elbow flexion, shoulder extension, hip flexion, knee angles)
- 6 distance metrics (shoulder width, hip width, limb spans)

**Derived Features:**
- Body proportions (shoulder/hip ratio)
- Vertical alignment (nose-hip distance)
- Symmetry indicators (left-right ankle distance)
- Confidence score (average landmark visibility)

### Machine Learning Pipeline

1. **Data Augmentation**: Horizontal mirrors for left-right variations
2. **Preprocessing**: StandardScaler normalization
3. **Model Selection**: Grid search on:
   - Random Forest (tuning `n_estimators`, `max_depth`, `min_samples_split`)
   - SVM with RBF kernel (tuning `C`, `gamma`)
   - XGBoost (tuning `n_estimators`, `learning_rate`, `max_depth`)
4. **Evaluation**: Stratified K-Fold cross-validation, confusion matrix analysis
5. **Export**: Best model serialized with joblib

### Qualitative Analysis Algorithm

Each pose has a **dedicated analyzer** implementing:

1. **Landmark Extraction**: Identify relevant body parts for the pose
2. **Metric Calculation**: Compute specific indicators (e.g., knee angle for Warrior II)
3. **Thresholding**: Compare to ideal ranges (e.g., 85-95° for perfect squat)
4. **Feedback Generation**: Map scores to actionable text with severity markers
5. **Aggregation**: Calculate overall quality score as weighted average

**Example: Plank Analysis**
```python
def _analyze_plank(self, landmarks):
    # 1. Calculate deviation from ideal straight line
    alignment_score = 100 - deviation_from_straight * 300

    # 2. Detect modified plank (knees) vs. full
    if knee_to_ankle_dist < 0.05:
        core_strength = 40  # Modified plank detected
    else:
        core_strength = 100

    # 3. Check vertical shoulder-wrist alignment
    shoulder_position = calculate_vertical_alignment(shoulders, wrists)

    return {
        "indicators": {alignment, core_strength, shoulder_position, ...},
        "feedback": [...]
    }
```

### Performance Characteristics

- **Inference Speed**: ~30 FPS on CPU (Intel i5)
- **Model Size**: <5MB (all models combined)
- **Latency**: <100ms per frame (pose estimation + classification + quality analysis)
- **Memory**: ~200MB runtime footprint

---

## 📁 Project Structure

```
ai-yoga-coach/
├── backend/
│   ├── best_model.ipynb           # Training pipeline
│   ├── yoga_quality_analyzer.py   # Qualitative analysis engine
│   ├── realtime_app.py            # Webcam application
│   ├── test_system.py             # Testing framework
│   ├── requirements.txt           # Dependencies
│   ├── best_yoga_model.pkl        # Trained classifier
│   ├── scaler.pkl                 # Feature scaler
│   ├── label_encoder.pkl          # Label encoder
│   └── DATASET/
│       ├── TRAIN/                 # Training images
│       │   ├── downdog/
│       │   ├── plank/
│       │   ├── tree/
│       │   ├── warrior2/
│       │   └── goddess/
│       └── TEST/                  # Test images (same structure)
├── README.md
└── CLAUDE.md                      # Developer documentation
```

---

## 🎓 Skills Demonstrated

This project showcases expertise in:

### Machine Learning & AI
- Multi-class classification with ensemble methods
- Feature engineering from raw sensor data
- Hyperparameter optimization and model selection
- Cross-validation and performance evaluation

### Computer Vision
- Pose estimation with MediaPipe
- Real-time video processing with OpenCV
- Landmark tracking and normalization
- Geometric calculations and transformations

### Software Engineering
- Modular and extensible architecture
- Clear separation of concerns (classification vs. analysis)
- Comprehensive error handling
- Production-ready code structure

### Domain Knowledge
- Biomechanics and kinesiology principles
- User experience design (progressive feedback)
- Real-time system optimization

---

## 🚧 Future Enhancements

- [ ] **Mobile Application**: iOS/Android deployment with TensorFlow Lite
- [ ] **More Poses**: Expansion to 20+ poses including advanced asanas
- [ ] **Video Analysis**: Complete session analysis with temporal coherence
- [ ] **Personalization**: User profiles with progress tracking
- [ ] **Multi-Person**: Support for group classes
- [ ] **Voice Feedback**: Audio guidance with speech synthesis
- [ ] **REST API**: API for third-party integrations

---

## 📝 Dataset

The model is trained on a curated dataset of yoga pose images:
- **5 Classes**: downdog, plank, tree, warrior2, goddess
- **Train/Test Split**: 80/20 stratified
- **Image Quality**: Varied backgrounds, lighting conditions, diverse body types
- **Annotations**: MediaPipe automatically extracts pose landmarks

*Details on dataset sources and licenses available upon request.*

---

## 🤝 Contribution

This is a portfolio project, but suggestions and feedback are welcome! If you are a recruiter or potential client, feel free to contact me to discuss:
- Custom pose additions
- Integration with fitness platforms
- White-label solutions
- Consulting on similar CV/ML projects

---

## 📧 Contact

**Aurélien Anand**
📧 aurelien.anand@gmail.com
🐙 [GitHub](https://github.com/Zhurah)

---

<div align="center">

**Developed with ❤️ using Python, MediaPipe and Machine Learning**

*Empowering practitioners with intelligent and accessible yoga coaching*

</div>
