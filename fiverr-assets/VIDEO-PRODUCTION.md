# Video Production Tracker

## Status: IN PROGRESS

Last Updated: 2026-02-03

---

## Strategy Overview

Building a complete, scalable video production pipeline using existing tools:
- **Canva Pro** - Video editing, templates, brand consistency
- **ComfyUI** - Image-to-video, talking heads (SadTalker), animations
- **OBS Studio** - Screen recording
- **Perplexity** - Research automation

**Philosophy:** Local-first, cloud as fallback. FantasyTalking replaces HeyGen ($0 vs $29-89/month).

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

| Capability | Model/Workflow | VRAM | Use Case | Status |
|------------|----------------|------|----------|--------|
| **Talking Head** | **FantasyTalking (Wan2.1)** | ~14GB | **AI avatar from photo + audio** | **APPROVED** |
| **Image-to-Video** | **Wan2.1 I2V 480p fp8** | ~13GB | **Animate product images** | **RECOMMENDED (~42 min)** |
| Image-to-Video GGUF | Wan2.1 I2V Q5_K_M | ~14GB | Slower on this GPU | **NOT RECOMMENDED (~70 min)** |
| Image-to-Video | AnimateDiff | ~10GB | Motion graphics, loops | Available |
| Talking Head (legacy) | SadTalker | ~6GB | Superseded by FantasyTalking | Deprecated |
| Lip Sync | Wav2Lip | ~4GB | Sync any face to audio | Available |
| Video Upscale | Real-ESRGAN | ~4GB | Enhance low-res clips | Available |
| Frame Interpolation | RIFE | ~2GB | Smooth motion | Available |

**GGUF Test Results (2026-02-03):** GGUF quantized models are **slower** on RTX 5060 Ti (~70 min vs ~42 min for fp8). This is because the GPU lacks specialized INT4/INT8 tensor cores and GGUF requires runtime dequantization. **Use fp8 for all video generation.**

### Workflows Created

| Workflow | File | Purpose |
|----------|------|---------|
| **Image-to-Video (Wan2.1 fp8)** | `workflows/image_to_video.json` | **RECOMMENDED - ~42 min** |
| Image-to-Video (GGUF) | `workflows/image_to_video_wan22.json` | Not recommended (~70 min) |
| Image-to-Video (AnimateDiff) | `workflows/image_to_video_animatediff.json` | Loop animations |
| **Talking Head (FantasyTalking)** | `workflows/talking_head_fantasy.json` | **Primary avatar videos** |
| Talking Head (SadTalker) | `workflows/talking_head.json` | Legacy (deprecated) |
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
- [x] Generate test talking head clip (SadTalker) - SUCCESS (2026-01-29)
- [x] **Install FantasyTalking** - INSTALLED (2026-02-01, ComfyUI-WanVideoWrapper + model)
- [x] **Download FantasyTalking model** - `fantasytalking_fp16.safetensors` (1.68GB)
- [x] **Download wav2vec2 model** - `facebook/wav2vec2-base-960h` (auto-downloaded)
- [x] **Generate FantasyTalking test** - SUCCESS (2026-02-02, 512x512 49 frames)
- [x] **Evaluate quality** - APPROVED. Better lip sync, no teeth distortion
- [ ] Take/select a photo of yourself (have `avatar_photo.jpg` but need final choice)
- [ ] Record production audio scripts

**Status:** FantasyTalking TESTED AND APPROVED. Replaces SadTalker as primary talking head.
**Decision:** FantasyTalking is the production tool. SadTalker deprecated.

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

### Step 5: Automated Pipeline Assembly (NEW - 2026-01-30)

**Replaced Canva editing with automated FFmpeg pipeline.**

- [x] Build 5-stage pipeline scripts (`video-production/scripts/`)
- [x] Create normalization standard config
- [x] Create 3 video structure configs (JSON timelines)
- [x] Test normalization on existing video (1024x1024 8fps -> 1920x1080 30fps)
- [x] Test validation (12/12 checks pass)
- [ ] Provide user assets (14 files -- see checklist below)
- [ ] Run Stage 2: generate SadTalker + I2V clips
- [ ] Run Stage 3: normalize all clips
- [ ] Run Stage 4: assemble 3 videos
- [ ] Run Stage 5: validate + export to fiverr-assets/

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
| Hook | 0-8s | Your face: "What if AI could plan..." | FantasyTalking |
| Demo | 8-45s | Screen recording: automation_brain.py | OBS |
| Results | 45-65s | Animated candle images | ComfyUI Wan2.1 |
| Stats | 65-75s | "30 posts, 5 images, 10 minutes" | Canva |
| CTA | 75-90s | Your face: "Ready to automate? Order now." | FantasyTalking |

### Video 2: AI Image Generation (45-60s)

| Segment | Duration | Content | Tool |
|---------|----------|---------|------|
| Hook | 0-5s | Quick image montage | Canva |
| Demo | 5-35s | ComfyUI generating image live | OBS |
| Gallery | 35-50s | Ken Burns slideshow | Canva |
| CTA | 50-60s | Your face + "Order today" | FantasyTalking |

### Video 3: Analytics Dashboard (45-60s)

| Segment | Duration | Content | Tool |
|---------|----------|---------|------|
| Hook | 0-5s | Your face: "See how your content performs" | FantasyTalking |
| Demo | 5-40s | Dashboard walkthrough | OBS |
| Features | 40-50s | Callout graphics | Canva |
| CTA | 50-60s | Text: "Included with every package" | Canva |

---

## Workflow: Creating a Talking Head Clip

```
1. Prepare photo (well-lit face, neutral expression, front-facing)
2. Record audio script (clear voice, quiet room)
3. Copy photo + audio to The Machine (C:\ComfyUI\input\)
4. Queue FantasyTalking workflow via ComfyUI API:
   - Source image: your_photo.png (resized to 512x512 by workflow)
   - Audio file: script_segment.wav
   - Model: fantasytalking_fp16 + Wan2.1 I2V 480p fp8
   - Settings: 20-30 steps, cfg 5.0, unipc, TeaCache, BlockSwap 15
5. Retrieve output video from C:\ComfyUI\output\
6. Normalize to 1080p30 via pipeline Stage 3
```

**API reference:** `temp_fantasytalking_test.py` (working API workflow)

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
- [x] SadTalker produces talking head video - VERIFIED (superseded by FantasyTalking)
- [x] FantasyTalking produces talking head video - VERIFIED & APPROVED (2026-02-02)
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

**Wan2.1 I2V Realism Tips:**

1. **Start from a strong still image** -- Generate or hand-pick a clean, well-lit, realistic key image first (Flux, SDXL, or WAN image model), then feed that into i2v_wan instead of a noisy/stylized base.

2. **Write longer, structured prompts (80-120 words)** -- Clearly specify subject, environment, motion, and camera behavior. Example: *"realistic 4K video of..., soft natural lighting, shallow depth of field, camera slowly dolly-in, no rapid movement."*

3. **Focus the prompt on motion, not redesign** -- Describe how the existing scene should move ("the woman gently turns her head and smiles; background stays fixed; subtle camera pan right") instead of re-describing a new character or different setting.

4. **Keep motion simple** -- Small head/eye/hand movements, slight camera pans/zooms, gentle parallax. Complex multi-action scenes tend to produce warped limbs and broken physics.

5. **Use negative prompts** -- Include: *"no distortion, no warped hands, no glitching, no flicker, no fast motion, no morphing, no unnatural movement"*

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

### 2026-01-30: Automated Video Production Pipeline Built

**Built a 5-stage FFmpeg pipeline to replace manual Canva editing.**

All scripts tested and working. Pipeline is ready for user-provided assets.

**What was built:**

```
video-production/
├── scripts/
│   ├── setup_environment.py        # Stage 1: Verify FFmpeg, SSH, ComfyUI, dirs
│   ├── generate_comfyui_assets.py  # Stage 2: SadTalker + Wan2.1 I2V via API
│   ├── normalize_clips.py          # Stage 3: Re-encode ALL clips to 1080p30
│   ├── assemble_video.py           # Stage 4: FFmpeg concat + crossfades + audio
│   └── validate_outputs.py         # Stage 5: ffprobe checks + thumbnails + export
├── configs/
│   ├── normalization_standard.json # Target: 1920x1080, 30fps, H.264, AAC 48kHz
│   ├── video1_structure.json       # AI Marketing Automation (6 segments, 75-90s)
│   ├── video2_structure.json       # AI Image Generation (4 segments, 45-60s)
│   └── video3_structure.json       # Analytics Dashboard (4 segments, 45-60s)
└── logs/
    ├── ffprobe_reports/            # Per-clip probe data
    └── validation_reports/         # Per-run validation JSON
```

**Test results:**
- `setup_environment.py`: All green (FFmpeg 8.0.1, SSH, ComfyUI RTX 5060 Ti 14.8GB free)
- `normalize_clips.py`: 1024x1024 8fps no-audio -> 1920x1080 30fps stereo AAC
- `validate_outputs.py`: 12/12 checks pass on normalized output

**Pitfalls handled in the pipeline:**
| Issue | Solution |
|-------|----------|
| AI clips have different codecs/FPS/resolution | Stage 3 normalizes everything to one standard |
| SadTalker outputs 512x512 | Pad to 1080p with black pillarbox |
| Wan2.1 outputs 480p @ 24fps | Upscale + fps conversion |
| Silent video clips (I2V has no audio) | Auto-generate silent stereo 48kHz track |
| Audio sample rate drift (44.1kHz vs 48kHz) | `aresample=48000:async=1` on all audio |
| Metadata inconsistencies | `setsar=1`, `setpts=PTS-STARTPTS` on all clips |
| xfade complex filter failures | Auto-fallback to concat demuxer |
| Windows Unicode in terminal | ASCII-only output characters |

---

## Automated Pipeline Reference

### How to Run the Pipeline

```bash
# Stage 1: Verify everything is ready
python video-production/scripts/setup_environment.py

# Stage 2: Generate AI clips (after placing user assets)
python video-production/scripts/generate_comfyui_assets.py --status    # check ComfyUI
python video-production/scripts/generate_comfyui_assets.py --sadtalker # SadTalker only
python video-production/scripts/generate_comfyui_assets.py --i2v       # Wan2.1 only
python video-production/scripts/generate_comfyui_assets.py             # both

# Stage 3: Normalize all clips to 1080p30
python video-production/scripts/normalize_clips.py                     # all raw clips
python video-production/scripts/normalize_clips.py path/to/clip.mp4    # single clip
python video-production/scripts/normalize_clips.py --probe path/clip   # probe only

# Stage 4: Assemble final videos
python video-production/scripts/assemble_video.py video-production/configs/video1_structure.json
python video-production/scripts/assemble_video.py video-production/configs/video2_structure.json
python video-production/scripts/assemble_video.py video-production/configs/video3_structure.json
python video-production/scripts/assemble_video.py --all                # all 3
python video-production/scripts/assemble_video.py --dry-run <config>   # preview command
python video-production/scripts/assemble_video.py --demuxer <config>   # safe concat (no transitions)

# Stage 5: Validate + export
python video-production/scripts/validate_outputs.py                    # validate all
python video-production/scripts/validate_outputs.py --export           # validate + copy to fiverr-assets/
python video-production/scripts/validate_outputs.py --thumbnails       # generate 1280x720 thumbnails
```

### User Assets Required Before Stage 2

Place these files in `demo-clients/candle-co/`:

| File | Location | Description |
|------|----------|-------------|
| `avatar_photo.png` | `photos/` | Your face photo (well-lit, front-facing, neutral) |
| `v1_intro.wav` | `audio/` | "What if AI could plan..." (~8s) |
| `v1_outro.wav` | `audio/` | "30 posts. Custom images..." (~15s) |
| `v2_cta.wav` | `audio/` | "Professional AI images..." (~10s) |
| `v3_intro.wav` | `audio/` | "See exactly how..." (~5s) |
| `demo_marketing.mp4` | `screen-recordings/` | automation_brain.py terminal demo |
| `demo_comfyui.mp4` | `screen-recordings/` | ComfyUI image generation demo |
| `demo_dashboard.mp4` | `screen-recordings/` | Analytics dashboard walkthrough |
| `stats_animation.mp4` | `canva-exports/` | Stats numbers graphic |
| `calendar_preview.mp4` | `canva-exports/` | Calendar preview mockup |
| `image_montage.mp4` | `canva-exports/` | Quick-cut 5-image montage |
| `ken_burns_slideshow.mp4` | `canva-exports/` | 5-image Ken Burns slideshow |
| `feature_callouts.mp4` | `canva-exports/` | Feature callout boxes animation |
| `cta_text_animation.mp4` | `canva-exports/` | CTA text animation |

Run `python video-production/scripts/setup_environment.py` to see which assets are still missing.

### Normalization Standard

All clips get re-encoded to:
- **Video:** 1920x1080, 30fps, H.264, yuv420p, CRF 23
- **Audio:** AAC, 48kHz, stereo, 192kbps
- **Filters:** scale+pad+fps+setsar+setpts (video), aresample+aformat (audio)

### Output Locations

```
demo-clients/candle-co/
├── video-assets/
│   ├── i2v/          # Raw Wan2.1 clips (Stage 2 output)
│   ├── fantasytalking/ # Raw talking head clips (Stage 2 output)
│   └── normalized/   # All clips standardized (Stage 3 output)
└── final-videos/     # 3 finished MP4s (Stage 4 output)

fiverr-assets/
├── videos/           # Final exports (Stage 5 copies here)
└── thumbnails/       # 1280x720 PNGs (Stage 5 generates)
```

---

### 2026-02-02: FantasyTalking Tested & Approved

**FantasyTalking replaces SadTalker as primary talking head tool.**

**Why switch:**
- SadTalker has teeth distortion issues (confirmed in testing)
- FantasyTalking (Alibaba, Wan2.1 backbone) produces better lip sync
- Better identity preservation, more natural head movements
- ComfyUI-native via WanVideoWrapper (same ecosystem as I2V)

**Test run:**
- Input: `avatar_photo.jpg` + `test_audio.wav` (from `C:\ComfyUI\input\`)
- Output: `FantasyTalking_test_00001-audio.mp4` (512x512, 49 frames @ 24fps, 2.04s)
- Settings: 20 steps, cfg 5.0, unipc scheduler, TeaCache enabled, BlockSwap 15
- Generation time: ~20-25 min on RTX 5060 Ti 16GB
- File size: 271 KB
- Quality: **APPROVED** - good lip sync, no teeth distortion

**Models required for FantasyTalking:**
- `WanVideo\fantasytalking_fp16.safetensors` (1.68GB) - in diffusion_models
- `Wan2.1\wan2.1_i2v_480p_14B_fp8_e4m3fn.safetensors` (16GB) - base I2V model
- `facebook/wav2vec2-base-960h` (~360MB) - auto-downloaded to models/transformers
- `umt5_xxl_fp16.safetensors` - text encoder
- `wan_2.1_vae.safetensors` - VAE
- `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` - vision encoder

**Custom nodes required:**
- ComfyUI-WanVideoWrapper (fantasytalking/ subfolder)
- ComfyUI-KJNodes (ImageResizeKJv2)
- ComfyUI-VideoHelperSuite (VHS_VideoCombine)

**API workflow notes (for `generate_comfyui_assets.py` integration):**
- Use `temp_fantasytalking_test.py` as reference for API format
- Key fix: `WanVideoBlockSwap` needs `vace_blocks_to_swap: 0` explicitly
- `WanVideoTextEncode` uses `positive_prompt`/`negative_prompt` (not `prompt`)
- Node parameter names differ from example workflow (API was updated)
- wav2vec model auto-downloads on first run

**Also confirmed downloaded (GGUF speed upgrade):**
- `wan2.1-i2v-14b-480p-Q5_K_M.gguf` (12.7GB) - quantized I2V model
- `umt5-xxl-encoder-Q5_K_M.gguf` (4.1GB) - quantized text encoder
- ComfyUI-GGUF nodes installed

**Next:** Record production audio scripts, finalize avatar photo, then generate production clips with FantasyTalking.

---
