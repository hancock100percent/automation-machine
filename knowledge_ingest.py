#!/usr/bin/env python3
"""
Knowledge Ingestion Pipeline for Automation Machine

Ingests content from various sources (YouTube, podcasts, PDFs, books)
and transforms them into structured training documents for the knowledge base.

Tools:
- YouTube: yt-dlp + faster-whisper (local transcription)
- Podcasts: faster-whisper (local transcription)
- PDFs: pdfplumber (local extraction)
- Summarization: Ollama (local LLM)

Cost: $0 (100% local processing)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

# Paths
BASE_DIR = Path("C:/automation-machine")
KNOWLEDGE_BASE = BASE_DIR / "knowledge-base"
TRAINING_DIR = KNOWLEDGE_BASE / "training"
CONFIG_PATH = BASE_DIR / "config.yaml"

# Ensure directories exist
TRAINING_DIR.mkdir(parents=True, exist_ok=True)


class KnowledgeIngestor:
    """
    Pipeline for ingesting knowledge from various sources.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.ollama_endpoint = "http://localhost:11434"
        self.summarization_model = "qwen2.5:32b"

    def _log(self, message: str) -> None:
        """Print verbose logging if enabled."""
        if self.verbose:
            print(f"[Ingest] {message}")

    def _call_ollama(self, prompt: str, model: Optional[str] = None) -> str:
        """Call local Ollama for summarization."""
        model = model or self.summarization_model

        try:
            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300  # 5 min timeout for long summaries
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            self._log(f"Ollama error: {e}")
            return f"[Summarization failed: {e}]"

    # =========================================================================
    # YouTube Ingestion
    # =========================================================================

    def ingest_youtube(self, url: str, output_path: Optional[Path] = None) -> Path:
        """
        Ingest a YouTube video:
        1. Download audio with yt-dlp
        2. Transcribe with faster-whisper
        3. Summarize with Ollama
        4. Save as training document
        """
        self._log(f"Ingesting YouTube: {url}")

        # Create temp directory for audio
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "audio.wav"

            # Step 1: Download audio
            self._log("Downloading audio with yt-dlp...")
            try:
                result = subprocess.run([
                    "yt-dlp",
                    "-x",  # Extract audio
                    "--audio-format", "wav",
                    "--audio-quality", "0",
                    "-o", str(audio_path.with_suffix("")),  # yt-dlp adds extension
                    "--no-playlist",
                    url
                ], capture_output=True, text=True, timeout=300)

                if result.returncode != 0:
                    raise RuntimeError(f"yt-dlp failed: {result.stderr}")

                # Find the actual output file (might have different extension)
                audio_files = list(Path(temp_dir).glob("audio.*"))
                if not audio_files:
                    raise RuntimeError("No audio file downloaded")
                audio_path = audio_files[0]

            except FileNotFoundError:
                print("ERROR: yt-dlp not installed. Install with: pip install yt-dlp")
                sys.exit(1)

            # Get video metadata
            self._log("Fetching video metadata...")
            try:
                meta_result = subprocess.run([
                    "yt-dlp",
                    "--dump-json",
                    "--no-download",
                    url
                ], capture_output=True, text=True, timeout=60)

                metadata = json.loads(meta_result.stdout) if meta_result.returncode == 0 else {}
            except Exception:
                metadata = {}

            title = metadata.get("title", "Unknown Video")
            channel = metadata.get("channel", "Unknown Channel")
            duration = metadata.get("duration", 0)

            # Step 2: Transcribe with faster-whisper
            self._log("Transcribing with faster-whisper...")
            transcript = self._transcribe_audio(audio_path)

            if not transcript:
                print("ERROR: Transcription failed")
                sys.exit(1)

        # Step 3: Summarize with Ollama
        self._log("Summarizing with Ollama...")
        summary = self._summarize_content(transcript, title, "YouTube video")

        # Step 4: Generate training document
        output_path = output_path or TRAINING_DIR / f"youtube_{self._slugify(title)}.md"

        doc_content = self._format_training_doc(
            title=title,
            source=url,
            source_type="YouTube",
            metadata={
                "channel": channel,
                "duration": f"{duration // 60}:{duration % 60:02d}" if duration else "Unknown"
            },
            transcript=transcript,
            summary=summary
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(doc_content, encoding="utf-8")

        self._log(f"Saved to: {output_path}")
        return output_path

    # =========================================================================
    # Podcast/Audio Ingestion
    # =========================================================================

    def ingest_audio(self, audio_path: str, output_path: Optional[Path] = None,
                     title: Optional[str] = None) -> Path:
        """
        Ingest an audio file (podcast, audiobook, etc.):
        1. Transcribe with faster-whisper
        2. Summarize with Ollama
        3. Save as training document
        """
        audio_file = Path(audio_path)
        if not audio_file.exists():
            print(f"ERROR: Audio file not found: {audio_path}")
            sys.exit(1)

        title = title or audio_file.stem
        self._log(f"Ingesting audio: {title}")

        # Step 1: Transcribe
        self._log("Transcribing with faster-whisper...")
        transcript = self._transcribe_audio(audio_file)

        if not transcript:
            print("ERROR: Transcription failed")
            sys.exit(1)

        # Step 2: Summarize
        self._log("Summarizing with Ollama...")
        summary = self._summarize_content(transcript, title, "Podcast/Audio")

        # Step 3: Generate training document
        output_path = output_path or TRAINING_DIR / f"audio_{self._slugify(title)}.md"

        doc_content = self._format_training_doc(
            title=title,
            source=str(audio_file),
            source_type="Podcast/Audio",
            metadata={
                "format": audio_file.suffix,
                "size": f"{audio_file.stat().st_size / (1024*1024):.1f} MB"
            },
            transcript=transcript,
            summary=summary
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(doc_content, encoding="utf-8")

        self._log(f"Saved to: {output_path}")
        return output_path

    # =========================================================================
    # PDF Ingestion
    # =========================================================================

    def ingest_pdf(self, pdf_path: str, output_path: Optional[Path] = None,
                   title: Optional[str] = None) -> Path:
        """
        Ingest a PDF document:
        1. Extract text with pdfplumber
        2. Summarize with Ollama
        3. Save as training document
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"ERROR: PDF file not found: {pdf_path}")
            sys.exit(1)

        title = title or pdf_file.stem
        self._log(f"Ingesting PDF: {title}")

        # Step 1: Extract text
        self._log("Extracting text with pdfplumber...")
        try:
            import pdfplumber
        except ImportError:
            print("ERROR: pdfplumber not installed. Install with: pip install pdfplumber")
            sys.exit(1)

        text_content = []
        page_count = 0

        with pdfplumber.open(pdf_file) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)

        full_text = "\n\n".join(text_content)

        if not full_text.strip():
            print("ERROR: No text extracted from PDF (may be image-based)")
            sys.exit(1)

        # Step 2: Summarize (chunk if too long)
        self._log("Summarizing with Ollama...")
        summary = self._summarize_content(full_text, title, "PDF Document")

        # Step 3: Generate training document
        output_path = output_path or TRAINING_DIR / f"pdf_{self._slugify(title)}.md"

        doc_content = self._format_training_doc(
            title=title,
            source=str(pdf_file),
            source_type="PDF Document",
            metadata={
                "pages": str(page_count),
                "size": f"{pdf_file.stat().st_size / (1024*1024):.1f} MB"
            },
            transcript=full_text[:50000],  # Limit to first 50k chars
            summary=summary
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(doc_content, encoding="utf-8")

        self._log(f"Saved to: {output_path}")
        return output_path

    # =========================================================================
    # Web Article Ingestion
    # =========================================================================

    def ingest_web(self, url: str, output_path: Optional[Path] = None) -> Path:
        """
        Ingest a web article:
        1. Fetch and parse with trafilatura
        2. Summarize with Ollama
        3. Save as training document
        """
        self._log(f"Ingesting web article: {url}")

        try:
            import trafilatura
        except ImportError:
            print("ERROR: trafilatura not installed. Install with: pip install trafilatura")
            sys.exit(1)

        # Fetch and extract
        self._log("Fetching and extracting content...")
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            print("ERROR: Failed to fetch URL")
            sys.exit(1)

        text = trafilatura.extract(downloaded, include_comments=False)
        metadata = trafilatura.extract_metadata(downloaded)

        if not text:
            print("ERROR: Failed to extract text from page")
            sys.exit(1)

        title = metadata.title if metadata else url.split("/")[-1]

        # Summarize
        self._log("Summarizing with Ollama...")
        summary = self._summarize_content(text, title, "Web Article")

        # Generate training document
        output_path = output_path or TRAINING_DIR / f"web_{self._slugify(title)}.md"

        doc_content = self._format_training_doc(
            title=title,
            source=url,
            source_type="Web Article",
            metadata={
                "author": metadata.author if metadata else "Unknown",
                "date": metadata.date if metadata else "Unknown"
            },
            transcript=text,
            summary=summary
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(doc_content, encoding="utf-8")

        self._log(f"Saved to: {output_path}")
        return output_path

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _transcribe_audio(self, audio_path: Path) -> str:
        """Transcribe audio using faster-whisper."""
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            print("ERROR: faster-whisper not installed.")
            print("Install with: pip install faster-whisper")
            print("Also requires: pip install torch (with CUDA for GPU support)")
            sys.exit(1)

        # Use small model for speed, medium for accuracy
        model_size = "small"  # Options: tiny, base, small, medium, large-v2

        self._log(f"Loading Whisper model: {model_size}")
        model = WhisperModel(model_size, device="cuda", compute_type="float16")

        self._log("Transcribing...")
        segments, info = model.transcribe(str(audio_path), beam_size=5)

        transcript_parts = []
        for segment in segments:
            transcript_parts.append(segment.text)

        return " ".join(transcript_parts)

    def _summarize_content(self, content: str, title: str, source_type: str) -> dict:
        """
        Summarize content using Ollama.
        Returns dict with key_takeaways, detailed_summary, actionable_items.
        """
        # Chunk content if too long (8k token limit approximation)
        max_chars = 24000  # ~6k tokens
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[Content truncated for summarization...]"

        prompt = f"""Analyze this {source_type} titled "{title}" and provide:

1. KEY TAKEAWAYS (3-7 bullet points of the most important insights)
2. DETAILED SUMMARY (2-4 paragraphs covering the main content)
3. ACTIONABLE ITEMS (specific tasks or next steps based on the content)

Format your response exactly as:
## Key Takeaways
- [takeaway 1]
- [takeaway 2]
...

## Detailed Summary
[paragraphs]

## Actionable Items
- [ ] [task 1]
- [ ] [task 2]
...

Content to analyze:
{content}"""

        response = self._call_ollama(prompt)

        # Parse response into sections
        sections = {
            "key_takeaways": "",
            "detailed_summary": "",
            "actionable_items": ""
        }

        # Simple parsing
        if "## Key Takeaways" in response:
            parts = response.split("## Key Takeaways")
            if len(parts) > 1:
                rest = parts[1]
                if "## Detailed Summary" in rest:
                    sections["key_takeaways"], rest = rest.split("## Detailed Summary", 1)
                    if "## Actionable Items" in rest:
                        sections["detailed_summary"], sections["actionable_items"] = rest.split("## Actionable Items", 1)
                    else:
                        sections["detailed_summary"] = rest
                else:
                    sections["key_takeaways"] = rest
        else:
            # Fallback: just use the whole response as summary
            sections["detailed_summary"] = response

        return sections

    def _format_training_doc(self, title: str, source: str, source_type: str,
                            metadata: dict, transcript: str, summary: dict) -> str:
        """Format the training document in markdown."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        meta_lines = "\n".join(f"**{k.title()}:** {v}" for k, v in metadata.items())

        return f"""# Training Document: {title}

**Source:** {source}
**Type:** {source_type}
**Processed:** {timestamp}

{meta_lines}

---

## Key Takeaways
{summary.get('key_takeaways', '- [No takeaways extracted]').strip()}

## Detailed Summary
{summary.get('detailed_summary', '[No summary generated]').strip()}

## Actionable Items
{summary.get('actionable_items', '- [ ] Review content manually').strip()}

---

## Full Transcript/Content

<details>
<summary>Click to expand full content ({len(transcript)} characters)</summary>

{transcript}

</details>

---

*Generated by Automation Machine Knowledge Pipeline*
"""

    def _slugify(self, text: str) -> str:
        """Convert text to a safe filename slug."""
        # Remove special characters, replace spaces with underscores
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[-\s]+', '_', slug)
        return slug[:50]  # Limit length


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Knowledge Ingestion Pipeline - Transform content into training documents"
    )

    # Source type (mutually exclusive)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--youtube", metavar="URL",
                              help="Ingest YouTube video by URL")
    source_group.add_argument("--audio", metavar="PATH",
                              help="Ingest audio file (podcast, audiobook)")
    source_group.add_argument("--pdf", metavar="PATH",
                              help="Ingest PDF document")
    source_group.add_argument("--web", metavar="URL",
                              help="Ingest web article by URL")
    source_group.add_argument("--list", action="store_true",
                              help="List all training documents")

    # Options
    parser.add_argument("--output", "-o", metavar="PATH",
                        help="Output path for training document")
    parser.add_argument("--title", "-t", metavar="TITLE",
                        help="Custom title for the document")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose output")

    args = parser.parse_args()

    ingestor = KnowledgeIngestor(verbose=args.verbose)

    output_path = Path(args.output) if args.output else None

    if args.list:
        # List existing training documents
        print("\n=== Training Documents ===\n")
        for doc in sorted(TRAINING_DIR.glob("*.md")):
            stat = doc.stat()
            size = stat.st_size / 1024
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
            print(f"  {doc.name:50} {size:>6.1f} KB  {mtime}")
        print()
        return

    if args.youtube:
        result = ingestor.ingest_youtube(args.youtube, output_path)
    elif args.audio:
        result = ingestor.ingest_audio(args.audio, output_path, args.title)
    elif args.pdf:
        result = ingestor.ingest_pdf(args.pdf, output_path, args.title)
    elif args.web:
        result = ingestor.ingest_web(args.web, output_path)

    print(f"\n✓ Training document created: {result}")
    print(f"  Location: {result}")
    print(f"  Size: {result.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
