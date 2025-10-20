import React, { useState } from 'react';
import RadarChart from './RadarChart';
import ExerciseRecommendation, { RecommendationCard } from './ExerciseRecommendation';
import './ResultsPanel.css';

const ResultsPanel = ({ results }) => {
  const [showRecommendationModal, setShowRecommendationModal] = useState(false);

  if (!results || !results.success) {
    return (
      <div className="results-error">
        <span className="error-icon">❌</span>
        <p>Erreur lors de l'analyse</p>
      </div>
    );
  }

  const { classification, quality_analysis } = results;

  /**
   * Rendu de la section classification
   */
  const renderClassification = () => (
    <div className="classification-section">
      <h2>🎯 Pose Détectée</h2>

      <div className="pose-card">
        <div className="pose-name">
          {getPoseName(classification.pose)}
        </div>
        <div className="confidence-bar-container">
          <div className="confidence-label">
            Confiance: {(classification.confidence * 100).toFixed(1)}%
          </div>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{ width: `${classification.confidence * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* All probabilities */}
      {classification.all_probabilities && (
        <div className="all-probabilities">
          <h4>Toutes les probabilités :</h4>
          <div className="probabilities-list">
            {Object.entries(classification.all_probabilities)
              .sort((a, b) => b[1] - a[1])
              .map(([pose, prob]) => (
                <div key={pose} className="probability-item">
                  <span className="pose-label">{getPoseName(pose)}</span>
                  <div className="prob-bar-mini">
                    <div
                      className="prob-fill-mini"
                      style={{ width: `${prob * 100}%` }}
                    />
                  </div>
                  <span className="prob-value">{(prob * 100).toFixed(1)}%</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );

  /**
   * Rendu de la section qualité avec API V2
   */
  const renderQualityAnalysis = () => {
    if (!quality_analysis || !quality_analysis.indicators) {
      return (
        <div className="quality-unavailable">
          <p>⚠️ Analyse qualitative non disponible</p>
          <p className="hint">Confiance insuffisante (seuil: 70%)</p>
        </div>
      );
    }

    const {
      indicators,
      global_score,
      skill_level,
      feedback,
      priority_indicator,
      recommended_exercise
    } = quality_analysis;

    return (
      <div className="quality-section">
        <h2>📊 Analyse Qualitative</h2>

        {/* Score global et niveau */}
        <div className="quality-header">
          <div className="overall-score-card">
            <div className="score-circle">
              <svg viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#e0e0e0"
                  strokeWidth="10"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke={getScoreColor(global_score || 0)}
                  strokeWidth="10"
                  strokeDasharray={`${((global_score || 0) / 100) * 283} 283`}
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div className="score-text">
                <span className="score-number">
                  {isNaN(global_score) || global_score === undefined || global_score === null
                    ? '0'
                    : Math.round(global_score)}
                </span>
                <span className="score-label">/100</span>
              </div>
            </div>
            <p className="score-title">Score Global</p>
          </div>

          {skill_level && (
            <div className="skill-level-card">
              <p className="skill-label">Niveau</p>
              <p className="skill-value">{getSkillLevelLabel(skill_level)}</p>
            </div>
          )}
        </div>

        {/* Radar Chart pour visualisation des indicateurs */}
        {indicators && (
          <RadarChart
            indicators={indicators}
            globalScore={global_score}
          />
        )}

        {/* Indicateur prioritaire */}
        {priority_indicator && (
          <div className="priority-indicator-card">
            <h3>🎯 Point d'Amélioration Prioritaire</h3>
            <div className="priority-content">
              <div className="priority-name">
                {formatIndicatorName(priority_indicator.name)}
              </div>
              <div className="priority-score">
                Score: <strong>
                  {isNaN(priority_indicator.score) ? '0' : Math.round(priority_indicator.score)}
                </strong>
              </div>
              <div className="priority-level">
                Amélioration: <em>{priority_indicator.improvement_needed}</em>
              </div>
            </div>
          </div>
        )}

        {/* Feedback */}
        {feedback && feedback.length > 0 && (
          <div className="feedback-section">
            <h3>💬 Feedback</h3>
            <ul className="feedback-list">
              {feedback.map((item, index) => (
                <li key={index} className={getFeedbackClass(item)}>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommandation d'exercice */}
        {recommended_exercise && (
          <>
            <div className="recommendation-section">
              <h3>💪 Exercice Recommandé</h3>
              <RecommendationCard
                recommendation={recommended_exercise}
                onExpand={() => setShowRecommendationModal(true)}
              />
            </div>

            {showRecommendationModal && (
              <ExerciseRecommendation
                recommendation={recommended_exercise}
                onClose={() => setShowRecommendationModal(false)}
              />
            )}
          </>
        )}
      </div>
    );
  };

  return (
    <div className="results-panel">
      {renderClassification()}
      {renderQualityAnalysis()}
    </div>
  );
};

/**
 * Utilitaires
 */
const getScoreColor = (score) => {
  if (score >= 85) return '#22c55e'; // Vert
  if (score >= 70) return '#3b82f6'; // Bleu
  if (score >= 50) return '#f59e0b'; // Orange
  return '#ef4444'; // Rouge
};

const formatIndicatorName = (key) => {
  const nameMap = {
    'alignment': 'Alignement',
    'balance': 'Équilibre',
    'hip_height': 'Hauteur Hanches',
    'leg_straightness': 'Jambes Droites',
    'shoulder_alignment': 'Épaules Alignées',
    'arm_position': 'Position Bras',
    'back_straightness': 'Dos Droit',
    'symmetry': 'Symétrie',
    'core_strength': 'Force Core',
    'shoulder_position': 'Position Épaules',
    'knee_flexion': 'Flexion Genoux',
    'front_knee_angle': 'Angle Genou Avant',
    'arm_alignment': 'Alignement Bras',
    'hip_opening': 'Ouverture Hanches',
    'knee_alignment': 'Alignement Genoux',
    'arm_height': 'Hauteur Bras'
  };

  return nameMap[key] || key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, char => char.toUpperCase());
};

const getFeedbackClass = (feedback) => {
  if (feedback.includes('✓✓') || feedback.includes('🏆')) return 'feedback-excellent';
  if (feedback.includes('✓')) return 'feedback-good';
  if (feedback.includes('⚠️')) return 'feedback-warning';
  if (feedback.includes('💡') || feedback.includes('💪')) return 'feedback-tip';
  return 'feedback-neutral';
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
  return names[pose] || pose.toUpperCase();
};

export default ResultsPanel;
