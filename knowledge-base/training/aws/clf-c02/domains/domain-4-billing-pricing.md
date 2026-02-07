# Domain 4: Billing, Pricing, and Support (12%)

> 3 task statements | ~6 questions on the exam
> **Smallest domain but straightforward -- free points if you study it**

## Task Statement 4.1: Compare AWS pricing models

### Core Pricing Principles

1. **Pay as you go** -- Pay only for what you consume, no upfront costs
2. **Pay less when you reserve** -- Commit for 1-3 years for significant discounts
3. **Pay less per unit by using more** -- Volume discounts (e.g., S3 storage tiers)
4. **Inbound data transfer is free** -- Data INTO AWS costs nothing
5. **Outbound data transfer is charged** -- Data OUT of AWS is metered

### Compute Pricing Models

| Model | Commitment | Savings | Best For |
|-------|-----------|---------|----------|
| **On-Demand** | None | 0% | Short-term, unpredictable, testing |
| **Reserved Instances (RI)** | 1 or 3 years, specific instance type | Up to 72% | Steady-state, predictable workloads |
| **Savings Plans** | 1 or 3 years, $/hour commitment | Up to 72% | Flexible compute (any instance family, Region, OS) |
| **Spot Instances** | None (can be interrupted with 2-min warning) | Up to 90% | Fault-tolerant, batch, CI/CD, big data |
| **Dedicated Hosts** | On-Demand or Reserved | Varies | Licensing compliance, regulatory |

### Reserved Instances Payment Options

| Option | Upfront | Monthly | Total Savings |
|--------|---------|---------|---------------|
| **All Upfront** | Full payment | $0 | Maximum savings |
| **Partial Upfront** | Some payment | Reduced | Medium savings |
| **No Upfront** | $0 | Higher | Minimum savings |

### Storage Pricing

- **S3**: Per GB stored + per request + data transfer out
- **EBS**: Per GB provisioned per month
- **EFS**: Per GB used per month
- **Glacier**: Per GB stored (very low) + retrieval fees

### Data Transfer Pricing

| Direction | Cost |
|-----------|------|
| Data IN to AWS | Free |
| Data OUT to internet | Charged per GB (tiered, decreasing) |
| Data between AZs | Small charge (~$0.01/GB) |
| Data between Regions | Charged per GB |
| Data within same AZ | Free (using private IPs) |

### AWS Free Tier

| Type | Description | Examples |
|------|-------------|---------|
| **Always Free** | Never expires | Lambda (1M requests/mo), DynamoDB (25 GB), CloudWatch (10 metrics) |
| **12 Months Free** | First year after signup | EC2 (750 hrs/mo t2.micro), S3 (5 GB), RDS (750 hrs/mo) |
| **Trials** | Short-term free trials | SageMaker, Inspector, GuardDuty (30-90 days) |

---

## Task Statement 4.2: Understand resources for billing, budget, and cost management

### Cost Management Tools

| Tool | Purpose |
|------|---------|
| **AWS Billing Dashboard** | Overview of current month charges, forecasts |
| **AWS Cost Explorer** | Visualize, understand, and manage costs over time. Filter by service, Region, tag. Forecast future spend. |
| **AWS Budgets** | Set custom cost and usage budgets. Get alerts when thresholds exceeded. |
| **AWS Cost and Usage Report (CUR)** | Most detailed cost data. CSV/Parquet for S3 delivery. Line-item granularity. |
| **AWS Pricing Calculator** | Estimate costs for new workloads BEFORE deploying. Public tool, no AWS account needed. |
| **Cost Allocation Tags** | Tag resources to categorize and track costs by project, team, or environment. |

### AWS Organizations -- Consolidated Billing

| Feature | Benefit |
|---------|---------|
| **Single bill** | One payment method for all accounts in the organization |
| **Volume discounts** | Aggregated usage across accounts qualifies for tiered pricing |
| **Reserved Instance sharing** | RIs purchased in one account can be shared across the organization |
| **Detailed billing** | See per-account breakdown while paying through management account |

### Cost Optimization Strategies

1. **Right-size instances** -- Use CloudWatch/Compute Optimizer to identify underutilized resources
2. **Use Reserved/Savings Plans** -- For predictable workloads
3. **Spot Instances** -- For fault-tolerant workloads
4. **Turn off unused resources** -- Dev/test environments off at night/weekends
5. **Use S3 lifecycle policies** -- Automatically move data to cheaper storage tiers
6. **Monitor with Cost Explorer** -- Review spend trends regularly
7. **Set Budgets and alerts** -- Catch unexpected spend early
8. **Use AWS Compute Optimizer** -- Recommendations for right-sizing EC2, EBS, Lambda

---

## Task Statement 4.3: Identify AWS technical resources and AWS Support options

### AWS Support Plans

| Feature | Basic (Free) | Developer ($29+) | Business ($100+) | Enterprise On-Ramp ($5,500) | Enterprise ($15,000+) |
|---------|-------------|------------------|------------------|---------------------------|---------------------|
| **Trusted Advisor** | 6 core checks | 6 core checks | All checks | All checks | All checks |
| **Support cases** | Account/billing only | 1 primary contact, technical | Unlimited contacts | Unlimited contacts | Unlimited contacts |
| **Severity / Response** | None | General: 24 hrs, System impaired: 12 hrs | General: 24 hrs, Urgent: 1 hr, Critical: 15 min | Critical: 30 min | Critical: 15 min |
| **TAM** | No | No | No | Pool of TAMs | Designated TAM |
| **Concierge** | No | No | No | No | Yes |
| **Architecture review** | None | General guidance | Contextual | Consultative review | Consultative + Well-Architected |
| **Training** | Self-paced | Self-paced | Self-paced | Self-paced | Online labs included |
| **3rd-party software** | No | No | Yes | Yes | Yes |
| **Proactive programs** | No | No | No | Some | Infrastructure Event Management, Ops Reviews |

### Key Terms

- **TAM (Technical Account Manager)**: Dedicated AWS expert who provides proactive guidance. Enterprise On-Ramp = pool, Enterprise = designated.
- **Concierge Support Team**: Billing and account specialists. Enterprise only.
- **Infrastructure Event Management (IEM)**: AWS helps plan for major events (product launches, migrations). Business (extra fee) or Enterprise (included).

### AWS Trusted Advisor

Five categories of checks:
1. **Cost Optimization** -- Idle resources, underutilized instances, unassociated EIPs
2. **Performance** -- Over-utilized instances, CloudFront optimization
3. **Security** -- Open security groups, IAM key rotation, MFA on root
4. **Fault Tolerance** -- AZ balance, RDS backups, EBS snapshots
5. **Service Limits** -- Approaching service quotas

Basic/Developer plans: Only 6 core security checks.
Business/Enterprise plans: All checks + API access.

### Additional Resources

| Resource | Purpose |
|----------|---------|
| **AWS re:Post** | Community-driven Q&A (replaced AWS Forums) |
| **AWS Partner Network (APN)** | Find AWS-certified consulting and technology partners |
| **AWS Professional Services** | AWS team helps with migrations, implementations |
| **AWS Marketplace** | Third-party software (AMIs, SaaS, containers). One-click deploy. |
| **AWS Training and Certification** | Official courses, labs, and certification exams |
| **AWS Whitepapers** | Deep-dive technical documents (Well-Architected, security, migration) |
| **AWS Documentation** | Service-specific guides and API references |
| **AWS Solutions Library** | Vetted architecture patterns and reference implementations |

---

## Practice Focus

- **Pricing models** -- Know On-Demand vs. Reserved vs. Spot vs. Savings Plans and when to use each
- **Free Tier** -- 3 types (Always Free, 12-Month, Trials) and key services
- **Support Plans** -- Know the 5 plans, key differences (TAM, response times, Trusted Advisor access)
- **Cost tools** -- Cost Explorer (visualize), Budgets (alerts), CUR (detailed export), Pricing Calculator (estimate)
- **Consolidated Billing** -- Benefits of Organizations (volume discounts, RI sharing)
- **Data Transfer** -- Inbound = free, outbound = charged, cross-AZ = small charge
