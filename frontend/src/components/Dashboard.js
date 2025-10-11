import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [apiStatus, setApiStatus] = useState({ status: 'checking', message: 'Checking API status...' });
  const [stats, setStats] = useState({
    totalCertificatesAnalyzed: 0,
    quantumSafeCertificates: 0,
    classicalCertificates: 0,
    lastUpdated: null,
    dataSource: 'loading'
  });
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    checkApiStatus();
    fetchDashboardStats();
    
    // Removed auto-refresh to minimize database queries and reduce costs
    // Stats will only refresh when user reloads the page
  }, []);

  const checkApiStatus = async () => {
    try {
      const response = await apiService.checkHealth();
      setApiStatus({
        status: 'healthy',
        message: 'API is running successfully',
        data: response.data
      });
    } catch (error) {
      setApiStatus({
        status: 'error',
        message: error.message || 'Unable to connect to API. Please ensure the backend server is running.'
      });
    }
  };

  const fetchDashboardStats = async () => {
    try {
      setStatsLoading(true);
      const response = await apiService.getDashboardStatistics();
      
      if (response.data && response.data.statistics) {
        const stats = response.data.statistics;
        
        setStats({
          totalCertificatesAnalyzed: stats.total_analyzed || 0,
          quantumSafeCertificates: stats.quantum_safe_count || 0,
          classicalCertificates: stats.classical_count || 0,
          lastUpdated: stats.last_updated,
          dataSource: stats.data_source || 'api'
        });
      }
    } catch (error) {
      console.error('Failed to fetch dashboard statistics:', error);
    } finally {
      setStatsLoading(false);
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'healthy': return 'status-healthy';
      case 'error': return 'status-error';
      case 'checking': return 'status-checking';
      default: return 'status-unknown';
    }
  };

  const quantumSafePercentage = stats.totalCertificatesAnalyzed > 0
    ? ((stats.quantumSafeCertificates / stats.totalCertificatesAnalyzed) * 100).toFixed(1)
    : 0;

  return (
    <div className="dashboard">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1>Quantum-Ready Certificate Analysis</h1>
          <p className="hero-subtitle">
            Enterprise-grade cryptographic assessment powered by AI. Identify quantum vulnerabilities 
            and ensure compliance with post-quantum cryptography standards.
          </p>
          <div className="hero-actions">
            <button className="btn-primary btn-large" onClick={() => window.location.href = '/upload'}>
              Analyze Certificate
            </button>
            <button className="btn-secondary btn-large" onClick={() => window.location.href = '/scanner'}>
              Scan Domain
            </button>
          </div>
        </div>
      </div>

      {/* System Status Bar */}
      <div className={`system-status-bar ${getStatusClass(apiStatus.status)}`}>
        <div className="status-indicator">
          <div className={`status-dot ${apiStatus.status}`}></div>
          <span className="status-text">
            System Status: <strong>{apiStatus.status === 'healthy' ? 'Operational' : apiStatus.status === 'checking' ? 'Initializing' : 'Offline'}</strong>
          </span>
        </div>
        {apiStatus.data && (
          <div className="system-info">
            <span>Version {apiStatus.data.version}</span>
            <span>Database: {apiStatus.data.services?.database || 'Disconnected'}</span>
            <span>AI Engine: {apiStatus.data.services?.ai_service || 'Unavailable'}</span>
          </div>
        )}
      </div>

      {/* Statistics Dashboard */}
      <div className="stats-section">
        <div className="stats-grid">
          <div className="stat-card primary">
            <div className="stat-header">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 11l3 3L22 4"></path>
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"></path>
              </svg>
            </div>
            <div className="stat-body">
              <h3>{statsLoading ? '...' : stats.totalCertificatesAnalyzed.toLocaleString()}</h3>
              <p>Total Certificates Analyzed</p>
              {stats.lastUpdated && (
                <span className="stat-meta">Last updated: {new Date(stats.lastUpdated).toLocaleDateString()}</span>
              )}
            </div>
          </div>

          <div className="stat-card success">
            <div className="stat-header">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
            <div className="stat-body">
              <h3>{statsLoading ? '...' : stats.quantumSafeCertificates.toLocaleString()}</h3>
              <p>Quantum-Safe Certificates</p>
              <span className="stat-meta">{quantumSafePercentage}% of total</span>
            </div>
          </div>

          <div className="stat-card warning">
            <div className="stat-header">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div className="stat-body">
              <h3>{statsLoading ? '...' : stats.classicalCertificates.toLocaleString()}</h3>
              <p>Classical Certificates</p>
              <span className="stat-meta">Require migration</span>
            </div>
          </div>

          <div className="stat-card info">
            <div className="stat-header">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"></path>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
            </div>
            <div className="stat-body">
              <h3>{apiStatus.status === 'healthy' ? 'Active' : 'Inactive'}</h3>
              <p>Analysis Engine</p>
              <span className="stat-meta">Advanced Security Analysis</span>
            </div>
          </div>
        </div>
      </div>

      {/* Enterprise Features */}
      <div className="features-section">
        <div className="section-header">
          <h2>Enterprise Capabilities</h2>
          <p>Comprehensive cryptographic analysis for the quantum era</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon teal">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
            </div>
            <h3>X.509 Certificate Analysis</h3>
            <p>Deep inspection of certificate structures, cryptographic algorithms, and security parameters with NIST compliance verification.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon mint">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0110 0v4"></path>
              </svg>
            </div>
            <h3>Quantum Safety Assessment</h3>
            <p>AI-powered evaluation of cryptographic resistance against quantum computing attacks based on current research and standards.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon teal">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M12 1v6m0 6v6m5.2-14.2l-4.3 4.3m0 6l-4.3 4.3M23 12h-6m-6 0H1m20.2-5.2l-4.3 4.3m0 6l-4.3 4.3"></path>
              </svg>
            </div>
            <h3>Live Domain Scanning</h3>
            <p>Real-time TLS certificate analysis for any domain or IP address with comprehensive chain validation and security scoring.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon mint">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <h3>Detailed Reporting</h3>
            <p>Executive summaries and technical reports with actionable recommendations for quantum-readiness migration strategies.</p>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="cta-section">
        <div className="cta-card">
          <h2>Ready to Assess Your Quantum Readiness?</h2>
          <p>Start analyzing your certificates today and prepare for the post-quantum cryptography transition.</p>
          <div className="cta-buttons">
            <button className="btn-primary btn-large" onClick={() => window.location.href = '/upload'}>
              Start Analysis
            </button>
            <button className="btn-outline btn-large" onClick={() => window.location.href = '/about'}>
              Learn More
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;