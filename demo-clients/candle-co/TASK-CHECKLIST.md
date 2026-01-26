# Fiverr Launch Task Checklist

**Goal:** Launch both gigs
**Created:** 2025-01-19
**Updated:** 2026-01-25

---

## Phase 1: Demo Materials (COMPLETE)

### ComfyUI Refinement
- [x] **SDXL quality workflow** ✓
  - Output: `workflows/sdxl_quality.json`

- [x] **Generate Candle Co. product images** ✓
  - Output: 14 images in `output/`

### Content Generation
- [x] **Create 30-day content calendar** ✓
  - Output: `demo-clients/candle-co/content-calendar.md`

### Dashboard Mockup
- [x] **Analytics dashboard HTML** ✓
  - Output: `fiverr-assets/analytics-dashboard-mockup.html`

---

## Phase 2: Documentation (COMPLETE)

- [x] **Case study** ✓
  - Output: `demo-clients/candle-co/CASE-STUDY.md`

- [x] **Gig descriptions** ✓
  - Output: `fiverr-assets/gig-ai-marketing-automation.md`
  - Output: `fiverr-assets/gig-ai-image-generation.md`

---

## Phase 3: Video Production (IN PROGRESS)

**Tools:** Canva Pro + ComfyUI + SadTalker (local, FREE - replaces SadTalker $29-89/mo)
**Scripts:** `demo-clients/candle-co/video-scripts.md`
**Tracker:** `fiverr-assets/VIDEO-PRODUCTION.md`

### Setup (Verified 2026-01-26)
- [x] ComfyUI running on The Machine (v0.7.0)
- [x] VideoHelperSuite nodes installed (40 nodes)
- [x] Wan2.1 I2V nodes installed (27 nodes)
- [x] AnimateDiff nodes installed (30+ nodes)
- [x] Workflow JSON updated (image_to_video.json)
- [ ] **Download Wan2.1 I2V model** (~14GB) via ComfyUI Manager
- [ ] **Install SadTalker** (not installed - needs git clone)
- [ ] Download SadTalker models
- [ ] Test image-to-video with candle image

### Video 1: AI Marketing Automation (Priority)
- [ ] Record SadTalker avatar clips (intro 8s + outro 15s)
- [ ] Screen record: automation_brain.py demo
- [ ] Create ComfyUI animated clips (2-3 candle images)
- [ ] Build Canva: stats graphics, calendar preview
- [ ] Final edit in Canva (60-90 seconds)
- [ ] Export: `fiverr-assets/videos/ai-marketing-demo.mp4`

### Video 2: AI Image Generation
- [ ] Record SadTalker CTA clip (10s)
- [ ] Screen record: ComfyUI workflow demo
- [ ] Build Canva: Ken Burns slideshow (5 images)
- [ ] Final edit in Canva (45-60 seconds)
- [ ] Export: `fiverr-assets/videos/ai-images-demo.mp4`

### Video 3: Analytics Dashboard
- [ ] Record SadTalker intro clip (5s)
- [ ] Screen record: Dashboard walkthrough
- [ ] Build Canva: Feature callout graphics
- [ ] Final edit in Canva (45-60 seconds)
- [ ] Export: `fiverr-assets/videos/analytics-demo.mp4`

### Thumbnails
- [ ] Video 1 thumbnail: Split screen (AI + calendar)
- [ ] Video 2 thumbnail: Image grid or before/after
- [ ] Video 3 thumbnail: Dashboard with metrics

---

## Phase 4: Launch

- [ ] **Publish automation gig**
  - [ ] Upload video + thumbnail
  - [ ] Paste description from `fiverr-assets/gig-ai-marketing-automation.md`
  - [ ] Set pricing ($500 / $1,200 / $2,500)
  - [ ] Publish

- [ ] **Publish image gig**
  - [ ] Upload video + thumbnail
  - [ ] Paste description from `fiverr-assets/gig-ai-image-generation.md`
  - [ ] Set pricing ($15 / $35 / $75)
  - [ ] Publish

- [ ] **Prepare response templates**
  - Output: `demo-clients/candle-co/response-templates.md`

---

## Next Action

**START HERE:** Download Wan2.1 I2V model via ComfyUI Manager
1. Open http://100.64.130.71:8188 in browser
2. Manager → Install Models → search "Wan2.1"
3. Download wan2.1_i2v_480p model
4. Test with one candle image

See `video-scripts.md` for full production scripts.
See `fiverr-assets/VIDEO-PRODUCTION.md` for detailed tracker.

---

*Last updated: 2026-01-26*
