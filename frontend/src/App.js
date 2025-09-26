import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import CertificateUpload from './components/CertificateUpload';
import Dashboard from './components/Dashboard';
import About from './components/About';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              🔐 QuantumCertify
            </Link>
            <div className="nav-menu">
              <Link to="/" className="nav-link">Dashboard</Link>
              <Link to="/upload" className="nav-link">Upload Certificate</Link>
              <Link to="/about" className="nav-link">About</Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<CertificateUpload />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>&copy; 2025 QuantumCertify - Quantum-Safe Certificate Analysis</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
