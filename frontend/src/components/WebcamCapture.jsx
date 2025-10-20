import React, { useRef, useEffect, useState } from 'react';
import mediapipeService from '../services/mediapipeService';
import { drawPoseOnCanvas, formatLandmarksForBackend } from '../utils/drawingUtils';
import './WebcamCapture.css';

const WebcamCapture = ({ onResults, onError }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  
  const [isActive, setIsActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [detectionStatus, setDetectionStatus] = useState('');
  const [frameCount, setFrameCount] = useState(0);

  useEffect(() => {
    if (isActive) {
      startWebcam();
    } else {
      stopWebcam();
    }

    return () => {
      stopWebcam();
    };
  }, [isActive]);

  /**
   * Démarre la webcam
   */
  const startWebcam = async () => {
    try {
      setIsProcessing(true);
      setDetectionStatus('Initialisation de la webcam...');

      // Initialiser MediaPipe
      await mediapipeService.initialize(handleMediaPipeResults);

      // Démarrer la caméra
      if (videoRef.current) {
        await mediapipeService.startCamera(videoRef.current);
        
        // Ajuster le canvas
        if (canvasRef.current) {
          canvasRef.current.width = 1280;
          canvasRef.current.height = 720;
        }

        setDetectionStatus('✅ Webcam active');
        setIsProcessing(false);
      }

    } catch (error) {
      console.error('❌ Erreur webcam:', error);
      setDetectionStatus('❌ Impossible d\'accéder à la webcam');
      setIsProcessing(false);
      if (onError) onError(error);
    }
  };

  /**
   * Arrête la webcam
   */
  const stopWebcam = () => {
    mediapipeService.stopCamera();
    setDetectionStatus('');
    setFrameCount(0);
  };

  /**
   * Traite les résultats de MediaPipe
   */
  const handleMediaPipeResults = (results) => {
    // Dessiner sur le canvas
    if (canvasRef.current) {
      drawPoseOnCanvas(canvasRef, results);
    }

    // Mettre à jour le compteur de frames
    setFrameCount(prev => prev + 1);

    // Envoyer les résultats au parent (throttle: 1 fois par seconde)
    if (results.poseLandmarks && frameCount % 30 === 0) {
      setDetectionStatus('✅ Pose détectée');
      
      if (onResults) {
        const formattedLandmarks = formatLandmarksForBackend(results.poseLandmarks);
        onResults({
          landmarks: formattedLandmarks,
          timestamp: Date.now()
        });
      }
    } else if (!results.poseLandmarks) {
      setDetectionStatus('⚠️ Aucune pose détectée');
    }
  };

  /**
   * Toggle webcam
   */
  const toggleWebcam = () => {
    setIsActive(!isActive);
  };

  return (
    <div className="webcam-capture">
      {!isActive ? (
        <div className="webcam-placeholder">
          <div className="webcam-icon">📹</div>
          <h3>Webcam désactivée</h3>
          <p>Activez la webcam pour commencer l'analyse en temps réel</p>
          <button className="start-btn" onClick={toggleWebcam}>
            Démarrer la webcam
          </button>
        </div>
      ) : (
        <>
          {/* Processing overlay */}
          {isProcessing && (
            <div className="processing-overlay">
              <div className="spinner"></div>
              <p>{detectionStatus}</p>
            </div>
          )}

          <div className="webcam-container">
            {/* Video element */}
            <video
              ref={videoRef}
              className="webcam-video"
              autoPlay
              playsInline
              muted
            />

            {/* Canvas overlay */}
            <canvas
              ref={canvasRef}
              className="webcam-canvas"
            />

            {/* Controls overlay */}
            <div className="webcam-controls">
              <button className="stop-btn" onClick={toggleWebcam}>
                ⏹ Arrêter
              </button>
            </div>
          </div>

          {/* Status bar */}
          {detectionStatus && (
            <div className={`detection-status ${detectionStatus.includes('✅') ? 'success' : 'warning'}`}>
              {detectionStatus}
              <span className="frame-counter">Frame: {frameCount}</span>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default WebcamCapture;