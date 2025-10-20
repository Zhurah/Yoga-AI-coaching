import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/apiService';
import RadarChart from '../components/RadarChart';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [history, setHistory] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [historyPage, setHistoryPage] = useState(1);

  useEffect(() => {
    loadDashboardData();
  }, [selectedPeriod]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError('');

    try {
      // Charger toutes les données en parallèle
      const [profileData, historyData, statsData] = await Promise.all([
        apiService.getProfile(),
        apiService.getHistory(historyPage, 10),
        apiService.getStatistics(selectedPeriod)
      ]);

      setProfile(profileData.profile);
      setHistory(historyData.sessions || []);
      setStatistics(statsData.statistics);
    } catch (err) {
      console.error('Dashboard error:', err);
      setError('Erreur lors du chargement du dashboard');

      // Si non authentifié, rediriger vers login
      if (err.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await apiService.logout();
    navigate('/login');
  };

  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette session ?')) {
      return;
    }

    try {
      await apiService.deleteSession(sessionId);
      // Recharger l'historique
      loadDashboardData();
    } catch (err) {
      console.error('Delete session error:', err);
      alert('Erreur lors de la suppression de la session');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSkillLevelLabel = (level) => {
    const labels = {
      'beginner': 'Débutant',
      'intermediate': 'Intermédiaire',
      'advanced': 'Avancé'
    };
    return labels[level] || level;
  };

  const getPoseName = (pose) => {
    const names = {
      'downdog': 'Chien Tête en Bas',
      'plank': 'Planche',
      'tree': 'Arbre',
      'warrior2': 'Guerrier II',
      'goddess': 'Déesse'
    };
    return names[pose] || pose;
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">Chargement...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Tableau de Bord</h1>
          <div className="header-actions">
            <button onClick={() => navigate('/')} className="btn-secondary">
              Analyse de Pose
            </button>
            <button onClick={handleLogout} className="btn-logout">
              Déconnexion
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        {/* Profile Summary */}
        <section className="profile-summary">
          <div className="profile-card">
            <div className="profile-avatar">
              {profile?.username?.charAt(0).toUpperCase()}
            </div>
            <div className="profile-info">
              <h2>{profile?.username}</h2>
              <p className="profile-email">{profile?.email}</p>
              <span className="skill-badge">
                {getSkillLevelLabel(profile?.skill_level)}
              </span>
            </div>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{profile?.total_sessions || 0}</div>
              <div className="stat-label">Sessions Total</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {isNaN(profile?.average_global_score)
                  ? '0'
                  : Math.round(profile?.average_global_score || 0)}
              </div>
              <div className="stat-label">Score Moyen</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {getPoseName(profile?.best_pose || '-')}
              </div>
              <div className="stat-label">Meilleure Pose</div>
            </div>
          </div>
        </section>

        {/* Statistics Period Selector */}
        <section className="statistics-section">
          <div className="section-header">
            <h3>Statistiques</h3>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(Number(e.target.value))}
              className="period-selector"
            >
              <option value={7}>7 derniers jours</option>
              <option value={30}>30 derniers jours</option>
              <option value={90}>90 derniers jours</option>
            </select>
          </div>

          {statistics && (
            <div className="stats-content">
              <div className="stats-overview">
                <div className="overview-card">
                  <h4>Sessions</h4>
                  <p className="big-number">{statistics.total_sessions}</p>
                </div>
                <div className="overview-card">
                  <h4>Score Moyen</h4>
                  <p className="big-number">
                    {isNaN(statistics.average_score)
                      ? '0'
                      : Math.round(statistics.average_score || 0)}
                  </p>
                </div>
                <div className="overview-card">
                  <h4>Progression</h4>
                  <p className="big-number">
                    {statistics.improvement_rate >= 0 ? '+' : ''}
                    {Math.round(statistics.improvement_rate || 0)}%
                  </p>
                </div>
              </div>

              {/* Pose Averages */}
              {statistics.pose_averages && Object.keys(statistics.pose_averages).length > 0 && (
                <div className="pose-averages">
                  <h4>Scores par Pose</h4>
                  <div className="pose-bars">
                    {Object.entries(statistics.pose_averages).map(([pose, score]) => (
                      <div key={pose} className="pose-bar-item">
                        <span className="pose-bar-label">{getPoseName(pose)}</span>
                        <div className="pose-bar">
                          <div
                            className="pose-bar-fill"
                            style={{
                              width: `${score}%`,
                              backgroundColor: score >= 80 ? '#22c55e' : score >= 60 ? '#3b82f6' : '#f59e0b'
                            }}
                          />
                        </div>
                        <span className="pose-bar-score">{Math.round(score)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Recent History */}
        <section className="history-section">
          <div className="section-header">
            <h3>Historique Récent</h3>
          </div>

          {history.length === 0 ? (
            <div className="empty-state">
              <p>Aucune session enregistrée</p>
              <button onClick={() => navigate('/')} className="btn-primary">
                Commencer une analyse
              </button>
            </div>
          ) : (
            <div className="history-list">
              {history.map((session) => (
                <div key={session.id} className="history-card">
                  <div className="history-header">
                    <div className="history-pose-name">
                      {getPoseName(session.pose_name)}
                    </div>
                    <div className="history-date">{formatDate(session.created_at)}</div>
                  </div>

                  <div className="history-scores">
                    <div className="history-score-item">
                      <span className="score-label">Score Global</span>
                      <span className="score-value global">
                        {isNaN(session.global_score)
                          ? '0'
                          : Math.round(session.global_score)}
                      </span>
                    </div>
                    <div className="history-score-item">
                      <span className="score-label">Confiance</span>
                      <span className="score-value">
                        {Math.round(session.confidence * 100)}%
                      </span>
                    </div>
                  </div>

                  {session.indicators && (
                    <div className="history-chart">
                      <RadarChart
                        indicators={JSON.parse(session.indicators)}
                        globalScore={session.global_score}
                      />
                    </div>
                  )}

                  {session.priority_indicator && (
                    <div className="history-priority">
                      <strong>Point d'amélioration :</strong> {session.priority_indicator}
                    </div>
                  )}

                  <div className="history-actions">
                    <button
                      onClick={() => handleDeleteSession(session.id)}
                      className="btn-delete"
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
