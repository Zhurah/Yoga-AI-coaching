// Utilitaires pour dessiner les keypoints sur le canvas
import { POSE_CONNECTIONS } from '@mediapipe/pose';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';

/**
 * Dessine les keypoints et le squelette sur le canvas
 */
export const drawPoseOnCanvas = (canvasRef, results, showConnections = true) => {
  if (!canvasRef.current || !results.poseLandmarks) {
    return;
  }

  const canvas = canvasRef.current;
  const ctx = canvas.getContext('2d');

  // Effacer le canvas
  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Dessiner les connexions (squelette)
  if (showConnections) {
    drawConnectors(ctx, results.poseLandmarks, POSE_CONNECTIONS, {
      color: '#00FF00',
      lineWidth: 4
    });
  }

  // Dessiner les landmarks (points)
  drawLandmarks(ctx, results.poseLandmarks, {
    color: '#FF0000',
    lineWidth: 2,
    radius: 6
  });

  ctx.restore();
};

/**
 * Dessine un score sur le canvas
 */
export const drawScoreIndicator = (canvasRef, score, label, position = 'top-left') => {
  if (!canvasRef.current) return;

  const canvas = canvasRef.current;
  const ctx = canvas.getContext('2d');

  // Position
  let x = 20;
  let y = 40;

  if (position === 'top-right') {
    x = canvas.width - 160;
  } else if (position === 'bottom-left') {
    y = canvas.height - 20;
  } else if (position === 'bottom-right') {
    x = canvas.width - 160;
    y = canvas.height - 20;
  }

  // Couleur selon le score
  const color = score >= 80 ? '#4CAF50' : score >= 60 ? '#FF9800' : '#F44336';

  // Fond
  ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
  ctx.fillRect(x - 10, y - 30, 150, 45);

  // Texte label
  ctx.fillStyle = '#FFFFFF';
  ctx.font = '14px Poppins, Arial';
  ctx.fillText(label, x, y - 10);

  // Texte score
  ctx.fillStyle = color;
  ctx.font = 'bold 18px Poppins, Arial';
  ctx.fillText(`${score.toFixed(1)}/100`, x, y + 15);
};

/**
 * Convertit les landmarks MediaPipe en format pour le backend
 */
export const formatLandmarksForBackend = (landmarks) => {
  return landmarks.map(landmark => ({
    x: landmark.x,
    y: landmark.y,
    z: landmark.z,
    visibility: landmark.visibility
  }));
};

/**
 * Calcule l'angle entre trois points
 */
export const calculateAngle = (a, b, c) => {
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - 
                  Math.atan2(a.y - b.y, a.x - b.x);
  let angle = Math.abs(radians * 180.0 / Math.PI);
  
  if (angle > 180.0) {
    angle = 360 - angle;
  }
  
  return angle;
};

/**
 * Calcule la distance entre deux points
 */
export const calculateDistance = (a, b) => {
  return Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
};