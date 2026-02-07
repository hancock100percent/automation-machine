# Domain 2: Security and Compliance (30%)

> 4 task statements | ~15 questions on the exam
> **Heaviest-weighted domain tied with Domain 3 -- study this thoroughly**

## Task Statement 2.1: Understand the AWS Shared Responsibility Model

### The Model

This is the single most important concept on the exam. Expect 5+ questions on it.

```
+-----------------------------------------------------+
|               CUSTOMER RESPONSIBILITY                |
|           "Security IN the Cloud"                    |
|                                                      |
|  Customer Data                                       |
|  Platform, Applications, IAM                         |
|  OS, Network, Firewall Configuration                 |
|  Client-Side Encryption & Data Integrity             |
|  Server-Side Encryption (File System / Data)         |
|  Network Traffic Protection (encryption, integrity)  |
+-----------------------------------------------------+
|               AWS RESPONSIBILITY                     |
|           "Security OF the Cloud"                    |
|                                                      |
|  Compute, Storage, Database, Networking              |
|  Hardware / AWS Global Infrastructure                |
|  Regions, Availability Zones, Edge Locations         |
|  Software (hypervisor, managed services host OS)     |
+-----------------------------------------------------+
```

### How Responsibility Shifts by Service Type

| Service Type | Customer Manages | AWS Manages |
|-------------|-----------------|-------------|
| **IaaS** (e.g., EC2) | OS, patching, firewall, app, data, encryption | Hardware, hypervisor, physical security |
| **Managed** (e.g., RDS) | Data, user access, encryption settings | OS patching, engine patching, hardware |
| **Serverless** (e.g., Lambda) | Code, data, IAM permissions | Everything else (runtime, scaling, OS, infra) |
| **SaaS** (e.g., S3 as object store) | Data, access policies, encryption config | Storage infrastructure, durability, availability |

### Key Exam Tips for Shared Responsibility

- **Patching EC2 OS** = Customer responsibility
- **Patching RDS database engine** = AWS responsibility
- **Physical security of data centers** = Always AWS
- **IAM user management** = Always Customer
- **Encryption configuration** = Customer chooses, AWS provides tools

---

## Task Statement 2.2: Understand AWS Cloud security, governance, and compliance concepts

### Compliance Programs

AWS maintains many compliance certifications. Customers inherit these for the infrastructure layer.

| Program | Description |
|---------|-------------|
| **SOC 1/2/3** | Service Organization Controls (auditing) |
| **PCI DSS** | Payment Card Industry Data Security Standard |
| **HIPAA** | Health Insurance Portability and Accountability Act |
| **FedRAMP** | Federal Risk and Authorization Management Program |
| **GDPR** | General Data Protection Regulation (EU data privacy) |
| **ISO 27001** | Information security management |

### Compliance Tools

| Service | Purpose |
|---------|---------|
| **AWS Artifact** | On-demand access to AWS compliance reports (SOC, PCI, ISO). Self-service portal. |
| **AWS Config** | Tracks resource configuration changes. Evaluate compliance rules. |
| **AWS CloudTrail** | Logs ALL API calls (who did what, when, from where). Governance audit trail. |
| **AWS Audit Manager** | Continuous auditing to assess compliance |

### Encryption

| Type | Description | AWS Services |
|------|-------------|-------------|
| **At rest** | Data encrypted on disk/storage | AWS KMS, S3 server-side encryption, EBS encryption |
| **In transit** | Data encrypted during transfer | TLS/SSL, AWS Certificate Manager (ACM), VPN |
| **Client-side** | Encrypted before sending to AWS | Customer-managed keys |

### AWS Key Management Service (KMS)

- Create and manage encryption keys
- Integrated with most AWS services (S3, EBS, RDS, Lambda, etc.)
- Customer Managed Keys (CMK) vs. AWS Managed Keys
- Automatic key rotation available

---

## Task Statement 2.3: Identify AWS access management capabilities

### IAM (Identity and Access Management)

IAM is free and global (not Region-specific).

| Concept | Description |
|---------|-------------|
| **Users** | Individual people or applications. Have credentials (password, access keys). |
| **Groups** | Collection of users. Attach policies to groups, not individual users. |
| **Roles** | Temporary credentials assumed by users, applications, or AWS services. No permanent credentials. |
| **Policies** | JSON documents defining permissions (Allow/Deny on specific Actions for specific Resources). |

### IAM Best Practices

1. **Lock away the root account** -- Use for initial setup only. Enable MFA.
2. **Create individual IAM users** -- Never share credentials.
3. **Use groups for permissions** -- Assign policies to groups, add users to groups.
4. **Grant least privilege** -- Start with minimum permissions, add as needed.
5. **Enable MFA** -- Especially on root and privileged accounts.
6. **Use roles for applications** -- EC2 instances and Lambda functions should use roles, not access keys.
7. **Rotate credentials regularly** -- Access keys should be rotated periodically.
8. **Use policy conditions** -- Restrict by IP, time, MFA status, etc.

### Multi-Factor Authentication (MFA)

Something you know (password) + something you have (MFA device).

Types: Virtual MFA (app like Authy), Hardware MFA key, U2F security key.

### AWS Organizations

| Feature | Description |
|---------|-------------|
| **Organizational Units (OUs)** | Group accounts hierarchically |
| **Service Control Policies (SCPs)** | Guardrails that restrict what accounts CAN do (deny-based) |
| **Consolidated Billing** | Single bill for all accounts, volume discounts |
| **Account isolation** | Security boundary between workloads |

### AWS IAM Identity Center (formerly AWS SSO)

- Single sign-on for multiple AWS accounts and business applications
- Centralized access management
- Integrates with external identity providers (Active Directory, Okta, etc.)

---

## Task Statement 2.4: Identify components and resources for security

### Network Security

| Service | Layer | Purpose |
|---------|-------|---------|
| **Security Groups** | Instance-level | Stateful firewall. Allow rules only. Default: deny all inbound, allow all outbound. |
| **NACLs** (Network ACLs) | Subnet-level | Stateless firewall. Allow AND deny rules. Default: allow all. |
| **AWS WAF** | Application (L7) | Web Application Firewall. Protects against SQL injection, XSS, bot attacks. |
| **AWS Shield** | Network (L3/L4) | DDoS protection. Standard (free, automatic) and Advanced (paid, 24/7 response). |

### Security Groups vs. NACLs

| Feature | Security Groups | NACLs |
|---------|----------------|-------|
| Level | Instance | Subnet |
| State | Stateful (return traffic auto-allowed) | Stateless (must explicitly allow return) |
| Rules | Allow only | Allow AND Deny |
| Default | Deny all inbound | Allow all |
| Evaluation | All rules evaluated together | Rules evaluated in number order |

### Threat Detection and Monitoring

| Service | Purpose |
|---------|---------|
| **Amazon GuardDuty** | Intelligent threat detection. Analyzes CloudTrail, VPC Flow Logs, DNS logs. ML-based. |
| **Amazon Inspector** | Automated vulnerability scanning for EC2, Lambda, and container images. |
| **Amazon Macie** | Uses ML to discover and protect sensitive data (PII, credit card numbers) in S3. |
| **AWS Security Hub** | Centralized security findings dashboard. Aggregates from GuardDuty, Inspector, Macie, etc. |
| **Amazon Detective** | Investigate and analyze security findings. Root cause analysis. |
| **AWS Trusted Advisor** | Best practice checks across security, cost, performance, fault tolerance, service limits. |

### AWS Trusted Advisor Security Checks (Basic/Free)

These 6 checks are available on all support plans:
1. S3 bucket permissions (public access)
2. Security groups -- unrestricted access (0.0.0.0/0)
3. IAM use (at least one IAM user created)
4. MFA on root account
5. EBS public snapshots
6. RDS public snapshots

---

## Practice Focus

- **Shared Responsibility Model** -- Know it cold. Be able to classify any task as customer or AWS responsibility.
- **Security Groups vs. NACLs** -- Stateful vs. stateless, instance vs. subnet, allow-only vs. allow+deny.
- **IAM** -- Users, groups, roles, policies. Least privilege. MFA.
- **Encryption** -- At rest vs. in transit. KMS. Certificate Manager.
- **Know the security services** -- GuardDuty (threat detection), Inspector (vulnerability scanning), Macie (sensitive data), WAF (web attacks), Shield (DDoS).
