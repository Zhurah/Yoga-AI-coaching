// Service pour communiquer avec le backend Python (API V2)
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Créer une instance axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Intercepteur pour ajouter le token JWT à chaque requête
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer le rafraîchissement du token
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si le token a expiré (401) et qu'on n'a pas déjà essayé de rafraîchir
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          // Réessayer la requête originale avec le nouveau token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Si le rafraîchissement échoue, déconnecter l'utilisateur
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

class ApiService {
  // ==================== ENDPOINTS PUBLICS ====================

  /**
   * Vérifie la santé du serveur
   */
  async healthCheck() {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('❌ Health check failed:', error);
      throw error;
    }
  }

  /**
   * Obtient la liste des poses disponibles
   */
  async getAvailablePoses() {
    try {
      const response = await api.get('/poses');
      return response.data;
    } catch (error) {
      console.error('❌ Erreur récupération poses:', error);
      throw error;
    }
  }

  // ==================== AUTHENTIFICATION ====================

  /**
   * Inscription d'un nouvel utilisateur
   */
  async register(email, username, password, skillLevel = 'beginner') {
    try {
      const response = await api.post('/auth/register', {
        email,
        username,
        password,
        skill_level: skillLevel
      });
      return response.data;
    } catch (error) {
      console.error('❌ Erreur inscription:', error);
      throw error;
    }
  }

  /**
   * Connexion utilisateur
   */
  async login(email, password) {
    try {
      const response = await api.post('/auth/login', {
        email,
        password
      });

      // Stocker les tokens (dans response.data.tokens)
      if (response.data.tokens) {
        if (response.data.tokens.access_token) {
          localStorage.setItem('access_token', response.data.tokens.access_token);
        }
        if (response.data.tokens.refresh_token) {
          localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
        }
      }

      return response.data;
    } catch (error) {
      console.error('❌ Erreur connexion:', error);
      throw error;
    }
  }

  /**
   * Déconnexion utilisateur
   */
  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('❌ Erreur déconnexion:', error);
    } finally {
      // Toujours supprimer les tokens localement
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  /**
   * Rafraîchir le token d'accès
   */
  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
        headers: { Authorization: `Bearer ${refreshToken}` }
      });

      if (response.data.access_token) {
        localStorage.setItem('access_token', response.data.access_token);
      }

      return response.data;
    } catch (error) {
      console.error('❌ Erreur rafraîchissement token:', error);
      throw error;
    }
  }

  /**
   * Obtenir les informations de l'utilisateur connecté
   */
  async getCurrentUser() {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      console.error('❌ Erreur récupération utilisateur:', error);
      throw error;
    }
  }

  /**
   * Vérifier si l'utilisateur est connecté
   */
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  // ==================== ANALYSE DE POSE (V2) ====================

  /**
   * Analyse complète d'une pose (V2 avec authentification)
   * Inclut: classification, qualité, score global, recommandations
   */
  async analyzeComplete(landmarks, userLevel = null) {
    try {
      const response = await api.post('/complete-analysis', {
        landmarks,
        user_level: userLevel
      });
      return response.data;
    } catch (error) {
      console.error('❌ Erreur analyse complète:', error);
      throw error;
    }
  }

  // Garder la compatibilité avec l'ancienne API (V1) pour tests
  async classifyPose(landmarks) {
    try {
      const response = await api.post('/classify', {
        landmarks
      });
      return response.data;
    } catch (error) {
      console.error('❌ Erreur classification:', error);
      throw error;
    }
  }

  async analyzePoseQuality(landmarks, poseName, userLevel = 'intermediate') {
    try {
      const response = await api.post('/analyze', {
        landmarks,
        pose_name: poseName,
        user_level: userLevel
      });
      return response.data;
    } catch (error) {
      console.error('❌ Erreur analyse qualité:', error);
      throw error;
    }
  }

  // ==================== PROFIL UTILISATEUR ====================

  /**
   * Obtenir le profil complet de l'utilisateur
   */
  async getProfile() {
    try {
      const response = await api.get('/profile');
      return response.data;
    } catch (error) {
      console.error('❌ Erreur récupération profil:', error);
      throw error;
    }
  }

  /**
   * Obtenir l'historique des sessions
   */
  async getHistory(page = 1, perPage = 20) {
    try {
      const response = await api.get('/profile/history', {
        params: { page, per_page: perPage }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Erreur récupération historique:', error);
      throw error;
    }
  }

  /**
   * Obtenir les statistiques sur une période
   */
  async getStatistics(days = 30) {
    try {
      const response = await api.get('/profile/statistics', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('❌ Erreur récupération statistiques:', error);
      throw error;
    }
  }

  /**
   * Obtenir la progression pour une pose spécifique
   */
  async getPoseProgress(poseName) {
    try {
      const response = await api.get(`/profile/pose-progress/${poseName}`);
      return response.data;
    } catch (error) {
      console.error('❌ Erreur récupération progression:', error);
      throw error;
    }
  }

  /**
   * Supprimer une session de l'historique
   */
  async deleteSession(sessionId) {
    try {
      const response = await api.delete(`/profile/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('❌ Erreur suppression session:', error);
      throw error;
    }
  }

  // ==================== RECOMMANDATIONS ====================

  /**
   * Obtenir des recommandations d'exercices
   */
  async getRecommendations(poseName, priorityIndicator, count = 3) {
    try {
      const response = await api.post('/recommendations', {
        pose_name: poseName,
        priority_indicator: priorityIndicator,
        count
      });
      return response.data;
    } catch (error) {
      console.error('❌ Erreur récupération recommandations:', error);
      throw error;
    }
  }
}

const apiService = new ApiService();
export default apiService;
