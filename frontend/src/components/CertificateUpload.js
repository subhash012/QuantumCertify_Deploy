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
            className="button-primary" 
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Certificate'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <h3>❌ Error</h3>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="result-section">
            <h2>📄 Certificate Analysis Results</h2>
            
            {/* Certificate Information */}
            <div className="result-card">
              <h3>📝 Certificate Information</h3>
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
                <h3>🔐 Cryptographic Analysis</h3>
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
                  <h3>🔑 Public Key Algorithm</h3>
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
                  <h3>✍️ Signature Algorithm</h3>
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
                <h3>🛡️ Security Assessment</h3>
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
                <h3>🛡️ Security Assessment</h3>
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
                <h3>🤖 AI-Powered Migration Recommendations</h3>
                
                {/* Public Key Recommendations */}
                {result.ai_recommendations.public_key && (
                  <div className="recommendation-section">
                    <h4>🔑 Public Key Migration</h4>
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

            {/* System Information */}
            {result.system_info && (
              <div className="result-card">
                <h3>ℹ️ Analysis Information</h3>
                <div className="system-info">
                  <div className="info-row">
                    <span className="info-label">Analysis Time:</span>
                    <span className="info-value">{new Date(result.system_info.analysis_timestamp).toLocaleString()}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">API Version:</span>
                    <span className="info-value">{result.system_info.api_version}</span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">AI Powered:</span>
                    <span className="info-value">
                      {result.system_info.ai_powered ? (
                        <span className="status safe">✓ Yes ({result.system_info.ai_provider})</span>
                      ) : (
                        <span className="status vulnerable">✗ Rule-based</span>
                      )}
                    </span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Database:</span>
                    <span className="info-value">
                      {result.system_info.database_connected ? (
                        <span className="status safe">✓ Connected</span>
                      ) : (
                        <span className="status vulnerable">✗ Disconnected</span>
                      )}
                    </span>
                  </div>
                  <div className="info-row">
                    <span className="info-label">Status:</span>
                    <span className="info-value status safe">{result.status}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Fallback Recommendations */}
            {result.recommendations && Array.isArray(result.recommendations) && result.recommendations.length > 0 && !result.ai_recommendations && (
              <div className="result-card">
                <h3>📋 Post-Quantum Migration Recommendations</h3>
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