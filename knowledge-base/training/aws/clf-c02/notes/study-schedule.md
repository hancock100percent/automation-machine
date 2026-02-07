# CLF-C02 4-Week Study Schedule

> Target: Pass AWS Cloud Practitioner (CLF-C02) in 4 weeks
> Study time: ~1 hour/day weekdays, ~2 hours/day weekends
> Total: ~40 hours of study

---

## Week 1: Foundation (Cloud Concepts + Security Basics)

**Goal:** Master Domain 1 (24%) and start Domain 2 (30%). Understand the "why" of cloud before diving into services.

### Day 1 (Mon) -- Cloud Value Proposition
- [ ] Read [Domain 1: Cloud Concepts](../domains/domain-1-cloud-concepts.md) -- Sections: Six Advantages, Cloud Value Proposition
- [ ] Memorize the 6 advantages of cloud computing (trade fixed for variable, economies of scale, stop guessing capacity, speed/agility, stop running data centers, go global in minutes)
- [ ] Understand TCO: capital expense (CapEx) vs. operational expense (OpEx)
- **Key question to answer:** "Why would a company move to the cloud?"

### Day 2 (Tue) -- Cloud Models and Deployment
- [ ] Read Domain 1 -- Sections: Service Models (IaaS/PaaS/SaaS), Deployment Models
- [ ] Know the differences: IaaS (EC2), PaaS (Elastic Beanstalk), SaaS (WorkSpaces)
- [ ] Understand deployment models: public, private, hybrid, multi-cloud
- **Key question to answer:** "What does the customer manage in each model?"

### Day 3 (Wed) -- Well-Architected Framework
- [ ] Read Domain 1 -- Sections: Well-Architected Framework, Design Principles
- [ ] Learn all 6 pillars: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability
- [ ] Understand design principles: design for failure, decouple, elasticity, think parallel
- **Key question to answer:** "Which pillar does this scenario belong to?"

### Day 4 (Thu) -- Migration Strategies
- [ ] Read Domain 1 -- Sections: Migration (6 R's), Snow Family, Migration Tools
- [ ] Memorize the 6 R's: Rehost, Replatform, Refactor, Repurchase, Retire, Retain
- [ ] Know when to use AWS Snow Family (Snowcone, Snowball, Snowmobile) vs. online transfer
- [ ] Understand Cloud Adoption Framework (CAF) perspectives
- **Key question to answer:** "Which migration strategy fits this scenario?"

### Day 5 (Fri) -- Domain 1 Review + Practice
- [ ] Do [Domain 1 Practice Questions](../practice-questions/domain-1-cloud-concepts.md) (20 questions)
- [ ] Score yourself and review explanations for wrong answers
- [ ] Re-read any weak areas identified from wrong answers
- **Target score:** 15/20 (75%) or higher

### Day 6 (Sat) -- Shared Responsibility Model
- [ ] Read [Domain 2: Security and Compliance](../domains/domain-2-security-compliance.md) -- Sections: Shared Responsibility Model
- [ ] Understand the fundamental split: AWS = security OF the cloud, Customer = security IN the cloud
- [ ] Know how responsibility shifts between IaaS, PaaS, and SaaS
- [ ] Study the examples: who patches the OS? Who encrypts data? Who secures the physical building?
- **Key question to answer:** "Is this AWS's responsibility or the customer's?"

### Day 7 (Sun) -- IAM Fundamentals
- [ ] Read Domain 2 -- Sections: IAM, Access Management
- [ ] Understand: users, groups, roles, policies
- [ ] Know: root account security, MFA, principle of least privilege
- [ ] Learn: AWS Organizations, SCPs, IAM Identity Center (SSO)
- [ ] Understand authentication vs. authorization
- **Key question to answer:** "Which IAM entity should be used here?"

**Week 1 checkpoint:** You should be able to explain why cloud matters, name the 6 pillars, describe the shared responsibility model, and set up basic IAM.

---

## Week 2: Security Completion + Core Services

**Goal:** Finish Domain 2 (30%) and start Domain 3 (34%). Heavy on services -- the bulk of the exam.

### Day 8 (Mon) -- Compliance and Encryption
- [ ] Read Domain 2 -- Sections: Compliance Programs, Encryption
- [ ] Know key compliance programs: SOC 1/2/3, PCI DSS, HIPAA, FedRAMP, GDPR
- [ ] Understand AWS Artifact (compliance reports on demand)
- [ ] Learn encryption: at rest (KMS, S3 SSE) vs. in transit (TLS/SSL, ACM)
- [ ] Know CloudTrail (API logging) and AWS Config (resource compliance)
- **Key question to answer:** "How does AWS help with compliance?"

### Day 9 (Tue) -- Security Services
- [ ] Read Domain 2 -- Sections: Security Services, Network Security
- [ ] Learn the security service lineup: GuardDuty, Inspector, Macie, WAF, Shield, Security Hub
- [ ] Understand Security Groups (stateful, instance-level) vs. NACLs (stateless, subnet-level)
- [ ] Know: AWS Shield Standard (free DDoS) vs. Shield Advanced (paid, 24/7 DRT)
- **Key question to answer:** "Which security service detects this threat?"

### Day 10 (Wed) -- Domain 2 Review + Practice
- [ ] Do [Domain 2 Practice Questions](../practice-questions/domain-2-security-compliance.md) (20 questions)
- [ ] Score yourself and review explanations for wrong answers
- [ ] Re-read weak areas from Domain 1 and Domain 2
- **Target score:** 15/20 (75%) or higher

### Day 11 (Thu) -- Compute Services
- [ ] Read [Domain 3: Cloud Technology and Services](../domains/domain-3-technology-services.md) -- Sections: Compute
- [ ] Learn EC2: instance types, pricing models (On-Demand, Reserved, Spot, Savings Plans, Dedicated)
- [ ] Understand Lambda: serverless, event-driven, pay per invocation, 15-min max
- [ ] Know containers: ECS, EKS, Fargate (serverless containers)
- [ ] Learn when to use: Elastic Beanstalk, Lightsail, Batch
- **Key question to answer:** "Which compute service fits this workload?"

### Day 12 (Fri) -- Storage Services
- [ ] Read Domain 3 -- Sections: Storage
- [ ] Master S3: object storage, 7 storage classes (Standard, IA, One Zone-IA, Intelligent-Tiering, Glacier Instant, Flexible, Deep Archive)
- [ ] Know EBS (block storage for EC2) vs. EFS (shared file storage) vs. FSx
- [ ] Understand Storage Gateway (hybrid cloud storage bridge)
- **Key question to answer:** "Which storage class for this access pattern?"

### Day 13 (Sat) -- Databases + Networking
- [ ] Read Domain 3 -- Sections: Databases, Networking
- [ ] Know the database options: RDS (relational), Aurora (high-perf relational), DynamoDB (NoSQL), ElastiCache (in-memory), Redshift (data warehouse)
- [ ] Understand VPC: subnets (public/private), route tables, internet gateway, NAT gateway
- [ ] Learn load balancing: ALB (HTTP/HTTPS) vs. NLB (TCP/UDP)
- [ ] Know: Route 53 (DNS), CloudFront (CDN), API Gateway
- **Key question to answer:** "Relational or NoSQL? Which specific service?"

### Day 14 (Sun) -- Global Infrastructure + Deployment
- [ ] Read Domain 3 -- Sections: Global Infrastructure, Deployment Methods, IaC
- [ ] Understand Regions, Availability Zones, Edge Locations, Local Zones
- [ ] Know: how to choose a Region (latency, compliance, service availability, cost)
- [ ] Learn IaC: CloudFormation (JSON/YAML templates) vs. CDK (programming languages)
- [ ] Understand: AWS CLI, SDKs, Management Console
- [ ] Review: high availability = multi-AZ, disaster recovery = multi-Region
- **Key question to answer:** "How many AZs in a Region? What's an Edge Location for?"

**Week 2 checkpoint:** You should be able to pick the right security service for a scenario, choose between EC2/Lambda/containers, pick the right S3 class, and select the right database.

---

## Week 3: Remaining Services + Billing

**Goal:** Complete Domain 3 (34%) and cover Domain 4 (12%). By end of week, all content reviewed.

### Day 15 (Mon) -- AI/ML and Analytics Services
- [ ] Read Domain 3 -- Sections: AI/ML Services, Analytics
- [ ] Know the AI/ML service map: SageMaker (build ML), Rekognition (images), Comprehend (NLP), Lex (chatbots), Polly (TTS), Transcribe (STT), Translate, Bedrock (foundation models)
- [ ] Learn analytics: Athena (query S3 with SQL), Kinesis (streaming), Glue (ETL), QuickSight (BI dashboards)
- **Key question to answer:** "Which AI service does this task?"

### Day 16 (Tue) -- Application Integration + Management
- [ ] Read Domain 3 -- Sections: Application Integration, Developer Tools, Management
- [ ] Know messaging: SQS (queue, decoupling) vs. SNS (pub/sub, fan-out) vs. EventBridge (event bus)
- [ ] Understand Step Functions (workflow orchestration)
- [ ] Learn monitoring: CloudWatch (metrics, logs, alarms), X-Ray (distributed tracing)
- [ ] Know management: Systems Manager, Trusted Advisor, Health Dashboard
- **Key question to answer:** "SQS or SNS? When to use Step Functions?"

### Day 17 (Wed) -- Domain 3 Review + Practice
- [ ] Do [Domain 3 Practice Questions](../practice-questions/domain-3-technology-services.md) (20 questions)
- [ ] Score yourself and review explanations for wrong answers
- [ ] This is the biggest domain (34%) -- spend extra time on weak areas
- **Target score:** 15/20 (75%) or higher

### Day 18 (Thu) -- Pricing Models
- [ ] Read [Domain 4: Billing, Pricing, and Support](../domains/domain-4-billing-pricing.md) -- Sections: Pricing Models, Data Transfer
- [ ] Master compute pricing: On-Demand vs. Reserved (1yr/3yr, payment options) vs. Spot (up to 90% off, can be interrupted) vs. Savings Plans
- [ ] Know data transfer rules: inbound = free, outbound = charged, between AZs = charged
- [ ] Understand Free Tier: 12-month (EC2 t2.micro), always free (Lambda 1M requests), trials
- **Key question to answer:** "Which pricing model for this workload pattern?"

### Day 19 (Fri) -- Cost Management Tools
- [ ] Read Domain 4 -- Sections: Cost Tools, Consolidated Billing
- [ ] Know the tools: Cost Explorer (visualize spend), Budgets (set alerts), Cost and Usage Report (detailed CSV), Pricing Calculator (estimate)
- [ ] Understand AWS Organizations: consolidated billing, volume discounts, SCPs
- [ ] Learn cost allocation tags (track spend by project/team)
- **Key question to answer:** "Which tool to estimate vs. track vs. alert on costs?"

### Day 20 (Sat) -- Support Plans + Domain 4 Practice
- [ ] Read Domain 4 -- Sections: Support Plans, Trusted Advisor
- [ ] Memorize 5 support plans: Basic (free), Developer ($29), Business ($100), Enterprise On-Ramp ($5,500), Enterprise ($15,000)
- [ ] Know key differences: response times, TAM access, Trusted Advisor scope
- [ ] Trusted Advisor 5 categories: cost optimization, performance, security, fault tolerance, service limits
- [ ] Do [Domain 4 Practice Questions](../practice-questions/domain-4-billing-pricing.md) (20 questions)
- **Target score:** 16/20 (80%) -- this domain is the most straightforward

### Day 21 (Sun) -- Full Review Day
- [ ] Review all wrong answers from practice questions (all 4 domains)
- [ ] Re-read [Exam Tips](../notes/exam-tips.md)
- [ ] Create a personal "weak areas" list -- topics you still struggle with
- [ ] Review key comparison tables:
  - Security Groups vs. NACLs
  - S3 storage classes
  - EC2 pricing models
  - Support plans
  - IaaS vs. PaaS vs. SaaS responsibilities
- **Self-assessment:** Can you confidently answer questions from all 4 domains?

**Week 3 checkpoint:** All content reviewed. All 80 practice questions attempted. Weak areas identified for targeted review in Week 4.

---

## Week 4: Practice Exams + Targeted Review

**Goal:** Solidify knowledge through practice exams and targeted review. Build exam-day confidence.

### Day 22 (Mon) -- Re-do Weak Domain Practice Questions
- [ ] Re-attempt practice questions from your two weakest domains
- [ ] Focus on understanding WHY the right answer is right and WHY the wrong answers are wrong
- [ ] For each wrong answer, go back to the domain study notes and re-read that section
- **Target:** Improve by at least 2 questions from your first attempt

### Day 23 (Tue) -- Rapid-Fire Service Identification
- [ ] Flash card exercise: for each AWS service, write a one-sentence description
- [ ] Focus on the "choose the right service" pattern -- the most common exam question type
- [ ] Key differentiators to drill:
  - RDS vs. DynamoDB vs. Redshift vs. ElastiCache
  - S3 vs. EBS vs. EFS
  - EC2 vs. Lambda vs. Fargate
  - SQS vs. SNS vs. EventBridge
  - GuardDuty vs. Inspector vs. Macie
  - CloudFormation vs. CDK vs. Elastic Beanstalk

### Day 24 (Wed) -- Scenario-Based Review
- [ ] Practice scenario questions: "A company needs to..." -- what service?
- [ ] Focus on the exam's favorite scenarios:
  - Cost optimization (right-sizing, Reserved, Spot)
  - Security (IAM, encryption, shared responsibility)
  - High availability (multi-AZ, load balancing, auto scaling)
  - Migration (6 R's, Snow Family)
  - Compliance (Artifact, Config, CloudTrail)
- [ ] Review the [Study Plan](../study-plan.md) task statements -- each maps to exam questions

### Day 25 (Thu) -- Timed Practice Run
- [ ] Set a 45-minute timer (half the real exam time)
- [ ] Do all 80 practice questions back-to-back without checking answers
- [ ] Score yourself: target 60/80 (75%) to simulate passing
- [ ] Review every wrong answer thoroughly
- **This simulates exam pressure** -- practice managing your time

### Day 26 (Fri) -- Final Weak Spots
- [ ] Based on your timed practice run, identify remaining weak spots
- [ ] Re-read relevant domain study notes for those topics
- [ ] Pay special attention to "tricky" questions -- those with two plausible answers
- [ ] Review the comparison tables one more time

### Day 27 (Sat) -- External Practice Exam (Recommended)
- [ ] Take a full-length external practice exam (see resources below)
- [ ] AWS official practice exam: free with exam registration
- [ ] Alternative: use recommended video courses for additional practice questions
- [ ] Target: 80%+ on external practice to feel confident
- [ ] Review any new concepts or services you encounter

### Day 28 (Sun) -- Exam Eve Review
- [ ] Light review only -- do NOT cram
- [ ] Re-read [Exam Tips](../notes/exam-tips.md)
- [ ] Quick review of key numbers to remember:
  - 6 advantages of cloud
  - 6 Well-Architected pillars
  - 6 R's of migration
  - 5 support plans
  - 5 Trusted Advisor categories
  - 7 S3 storage classes
  - 5 EC2 pricing models
- [ ] Prepare for exam day: ID, test environment, eat well, sleep well
- [ ] **You are ready.** Trust your 4 weeks of preparation.

---

## Exam Day Tips

1. **Time management:** 90 minutes / 65 questions = ~80 seconds per question. Flag hard ones and move on.
2. **Elimination:** Most questions have 2 obviously wrong answers. Choose between the remaining 2.
3. **Key words matter:** "most cost-effective" = different answer than "most reliable"
4. **15 unscored questions:** You don't know which are unscored, so answer all questions seriously.
5. **No penalty for guessing:** Never leave a question blank.
6. **Read carefully:** "Which TWO" means multiple response -- select exactly 2 answers.

---

## External Resources for Practice

- AWS official practice exam (free with registration)
- AWS Skill Builder (free digital training courses)
- AWS Cloud Practitioner Essentials (free course on Skill Builder)
- See [resources.md](../resources.md) for recommended YouTube courses and podcasts to ingest via `knowledge_ingest.py`

---

## Progress Tracker

| Week | Days | Domains Covered | Practice Questions | Status |
|------|------|----------------|-------------------|--------|
| 1 | 1-7 | Domain 1, Domain 2 (partial) | D1: 20 questions | [ ] |
| 2 | 8-14 | Domain 2 (finish), Domain 3 (partial) | D2: 20 questions | [ ] |
| 3 | 15-21 | Domain 3 (finish), Domain 4 (all) | D3 + D4: 40 questions | [ ] |
| 4 | 22-28 | Full review + practice exams | All 80 re-attempted | [ ] |
