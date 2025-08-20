# Security Guidelines and Best Practices

## Overview

This context provides comprehensive security guidelines covering application security, infrastructure security, data protection, compliance, and incident response. These practices ensure robust security posture and protection against modern cyber threats.

## Security Fundamentals

### Security Principles

- **Defense in Depth**: Implement multiple layers of security controls
- **Least Privilege**: Grant minimum necessary access rights
- **Zero Trust**: Never trust, always verify
- **Fail Secure**: Systems should fail to a secure state
- **Security by Design**: Build security into systems from the start

### CIA Triad

#### Confidentiality

- **Data Classification**: Classify data based on sensitivity
- **Access Controls**: Implement appropriate access restrictions
- **Encryption**: Protect data at rest and in transit
- **Information Handling**: Establish proper data handling procedures

#### Integrity

- **Data Validation**: Validate all input data
- **Digital Signatures**: Use cryptographic signatures for verification
- **Version Control**: Maintain integrity of code and configurations
- **Audit Trails**: Log all changes and access attempts

#### Availability

- **Redundancy**: Implement system redundancy and failover
- **DDoS Protection**: Protect against denial of service attacks
- **Backup and Recovery**: Maintain reliable backup and recovery procedures
- **Performance Monitoring**: Monitor system performance and availability

## Application Security

### Secure Coding Practices

#### Input Validation

```python
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email format with proper sanitization."""
    if not email or len(email) > 254:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_input(user_input: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '*']
    sanitized = user_input
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    return sanitized.strip()[:1000]  # Limit length
```

#### SQL Injection Prevention

```python
import sqlite3
from typing import List, Tuple

# GOOD: Using parameterized queries
def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Use parameterized query to prevent SQL injection
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()
    return result

# BAD: String concatenation (vulnerable to SQL injection)
def vulnerable_query(username: str):
    # NEVER DO THIS
    query = f"SELECT * FROM users WHERE username = '{username}'"
    # This is vulnerable to SQL injection attacks
```

#### Cross-Site Scripting (XSS) Prevention

```javascript
// HTML encoding function to prevent XSS
function htmlEncode(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;")
    .replace(/\//g, "&#x2F;");
}

// Content Security Policy header
app.use((req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
  );
  next();
});
```

### OWASP Top 10 Mitigation

#### A01: Broken Access Control

- **Implement proper authorization checks**
- **Use role-based access control (RBAC)**
- **Validate permissions on server-side**
- **Implement principle of least privilege**

#### A02: Cryptographic Failures

- **Use strong encryption algorithms (AES-256, RSA-2048+)**
- **Implement proper key management**
- **Use HTTPS for all communications**
- **Hash passwords with salt using bcrypt or Argon2**

#### A03: Injection

- **Use parameterized queries**
- **Validate and sanitize all inputs**
- **Use ORM frameworks properly**
- **Implement input length limits**

#### A04: Insecure Design

- **Implement security by design**
- **Use threat modeling**
- **Conduct security architecture reviews**
- **Implement secure development lifecycle**

#### A05: Security Misconfiguration

- **Use security hardening guides**
- **Remove default accounts and passwords**
- **Keep systems updated**
- **Implement proper error handling**

### Authentication and Authorization

#### Multi-Factor Authentication (MFA)

```python
import pyotp
import qrcode
from datetime import datetime, timedelta

class MFAManager:
    def __init__(self):
        self.secret_key = pyotp.random_base32()

    def generate_qr_code(self, user_email: str, app_name: str) -> str:
        """Generate QR code for MFA setup."""
        totp_uri = pyotp.totp.TOTP(self.secret_key).provisioning_uri(
            name=user_email,
            issuer_name=app_name
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        return qr.get_matrix()

    def verify_token(self, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(token, valid_window=1)
```

#### JWT Security

```python
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional

class JWTManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = 'HS256'

    def create_token(self, user_id: str, roles: list) -> str:
        """Create secure JWT token."""
        payload = {
            'user_id': user_id,
            'roles': roles,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=1),
            'iss': 'your-app-name',
            'aud': 'your-app-users'
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'require': ['exp', 'iat', 'iss', 'aud']}
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

## Infrastructure Security

### Network Security

#### Firewall Configuration

```bash
#!/bin/bash
# Example iptables configuration for web server

# Flush existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback traffic
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established and related connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (change port as needed)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP and HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow ping (ICMP)
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: "

# Save rules
iptables-save > /etc/iptables/rules.v4
```

#### Network Segmentation

```yaml
# Kubernetes Network Policy Example
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-app-netpol
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web-app
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: database
      ports:
        - protocol: TCP
          port: 5432
    - to: []
      ports:
        - protocol: TCP
          port: 443 # HTTPS outbound
```

### Container Security

#### Dockerfile Security Best Practices

```dockerfile
# Use specific, minimal base image
FROM node:18-alpine

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 -G nodejs

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies as root, then switch user
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application code
COPY --chown=nextjs:nodejs . .

# Remove unnecessary packages and files
RUN apk del --no-cache \
    && rm -rf /var/cache/apk/* \
    && rm -rf /tmp/*

# Switch to non-root user
USER nextjs

# Expose port (non-privileged)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Use exec form for better signal handling
CMD ["node", "server.js"]
```

#### Container Scanning

```yaml
# Example container security scanning in CI/CD
container_security:
  stage: security
  image: aquasec/trivy:latest
  script:
    # Scan for vulnerabilities
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

    # Scan for misconfigurations
    - trivy config --exit-code 1 .

    # Generate report
    - trivy image --format json --output trivy-report.json $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

  artifacts:
    reports:
      container_scanning: trivy-report.json
    expire_in: 1 week
```

### Cloud Security

#### AWS Security Best Practices

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureConnections",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-secure-bucket",
        "arn:aws:s3:::my-secure-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    },
    {
      "Sid": "AllowSSLRequestsOnly",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/MyRole"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-secure-bucket/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "true"
        }
      }
    }
  ]
}
```

#### Infrastructure as Code Security

```hcl
# Terraform security configuration example
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket"
}

resource "aws_s3_bucket_encryption" "secure_bucket_encryption" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "secure_bucket_pab" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "secure_bucket_versioning" {
  bucket = aws_s3_bucket.secure_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

## Data Protection

### Data Classification

#### Classification Levels

1. **Public**: Information that can be freely shared
2. **Internal**: Information for internal use only
3. **Confidential**: Sensitive information requiring protection
4. **Restricted**: Highly sensitive information with strict access controls

#### Data Handling Matrix

| Classification | Storage                 | Transmission  | Access Control | Retention |
| -------------- | ----------------------- | ------------- | -------------- | --------- |
| Public         | Standard                | HTTP/HTTPS    | None           | As needed |
| Internal       | Encrypted               | HTTPS/VPN     | Authentication | 3 years   |
| Confidential   | Encrypted + Access logs | TLS 1.3 + VPN | MFA + RBAC     | 7 years   |
| Restricted     | HSM/Encrypted + Audit   | mTLS + VPN    | MFA + Approval | 10 years  |

### Encryption Implementation

#### Data at Rest

```python
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self):
        # Generate or load encryption key
        self.key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.key)

    def _get_or_create_key(self) -> bytes:
        """Get encryption key from environment or generate new one."""
        key_env = os.getenv('ENCRYPTION_KEY')
        if key_env:
            return base64.urlsafe_b64decode(key_env)
        else:
            # Generate new key (store securely in production)
            return Fernet.generate_key()

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_data.decode()
```

#### Data in Transit

```python
import ssl
import requests
from urllib3.util.ssl_ import create_urllib3_context

def create_secure_session():
    """Create requests session with strong TLS configuration."""
    session = requests.Session()

    # Create secure SSL context
    context = create_urllib3_context()
    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_3

    # Configure session
    session.verify = True  # Always verify certificates
    session.headers.update({
        'User-Agent': 'SecureApp/1.0',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
    })

    return session
```

### Privacy and Compliance

#### GDPR Compliance

```python
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GDPRCompliance:
    def __init__(self):
        self.data_retention_periods = {
            'user_profiles': timedelta(days=2555),  # 7 years
            'transaction_logs': timedelta(days=2190),  # 6 years
            'marketing_data': timedelta(days=1095),  # 3 years
            'session_data': timedelta(days=30)  # 30 days
        }

    def handle_data_subject_request(self, user_id: str, request_type: str) -> Dict:
        """Handle GDPR data subject requests."""
        if request_type == 'access':
            return self._export_user_data(user_id)
        elif request_type == 'deletion':
            return self._delete_user_data(user_id)
        elif request_type == 'portability':
            return self._export_portable_data(user_id)
        elif request_type == 'rectification':
            return self._update_user_data(user_id)
        else:
            raise ValueError(f"Unknown request type: {request_type}")

    def _export_user_data(self, user_id: str) -> Dict:
        """Export all user data for access request."""
        # Implementation would gather all user data
        return {
            'user_id': user_id,
            'personal_data': {},
            'processing_activities': [],
            'data_sources': [],
            'export_date': datetime.utcnow().isoformat()
        }

    def check_retention_compliance(self) -> List[Dict]:
        """Check data retention compliance."""
        violations = []
        # Implementation would check all data stores
        return violations
```

## Incident Response

### Incident Classification

#### Severity Levels

1. **Critical (P1)**: System compromise, data breach, complete service outage
2. **High (P2)**: Partial system compromise, significant security vulnerability
3. **Medium (P3)**: Minor security issue, limited impact
4. **Low (P4)**: Security policy violation, informational

#### Response Timeline

| Severity | Initial Response | Investigation | Resolution | Post-Mortem |
| -------- | ---------------- | ------------- | ---------- | ----------- |
| P1       | 15 minutes       | 1 hour        | 4 hours    | 24 hours    |
| P2       | 1 hour           | 4 hours       | 24 hours   | 72 hours    |
| P3       | 4 hours          | 24 hours      | 72 hours   | 1 week      |
| P4       | 24 hours         | 1 week        | 2 weeks    | 1 month     |

### Incident Response Playbook

#### Security Incident Response Process

```python
from enum import Enum
from datetime import datetime
from typing import List, Dict

class IncidentSeverity(Enum):
    CRITICAL = "P1"
    HIGH = "P2"
    MEDIUM = "P3"
    LOW = "P4"

class IncidentResponse:
    def __init__(self):
        self.incident_log = []
        self.response_team = {
            'incident_commander': 'security-lead@company.com',
            'security_analyst': 'analyst@company.com',
            'communications': 'comms@company.com',
            'legal': 'legal@company.com'
        }

    def initiate_response(self, incident_type: str, severity: IncidentSeverity, description: str):
        """Initiate incident response process."""
        incident = {
            'id': self._generate_incident_id(),
            'type': incident_type,
            'severity': severity.value,
            'description': description,
            'start_time': datetime.utcnow(),
            'status': 'active',
            'actions': []
        }

        # Immediate actions based on severity
        if severity == IncidentSeverity.CRITICAL:
            self._execute_critical_response(incident)
        elif severity == IncidentSeverity.HIGH:
            self._execute_high_response(incident)

        self.incident_log.append(incident)
        return incident['id']

    def _execute_critical_response(self, incident: Dict):
        """Execute critical incident response procedures."""
        actions = [
            'Alert incident commander immediately',
            'Activate emergency response team',
            'Isolate affected systems',
            'Preserve evidence',
            'Notify executive leadership',
            'Prepare external communications'
        ]

        for action in actions:
            incident['actions'].append({
                'action': action,
                'timestamp': datetime.utcnow(),
                'status': 'pending'
            })
```

### Forensics and Evidence Collection

#### Digital Forensics Checklist

```bash
#!/bin/bash
# Digital forensics evidence collection script

INCIDENT_ID=$1
EVIDENCE_DIR="/forensics/evidence/${INCIDENT_ID}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create evidence directory
mkdir -p "${EVIDENCE_DIR}"

# System information
echo "Collecting system information..."
uname -a > "${EVIDENCE_DIR}/system_info_${TIMESTAMP}.txt"
ps aux > "${EVIDENCE_DIR}/processes_${TIMESTAMP}.txt"
netstat -tulpn > "${EVIDENCE_DIR}/network_connections_${TIMESTAMP}.txt"
lsof > "${EVIDENCE_DIR}/open_files_${TIMESTAMP}.txt"

# Memory dump (if tools available)
if command -v memdump &> /dev/null; then
    echo "Creating memory dump..."
    memdump > "${EVIDENCE_DIR}/memory_dump_${TIMESTAMP}.raw"
fi

# Log files
echo "Collecting log files..."
cp -r /var/log "${EVIDENCE_DIR}/logs_${TIMESTAMP}/"

# Network traffic capture
if command -v tcpdump &> /dev/null; then
    echo "Starting network capture..."
    tcpdump -i any -w "${EVIDENCE_DIR}/network_capture_${TIMESTAMP}.pcap" &
    TCPDUMP_PID=$!
    sleep 300  # Capture for 5 minutes
    kill $TCPDUMP_PID
fi

# Calculate checksums for integrity
find "${EVIDENCE_DIR}" -type f -exec sha256sum {} \; > "${EVIDENCE_DIR}/checksums_${TIMESTAMP}.txt"

echo "Evidence collection completed for incident ${INCIDENT_ID}"
```

## Security Testing

### Vulnerability Assessment

#### Automated Scanning

```python
import subprocess
import json
from typing import Dict, List

class VulnerabilityScanner:
    def __init__(self):
        self.scan_results = {}

    def run_nmap_scan(self, target: str) -> Dict:
        """Run Nmap vulnerability scan."""
        cmd = [
            'nmap',
            '-sV',  # Version detection
            '--script=vuln',  # Vulnerability scripts
            '-oX', '-',  # XML output to stdout
            target
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            # Parse XML output (simplified)
            return {'status': 'completed', 'output': result.stdout}
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'error': 'Scan timed out'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def run_web_scan(self, url: str) -> Dict:
        """Run web application vulnerability scan."""
        # Example using OWASP ZAP API
        zap_cmd = [
            'zap-baseline.py',
            '-t', url,
            '-J', 'zap-report.json'
        ]

        try:
            result = subprocess.run(zap_cmd, capture_output=True, text=True, timeout=600)
            return {'status': 'completed', 'output': result.stdout}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
```

### Penetration Testing

#### Testing Methodology

1. **Reconnaissance**: Information gathering and target identification
2. **Scanning**: Port scanning and service enumeration
3. **Enumeration**: Detailed service and application analysis
4. **Vulnerability Assessment**: Identify potential security weaknesses
5. **Exploitation**: Attempt to exploit identified vulnerabilities
6. **Post-Exploitation**: Assess impact and potential for lateral movement
7. **Reporting**: Document findings and provide remediation recommendations

#### Testing Checklist

```markdown
# Penetration Testing Checklist

## Pre-Engagement

- [ ] Scope definition and rules of engagement
- [ ] Legal authorization and contracts
- [ ] Emergency contact information
- [ ] Testing timeline and windows

## Information Gathering

- [ ] OSINT collection
- [ ] DNS enumeration
- [ ] Subdomain discovery
- [ ] Social media reconnaissance
- [ ] Employee information gathering

## Network Testing

- [ ] Port scanning
- [ ] Service enumeration
- [ ] Network mapping
- [ ] Firewall testing
- [ ] Wireless network assessment

## Web Application Testing

- [ ] Input validation testing
- [ ] Authentication bypass attempts
- [ ] Session management testing
- [ ] Authorization testing
- [ ] SQL injection testing
- [ ] XSS testing
- [ ] CSRF testing

## Post-Exploitation

- [ ] Privilege escalation attempts
- [ ] Lateral movement testing
- [ ] Data exfiltration simulation
- [ ] Persistence mechanisms
- [ ] Clean-up and evidence removal

## Reporting

- [ ] Executive summary
- [ ] Technical findings
- [ ] Risk assessment
- [ ] Remediation recommendations
- [ ] Proof of concept documentation
```

## Security Metrics and KPIs

### Key Security Metrics

#### Vulnerability Management

- **Mean Time to Detection (MTTD)**: Average time to detect vulnerabilities
- **Mean Time to Remediation (MTTR)**: Average time to fix vulnerabilities
- **Vulnerability Density**: Number of vulnerabilities per application/system
- **Patch Compliance**: Percentage of systems with current patches

#### Incident Response

- **Incident Response Time**: Time from detection to initial response
- **Incident Resolution Time**: Time from detection to full resolution
- **False Positive Rate**: Percentage of false security alerts
- **Security Awareness**: Training completion and phishing test results

#### Compliance and Governance

- **Compliance Score**: Percentage of compliance requirements met
- **Policy Compliance**: Adherence to security policies and procedures
- **Risk Assessment Coverage**: Percentage of assets with current risk assessments
- **Audit Findings**: Number and severity of audit findings

### Security Dashboard

```python
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

class SecurityDashboard:
    def __init__(self):
        self.metrics_data = {}

    def generate_vulnerability_trend(self, data: pd.DataFrame):
        """Generate vulnerability trend chart."""
        plt.figure(figsize=(12, 6))

        # Group by severity and date
        severity_trends = data.groupby(['date', 'severity']).size().unstack(fill_value=0)

        # Plot trends
        severity_trends.plot(kind='line', stacked=False)
        plt.title('Vulnerability Trends by Severity')
        plt.xlabel('Date')
        plt.ylabel('Number of Vulnerabilities')
        plt.legend(title='Severity')
        plt.grid(True, alpha=0.3)

        return plt

    def calculate_security_score(self, metrics: Dict) -> float:
        """Calculate overall security score."""
        weights = {
            'vulnerability_score': 0.3,
            'incident_response_score': 0.2,
            'compliance_score': 0.2,
            'training_score': 0.15,
            'patch_score': 0.15
        }

        total_score = sum(metrics.get(metric, 0) * weight
                         for metric, weight in weights.items())

        return min(100, max(0, total_score))
```

This comprehensive security context should be used as a reference for implementing robust security practices, ensuring compliance with security frameworks, and maintaining a strong security posture throughout the software development and deployment lifecycle.
