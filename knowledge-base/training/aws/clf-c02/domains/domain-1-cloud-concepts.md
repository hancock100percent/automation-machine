# Domain 1: Cloud Concepts (24%)

> 3 task statements | ~12 questions on the exam

## Task Statement 1.1: Define the benefits of the AWS Cloud

### Why Cloud?

The cloud replaces upfront capital expense (CapEx) with variable operational expense (OpEx). You pay only for what you use.

### Six Advantages of Cloud Computing

1. **Trade fixed expense for variable expense** -- No large upfront hardware purchases. Pay only for consumed resources.
2. **Benefit from massive economies of scale** -- AWS aggregates usage from hundreds of thousands of customers, achieving lower pay-as-you-go prices.
3. **Stop guessing capacity** -- Scale up or down based on actual demand, eliminating costly over-provisioning or performance-limiting under-provisioning.
4. **Increase speed and agility** -- New IT resources are a click away. Reduce time to make resources available from weeks to minutes.
5. **Stop spending money running data centers** -- Focus on projects that differentiate your business, not infrastructure.
6. **Go global in minutes** -- Deploy applications in multiple AWS Regions around the world with a few clicks.

### Cloud Computing Models

| Model | What You Manage | Examples |
|-------|----------------|---------|
| **IaaS** (Infrastructure as a Service) | OS, runtime, app, data | EC2, VPC |
| **PaaS** (Platform as a Service) | App, data | Elastic Beanstalk, Lambda |
| **SaaS** (Software as a Service) | Nothing (just use it) | Gmail, Salesforce |

### Cloud Deployment Models

| Model | Description |
|-------|-------------|
| **Public Cloud** | All resources on AWS (or another cloud provider) |
| **Private Cloud (On-Premises)** | Resources deployed on-premises using virtualization (e.g., VMware) |
| **Hybrid Cloud** | Mix of public cloud + on-premises. Connected via VPN or Direct Connect |

### Total Cost of Ownership (TCO)

Cloud reduces TCO by eliminating:
- Server hardware purchase and maintenance
- Data center space, power, and cooling
- IT staff for physical infrastructure
- Over-provisioned capacity sitting idle

AWS tool: **AWS Pricing Calculator** -- estimate cloud costs before migrating.

---

## Task Statement 1.2: Identify design principles of the AWS Cloud

### Well-Architected Framework (6 Pillars)

| Pillar | Focus | Key Question |
|--------|-------|-------------|
| Operational Excellence | Automate operations, respond to events | "How do you evolve and improve?" |
| Security | Protect data, systems, assets | "How do you protect information?" |
| Reliability | Recover from disruptions, meet demand | "How do you prevent and recover from failures?" |
| Performance Efficiency | Use resources efficiently | "How do you select the right resource types?" |
| Cost Optimization | Avoid unnecessary costs | "How do you manage and reduce costs?" |
| Sustainability | Minimize environmental impact | "How do you reduce the environmental impact?" |

### Design Principles

- **Design for failure** -- Everything fails eventually. Use multi-AZ, auto-scaling, health checks.
- **Decouple components** -- Use SQS, SNS, EventBridge to separate services so one failure doesn't cascade.
- **Implement elasticity** -- Auto Scaling groups to match capacity to demand.
- **Think parallel** -- Distribute workloads across multiple instances.
- **Stop guessing capacity** -- Use auto-scaling instead of static provisioning.
- **Automate everything** -- CloudFormation, CDK, Systems Manager for infrastructure and operations.

### AWS Well-Architected Tool

Free tool in the AWS Console that reviews your workloads against the 6 pillars and provides improvement recommendations.

---

## Task Statement 1.3: Understand the benefits of and strategies for migration to the AWS Cloud

### The 6 R's of Migration

| Strategy | Description | Example |
|----------|-------------|---------|
| **Rehost** ("Lift and shift") | Move as-is to cloud | VM to EC2 |
| **Replatform** ("Lift, tinker, and shift") | Minor optimizations during migration | MySQL on EC2 to RDS |
| **Refactor** (Re-architect) | Redesign using cloud-native features | Monolith to microservices on Lambda |
| **Repurchase** | Switch to a different product (often SaaS) | On-prem CRM to Salesforce |
| **Retire** | Turn off things you no longer need | Decommission legacy apps |
| **Retain** | Keep on-premises (not ready to migrate) | Complex legacy with dependencies |

### AWS Cloud Adoption Framework (AWS CAF)

Organizes guidance into 6 perspectives:

| Perspective | Stakeholders | Focus |
|-------------|-------------|-------|
| Business | Business managers, finance | Ensuring cloud investments align with business goals |
| People | HR, staffing | Organizational change management, training |
| Governance | CIO, program managers | Governance, risk, compliance |
| Platform | CTO, engineers | Cloud platform architecture |
| Security | CISO, security team | Security controls and compliance |
| Operations | IT ops, support | Cloud operations and monitoring |

### Migration Tools

| Tool | Purpose |
|------|---------|
| **AWS Migration Hub** | Central place to track migration progress across tools |
| **AWS Application Migration Service** | Automates lift-and-shift migrations (formerly CloudEndure) |
| **AWS Database Migration Service (DMS)** | Migrate databases with minimal downtime. Supports homogeneous and heterogeneous migrations |
| **AWS Snow Family** | Physical devices for offline bulk data transfer |

### AWS Snow Family

| Device | Storage | Use Case |
|--------|---------|----------|
| **Snowcone** | 8-14 TB | Edge computing, small data transfer |
| **Snowball Edge** | 80 TB | Large-scale data transfer, edge computing |
| **Snowmobile** | 100 PB | Exabyte-scale data center migrations |

---

## Key Terms to Know

| Term | Definition |
|------|-----------|
| **Elasticity** | Ability to scale resources up/down automatically based on demand |
| **High Availability** | System designed to be operational and accessible with minimal downtime |
| **Fault Tolerance** | System continues operating even when components fail |
| **Scalability** | Ability to handle increased load (vertical = bigger instance, horizontal = more instances) |
| **Agility** | Speed at which cloud resources can be provisioned and deployed |
| **CapEx** | Capital Expenditure -- upfront investment in physical assets |
| **OpEx** | Operational Expenditure -- ongoing pay-as-you-go costs |
| **TCO** | Total Cost of Ownership -- full cost of owning and operating infrastructure |

---

## Practice Focus

- Be able to explain WHY cloud vs. on-premises (cost, agility, scale)
- Know all 6 advantages by heart
- Understand the 6 R's and when to use each
- Know the Well-Architected pillars (all 6) and what each addresses
- Understand IaaS vs. PaaS vs. SaaS boundaries
