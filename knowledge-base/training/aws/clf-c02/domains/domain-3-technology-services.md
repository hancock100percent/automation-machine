# Domain 3: Cloud Technology and Services (34%)

> 4 task statements | ~17 questions on the exam
> **Largest domain -- know your services**

## Task Statement 3.1: Define methods of deploying and operating in the AWS Cloud

### Ways to Access AWS

| Method | Description | Use Case |
|--------|-------------|----------|
| **AWS Management Console** | Web-based GUI | Visual management, exploring services |
| **AWS CLI** | Command-line tool | Scripting, automation |
| **AWS SDKs** | Language-specific libraries (Python boto3, JS, Java, etc.) | Application integration |
| **AWS CloudShell** | Browser-based shell (pre-authenticated) | Quick CLI access without local setup |
| **AWS APIs** | REST API calls | Direct programmatic access |

### Infrastructure as Code (IaC)

| Service | Description |
|---------|-------------|
| **AWS CloudFormation** | Declarative templates (JSON/YAML) to provision infrastructure. Repeatable, version-controlled. |
| **AWS CDK** | Define infrastructure using programming languages (TypeScript, Python, Java). Compiles to CloudFormation. |
| **AWS Elastic Beanstalk** | PaaS -- upload code, it handles provisioning, load balancing, scaling, monitoring. |

### Deployment Models

| Model | Description | Use Case |
|-------|-------------|----------|
| **Single AZ** | Resources in one Availability Zone | Dev/test, non-critical |
| **Multi-AZ** | Resources spread across 2+ AZs in one Region | Production, high availability |
| **Multi-Region** | Resources in multiple Regions | Global apps, disaster recovery |

### Connectivity

| Service | Description |
|---------|-------------|
| **Internet Gateway** | Connect VPC to the public internet |
| **NAT Gateway** | Let private subnet resources access internet (outbound only) |
| **VPN** | Encrypted tunnel from on-premises to AWS over the internet |
| **AWS Direct Connect** | Dedicated private network connection from on-premises to AWS (not over internet) |
| **VPC Peering** | Connect two VPCs directly (no transitive routing) |
| **AWS Transit Gateway** | Hub for connecting multiple VPCs and on-premises networks |

---

## Task Statement 3.2: Define the AWS global infrastructure

### Core Concepts

| Concept | Description | Count (approx.) |
|---------|-------------|-----------------|
| **Region** | Geographic area with 2+ AZs. Completely independent. | 30+ |
| **Availability Zone (AZ)** | One or more discrete data centers with redundant power, networking, connectivity. | 90+ |
| **Edge Location** | CDN endpoint for CloudFront. Closest to end users. | 400+ |
| **Local Zone** | Extension of a Region closer to users for latency-sensitive apps. | 30+ |
| **Wavelength Zone** | AWS infrastructure embedded in 5G carrier networks. | Select locations |

### Choosing a Region

Consider these factors:
1. **Compliance** -- Data sovereignty requirements (GDPR = EU Region)
2. **Latency** -- Closer to users = lower latency
3. **Service availability** -- Not all services available in all Regions
4. **Pricing** -- Costs vary by Region (US East is usually cheapest)

### Content Delivery and DNS

| Service | Purpose |
|---------|---------|
| **Amazon CloudFront** | CDN. Caches content at Edge Locations for low latency delivery. Works with S3, EC2, ALB. |
| **Amazon Route 53** | DNS service. Domain registration, routing policies (simple, weighted, latency, failover, geolocation). |
| **AWS Global Accelerator** | Routes traffic through AWS global network (not public internet) for improved performance. Static IP endpoints. |

### Extending AWS

| Service | Purpose |
|---------|---------|
| **AWS Outposts** | AWS infrastructure and services on-premises. Same APIs, tools, hardware. |
| **AWS Local Zones** | Run latency-sensitive workloads closer to end users. |
| **AWS Wavelength** | Ultra-low-latency apps on 5G mobile networks. |

---

## Task Statement 3.3: Identify AWS compute services

### Compute Services Overview

| Service | Type | Best For |
|---------|------|----------|
| **Amazon EC2** | Virtual machines | Full control, any workload |
| **AWS Lambda** | Serverless functions | Event-driven, short tasks (<15 min) |
| **Amazon ECS** | Container orchestration (AWS-native) | Docker containers |
| **Amazon EKS** | Container orchestration (Kubernetes) | Kubernetes workloads |
| **AWS Fargate** | Serverless containers | Containers without managing servers |
| **AWS Elastic Beanstalk** | PaaS | Quick deployments, web apps |
| **AWS Lightsail** | Simplified VPS | Simple websites, small apps |
| **AWS Batch** | Batch processing | Large-scale parallel jobs |
| **AWS App Runner** | Managed container service | Deploy from source code or container image |

### Amazon EC2 Deep Dive

**Instance types** (know the categories):
| Family | Optimized For | Example Use |
|--------|--------------|-------------|
| **General Purpose** (M, T) | Balanced compute/memory/networking | Web servers, code repos |
| **Compute Optimized** (C) | High-performance processors | Batch processing, ML inference, gaming |
| **Memory Optimized** (R, X) | Large in-memory datasets | In-memory databases, real-time analytics |
| **Storage Optimized** (I, D, H) | High sequential read/write to local storage | Data warehousing, distributed file systems |
| **Accelerated Computing** (P, G, Inf) | GPU/hardware accelerators | ML training, video encoding, HPC |

**EC2 Pricing Models:**
| Model | Description | Savings | Commitment |
|-------|-------------|---------|------------|
| **On-Demand** | Pay by hour/second. No commitment. | 0% (baseline) | None |
| **Reserved Instances** | 1 or 3 year commitment for specific instance type. | Up to 72% | 1-3 years |
| **Savings Plans** | Commit to $/hour spend. Flexible instance types. | Up to 72% | 1-3 years |
| **Spot Instances** | Bid on spare capacity. Can be interrupted. | Up to 90% | None (can be revoked) |
| **Dedicated Hosts** | Physical server dedicated to you. | Varies | On-Demand or Reserved |

**When to use which pricing:**
- Steady-state workloads = Reserved / Savings Plans
- Flexible, fault-tolerant workloads = Spot
- Short-term, unpredictable = On-Demand
- Compliance/licensing requirements = Dedicated Hosts

### Auto Scaling

| Component | Purpose |
|-----------|---------|
| **Launch Template** | Defines instance configuration (AMI, type, key pair) |
| **Auto Scaling Group** | Manages fleet of EC2 instances. Min/max/desired capacity. |
| **Scaling Policies** | Target tracking, step, simple, scheduled, predictive |
| **Elastic Load Balancer** | Distributes traffic across instances |

### Serverless vs. Server-Based

| Aspect | Serverless (Lambda) | Server-Based (EC2) |
|--------|-------------------|-------------------|
| Management | No servers to manage | You manage OS, patching |
| Scaling | Automatic, per-request | Manual or Auto Scaling Groups |
| Pricing | Per invocation + duration | Per hour/second running |
| Max runtime | 15 minutes | Unlimited |
| State | Stateless | Stateful possible |

---

## Task Statement 3.4: Identify AWS services for other key areas

### Storage Services

| Service | Type | Use Case | Durability |
|---------|------|----------|------------|
| **Amazon S3** | Object storage | Files, backups, static websites, data lakes | 99.999999999% (11 9's) |
| **Amazon EBS** | Block storage | EC2 instance boot volumes, databases | 99.999% |
| **Amazon EFS** | File storage (NFS) | Shared file system across EC2 instances (Linux) | 99.999999999% |
| **Amazon FSx** | Managed file systems | Windows File Server (SMB), Lustre (HPC) | Varies |
| **AWS Storage Gateway** | Hybrid storage | Bridge on-premises to cloud storage | N/A (gateway) |

**S3 Storage Classes:**
| Class | Use Case | Retrieval |
|-------|----------|-----------|
| **S3 Standard** | Frequently accessed | Immediate |
| **S3 Intelligent-Tiering** | Unpredictable access patterns | Automatic tier movement |
| **S3 Standard-IA** | Infrequent access, rapid retrieval needed | Immediate (retrieval fee) |
| **S3 One Zone-IA** | Infrequent, non-critical, single AZ | Immediate (retrieval fee) |
| **S3 Glacier Instant Retrieval** | Archive with millisecond access | Milliseconds |
| **S3 Glacier Flexible Retrieval** | Archive, minutes to hours | 1 min to 12 hrs |
| **S3 Glacier Deep Archive** | Long-term archive, lowest cost | 12-48 hours |

### Database Services

| Service | Type | Use Case |
|---------|------|----------|
| **Amazon RDS** | Managed relational (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) | Traditional SQL workloads |
| **Amazon Aurora** | High-performance relational (MySQL/PostgreSQL compatible) | Enterprise-grade SQL, 5x MySQL perf |
| **Amazon DynamoDB** | Managed NoSQL (key-value, document) | Single-digit ms latency at any scale |
| **Amazon ElastiCache** | In-memory (Redis, Memcached) | Caching, session stores |
| **Amazon Redshift** | Data warehouse | Analytics, BI queries on large datasets |
| **Amazon DocumentDB** | Document database (MongoDB compatible) | JSON document workloads |
| **Amazon Neptune** | Graph database | Social networks, fraud detection |
| **Amazon Keyspaces** | Managed Cassandra | Wide-column NoSQL |
| **Amazon QLDB** | Ledger database | Immutable, cryptographically verifiable logs |
| **Amazon MemoryDB** | Durable in-memory (Redis compatible) | Microsecond reads, durable |

**RDS vs. DynamoDB (exam favorite):**
| Feature | RDS | DynamoDB |
|---------|-----|----------|
| Type | Relational (SQL) | NoSQL (key-value) |
| Schema | Fixed schema | Flexible schema |
| Scaling | Vertical (bigger instance) | Horizontal (automatic) |
| Use case | Complex queries, joins | Simple lookups, high throughput |
| Management | Managed (you choose instance) | Fully managed (serverless option) |

### Networking

| Service | Purpose |
|---------|---------|
| **Amazon VPC** | Isolated virtual network. Your own private cloud within AWS. |
| **Subnets** | Subdivide VPC. Public (internet-facing) or private (no direct internet). |
| **Internet Gateway** | Allows VPC traffic to reach the internet. |
| **NAT Gateway** | Allows private subnet outbound internet access. |
| **Route Tables** | Rules determining where network traffic is directed. |
| **Elastic Load Balancing** | Distributes incoming traffic. ALB (HTTP/HTTPS L7), NLB (TCP L4), GLB (L3). |
| **Amazon API Gateway** | Create, publish, maintain REST/WebSocket APIs. |

### AI/ML Services (know at a high level)

| Service | Purpose |
|---------|---------|
| **Amazon SageMaker** | Build, train, deploy ML models (full platform) |
| **Amazon Rekognition** | Image and video analysis (facial, object, text detection) |
| **Amazon Comprehend** | Natural language processing (sentiment, entities, key phrases) |
| **Amazon Lex** | Build chatbots (same tech as Alexa) |
| **Amazon Polly** | Text-to-speech |
| **Amazon Transcribe** | Speech-to-text |
| **Amazon Translate** | Language translation |
| **Amazon Bedrock** | Access foundation models (Claude, Titan, etc.) |
| **Amazon Q** | AI assistant for business and developers |
| **Amazon Kendra** | Intelligent enterprise search |
| **Amazon Textract** | Extract text and data from documents |
| **Amazon Forecast** | Time-series forecasting |
| **Amazon Personalize** | Real-time personalization and recommendations |

### Analytics

| Service | Purpose |
|---------|---------|
| **Amazon Athena** | Serverless SQL queries directly on S3 data |
| **Amazon Kinesis** | Real-time streaming data (ingest, process, analyze) |
| **AWS Glue** | Serverless ETL (extract, transform, load). Data catalog. |
| **Amazon QuickSight** | BI dashboards and visualizations |
| **Amazon EMR** | Managed Hadoop/Spark clusters for big data |
| **AWS Data Pipeline** | Data-driven workflow orchestration |

### Application Integration

| Service | Purpose |
|---------|---------|
| **Amazon SQS** | Message queue (decouple components). Standard (best effort ordering) or FIFO (exactly once). |
| **Amazon SNS** | Pub/sub notifications (email, SMS, HTTP, Lambda triggers). |
| **AWS Step Functions** | Visual workflow orchestration. Coordinate Lambda functions and services. |
| **Amazon EventBridge** | Serverless event bus. Route events between AWS services, SaaS apps. |

### Management and Governance

| Service | Purpose |
|---------|---------|
| **Amazon CloudWatch** | Monitoring, logs, metrics, alarms, dashboards. The "eyes" of AWS. |
| **AWS CloudTrail** | API call logging. "Who did what?" Governance and auditing. |
| **AWS Config** | Resource inventory, configuration history, compliance rules. |
| **AWS Systems Manager** | Operational management. Patch Manager, Parameter Store, Session Manager. |
| **AWS CloudFormation** | Infrastructure as Code (JSON/YAML templates). |
| **AWS Trusted Advisor** | Best practice recommendations (cost, security, performance, fault tolerance, limits). |
| **AWS Health Dashboard** | Service health events and notifications. |
| **AWS Service Catalog** | Curated catalog of approved IT services (governance). |

---

## Practice Focus

- **Know the core services** -- EC2, S3, RDS, Lambda, VPC, CloudFront, Route 53 at minimum
- **Match service to use case** -- "Need a message queue?" = SQS. "Need a CDN?" = CloudFront.
- **Serverless services** -- Lambda, Fargate, DynamoDB, S3, API Gateway, SQS, SNS, Step Functions, EventBridge, Athena
- **S3 storage classes** -- Know when to use each tier
- **EC2 pricing models** -- On-Demand vs. Reserved vs. Spot vs. Savings Plans
- **Database selection** -- Relational (RDS/Aurora) vs. NoSQL (DynamoDB) vs. Cache (ElastiCache) vs. Warehouse (Redshift)
