# CLF-C02 Recommended Resources

> Free and low-cost resources for AWS Cloud Practitioner exam prep.
> Resources marked with `[INGEST]` can be ingested via `knowledge_ingest.py`.

---

## YouTube Courses (Free)

### Top Picks

| # | Course | Creator | Length | Why |
|---|--------|---------|--------|-----|
| 1 | **AWS Certified Cloud Practitioner (CLF-C02) Full Course** | freeCodeCamp / Andrew Brown (ExamPro) | ~14 hrs | Most comprehensive free CLF-C02 course. Updated for C02. Covers every domain with hands-on demos. |
| 2 | **AWS Cloud Practitioner Essentials** | AWS Training & Certification | ~6 hrs | Official AWS course, free on AWS Skill Builder. Concise, authoritative, covers core concepts. |
| 3 | **AWS CLF-C02 Cloud Practitioner Certification Course** | Stephane Maarek (preview lectures) | ~2 hrs (free portion) | Maarek's courses are gold standard. Free preview covers fundamentals. Full course on Udemy (~$15 on sale). |
| 4 | **AWS Certified Cloud Practitioner 2024/2025** | TechWorld with Nana | ~3 hrs | Beginner-friendly, visual explanations, good for quick overview before deep study. |

### Supplemental Videos (Topic-Specific)

| Topic | Video | Creator | Length |
|-------|-------|---------|--------|
| IAM Deep Dive | "AWS IAM Tutorial" | Be A Better Dev | ~20 min |
| S3 Explained | "Amazon S3 Tutorial for Beginners" | Stephane Maarek | ~15 min |
| EC2 Pricing | "EC2 Pricing Explained" | Digital Cloud Training | ~12 min |
| Well-Architected | "AWS Well-Architected Framework" | AWS Online Tech Talks | ~45 min |
| Shared Responsibility | "AWS Shared Responsibility Model" | AWS | ~10 min |
| VPC Basics | "AWS VPC Beginner to Pro" | Be A Better Dev | ~30 min |

### Ingestion Commands

```bash
# Full courses (ingest for searchable notes)
python knowledge_ingest.py --youtube "https://www.youtube.com/watch?v=SOTamWNgDKc" --title "freeCodeCamp CLF-C02 Full Course"

# AWS official course (available on Skill Builder, not YouTube - take directly)
# https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials

# Topic-specific videos
python knowledge_ingest.py --youtube "https://www.youtube.com/watch?v=SFaSB6vgp8k" --title "IAM Tutorial - Be A Better Dev"
python knowledge_ingest.py --youtube "https://www.youtube.com/watch?v=e6w9LwZJFIA" --title "S3 Tutorial - Stephane Maarek"
```

> **Note:** YouTube URLs above are based on well-known channels. Verify URLs are current before ingesting -- creators occasionally re-upload updated versions. Search the channel name + topic if a link is broken.

---

## Podcasts (Free)

### AWS-Focused Podcasts

| # | Podcast | Host | Episode Frequency | Best For |
|---|---------|------|-------------------|----------|
| 1 | **AWS Podcast** | AWS (official) | Weekly | Service announcements, use cases, best practices. Listen for real-world context. |
| 2 | **Screaming in the Cloud** | Corey Quinn | Weekly | Cloud economics, cost optimization (great for Domain 4), industry perspective. |
| 3 | **Cloud Security Podcast** | Google Cloud | Bi-weekly | Security concepts (Domain 2). Cloud-agnostic security thinking. |
| 4 | **Day Two Cloud** | Packet Pushers | Weekly | Cloud networking, architecture. Good for Domain 3 networking concepts. |

### Recommended Episodes for CLF-C02

| Podcast | Episode Topic | Domain |
|---------|--------------|--------|
| AWS Podcast | "What is Cloud Computing?" (intro episodes) | Domain 1 |
| Screaming in the Cloud | Any episode on AWS billing/pricing | Domain 4 |
| Cloud Security Podcast | Episodes on shared responsibility, IAM | Domain 2 |
| Day Two Cloud | Episodes on VPC, networking basics | Domain 3 |

### Ingestion Commands

```bash
# Download podcast episodes as MP3 then ingest
# Use your preferred podcast app to download, then:
python knowledge_ingest.py --audio "path/to/episode.mp3" --title "AWS Podcast - Cloud Computing Intro"
```

---

## Official AWS Training (Free)

| Resource | URL | Notes |
|----------|-----|-------|
| **AWS Skill Builder** | https://explore.skillbuilder.aws | Free digital training. Start with "Cloud Practitioner Essentials" |
| **AWS Cloud Practitioner Essentials** | Skill Builder (search for it) | Official 6-hour course, exactly aligned to CLF-C02 |
| **AWS Cloud Quest: Cloud Practitioner** | Skill Builder | Gamified learning, hands-on labs in a virtual city |
| **AWS Educate** | https://aws.amazon.com/education/awseducate/ | Free for students, includes labs and badges |
| **AWS Well-Architected Labs** | https://wellarchitectedlabs.com | Hands-on labs for the 6 pillars |
| **AWS Whitepapers** | https://aws.amazon.com/whitepapers/ | Deep dives (read "Overview of Amazon Web Services" whitepaper) |
| **AWS Official Practice Exam** | Free with exam registration | 20 questions, simulates real exam format |

### Key Whitepapers for CLF-C02

1. **Overview of Amazon Web Services** -- covers all major services (Domain 3)
2. **AWS Well-Architected Framework** -- the 6 pillars (Domain 1)
3. **AWS Pricing Overview** -- pricing models explained (Domain 4)
4. **Shared Responsibility Model** -- security division (Domain 2)

```bash
# Ingest whitepapers (download PDF first from AWS)
python knowledge_ingest.py --pdf "path/to/aws-overview-whitepaper.pdf" --title "AWS Overview Whitepaper"
python knowledge_ingest.py --pdf "path/to/well-architected-framework.pdf" --title "Well-Architected Framework"
```

---

## Paid Resources (Low Cost, High Value)

> Only if you want additional practice exams or structured courses.

| Resource | Price | Why Worth It |
|----------|-------|-------------|
| **Stephane Maarek - CLF-C02 (Udemy)** | ~$15 on sale | Best-rated CLF-C02 course. Clear explanations, constantly updated. |
| **Tutorial Dojo Practice Exams (Jon Bonso)** | ~$15 on sale | 390+ practice questions with detailed explanations. Closest to real exam difficulty. |
| **AWS Official Practice Exam Set** | Free (with registration) | Official questions from AWS. Take this last as a final benchmark. |

---

## Study Strategy with Resources

### Phase 1: Foundation (Week 1-2)
1. Watch the **freeCodeCamp full course** (or AWS Cloud Practitioner Essentials) at 1.5x speed
2. After each section, read the corresponding domain study notes in this guide
3. Take notes on concepts that are new or confusing

### Phase 2: Deepen (Week 2-3)
1. Watch **supplemental topic videos** for weak areas
2. Read relevant **AWS whitepapers** (skim, don't memorize)
3. Ingest videos/podcasts via `knowledge_ingest.py` for searchable reference

### Phase 3: Practice (Week 3-4)
1. Do all **80 practice questions** in this study guide
2. If budget allows, do **Tutorial Dojo practice exams** for additional drilling
3. Take the **AWS official practice exam** as final benchmark
4. Score 80%+ consistently before scheduling the real exam

---

## Ingestion Priority List

For the `knowledge_ingest.py` pipeline, ingest in this order:

| Priority | Resource | Type | Estimated Time |
|----------|----------|------|---------------|
| 1 | freeCodeCamp CLF-C02 Full Course | YouTube | ~14 hrs (transcript) |
| 2 | AWS Overview whitepaper | PDF | ~30 pages |
| 3 | Well-Architected Framework whitepaper | PDF | ~50 pages |
| 4 | AWS Pricing Overview whitepaper | PDF | ~20 pages |
| 5 | Screaming in the Cloud - billing episodes | Podcast | ~1 hr each |
| 6 | Topic-specific YouTube videos | YouTube | ~15-30 min each |

> **Tip:** Ingesting the freeCodeCamp course transcript gives you a searchable 14-hour knowledge base covering the entire exam. This single ingestion is the highest ROI action.
