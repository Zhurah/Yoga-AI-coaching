import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import DashboardDebug from './pages/DashboardDebug';
import apiService from './services/apiService';
import './App.css';

/**
 * Composant de route protégée
 * Redirige vers /login si l'utilisateur n'est pas authentifié
 */
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = apiService.isAuthenticated();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

/**
 * Composant principal de l'application
 * Gère le routing entre les différentes pages
 */
function App() {
  return (
    <Router>
      <Routes>
        {/* Page d'accueil - Analyse de pose (accessible à tous) */}
        <Route path="/" element={<Home />} />

        {/* Pages d'authentification */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Dashboard - Protégé par authentification */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Dashboard Debug - Pour diagnostiquer les problèmes */}
        <Route
          path="/dashboard-debug"
          element={
            <ProtectedRoute>
              <DashboardDebug />
            </ProtectedRoute>
          }
        />

        {/* Redirection par défaut */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
