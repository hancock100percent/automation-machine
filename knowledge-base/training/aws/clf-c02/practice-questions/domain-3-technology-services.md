# Domain 3: Cloud Technology and Services -- Practice Questions

> 20 questions | Exam weight: 34% (~17 questions on the real exam)
> Format: Multiple choice (1 correct from 4) unless marked [Multiple Response]

---

### Q1. EC2 Pricing -- Spot Instances

A research team needs to run a large batch computation job that can tolerate interruptions. Which EC2 pricing model offers the highest discount?

A. On-Demand
B. Reserved Instances
C. Spot Instances
D. Dedicated Hosts

**Answer: C**

> Spot Instances offer up to 90% savings by using spare AWS capacity. They can be interrupted with a 2-minute warning, making them ideal for fault-tolerant workloads like batch processing, data analysis, and CI/CD. Reserved Instances offer up to 72% but require a commitment.

---

### Q2. EC2 Pricing -- Reserved vs On-Demand

A company runs a web application server 24/7 with predictable, steady traffic. Which pricing model is MOST cost-effective?

A. On-Demand
B. Spot Instances
C. Reserved Instances or Savings Plans
D. Dedicated Hosts

**Answer: C**

> For steady-state, predictable workloads running continuously, Reserved Instances or Savings Plans provide up to 72% savings with a 1-3 year commitment. On-Demand has no discount. Spot can be interrupted. Dedicated Hosts are for compliance/licensing needs.

---

### Q3. S3 Storage Classes

A company needs to store backup data that is accessed once or twice a year but must be retrieved within minutes when needed. Which S3 storage class is MOST cost-effective?

A. S3 Standard
B. S3 Standard-IA (Infrequent Access)
C. S3 Glacier Deep Archive
D. S3 One Zone-IA

**Answer: B**

> S3 Standard-IA is designed for infrequently accessed data with rapid retrieval (milliseconds). It costs less than Standard but has a retrieval fee. Glacier Deep Archive takes 12-48 hours to retrieve, too slow for "within minutes." One Zone-IA lacks multi-AZ resilience.

---

### Q4. S3 Glacier Deep Archive

Which S3 storage class provides the lowest cost but takes 12-48 hours for data retrieval?

A. S3 Glacier Flexible Retrieval
B. S3 Glacier Deep Archive
C. S3 Standard-IA
D. S3 Intelligent-Tiering

**Answer: B**

> S3 Glacier Deep Archive is the lowest-cost storage class, designed for long-term data archiving with retrieval times of 12-48 hours. It is ideal for compliance archives and data you may never need to access but must retain.

---

### Q5. Lambda

A developer needs to run a function that processes an image upload to S3 and completes within 30 seconds. The function runs infrequently (a few times per day). Which service is MOST appropriate?

A. Amazon EC2
B. AWS Lambda
C. Amazon ECS
D. AWS Elastic Beanstalk

**Answer: B**

> AWS Lambda is ideal for short-duration, event-driven workloads. It runs code without provisioning servers, scales automatically, and charges per invocation and duration. Running an EC2 instance 24/7 for a few invocations per day would be wasteful.

---

### Q6. RDS vs DynamoDB

A developer needs a database for an e-commerce application that requires complex SQL queries with joins across multiple tables. Which database service is MOST appropriate?

A. Amazon DynamoDB
B. Amazon RDS
C. Amazon ElastiCache
D. Amazon Redshift

**Answer: B**

> Amazon RDS is a managed relational database supporting SQL, joins, transactions, and complex queries. DynamoDB is NoSQL (key-value) and does not support joins. ElastiCache is for caching. Redshift is for analytics/data warehousing, not transactional workloads.

---

### Q7. DynamoDB

Which AWS database service is a fully managed NoSQL database that provides single-digit millisecond performance at any scale?

A. Amazon RDS
B. Amazon Aurora
C. Amazon DynamoDB
D. Amazon Neptune

**Answer: C**

> Amazon DynamoDB is a serverless, fully managed NoSQL database offering consistent single-digit millisecond performance. It scales automatically with no capacity planning needed. RDS and Aurora are relational. Neptune is a graph database.

---

### Q8. CloudFront

A company wants to reduce latency for users accessing their website globally by caching content closer to end users. Which AWS service should they use?

A. Amazon Route 53
B. Amazon CloudFront
C. AWS Global Accelerator
D. Elastic Load Balancing

**Answer: B**

> Amazon CloudFront is a CDN that caches content at 400+ Edge Locations worldwide. It reduces latency by serving content from the location closest to the user. Route 53 is DNS. Global Accelerator routes traffic over AWS backbone but doesn't cache content.

---

### Q9. VPC

What is an Amazon VPC?

A. A physical data center
B. An isolated virtual network in the AWS Cloud
C. A type of EC2 instance
D. A DNS service

**Answer: B**

> An Amazon Virtual Private Cloud (VPC) is a logically isolated section of the AWS Cloud where you launch resources in a virtual network you define, with control over IP ranges, subnets, route tables, and gateways.

---

### Q10. Infrastructure as Code

Which AWS service allows you to define cloud infrastructure using JSON or YAML templates and provision resources repeatably?

A. AWS CodePipeline
B. AWS CloudFormation
C. Amazon CloudWatch
D. AWS Config

**Answer: B**

> AWS CloudFormation uses declarative JSON/YAML templates to provision and manage infrastructure as code. Templates are version-controlled and repeatable. CodePipeline is for CI/CD. CloudWatch is monitoring. Config tracks resource configuration.

---

### Q11. Regions and Availability Zones

What is the MINIMUM number of Availability Zones in an AWS Region?

A. 1
B. 2
C. 3
D. 5

**Answer: B**

> Every AWS Region has a minimum of 2 Availability Zones (most have 3 or more). Each AZ consists of one or more discrete data centers with redundant power, networking, and connectivity.

---

### Q12. Elastic Load Balancing

A web application needs to distribute incoming HTTP/HTTPS traffic across multiple EC2 instances. Which type of load balancer is MOST appropriate?

A. Network Load Balancer (NLB)
B. Application Load Balancer (ALB)
C. Gateway Load Balancer (GLB)
D. Classic Load Balancer

**Answer: B**

> ALB operates at Layer 7 (HTTP/HTTPS) and is designed for web applications. It supports path-based routing, host-based routing, and WebSocket. NLB operates at Layer 4 (TCP/UDP) for ultra-high performance. GLB is for third-party network appliances.

---

### Q13. SQS

A microservices architecture needs a way to decouple components so that if one service goes down, messages are not lost. Which service should they use?

A. Amazon SNS
B. Amazon SQS
C. Amazon Kinesis
D. Amazon EventBridge

**Answer: B**

> Amazon SQS (Simple Queue Service) is a fully managed message queue that decouples components. Messages persist in the queue until processed, so if a consumer goes down, messages are retained. SNS is pub/sub (push-based, no persistence). Kinesis is for real-time streaming. EventBridge is an event bus.

---

### Q14. Serverless Services

Which of the following AWS services are serverless? [Multiple Response -- select 3]

A. Amazon EC2
B. AWS Lambda
C. Amazon DynamoDB
D. Amazon EBS
E. Amazon S3

**Answer: B, C, E**

> Lambda (compute), DynamoDB (database), and S3 (storage) are all serverless -- no servers to manage, automatic scaling, pay-per-use. EC2 requires managing instances. EBS is block storage attached to EC2 instances.

---

### Q15. Route 53

Which AWS service provides domain name registration and DNS routing?

A. Amazon CloudFront
B. Amazon Route 53
C. AWS Direct Connect
D. Amazon API Gateway

**Answer: B**

> Amazon Route 53 is a scalable DNS web service. It provides domain name registration, DNS routing (simple, weighted, latency, failover, geolocation), and health checking. CloudFront is CDN. Direct Connect is a dedicated network connection.

---

### Q16. Amazon Aurora

What advantage does Amazon Aurora have over standard Amazon RDS MySQL?

A. Aurora is NoSQL
B. Aurora provides up to 5x the throughput of standard MySQL on RDS
C. Aurora is free
D. Aurora does not require a VPC

**Answer: B**

> Amazon Aurora is MySQL and PostgreSQL compatible but provides up to 5x MySQL throughput and 3x PostgreSQL throughput with high availability (6 copies of data across 3 AZs). It is still a relational database, not free, and runs in a VPC.

---

### Q17. Amazon Bedrock

Which AWS service provides access to foundation models (like Claude) for building generative AI applications?

A. Amazon SageMaker
B. Amazon Rekognition
C. Amazon Bedrock
D. Amazon Comprehend

**Answer: C**

> Amazon Bedrock provides serverless access to foundation models from Anthropic (Claude), AI21, Cohere, Meta, Stability AI, and Amazon (Titan). SageMaker is for building custom ML models. Rekognition is computer vision. Comprehend is NLP.

---

### Q18. Direct Connect

A company needs a dedicated, private network connection from its on-premises data center to AWS that does NOT traverse the public internet. Which service should they use?

A. VPN
B. AWS Direct Connect
C. VPC Peering
D. AWS Transit Gateway

**Answer: B**

> AWS Direct Connect provides a dedicated private network connection from on-premises to AWS. It does not go over the public internet, providing more consistent network performance and lower latency. VPN is encrypted but uses the public internet.

---

### Q19. CloudWatch

Which AWS service provides monitoring, logging, and alerting for AWS resources and applications?

A. AWS CloudTrail
B. Amazon CloudWatch
C. AWS Config
D. AWS X-Ray

**Answer: B**

> Amazon CloudWatch collects metrics, logs, and events for monitoring and observability. It creates alarms, dashboards, and automated actions. CloudTrail logs API calls (auditing). Config tracks resource configurations. X-Ray traces distributed applications.

---

### Q20. Containers -- Fargate

A team wants to run Docker containers without managing the underlying EC2 instances. Which service should they use?

A. Amazon ECS on EC2
B. AWS Fargate
C. AWS Elastic Beanstalk
D. Amazon Lightsail

**Answer: B**

> AWS Fargate is a serverless compute engine for containers. It works with ECS and EKS, eliminating the need to manage EC2 instances. You define the container and Fargate handles the infrastructure. ECS on EC2 requires managing instances.

---

## Score Tracker

| Attempt | Date | Score | Notes |
|---------|------|-------|-------|
| 1 | | /20 | |
| 2 | | /20 | |
| 3 | | /20 | |
