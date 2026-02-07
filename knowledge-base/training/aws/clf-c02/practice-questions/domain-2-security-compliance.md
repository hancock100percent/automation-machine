# Domain 2: Security and Compliance -- Practice Questions

> 20 questions | Exam weight: 30% (~15 questions on the real exam)
> Format: Multiple choice (1 correct from 4) unless marked [Multiple Response]

---

### Q1. Shared Responsibility -- EC2 Patching

Who is responsible for patching the operating system on an Amazon EC2 instance?

A. AWS
B. The customer
C. Both AWS and the customer share OS patching equally
D. Neither -- patching is automatic

**Answer: B**

> Under the Shared Responsibility Model, EC2 is an IaaS service. The customer manages the guest OS, including patching and updates. AWS manages the underlying hardware and hypervisor.

---

### Q2. Shared Responsibility -- RDS Patching

Who is responsible for patching the database engine on an Amazon RDS instance?

A. The customer
B. AWS
C. The database vendor (Oracle, MySQL, etc.)
D. A third-party managed services provider

**Answer: B**

> RDS is a managed service. AWS handles database engine patching, OS patching, and hardware maintenance. The customer manages data, user access, and encryption configuration.

---

### Q3. IAM -- Least Privilege

A new developer needs access to a specific S3 bucket to upload files. Which IAM best practice should be followed?

A. Give the developer the AdministratorAccess policy for convenience
B. Create a policy granting only PutObject access to the specific bucket
C. Share the root account credentials with the developer
D. Disable IAM and use S3 bucket policies only

**Answer: B**

> The principle of least privilege states that users should have only the minimum permissions needed for their task. A custom policy granting PutObject on the specific bucket follows this principle.

---

### Q4. MFA

Which authentication mechanism adds an extra layer of security beyond a password?

A. Access keys
B. Multi-Factor Authentication (MFA)
C. Security groups
D. NACLs

**Answer: B**

> MFA requires something you know (password) + something you have (MFA device/token). It is strongly recommended for root accounts and privileged IAM users. Access keys are credentials, not an additional authentication factor.

---

### Q5. Security Groups vs NACLs

A security team needs to create an explicit DENY rule for a specific IP address trying to access their web server. Which should they use?

A. Security Groups
B. Network ACLs (NACLs)
C. AWS WAF
D. IAM policies

**Answer: B**

> NACLs support both Allow and Deny rules, making them suitable for explicitly blocking specific IPs. Security Groups only support Allow rules -- they implicitly deny everything not explicitly allowed. While WAF could also block IPs, NACLs are the network-layer answer.

---

### Q6. Security Groups -- Stateful

What does it mean that Security Groups are "stateful"?

A. They keep a log of all traffic
B. If inbound traffic is allowed, the response traffic is automatically allowed
C. They can store encryption keys
D. Rules must be applied in a specific order

**Answer: B**

> Stateful means that if an inbound request is allowed, the outbound response is automatically allowed (and vice versa). You don't need to create separate inbound and outbound rules for the same traffic. NACLs, by contrast, are stateless and require explicit rules for both directions.

---

### Q7. AWS Shield

A company's website is experiencing a DDoS attack. Which AWS service provides managed DDoS protection?

A. AWS WAF
B. AWS Shield
C. Amazon Inspector
D. Amazon GuardDuty

**Answer: B**

> AWS Shield provides DDoS protection. Shield Standard is free and automatic for all AWS customers. Shield Advanced ($3,000/mo) provides enhanced DDoS protection, 24/7 DDoS response team, and cost protection. WAF protects against web application attacks (SQL injection, XSS) but is not specifically for DDoS.

---

### Q8. AWS WAF

Which type of attack does AWS WAF protect against?

A. DDoS attacks
B. SQL injection and cross-site scripting (XSS)
C. Physical data center intrusion
D. Brute force SSH attacks

**Answer: B**

> AWS WAF (Web Application Firewall) operates at Layer 7 and protects against common web exploits like SQL injection, XSS, and bot attacks. It works with CloudFront, ALB, and API Gateway.

---

### Q9. AWS Artifact

Where can a customer download AWS compliance reports such as SOC and PCI DSS?

A. AWS Config
B. AWS Artifact
C. AWS Trusted Advisor
D. AWS CloudTrail

**Answer: B**

> AWS Artifact is a self-service portal for on-demand access to AWS compliance reports and security documentation, including SOC reports, PCI DSS attestation, and ISO certifications.

---

### Q10. CloudTrail

Which AWS service logs ALL API calls made to your AWS account, including who made the call, when, and from what IP?

A. Amazon CloudWatch
B. AWS Config
C. AWS CloudTrail
D. Amazon Inspector

**Answer: C**

> AWS CloudTrail records API activity across your AWS account. Every action taken in the Console, CLI, or SDK is logged. CloudWatch monitors metrics and logs (operational), while CloudTrail is for governance and auditing.

---

### Q11. GuardDuty

Which AWS service uses machine learning to continuously monitor for malicious activity and unauthorized behavior in your AWS environment?

A. Amazon Inspector
B. Amazon Macie
C. Amazon GuardDuty
D. AWS Config

**Answer: C**

> Amazon GuardDuty is an intelligent threat detection service that analyzes CloudTrail logs, VPC Flow Logs, and DNS logs using ML to identify threats like cryptocurrency mining, compromised instances, and unauthorized access.

---

### Q12. Amazon Inspector

A security team wants to scan their EC2 instances for known software vulnerabilities and unintended network exposure. Which service should they use?

A. Amazon GuardDuty
B. Amazon Inspector
C. Amazon Macie
D. AWS Shield

**Answer: B**

> Amazon Inspector automatically scans EC2 instances, Lambda functions, and container images for software vulnerabilities (CVEs) and unintended network exposure. GuardDuty detects threats; Macie finds sensitive data; Shield protects against DDoS.

---

### Q13. Amazon Macie

Which AWS service uses machine learning to discover, classify, and protect sensitive data (such as PII) stored in Amazon S3?

A. Amazon GuardDuty
B. Amazon Inspector
C. Amazon Macie
D. AWS Secrets Manager

**Answer: C**

> Amazon Macie automatically discovers sensitive data like personally identifiable information (PII), credit card numbers, and other confidential data stored in S3 buckets.

---

### Q14. Encryption at Rest

Which AWS service is used to create and manage encryption keys for encrypting data at rest?

A. AWS Certificate Manager
B. AWS Key Management Service (KMS)
C. AWS Secrets Manager
D. AWS IAM

**Answer: B**

> AWS KMS creates, manages, and controls encryption keys used to encrypt data at rest. It integrates with most AWS services (S3, EBS, RDS, etc.). Certificate Manager handles SSL/TLS certificates for data in transit. Secrets Manager stores application secrets, not encryption keys.

---

### Q15. IAM Roles

An application running on an EC2 instance needs to access an S3 bucket. What is the MOST secure way to grant this access?

A. Store access keys in the application code
B. Store access keys in environment variables on the instance
C. Attach an IAM role to the EC2 instance
D. Use the root account credentials

**Answer: C**

> IAM roles provide temporary security credentials that are automatically rotated. Attaching a role to EC2 is the recommended approach. Storing access keys in code or environment variables is insecure and against best practices. Never use root credentials for application access.

---

### Q16. Root Account Security

Which of the following are AWS best practices for securing the root account? [Multiple Response -- select 2]

A. Use the root account for daily administrative tasks
B. Enable multi-factor authentication (MFA) on the root account
C. Share root credentials among the IT team for emergencies
D. Create individual IAM users for daily tasks instead of using root
E. Delete the root account after initial setup

**Answer: B, D**

> Best practices: Enable MFA on root, and create IAM users for daily use. The root account should only be used for initial setup and tasks that specifically require it (like changing the support plan). Never share credentials. The root account cannot be deleted.

---

### Q17. AWS Organizations -- SCPs

What is the purpose of Service Control Policies (SCPs) in AWS Organizations?

A. They grant permissions to IAM users
B. They set maximum permission boundaries for accounts in the organization
C. They encrypt data at rest
D. They monitor API calls

**Answer: B**

> SCPs define the maximum permissions available to accounts in an Organization. They act as guardrails -- even if an IAM policy grants access, the SCP can deny it. SCPs do not grant permissions; they restrict what is allowed.

---

### Q18. Security Hub

Which AWS service provides a centralized dashboard that aggregates security findings from GuardDuty, Inspector, Macie, and other security tools?

A. AWS CloudTrail
B. AWS Security Hub
C. Amazon CloudWatch
D. AWS Config

**Answer: B**

> AWS Security Hub gives you a comprehensive view of security alerts and compliance status across your AWS accounts. It aggregates findings from GuardDuty, Inspector, Macie, Firewall Manager, and partner tools into a single dashboard.

---

### Q19. Shared Responsibility -- Physical Security

Who is responsible for the physical security of AWS data centers?

A. The customer
B. AWS
C. A third-party security company
D. Shared between AWS and the customer

**Answer: B**

> Physical security of data centers (locks, cameras, guards, biometrics) is always an AWS responsibility. This is part of "Security OF the Cloud." Customers never have physical access to AWS facilities.

---

### Q20. Encryption in Transit

Which AWS service helps provision and manage SSL/TLS certificates to encrypt data in transit?

A. AWS KMS
B. AWS Certificate Manager (ACM)
C. AWS Secrets Manager
D. AWS CloudHSM

**Answer: B**

> AWS Certificate Manager (ACM) provisions, manages, and deploys SSL/TLS certificates for encrypting data in transit. ACM integrates with CloudFront, ALB, and API Gateway. KMS is for encryption at rest. CloudHSM provides hardware-based key storage.

---

## Score Tracker

| Attempt | Date | Score | Notes |
|---------|------|-------|-------|
| 1 | | /20 | |
| 2 | | /20 | |
| 3 | | /20 | |
