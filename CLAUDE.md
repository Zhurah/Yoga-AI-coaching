# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **full-stack Yoga Pose Quality Analyzer** system that uses computer vision and machine learning to:
1. Classify yoga poses from images/video using MediaPipe pose estimation
2. Provide real-time qualitative feedback on pose execution quality
3. Offer coaching feedback via webcam or file upload
4. Provide a web-based interface for interactive analysis

The system supports 5 yoga poses: `downdog`, `plank`, `tree`, `warrior2`, and `goddess`.

**Stack:**
- **Backend**: Python (Flask REST API, MediaPipe, scikit-learn, JWT auth)
- **Frontend**: React 18 with MediaPipe Pose in-browser, React Router for navigation
- **ML Pipeline**: Jupyter notebook for model training
- **Visualization**: Recharts for performance metrics and radar charts

## Architecture

### Core Components

**1. Pose Classification Pipeline** (`backend/best_model.ipynb`)
- Jupyter notebook for training the ML classifier
- Extracts MediaPipe keypoints (33 landmarks with x, y, z, visibility)
- Engineers features: angles, distances, ratios, symmetry metrics
- Trains multiple models (Random Forest, SVM, XGBoost) with hyperparameter tuning
- Exports: `best_yoga_model.pkl`, `scaler.pkl`, `label_encoder.pkl`

**2. Quality Analysis Engine** (`backend/yoga_quality_analyzer.py`)
- `YogaPoseQualityAnalyzer` class: Analyzes pose execution quality
- Pose-specific analyzers for each of the 5 supported poses
- Returns structured feedback:
  - **Indicators**: Numeric scores (0-100) for specific aspects (alignment, symmetry, knee angle, etc.)
  - **Feedback**: Human-readable coaching tips with emoji markers (✓✓, ✓, ⚠️, 💡, 💪)
- Key utility functions:
  - `calculate_angle()`: 3D angle between three points
  - `calculate_2d_angle()`: 2D angle in x-y plane
  - `calculate_horizontal_alignment()` / `calculate_vertical_alignment()`: Alignment scores
  - `calculate_symmetry()`: Symmetry score relative to center point

**3. Flask REST API** (`backend/api.py`)
- Production-ready API with CORS support
- Endpoints:
  - `GET /api/health`: Health check
  - `GET /api/poses`: List available poses
  - `POST /api/classify`: Classify pose from landmarks
  - `POST /api/analyze`: Analyze pose quality
  - `POST /api/complete-analysis`: Combined classification + quality analysis
- Runs on port 8000 by default
- Includes user_level personalization (beginner/intermediate/advanced)

**4. React Frontend** (`frontend/`)
- Interactive web interface for pose analysis with user authentication
- Pages:
  - `Home`: Main analysis interface with webcam/upload options
  - `Login`/`Register`: User authentication pages
  - `Dashboard`: User progress tracking and analytics
- Components:
  - `WebcamCapture`: Real-time webcam feed with MediaPipe
  - `FileUploader`: Upload images/videos for analysis
  - `MediaPipeProcessor`: Client-side pose detection
  - `ResultsPanel`: Display classification and quality feedback
  - `RadarChart`: Visual representation of pose quality metrics
  - `ExerciseRecommendation`: Personalized exercise suggestions
- Services:
  - `apiService.js`: Axios-based API client
  - `mediapipeService.js`: MediaPipe Pose wrapper
- Runs on port 3000 (React dev server)

**5. Standalone Applications**
- `realtime_app.py`: OpenCV-based standalone webcam coaching (no web server needed)
- `test_system.py`: CLI testing tool for batch image analysis

### Data Flow

**Web Application Flow:**
```
Browser Webcam/Upload → MediaPipe.js (client) → Landmarks (33 × 4) →
  ↓
POST /api/complete-analysis → Flask API → Feature Engineering →
  ↓
Scaler → ML Model → Pose Classification + Confidence →
  ↓
YogaPoseQualityAnalyzer → Indicators + Feedback → JSON Response → React UI
```

**Standalone Application Flow:**
```
OpenCV Webcam → MediaPipe (Python) → Keypoints → Feature Engineering →
  ↓
Scaler → ML Model → Classification → Quality Analyzer → OpenCV Overlay Display
```

### Feature Engineering Strategy

From raw keypoints (132 values: 33 landmarks × 4 dimensions), features are extracted:
- **Key points**: Positions of 13 critical landmarks (nose, shoulders, elbows, wrists, hips, knees, ankles)
- **Angles**: 8 joint angles (elbows, shoulders, hips, knees, torso)
- **Distances**: 6 distance metrics (shoulder width, hip width, hand-to-ankle, etc.)
- **Ratios**: Shoulder/hip width ratio, nose-to-hip vertical distance
- **Symmetry**: Left-right ankle distance
- **Confidence**: Average visibility score

This results in ~56 engineered features used for classification.

## Dataset Structure

```
backend/DATASET/
├── TRAIN/
│   ├── downdog/
│   ├── goddess/
│   ├── plank/
│   ├── tree/
│   └── warrior2/
└── TEST/
    ├── downdog/
    ├── goddess/
    ├── plank/
    ├── tree/
    └── warrior2/
```

Images should be in JPG or PNG format.

## Common Commands

### Initial Setup

**Backend:**
```bash
# Install Python dependencies
pip install -r requirements.txt
# Note: requirements.txt in root is identical to backend/requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install

# Create .env file (if not exists)
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
```

**Note**: The `.env` file should already exist in the frontend directory.

### Running the Full-Stack Application

**Terminal 1 - Start Backend API:**
```bash
cd backend
python api.py
# Runs on http://localhost:8000
# API docs displayed in console on startup
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm start
# Runs on http://localhost:3000
# Opens browser automatically
```

**Access the app:** Navigate to `http://localhost:3000`

### Running Standalone Applications

**OpenCV Webcam Coach (no web server):**
```bash
cd backend
python realtime_app.py
# Press 'q' to quit, spacebar to force analysis
```

**Batch Image Testing:**
```bash
cd backend
python test_system.py
# Tests on sample images from DATASET/TEST/
# Outputs: result_*.json files with analysis
```

**Important**: All backend Python scripts (`api.py`, `realtime_app.py`, `test_system.py`) must be run from within the `backend/` directory, as they rely on relative paths to load the `.pkl` model files and access the `DATASET/` folder.

### Model Training

```bash
cd backend
jupyter notebook best_model.ipynb
# Run all cells to train and export models
# Generates: best_yoga_model.pkl, scaler.pkl, label_encoder.pkl
```

### Testing Individual Modules

```bash
cd backend
python yoga_quality_analyzer.py
# Runs demo_usage() with example output
```

### Testing

**Frontend Tests:**
```bash
cd frontend
npm test
# Runs Jest test suite
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
# Creates optimized build/ folder
```

## Key Design Patterns

### Feature Engineering Consistency
**CRITICAL**: The `engineer_features()` function in `api.py` and `test_system.py` must produce identical features to those used during model training in `best_model.ipynb`. Any modifications to feature engineering require retraining the model.

### Pose-Specific Analysis
Each pose has a dedicated analyzer method (e.g., `_analyze_downdog()`, `_analyze_plank()`) in `YogaPoseQualityAnalyzer` that:
1. Extracts relevant landmarks for that pose
2. Computes pose-specific indicators (e.g., hip angle for downdog, knee flexion for warrior2)
3. Generates contextual feedback based on indicator thresholds
4. Returns a consistent structure: `{"pose": str, "indicators": dict, "feedback": list}`

### Feedback Severity Levels
- ✓✓: Excellent (score ≥ 85-90)
- ✓: Good (score ≥ 70-80)
- ⚠️: Warning (score < 60-70, needs correction)
- 💡: Tip (educational guidance, not necessarily poor performance)
- 💪: Encouragement (modification detected or progress suggestion)

### Confidence Thresholding
Quality analysis only runs when classification confidence ≥ 70% (configurable). This prevents misleading feedback on uncertain classifications.

### Client-Server Architecture
- **Client-side (React)**: MediaPipe Pose runs in the browser, extracts landmarks, sends to API
- **Server-side (Flask)**: Receives landmarks, performs classification and quality analysis
- This separation allows the heavy ML models to run server-side while keeping the client lightweight

## Model Files

These files are generated by `best_model.ipynb` and required for runtime:
- `best_yoga_model.pkl`: Trained classifier (likely Random Forest or XGBoost)
- `scaler.pkl`: StandardScaler for feature normalization
- `label_encoder.pkl`: Maps class indices to pose names

**Location**: All three `.pkl` files must be in the `backend/` directory.

**Important**: These files currently exist in the project. Do not commit large model files to version control. If retraining is needed, run `best_model.ipynb` to regenerate them.

## Adding New Poses

To add a new pose (e.g., "cobra"):

1. **Dataset**: Add `backend/DATASET/TRAIN/cobra/` and `backend/DATASET/TEST/cobra/` with images
2. **Retrain**: Run `best_model.ipynb` to include new class (exports updated .pkl files)
3. **Quality Analyzer**: Add `_analyze_cobra()` method in `YogaPoseQualityAnalyzer`:
   - Define pose-specific indicators (e.g., back arch, arm position)
   - Set thresholds and feedback messages
   - Register in `self.pose_analyzers` dict in `__init__()`
4. **Test**:
   - CLI: Run `test_system.py` with cobra images
   - API: Restart `api.py` (auto-loads new label_encoder.pkl)
   - Frontend: Should automatically show new pose (no code changes needed)

## Troubleshooting

### Backend Issues

**"Aucune pose détectée dans l'image"**
- MediaPipe couldn't detect a person in the frame
- Ensure good lighting, full body visible, and contrasting background

**Low Confidence Predictions**
- Pose may be ambiguous or not well-represented in training data
- Check that the person is fully visible and pose is held clearly
- Consider augmenting training dataset for that pose

**Feature Count Mismatch**
- `engineer_features()` must produce exactly the same number of features as during training
- If modifying feature engineering, retrain the model

**Webcam Not Opening (realtime_app.py)**
- Check camera permissions
- Verify `camera_id=0` is correct (try 1, 2 if multiple cameras)
- On macOS, ensure Terminal/app has camera access in System Preferences

**Models Not Found Error**
- Run `best_model.ipynb` to generate .pkl files
- Ensure you're in the `backend/` directory when running scripts (critical for relative imports)

**Import Errors in Backend Scripts**
- Backend scripts use imports like `from backend.yoga_quality_analyzer import ...`
- These require running from the `backend/` directory
- If imports fail, verify current working directory is `backend/`

### Frontend Issues

**CORS Error**
- Verify `flask-cors` is installed in backend
- Check that backend is running on port 8000
- Verify `REACT_APP_API_URL` in `frontend/.env` is correct

**MediaPipe Not Loading**
- Check internet connection (MediaPipe loads from CDN)
- Try clearing browser cache

**Webcam Not Working in Browser**
- Grant camera permissions in browser settings
- HTTPS required in production (use localhost for development)
- Check that no other app is using the webcam

**API Connection Failed**
- Ensure backend API is running (`python api.py`)
- Check browser console for exact error message
- Verify backend prints "API démarrée sur http://localhost:8000"

## Project Structure

```
yoga_project/
├── backend/
│   ├── api.py                      # Flask REST API
│   ├── yoga_quality_analyzer.py    # Quality analysis engine
│   ├── realtime_app.py             # Standalone OpenCV app
│   ├── test_system.py              # CLI testing tool
│   ├── best_model.ipynb            # Model training notebook
│   ├── requirements.txt            # Python dependencies
│   ├── best_yoga_model.pkl         # Trained classifier (generated)
│   ├── scaler.pkl                  # Feature scaler (generated)
│   ├── label_encoder.pkl           # Label encoder (generated)
│   └── DATASET/
│       ├── TRAIN/                  # Training images (5 pose folders)
│       └── TEST/                   # Test images (5 pose folders)
├── frontend/
│   ├── src/
│   │   ├── pages/                  # Page components
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── components/             # React components
│   │   │   ├── WebcamCapture.jsx
│   │   │   ├── FileUploader.jsx
│   │   │   ├── MediaPipeProcessor.jsx
│   │   │   ├── ResultsPanel.jsx
│   │   │   ├── RadarChart.jsx
│   │   │   └── ExerciseRecommendation.jsx
│   │   ├── services/               # API and MediaPipe services
│   │   │   ├── apiService.js
│   │   │   └── mediapipeService.js
│   │   ├── utils/                  # Helper functions
│   │   │   └── drawingUtils.js
│   │   └── App.jsx                 # Main app component
│   ├── public/                     # Static assets
│   ├── package.json                # Node dependencies
│   ├── .env                        # Environment config (already exists)
│   └── .git/                       # Git repository (frontend only)
├── requirements.txt                # Root Python dependencies
├── README.md                       # Project documentation (French)
└── CLAUDE.md                       # This file
```

**Note**: Version control (`.git`) is only in the `frontend/` directory, not at the root level.

## Code Quality Notes

- **Language**: Codebase is in French (comments, variable names, feedback messages)
- **Determinism**: All pose analysis logic is deterministic (no randomness)
- **Coordinate System**: MediaPipe coordinates are normalized (0-1 range)
- **Single Person**: The system assumes a single person per frame
- **API Design**: RESTful with clear separation of concerns (classification vs. analysis endpoints)
- **Error Handling**: Both frontend and backend have comprehensive error handling
