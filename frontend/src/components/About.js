import React from 'react';
import './About.css';

const About = () => {
  return (
    <div className="about">
      {/* Hero Section */}
      <div className="about-hero">
        <div className="hero-content">
          <h1>About QuantumCertify</h1>
          <p className="hero-subtitle">
            Enterprise-grade cryptographic analysis for the quantum era. Powered by AI to safeguard 
            your organization's digital infrastructure against emerging quantum computing threats.
          </p>
        </div>
      </div>

      {/* Mission Section */}
      <div className="mission-section">
        <div className="section-container">
          <div className="section-header-center">
            <h2>Our Mission</h2>
            <div className="header-underline"></div>
          </div>
          <p className="mission-text">
            QuantumCertify empowers organizations worldwide to assess, understand, and transition their 
            cryptographic infrastructure to quantum-safe standards. We provide comprehensive certificate 
            analysis, AI-powered recommendations, and actionable insights to ensure your systems remain 
            secure in the post-quantum cryptography landscape.
          </p>
          <div className="mission-stats">
            <div className="stat-item">
              <div className="stat-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
              </div>
              <h3>Quantum-Safe</h3>
              <p>NIST-approved algorithms</p>
            </div>
            <div className="stat-item">
              <div className="stat-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"></path>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
              </div>
              <h3>Advanced Analysis</h3>
              <p>Deep security insights</p>
            </div>
            <div className="stat-item">
              <div className="stat-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
              </div>
              <h3>Real-Time</h3>
              <p>Instant analysis & reports</p>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="how-it-works-section">
        <div className="section-container">
          <div className="section-header-center">
            <h2>How It Works</h2>
            <div className="header-underline"></div>
            <p className="section-description">
              Our streamlined process delivers comprehensive cryptographic analysis in seconds
            </p>
          </div>
          
          <div className="process-timeline">
            <div className="timeline-step">
              <div className="step-number">01</div>
              <div className="step-content">
                <h3>Upload Certificate</h3>
                <p>
                  Submit your X.509 certificate via file upload or scan domains directly. 
                  Supports PEM, DER, CRT, and CER formats with automatic format detection.
                </p>
              </div>
              <div className="step-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
              </div>
            </div>

            <div className="timeline-connector"></div>

            <div className="timeline-step">
              <div className="step-number">02</div>
              <div className="step-content">
                <h3>Deep Analysis</h3>
                <p>
                  Advanced parsing extracts public key algorithms, signature algorithms, key sizes, 
                  and cryptographic parameters using industry-standard libraries.
                </p>
              </div>
              <div className="step-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8"></circle>
                  <path d="M21 21l-4.35-4.35"></path>
                </svg>
              </div>
            </div>

            <div className="timeline-connector"></div>

            <div className="timeline-step">
              <div className="step-number">03</div>
              <div className="step-content">
                <h3>Security Assessment</h3>
                <p>
                  Our advanced engine evaluates quantum safety, generates migration strategies, 
                  and provides context-aware security recommendations.
                </p>
              </div>
              <div className="step-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"></path>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>
                </svg>
              </div>
            </div>

            <div className="timeline-connector"></div>

            <div className="timeline-step">
              <div className="step-number">04</div>
              <div className="step-content">
                <h3>Actionable Report</h3>
                <p>
                  Receive comprehensive analysis with risk levels, compliance status, 
                  and detailed migration roadmaps for quantum readiness.
                </p>
              </div>
              <div className="step-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technology Stack Section */}
      <div className="technology-section">
        <div className="section-container">
          <div className="section-header-center">
            <h2>Technology Stack</h2>
            <div className="header-underline"></div>
            <p className="section-description">
              Built with cutting-edge technologies for performance, security, and scalability
            </p>
          </div>

          <div className="tech-grid">
            <div className="tech-card">
              <div className="tech-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="16 18 22 12 16 6"></polyline>
                  <polyline points="8 6 2 12 8 18"></polyline>
                </svg>
              </div>
              <h3>Backend</h3>
              <p>FastAPI (Python 3.12)</p>
              <ul>
                <li>Async/await architecture</li>
                <li>Cryptography library</li>
                <li>SQLAlchemy ORM</li>
                <li>Azure SQL Database</li>
              </ul>
            </div>

            <div className="tech-card">
              <div className="tech-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                  <line x1="8" y1="21" x2="16" y2="21"></line>
                  <line x1="12" y1="17" x2="12" y2="21"></line>
                </svg>
              </div>
              <h3>Frontend</h3>
              <p>React 18</p>
              <ul>
                <li>Modern hooks & context</li>
                <li>React Router v6</li>
                <li>Responsive design</li>
                <li>Unisys theme</li>
              </ul>
            </div>

            <div className="tech-card">
              <div className="tech-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"></path>
                </svg>
              </div>
              <h3>Analysis Engine</h3>
              <p>Advanced Security Platform</p>
              <ul>
                <li>30-second analysis</li>
                <li>Context-aware insights</li>
                <li>Migration strategies</li>
                <li>Risk assessment</li>
              </ul>
            </div>

            <div className="tech-card">
              <div className="tech-icon">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </div>
              <h3>Performance</h3>
              <p>Optimized Analysis</p>
              <ul>
                <li>37-54 sec scans</li>
                <li>Concurrent processing</li>
                <li>Caching strategies</li>
                <li>Real-time updates</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Quantum Threat Section */}
      <div className="threat-section">
        <div className="section-container">
          <div className="section-header-center">
            <h2>Understanding the Quantum Threat</h2>
            <div className="header-underline"></div>
          </div>

          <div className="threat-content">
            <div className="threat-explanation">
              <h3>The Challenge</h3>
              <p>
                Quantum computers leverage quantum mechanical phenomena to solve certain mathematical 
                problems exponentially faster than classical computers. Shor's algorithm, running on 
                a cryptographically-relevant quantum computer (CRQC), can efficiently factor large 
                integers and solve discrete logarithm problems—the mathematical foundations of RSA, 
                ECC, and most current public-key cryptography.
              </p>
            </div>

            <div className="threat-timeline">
              <h3>Timeline & Projections</h3>
              <div className="timeline-items">
                <div className="timeline-item">
                  <div className="timeline-year">2024-2025</div>
                  <div className="timeline-desc">
                    <strong>Current State:</strong> NIST finalizes post-quantum cryptography standards. 
                    Organizations begin assessment and planning phases.
                  </div>
                </div>
                <div className="timeline-item">
                  <div className="timeline-year">2025-2030</div>
                  <div className="timeline-desc">
                    <strong>Migration Phase:</strong> Industry-wide transition to PQC algorithms. 
                    Hybrid approaches combining classical and quantum-safe methods.
                  </div>
                </div>
                <div className="timeline-item">
                  <div className="timeline-year">2030-2035</div>
                  <div className="timeline-desc">
                    <strong>Quantum Era:</strong> Potential emergence of cryptographically-relevant 
                    quantum computers capable of breaking classical encryption.
                  </div>
                </div>
                <div className="timeline-item">
                  <div className="timeline-year">2035+</div>
                  <div className="timeline-desc">
                    <strong>Post-Quantum Security:</strong> Classical cryptography considered 
                    obsolete for sensitive applications. PQC becomes the standard.
                  </div>
                </div>
              </div>
            </div>

            <div className="threat-impact">
              <h3>Impact & Urgency</h3>
              <div className="impact-grid">
                <div className="impact-item">
                  <strong>"Harvest Now, Decrypt Later"</strong>
                  <p>
                    Adversaries are already collecting encrypted data to decrypt once quantum 
                    computers become available, making migration urgent even before CRQC emergence.
                  </p>
                </div>
                <div className="impact-item">
                  <strong>Regulatory Compliance</strong>
                  <p>
                    Government agencies and financial institutions face mandates to transition 
                    to quantum-safe cryptography by specific deadlines.
                  </p>
                </div>
                <div className="impact-item">
                  <strong>Long-Term Data Protection</strong>
                  <p>
                    Data requiring confidentiality beyond 10-15 years must be protected with 
                    PQC today to prevent future quantum-based breaches.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Algorithms Section */}
      <div className="algorithms-section">
        <div className="section-container">
          <div className="section-header-center">
            <h2>Cryptographic Algorithm Coverage</h2>
            <div className="header-underline"></div>
            <p className="section-description">
              Comprehensive analysis of classical and post-quantum cryptographic algorithms
            </p>
          </div>

          <div className="algorithms-comparison">
            <div className="algorithm-column quantum-safe-column">
              <div className="column-header">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                  <polyline points="9 12 11 14 15 10"></polyline>
                </svg>
                <h3>NIST-Approved Quantum-Safe</h3>
              </div>
              <ul className="algorithm-list">
                <li>
                  <strong>CRYSTALS-Kyber</strong>
                  <span>Key Encapsulation (KEM)</span>
                </li>
                <li>
                  <strong>CRYSTALS-Dilithium</strong>
                  <span>Digital Signatures</span>
                </li>
                <li>
                  <strong>FALCON</strong>
                  <span>Digital Signatures (Compact)</span>
                </li>
                <li>
                  <strong>SPHINCS+</strong>
                  <span>Stateless Hash-Based Signatures</span>
                </li>
                <li>
                  <strong>Classic McEliece</strong>
                  <span>Key Encapsulation (Conservative)</span>
                </li>
                <li>
                  <strong>BIKE, HQC</strong>
                  <span>Alternative KEMs (Round 4)</span>
                </li>
              </ul>
            </div>

            <div className="algorithm-column classical-column">
              <div className="column-header">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"></path>
                  <line x1="12" y1="9" x2="12" y2="13"></line>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <h3>Classical (Quantum-Vulnerable)</h3>
              </div>
              <ul className="algorithm-list">
                <li>
                  <strong>RSA (1024-4096 bit)</strong>
                  <span>Public Key Encryption & Signatures</span>
                </li>
                <li>
                  <strong>ECDSA (P-256, P-384, P-521)</strong>
                  <span>Elliptic Curve Signatures</span>
                </li>
                <li>
                  <strong>ECDH</strong>
                  <span>Elliptic Curve Key Exchange</span>
                </li>
                <li>
                  <strong>DSA</strong>
                  <span>Digital Signature Algorithm</span>
                </li>
                <li>
                  <strong>DH (Diffie-Hellman)</strong>
                  <span>Key Exchange Protocol</span>
                </li>
                <li>
                  <strong>Ed25519, X25519</strong>
                  <span>Modern Elliptic Curves</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Section */}
      <div className="contact-section">
        <div className="section-container">
          <div className="contact-card">
            <div className="contact-content">
              <h2>Get Started Today</h2>
              <p>
                Ready to assess your organization's quantum readiness? QuantumCertify provides 
                the insights you need to secure your cryptographic infrastructure for the future.
              </p>
              <div className="cta-buttons">
                <button className="btn-primary btn-large" onClick={() => window.location.href = '/upload'}>
                  Analyze Certificate
                </button>
                <button className="btn-secondary btn-large" onClick={() => window.location.href = '/scanner'}>
                  Scan Domain
                </button>
              </div>
            </div>
            <div className="contact-info">
              <h3>Contact & Support</h3>
              <div className="info-item">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                  <polyline points="22,6 12,13 2,6"></polyline>
                </svg>
                <div>
                  <strong>Email</strong>
                  <a href="mailto:quantumcertify@gmail.com">quantumcertify@gmail.com</a>
                </div>
              </div>
              <div className="info-item">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 11a3 3 0 1 0 6 0a3 3 0 0 0 -6 0"></path>
                  <path d="M17.657 16.657l-4.243 4.243a2 2 0 0 1 -2.827 0l-4.244 -4.243a8 8 0 1 1 11.314 0z"></path>
                </svg>
                <div>
                  <strong>Version</strong>
                  <span>1.0.0 (October 2025)</span>
                </div>
              </div>
              <div className="info-item">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"></path>
                  <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
                <div>
                  <strong>Advanced Analytics</strong>
                  <span>Enterprise Security Platform</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Note */}
      <div className="about-footer">
        <div className="section-container">
          <p>
            QuantumCertify is designed to help organizations prepare for the post-quantum cryptography 
            transition. Analysis results are generated using AI and should be validated by security 
            professionals for critical infrastructure decisions.
          </p>
        </div>
      </div>
    </div>
  );
};

export default About;