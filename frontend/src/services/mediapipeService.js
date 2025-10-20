// Service pour gérer MediaPipe Pose
import { Pose } from '@mediapipe/pose';
import { Camera } from '@mediapipe/camera_utils';

class MediaPipeService {
  constructor() {
    this.pose = null;
    this.camera = null;
    this.onResultsCallback = null;
  }

  /**
   * Initialise MediaPipe Pose
   */
  async initialize(onResults) {
    this.onResultsCallback = onResults;

    this.pose = new Pose({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
      }
    });

    this.pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      smoothSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    this.pose.onResults((results) => {
      if (this.onResultsCallback) {
        this.onResultsCallback(results);
      }
    });

    console.log('✅ MediaPipe Pose initialisé');
  }

  /**
   * Traite une image
   */
  async processImage(imageElement) {
    if (!this.pose) {
      throw new Error('MediaPipe non initialisé');
    }

    await this.pose.send({ image: imageElement });
  }

  /**
   * Démarre la webcam
   */
  async startCamera(videoElement, onFrame) {
    if (!this.pose) {
      throw new Error('MediaPipe non initialisé');
    }

    this.camera = new Camera(videoElement, {
      onFrame: onFrame || (async () => {
        await this.pose.send({ image: videoElement });
      }),
      width: 1280,
      height: 720
    });

    await this.camera.start();
    console.log('📹 Caméra démarrée');
  }

  /**
   * Arrête la caméra
   */
  stopCamera() {
    if (this.camera) {
      this.camera.stop();
      this.camera = null;
      console.log('📹 Caméra arrêtée');
    }
  }

  /**
   * Nettoie les ressources
   */
  cleanup() {
    this.stopCamera();
    if (this.pose) {
      this.pose.close();
      this.pose = null;
    }
  }
}

const mediaPipeService = new MediaPipeService();
export default mediaPipeService;