# ComfyUI Video Generation Setup Script
# Run this on The Machine (100.64.130.71) to set up video generation capabilities
#
# Usage:
#   1. SSH to The Machine: ssh michael@100.64.130.71
#   2. Copy this script to The Machine
#   3. Run: powershell -ExecutionPolicy Bypass -File setup_comfyui_video.ps1

$ErrorActionPreference = "Stop"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "ComfyUI Video Generation Setup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$COMFYUI_PATH = "C:\ComfyUI"
$CUSTOM_NODES_PATH = "$COMFYUI_PATH\custom_nodes"
$MODELS_PATH = "$COMFYUI_PATH\models"

# Check if ComfyUI exists
if (-not (Test-Path $COMFYUI_PATH)) {
    Write-Host "ERROR: ComfyUI not found at $COMFYUI_PATH" -ForegroundColor Red
    Write-Host "Please install ComfyUI first." -ForegroundColor Red
    exit 1
}

Write-Host "ComfyUI found at: $COMFYUI_PATH" -ForegroundColor Green
Write-Host ""

# Navigate to custom_nodes
Set-Location $CUSTOM_NODES_PATH
Write-Host "Working in: $CUSTOM_NODES_PATH" -ForegroundColor Yellow
Write-Host ""

# ============================================
# Step 1: Install VideoHelperSuite
# ============================================
Write-Host "--- Step 1: VideoHelperSuite ---" -ForegroundColor Cyan

if (Test-Path "$CUSTOM_NODES_PATH\ComfyUI-VideoHelperSuite") {
    Write-Host "VideoHelperSuite already installed." -ForegroundColor Green
} else {
    Write-Host "Installing ComfyUI-VideoHelperSuite..." -ForegroundColor Yellow
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git

    # Install requirements
    if (Test-Path "$CUSTOM_NODES_PATH\ComfyUI-VideoHelperSuite\requirements.txt") {
        Write-Host "Installing VideoHelperSuite dependencies..." -ForegroundColor Yellow
        pip install -r "$CUSTOM_NODES_PATH\ComfyUI-VideoHelperSuite\requirements.txt"
    }
    Write-Host "VideoHelperSuite installed." -ForegroundColor Green
}
Write-Host ""

# ============================================
# Step 2: Install SadTalker Nodes
# ============================================
Write-Host "--- Step 2: SadTalker (Talking Heads) ---" -ForegroundColor Cyan

# Check for SadTalker or compatible node pack
$sadtalker_installed = $false
$sadtalker_paths = @(
    "$CUSTOM_NODES_PATH\ComfyUI-SadTalker",
    "$CUSTOM_NODES_PATH\comfyui-sadtalker",
    "$CUSTOM_NODES_PATH\SadTalker"
)

foreach ($path in $sadtalker_paths) {
    if (Test-Path $path) {
        $sadtalker_installed = $true
        Write-Host "SadTalker found at: $path" -ForegroundColor Green
        break
    }
}

if (-not $sadtalker_installed) {
    Write-Host "Installing SadTalker nodes..." -ForegroundColor Yellow
    Write-Host "NOTE: SadTalker may require manual model download." -ForegroundColor Yellow

    # Try official SadTalker ComfyUI wrapper
    try {
        git clone https://github.com/SadTalker/SadTalker.git "$CUSTOM_NODES_PATH\SadTalker"
        Write-Host "SadTalker cloned. Installing dependencies..." -ForegroundColor Yellow

        if (Test-Path "$CUSTOM_NODES_PATH\SadTalker\requirements.txt") {
            pip install -r "$CUSTOM_NODES_PATH\SadTalker\requirements.txt"
        }
        Write-Host "SadTalker installed." -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Could not clone SadTalker. Try installing via ComfyUI Manager." -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================
# Step 3: Install Wav2Lip Nodes (Alternative)
# ============================================
Write-Host "--- Step 3: Wav2Lip (Alternative Lip Sync) ---" -ForegroundColor Cyan

if (Test-Path "$CUSTOM_NODES_PATH\ComfyUI-Wav2Lip") {
    Write-Host "Wav2Lip already installed." -ForegroundColor Green
} else {
    Write-Host "Installing Wav2Lip nodes..." -ForegroundColor Yellow
    try {
        git clone https://github.com/numz/ComfyUI-Wav2Lip.git "$CUSTOM_NODES_PATH\ComfyUI-Wav2Lip"

        if (Test-Path "$CUSTOM_NODES_PATH\ComfyUI-Wav2Lip\requirements.txt") {
            pip install -r "$CUSTOM_NODES_PATH\ComfyUI-Wav2Lip\requirements.txt"
        }
        Write-Host "Wav2Lip installed." -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Could not install Wav2Lip. Try ComfyUI Manager." -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================
# Step 4: Install AnimateDiff (Optional)
# ============================================
Write-Host "--- Step 4: AnimateDiff (Motion Loops) ---" -ForegroundColor Cyan

if (Test-Path "$CUSTOM_NODES_PATH\ComfyUI-AnimateDiff-Evolved") {
    Write-Host "AnimateDiff already installed." -ForegroundColor Green
} else {
    Write-Host "Installing AnimateDiff nodes..." -ForegroundColor Yellow
    try {
        git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git

        if (Test-Path "$CUSTOM_NODES_PATH\ComfyUI-AnimateDiff-Evolved\requirements.txt") {
            pip install -r "$CUSTOM_NODES_PATH\ComfyUI-AnimateDiff-Evolved\requirements.txt"
        }
        Write-Host "AnimateDiff installed." -ForegroundColor Green
    } catch {
        Write-Host "WARNING: Could not install AnimateDiff." -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================
# Step 5: Model Download Instructions
# ============================================
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "MODEL DOWNLOAD REQUIRED" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "The following models need to be downloaded manually:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Wan2.1 Image-to-Video (for image animation):" -ForegroundColor White
Write-Host "   - Download: wan2.1_i2v_480p_14B_bf16.safetensors" -ForegroundColor Gray
Write-Host "   - Place in: $MODELS_PATH\checkpoints\" -ForegroundColor Gray
Write-Host "   - Source: https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P" -ForegroundColor Gray
Write-Host ""

Write-Host "2. SadTalker Models (for talking heads):" -ForegroundColor White
Write-Host "   - Download from: https://github.com/OpenTalker/SadTalker" -ForegroundColor Gray
Write-Host "   - Required files:" -ForegroundColor Gray
Write-Host "     * SadTalker_V0.0.2_512.safetensors" -ForegroundColor Gray
Write-Host "     * mapping_00109-model.pth.tar" -ForegroundColor Gray
Write-Host "     * mapping_00229-model.pth.tar" -ForegroundColor Gray
Write-Host "   - Place in: $MODELS_PATH\sadtalker\" -ForegroundColor Gray
Write-Host ""

Write-Host "3. AnimateDiff Motion Models (optional):" -ForegroundColor White
Write-Host "   - Download: mm_sdxl_v10_beta.ckpt" -ForegroundColor Gray
Write-Host "   - Place in: $MODELS_PATH\animatediff_models\" -ForegroundColor Gray
Write-Host "   - Source: https://huggingface.co/guoyww/animatediff" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Face Restoration (GFPGAN) for SadTalker:" -ForegroundColor White
Write-Host "   - Download: GFPGANv1.4.pth" -ForegroundColor Gray
Write-Host "   - Place in: $MODELS_PATH\facerestore_models\" -ForegroundColor Gray
Write-Host "   - Source: https://github.com/TencentARC/GFPGAN" -ForegroundColor Gray
Write-Host ""

# ============================================
# Step 6: Create model directories
# ============================================
Write-Host "Creating model directories..." -ForegroundColor Yellow

$model_dirs = @(
    "$MODELS_PATH\sadtalker",
    "$MODELS_PATH\animatediff_models",
    "$MODELS_PATH\facerestore_models"
)

foreach ($dir in $model_dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    }
}
Write-Host ""

# ============================================
# Summary
# ============================================
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Installed nodes:" -ForegroundColor Green
Write-Host "  - ComfyUI-VideoHelperSuite (video I/O)" -ForegroundColor White
Write-Host "  - SadTalker (talking heads)" -ForegroundColor White
Write-Host "  - Wav2Lip (lip sync alternative)" -ForegroundColor White
Write-Host "  - AnimateDiff (motion loops)" -ForegroundColor White
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Download required models (see above)" -ForegroundColor White
Write-Host "  2. Restart ComfyUI to load new nodes" -ForegroundColor White
Write-Host "  3. Test with: python automation_brain.py 'animate this candle image'" -ForegroundColor White
Write-Host ""

Write-Host "Verification commands:" -ForegroundColor Yellow
Write-Host "  - Check nodes: dir $CUSTOM_NODES_PATH" -ForegroundColor Gray
Write-Host "  - Check models: dir $MODELS_PATH" -ForegroundColor Gray
Write-Host ""

Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  - VIDEO-PRODUCTION.md in automation-machine repo" -ForegroundColor Gray
Write-Host "  - workflows/image_to_video.json" -ForegroundColor Gray
Write-Host "  - workflows/talking_head.json" -ForegroundColor Gray
Write-Host ""
