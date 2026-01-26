#!/bin/bash
# ComfyUI Video Generation Setup Script (Bash version)
# Run this on The Machine (100.64.130.71) via SSH
#
# Usage:
#   ssh michael@100.64.130.71
#   cd /path/to/automation-machine
#   bash setup_comfyui_video.sh

set -e

echo "============================================="
echo "ComfyUI Video Generation Setup"
echo "============================================="
echo ""

# Configuration - adjust these paths for Windows via Git Bash or WSL
COMFYUI_PATH="/c/ComfyUI"  # Git Bash style
CUSTOM_NODES_PATH="$COMFYUI_PATH/custom_nodes"
MODELS_PATH="$COMFYUI_PATH/models"

# For native Windows paths (if running via PowerShell/CMD)
if [ ! -d "$COMFYUI_PATH" ]; then
    COMFYUI_PATH="C:/ComfyUI"
    CUSTOM_NODES_PATH="$COMFYUI_PATH/custom_nodes"
    MODELS_PATH="$COMFYUI_PATH/models"
fi

# Check if ComfyUI exists
if [ ! -d "$COMFYUI_PATH" ]; then
    echo "ERROR: ComfyUI not found at $COMFYUI_PATH"
    echo "Please install ComfyUI first."
    exit 1
fi

echo "ComfyUI found at: $COMFYUI_PATH"
echo ""

cd "$CUSTOM_NODES_PATH"
echo "Working in: $CUSTOM_NODES_PATH"
echo ""

# ============================================
# Step 1: Install VideoHelperSuite
# ============================================
echo "--- Step 1: VideoHelperSuite ---"

if [ -d "$CUSTOM_NODES_PATH/ComfyUI-VideoHelperSuite" ]; then
    echo "VideoHelperSuite already installed."
else
    echo "Installing ComfyUI-VideoHelperSuite..."
    git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git

    if [ -f "ComfyUI-VideoHelperSuite/requirements.txt" ]; then
        echo "Installing dependencies..."
        pip install -r ComfyUI-VideoHelperSuite/requirements.txt
    fi
    echo "VideoHelperSuite installed."
fi
echo ""

# ============================================
# Step 2: Install SadTalker Nodes
# ============================================
echo "--- Step 2: SadTalker (Talking Heads) ---"

SADTALKER_INSTALLED=false
for path in "$CUSTOM_NODES_PATH/ComfyUI-SadTalker" "$CUSTOM_NODES_PATH/SadTalker" "$CUSTOM_NODES_PATH/comfyui-sadtalker"; do
    if [ -d "$path" ]; then
        SADTALKER_INSTALLED=true
        echo "SadTalker found at: $path"
        break
    fi
done

if [ "$SADTALKER_INSTALLED" = false ]; then
    echo "Installing SadTalker nodes..."
    git clone https://github.com/SadTalker/SadTalker.git || echo "WARNING: Could not clone SadTalker"

    if [ -f "SadTalker/requirements.txt" ]; then
        pip install -r SadTalker/requirements.txt || true
    fi
fi
echo ""

# ============================================
# Step 3: Install Wav2Lip Nodes
# ============================================
echo "--- Step 3: Wav2Lip (Alternative Lip Sync) ---"

if [ -d "$CUSTOM_NODES_PATH/ComfyUI-Wav2Lip" ]; then
    echo "Wav2Lip already installed."
else
    echo "Installing Wav2Lip nodes..."
    git clone https://github.com/numz/ComfyUI-Wav2Lip.git || echo "WARNING: Could not install Wav2Lip"

    if [ -f "ComfyUI-Wav2Lip/requirements.txt" ]; then
        pip install -r ComfyUI-Wav2Lip/requirements.txt || true
    fi
fi
echo ""

# ============================================
# Step 4: Install AnimateDiff
# ============================================
echo "--- Step 4: AnimateDiff (Motion Loops) ---"

if [ -d "$CUSTOM_NODES_PATH/ComfyUI-AnimateDiff-Evolved" ]; then
    echo "AnimateDiff already installed."
else
    echo "Installing AnimateDiff nodes..."
    git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git || echo "WARNING: Could not install AnimateDiff"

    if [ -f "ComfyUI-AnimateDiff-Evolved/requirements.txt" ]; then
        pip install -r ComfyUI-AnimateDiff-Evolved/requirements.txt || true
    fi
fi
echo ""

# ============================================
# Step 5: Create model directories
# ============================================
echo "Creating model directories..."

mkdir -p "$MODELS_PATH/sadtalker"
mkdir -p "$MODELS_PATH/animatediff_models"
mkdir -p "$MODELS_PATH/facerestore_models"

echo "Model directories created."
echo ""

# ============================================
# Summary
# ============================================
echo "============================================="
echo "SETUP COMPLETE"
echo "============================================="
echo ""

echo "Installed nodes:"
echo "  - ComfyUI-VideoHelperSuite (video I/O)"
echo "  - SadTalker (talking heads)"
echo "  - Wav2Lip (lip sync alternative)"
echo "  - AnimateDiff (motion loops)"
echo ""

echo "MODELS NEEDED (download manually):"
echo ""
echo "1. Wan2.1 Image-to-Video:"
echo "   https://huggingface.co/Wan-AI/Wan2.1-I2V-14B-480P"
echo "   -> $MODELS_PATH/checkpoints/"
echo ""
echo "2. SadTalker Models:"
echo "   https://github.com/OpenTalker/SadTalker"
echo "   -> $MODELS_PATH/sadtalker/"
echo ""
echo "3. AnimateDiff Motion Models:"
echo "   https://huggingface.co/guoyww/animatediff"
echo "   -> $MODELS_PATH/animatediff_models/"
echo ""
echo "4. GFPGAN Face Restoration:"
echo "   https://github.com/TencentARC/GFPGAN"
echo "   -> $MODELS_PATH/facerestore_models/"
echo ""

echo "Next steps:"
echo "  1. Download models"
echo "  2. Restart ComfyUI"
echo "  3. Test: python automation_brain.py 'animate this image'"
echo ""
