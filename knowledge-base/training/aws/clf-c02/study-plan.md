# CLF-C02 Study Plan -- Exam Domain Map

> Source: AWS Certified Cloud Practitioner (CLF-C02) Exam Guide
> Last updated: 2026-02-07

## Exam Structure

| Item | Detail |
|------|--------|
| Exam code | CLF-C02 |
| Duration | 90 minutes |
| Questions | 65 (50 scored + 15 unscored/experimental) |
| Passing score | 700 / 1000 (scaled) |
| Format | Multiple choice (1 correct out of 4) and Multiple response (2+ correct out of 5) |
| Cost | $100 USD |
| Languages | English, Japanese, Korean, Simplified Chinese, Traditional Chinese, Bahasa Indonesian, Spanish, French, German, Italian, Portuguese |
| Testing | Pearson VUE (test center or online proctored) |
| Validity | 3 years |

## Domain Breakdown

| # | Domain | Weight | Task Statements | Study Notes |
|---|--------|--------|-----------------|-------------|
| 1 | Cloud Concepts | 24% | 3 | [domain-1](domains/domain-1-cloud-concepts.md) |
| 2 | Security and Compliance | 30% | 4 | [domain-2](domains/domain-2-security-compliance.md) |
| 3 | Cloud Technology and Services | 34% | 4 | [domain-3](domains/domain-3-technology-services.md) |
| 4 | Billing, Pricing, and Support | 12% | 3 | [domain-4](domains/domain-4-billing-pricing.md) |
| | **Total** | **100%** | **14** | |

## Study Priority (by impact)

Focus study time proportional to domain weight:

1. **Domain 3: Cloud Technology and Services (34%)** -- Largest domain. Know core services across compute, storage, networking, databases. Understand when to use which service.
2. **Domain 2: Security and Compliance (30%)** -- Second largest. Shared responsibility model is foundational. Know IAM inside-out.
3. **Domain 1: Cloud Concepts (24%)** -- Cloud fundamentals. Understand the "why" of cloud, not just the "what."
4. **Domain 4: Billing, Pricing, and Support (12%)** -- Smallest but free points. Pricing models and support plans are straightforward memorization.

---

## Domain 1: Cloud Concepts (24%)

### Task Statement 1.1: Define the benefits of the AWS Cloud

**Knowledge of:**
- Value proposition of the AWS Cloud (cost savings, agility, global reach)
- Benefits: high availability, elasticity, agility, pay-as-you-go pricing
- Six advantages of cloud computing (from AWS Well-Architected)
- Migration strategies (the 6 R's): Rehost, Replatform, Refactor, Repurchase, Retire, Retain

**Skills in:**
- Understanding the advantages of cloud vs. on-premises
- Identifying how cloud reduces TCO (Total Cost of Ownership)
- Understanding the benefits of economies of scale

### Task Statement 1.2: Identify design principles of the AWS Cloud

**Knowledge of:**
- AWS Well-Architected Framework (6 pillars)
- AWS Cloud Adoption Framework (AWS CAF)

**Skills in:**
- Understanding the pillars of the Well-Architected Framework:
  1. Operational Excellence
  2. Security
  3. Reliability
  4. Performance Efficiency
  5. Cost Optimization
  6. Sustainability
- Applying design principles: design for failure, decouple components, implement elasticity, think parallel

### Task Statement 1.3: Understand the benefits of and strategies for migration to the AWS Cloud

**Knowledge of:**
- Cloud adoption strategies
- Migration tools: AWS Migration Hub, AWS Application Migration Service, AWS Database Migration Service (DMS)
- AWS Snow Family for offline data transfer

**Skills in:**
- Identifying appropriate migration strategies for workloads
- Understanding the benefits of AWS migration tools

---

## Domain 2: Security and Compliance (30%)

### Task Statement 2.1: Understand the AWS Shared Responsibility Model

**Knowledge of:**
- AWS Shared Responsibility Model
- Customer responsibilities (security IN the cloud): data, OS patching, firewall config, encryption
- AWS responsibilities (security OF the cloud): hardware, global infrastructure, managed services

**Skills in:**
- Describing the shared responsibility model
- Recognizing which security tasks are customer vs. AWS responsibility
- Understanding how responsibilities shift between IaaS, PaaS, and SaaS

### Task Statement 2.2: Understand AWS Cloud security, governance, and compliance concepts

**Knowledge of:**
- AWS compliance programs (SOC, PCI DSS, HIPAA, FedRAMP, GDPR)
- AWS Artifact (compliance reports)
- AWS Config (resource compliance)
- AWS CloudTrail (API logging)
- Encryption at rest and in transit (AWS KMS, AWS Certificate Manager)
- Geographic/regulatory data sovereignty

**Skills in:**
- Identifying AWS compliance resources
- Understanding encryption concepts and where they apply
- Recognizing governance best practices

### Task Statement 2.3: Identify AWS access management capabilities

**Knowledge of:**
- IAM: users, groups, roles, policies
- Root account security and MFA
- AWS Organizations, SCPs (Service Control Policies)
- AWS IAM Identity Center (SSO)
- Principle of least privilege

**Skills in:**
- Understanding IAM identities and their use cases
- Describing authentication vs. authorization
- Implementing MFA and access key rotation

### Task Statement 2.4: Identify components and resources for security

**Knowledge of:**
- Security groups and NACLs (Network Access Control Lists)
- AWS WAF (Web Application Firewall)
- AWS Shield (DDoS protection)
- Amazon Inspector (vulnerability scanning)
- Amazon GuardDuty (threat detection)
- AWS Security Hub
- Amazon Macie (sensitive data discovery)
- AWS Trusted Advisor (security checks)

**Skills in:**
- Identifying appropriate security services for different scenarios
- Understanding network security layers
- Recognizing when to use which security tool

---

## Domain 3: Cloud Technology and Services (34%)

### Task Statement 3.1: Define methods of deploying and operating in the AWS Cloud

**Knowledge of:**
- Programmatic access: AWS CLI, SDKs, APIs
- AWS Management Console
- Infrastructure as Code: AWS CloudFormation, AWS CDK
- Deployment models: single AZ, multi-AZ, multi-Region
- Connectivity options: VPN, AWS Direct Connect, public internet

**Skills in:**
- Selecting appropriate deployment strategies
- Identifying different access methods and their use cases
- Understanding IaC benefits

### Task Statement 3.2: Define the AWS global infrastructure

**Knowledge of:**
- Regions, Availability Zones, Edge Locations
- AWS Local Zones, Wavelength Zones
- High availability through multi-AZ and multi-Region
- AWS CloudFront (CDN), Route 53 (DNS)
- AWS Global Accelerator
- AWS Outposts (on-premises extension)

**Skills in:**
- Describing Regions, AZs, and Edge Locations
- Choosing appropriate Regions based on latency, compliance, service availability
- Understanding high availability architectures

### Task Statement 3.3: Identify AWS compute services

**Knowledge of:**
- Amazon EC2 (instances, types, pricing models)
- AWS Lambda (serverless)
- Amazon ECS / EKS / Fargate (containers)
- AWS Elastic Beanstalk (PaaS)
- AWS Lightsail (simplified compute)
- AWS Batch (batch processing)

**Skills in:**
- Selecting appropriate compute services for use cases
- Understanding EC2 pricing: On-Demand, Reserved, Spot, Savings Plans
- Differentiating serverless vs. server-based

### Task Statement 3.4: Identify AWS services for other key areas

**Knowledge of:**

**Storage:**
- Amazon S3 (object storage, storage classes)
- Amazon EBS (block storage)
- Amazon EFS (file storage)
- Amazon S3 Glacier (archival)
- AWS Storage Gateway

**Database:**
- Amazon RDS (relational, managed)
- Amazon DynamoDB (NoSQL, key-value)
- Amazon ElastiCache (in-memory)
- Amazon Redshift (data warehouse)
- Amazon Aurora (high-performance relational)

**Networking:**
- Amazon VPC (Virtual Private Cloud)
- Subnets, Route Tables, Internet Gateways, NAT Gateways
- Elastic Load Balancing (ALB, NLB)
- Amazon API Gateway

**AI/ML:**
- Amazon SageMaker (ML platform)
- Amazon Rekognition (image/video analysis)
- Amazon Comprehend (NLP)
- Amazon Lex (chatbots)
- Amazon Polly (text-to-speech)
- Amazon Transcribe (speech-to-text)
- Amazon Translate (language translation)
- Amazon Bedrock (foundation models)

**Analytics:**
- Amazon Athena (S3 query)
- Amazon Kinesis (real-time streaming)
- AWS Glue (ETL)
- Amazon QuickSight (BI)

**Application Integration:**
- Amazon SQS (message queue)
- Amazon SNS (pub/sub notifications)
- AWS Step Functions (workflow orchestration)
- Amazon EventBridge (event bus)

**Developer Tools:**
- AWS CodeCommit, CodeBuild, CodeDeploy, CodePipeline
- AWS X-Ray (tracing)
- Amazon CloudWatch (monitoring, logs, alarms)

**Management & Governance:**
- AWS CloudFormation
- AWS Systems Manager
- AWS Trusted Advisor
- AWS Health Dashboard

**Skills in:**
- Selecting the right service for a given scenario
- Understanding managed vs. unmanaged services
- Knowing which services are serverless

---

## Domain 4: Billing, Pricing, and Support (12%)

### Task Statement 4.1: Compare AWS pricing models

**Knowledge of:**
- On-Demand, Reserved Instances, Savings Plans, Spot Instances
- Data transfer pricing (inbound free, outbound charged)
- Storage tiers and pricing (S3 Standard vs. IA vs. Glacier)
- Free Tier: 12-month, always free, trials

**Skills in:**
- Identifying which pricing model fits a workload
- Understanding how data transfer costs work
- Recognizing Free Tier eligible services

### Task Statement 4.2: Understand resources for billing, budget, and cost management

**Knowledge of:**
- AWS Billing Dashboard / AWS Billing and Cost Management
- AWS Cost Explorer (analyze spend)
- AWS Budgets (set alerts)
- AWS Cost and Usage Report (detailed CSV)
- AWS Pricing Calculator (estimate costs)
- Cost allocation tags
- AWS Organizations consolidated billing

**Skills in:**
- Setting up billing alerts and budgets
- Reading and interpreting Cost Explorer
- Understanding consolidated billing benefits

### Task Statement 4.3: Identify AWS technical resources and AWS Support options

**Knowledge of:**
- AWS Support plans: Basic, Developer, Business, Enterprise On-Ramp, Enterprise
- AWS Trusted Advisor (checks across cost, performance, security, fault tolerance, service limits)
- AWS Personal Health Dashboard
- AWS re:Post (community)
- AWS Partner Network (APN)
- AWS Professional Services
- AWS Marketplace
- AWS Training and Certification
- AWS documentation, whitepapers, blogs

**Skills in:**
- Selecting appropriate support plan based on needs
- Understanding Trusted Advisor check categories
- Knowing when to use AWS Support vs. self-service

---

## AWS Support Plans Quick Reference

| Feature | Basic | Developer | Business | Enterprise On-Ramp | Enterprise |
|---------|-------|-----------|----------|-------------------|------------|
| Price | Free | $29/mo+ | $100/mo+ | $5,500/mo | $15,000/mo+ |
| Trusted Advisor | Core checks | Core checks | Full checks | Full checks | Full checks |
| Response time | None | 12-24 hrs | 1-24 hrs | 30 min (critical) | 15 min (critical) |
| TAM | No | No | No | Pool of TAMs | Designated TAM |
| Architecture support | None | General guidance | Contextual | Consultative | Consultative |

---

## Key Concepts to Master

### Six Advantages of Cloud Computing
1. Trade fixed expense for variable expense
2. Benefit from massive economies of scale
3. Stop guessing capacity
4. Increase speed and agility
5. Stop spending money running data centers
6. Go global in minutes

### Well-Architected Framework Pillars
1. **Operational Excellence** -- Run and monitor systems, continuously improve
2. **Security** -- Protect data, systems, and assets
3. **Reliability** -- Recover from failures, meet demand
4. **Performance Efficiency** -- Use resources efficiently
5. **Cost Optimization** -- Avoid unnecessary costs
6. **Sustainability** -- Minimize environmental impact

### Shared Responsibility Model (Critical)
- **AWS:** Physical security, hardware, networking, hypervisor, managed services infrastructure
- **Customer:** Data encryption, IAM, OS/network/firewall config, client-side encryption, application security
- **Varies by service type:** IaaS (EC2) = more customer responsibility; SaaS = more AWS responsibility

---

## Cross-References

- Practice questions: [practice-questions/](practice-questions/)
- Exam tips: [notes/exam-tips.md](notes/exam-tips.md)
- Recommended resources: [resources.md](resources.md)
