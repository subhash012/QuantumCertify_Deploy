import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import CertificateUpload from './components/CertificateUpload';
import Dashboard from './components/Dashboard';
import About from './components/About';
import DomainScanner from './components/DomainScanner';
import './App.css';

function Navigation() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-header">
          <Link to="/" className="nav-logo">
            <div className="logo-icon">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="6" fill="#0052CC"/>
                <path d="M16 8L22 12V20L16 24L10 20V12L16 8Z" stroke="white" strokeWidth="2" fill="none"/>
                <circle cx="16" cy="16" r="3" fill="white"/>
              </svg>
            </div>
            <div className="logo-text">
              <span className="logo-name">QuantumCertify</span>
              <span className="logo-tagline">Enterprise Security Solutions</span>
            </div>
          </Link>
          <button 
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
        <div className={`nav-menu ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          <Link 
            to="/" 
            className={`nav-link ${isActive('/') ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            Overview
          </Link>
          <Link 
            to="/scanner" 
            className={`nav-link ${isActive('/scanner') ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            Domain Scanner
          </Link>
          <Link 
            to="/upload" 
            className={`nav-link ${isActive('/upload') ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            Certificate Analysis
          </Link>
          <Link 
            to="/about" 
            className={`nav-link ${isActive('/about') ? 'active' : ''}`}
            onClick={() => setMobileMenuOpen(false)}
          >
            About
          </Link>
          <a 
            href="mailto:quantumcertify@gmail.com" 
            className="nav-link nav-link-contact"
          >
            Contact Us
          </a>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<CertificateUpload />} />
            <Route path="/scanner" element={<DomainScanner />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        <footer className="footer">
          <div className="footer-container">
            <div className="footer-section">
              <h3>QuantumCertify</h3>
              <p>Enterprise-grade post-quantum cryptography analysis and migration solutions.</p>
            </div>
            <div className="footer-section">
              <h4>Solutions</h4>
              <ul>
                <li><Link to="/scanner">Domain Scanner</Link></li>
                <li><Link to="/upload">Certificate Analysis</Link></li>
                <li><Link to="/about">Documentation</Link></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <ul>
                <li><Link to="/about">About Us</Link></li>
                <li><a href="mailto:quantumcertify@gmail.com">Contact</a></li>
                <li><Link to="/about">Privacy Policy</Link></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Resources</h4>
              <ul>
                <li><a href="https://csrc.nist.gov/projects/post-quantum-cryptography" target="_blank" rel="noopener noreferrer">NIST PQC</a></li>
                <li><a href="https://github.com/subhash012/QuantumCertify_Deploy" target="_blank" rel="noopener noreferrer">API Documentation</a></li>
                <li><a href="mailto:quantumcertify@gmail.com?subject=Support Request">Support Center</a></li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 QuantumCertify. All rights reserved.</p>
            <p>NIST-Compliant PQC Standards | Enterprise-Grade Security</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
