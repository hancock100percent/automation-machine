# Active Projects

**Living document - Updated automatically and manually**

---

## Fiverr Domination System
**Status:** In Progress - Building demo materials
**Deadline:** End of week (launch 2 gigs)
**Last Updated:** 2025-01-19

### THE PLAN (DO NOT DEVIATE):

**Primary Gig: AI Marketing Automation System**
- Title: "I will build an AI marketing automation system for your business"
- Price: $500 (Basic) / $1,200 (Standard) / $2,500 (Premium)
- Deliverables: Content generation + image generation + auto-posting + analytics
- Target: E-commerce brands, content creators, small agencies
- Differentiator: Build SYSTEMS, not just outputs
- Why: Defensible, high-value, uses orchestration expertise

**Secondary Gig: AI Image Generation**
- Title: "I will create custom AI generated images for your brand"
- Price: $15 (Basic) / $35 (Standard) / $75 (Premium)
- Deliverables: AI-generated images in any style
- Target: Small budget clients, upsell path to automation
- Why: Entry point, recurring add-on for automation clients

### Current Phase: Video Production
**Building:** 3 Fiverr demo videos using automated FFmpeg pipeline + ComfyUI

**What's done:**
1. [x] ComfyUI images generated (14 sample candle images)
2. [x] Content generation examples (30-day calendar)
3. [x] Analytics dashboard mockup (fiverr-assets/)
4. [x] Case study documentation (demo-clients/candle-co/)
5. [x] Gig descriptions written (fiverr-assets/)
6. [x] Video production pipeline built (5 Python scripts, tested)
7. [x] SadTalker + Wan2.1 I2V working on The Machine
8. [x] Normalization + validation tested end-to-end

**What's next (IN ORDER):**
1. Record/create 14 user assets (photos, audio, screen recordings, Canva exports)
2. Run pipeline Stage 2: generate SadTalker + I2V clips via ComfyUI API
3. Run pipeline Stage 3: normalize all clips to 1080p30
4. Run pipeline Stage 4: assemble 3 videos
5. Run pipeline Stage 5: validate + export to fiverr-assets/
6. Upload videos to Fiverr gig pages
7. Publish gigs

### Pipeline Status (2026-01-30):
- **Scripts:** `video-production/scripts/` (5 scripts, all tested)
- **Configs:** `video-production/configs/` (normalization standard + 3 video structures)
- **Tracker:** `fiverr-assets/VIDEO-PRODUCTION.md` (full reference with run commands)
- **Quick check:** `python video-production/scripts/setup_environment.py`

### Blockers:
- 14 user-provided assets needed (see VIDEO-PRODUCTION.md for full list)
- Key files: avatar photo, 4 audio recordings, 3 screen recordings, 6 Canva exports

### System Locations:
- Automation Machine: C:\automation-machine\ (gaming-pc)
- ComfyUI: http://100.64.130.71:8188 (The Machine)
- Demo folder: C:\automation-machine\demo-clients\candle-co\
- Documentation: C:\automation-machine\knowledge-base\

### Critical Rules:
- Primary focus = automation gig (high value)
- Images = supporting evidence + upsell
- Don't over-engineer before first sale
- Document everything as you build
- Update ACTIVE-PROJECTS.md after each task

---

## Backlog

### Phase 2 Completion
- [x] ComfyUI REST API integration
- [ ] GitHub MCP setup
- [ ] Supabase MCP setup
- [ ] Citation extraction for Perplexity

### Future Ideas
- Autonomous agent workflows
- Client project automation
- Batch processing for orders

---

## EOD Summaries

### 2026-01-30
- Built 5-stage automated video production pipeline (video-production/scripts/)
- Created normalization standard + 3 video structure configs
- Tested normalization: 1024x1024 8fps -> 1920x1080 30fps (12/12 validation checks pass)
- Pipeline handles all known pitfalls: codec mismatch, resolution scaling, silent audio, sample rate drift
- Setup validation shows all-green: FFmpeg 8.0.1, SSH, ComfyUI (RTX 5060 Ti, 14.8GB free)
- Waiting on 14 user-provided assets before full pipeline run

### 2026-01-19
- Created handoff system (HANDOFF.md, ACTIVE-PROJECTS.md)
- Added --update-projects flag to auto_doc.py

### 2026-01-18
- Automation Machine fully operational
- Perplexity integration working
- Cost tracking functional
- 11 queries processed, $0.004734 total cost

---

## Handoff Command

To resume work, use:

```
Resume Automation Machine work.
Read HANDOFF.md first, then check state files, continue from ACTIVE-PROJECTS.md
```

---

*Last auto-update: 2026-01-30*
