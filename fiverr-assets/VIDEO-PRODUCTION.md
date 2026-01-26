# Video Production Tracker

## Status: IN PROGRESS

Last Updated: 2026-01-26

---

## Strategy Overview

Building a complete, scalable video production pipeline using existing tools:
- **Canva Pro** - Video editing, templates, brand consistency
- **ComfyUI** - Image-to-video, talking heads (SadTalker), animations
- **OBS Studio** - Screen recording
- **Perplexity** - Research automation

**Philosophy:** Local-first, cloud as fallback. SadTalker replaces HeyGen ($0 vs $29-89/month).

---

## Tool Stack

### Primary (Already Have)

| Tool | Role | Cost |
|------|------|------|
| ComfyUI | Image gen, video gen, avatars | FREE |
| Canva Pro | Video editing, templates, brand | $13/mo |
| Perplexity | Research automation | $20/mo |
| OBS Studio | Screen recording | FREE |

### Optional Add-ons

| Tool | Role | Cost | When to Add |
|------|------|------|-------------|
| ElevenLabs | AI voice cloning | $5/mo | If you want AI voiceover |
| D-ID | Backup avatar service | $6/mo | If ComfyUI quality insufficient |
| Runway | Advanced video effects | $15/mo | For premium client work |

**Total:** $33/month (current) | $38/month (with voice) | $53/month (premium)

---

## Videos Overview

| Video | Status | Target Length | Priority |
|-------|--------|---------------|----------|
| AI Marketing Automation | Not Started | 60-90s | HIGH |
| AI Image Generation | Not Started | 45-60s | MEDIUM |
| Analytics Dashboard | Not Started | 45-60s | MEDIUM |

---

## ComfyUI Video Capabilities (RTX 5060 Ti 16GB)

| Capability | Model/Workflow | VRAM | Use Case |
|------------|----------------|------|----------|
| Image-to-Video | Wan2.1 I2V 480p | ~8GB | Animate product images |
| Image-to-Video | AnimateDiff | ~10GB | Motion graphics, loops |
| Talking Head | SadTalker | ~6GB | AI avatar from photo + audio |
| Lip Sync | Wav2Lip | ~4GB | Sync any face to audio |
| Video Upscale | Real-ESRGAN | ~4GB | Enhance low-res clips |
| Frame Interpolation | RIFE | ~2GB | Smooth motion |

### Workflows Created

| Workflow | File | Purpose |
|----------|------|---------|
| Image-to-Video (Wan2.1) | `workflows/image_to_video.json` | Main I2V workflow |
| Image-to-Video (AnimateDiff) | `workflows/image_to_video_animatediff.json` | Loop animations |
| Talking Head (SadTalker) | `workflows/talking_head.json` | Avatar videos |
| Lip Sync (Wav2Lip) | `workflows/lipsync_wav2lip.json` | Alternative lip sync |

---

## Implementation Checklist

### Step 1: ComfyUI Video Setup

- [x] SSH to The Machine (100.64.130.71) - Accessible via Tailscale
- [x] Install ComfyUI-VideoHelperSuite - **INSTALLED** (40 nodes)
- [x] Install Wan2.1 nodes - **INSTALLED** (27 nodes)
- [x] Install AnimateDiff nodes - **INSTALLED** (30+ nodes)
- [ ] **Download Wan2.1 I2V model** (~14GB) - diffusion_models/ is empty
- [ ] Update workflow JSON (node names changed)
- [ ] Test image-to-video with one candle image
- [ ] Verify output quality

**Status as of 2026-01-26:**
- ComfyUI v0.7.0 running on The Machine
- RTX 5060 Ti: 16GB VRAM, ~15GB free
- All video NODES installed, but Wan2.1 MODEL not downloaded yet

```bash
# Download model via ComfyUI Manager (in browser):
# 1. Open http://100.64.130.71:8188
# 2. Manager → Install Models → search "Wan2.1 I2V"
# 3. Download wan2.1_i2v_480p (smaller) or wan2.1_i2v_720p

# Alternative: Direct download to C:\ComfyUI\models\diffusion_models\
```

### Step 2: Talking Head Setup

- [ ] **Install SadTalker nodes** - NOT INSTALLED (false positive earlier)
- [x] Kling API lip sync available (KlingLipSyncAudioToVideoNode) - requires account
- [ ] Download SadTalker models
- [ ] Take/select a photo of yourself
- [ ] Record a 10-second test audio
- [ ] Generate test talking head clip
- [ ] Evaluate quality vs HeyGen

**Status:** SadTalker NOT installed. Options:
1. **Install locally (FREE):** `cd C:\ComfyUI\custom_nodes && git clone https://github.com/AIFSH/ComfyUI-SadTalker`
2. **Use Kling API:** KlingLipSyncAudioToVideoNode (requires Kling account/credits)
3. **Use HeyGen via Canva:** Fallback if local doesn't work

```bash
# Install SadTalker on The Machine:
# 1. RDP or SSH to 100.64.130.71
# 2. cd C:\ComfyUI\custom_nodes
# 3. git clone https://github.com/AIFSH/ComfyUI-SadTalker
# 4. Restart ComfyUI
# 5. Download models via ComfyUI Manager
```

### Step 3: Audio Recording

- [ ] Write final scripts for all 3 videos
- [ ] Record audio for each video segment (your voice)
- [ ] Optional: Test ElevenLabs for AI voice alternative

### Step 4: Asset Generation

- [ ] Generate talking head clips (SadTalker) - Your face, your voice
- [ ] Animate 3-5 candle images (Wan2.1)
- [ ] Screen record all demos (OBS)
- [ ] Create Canva graphics (stats, callouts)

### Step 5: Final Edit

- [ ] Edit Video 1 in Canva Pro
- [ ] Edit Video 2 in Canva Pro
- [ ] Edit Video 3 in Canva Pro
- [ ] Create thumbnails
- [ ] Export all as MP4 1080p

### Step 6: Publish

- [ ] Upload to Fiverr gig pages
- [ ] Update CLAUDE.md checklist

---

## Asset Generation Progress

### Source Images (from output/)

Available for image-to-video conversion:
- `20260119_122316_automation_machine_00001_.png`
- `20260119_122539_automation_machine_00002_.png`
- `20260119_122631_automation_machine_00003_.png`
- `20260119_122738_automation_machine_00004_.png`
- `20260119_122841_automation_machine_00005_.png`
- `20260119_122940_automation_machine_00006_.png`
- `20260119_123041_automation_machine_00007_.png`
- `20260119_123138_automation_machine_00008_.png`
- `20260119_123235_automation_machine_00009_.png`
- `20260125_061654_automation_machine_00010_.png`
- `20260125_061802_automation_machine_00011_.png`
- `20260125_061910_automation_machine_00012_.png`
- `20260125_062027_automation_machine_00013_.png`
- `20260125_062127_automation_machine_00014_.png`

### SadTalker Avatar Clips (Replaces HeyGen)

- [ ] Video 1 intro (8s): "What if AI could plan..." (your face + audio)
- [ ] Video 1 outro (15s): "30 posts. Custom images..." (your face + audio)
- [ ] Video 2 CTA (10s): "Professional AI images..." (your face + audio)
- [ ] Video 3 intro (5s): "See exactly how..." (your face + audio)

### Screen Recordings

- [ ] automation_brain.py content calendar demo
- [ ] ComfyUI SDXL generation workflow
- [ ] Analytics dashboard walkthrough

### ComfyUI Video Clips

- [ ] Candle image 1 animated (3-4s) - flame flicker
- [ ] Candle image 2 animated (3-4s) - soft glow
- [ ] Candle image 3 animated (3-4s) - ambient motion

### Canva Graphics

- [ ] Stats animation (30 posts, 5 images, 10 min)
- [ ] Calendar preview mockup
- [ ] 5-image Ken Burns slideshow
- [ ] Feature callout boxes
- [ ] CTA text animations

---

## Video Structure (Updated)

### Video 1: AI Marketing Automation (60-90s)

| Segment | Duration | Content | Tool |
|---------|----------|---------|------|
| Hook | 0-8s | Your face: "What if AI could plan..." | SadTalker |
| Demo | 8-45s | Screen recording: automation_brain.py | OBS |
| Results | 45-65s | Animated candle images | ComfyUI Wan2.1 |
| Stats | 65-75s | "30 posts, 5 images, 10 minutes" | Canva |
| CTA | 75-90s | Your face: "Ready to automate? Order now." | SadTalker |

### Video 2: AI Image Generation (45-60s)

| Segment | Duration | Content | Tool |
|---------|----------|---------|------|
| Hook | 0-5s | Quick image montage | Canva |
| Demo | 5-35s | ComfyUI generating image live | OBS |
| Gallery | 35-50s | Ken Burns slideshow | Canva |
| CTA | 50-60s | Your face + "Order today" | SadTalker |

### Video 3: Analytics Dashboard (45-60s)

| Segment | Duration | Content | Tool |
|---------|----------|---------|------|
| Hook | 0-5s | Your face: "See how your content performs" | SadTalker |
| Demo | 5-40s | Dashboard walkthrough | OBS |
| Features | 40-50s | Callout graphics | Canva |
| CTA | 50-60s | Text: "Included with every package" | Canva |

---

## Workflow: Creating a Talking Head Clip

```
1. Prepare photo (well-lit face, neutral expression)
2. Record audio script (clear voice, quiet room)
3. Copy photo + audio to The Machine
4. Queue SadTalker workflow via ComfyUI API:
   - Source image: your_photo.png
   - Audio file: script_segment.wav
   - Settings: preprocess=crop, enhancer=gfpgan
5. Retrieve output video
6. Import to Canva for final editing
```

**automation_brain.py integration:**
```bash
python automation_brain.py "generate talking head from photo.png with audio.wav"
```

---

## Quality Checklist (Before Export)

### Video 1 - AI Marketing

- [ ] Hook grabs attention in first 3 seconds
- [ ] Demo clearly shows value proposition
- [ ] Stats are readable and impactful
- [ ] CTA is clear and actionable
- [ ] Audio levels consistent
- [ ] No typos in text overlays
- [ ] SadTalker lip sync is natural

### Video 2 - AI Images

- [ ] Image quality is sharp
- [ ] ComfyUI workflow is understandable
- [ ] Gallery showcases variety
- [ ] Transitions are smooth

### Video 3 - Analytics

- [ ] Dashboard features are clearly visible
- [ ] Mouse movements are deliberate
- [ ] Callouts don't obscure content
- [ ] Value proposition is clear

---

## Final Deliverables

### Videos

- `fiverr-assets/videos/ai-marketing-demo.mp4`
- `fiverr-assets/videos/ai-images-demo.mp4`
- `fiverr-assets/videos/analytics-demo.mp4`

### Thumbnails

- `fiverr-assets/thumbnails/ai-marketing-thumb.png`
- `fiverr-assets/thumbnails/ai-images-thumb.png`
- `fiverr-assets/thumbnails/analytics-thumb.png`

---

## Verification Criteria

- [ ] ComfyUI can generate 3-5 second video clips from images
- [ ] SadTalker produces acceptable talking head quality
- [ ] Full workflow tested end-to-end before production
- [ ] All 3 videos exported under 2 minutes each
- [ ] Videos uploaded to Fiverr

---

## Notes

### 2026-01-26: Infrastructure Verification

Verified The Machine status via ComfyUI API:
- ComfyUI v0.7.0 running, accessible at http://100.64.130.71:8188
- RTX 5060 Ti 16GB detected, ~15GB VRAM free
- PyTorch 2.9.1+cu128

**Installed nodes:**
- VideoHelperSuite: 40 nodes (VHS_VideoCombine, VHS_LoadVideo, etc.)
- Wan2.1: 27 nodes (WanImageToVideo, WanFirstLastFrameToVideo, etc.)
- AnimateDiff: 30+ nodes (ADE_AnimateDiffLoaderWithContext, etc.)
- Kling Lip Sync: Available (API-based, requires account)

**NOT Installed:**
- SadTalker: Needs manual installation (false positive earlier)
- Wan2.1 I2V model file (~14GB) - diffusion_models/ folder empty

**Updated:**
- image_to_video.json: Fixed for ComfyUI v0.7.0 node structure
- talking_head.json: Marked as requiring SadTalker installation

**Next:** Download models via ComfyUI Manager, then test I2V with candle image.

---
