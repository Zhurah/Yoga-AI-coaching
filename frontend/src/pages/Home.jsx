import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/FileUploader';
import MediaPipeProcessor from '../components/MediaPipeProcessor';
import WebcamCapture from '../components/WebcamCapture';
import ResultsPanel from '../components/ResultsPanel';
import apiService from '../services/apiService';
import './Home.css';

function Home() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [currentMode, setCurrentMode] = useState('upload'); // 'upload' ou 'webcam'
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);

  const isAuthenticated = apiService.isAuthenticated();

  /**
   * Gère la sélection d'un fichier
   */
  const handleFileSelected = (file) => {
    console.log('📁 Fichier sélectionné:', file.name);
    setSelectedFile(file);
    setAnalysisResults(null);
    setError(null);
  };

  /**
   * Gère les résultats de MediaPipe
   */
  const handleMediaPipeResults = async (results) => {
    if (!results.landmarks || results.landmarks.length === 0) {
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      // Si authentifié, utiliser analyzeComplete pour sauvegarder en DB
      // Sinon, utiliser l'ancienne méthode sans sauvegarde
      let analysis;

      if (isAuthenticated) {
        analysis = await apiService.analyzeComplete(results.landmarks);
      } else {
        // Pour les utilisateurs non authentifiés, simuler une réponse
        // (ou utiliser un endpoint public si disponible)
        const classification = await apiService.classifyPose(results.landmarks);
        if (classification.success) {
          const quality = await apiService.analyzePoseQuality(
            results.landmarks,
            classification.pose
          );
          analysis = {
            success: true,
            classification,
            quality_analysis: quality
          };
        }
      }

      setAnalysisResults(analysis);
      console.log('✅ Analyse reçue:', analysis);

    } catch (err) {
      console.error('❌ Erreur analyse:', err);

      // Si erreur 401 (non authentifié), rediriger vers login
      if (err.response?.status === 401) {
        alert('Veuillez vous connecter pour utiliser l\'analyse complète.');
        navigate('/login');
        return;
      }

      setError('Erreur lors de l\'analyse. Vérifiez que le serveur backend est démarré.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  /**
   * Gère les erreurs MediaPipe
   */
  const handleMediaPipeError = (error) => {
    console.error('❌ Erreur MediaPipe:', error);
    setError('Erreur lors de la détection de pose. Assurez-vous que le corps est bien visible.');
  };

  /**
   * Réinitialise l'application
   */
  const handleReset = () => {
    setSelectedFile(null);
    setAnalysisResults(null);
    setError(null);
    setIsAnalyzing(false);
  };

  /**
   * Change de mode (upload/webcam)
   */
  const handleModeChange = (mode) => {
    setCurrentMode(mode);
    handleReset();
  };

  /**
   * Déconnexion
   */
  const handleLogout = async () => {
    await apiService.logout();
    navigate('/login');
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🧘 Yoga Coaching AI</h1>
          <p>Analysez vos poses de yoga avec l'intelligence artificielle</p>
        </div>
        <div className="header-actions">
          {isAuthenticated ? (
            <>
              <button
                className="btn-dashboard"
                onClick={() => navigate('/dashboard')}
              >
                📊 Dashboard
              </button>
              <button
                className="btn-logout"
                onClick={handleLogout}
              >
                Déconnexion
              </button>
            </>
          ) : (
            <>
              <button
                className="btn-login"
                onClick={() => navigate('/login')}
              >
                Connexion
              </button>
              <button
                className="btn-register"
                onClick={() => navigate('/register')}
              >
                Créer un compte
              </button>
            </>
          )}
        </div>
      </header>

      {/* Mode selector */}
      <div className="mode-selector">
        <button
          className={`mode-btn ${currentMode === 'upload' ? 'active' : ''}`}
          onClick={() => handleModeChange('upload')}
        >
          📤 Upload Image/Vidéo
        </button>
        <button
          className={`mode-btn ${currentMode === 'webcam' ? 'active' : ''}`}
          onClick={() => handleModeChange('webcam')}
        >
          📹 Webcam en direct
        </button>
      </div>

      {/* Main content */}
      <main className="app-main">
        <div className="content-grid">
          {/* Left panel - Input */}
          <div className="input-panel">
            {currentMode === 'upload' ? (
              <>
                {!selectedFile ? (
                  <FileUploader onFileSelected={handleFileSelected} />
                ) : (
                  <div className="processor-container">
                    <MediaPipeProcessor
                      file={selectedFile}
                      onResults={handleMediaPipeResults}
                      onError={handleMediaPipeError}
                    />
                    <button className="reset-btn" onClick={handleReset}>
                      🔄 Charger un autre fichier
                    </button>
                  </div>
                )}
              </>
            ) : (
              <WebcamCapture
                onResults={handleMediaPipeResults}
                onError={handleMediaPipeError}
              />
            )}

            {/* Error display */}
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                <p>{error}</p>
              </div>
            )}

            {/* Loading indicator */}
            {isAnalyzing && (
              <div className="analyzing-indicator">
                <div className="spinner"></div>
                <p>Analyse en cours...</p>
              </div>
            )}
          </div>

          {/* Right panel - Results */}
          <div className="results-panel-container">
            {analysisResults ? (
              <ResultsPanel results={analysisResults} />
            ) : (
              <div className="placeholder-panel">
                <div className="placeholder-icon">🎯</div>
                <h3>En attente d'analyse</h3>
                <p>
                  {currentMode === 'upload'
                    ? 'Chargez une image ou vidéo pour commencer'
                    : 'Positionnez-vous devant la caméra pour commencer'}
                </p>
                {!isAuthenticated && (
                  <div className="auth-notice">
                    <p>
                      💡 <strong>Astuce:</strong> Connectez-vous pour sauvegarder
                      votre historique et suivre votre progression !
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>© 2025 Yoga Coaching AI - Propulsé par MediaPipe & Machine Learning</p>
      </footer>
    </div>
  );
}

export default Home;
