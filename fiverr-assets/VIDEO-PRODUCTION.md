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
- [x] **Download Wan2.1 I2V model** - DOWNLOADED (480p fp8 + 720p fp16)
- [x] Update workflow JSON (node names changed) - FIXED (umt5_xxl, crop param, pingpong)
- [x] Test image-to-video with one candle image - SUCCESS (i2v_wan_test_00001.mp4)
- [x] Verify output quality - 81 frames @ 24fps = 3.4s video

**Status as of 2026-01-26:**
- ComfyUI v0.7.0 running on The Machine
- ComfyUI-Manager v3.39.2 INSTALLED
- RTX 5060 Ti: 16GB VRAM, ~13GB used during generation
- Wan2.1 I2V 480p fp8 model WORKING
- First test video generated successfully: `i2v_wan_test_00001.mp4`

**Restarting ComfyUI (important!):**
```powershell
# SSH to The Machine
ssh michael@100.64.130.71

# ComfyUI runs as a Windows Service - use service commands
Stop-Service ComfyUI

# Do maintenance (install deps, etc.)
pip install <package>

# Restart
Start-Service ComfyUI

# DON'T use taskkill - service auto-restarts immediately
```

```bash
# Download model via ComfyUI Manager (in browser):
# 1. Open http://100.64.130.71:8188
# 2. Manager → Install Models → search "Wan2.1 I2V"
# 3. Download wan2.1_i2v_480p (smaller) or wan2.1_i2v_720p

# Alternative: Direct download to C:\ComfyUI\models\diffusion_models\
```

### Step 2: Talking Head Setup

- [x] **Install SadTalker nodes** - INSTALLED (2026-01-27)
- [x] Kling API lip sync available (KlingLipSyncAudioToVideoNode) - requires account
- [x] Download SadTalker models - DOWNLOADED (2026-01-29, via SSH from Gaming PC)
- [ ] Take/select a photo of yourself
- [ ] Record a 10-second test audio
- [x] Generate test talking head clip - SUCCESS (2026-01-29, via API from Gaming PC)
- [ ] Evaluate quality vs HeyGen

**Status:** SadTalker TESTED AND WORKING. First talking head video generated via API.

**Installation notes (2026-01-27):**
```powershell
# 1. SSH to The Machine
ssh michael@100.64.130.71

# 2. Clone repo (note: correct repo is haomole, not AIFSH)
cd C:\ComfyUI\custom_nodes
git clone https://github.com/haomole/Comfyui-SadTalker

# 3. Install dependencies to venv (NOT system Python!)
Stop-Service ComfyUI
C:\ComfyUI\venv\Scripts\pip install moviepy soundfile librosa scikit-image facexlib gfpgan face_alignment yacs pydub resampy kornia basicsr av
Start-Service ComfyUI
```

**Patches required (compatibility fixes):**

1. **numpy fix** - `SadTalker\src\face3d\util\preprocess.py` line 13:
```python
# Changed from:
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
# To:
try:
    warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
except AttributeError:
    pass  # numpy >= 1.24 moved this to numpy.exceptions
```

2. **torchvision fix** - `C:\ComfyUI\venv\Lib\site-packages\basicsr\data\degradations.py` line 8:
```python
# Changed from:
from torchvision.transforms.functional_tensor import rgb_to_grayscale
# To:
from torchvision.transforms.functional import rgb_to_grayscale
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

- [x] Candle image 1 animated (3.4s) - `i2v_wan_test_00001.mp4` on The Machine
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

- [x] ComfyUI can generate 3-5 second video clips from images - VERIFIED
- [x] SadTalker produces talking head video - VERIFIED (quality evaluation pending)
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

**Models Downloaded:**
- `Wan2.1\wan2.1_i2v_480p_14B_fp8_e4m3fn.safetensors` - WORKING
- `Wan2.1\wan2.1_i2v_720p_14B_fp16.safetensors` - Available (needs more RAM)
- `umt5_xxl_fp16.safetensors` - Text encoder (required for Wan)
- `wan_2.1_vae.safetensors` - VAE
- `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` - Vision encoder

**Next:** Install SadTalker for talking head videos, or generate more candle animations.

---

### 2026-01-26: First Successful Video Generation

**Test Run:**
- Input: `20260119_122316_automation_machine_00001_.png` (candle image)
- Output: `i2v_wan_test_00001.mp4` (3.4s @ 24fps)
- Settings: 848x480, 81 frames, 30 steps, cfg 5.0, euler sampler
- Generation time: ~42 minutes on RTX 5060 Ti 16GB
- VRAM usage: ~13GB peak

**Workflow fixes applied:**
1. Use `umt5_xxl_fp16.safetensors` (not t5xxl - missing tokenizer)
2. Add `crop: center` to CLIPVisionEncode node
3. Add `pingpong: false` to VHS_VideoCombine node

**Performance notes:**
- 81 frames @ 30 steps = ~42 min (~2 frames/min)
- For faster tests, use 33 frames @ 20 steps (~10 min)
- 480p fp8 model works well, 720p needs more paging file

---

### 2026-01-27: SadTalker Installation

**Successfully installed SadTalker nodes on The Machine.**

**Process:**
1. Cloned repo: `git clone https://github.com/haomole/Comfyui-SadTalker` (note: haomole, not AIFSH)
2. Discovered ComfyUI runs as Windows Service (auto-restarts on taskkill)
3. Used `Stop-Service ComfyUI` / `Start-Service ComfyUI` for proper restart
4. Installed dependencies to venv: moviepy, soundfile, librosa, scikit-image, facexlib, gfpgan, face_alignment, yacs, pydub, resampy, kornia, basicsr, av

**Compatibility patches required:**
1. `numpy.VisibleDeprecationWarning` removed in numpy 1.24+ - wrapped in try/except
2. `torchvision.transforms.functional_tensor` removed - changed to `functional`

**Current status:**
- SadTalker nodes: LOADED (1.3s load time)
- Models: DOWNLOADED (2026-01-29)

**Next:** Test with photo + audio.

---

### 2026-01-29: SadTalker FFmpeg/TorchCodec Error

**Issue:** ShowAudio node fails with `Could not load libtorchcodec` error when running SadTalker workflow.

**Root cause:** PyTorch 2.9.1+cu128 ships with `torchcodec` as the default `torchaudio` backend. `torchcodec` requires FFmpeg shared DLLs (avcodec, avformat, etc.) installed system-wide on Windows. The Machine does not have FFmpeg installed.

**Error location:** `Comfyui-SadTalker\nodes\ShowAudio.py` line 29: `torchaudio.load(audio_path)`

**Two fix options (pick one):**

1. **Install FFmpeg (robust, long-term):**
   ```powershell
   ssh michael@100.64.130.71
   winget install Gyan.FFmpeg
   # Or download "full-shared" build from https://github.com/BtbN/FFmpeg-Builds/releases
   # Add bin/ folder to system PATH
   ffmpeg -version  # verify
   Restart-Service ComfyUI
   ```

2. **Use soundfile backend (quick fix, no FFmpeg needed):**
   ```powershell
   ssh michael@100.64.130.71
   Stop-Service ComfyUI
   C:\ComfyUI\venv\Scripts\pip install soundfile
   ```
   Then edit `C:\ComfyUI\custom_nodes\Comfyui-SadTalker\nodes\ShowAudio.py` line 29:
   ```python
   # Change from:
   waveform, sample_rate = torchaudio.load(audio_path)
   # To:
   waveform, sample_rate = torchaudio.load(audio_path, backend="soundfile")
   ```
   Then `Start-Service ComfyUI`.

**Status:** FIXED (2026-01-29). Applied soundfile backend fix remotely via SSH.

**Fix applied:**
- `soundfile` was already installed in venv
- Patched `ShowAudio.py` line 29: `torchaudio.load(audio_path, backend="soundfile")`
- Restarted ComfyUI service — confirmed running

**Also completed:** Set up SSH key auth from Gaming PC to The Machine (passwordless).
- Key: `~/.ssh/id_ed25519` (ed25519)
- Config: Added `Match Group administrators` block to `sshd_config`
- Auth file: `C:\ProgramData\ssh\administrators_authorized_keys`
- Now Claude Code can run remote commands on The Machine directly

**Next:** Test SadTalker with photo + audio.

---

### 2026-01-29: SadTalker Models Downloaded

**Downloaded all required models remotely via SSH (from Gaming PC).**

**Checkpoints** (`Comfyui-SadTalker/SadTalker/checkpoints/`):
- `SadTalker_V0.0.2_256.safetensors` (725MB) - 256px model
- `SadTalker_V0.0.2_512.safetensors` (725MB) - 512px model
- `mapping_00109-model.pth.tar` (156MB) - already existed
- `mapping_00229-model.pth.tar` (156MB) - already existed

**GFPGAN face enhancer** (`Comfyui-SadTalker/SadTalker/gfpgan/weights/`):
- `alignment_WFLW_4HG.pth` (194MB)
- `detection_Resnet50_Final.pth` (109MB)
- `GFPGANv1.4.pth` (349MB)
- `parsing_parsenet.pth` (85MB)

**Total downloaded:** ~2.5GB
**ComfyUI restarted and confirmed running.**

**SadTalker status:** FULLY OPERATIONAL. Ready for testing with photo + audio.

**Next:** Evaluate quality of test output, then proceed to production clips.

---

### 2026-01-29: SadTalker First Successful Test

**First talking head video generated via ComfyUI API from Gaming PC.**

**Test inputs:** `test_face.jpg` + `test_audio.wav` (already in `C:\ComfyUI\input\`)
**Output:** `C:\ComfyUI\output\20260129185450.mp4` (743KB, ~4.5s @ 30fps, 256x256)
**Generation time:** ~15 seconds on RTX 5060 Ti

**Bugs fixed to get SadTalker working (7 total):**

| # | File | Issue | Fix |
|---|------|-------|-----|
| 1 | `ShowAudio.py` | `torchaudio` crashes importing `torchcodec` (needs FFmpeg DLLs) | Rewrote to use `soundfile` directly, removed `torchaudio` import entirely |
| 2 | `videoio.py` | `ffmpeg` not found by service (user PATH not visible to LocalSystem) | Changed all `ffmpeg` refs to `C:\ComfyUI\ffmpeg.exe` full path |
| 3 | `videoio.py` | `-qscale 0` deprecated in ffmpeg 8 | Changed to `-q:v 0` |
| 4 | `videoio.py` | `logging.error("Error:", e)` crashes Python logging (bad format) | Changed to `logging.error("Error: %s", e)` |
| 5 | `ShowText.py` | `extra_pnginfo[0]` is None when submitted via API (no browser UI) | Added None check before `"workflow" in` |
| 6 | `ShowVideo.py` | Same `extra_pnginfo[0]` None issue | Same None check fix |
| 7 | System | FFmpeg not accessible to ComfyUI service | Copied `ffmpeg.exe` + `ffprobe.exe` to `C:\ComfyUI\` |

**API workflow (from Gaming PC):**
```powershell
# Submit SadTalker job via ComfyUI API
# Nodes: LoadImage → ShowAudio → SadTalker → ShowText
# See: temp_sadtalker_test.ps1
```

**Next:** Evaluate video quality. If acceptable, record real audio scripts and generate production clips.

---
