import React, { useState } from 'react';
import axios from 'axios';
import './DomainScanner.css';

const DomainScanner = () => {
    const [host, setHost] = useState('');
    const [ports, setPorts] = useState('');
    const [scanning, setScanning] = useState(false);
    const [scanResults, setScanResults] = useState(null);
    const [error, setError] = useState(null);

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const handleScan = async (e) => {
        e.preventDefault();
        
        // Reset states
        setError(null);
        setScanResults(null);
        setScanning(true);

        try {
            // Validate host
            if (!host.trim()) {
                setError('Please enter a domain or IP address');
                setScanning(false);
                return;
            }

            // Parse ports if provided
            let portArray = null;
            if (ports.trim()) {
                portArray = ports.split(',').map(p => {
                    const port = parseInt(p.trim());
                    if (isNaN(port) || port < 1 || port > 65535) {
                        throw new Error(`Invalid port number: ${p.trim()}`);
                    }
                    return port;
                });
            }

            // Prepare request body
            const requestBody = {
                host: host.trim()
            };
            
            if (portArray && portArray.length > 0) {
                requestBody.ports = portArray;
            }

            // Make API request
            console.log('Making request to:', `${API_BASE_URL}/scan-domain`);
            console.log('Request body:', requestBody);
            
            const response = await axios.post(`${API_BASE_URL}/scan-domain`, requestBody);
            
            console.log('Response received:', response.data);
            setScanResults(response.data);
            
        } catch (err) {
            console.error('Scan error:', err);
            console.error('Error response:', err.response);
            console.error('Error message:', err.message);
            console.error('Error config:', err.config);
            
            if (err.response) {
                setError(`Scan failed: ${err.response.data.detail || err.response.statusText}`);
            } else if (err.message) {
                setError(err.message);
            } else {
                setError('An unexpected error occurred during the scan');
            }
        } finally {
            setScanning(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        } catch (e) {
            return dateString;
        }
    };

    const getQuantumSafetyBadge = (isQuantumSafe) => {
        return isQuantumSafe ? (
            <span className="badge badge-safe">✓ Quantum Safe</span>
        ) : (
            <span className="badge badge-vulnerable">⚠ Vulnerable to Quantum Attacks</span>
        );
    };

    return (
        <div className="domain-scanner-container">
            <div className="scanner-header">
                <h1>🌐 Domain TLS Scanner</h1>
                <p className="scanner-description">
                    Scan any domain or IP address to analyze its TLS certificates for quantum safety
                </p>
            </div>

            <div className="scanner-form-card">
                <form onSubmit={handleScan} className="scanner-form">
                    <div className="form-group">
                        <label htmlFor="host">
                            Domain or IP Address <span className="required">*</span>
                        </label>
                        <input
                            type="text"
                            id="host"
                            className="form-input"
                            value={host}
                            onChange={(e) => setHost(e.target.value)}
                            placeholder="example.com or 192.168.1.1"
                            disabled={scanning}
                        />
                        <small className="form-hint">
                            Enter a domain name or IP address to scan
                        </small>
                    </div>

                    <div className="form-group">
                        <label htmlFor="ports">
                            Ports (Optional)
                        </label>
                        <input
                            type="text"
                            id="ports"
                            className="form-input"
                            value={ports}
                            onChange={(e) => setPorts(e.target.value)}
                            placeholder="443, 8443, 993"
                            disabled={scanning}
                        />
                        <small className="form-hint">
                            Leave empty to scan all common TLS ports (443, 8443, 993, 995, etc.)
                            <br />
                            Or specify ports separated by commas
                        </small>
                    </div>

                    <button 
                        type="submit" 
                        className="scan-button"
                        disabled={scanning}
                    >
                        {scanning ? (
                            <>
                                <span className="spinner"></span>
                                Scanning...
                            </>
                        ) : (
                            <>
                                🔍 Start Scan
                            </>
                        )}
                    </button>
                    
                    {scanning && (
                        <div className="info-message">
                            <span className="spinner-icon">⏳</span>
                            <p>
                                <strong>Scanning & Analyzing...</strong><br />
                                Please wait while we fetch the TLS certificates and perform AI-powered 
                                quantum safety analysis. This may take 3-5 minutes depending on the 
                                number of ports and certificates. Thank you for your patience.
                            </p>
                        </div>
                    )}
                </form>
            </div>

            {error && (
                <div className="error-alert">
                    <strong>Error:</strong> {error}
                </div>
            )}

            {scanResults && (
                <div className="scan-results">
                    {/* Scan Summary */}
                    <div className="scan-summary">
                        <h2>Scan Summary</h2>
                        <div className="summary-grid">
                            <div className="summary-item">
                                <span className="summary-label">Target:</span>
                                <span className="summary-value">{scanResults.scan_info.host}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Scanned Ports:</span>
                                <span className="summary-value">
                                    {scanResults.scan_info.scanned_ports.join(', ')}
                                </span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Scan Duration:</span>
                                <span className="summary-value">
                                    {scanResults.scan_info.scan_duration_ms}ms
                                </span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Timestamp:</span>
                                <span className="summary-value">
                                    {formatDate(scanResults.scan_info.timestamp)}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Port Scan Results */}
                    <div className="port-results">
                        <h2>Port Scan Results</h2>
                        
                        {scanResults.successful_ports.length > 0 && (
                            <div className="successful-ports">
                                <h3 className="success-header">
                                    ✓ Successful ({scanResults.successful_ports.length})
                                </h3>
                                <table className="results-table">
                                    <thead>
                                        <tr>
                                            <th>Port</th>
                                            <th>Certificates Found</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {scanResults.successful_ports.map((portData) => (
                                            <tr key={portData.port}>
                                                <td>{portData.port}</td>
                                                <td>{portData.cert_count}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}

                        {scanResults.failed_ports.length > 0 && (
                            <div className="failed-ports">
                                <h3 className="error-header">
                                    ✗ Failed ({scanResults.failed_ports.length})
                                </h3>
                                <table className="results-table">
                                    <thead>
                                        <tr>
                                            <th>Port</th>
                                            <th>Error</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {scanResults.failed_ports.map((portData) => (
                                            <tr key={portData.port}>
                                                <td>{portData.port}</td>
                                                <td className="error-text">{portData.error}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>

                    {/* Certificate Analysis Results */}
                    {scanResults.certificates && scanResults.certificates.length > 0 && (
                        <div className="certificate-results">
                            <h2>Certificate Analysis ({scanResults.certificates.length})</h2>
                            
                            {scanResults.certificates.map((certData, index) => (
                                <div key={index} className="certificate-card">
                                    {certData.error ? (
                                        <div className="cert-error">
                                            <h3>Port {certData.port} - Certificate #{certData.position}</h3>
                                            <p className="error-text">{certData.error}</p>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="cert-header">
                                                <h3>
                                                    Port {certData.port} - Certificate #{certData.position}
                                                </h3>
                                                {getQuantumSafetyBadge(certData.analysis.is_quantum_safe)}
                                            </div>

                                            <div className="cert-details">
                                                <div className="detail-group">
                                                    <h4>Certificate Information</h4>
                                                    <div className="detail-item">
                                                        <span className="detail-label">Subject:</span>
                                                        <span className="detail-value">{certData.subject}</span>
                                                    </div>
                                                    <div className="detail-item">
                                                        <span className="detail-label">Issuer:</span>
                                                        <span className="detail-value">{certData.issuer}</span>
                                                    </div>
                                                    <div className="detail-item">
                                                        <span className="detail-label">Valid From:</span>
                                                        <span className="detail-value">
                                                            {formatDate(certData.analysis.valid_from)}
                                                        </span>
                                                    </div>
                                                    <div className="detail-item">
                                                        <span className="detail-label">Valid Until:</span>
                                                        <span className="detail-value">
                                                            {formatDate(certData.analysis.valid_until)}
                                                        </span>
                                                    </div>
                                                    <div className="detail-item">
                                                        <span className="detail-label">Status:</span>
                                                        <span className={certData.analysis.is_valid ? "status-valid" : "status-invalid"}>
                                                            {certData.analysis.is_valid ? '✓ Valid' : '✗ Invalid/Expired'}
                                                        </span>
                                                    </div>
                                                </div>

                                                <div className="detail-group">
                                                    <h4>Cryptographic Analysis</h4>
                                                    <div className="detail-item">
                                                        <span className="detail-label">Public Key Algorithm:</span>
                                                        <span className="detail-value">
                                                            {certData.analysis.public_key_algorithm || 'Unknown'}
                                                            {certData.analysis.public_key_size && 
                                                                ` (${certData.analysis.public_key_size} bits)`
                                                            }
                                                        </span>
                                                    </div>
                                                    <div className="detail-item">
                                                        <span className="detail-label">Signature Algorithm:</span>
                                                        <span className="detail-value">
                                                            {certData.analysis.signature_algorithm || 'Unknown'}
                                                        </span>
                                                    </div>
                                                    {certData.analysis.is_pqc && (
                                                        <div className="detail-item pqc-highlight">
                                                            <span className="detail-label">PQC Algorithm:</span>
                                                            <span className="detail-value">
                                                                {certData.analysis.pqc_algorithm}
                                                            </span>
                                                        </div>
                                                    )}
                                                </div>

                                                {certData.analysis.quantum_safe_reason && 
                                                 certData.analysis.quantum_safe_reason.length > 0 && (
                                                    <div className="detail-group">
                                                        <h4>Quantum Safety Analysis</h4>
                                                        <ul className="reason-list">
                                                            {certData.analysis.quantum_safe_reason.map((reason, idx) => (
                                                                <li key={idx}>{reason}</li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}

                                                {certData.analysis.ai_recommendation && (
                                                    <div className="detail-group ai-recommendation">
                                                        <h4>🤖 AI Recommendation</h4>
                                                        
                                                        <div className="ai-section">
                                                            <div className="vulnerability-badge">
                                                                {certData.analysis.ai_recommendation.quantum_vulnerability}
                                                            </div>
                                                        </div>

                                                        <div className="ai-section">
                                                            <h5>Primary Recommendation</h5>
                                                            <p>{certData.analysis.ai_recommendation.primary_recommendation}</p>
                                                        </div>

                                                        {certData.analysis.ai_recommendation.recommended_pqc_algorithms && 
                                                         Array.isArray(certData.analysis.ai_recommendation.recommended_pqc_algorithms) &&
                                                         certData.analysis.ai_recommendation.recommended_pqc_algorithms.length > 0 && (
                                                            <div className="ai-section">
                                                                <h5>Recommended PQC Algorithms</h5>
                                                                <ul className="pqc-algorithm-list">
                                                                    {certData.analysis.ai_recommendation.recommended_pqc_algorithms.map((alg, idx) => (
                                                                        <li key={idx}>{alg}</li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        )}

                                                        {certData.analysis.ai_recommendation.security_assessment && (
                                                            <div className="ai-section">
                                                                <h5>Security Assessment</h5>
                                                                <p style={{whiteSpace: 'pre-line'}}>
                                                                    {certData.analysis.ai_recommendation.security_assessment}
                                                                </p>
                                                            </div>
                                                        )}

                                                        {certData.analysis.ai_recommendation.performance_comparison && (
                                                            <div className="ai-section">
                                                                <h5>Performance Comparison</h5>
                                                                <p style={{whiteSpace: 'pre-line'}}>
                                                                    {certData.analysis.ai_recommendation.performance_comparison}
                                                                </p>
                                                            </div>
                                                        )}

                                                        {certData.analysis.ai_recommendation.migration_strategy && (
                                                            <div className="ai-section">
                                                                <h5>Migration Strategy</h5>
                                                                <p style={{whiteSpace: 'pre-line'}}>
                                                                    {certData.analysis.ai_recommendation.migration_strategy}
                                                                </p>
                                                            </div>
                                                        )}

                                                        {certData.analysis.ai_recommendation.risk_timeline && (
                                                            <div className="ai-section">
                                                                <h5>Risk Timeline</h5>
                                                                <p style={{whiteSpace: 'pre-line'}}>
                                                                    {certData.analysis.ai_recommendation.risk_timeline}
                                                                </p>
                                                            </div>
                                                        )}

                                                        {certData.analysis.ai_recommendation.implementation_considerations && (
                                                            <div className="ai-section">
                                                                <h5>Implementation Considerations</h5>
                                                                <p style={{whiteSpace: 'pre-line'}}>
                                                                    {certData.analysis.ai_recommendation.implementation_considerations}
                                                                </p>
                                                            </div>
                                                        )}

                                                        {certData.analysis.ai_recommendation.compliance_notes && (
                                                            <div className="ai-section">
                                                                <h5>Compliance Notes</h5>
                                                                <p style={{whiteSpace: 'pre-line'}}>
                                                                    {certData.analysis.ai_recommendation.compliance_notes}
                                                                </p>
                                                            </div>
                                                        )}

                                                        {certData.analysis.ai_recommendation.cost_benefit_analysis && (
                                                            <div className="ai-section">
                                                                <h5>Cost-Benefit Analysis</h5>
                                                                <p style={{whiteSpace: 'pre-line'}}>
                                                                    {certData.analysis.ai_recommendation.cost_benefit_analysis}
                                                                </p>
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default DomainScanner;
