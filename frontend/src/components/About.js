import React from 'react';
import './About.css';

const About = () => {
  return (
    <div className="about">
      <div className="card">
        <h1>About QuantumCertify</h1>
        <p className="intro">
          QuantumCertify is a specialized tool designed to analyze X.509 certificates and identify 
          their cryptographic algorithms to determine quantum safety in preparation for the 
          post-quantum cryptography era.
        </p>
      </div>

      <div className="card">
        <h2>🎯 Mission</h2>
        <p>
          Our mission is to help organizations assess their current cryptographic infrastructure 
          and prepare for the transition to quantum-safe cryptography. By analyzing certificates, 
          we provide valuable insights into which systems may be vulnerable to quantum attacks.
        </p>
      </div>

      <div className="card">
        <h2>🔬 How It Works</h2>
        <div className="process-steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Upload Certificate</h3>
              <p>Upload your X.509 certificate file in PEM or DER format</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Parse & Extract</h3>
              <p>We parse the certificate and extract cryptographic algorithm information</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Analyze Safety</h3>
              <p>Algorithms are checked against our database of quantum-safe algorithms</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>Generate Report</h3>
              <p>Receive detailed analysis with quantum safety recommendations</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>🛡️ Supported Algorithms</h2>
        <div className="algorithms-grid">
          <div className="algorithm-category">
            <h3>✅ Quantum-Safe Algorithms</h3>
            <ul>
              <li>CRYSTALS-Dilithium (Signatures)</li>
              <li>CRYSTALS-Kyber (Key Exchange)</li>
              <li>FALCON (Signatures)</li>
              <li>SPHINCS+ (Signatures)</li>
              <li>McEliece (Key Exchange)</li>
              <li>NTRU (Key Exchange)</li>
            </ul>
          </div>
          
          <div className="algorithm-category">
            <h3>⚠️ Classical Algorithms</h3>
            <ul>
              <li>RSA (All variants)</li>
              <li>ECC (Elliptic Curve Cryptography)</li>
              <li>DSA (Digital Signature Algorithm)</li>
              <li>ECDSA (Elliptic Curve DSA)</li>
              <li>DH (Diffie-Hellman)</li>
              <li>ECDH (Elliptic Curve DH)</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>🚨 The Quantum Threat</h2>
        <div className="threat-info">
          <p>
            Quantum computers pose a significant threat to current cryptographic systems. 
            Shor's algorithm, when run on a sufficiently powerful quantum computer, can efficiently 
            factor large integers and solve discrete logarithm problems, breaking RSA, ECC, and 
            other widely-used cryptographic algorithms.
          </p>
          
          <div className="timeline">
            <h3>Timeline & Impact</h3>
            <ul>
              <li><strong>2025-2030:</strong> Continued quantum computer development</li>
              <li><strong>2030-2035:</strong> Potential cryptographically relevant quantum computers</li>
              <li><strong>2035+:</strong> Classical cryptography may become obsolete</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>🔧 Technical Details</h2>
        <div className="tech-details">
          <div className="tech-item">
            <h3>Backend</h3>
            <p>FastAPI with Python, cryptography library for certificate parsing</p>
          </div>
          
          <div className="tech-item">
            <h3>Frontend</h3>
            <p>React.js with responsive design and modern UI components</p>
          </div>
          
          <div className="tech-item">
            <h3>Database</h3>
            <p>SQLAlchemy with support for algorithm classification and analysis</p>
          </div>
          
          <div className="tech-item">
            <h3>Supported Formats</h3>
            <p>PEM (.pem, .crt, .cer) and DER (.der) certificate formats</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>📞 Contact & Support</h2>
        <p>
          QuantumCertify is an AI-powered tool designed to help organizations prepare 
          for the post-quantum cryptography transition. Our advanced analysis provides 
          comprehensive recommendations using Google Gemini AI technology.
        </p>
        
        <div className="contact-info">
          <h3>Get In Touch</h3>
          <p>
            <strong>Email:</strong> <a href="mailto:subhashsubu106@gmail.com">subhashsubu106@gmail.com</a>
          </p>
          <p>
            For questions, contributions, feedback, or enterprise support, please don't hesitate to reach out.
          </p>
        </div>
        
        <div className="version-info">
          <p><strong>Version:</strong> 1.0.0</p>
          <p><strong>Last Updated:</strong> September 2025</p>
          <p><strong>AI Integration:</strong> Google Gemini API</p>
        </div>
      </div>

      <div className="card">
        <h2>🤖 AI-Powered Features</h2>
        <div className="ai-features">
          <div className="feature-item">
            <h3>Smart Analysis</h3>
            <p>Google Gemini AI analyzes your certificates and provides context-aware recommendations for quantum-safe migration</p>
          </div>
          
          <div className="feature-item">
            <h3>Migration Strategies</h3>
            <p>AI-generated migration plans tailored to your specific cryptographic infrastructure and security requirements</p>
          </div>
          
          <div className="feature-item">
            <h3>Risk Assessment</h3>
            <p>Intelligent vulnerability assessment with severity ratings and timeline predictions for quantum threats</p>
          </div>
          
          <div className="feature-item">
            <h3>Implementation Guidance</h3>
            <p>Step-by-step implementation notes and risk mitigation strategies powered by advanced AI reasoning</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;