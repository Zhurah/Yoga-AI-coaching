import React, { useRef, useEffect, useState } from 'react';
import mediapipeService from '../services/mediapipeService';
import { drawPoseOnCanvas, formatLandmarksForBackend } from '../utils/drawingUtils';
import './MediaPipeProcessor.css';

const MediaPipeProcessor = ({ file, onResults, onError }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const imageRef = useRef(null);
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [mediaType, setMediaType] = useState(null);
  const [detectionStatus, setDetectionStatus] = useState('');

  useEffect(() => {
    if (!file) return;

    const initializeMediaPipe = async () => {
      try {
        setIsProcessing(true);
        setDetectionStatus('Initialisation de MediaPipe...');
        
        // Initialiser MediaPipe
        await mediapipeService.initialize(handleMediaPipeResults);

        // Déterminer le type de média
        const type = file.type.startsWith('image/') ? 'image' : 'video';
        setMediaType(type);

        // Charger le média
        const fileURL = URL.createObjectURL(file);

        if (type === 'image') {
          await processImage(fileURL);
        } else {
          await processVideo(fileURL);
        }

      } catch (error) {
        console.error('❌ Erreur MediaPipe:', error);
        if (onError) onError(error);
        setIsProcessing(false);
        setDetectionStatus('Erreur lors de la détection');
      }
    };

    initializeMediaPipe();

    // Cleanup
    return () => {
      mediapipeService.cleanup();
      if (file) {
        URL.revokeObjectURL(URL.createObjectURL(file));
      }
    };
  }, [file]);

  /**
   * Traite les résultats de MediaPipe
   */
  const handleMediaPipeResults = (results) => {
    // Dessiner sur le canvas
    if (canvasRef.current) {
      drawPoseOnCanvas(canvasRef, results);
    }

    // Vérifier si une pose est détectée
    if (results.poseLandmarks && results.poseLandmarks.length > 0) {
      setDetectionStatus('✅ Pose détectée');
      setIsProcessing(false);

      // Envoyer les résultats au parent
      if (onResults) {
        const formattedLandmarks = formatLandmarksForBackend(results.poseLandmarks);
        onResults({
          landmarks: formattedLandmarks,
          timestamp: Date.now()
        });
      }
    } else {
      setDetectionStatus('⚠️ Aucune pose détectée');
    }
  };

  /**
   * Traite une image
   */
  const processImage = async (imageURL) => {
    const img = imageRef.current;
    img.src = imageURL;

    img.onload = async () => {
      // Ajuster la taille du canvas
      if (canvasRef.current) {
        canvasRef.current.width = img.naturalWidth;
        canvasRef.current.height = img.naturalHeight;
      }

      setDetectionStatus('Analyse de l\'image...');

      // Traiter l'image
      await mediapipeService.processImage(img);
    };

    img.onerror = () => {
      setDetectionStatus('❌ Erreur de chargement de l\'image');
      setIsProcessing(false);
      if (onError) onError(new Error('Impossible de charger l\'image'));
    };
  };

  /**
   * Traite une vidéo
   */
  const processVideo = async (videoURL) => {
    const video = videoRef.current;
    video.src = videoURL;

    video.onloadedmetadata = async () => {
      // Ajuster la taille du canvas
      if (canvasRef.current) {
        canvasRef.current.width = video.videoWidth;
        canvasRef.current.height = video.videoHeight;
      }

      setDetectionStatus('Lecture de la vidéo...');

      // Démarrer le traitement
      video.play();
      processVideoFrame();
    };

    video.onerror = () => {
      setDetectionStatus('❌ Erreur de chargement de la vidéo');
      setIsProcessing(false);
      if (onError) onError(new Error('Impossible de charger la vidéo'));
    };
  };

  /**
   * Traite les frames de la vidéo
   */
  const processVideoFrame = async () => {
    const video = videoRef.current;
    
    if (!video || video.paused || video.ended) {
      return;
    }

    try {
      await mediapipeService.processImage(video);
    } catch (error) {
      console.error('❌ Erreur traitement frame:', error);
    }

    // Traiter la prochaine frame
    requestAnimationFrame(processVideoFrame);
  };

  return (
    <div className="mediapipe-processor">
      {/* Processing overlay */}
      {isProcessing && (
        <div className="processing-overlay">
          <div className="spinner"></div>
          <p>{detectionStatus}</p>
        </div>
      )}

      <div className="media-container">
        {/* Image hidden pour traitement */}
        <img
          ref={imageRef}
          style={{ display: 'none' }}
          alt="Input"
        />

        {/* Video */}
        {mediaType === 'video' && (
          <video
            ref={videoRef}
            className="media-element"
            controls
            muted
            loop
          />
        )}

        {/* Image visible */}
        {mediaType === 'image' && imageRef.current && imageRef.current.src && (
          <img
            src={imageRef.current.src}
            className="media-element"
            alt="Pose"
          />
        )}

        {/* Canvas pour dessiner les keypoints */}
        <canvas
          ref={canvasRef}
          className="pose-canvas"
        />
      </div>

      {/* Detection status */}
      {detectionStatus && (
        <div className={`detection-status ${detectionStatus.includes('✅') ? 'success' : detectionStatus.includes('⚠️') ? 'warning' : 'info'}`}>
          {detectionStatus}
        </div>
      )}
    </div>
  );
};

export default MediaPipeProcessor;