import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/apiService';

const DashboardDebug = () => {
  const navigate = useNavigate();
  const [results, setResults] = useState({
    profile: null,
    history: null,
    statistics: null
  });
  const [errors, setErrors] = useState({});
  const [user, setUser] = useState(null);

  useEffect(() => {
    testAllEndpoints();
  }, []);

  const testAllEndpoints = async () => {
    console.log('🧪 TEST DES ENDPOINTS DU DASHBOARD');

    // Test 1 : /api/auth/me
    try {
      console.log('📡 Test 1: getCurrentUser()...');
      const userData = await apiService.getCurrentUser();
      console.log('✅ getCurrentUser OK:', userData);
      setUser(userData.user);
    } catch (err) {
      console.error('❌ getCurrentUser ERREUR:', err.response?.data || err.message);
      setErrors(prev => ({ ...prev, user: err.response?.data || err.message }));
    }

    // Test 2 : /api/profile
    try {
      console.log('📡 Test 2: getProfile()...');
      const profileData = await apiService.getProfile();
      console.log('✅ getProfile OK:', profileData);
      setResults(prev => ({ ...prev, profile: profileData }));
    } catch (err) {
      console.error('❌ getProfile ERREUR:', err.response?.data || err.message);
      setErrors(prev => ({ ...prev, profile: err.response?.data || err.message }));
    }

    // Test 3 : /api/profile/history
    try {
      console.log('📡 Test 3: getHistory()...');
      const historyData = await apiService.getHistory(1, 10);
      console.log('✅ getHistory OK:', historyData);
      setResults(prev => ({ ...prev, history: historyData }));
    } catch (err) {
      console.error('❌ getHistory ERREUR:', err.response?.data || err.message);
      setErrors(prev => ({ ...prev, history: err.response?.data || err.message }));
    }

    // Test 4 : /api/profile/statistics
    try {
      console.log('📡 Test 4: getStatistics()...');
      const statsData = await apiService.getStatistics(30);
      console.log('✅ getStatistics OK:', statsData);
      setResults(prev => ({ ...prev, statistics: statsData }));
    } catch (err) {
      console.error('❌ getStatistics ERREUR:', err.response?.data || err.message);
      setErrors(prev => ({ ...prev, statistics: err.response?.data || err.message }));
    }
  };

  const handleLogout = async () => {
    await apiService.logout();
    navigate('/login');
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>🧪 Dashboard Debug</h1>
      <button onClick={handleLogout} style={{ marginBottom: '20px' }}>
        Déconnexion
      </button>

      <h2>👤 Utilisateur Connecté</h2>
      {user ? (
        <pre style={{ background: '#e8f5e9', padding: '10px' }}>
          {JSON.stringify(user, null, 2)}
        </pre>
      ) : errors.user ? (
        <pre style={{ background: '#ffebee', padding: '10px' }}>
          ❌ Erreur: {JSON.stringify(errors.user, null, 2)}
        </pre>
      ) : (
        <p>Chargement...</p>
      )}

      <h2>📊 Test 1: /api/profile</h2>
      {results.profile ? (
        <pre style={{ background: '#e8f5e9', padding: '10px' }}>
          {JSON.stringify(results.profile, null, 2)}
        </pre>
      ) : errors.profile ? (
        <pre style={{ background: '#ffebee', padding: '10px' }}>
          ❌ Erreur: {JSON.stringify(errors.profile, null, 2)}
        </pre>
      ) : (
        <p>Chargement...</p>
      )}

      <h2>📜 Test 2: /api/profile/history</h2>
      {results.history ? (
        <pre style={{ background: '#e8f5e9', padding: '10px' }}>
          {JSON.stringify(results.history, null, 2)}
        </pre>
      ) : errors.history ? (
        <pre style={{ background: '#ffebee', padding: '10px' }}>
          ❌ Erreur: {JSON.stringify(errors.history, null, 2)}
        </pre>
      ) : (
        <p>Chargement...</p>
      )}

      <h2>📈 Test 3: /api/profile/statistics</h2>
      {results.statistics ? (
        <pre style={{ background: '#e8f5e9', padding: '10px' }}>
          {JSON.stringify(results.statistics, null, 2)}
        </pre>
      ) : errors.statistics ? (
        <pre style={{ background: '#ffebee', padding: '10px' }}>
          ❌ Erreur: {JSON.stringify(errors.statistics, null, 2)}
        </pre>
      ) : (
        <p>Chargement...</p>
      )}

      <hr />
      <p>
        <strong>Instructions:</strong> Ouvrez la console (F12) pour voir les détails des requêtes.
      </p>
      <button onClick={testAllEndpoints}>🔄 Relancer les tests</button>
    </div>
  );
};

export default DashboardDebug;
