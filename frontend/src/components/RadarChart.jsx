import React from 'react';
import {
  Radar,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip
} from 'recharts';
import './RadarChart.css';

// Formater le nom de l'indicateur pour l'affichage
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
    'arm_height': 'Hauteur Bras',
    'foot_height': 'Hauteur Pied',
    'shoulder_level': 'Niveau Épaules'
  };

  return nameMap[key] || key.split('_').map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
};

// Tooltip personnalisé
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="custom-tooltip">
        <p className="tooltip-label">{data.indicator}</p>
        <p className="tooltip-value">
          Score: <strong>{data.score}</strong> / {data.fullMark}
        </p>
      </div>
    );
  }
  return null;
};

/**
 * Composant RadarChart pour visualiser les indicateurs de qualité de pose
 * Affiche un diagramme radar avec les scores pour chaque indicateur
 */
const RadarChart = ({ indicators, globalScore }) => {
  // Débogage
  console.log('RadarChart - indicators:', indicators);
  console.log('RadarChart - globalScore:', globalScore);

  // Vérifier que les indicateurs existent
  if (!indicators || Object.keys(indicators).length === 0) {
    console.warn('RadarChart: Aucun indicateur fourni');
    return (
      <div className="radar-chart-empty">
        <p>Aucune donnée à afficher</p>
      </div>
    );
  }

  // Transformer les indicateurs en format compatible Recharts
  const data = Object.entries(indicators).map(([key, value]) => ({
    indicator: formatIndicatorName(key),
    score: isNaN(value) ? 0 : Math.round(value * 10) / 10, // Arrondir à 1 décimale
    fullMark: 100
  }));

  console.log('RadarChart - data transformed:', data);

  // Déterminer la couleur en fonction du score global
  const getColor = (score) => {
    if (score >= 85) return '#22c55e'; // Vert
    if (score >= 70) return '#3b82f6'; // Bleu
    if (score >= 50) return '#f59e0b'; // Orange
    return '#ef4444'; // Rouge
  };

  const chartColor = getColor(globalScore || 0);

  return (
    <div className="radar-chart-container">
      <div className="radar-chart-header">
        <h3>Analyse Détaillée</h3>
        {globalScore !== undefined && (
          <div className="global-score" style={{ borderColor: chartColor }}>
            <span className="score-label">Score Global</span>
            <span className="score-value" style={{ color: chartColor }}>
              {isNaN(globalScore) ? '0' : Math.round(globalScore)}
            </span>
          </div>
        )}
      </div>

      <div style={{ width: '100%', height: 400, marginBottom: '20px' }}>
        <RechartsRadar width={600} height={400} data={data}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="indicator"
            tick={{ fill: '#374151', fontSize: 12 }}
          />
          <PolarRadiusAxis
            domain={[0, 100]}
            tick={{ fill: '#6b7280', fontSize: 11 }}
            axisLine={false}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke={chartColor}
            fill={chartColor}
            fillOpacity={0.5}
          />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }}
          />
          <Legend />
        </RechartsRadar>
      </div>

      <div className="indicators-list">
        {data.map((item, index) => (
          <div key={index} className="indicator-item">
            <span className="indicator-name">{item.indicator}</span>
            <div className="indicator-bar">
              <div
                className="indicator-fill"
                style={{
                  width: `${item.score}%`,
                  backgroundColor: getColor(item.score)
                }}
              />
            </div>
            <span className="indicator-score">{item.score}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RadarChart;
