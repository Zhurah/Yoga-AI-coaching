import React, { useState } from 'react';
import './ExerciseRecommendation.css';

/**
 * Composant pour afficher les recommandations d'exercices
 * Affiche une modal avec les détails de l'exercice recommandé
 */
const ExerciseRecommendation = ({ recommendation, onClose }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!recommendation) return null;

  const getDifficultyColor = (difficulty) => {
    const colors = {
      'beginner': '#22c55e',
      'intermediate': '#3b82f6',
      'advanced': '#ef4444'
    };
    return colors[difficulty] || '#6b7280';
  };

  const getDifficultyLabel = (difficulty) => {
    const labels = {
      'beginner': 'Débutant',
      'intermediate': 'Intermédiaire',
      'advanced': 'Avancé'
    };
    return labels[difficulty] || difficulty;
  };

  return (
    <div className="recommendation-overlay" onClick={onClose}>
      <div
        className={`recommendation-modal ${isExpanded ? 'expanded' : 'collapsed'}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="recommendation-header">
          <div className="recommendation-title-section">
            <h3>{recommendation.title}</h3>
            <div className="recommendation-meta">
              <span
                className="difficulty-badge"
                style={{ backgroundColor: getDifficultyColor(recommendation.difficulty) }}
              >
                {getDifficultyLabel(recommendation.difficulty)}
              </span>
              <span className="duration-badge">
                {recommendation.duration}
              </span>
            </div>
          </div>
          <div className="recommendation-actions">
            <button
              className="btn-toggle"
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? 'Réduire' : 'Agrandir'}
            >
              {isExpanded ? '−' : '+'}
            </button>
            <button
              className="btn-close"
              onClick={onClose}
              title="Fermer"
            >
              ×
            </button>
          </div>
        </div>

        {isExpanded && (
          <div className="recommendation-body">
            <p className="recommendation-description">
              {recommendation.description}
            </p>

            {recommendation.target_indicator && (
              <div className="target-indicator">
                <strong>Cible :</strong> {recommendation.target_indicator}
              </div>
            )}

            <div className="recommendation-steps">
              <h4>Étapes :</h4>
              <ol>
                {recommendation.steps.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
            </div>

            {recommendation.benefit && (
              <div className="recommendation-benefit">
                <strong>Bénéfice :</strong> {recommendation.benefit}
              </div>
            )}

            {recommendation.motivation && (
              <div className="recommendation-motivation">
                {recommendation.motivation}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Composant compact pour afficher la recommandation dans ResultsPanel
 */
export const RecommendationCard = ({ recommendation, onExpand }) => {
  if (!recommendation) return null;

  const getDifficultyColor = (difficulty) => {
    const colors = {
      'beginner': '#22c55e',
      'intermediate': '#3b82f6',
      'advanced': '#ef4444'
    };
    return colors[difficulty] || '#6b7280';
  };

  return (
    <div className="recommendation-card" onClick={onExpand}>
      <div className="recommendation-card-header">
        <h4>{recommendation.title}</h4>
        <span
          className="difficulty-badge small"
          style={{ backgroundColor: getDifficultyColor(recommendation.difficulty) }}
        >
          {recommendation.duration}
        </span>
      </div>
      <p className="recommendation-card-description">
        {recommendation.description}
      </p>
      <button className="btn-view-details">
        Voir les détails →
      </button>
    </div>
  );
};

export default ExerciseRecommendation;
