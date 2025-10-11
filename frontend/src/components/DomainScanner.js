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
            <span className="badge badge-safe">Quantum Safe</span>
        ) : (
            <span className="badge badge-vulnerable">Vulnerable to Quantum Attacks</span>
        );
    };

    const downloadPDF = () => {
        if (!scanResults) return;

        // Debug: Log the scan results structure
        console.log('Full Scan Results:', scanResults);
        console.log('Certificates:', scanResults.certificates);
        if (scanResults.certificates && scanResults.certificates.length > 0) {
            console.log('First Certificate:', scanResults.certificates[0]);
        }

        // Helper function to safely get nested values
        const safeGet = (obj, path, defaultValue = 'N/A') => {
            const value = path.split('.').reduce((acc, part) => acc && acc[part], obj);
            return value !== undefined && value !== null && value !== '' ? value : defaultValue;
        };

        // Format date
        const formatDatePDF = (dateStr) => {
            if (!dateStr) return 'N/A';
            try {
                return new Date(dateStr).toLocaleString('en-US', { 
                    dateStyle: 'full', 
                    timeStyle: 'short' 
                });
            } catch {
                return dateStr;
            }
        };

        // Generate certificate details HTML
        const generateCertificateDetails = () => {
            console.log('generateCertificateDetails called');
            console.log('certificates in generator:', scanResults.certificates);
            
            let html = '';
            
            // Check if certificates exists and has data
            if (!scanResults.certificates || scanResults.certificates.length === 0) {
                console.log('No certificates found - returning fallback');
                return `
                <div class="section">
                    <h2>Certificate Details</h2>
                    <p>No certificates found in this scan.</p>
                </div>`;
            }
            
            console.log('Processing', scanResults.certificates.length, 'certificates');
            
            scanResults.certificates.forEach((certData, index) => {
                console.log(`Certificate ${index}:`, certData);
                
                // Skip if certificate has an error
                if (certData.error) {
                    html += `
                    <div class="section">
                        <h2>Certificate ${index + 1} - Port ${certData.port}</h2>
                        <div class="error-box" style="background: #fee; border-left: 4px solid #c00; padding: 15px; margin: 10px 0;">
                            <p style="color: #c00;"><strong>Error:</strong> ${certData.error}</p>
                        </div>
                    </div>
                    `;
                    return;
                }
                
                const analysis = certData.analysis || {};
                const isQuantumSafe = analysis.is_quantum_safe || false;
                const publicKeyPQC = analysis.public_key_is_pqc || false;
                const signaturePQC = analysis.signature_is_pqc || false;
                
                html += `
                <div class="section">
                    <h2>Certificate ${index + 1} - Port ${certData.port} (Position #${certData.position})</h2>
                    
                    <!-- Certificate Information -->
                    <h3>Certificate Information</h3>
                    <div class="info-grid">
                        <div class="info-row">
                            <span class="info-label">Subject:</span>
                            <span class="info-value">${certData.subject || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Issuer:</span>
                            <span class="info-value">${certData.issuer || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Valid From:</span>
                            <span class="info-value">${formatDatePDF(analysis.valid_from)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Valid Until:</span>
                            <span class="info-value">${formatDatePDF(analysis.valid_until)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Serial Number:</span>
                            <span class="info-value">${certData.serial_number || 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Version:</span>
                            <span class="info-value">${certData.version || 'N/A'}</span>
                        </div>
                    </div>

                    <!-- Cryptographic Details -->
                    <h3>Cryptographic Analysis</h3>
                    <div class="info-grid">
                        <div class="info-row">
                            <span class="info-label">Public Key Algorithm:</span>
                            <span class="info-value">${analysis.public_key_algorithm || 'Unknown'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Key Size:</span>
                            <span class="info-value">${analysis.key_size ? analysis.key_size + ' bits' : 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Public Key Quantum Safety:</span>
                            <span class="info-value">
                                <span class="badge ${publicKeyPQC ? 'safe' : 'vulnerable'}">
                                    ${publicKeyPQC ? '✓ Quantum Safe' : '⚠ Quantum Vulnerable'}
                                </span>
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Signature Algorithm:</span>
                            <span class="info-value">${analysis.signature_algorithm || 'Unknown'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Signature Quantum Safety:</span>
                            <span class="info-value">
                                <span class="badge ${signaturePQC ? 'safe' : 'vulnerable'}">
                                    ${signaturePQC ? '✓ Quantum Safe' : '⚠ Quantum Vulnerable'}
                                </span>
                            </span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Overall Status:</span>
                            <span class="info-value">
                                <span class="badge ${isQuantumSafe ? 'safe' : 'vulnerable'}">
                                    ${isQuantumSafe ? '✓ Fully Quantum Safe' : '⚠ Quantum Vulnerable'}
                                </span>
                            </span>
                        </div>
                    </div>

                    <!-- Recommendations -->
                    ${!isQuantumSafe ? `
                    <h3>Migration Recommendations</h3>
                    <div class="recommendation">
                        <p><strong>This certificate uses classical cryptography that is vulnerable to quantum attacks.</strong></p>
                        <p>Recommended Actions:</p>
                        <ul style="margin-left: 20px; line-height: 1.8;">
                            ${!publicKeyPQC ? `
                            <li><strong>Public Key:</strong> Migrate to ML-KEM (CRYSTALS-Kyber) for quantum-safe key encapsulation</li>
                            ` : ''}
                            ${!signaturePQC ? `
                            <li><strong>Signature:</strong> Migrate to ML-DSA (CRYSTALS-Dilithium) or FALCON for quantum-safe signatures</li>
                            ` : ''}
                            <li><strong>Timeline:</strong> Begin migration within 12-24 months</li>
                            <li><strong>Standards:</strong> Follow NIST FIPS 203, 204, and 205</li>
                        </ul>
                    </div>
                    ` : `
                    <h3>Security Assessment</h3>
                    <div class="recommendation" style="background: #d1fae5;">
                        <p style="color: #065f46;"><strong>✓ This certificate is quantum-safe!</strong></p>
                        <p style="color: #065f46;">Both the public key and signature algorithms are resistant to quantum attacks.</p>
                    </div>
                    `}
                </div>
                `;
            });
            
            return html;
        };

        // Generate HTML content for the report
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Domain TLS Scan Report - QuantumCertify</title>
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
                        grid-template-columns: 220px 1fr;
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
                    .recommendation {
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        margin-top: 15px;
                        border: 1px solid #e5e7eb;
                        page-break-inside: avoid;
                    }
                    .recommendation p {
                        color: #555;
                        line-height: 1.7;
                        margin-bottom: 10px;
                    }
                    .recommendation ul {
                        margin-top: 10px;
                    }
                    .recommendation li {
                        margin-bottom: 8px;
                        color: #555;
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
                    <h1>Domain TLS Scan Report</h1>
                    <p class="subtitle">Comprehensive TLS Certificate Analysis</p>
                    <p class="generated">Generated: ${formatDatePDF(new Date().toISOString())}</p>
                </div>

                <!-- Scan Summary -->
                <div class="section">
                    <h2>Scan Summary</h2>
                    <div class="info-grid">
                        <div class="info-row">
                            <span class="info-label">Target Host:</span>
                            <span class="info-value">${safeGet(scanResults, 'scan_info.host')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Scanned Ports:</span>
                            <span class="info-value">${scanResults.scan_info && scanResults.scan_info.scanned_ports ? scanResults.scan_info.scanned_ports.join(', ') : 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Successful Ports:</span>
                            <span class="info-value">${scanResults.successful_ports ? scanResults.successful_ports.length : 0}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Failed Ports:</span>
                            <span class="info-value">${scanResults.failed_ports ? scanResults.failed_ports.length : 0}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Total Certificates Found:</span>
                            <span class="info-value">${scanResults.successful_ports ? scanResults.successful_ports.reduce((sum, p) => sum + (p.cert_count || 0), 0) : 0}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Scan Duration:</span>
                            <span class="info-value">${safeGet(scanResults, 'scan_info.scan_duration_ms')} ms</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Scan Timestamp:</span>
                            <span class="info-value">${formatDatePDF(safeGet(scanResults, 'scan_info.timestamp'))}</span>
                        </div>
                    </div>
                </div>

                <!-- Certificate Details -->
                ${generateCertificateDetails()}

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
                    printWindow.document.title = `QuantumCertify_DomainScan_${scanResults.scan_info.host}_${new Date().toISOString().split('T')[0]}`;
                    printWindow.print();
                    // Note: User can choose "Save as PDF" from print dialog
                }, 500);
            };
        } else {
            alert('Please allow popups to download the PDF report.');
        }
    };

    return (
        <div className="domain-scanner-container">
            <div className="scanner-header">
                <h1>Domain TLS Scanner</h1>
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
                                Start Scan
                            </>
                        )}
                    </button>
                    
                    {scanning && (
                        <div className="info-message">
                            <span className="spinner-icon"></span>
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
                    {/* Results Header with Download Button */}
                    <div className="results-header">
                        <h2>Scan Results</h2>
                        <button className="btn-download" onClick={downloadPDF}>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="7 10 12 15 17 10"></polyline>
                                <line x1="12" y1="15" x2="12" y2="3"></line>
                            </svg>
                            Download PDF Report
                        </button>
                    </div>

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
