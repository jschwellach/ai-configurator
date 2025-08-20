# DevOps Methodologies and Best Practices

## Overview

This context provides comprehensive guidelines for DevOps practices, covering infrastructure as code, CI/CD pipelines, monitoring, security, and operational excellence. These methodologies ensure reliable, scalable, and secure software delivery and infrastructure management.

## Infrastructure as Code (IaC)

### Core Principles

- **Version Control Everything**: All infrastructure definitions should be stored in version control
- **Immutable Infrastructure**: Treat infrastructure as immutable; replace rather than modify
- **Declarative Configuration**: Use declarative rather than imperative approaches
- **Idempotency**: Ensure operations can be run multiple times safely
- **Documentation as Code**: Keep infrastructure documentation alongside code

### Terraform Best Practices

```hcl
# Use consistent naming conventions
resource "aws_instance" "web_server" {
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = {
    Name        = "${var.project_name}-web-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

# Use variables for reusability
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

### Directory Structure

```
infrastructure/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   ├── compute/
│   └── database/
├── shared/
│   ├── variables.tf
│   └── outputs.tf
└── scripts/
    ├── deploy.sh
    └── destroy.sh
```

### State Management

- **Remote State**: Always use remote state backends (S3, GCS, Azure Storage)
- **State Locking**: Implement state locking to prevent concurrent modifications
- **State Encryption**: Encrypt state files at rest and in transit
- **Backup Strategy**: Implement regular state backups and recovery procedures
- **Access Control**: Restrict access to state files based on principle of least privilege

## Continuous Integration/Continuous Deployment (CI/CD)

### Pipeline Design Principles

- **Fast Feedback**: Optimize for quick feedback loops
- **Fail Fast**: Detect and report failures as early as possible
- **Parallel Execution**: Run independent tasks in parallel
- **Artifact Management**: Properly version and store build artifacts
- **Environment Parity**: Maintain consistency across environments

### GitHub Actions Example

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "18"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Run security scan
        run: npm audit

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t ${{ github.repository }}:${{ github.sha }} .
          docker tag ${{ github.repository }}:${{ github.sha }} ${{ github.repository }}:latest

      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push ${{ github.repository }}:${{ github.sha }}
          docker push ${{ github.repository }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Deployment logic here
          kubectl set image deployment/app app=${{ github.repository }}:${{ github.sha }}
```

### Deployment Strategies

#### Blue-Green Deployment

- **Zero Downtime**: Switch traffic between two identical environments
- **Quick Rollback**: Instant rollback by switching traffic back
- **Resource Intensive**: Requires double the resources during deployment
- **Testing**: Full production testing before traffic switch

#### Canary Deployment

- **Gradual Rollout**: Deploy to small subset of users first
- **Risk Mitigation**: Limit blast radius of potential issues
- **Monitoring**: Requires robust monitoring and alerting
- **Automated Rollback**: Automatic rollback based on metrics

#### Rolling Deployment

- **Resource Efficient**: Updates instances one at a time
- **Gradual Process**: Slower deployment but maintains availability
- **Health Checks**: Requires proper health check implementation
- **Rollback Complexity**: More complex rollback process

## Containerization and Orchestration

### Docker Best Practices

```dockerfile
# Use specific base image versions
FROM node:18-alpine

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY --chown=nextjs:nodejs . .

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start application
CMD ["npm", "start"]
```

### Kubernetes Deployment Patterns

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
        - name: web-app
          image: myapp:latest
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "64Mi"
              cpu: "250m"
            limits:
              memory: "128Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: NODE_ENV
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: url
```

## Monitoring and Observability

### The Three Pillars

#### Metrics

- **System Metrics**: CPU, memory, disk, network usage
- **Application Metrics**: Response time, throughput, error rates
- **Business Metrics**: User engagement, conversion rates, revenue
- **Infrastructure Metrics**: Container health, cluster status

#### Logging

- **Structured Logging**: Use JSON format for better parsing
- **Log Levels**: Appropriate use of DEBUG, INFO, WARN, ERROR
- **Centralized Logging**: Aggregate logs from all services
- **Log Retention**: Implement appropriate retention policies

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "user-service",
  "version": "1.2.3",
  "request_id": "abc123",
  "user_id": "user456",
  "message": "User login successful",
  "duration_ms": 150,
  "status_code": 200
}
```

#### Tracing

- **Distributed Tracing**: Track requests across microservices
- **Span Context**: Maintain context across service boundaries
- **Performance Analysis**: Identify bottlenecks and latency issues
- **Error Correlation**: Connect errors across service calls

### Alerting Best Practices

- **Alert on Symptoms**: Alert on user-facing issues, not just causes
- **Actionable Alerts**: Every alert should have a clear action
- **Alert Fatigue**: Avoid too many alerts; tune thresholds carefully
- **Escalation Policies**: Define clear escalation procedures
- **Documentation**: Include runbooks with alerts

### Prometheus Configuration Example

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093
```

## Security in DevOps (DevSecOps)

### Security Integration Points

#### Code Security

- **Static Analysis**: Use tools like SonarQube, CodeQL
- **Dependency Scanning**: Check for vulnerable dependencies
- **Secret Management**: Never commit secrets to version control
- **Code Review**: Include security review in code review process

#### Build Security

- **Container Scanning**: Scan images for vulnerabilities
- **Supply Chain Security**: Verify integrity of dependencies
- **Signed Artifacts**: Sign and verify build artifacts
- **Secure Build Environment**: Harden build infrastructure

#### Deployment Security

- **Network Policies**: Implement proper network segmentation
- **RBAC**: Use role-based access control
- **Secrets Management**: Use proper secret management solutions
- **Runtime Security**: Monitor for runtime threats

### Security Tools Integration

```yaml
# Example security scanning in CI/CD
security_scan:
  stage: security
  script:
    # Container vulnerability scanning
    - trivy image $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

    # Infrastructure security scanning
    - tfsec terraform/

    # Kubernetes security scanning
    - kube-score k8s/manifests/

    # Dependency vulnerability scanning
    - npm audit

    # Static code analysis
    - sonar-scanner
  artifacts:
    reports:
      sast: gl-sast-report.json
      container_scanning: gl-container-scanning-report.json
```

## Configuration Management

### Ansible Best Practices

```yaml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  vars:
    app_name: myapp
    app_version: "{{ lookup('env', 'APP_VERSION') | default('latest') }}"

  tasks:
    - name: Install required packages
      package:
        name: "{{ item }}"
        state: present
      loop:
        - nginx
        - python3
        - python3-pip
      tags: packages

    - name: Configure nginx
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        backup: yes
      notify: restart nginx
      tags: config

    - name: Deploy application
      copy:
        src: "{{ app_name }}-{{ app_version }}.tar.gz"
        dest: "/opt/{{ app_name }}/"
      notify: restart app
      tags: deploy

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted

    - name: restart app
      service:
        name: "{{ app_name }}"
        state: restarted
```

### Configuration Principles

- **Idempotency**: Configurations should be idempotent
- **Version Control**: All configurations in version control
- **Environment Separation**: Separate configs for different environments
- **Validation**: Validate configurations before applying
- **Documentation**: Document configuration parameters and dependencies

## Incident Response and Recovery

### Incident Management Process

1. **Detection**: Automated monitoring and alerting
2. **Response**: Immediate response team activation
3. **Mitigation**: Quick actions to reduce impact
4. **Resolution**: Permanent fix implementation
5. **Post-Mortem**: Learning and improvement process

### Runbook Template

```markdown
# Service Outage Runbook

## Symptoms

- High error rate (>5%)
- Increased response time (>2s)
- Failed health checks

## Investigation Steps

1. Check service logs: `kubectl logs -f deployment/myapp`
2. Check metrics dashboard: [Link to Grafana]
3. Verify database connectivity
4. Check external dependencies

## Mitigation Steps

1. Scale up replicas: `kubectl scale deployment myapp --replicas=5`
2. Restart unhealthy pods: `kubectl delete pod -l app=myapp`
3. Enable circuit breaker if available
4. Redirect traffic to backup service

## Escalation

- Primary: @oncall-team
- Secondary: @engineering-lead
- Manager: @engineering-manager

## Communication

- Status page: [Link]
- Slack channel: #incidents
- Email list: incidents@company.com
```

### Disaster Recovery

- **Backup Strategy**: Regular, tested backups of critical data
- **Recovery Time Objective (RTO)**: Maximum acceptable downtime
- **Recovery Point Objective (RPO)**: Maximum acceptable data loss
- **Failover Procedures**: Documented and tested failover processes
- **Communication Plan**: Clear communication during disasters

## Performance Optimization

### Application Performance

- **Caching Strategies**: Implement appropriate caching layers
- **Database Optimization**: Query optimization and indexing
- **CDN Usage**: Use content delivery networks for static assets
- **Load Balancing**: Distribute traffic effectively
- **Auto-scaling**: Implement horizontal and vertical scaling

### Infrastructure Performance

- **Resource Right-sizing**: Match resources to actual needs
- **Network Optimization**: Optimize network configuration
- **Storage Performance**: Choose appropriate storage types
- **Monitoring**: Continuous performance monitoring
- **Capacity Planning**: Plan for future growth

## Cost Optimization

### Cloud Cost Management

- **Resource Tagging**: Implement comprehensive tagging strategy
- **Reserved Instances**: Use reserved instances for predictable workloads
- **Spot Instances**: Use spot instances for fault-tolerant workloads
- **Auto-scaling**: Scale resources based on demand
- **Regular Reviews**: Conduct regular cost optimization reviews

### Cost Monitoring

```yaml
# Example cost alert configuration
cost_alert:
  name: "Monthly AWS Cost Alert"
  threshold: 1000
  currency: USD
  time_period: MONTHLY
  notification:
    - email: finance@company.com
    - slack: #finance-alerts
  filters:
    - service: EC2-Instance
    - environment: production
```

## Team Collaboration and Culture

### DevOps Culture Principles

- **Collaboration**: Break down silos between teams
- **Shared Responsibility**: Everyone owns quality and reliability
- **Continuous Learning**: Embrace learning from failures
- **Automation**: Automate repetitive tasks
- **Measurement**: Make decisions based on data

### Communication Practices

- **Daily Standups**: Regular team synchronization
- **Incident Reviews**: Blameless post-mortems
- **Knowledge Sharing**: Regular tech talks and documentation
- **Cross-training**: Team members learn multiple areas
- **Feedback Loops**: Regular retrospectives and improvements

### Documentation Standards

- **Architecture Decisions**: Document architectural decisions and rationale
- **Runbooks**: Maintain up-to-date operational procedures
- **API Documentation**: Keep API documentation current
- **Deployment Guides**: Document deployment procedures
- **Troubleshooting Guides**: Common issues and solutions

This context should be used as a comprehensive reference for implementing DevOps best practices, ensuring reliable and scalable software delivery, and maintaining operational excellence throughout the software development lifecycle.
