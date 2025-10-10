#!/usr/bin/env python3
"""
tls_scanner.py
Comprehensive TLS certificate scanner (implicit TLS + STARTTLS) with many edge cases handled.

Features:
- Resolve CNAMEs and A/AAAA records (optionally follow CNAME chain)
- Optionally scan all resolved IPs or only first IP
- Implicit TLS support (443, 8443, 993, 995, 465...)
- STARTTLS support via openssl s_client for protocols: smtp, imap, pop3, ftp, xmpp (configurable)
- Captures leaf cert and certificate chain (via openssl -showcerts fallback)
- Parses certificate using cryptography to extract:
  - subject, issuer, SANs, validity, serial
  - public key algorithm and size (RSA/ECDSA/DSA/Ed25519 etc.)
  - signature algorithm OID & hash algorithm (when available)
  - SHA256 fingerprint
- Returns structured JSON per scanned item and writes to output file if requested

Requirements:
  pip install dnspython cryptography
  openssl CLI in PATH (used for STARTTLS and chain extraction)

Usage examples:
  python tls_scanner.py --host example.com --ports 443 8443 --follow-cname --resolve-all-ips --starttls smtp imap --concurrency 20 --timeout 8 --out results.json
  python tls_scanner.py --input hosts.txt --ports 443 993 995 --out results.json
"""

import argparse
import socket
import ssl
import subprocess
import json
import sys
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import shutil

# Try imports and give friendly error messages
try:
    import dns.resolver
except Exception:
    print("Missing dependency 'dnspython'. Install with: pip install dnspython", file=sys.stderr)
    raise

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec
    from cryptography.hazmat.backends import default_backend
except Exception:
    print("Missing dependency 'cryptography'. Install with: pip install cryptography", file=sys.stderr)
    raise

# Known STARTTLS-capable protocols mapping; openssl supports these names.
STARTTLS_PORT_PROTO = {
    25: 'smtp',
    587: 'smtp',
    143: 'imap',
    110: 'pop3',
    21: 'ftp',
    5222: 'xmpp',  # XMPP client
}

# Ports commonly treated as implicit TLS
IMPLICIT_TLS_PORTS = {443, 8443, 993, 995, 465, 5061}  # extend as needed


def follow_cname_chain(name: str, max_depth: int = 10) -> Tuple[str, List[str]]:
    resolver = dns.resolver.Resolver()
    chain = []
    current = name
    for _ in range(max_depth):
        try:
            ans = resolver.resolve(current, 'CNAME', raise_on_no_answer=False)
            if not ans or len(ans) == 0:
                break
            target = str(ans[0].target).rstrip('.')
            chain.append(target)
            current = target
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.DNSException):
            break
    return current, chain


def resolve_ips(name: str) -> List[str]:
    resolver = dns.resolver.Resolver()
    ips = []
    try:
        for r in resolver.resolve(name, 'A', raise_on_no_answer=False):
            ips.append(str(r))
    except Exception:
        pass
    try:
        for r in resolver.resolve(name, 'AAAA', raise_on_no_answer=False):
            ips.append(str(r))
    except Exception:
        pass
    return ips


def run_openssl_showcerts(host_for_connect: str, port: int, servername: Optional[str],
                          starttls_proto: Optional[str], timeout: int = 8) -> Tuple[Optional[str], Optional[str]]:
    """
    Run openssl s_client -showcerts to retrieve chain PEM output.
    Returns (stdout, stderr) or (None, error_message) on failure.
    """
    # Quick check: if openssl not available, avoid attempting subprocess call
    if not shutil.which('openssl'):
        return None, 'openssl not found in PATH'

    cmd = ["openssl", "s_client", "-connect", f"{host_for_connect}:{port}", "-showcerts"]
    if servername:
        cmd.extend(["-servername", servername])
    if starttls_proto:
        cmd.extend(["-starttls", starttls_proto])
    try:
        # Send "Q\n" to stdin to gracefully close connection after handshake
        proc = subprocess.run(cmd, input="Q\n", capture_output=True, text=True, timeout=timeout)
        return proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as e:
        return None, f"openssl timeout: {e}"
    except FileNotFoundError:
        return None, "openssl not found in PATH"
    except Exception as e:
        return None, str(e)


def extract_pems_from_openssl_output(openssl_out: str) -> List[str]:
    pems = []
    if not openssl_out:
        return pems
    blocks = re.findall(r"(-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----)", openssl_out, re.DOTALL)
    for b in blocks:
        pems.append(b)
    return pems


def parse_cert_from_der(der_bytes: bytes) -> x509.Certificate:
    return x509.load_der_x509_certificate(der_bytes, backend=default_backend())


def parse_cert_from_pem(pem: str) -> x509.Certificate:
    return x509.load_pem_x509_certificate(pem.encode(), backend=default_backend())


def cert_to_metadata(cert: x509.Certificate) -> Dict[str, Any]:
    d: Dict[str, Any] = {}
    try:
        d['subject'] = cert.subject.rfc4514_string()
        d['issuer'] = cert.issuer.rfc4514_string()
        d['not_before'] = cert.not_valid_before.isoformat()
        d['not_after'] = cert.not_valid_after.isoformat()
        d['serial_number'] = format(cert.serial_number, 'x')
    except Exception as e:
        d['parse_error_basic'] = str(e)

    # SANs
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        dns_names = ext.value.get_values_for_type(x509.DNSName)
        ip_names = ext.value.get_values_for_type(x509.IPAddress)
        d['san'] = dns_names + [str(i) for i in ip_names]
    except Exception:
        d['san'] = []

    # public key algorithm + details
    pub = cert.public_key()
    try:
        if isinstance(pub, rsa.RSAPublicKey):
            d['public_key_algorithm'] = 'RSA'
            d['public_key_bits'] = pub.key_size
        elif isinstance(pub, ec.EllipticCurvePublicKey):
            d['public_key_algorithm'] = 'ECDSA'
            try:
                d['public_key_curve'] = pub.curve.name
            except Exception:
                d['public_key_curve'] = str(pub.curve)
        elif isinstance(pub, dsa.DSAPublicKey):
            d['public_key_algorithm'] = 'DSA'
            d['public_key_bits'] = pub.key_size
        else:
            # Ed25519, Ed448, unknown: class name as best-effort label
            d['public_key_algorithm'] = pub.__class__.__name__
    except Exception as e:
        d['public_key_parse_error'] = str(e)

    # signature algorithm OID and hash
    try:
        d['signature_algorithm_oid'] = cert.signature_algorithm_oid.dotted_string
    except Exception:
        d['signature_algorithm_oid'] = None
    try:
        sha = cert.signature_hash_algorithm
        d['signature_hash_algorithm'] = sha.name if sha else None
    except Exception:
        d['signature_hash_algorithm'] = None

    # fingerprint SHA256
    try:
        fp = cert.fingerprint(hashes.SHA256())
        d['sha256_fingerprint'] = fp.hex()
    except Exception:
        d['sha256_fingerprint'] = None

    return d


def fetch_cert_implicit(ip: str, port: int, servername: Optional[str], timeout: int = 8) -> Dict[str, Any]:
    """
    Try Python ssl first for leaf DER, then use openssl for full chain if available.
    Connects to IP:port, uses SNI=servername when wrapping TLS.
    """
    out: Dict[str, Any] = {'ip': ip, 'port': port, 'mode': 'implicit', 'servername': servername}
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=servername) as ssock:
                der = ssock.getpeercert(binary_form=True)
                if der:
                    try:
                        cert = parse_cert_from_der(der)
                        out['leaf'] = cert_to_metadata(cert)
                    except Exception:
                        out.setdefault('warnings', []).append('failed_parse_leaf_from_der')
                # Try to get chain via openssl to capture intermediates
                openssl_out, openssl_err = run_openssl_showcerts(ip, port, servername, None, timeout=timeout)
                if openssl_out:
                    pems = extract_pems_from_openssl_output(openssl_out)
                    chain = []
                    for pem in pems:
                        try:
                            c = parse_cert_from_pem(pem)
                            chain.append(cert_to_metadata(c))
                        except Exception:
                            chain.append({'parse_error': 'parse_failed_for_pem'})
                    if chain:
                        out['chain'] = chain
        out['error'] = None
    except Exception as e:
        # fallback: try openssl only (some servers require different ClientHello)
        openssl_out, openssl_err = run_openssl_showcerts(ip, port, servername, None, timeout=timeout)
        if openssl_out:
            pems = extract_pems_from_openssl_output(openssl_out)
            chain = []
            for pem in pems:
                try:
                    c = parse_cert_from_pem(pem)
                    chain.append(cert_to_metadata(c))
                except Exception:
                    chain.append({'parse_error': 'parse_failed_for_pem'})
            if chain:
                out['chain'] = chain
                out['leaf'] = chain[0] if chain else None
                out['error'] = None
            else:
                out['error'] = f"openssl returned no certs; err: {openssl_err!s}"
        else:
            out['error'] = str(e)
    return out


def fetch_cert_starttls(target_host: str, port: int, starttls_proto: str, servername: Optional[str], timeout: int = 8) -> Dict[str, Any]:
    """
    Use openssl -starttls <proto> to perform STARTTLS and extract cert chain.
    target_host is used for TCP connect; servername used for -servername (SNI).
    """
    out: Dict[str, Any] = {'host': target_host, 'port': port, 'mode': 'starttls', 'protocol': starttls_proto, 'servername': servername}
    openssl_out, openssl_err = run_openssl_showcerts(target_host, port, servername, starttls_proto, timeout=timeout)
    if not openssl_out:
        out['error'] = openssl_err or 'no_output_from_openssl'
        return out
    pems = extract_pems_from_openssl_output(openssl_out)
    if not pems:
        out['error'] = 'no_pem_found_in_openssl_output'
        out['raw_openssl'] = openssl_out[:2000]
        return out
    chain = []
    for pem in pems:
        try:
            c = parse_cert_from_pem(pem)
            chain.append(cert_to_metadata(c))
        except Exception as e:
            chain.append({'parse_error': str(e)})
    out['chain'] = chain
    out['leaf'] = chain[0] if chain else None
    out['error'] = None
    return out


def scan_target(host: str, ports: List[int], follow_cname: bool = True, resolve_all_ips: bool = True,
                starttls_protocols: List[str] = [], concurrency: int = 10, timeout: int = 8) -> Dict[str, Any]:
    """Main orchestration function. Returns dict with results list."""
    result = {'requested_host': host, 'scanned_at': datetime.utcnow().isoformat() + 'Z', 'results': []}
    canonical = host
    cname_chain = []
    if follow_cname:
        try:
            canonical, cname_chain = follow_cname_chain(host)
        except Exception:
            canonical = host
    result['canonical_name'] = canonical
    result['cname_chain'] = cname_chain

    ips = resolve_ips(canonical)
    if not ips:
        # If no DNS records, and host looks like IP, scan that literal
        ips = [host]

    result['resolved_ips'] = ips

    tasks = []
    for ip in ips if resolve_all_ips else ips[:1]:
        for port in ports:
            # Determine mode: implicit TLS or STARTTLS if listed
            if port in IMPLICIT_TLS_PORTS:
                tasks.append(('implicit', ip, port, host))
            else:
                proto = STARTTLS_PORT_PROTO.get(port)
                if proto and proto in starttls_protocols:
                    tasks.append(('starttls', ip, port, proto, host))
                else:
                    # Try implicit first for unknown ports (safe approach) but record choice
                    tasks.append(('implicit', ip, port, host))

    # Concurrency using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        future_map = {}
        for t in tasks:
            if t[0] == 'implicit':
                _, ip, port, host_for_sni = t
                fut = ex.submit(fetch_cert_implicit, ip, port, host_for_sni, timeout)
                future_map[fut] = {'type': 'implicit', 'ip': ip, 'port': port, 'sni': host_for_sni}
            else:
                _, ip, port, proto, host_for_sni = t
                # For STARTTLS, we connect to ip (target) but use host_for_sni as -servername
                fut = ex.submit(fetch_cert_starttls, ip, port, proto, host_for_sni, timeout)
                future_map[fut] = {'type': 'starttls', 'ip': ip, 'port': port, 'proto': proto, 'sni': host_for_sni}

        for fut in as_completed(future_map):
            meta = future_map[fut]
            try:
                res = fut.result()
            except Exception as e:
                res = {'error': str(e)}
            entry = {
                'type': meta.get('type'),
                'ip': meta.get('ip'),
                'port': meta.get('port'),
                'sni': meta.get('sni'),
                'result': res
            }
            result['results'].append(entry)

    return result


def main():
    parser = argparse.ArgumentParser(description='TLS Scanner - implicit TLS + STARTTLS, chain extraction, cert metadata.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--host', help='Single host (domain name or IP) to scan')
    group.add_argument('--input', help='File with one host per line to scan')
    parser.add_argument('--ports', type=int, nargs='+', default=None, help='Ports to scan (space separated). If not specified, scans all common TLS ports: 443, 8443, 993, 995, 465, 5061, 25, 587, 143, 110, 21, 5222')
    parser.add_argument('--follow-cname', action='store_true', help='Follow CNAME chain to the final target')
    parser.add_argument('--resolve-all-ips', action='store_true', help='Resolve and scan all A/AAAA records (default: false)')
    parser.add_argument('--starttls', nargs='*', default=[], help='List of STARTTLS protocols to attempt (e.g., smtp imap pop3)')
    parser.add_argument('--concurrency', type=int, default=10, help='Max concurrent workers')
    parser.add_argument('--timeout', type=int, default=8, help='Network timeout seconds for each connection')
    parser.add_argument('--out', help='Write JSON output to file')
    args = parser.parse_args()
    
    # If no ports specified, scan all common TLS ports
    if args.ports is None:
        # Combine implicit TLS ports and STARTTLS ports
        all_common_ports = sorted(list(IMPLICIT_TLS_PORTS) + list(STARTTLS_PORT_PROTO.keys()))
        args.ports = all_common_ports
        # Auto-enable all STARTTLS protocols when scanning all ports
        if not args.starttls:
            args.starttls = ['smtp', 'imap', 'pop3', 'ftp', 'xmpp']

    hosts = []
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            for line in f:
                h = line.strip()
                # Strip BOM if present at start of file
                if h.startswith('\ufeff'):
                    h = h.lstrip('\ufeff')
                if h and not h.startswith('#'):
                    hosts.append(h)
    elif args.host:
        hosts = [args.host.strip()]

    all_results = []
    for h in hosts:
        r = scan_target(h, args.ports, follow_cname=args.follow_cname, resolve_all_ips=args.resolve_all_ips,
                        starttls_protocols=[p.lower() for p in args.starttls], concurrency=args.concurrency, timeout=args.timeout)
        all_results.append(r)
        # Pretty print one result at a time for progress
        print(json.dumps(r, indent=2))

    if args.out:
        try:
            with open(args.out, 'w', encoding='utf-8') as outf:
                json.dump(all_results, outf, indent=2)
        except Exception as e:
            print(f"Failed to write output file: {e}", file=sys.stderr)


if __name__ == '__main__':
    main()
