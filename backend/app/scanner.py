"""
TLS Certificate Scanner Module
Scans live domains/IPs for TLS certificates across multiple ports
Integrated with QuantumCertify certificate analysis
"""
import socket
import ssl
import subprocess
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Common TLS ports
IMPLICIT_TLS_PORTS = {443, 8443, 993, 995, 465, 5061}
STARTTLS_PORTS = {25, 587, 143, 110, 21, 5222}
ALL_COMMON_PORTS = sorted(list(IMPLICIT_TLS_PORTS) + list(STARTTLS_PORTS))


def parse_cert_from_der(der_bytes: bytes) -> x509.Certificate:
    """Parse certificate from DER bytes"""
    return x509.load_der_x509_certificate(der_bytes, backend=default_backend())


def parse_cert_from_pem(pem: str) -> x509.Certificate:
    """Parse certificate from PEM string"""
    return x509.load_pem_x509_certificate(pem.encode(), backend=default_backend())


def extract_pems_from_openssl_output(openssl_out: str) -> List[str]:
    """Extract all PEM certificates from openssl s_client output"""
    pems = []
    if not openssl_out:
        return pems
    blocks = re.findall(
        r"(-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----)", 
        openssl_out, 
        re.DOTALL
    )
    return blocks


def run_openssl_showcerts(host: str, port: int, servername: Optional[str], 
                          timeout: int = 8) -> Tuple[Optional[str], Optional[str]]:
    """
    Run openssl s_client -showcerts to retrieve certificate chain
    Returns (stdout, stderr) or (None, error_message) on failure
    """
    try:
        import shutil
        if not shutil.which('openssl'):
            return None, 'openssl not found in PATH'
    except:
        return None, 'openssl not available'

    cmd = ["openssl", "s_client", "-connect", f"{host}:{port}", "-showcerts"]
    if servername:
        cmd.extend(["-servername", servername])
    
    try:
        proc = subprocess.run(
            cmd, 
            input="Q\n", 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return None, f"Connection timeout after {timeout}s"
    except FileNotFoundError:
        return None, "openssl not found in PATH"
    except Exception as e:
        return None, str(e)


def fetch_cert_from_port(host: str, port: int, timeout: int = 8) -> Dict[str, Any]:
    """
    Fetch certificate(s) from a specific host:port
    Returns dict with success status, certificates in DER format, and error info
    """
    result = {
        'host': host,
        'port': port,
        'success': False,
        'certificates': [],
        'error': None,
        'scanned_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        # Try Python SSL first
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                # Get peer certificate in DER format
                der = ssock.getpeercert(binary_form=True)
                if der:
                    result['certificates'].append(der)
                    result['success'] = True
                    
                    # Try to get full chain via openssl
                    try:
                        openssl_out, _ = run_openssl_showcerts(host, port, host, timeout)
                        if openssl_out:
                            pems = extract_pems_from_openssl_output(openssl_out)
                            # Convert PEMs to DER and add to certificates (skip first if duplicate)
                            for i, pem in enumerate(pems):
                                try:
                                    cert = parse_cert_from_pem(pem)
                                    cert_der = cert.public_bytes(encoding=serialization.Encoding.DER)
                                    # Add if not already in list (avoid duplicate leaf cert)
                                    if i > 0 or cert_der != der:
                                        result['certificates'].append(cert_der)
                                except Exception:
                                    pass
                    except Exception as e:
                        logging.warning(f"OpenSSL chain extraction failed: {e}")
                else:
                    result['error'] = "No certificate returned by server"
                    
    except socket.timeout:
        result['error'] = f"Connection timeout after {timeout}s"
    except socket.gaierror as e:
        result['error'] = f"DNS resolution failed: {e}"
    except ConnectionRefusedError:
        result['error'] = "Connection refused"
    except ssl.SSLError as e:
        result['error'] = f"SSL/TLS error: {e}"
    except Exception as e:
        result['error'] = str(e)
    
    return result


def scan_domain(host: str, ports: Optional[List[int]] = None, 
                timeout: int = 8) -> Dict[str, Any]:
    """
    Scan a domain/IP for TLS certificates on specified ports
    
    Args:
        host: Domain name or IP address
        ports: List of ports to scan (None = scan all common ports)
        timeout: Connection timeout in seconds
    
    Returns:
        Dict with scan results including successful/failed ports and certificates
    """
    scan_result = {
        'host': host,
        'scan_started': datetime.utcnow().isoformat() + 'Z',
        'ports_scanned': [],
        'successful_ports': [],
        'failed_ports': [],
        'certificates': [],
        'total_certs_found': 0
    }
    
    # Determine ports to scan
    if ports is None or len(ports) == 0:
        ports_to_scan = ALL_COMMON_PORTS
    else:
        ports_to_scan = ports
    
    scan_result['ports_scanned'] = ports_to_scan
    
    # Scan each port
    for port in ports_to_scan:
        logging.info(f"Scanning {host}:{port}")
        port_result = fetch_cert_from_port(host, port, timeout)
        
        if port_result['success']:
            scan_result['successful_ports'].append({
                'port': port,
                'num_certificates': len(port_result['certificates'])
            })
            
            # Add certificates with metadata
            for i, cert_der in enumerate(port_result['certificates']):
                scan_result['certificates'].append({
                    'port': port,
                    'chain_position': i,
                    'der_bytes': cert_der,
                    'scanned_at': port_result['scanned_at']
                })
        else:
            scan_result['failed_ports'].append({
                'port': port,
                'error': port_result['error']
            })
    
    scan_result['total_certs_found'] = len(scan_result['certificates'])
    scan_result['scan_completed'] = datetime.utcnow().isoformat() + 'Z'
    
    return scan_result
