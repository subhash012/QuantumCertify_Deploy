import React, { useState } from 'react';
import { apiService } from '../services/api';
import './CertificateUpload.css';

const CertificateUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setResult(null);
    setError(null);
  };

  const downloadPDF = () => {
    if (!result) return;

    // Debug: Log the result to see AI recommendations
    console.log('Full Result Object:', result);
    console.log('AI Recommendations:', result.ai_recommendations);

    // Helper function to safely get nested values
    const safeGet = (obj, path, defaultValue = 'Not Available') => {
      const value = path.split('.').reduce((acc, part) => acc && acc[part], obj);
      return value !== undefined && value !== null && value !== '' ? value : defaultValue;
    };

    // Format date
    const formatDate = (dateStr) => {
      if (!dateStr) return 'N/A';
      try {
        return new Date(dateStr).toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
      } catch {
        return dateStr;
      }
    };

    // Generate recommendations HTML
    const generateRecommendations = () => {
      const aiRecs = result.ai_recommendations;
      
      if (!aiRecs || (Object.keys(aiRecs).length === 0)) {
        return `
        <div class="section">
          <h2>Migration Recommendations</h2>
          <div class="recommendation">
            <p><em>No specific recommendations available for this certificate.</em></p>
            <p>For quantum-vulnerable algorithms, we recommend:</p>
            <ul style="margin-left: 20px; line-height: 1.8;">
              <li><strong>RSA:</strong> Migrate to ML-KEM (CRYSTALS-Kyber) for key encapsulation</li>
              <li><strong>ECDSA:</strong> Migrate to ML-DSA (CRYSTALS-Dilithium) or FALCON for digital signatures</li>
              <li><strong>Timeline:</strong> Begin migration within 12-24 months</li>
              <li><strong>Standards:</strong> Follow NIST FIPS 203, 204, and 205</li>
            </ul>
          </div>
        </div>`;
      }

      let html = '<div class="section"><h2>Migration Recommendations</h2>';
      
      // Public Key Recommendations
      if (aiRecs.public_key) {
        const pk = aiRecs.public_key;
        html += '<h3>Public Key Migration</h3><div class="recommendation">';
        
        if (pk.quantum_vulnerability) html += `<h4>Quantum Vulnerability</h4><p>${pk.quantum_vulnerability}</p>`;
        if (pk.security_assessment) html += `<h4>Security Assessment</h4><p>${pk.security_assessment}</p>`;
        if (pk.primary_recommendation) html += `<h4>Primary Recommendation</h4><p>${pk.primary_recommendation}</p>`;
        if (pk.recommended_pqc_algorithms && pk.recommended_pqc_algorithms.length > 0) {
          html += `<h4>Recommended Algorithms</h4><ul style="margin-left: 20px;">`;
          pk.recommended_pqc_algorithms.forEach(alg => html += `<li>${alg}</li>`);
          html += `</ul>`;
        }
        if (pk.migration_strategy) html += `<h4>Migration Strategy</h4><p>${pk.migration_strategy}</p>`;
        if (pk.implementation_considerations) html += `<h4>Implementation Considerations</h4><p>${pk.implementation_considerations}</p>`;
        if (pk.risk_timeline) html += `<h4>Risk Timeline</h4><p>${pk.risk_timeline}</p>`;
        if (pk.cost_benefit_analysis) html += `<h4>Cost-Benefit Analysis</h4><p>${pk.cost_benefit_analysis}</p>`;
        if (pk.compliance_notes) html += `<h4>Compliance Notes</h4><p>${pk.compliance_notes}</p>`;
        
        html += '</div>';
      }
      
      // Signature Recommendations
      if (aiRecs.signature) {
        const sig = aiRecs.signature;
        html += '<h3>Signature Algorithm Migration</h3><div class="recommendation">';
        
        if (sig.quantum_vulnerability) html += `<h4>Quantum Vulnerability</h4><p>${sig.quantum_vulnerability}</p>`;
        if (sig.security_assessment) html += `<h4>Security Assessment</h4><p>${sig.security_assessment}</p>`;
        if (sig.primary_recommendation) html += `<h4>Primary Recommendation</h4><p>${sig.primary_recommendation}</p>`;
        if (sig.recommended_pqc_algorithms && sig.recommended_pqc_algorithms.length > 0) {
          html += `<h4>Recommended Algorithms</h4><ul style="margin-left: 20px;">`;
          sig.recommended_pqc_algorithms.forEach(alg => html += `<li>${alg}</li>`);
          html += `</ul>`;
        }
        if (sig.migration_strategy) html += `<h4>Migration Strategy</h4><p>${sig.migration_strategy}</p>`;
        if (sig.implementation_considerations) html += `<h4>Implementation Considerations</h4><p>${sig.implementation_considerations}</p>`;
        if (sig.risk_timeline) html += `<h4>Risk Timeline</h4><p>${sig.risk_timeline}</p>`;
        if (sig.cost_benefit_analysis) html += `<h4>Cost-Benefit Analysis</h4><p>${sig.cost_benefit_analysis}</p>`;
        if (sig.compliance_notes) html += `<h4>Compliance Notes</h4><p>${sig.compliance_notes}</p>`;
        
        html += '</div>';
      }
      
      html += '</div>';
      return html;
    };

    // Generate HTML content for the report
    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>Certificate Analysis Report - QuantumCertify</title>
        <meta charset="UTF-8">
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: white;
          }
          .header {
            text-align: center;
            border-bottom: 4px solid #00A3A1;
            padding-bottom: 20px;
            margin-bottom: 40px;
          }
          .header h1 {
            color: #00A3A1;
            margin: 0 0 10px 0;
            font-size: 32px;
            font-weight: 700;
          }
          .header .subtitle {
            color: #666;
            font-size: 16px;
            margin-bottom: 15px;
          }
          .header .generated {
            color: #888;
            font-size: 13px;
            font-style: italic;
          }
          .section {
            margin-bottom: 35px;
            padding: 25px;
            border-left: 4px solid #00A3A1;
            background: #f8fafb;
            border-radius: 0 8px 8px 0;
            page-break-inside: avoid;
          }
          .section h2 {
            color: #00A3A1;
            font-size: 22px;
            margin-bottom: 20px;
            font-weight: 600;
          }
          .section h3 {
            color: #00A3A1;
            font-size: 18px;
            margin: 20px 0 15px 0;
            font-weight: 600;
            padding-bottom: 8px;
            border-bottom: 2px solid #A0D9B4;
          }
          .info-grid {
            display: grid;
            gap: 12px;
          }
          .info-row {
            display: grid;
            grid-template-columns: 180px 1fr;
            gap: 15px;
            padding: 10px 0;
            border-bottom: 1px solid #e5e7eb;
          }
          .info-row:last-child {
            border-bottom: none;
          }
          .info-label {
            font-weight: 600;
            color: #555;
          }
          .info-value {
            color: #333;
            word-break: break-word;
          }
          .badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 5px;
            font-size: 13px;
            font-weight: 600;
          }
          .badge.safe {
            background: #d1fae5;
            color: #065f46;
          }
          .badge.vulnerable {
            background: #fee2e2;
            color: #991b1b;
          }
          .badge.high {
            background: #fef3c7;
            color: #92400e;
          }
          .badge.medium {
            background: #ffedd5;
            color: #9a3412;
          }
          .recommendation {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #e5e7eb;
            page-break-inside: avoid;
          }
          .recommendation h4 {
            color: #00A3A1;
            margin: 15px 0 8px 0;
            font-size: 15px;
          }
          .recommendation h4:first-child {
            margin-top: 0;
          }
          .recommendation p {
            color: #555;
            line-height: 1.7;
            margin-bottom: 10px;
          }
          .footer {
            margin-top: 60px;
            padding-top: 30px;
            border-top: 3px solid #e5e7eb;
            text-align: center;
            color: #666;
            font-size: 13px;
          }
          .footer p {
            margin: 5px 0;
          }
          .footer strong {
            color: #00A3A1;
          }
          @media print {
            body { padding: 20px; }
            .section { page-break-inside: avoid; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>Certificate Analysis Report</h1>
          <p class="subtitle">Comprehensive Quantum Safety Assessment</p>
          <p class="generated">Generated: ${new Date().toLocaleString('en-US', { 
            dateStyle: 'full', 
            timeStyle: 'short' 
          })}</p>
        </div>

        <!-- Certificate Information -->
        <div class="section">
          <h2>Certificate Information</h2>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Subject:</span>
              <span class="info-value">${safeGet(result, 'certificate_info.subject') || safeGet(result, 'subject')}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Issuer:</span>
              <span class="info-value">${safeGet(result, 'certificate_info.issuer') || safeGet(result, 'issuer')}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Valid From:</span>
              <span class="info-value">${formatDate(safeGet(result, 'certificate_info.valid_from') || safeGet(result, 'certificate_info.not_before'))}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Valid Until:</span>
              <span class="info-value">${formatDate(safeGet(result, 'certificate_info.valid_until') || safeGet(result, 'certificate_info.not_after'))}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Serial Number:</span>
              <span class="info-value">${safeGet(result, 'certificate_info.serial_number')}</span>
            </div>
          </div>
        </div>

        <!-- Cryptographic Analysis -->
        ${result.cryptographic_analysis ? `
        <div class="section">
          <h2>Cryptographic Analysis</h2>
          ${result.cryptographic_analysis.public_key ? `
          <h3>Public Key Algorithm</h3>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Algorithm:</span>
              <span class="info-value">${safeGet(result, 'cryptographic_analysis.public_key.algorithm')}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Type:</span>
              <span class="info-value">${safeGet(result, 'cryptographic_analysis.public_key.type')}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Key Size:</span>
              <span class="info-value">${safeGet(result, 'cryptographic_analysis.public_key.size')} bits</span>
            </div>
            <div class="info-row">
              <span class="info-label">Quantum Safety:</span>
              <span class="info-value">
                <span class="badge ${result.cryptographic_analysis.public_key.is_quantum_safe ? 'safe' : 'vulnerable'}">
                  ${result.cryptographic_analysis.public_key.is_quantum_safe ? '✓ Quantum Safe' : '⚠ Quantum Vulnerable'}
                </span>
              </span>
            </div>
          </div>
          ` : ''}
          
          ${result.cryptographic_analysis.signature ? `
          <h3>Signature Algorithm</h3>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Algorithm:</span>
              <span class="info-value">${safeGet(result, 'cryptographic_analysis.signature.algorithm')}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Quantum Safety:</span>
              <span class="info-value">
                <span class="badge ${result.cryptographic_analysis.signature.is_quantum_safe ? 'safe' : 'vulnerable'}">
                  ${result.cryptographic_analysis.signature.is_quantum_safe ? '✓ Quantum Safe' : '⚠ Quantum Vulnerable'}
                </span>
              </span>
            </div>
          </div>
          ` : ''}
        </div>
        ` : ''}

        <!-- Security Assessment -->
        ${result.security_assessment ? `
        <div class="section">
          <h2>Security Assessment</h2>
          <div class="info-grid">
            <div class="info-row">
              <span class="info-label">Quantum Safety Status:</span>
              <span class="info-value">
                <span class="badge ${result.security_assessment.overall_quantum_safety === 'SAFE' ? 'safe' : 'vulnerable'}">
                  ${safeGet(result, 'security_assessment.overall_quantum_safety')}
                </span>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">Risk Level:</span>
              <span class="info-value">
                <span class="badge ${result.security_assessment.risk_level === 'HIGH' ? 'vulnerable' : result.security_assessment.risk_level === 'MEDIUM' ? 'medium' : 'safe'}">
                  ${safeGet(result, 'security_assessment.risk_level')}
                </span>
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">Migration Priority:</span>
              <span class="info-value">
                <span class="badge ${result.security_assessment.migration_urgency === 'IMMEDIATE' || result.security_assessment.migration_urgency === 'HIGH' ? 'vulnerable' : result.security_assessment.migration_urgency === 'MEDIUM' ? 'medium' : 'safe'}">
                  ${safeGet(result, 'security_assessment.migration_urgency')}
                </span>
              </span>
            </div>
          </div>
        </div>
        ` : ''}

        <!-- Recommendations -->
        ${generateRecommendations()}

        <div class="footer">
          <p><strong>QuantumCertify</strong> - Enterprise Security Solutions</p>
          <p>© 2025 QuantumCertify. All rights reserved.</p>
          <p>NIST-Compliant PQC Standards | Enterprise-Grade Security</p>
          <p style="margin-top: 10px; color: #888;">Contact: quantumcertify@gmail.com</p>
        </div>
      </body>
      </html>
    `;

    // Open in new window and trigger print dialog for PDF save
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    if (printWindow) {
      printWindow.document.write(htmlContent);
      printWindow.document.close();
      
      // Wait for content to load, then trigger print
      printWindow.onload = function() {
        setTimeout(() => {
          printWindow.document.title = `QuantumCertify_Report_${new Date().toISOString().split('T')[0]}`;
          printWindow.print();
          // Note: User can choose "Save as PDF" from print dialog
        }, 500);
      };
    } else {
      alert('Please allow popups to download the PDF report.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a certificate file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiService.uploadCertificate(file);
      console.log('Certificate analysis result:', response.data);
      setResult(response.data);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'An error occurred while processing the certificate');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (isQuantumSafe) => {
    if (isQuantumSafe === true) {
      return <span className="status-badge status-quantum-safe">✓ Quantum Safe</span>;
    } else if (isQuantumSafe === false) {
      return <span className="status-badge status-classical">⚠ Classical</span>;
    } else {
      return <span className="status-badge status-unknown">? Unknown</span>;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getRiskBadgeColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  return (
    <div className="certificate-upload">
      <div className="card">
        <h1>Certificate Analysis</h1>
        <p>Upload an X.509 certificate to analyze its cryptographic algorithms and quantum safety.</p>
        
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="form-group">
            <label htmlFor="certificate-file" className="form-label">
              Select Certificate File (PEM or DER format)
            </label>
            <input
              type="file"
              id="certificate-file"
              accept=".pem,.crt,.cer,.der"
              onChange={handleFileChange}
              className="form-input"
            />
          </div>
          
          <button 
            type="submit" 
            className="btn-primary btn-large" 
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Certificate'}
          </button>
          
          {loading && (
            <div className="info-message">
              <span className="spinner-icon"></span>
              <p>
                <strong>Analysis in Progress...</strong><br />
                This may take 2-4 minutes as we provide detailed 
                quantum safety recommendations and migration strategies. Please be patient.
              </p>
            </div>
          )}
        </form>

        {error && (
          <div className="error-message">
            <h3>❌ Error</h3>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="result-section">
            <div className="results-header">
              <h2>Certificate Analysis Report</h2>
              <p className="results-subtitle">Comprehensive quantum safety assessment and migration guidance</p>
              <button className="btn-download" onClick={downloadPDF}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Download PDF Report
              </button>
            </div>
            
            {/* Certificate Information */}
            <div className="result-card">
              <h3>Certificate Information</h3>
              <div className="info-grid">
                <div className="info-row">
                  <span className="info-label">Subject:</span>
                  <span className="info-value">{result.certificate_info?.subject || result.subject || 'N/A'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Issuer:</span>
                  <span className="info-value">{result.certificate_info?.issuer || result.issuer || 'N/A'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label">Valid From:</span>
                  <span className="info-value">
                    {result.certificate_info?.valid_from 
                      ? formatDate(result.certificate_info.valid_from) 
                      : (result.certificate_info?.not_before || 'N/A')}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Valid Until:</span>
                  <span className="info-value">
                    {result.certificate_info?.valid_until 
                      ? formatDate(result.certificate_info.valid_until) 
                      : (result.certificate_info?.not_after || (result.expiry_date ? formatDate(result.expiry_date) : 'N/A'))}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Serial Number:</span>
                  <span className="info-value">{result.certificate_info?.serial_number || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Cryptographic Analysis */}
            {result.cryptographic_analysis && (
              <div className="result-card">
                <h3>Cryptographic Analysis</h3>
                <div className="algorithm-list">
                  {/* Public Key Analysis */}
                  {result.cryptographic_analysis.public_key && (
                    <div className="algorithm-item">
                      <div className="algorithm-header">
                        <span className="algorithm-name">Public Key: {result.cryptographic_analysis.public_key.algorithm}</span>
                        <span className={`status ${result.cryptographic_analysis.public_key.is_quantum_safe ? 'safe' : 'vulnerable'}`}>
                          {result.cryptographic_analysis.public_key.is_quantum_safe ? 'Quantum Safe' : 'Quantum Vulnerable'}
                        </span>
                      </div>
                      <div className="algorithm-details">
                        <p><strong>Type:</strong> {result.cryptographic_analysis.public_key.type}</p>
                        <p><strong>Key Size:</strong> {result.cryptographic_analysis.public_key.size} bits</p>
                        {result.cryptographic_analysis.public_key.oid && (
                          <p><strong>OID:</strong> {result.cryptographic_analysis.public_key.oid}</p>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Signature Analysis */}
                  {result.cryptographic_analysis.signature && (
                    <div className="algorithm-item">
                      <div className="algorithm-header">
                        <span className="algorithm-name">Signature: {result.cryptographic_analysis.signature.algorithm}</span>
                        <span className={`status ${result.cryptographic_analysis.signature.is_quantum_safe ? 'safe' : 'vulnerable'}`}>
                          {result.cryptographic_analysis.signature.is_quantum_safe ? 'Quantum Safe' : 'Quantum Vulnerable'}
                        </span>
                      </div>
                      <div className="algorithm-details">
                        <p><strong>OID:</strong> {result.cryptographic_analysis.signature.oid}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Fallback for old format */}
            {!result.cryptographic_analysis && result.public_key_algorithm && (
              <div className="result-grid">
                <div className="result-card">
                  <h3>Public Key Algorithm</h3>
                  <div className="info-row">
                    <span className="info-label">Algorithm:</span>
                    <span className="info-value">{result.public_key_algorithm}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Key Type:</span>
                    <span className="info-value">{result.key_type}</span>
                  </div>
                  {result.key_size && (
                    <div className="info-row">
                      <span className="info-label">Key Size:</span>
                      <span className="info-value">{result.key_size} bits</span>
                    </div>
                  )}
                  <div className="info-row">
                    <span className="info-label">Quantum Safety:</span>
                    <span className="info-value">{getStatusBadge(result.public_key_is_pqc)}</span>
                  </div>
                </div>

                <div className="result-card">
                  <h3>Signature Algorithm</h3>
                  <div className="info-row">
                    <span className="info-label">Algorithm:</span>
                    <span className="info-value">{result.signature_algorithm}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Quantum Safety:</span>
                    <span className="info-value">{getStatusBadge(result.signature_is_pqc)}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Security Assessment */}
            {result.security_assessment && (
              <div className="result-card">
                <h3>Security Assessment</h3>
                <div className="security-assessment">
                  <div className="overall-risk">
                    <span className="risk-label">Quantum Safety:</span>
                    <span 
                      className="risk-badge" 
                      style={{ backgroundColor: getRiskBadgeColor(result.security_assessment.overall_quantum_safety) }}
                    >
                      {result.security_assessment.overall_quantum_safety}
                    </span>
                  </div>
                  
                  <div className="overall-risk">
                    <span className="risk-label">Risk Level:</span>
                    <span 
                      className="risk-badge" 
                      style={{ backgroundColor: getRiskBadgeColor(result.security_assessment.risk_level) }}
                    >
                      {result.security_assessment.risk_level}
                    </span>
                  </div>

                  <div className="overall-risk">
                    <span className="risk-label">Migration Priority:</span>
                    <span 
                      className="risk-badge" 
                      style={{ backgroundColor: getPriorityColor(result.security_assessment.migration_urgency) }}
                    >
                      {result.security_assessment.migration_urgency}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Fallback Security Assessment */}
            {!result.security_assessment && result.public_key_is_pqc !== undefined && (
              <div className="result-card">
                <h3>Security Assessment</h3>
                <div className="security-summary">
                  {(result.public_key_is_pqc === true || result.signature_is_pqc === true) ? (
                    <div className="security-good">
                      <h4>✅ Quantum-Resistant Elements Detected</h4>
                      <p>This certificate uses some quantum-safe cryptographic algorithms.</p>
                    </div>
                  ) : (result.public_key_is_pqc === false && result.signature_is_pqc === false) ? (
                    <div className="security-warning">
                      <h4>⚠️ Classical Cryptography Only</h4>
                      <p>This certificate uses only classical algorithms that may be vulnerable to quantum attacks.</p>
                    </div>
                  ) : (
                    <div className="security-unknown">
                      <h4>❓ Unknown Quantum Safety</h4>
                      <p>Unable to determine quantum safety of the algorithms used.</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* AI Recommendations */}
            {result.ai_recommendations && (
              <div className="result-card ai-recommendations">
                <h3>Migration Recommendations</h3>
                
                {/* Public Key Recommendations */}
                {result.ai_recommendations.public_key && (
                  <div className="recommendation-section">
                    <h4>Public Key Migration</h4>
                    <div className="strategy-item">
                      <div className="vulnerability-assessment">
                        <strong>Quantum Vulnerability:</strong> 
                        <span className="vulnerability-level">{result.ai_recommendations.public_key.quantum_vulnerability}</span>
                      </div>
                      
                      <div className="primary-recommendation">
                        <strong>Primary Recommendation:</strong>
                        <p>{result.ai_recommendations.public_key.primary_recommendation}</p>
                      </div>

                      <div className="recommended-algorithms">
                        <strong>Recommended Post-Quantum Algorithms:</strong>
                        <ul>
                          {result.ai_recommendations.public_key.recommended_pqc_algorithms.map((alg, index) => (
                            <li key={index}>{alg}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="security-details">
                        <p><strong>Security Assessment:</strong> {result.ai_recommendations.public_key.security_assessment}</p>
                        <p><strong>Performance:</strong> {result.ai_recommendations.public_key.performance_comparison}</p>
                        <p><strong>Migration Strategy:</strong> {result.ai_recommendations.public_key.migration_strategy}</p>
                        <p><strong>Timeline:</strong> {result.ai_recommendations.public_key.risk_timeline}</p>
                      </div>

                      <div className="implementation-notes">
                        <h5>Implementation Considerations</h5>
                        <p>{result.ai_recommendations.public_key.implementation_considerations}</p>
                        <p><strong>Compliance:</strong> {result.ai_recommendations.public_key.compliance_notes}</p>
                        <p><strong>Cost-Benefit:</strong> {result.ai_recommendations.public_key.cost_benefit_analysis}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Signature Recommendations */}
                {result.ai_recommendations.signature && (
                  <div className="recommendation-section">
                    <h4>✍️ Digital Signature Migration</h4>
                    <div className="strategy-item">
                      <div className="vulnerability-assessment">
                        <strong>Quantum Vulnerability:</strong> 
                        <span className="vulnerability-level">{result.ai_recommendations.signature.quantum_vulnerability}</span>
                      </div>
                      
                      <div className="primary-recommendation">
                        <strong>Primary Recommendation:</strong>
                        <p>{result.ai_recommendations.signature.primary_recommendation}</p>
                      </div>

                      <div className="recommended-algorithms">
                        <strong>Recommended Post-Quantum Algorithms:</strong>
                        <ul>
                          {result.ai_recommendations.signature.recommended_pqc_algorithms.map((alg, index) => (
                            <li key={index}>{alg}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="security-details">
                        <p><strong>Security Assessment:</strong> {result.ai_recommendations.signature.security_assessment}</p>
                        <p><strong>Performance:</strong> {result.ai_recommendations.signature.performance_comparison}</p>
                        <p><strong>Migration Strategy:</strong> {result.ai_recommendations.signature.migration_strategy}</p>
                        <p><strong>Timeline:</strong> {result.ai_recommendations.signature.risk_timeline}</p>
                      </div>

                      <div className="implementation-notes">
                        <h5>Implementation Considerations</h5>
                        <p>{result.ai_recommendations.signature.implementation_considerations}</p>
                        <p><strong>Compliance:</strong> {result.ai_recommendations.signature.compliance_notes}</p>
                        <p><strong>Cost-Benefit:</strong> {result.ai_recommendations.signature.cost_benefit_analysis}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Fallback Recommendations */}
            {result.recommendations && Array.isArray(result.recommendations) && result.recommendations.length > 0 && !result.ai_recommendations && (
              <div className="result-card">
                <h3>Post-Quantum Migration Recommendations</h3>
                <div className="recommendations">
                  {result.recommendations.map((rec, index) => (
                    <div key={index} className="recommendation-item">
                      <h4>{rec.algorithm}</h4>
                      <p><strong>Priority:</strong> <span className={`priority ${rec.priority}`}>{rec.priority}</span></p>
                      <p><strong>Reason:</strong> {rec.reason}</p>
                      <p><strong>Alternative:</strong> {rec.alternative}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CertificateUpload;