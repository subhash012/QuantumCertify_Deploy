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
    
    // Set up periodic refresh of statistics
    const statsInterval = setInterval(fetchDashboardStats, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(statsInterval);
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
      // Keep existing stats on error
    } finally {
      setStatsLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return '✅';
      case 'error': return '❌';
      case 'checking': return '🔄';
      default: return '❓';
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

  return (
    <div className="dashboard">
      <div className="hero-section">
        <div className="card hero-card">
          <h1>🔐 QuantumCertify Dashboard</h1>
          <p className="hero-description">
            Analyze X.509 certificates to identify quantum-safe cryptographic algorithms 
            and prepare for the post-quantum cryptography era.
          </p>
          
          <div className={`api-status ${getStatusClass(apiStatus.status)}`}>
            <h3>{getStatusIcon(apiStatus.status)} API Status</h3>
            <p>{apiStatus.message}</p>
            {apiStatus.data && (
              <div className="api-details">
                <small>
                  Version: {apiStatus.data.version} | 
                  Database: {apiStatus.data.services?.database || 'Not connected'} | 
                  AI Service: {apiStatus.data.services?.ai_service || 'Not available'}
                </small>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="stats-section">
        <div className="stats-header">
          <h2>📈 Certificate Analysis Statistics</h2>
        </div>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <h3>{stats.totalCertificatesAnalyzed}</h3>
              <p>Total Analyzed</p>
            </div>
          </div>
          
          <div className="stat-card quantum-safe">
            <div className="stat-icon">🛡️</div>
            <div className="stat-content">
              <h3>{stats.quantumSafeCertificates}</h3>
              <p>Quantum Safe</p>
            </div>
          </div>
          
          <div className="stat-card classical">
            <div className="stat-icon">⚠️</div>
            <div className="stat-content">
              <h3>{stats.classicalCertificates}</h3>
              <p>Classical Only</p>
            </div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="card">
          <h2>🚀 Features</h2>
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">🔍</div>
              <h3>Certificate Analysis</h3>
              <p>Upload and analyze X.509 certificates to identify cryptographic algorithms</p>
            </div>
            
            <div className="feature-item">
              <div className="feature-icon">🛡️</div>
              <h3>Quantum Safety Check</h3>
              <p>Determine if certificates use quantum-safe or classical cryptographic algorithms</p>
            </div>
            
            <div className="feature-item">
              <div className="feature-icon">📊</div>
              <h3>Detailed Reports</h3>
              <p>Get comprehensive analysis including algorithm details and security recommendations</p>
            </div>
            
            <div className="feature-item">
              <div className="feature-icon">⚡</div>
              <h3>Fast Processing</h3>
              <p>Quick certificate parsing and analysis with real-time results</p>
            </div>
          </div>
        </div>
      </div>

      <div className="info-section">
        <div className="card">
          <h2>💡 About Post-Quantum Cryptography</h2>
          <div className="info-content">
            <p>
              Post-quantum cryptography refers to cryptographic algorithms that are thought to be secure 
              against an attack by a quantum computer. As quantum computers become more powerful, 
              traditional cryptographic algorithms like RSA and ECC may become vulnerable.
            </p>
            <br />
            <p>
              <strong>Why it matters:</strong>
            </p>
            <ul>
              <li>Quantum computers could break current encryption methods</li>
              <li>Organizations need to transition to quantum-safe algorithms</li>
              <li>Certificate analysis helps identify vulnerable systems</li>
              <li>Early preparation ensures security in the quantum era</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;