# Domain 1: Cloud Concepts -- Practice Questions

> 20 questions | Exam weight: 24% (~12 questions on the real exam)
> Format: Multiple choice (1 correct from 4) unless marked [Multiple Response]

---

### Q1. Six Advantages of Cloud

A company is considering migrating to the cloud. Which of the following is one of the six advantages of cloud computing as defined by AWS?

A. Guaranteed 100% uptime SLA for all services
B. Benefit from massive economies of scale
C. Complete elimination of all security responsibilities
D. Free unlimited data storage

**Answer: B**

> AWS aggregates usage from hundreds of thousands of customers, achieving lower variable costs than any single company could on its own. This is one of the official six advantages. A is incorrect (no 100% SLA), C is incorrect (shared responsibility model), D is incorrect (storage is metered).

---

### Q2. CapEx vs OpEx

What financial benefit does cloud computing offer compared to traditional on-premises infrastructure?

A. Cloud computing requires a larger upfront capital investment
B. Cloud computing replaces variable expenses with fixed expenses
C. Cloud computing replaces upfront capital expenses with variable operational expenses
D. Cloud computing eliminates all IT costs

**Answer: C**

> Cloud shifts from CapEx (buying servers upfront) to OpEx (pay for what you consume). B has it reversed. A and D are incorrect.

---

### Q3. Cloud Deployment Models

A healthcare company must keep sensitive patient data within its own data center for regulatory reasons but wants to use AWS for its web application front-end. Which cloud deployment model should they use?

A. Public cloud
B. Private cloud
C. Hybrid cloud
D. Community cloud

**Answer: C**

> Hybrid cloud combines on-premises (private) infrastructure with public cloud. The company keeps data on-premises for compliance while using AWS for the application layer.

---

### Q4. IaaS vs PaaS vs SaaS

Which cloud computing model gives the customer the MOST control over the underlying infrastructure?

A. SaaS
B. PaaS
C. IaaS
D. FaaS

**Answer: C**

> IaaS (Infrastructure as a Service) gives customers control over OS, runtime, middleware, and data. Examples include EC2. PaaS manages the platform; SaaS manages everything. FaaS (Function as a Service) like Lambda manages all infrastructure.

---

### Q5. Elasticity

A retail company experiences a 10x traffic spike during Black Friday but normal traffic the rest of the year. Which cloud benefit BEST addresses this scenario?

A. High availability
B. Fault tolerance
C. Elasticity
D. Durability

**Answer: C**

> Elasticity is the ability to automatically scale resources up and down based on demand. Auto Scaling handles the Black Friday spike and then scales back, so the company only pays for what it uses.

---

### Q6. Well-Architected Framework

Which pillar of the AWS Well-Architected Framework focuses on the ability to recover from infrastructure or service failures and dynamically acquire resources to meet demand?

A. Operational Excellence
B. Security
C. Reliability
D. Performance Efficiency

**Answer: C**

> Reliability focuses on recovering from disruptions, meeting demand through scaling, and mitigating issues like misconfigurations. It covers fault tolerance, disaster recovery, and scaling.

---

### Q7. Economies of Scale

How does AWS achieve lower per-unit costs compared to individual companies running their own data centers?

A. AWS uses lower-quality hardware
B. AWS aggregates demand from many customers to negotiate better prices
C. AWS does not provide customer support
D. AWS only operates in one geographic region

**Answer: B**

> Massive economies of scale mean AWS's combined purchasing power across hundreds of thousands of customers results in lower pay-as-you-go prices.

---

### Q8. Migration -- 6 R's

A company decides to move its on-premises MySQL database to Amazon RDS without re-architecting the application. Which migration strategy does this BEST represent?

A. Rehost
B. Replatform
C. Refactor
D. Repurchase

**Answer: B**

> Replatforming ("lift, tinker, and shift") makes minor optimizations during migration. Moving MySQL from a self-managed server to managed RDS is replatforming -- the database engine stays the same but the hosting platform changes. Rehost would be moving MySQL to EC2 as-is. Refactor would mean re-architecting to DynamoDB or Aurora.

---

### Q9. Migration -- Retire Strategy

During a migration assessment, a team discovers several legacy applications that are no longer used by anyone. Which migration strategy is MOST appropriate?

A. Rehost
B. Retain
C. Retire
D. Repurchase

**Answer: C**

> Retire means decommissioning applications that are no longer needed. There is no point in migrating unused applications.

---

### Q10. Well-Architected -- Sustainability

Which Well-Architected Framework pillar was added most recently and focuses on minimizing the environmental impact of running cloud workloads?

A. Cost Optimization
B. Operational Excellence
C. Sustainability
D. Reliability

**Answer: C**

> Sustainability was added as the 6th pillar. It focuses on reducing the environmental impact of cloud workloads, including energy efficiency and resource utilization.

---

### Q11. Cloud Adoption Framework (CAF)

Which perspective of the AWS Cloud Adoption Framework (CAF) is primarily concerned with organizational change management and staff training?

A. Business
B. People
C. Governance
D. Platform

**Answer: B**

> The People perspective focuses on HR, staffing, organizational change management, and training to ensure the workforce can adopt cloud technologies.

---

### Q12. Snow Family

A company needs to migrate 80 TB of data from an on-premises data center to AWS, but their internet connection is too slow. Which AWS service should they use?

A. AWS Direct Connect
B. AWS Snowball Edge
C. AWS DataSync
D. AWS Storage Gateway

**Answer: B**

> AWS Snowball Edge can hold up to 80 TB and is a physical device shipped to the customer for offline bulk data transfer. While Direct Connect provides a dedicated connection, it would still take significant time for 80 TB. Snowball is the right choice for one-time large data transfers.

---

### Q13. AWS Migration Hub

Which AWS service provides a single place to track the progress of application migrations across multiple AWS and partner tools?

A. AWS CloudFormation
B. AWS Migration Hub
C. AWS Config
D. AWS Systems Manager

**Answer: B**

> AWS Migration Hub provides a central location to track migrations across AWS Application Migration Service, AWS DMS, and other tools.

---

### Q14. Design Principles -- Decouple

A solutions architect wants to ensure that a failure in one component of an application does not cascade to other components. Which design principle should they apply?

A. Think parallel
B. Implement elasticity
C. Decouple components
D. Design for single AZ

**Answer: C**

> Decoupling components using services like SQS, SNS, or EventBridge ensures that failures in one component don't cascade to others. Each component operates independently.

---

### Q15. Agility

What does "agility" mean in the context of cloud computing?

A. The speed at which resources can be provisioned and deployed
B. The ability to recover from failures
C. The durability of stored data
D. The physical security of data centers

**Answer: A**

> Agility refers to the speed at which cloud resources can be made available -- reducing provisioning time from weeks to minutes, enabling rapid experimentation and innovation.

---

### Q16. Scalability Types

What is the difference between vertical scaling and horizontal scaling?

A. Vertical scaling adds more instances; horizontal scaling increases instance size
B. Vertical scaling increases instance size; horizontal scaling adds more instances
C. Vertical scaling is cloud-only; horizontal scaling is on-premises only
D. They are the same concept

**Answer: B**

> Vertical scaling (scale up) means increasing the size of a single resource (e.g., upgrading from t3.small to t3.xlarge). Horizontal scaling (scale out) means adding more instances of the same resource.

---

### Q17. Total Cost of Ownership

Which of the following costs are ELIMINATED when migrating to the AWS Cloud? [Multiple Response -- select 2]

A. Application licensing costs
B. Data center power and cooling costs
C. Staff costs for managing physical servers
D. Database query costs
E. Network bandwidth costs

**Answer: B, C**

> Cloud eliminates data center operational costs (power, cooling, physical space) and reduces the need for staff who manage physical infrastructure. Application licensing, database queries, and network bandwidth still have costs in the cloud.

---

### Q18. Fault Tolerance vs High Availability

What is the PRIMARY difference between fault tolerance and high availability?

A. They are the same concept
B. High availability minimizes downtime; fault tolerance ensures zero downtime during failures
C. Fault tolerance is cheaper to implement
D. High availability only applies to databases

**Answer: B**

> High availability ensures the system is operational most of the time (e.g., 99.99% uptime). Fault tolerance means the system continues operating without interruption even when components fail (zero downtime). Fault tolerance is more robust but more expensive to implement.

---

### Q19. Rehost Migration

A company wants to migrate its applications to AWS as quickly as possible with minimal changes to the existing architecture. Which migration strategy should they use?

A. Refactor
B. Repurchase
C. Rehost
D. Replatform

**Answer: C**

> Rehost ("lift and shift") moves applications as-is to the cloud with no code changes. It is the fastest migration strategy. Refactor requires re-architecting. Replatform makes some changes. Repurchase means switching to a different product.

---

### Q20. Stop Guessing Capacity

A company traditionally buys servers to handle their peak traffic of 100,000 users, but most days they only have 10,000 users. Which cloud advantage DIRECTLY solves this problem?

A. Go global in minutes
B. Stop guessing capacity
C. Trade fixed expense for variable expense
D. Benefit from massive economies of scale

**Answer: B**

> "Stop guessing capacity" means using auto-scaling to match resources to actual demand. The company no longer needs to buy for peak capacity and waste money on idle resources during normal traffic. While C is related (pay-as-you-go), the direct advantage addressing capacity planning is B.

---

## Score Tracker

| Attempt | Date | Score | Notes |
|---------|------|-------|-------|
| 1 | | /20 | |
| 2 | | /20 | |
| 3 | | /20 | |
