# Domain 4: Billing, Pricing, and Support -- Practice Questions

> 20 questions | Exam weight: 12% (~6 questions on the real exam)
> Format: Multiple choice (1 correct from 4) unless marked [Multiple Response]

---

### Q1. Data Transfer Pricing

Which of the following data transfers is FREE in AWS?

A. Data transfer from EC2 to the internet
B. Data transfer between AWS Regions
C. Data transfer INTO AWS from the internet
D. Data transfer between Availability Zones

**Answer: C**

> Inbound data transfer (into AWS from the internet) is always free. Outbound to internet, cross-Region, and cross-AZ transfers all incur charges.

---

### Q2. Free Tier Types

Which type of AWS Free Tier offer provides 750 hours per month of EC2 t2.micro usage for the first 12 months after account creation?

A. Always Free
B. 12 Months Free
C. Free Trials
D. Savings Plans

**Answer: B**

> The 12 Months Free tier provides services free for the first year after signing up. EC2 t2.micro (750 hrs/mo), S3 (5 GB), and RDS (750 hrs/mo) are examples. Always Free services never expire (e.g., Lambda 1M requests/mo). Trials are short-term.

---

### Q3. Cost Explorer

Which AWS tool allows you to visualize and analyze your AWS spending over time, with filters by service, Region, and tags?

A. AWS Budgets
B. AWS Cost Explorer
C. AWS Pricing Calculator
D. AWS Cost and Usage Report

**Answer: B**

> AWS Cost Explorer provides interactive charts to visualize, understand, and manage costs over time. It offers filtering by service, linked account, Region, and tags, plus spend forecasting. Budgets sets alerts. CUR provides raw CSV data. Pricing Calculator estimates future costs.

---

### Q4. AWS Budgets

A finance team wants to receive an email alert when their monthly AWS spending exceeds $1,000. Which tool should they use?

A. AWS Cost Explorer
B. AWS Budgets
C. AWS Pricing Calculator
D. AWS Trusted Advisor

**Answer: B**

> AWS Budgets lets you set custom cost and usage budgets with alert thresholds. You can receive email or SNS notifications when actual or forecasted spending exceeds your budget. Cost Explorer visualizes past spending but doesn't send alerts.

---

### Q5. Pricing Calculator

A startup wants to estimate the cost of running a web application on AWS BEFORE creating an account. Which tool should they use?

A. AWS Cost Explorer
B. AWS Billing Dashboard
C. AWS Pricing Calculator
D. AWS Cost and Usage Report

**Answer: C**

> AWS Pricing Calculator is a free, public tool that estimates costs for AWS services without needing an AWS account. It helps plan budgets before deployment. Cost Explorer and the Billing Dashboard require an active AWS account.

---

### Q6. Consolidated Billing

What is a benefit of using consolidated billing with AWS Organizations?

A. All accounts get free unlimited storage
B. Aggregated usage across accounts can qualify for volume pricing discounts
C. All accounts share the same IAM users
D. Reserved Instances cannot be shared across accounts

**Answer: B**

> Consolidated billing aggregates usage from all accounts in an Organization, which can qualify for volume pricing discounts (e.g., S3 tiered pricing). Additionally, Reserved Instances CAN be shared across accounts in the organization.

---

### Q7. Support Plans -- TAM

Which AWS Support plan provides a designated Technical Account Manager (TAM)?

A. Business
B. Enterprise On-Ramp
C. Enterprise
D. Developer

**Answer: C**

> Only the Enterprise plan ($15,000+/mo) provides a designated TAM. Enterprise On-Ramp ($5,500/mo) provides a pool of TAMs. Business and Developer do not include TAM access.

---

### Q8. Support Plans -- Response Times

A production system is down and causing business impact. Which AWS Support plan offers the fastest response time for critical system-down situations?

A. Developer (12-hour response)
B. Business (1-hour response)
C. Enterprise (15-minute response)
D. Basic (no technical support)

**Answer: C**

> Enterprise plan provides a 15-minute response time for critical/system-down situations. Business offers 1 hour for urgent production issues. Developer offers 12-24 hours. Basic provides no technical support cases.

---

### Q9. Trusted Advisor

Which of the following are categories checked by AWS Trusted Advisor? [Multiple Response -- select 3]

A. Cost Optimization
B. Application Performance
C. Security
D. Service Limits
E. Database Schema Design

**Answer: A, C, D**

> AWS Trusted Advisor checks five categories: Cost Optimization, Performance (not "Application Performance"), Security, Fault Tolerance, and Service Limits. It does not review database schema design.

---

### Q10. Trusted Advisor -- Basic Plan

Which Trusted Advisor checks are available on the Basic (free) support plan?

A. All checks across all five categories
B. Only 6 core security checks
C. Cost Optimization checks only
D. No Trusted Advisor access at all

**Answer: B**

> Basic and Developer plans get 6 core security checks: S3 bucket permissions, security groups (unrestricted access), IAM usage, MFA on root, EBS public snapshots, and RDS public snapshots. Full Trusted Advisor requires Business or Enterprise.

---

### Q11. Cost Allocation Tags

How can a company track AWS costs by department (e.g., Marketing, Engineering, Finance)?

A. Create separate AWS accounts for each department
B. Use cost allocation tags to label resources by department
C. Use AWS Config rules
D. Deploy resources in different Regions per department

**Answer: B**

> Cost allocation tags are key-value pairs attached to AWS resources. When activated, they appear in billing reports, allowing cost tracking by department, project, environment, or any custom category. Separate accounts work but tags are simpler.

---

### Q12. Reserved Instance Payment Options

Which Reserved Instance payment option provides the MAXIMUM cost savings?

A. No Upfront
B. Partial Upfront
C. All Upfront
D. Pay-as-you-go

**Answer: C**

> All Upfront provides the maximum discount because you pay the entire cost upfront. Partial Upfront has moderate savings. No Upfront has the least savings of the three RI options. Pay-as-you-go is On-Demand pricing (no savings).

---

### Q13. AWS Marketplace

Where can a customer find and purchase third-party software solutions that run on AWS, such as pre-configured AMIs and SaaS products?

A. AWS Partner Network
B. AWS Marketplace
C. AWS Service Catalog
D. AWS Solutions Library

**Answer: B**

> AWS Marketplace is a digital catalog of third-party software, AMIs, containers, SaaS applications, and professional services. Purchases are billed through the AWS account. Service Catalog is for internal governance of approved products.

---

### Q14. Support Plans -- Comparison

Which is the ONLY support plan that includes access to the Concierge Support Team for billing and account assistance?

A. Developer
B. Business
C. Enterprise On-Ramp
D. Enterprise

**Answer: D**

> The Concierge Support Team is exclusive to the Enterprise plan. They are billing and account specialists who provide personalized assistance. Enterprise On-Ramp does not include Concierge access.

---

### Q15. Cost and Usage Report

Which AWS tool provides the MOST detailed and granular billing data, including line-item details for every AWS charge?

A. AWS Cost Explorer
B. AWS Budgets
C. AWS Cost and Usage Report (CUR)
D. AWS Billing Dashboard

**Answer: C**

> The AWS Cost and Usage Report (CUR) provides the most comprehensive billing data. It includes line-item detail for every charge and can be delivered to S3 in CSV or Parquet format for analysis with Athena, QuickSight, or third-party tools.

---

### Q16. Always Free Tier

Which of the following AWS services offers an "Always Free" tier that never expires?

A. Amazon EC2 (750 hours t2.micro)
B. AWS Lambda (1 million requests per month)
C. Amazon RDS (750 hours)
D. Amazon S3 (5 GB)

**Answer: B**

> AWS Lambda offers 1 million free requests and 400,000 GB-seconds of compute per month, always free (no expiration). EC2 t2.micro, RDS, and S3 free tiers expire after 12 months.

---

### Q17. Savings Plans vs Reserved Instances

What advantage do Savings Plans offer over Reserved Instances?

A. Savings Plans are free
B. Savings Plans provide greater flexibility across instance families, Regions, and OS
C. Savings Plans require no commitment
D. Savings Plans provide a higher discount than Reserved Instances

**Answer: B**

> Savings Plans commit to a $/hour spend amount but offer flexibility -- they apply across instance families, sizes, Regions, OS, and tenancy. RIs are locked to a specific instance type and Region. Both offer similar discounts (up to 72%).

---

### Q18. AWS re:Post

Where can AWS customers ask technical questions and get answers from the AWS community and AWS staff?

A. AWS Artifact
B. AWS re:Post
C. AWS Health Dashboard
D. AWS Service Catalog

**Answer: B**

> AWS re:Post is a community-driven Q&A service (replacing the old AWS Forums). Customers can ask questions, search for answers, and get help from the community and AWS experts.

---

### Q19. Compute Optimizer

Which AWS tool provides recommendations for right-sizing EC2 instances based on actual utilization data?

A. AWS Trusted Advisor
B. AWS Compute Optimizer
C. AWS Cost Explorer
D. AWS Config

**Answer: B**

> AWS Compute Optimizer uses machine learning to analyze utilization metrics and recommend optimal EC2 instance types, EBS volume types, and Lambda function configurations. Trusted Advisor has basic right-sizing checks, but Compute Optimizer is more detailed.

---

### Q20. Pricing -- Cross-AZ Data Transfer

A company runs an application with EC2 instances in two different Availability Zones within the same Region. Is there a cost for data transfer between these instances?

A. No, all data transfer within a Region is free
B. Yes, there is a small charge for cross-AZ data transfer
C. Only if the instances are in different VPCs
D. Only if the data exceeds 1 TB

**Answer: B**

> Data transfer between Availability Zones within the same Region incurs a small charge (~$0.01/GB). Data transfer within the same AZ using private IP addresses is free. This is an important consideration when designing for high availability (multi-AZ).

---

## Score Tracker

| Attempt | Date | Score | Notes |
|---------|------|-------|-------|
| 1 | | /20 | |
| 2 | | /20 | |
| 3 | | /20 | |
