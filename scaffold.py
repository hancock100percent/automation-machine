"""
Universal Project Scaffold -- Create new projects from the automation-machine template.

Usage:
    python scaffold.py                                          # Interactive mode
    python scaffold.py --name "my-project" --type generic       # Quick mode
    python scaffold.py --name "my-project" --dry-run            # Preview only
    python scaffold.py --list-types                             # Show project types

Creates a new project at C:\\<project-name>\\ with:
- CLAUDE.md, SESSION-LOG.md, HANDOFF.md (filled placeholders)
- config.yaml, tools_config.json, usage_log.json
- knowledge-base/, agents/, state/, scripts/
- Git repo initialized with initial commit
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent
TEMPLATE_DIR = SCRIPT_DIR / "project-template"
TARGET_ROOT = Path("C:\\")

# Project type definitions with starter checklists
PROJECT_TYPES = {
    "client": {
        "label": "Client Project",
        "description": "Client deliverable with assets, demos, and delivery milestones",
        "checklist": [
            "- [ ] Gather client requirements and assets",
            "- [ ] Define deliverables and timeline",
            "- [ ] Create initial demos/mockups",
            "- [ ] Client review and feedback",
            "- [ ] Final delivery and handoff",
        ],
        "focus": "Deliver client project on time and to spec",
        "business_context": "Client engagement -- deliver value, earn review",
    },
    "saas": {
        "label": "SaaS Product",
        "description": "Software-as-a-service product with backend, frontend, and deployment",
        "checklist": [
            "- [ ] Define MVP feature set",
            "- [ ] Set up backend (API, database, auth)",
            "- [ ] Build frontend (UI, routing, state)",
            "- [ ] Deploy to staging environment",
            "- [ ] Launch and gather feedback",
        ],
        "focus": "Ship MVP and validate with real users",
        "business_context": "Product development -- build, ship, iterate",
    },
    "learning": {
        "label": "Learning / Certification",
        "description": "Study track for certification or skill development",
        "checklist": [
            "- [ ] Define curriculum and study plan",
            "- [ ] Create/gather study materials",
            "- [ ] Complete practice exercises",
            "- [ ] Take practice exams",
            "- [ ] Pass certification exam",
        ],
        "focus": "Complete certification study track",
        "business_context": "Skill development -- expand service offerings",
    },
    "generic": {
        "label": "Generic Project",
        "description": "General-purpose project template",
        "checklist": [
            "- [ ] Research and define scope",
            "- [ ] Plan implementation approach",
            "- [ ] Build core functionality",
            "- [ ] Test and validate",
            "- [ ] Ship and document",
        ],
        "focus": "Define scope and deliver results",
        "business_context": "General project -- define and execute",
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_kebab(name: str) -> str:
    """Convert a name to kebab-case (lowercase, hyphens)."""
    return name.lower().strip().replace(" ", "-").replace("_", "-")


def to_title(name: str) -> str:
    """Convert kebab-case to Title Case."""
    return name.replace("-", " ").replace("_", " ").title()


def prompt_input(label: str, default: str = "") -> str:
    """Prompt user for input with optional default."""
    if default:
        val = input(f"  {label} [{default}]: ").strip()
        return val if val else default
    while True:
        val = input(f"  {label}: ").strip()
        if val:
            return val
        print("    (required)")


def prompt_choice(label: str, choices: dict) -> str:
    """Prompt user to pick from choices."""
    print(f"\n  {label}:")
    keys = list(choices.keys())
    for i, key in enumerate(keys, 1):
        info = choices[key]
        print(f"    {i}. {info['label']} -- {info['description']}")
    while True:
        val = input(f"  Choice [1-{len(keys)}]: ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            if val in keys:
                return val
        print(f"    (pick 1-{len(keys)})")


def fill_placeholders(content: str, placeholders: dict) -> str:
    """Replace all {{PLACEHOLDER}} tokens in content."""
    for key, value in placeholders.items():
        content = content.replace("{{" + key + "}}", str(value))
    return content


def is_text_file(path: Path) -> bool:
    """Check if a file is likely a text file (safe to do placeholder replacement)."""
    text_extensions = {
        ".md", ".txt", ".json", ".yaml", ".yml", ".py", ".ps1",
        ".sh", ".bat", ".cfg", ".ini", ".toml", ".gitignore",
        ".gitkeep", ".csv", ".html", ".css", ".js", ".ts",
    }
    if path.suffix.lower() in text_extensions:
        return True
    if path.name in {".gitignore", ".gitkeep", ".env.example"}:
        return True
    return False


# ---------------------------------------------------------------------------
# Core Logic
# ---------------------------------------------------------------------------

def gather_inputs(args) -> dict:
    """Gather all inputs either from args or interactively."""
    print("\n  === Universal Project Scaffold ===\n")

    # Determine if we're in non-interactive mode (name + type both provided)
    non_interactive = bool(args.name and args.type)

    # Project name
    if args.name:
        name = to_kebab(args.name)
    else:
        raw = prompt_input("Project name (kebab-case)")
        name = to_kebab(raw)

    # Project type
    if args.type:
        ptype = args.type
        if ptype not in PROJECT_TYPES:
            print(f"  Unknown type '{ptype}'. Valid: {', '.join(PROJECT_TYPES.keys())}")
            sys.exit(1)
    else:
        ptype = prompt_choice("Project type", PROJECT_TYPES)

    type_info = PROJECT_TYPES[ptype]

    # Description
    if args.description:
        description = args.description
    elif non_interactive:
        description = type_info["description"]
    else:
        description = prompt_input("One-line description", type_info["description"])

    # Goal
    if args.goal:
        goal = args.goal
    elif non_interactive:
        goal = type_info["focus"]
    else:
        goal = prompt_input("Goal statement", type_info["focus"])

    # Business context
    if args.context:
        business_context = args.context
    elif non_interactive:
        business_context = type_info["business_context"]
    else:
        business_context = prompt_input("Business context", type_info["business_context"])

    # Architecture notes
    if args.architecture:
        architecture = args.architecture
    elif non_interactive:
        architecture = "Local-first development with cloud fallback"
    else:
        architecture = prompt_input(
            "Architecture notes (or press Enter for default)",
            "Local-first development with cloud fallback"
        )

    # Budget
    daily = args.daily_budget or 5
    monthly = args.monthly_budget or 50

    today = datetime.now().strftime("%Y-%m-%d")

    return {
        "name": name,
        "type": ptype,
        "placeholders": {
            "PROJECT_NAME": to_title(name),
            "PROJECT_NAME_KEBAB": name,
            "PROJECT_DESCRIPTION": description,
            "PROJECT_GOAL": goal,
            "BUSINESS_CONTEXT": business_context,
            "ARCHITECTURE_NOTES": architecture,
            "CURRENT_FOCUS": type_info["focus"],
            "CHECKLIST": "\n".join(type_info["checklist"]),
            "DAILY_BUDGET": str(daily),
            "MONTHLY_BUDGET": str(monthly),
            "MONTHLY_BUDGET_WARNING": str(int(monthly * 0.6)),
            "DATE": today,
        },
    }


def scaffold_project(inputs: dict, dry_run: bool = False) -> Path:
    """Copy template to target directory and fill placeholders."""
    name = inputs["name"]
    target = TARGET_ROOT / name
    placeholders = inputs["placeholders"]

    # Safety checks
    if target.exists():
        # Allow scaffolding into an existing directory if it has no real files
        existing = [p for p in target.rglob("*") if p.is_file()]
        if existing:
            print(f"\n  ERROR: Directory already exists and contains files: {target}")
            for p in existing[:10]:
                print(f"    {p.relative_to(target)}")
            if len(existing) > 10:
                print(f"    ... and {len(existing) - 10} more")
            print("  Remove them first or choose a different name.")
            sys.exit(1)
        print(f"  (directory exists but is empty -- scaffolding into it)")

    if not TEMPLATE_DIR.exists():
        print(f"\n  ERROR: Template directory not found: {TEMPLATE_DIR}")
        print("  Run this script from the automation-machine directory.")
        sys.exit(1)

    # Preview
    print(f"\n  === Scaffold Preview ===")
    print(f"  Project:     {placeholders['PROJECT_NAME']}")
    print(f"  Directory:   {target}")
    print(f"  Type:        {inputs['type']}")
    print(f"  Description: {placeholders['PROJECT_DESCRIPTION']}")
    print(f"  Budget:      ${placeholders['DAILY_BUDGET']}/day, ${placeholders['MONTHLY_BUDGET']}/month")
    print()

    if dry_run:
        print("  [DRY RUN] Files that would be created:\n")
        for root, dirs, files in os.walk(TEMPLATE_DIR):
            rel_root = Path(root).relative_to(TEMPLATE_DIR)
            for f in sorted(files):
                rel_path = rel_root / f
                print(f"    {target / rel_path}")
        print(f"\n  [DRY RUN] No files were created.")
        return target

    # Copy template tree
    print(f"  Copying template to {target}...")
    shutil.copytree(str(TEMPLATE_DIR), str(target), dirs_exist_ok=True)

    # Fill placeholders in all text files
    filled_count = 0
    for root, dirs, files in os.walk(target):
        for f in files:
            fpath = Path(root) / f
            if is_text_file(fpath):
                try:
                    content = fpath.read_text(encoding="utf-8")
                    new_content = fill_placeholders(content, placeholders)
                    if new_content != content:
                        fpath.write_text(new_content, encoding="utf-8")
                        filled_count += 1
                except (UnicodeDecodeError, PermissionError):
                    pass  # Skip binary or locked files

    print(f"  Filled placeholders in {filled_count} files.")

    # Initialize git
    print("  Initializing git repository...")
    try:
        subprocess.run(
            ["git", "init"],
            cwd=str(target),
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(target),
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"Initial scaffold: {placeholders['PROJECT_NAME']}"],
            cwd=str(target),
            capture_output=True,
            text=True,
            check=True,
        )
        print("  Git repo initialized with initial commit.")
    except FileNotFoundError:
        print("  WARNING: git not found -- skipping repo init.")
    except subprocess.CalledProcessError as e:
        print(f"  WARNING: git command failed: {e.stderr.strip()}")

    return target


def print_summary(target: Path, inputs: dict):
    """Print post-scaffold summary and next steps."""
    name = inputs["placeholders"]["PROJECT_NAME"]
    print(f"\n  === {name} -- Ready! ===\n")
    print(f"  Location: {target}")
    print(f"  Type:     {inputs['type']}")
    print()
    print("  Next steps:")
    print(f"    1. cd {target}")
    print(f"    2. Open in your editor")
    print(f"    3. Read CLAUDE.md (your project bible)")
    print(f"    4. Update SESSION-LOG.md as you work")
    print(f"    5. (Optional) Set up agents in agents/")
    print()
    print(f"  To use with Claude Code:")
    print(f"    cd {target}")
    print(f"    claude")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Universal Project Scaffold -- create new projects from template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scaffold.py                                    # Interactive
  python scaffold.py --name "my-app" --type saas        # Quick
  python scaffold.py --name "test" --dry-run             # Preview
  python scaffold.py --list-types                        # Show types
        """,
    )
    parser.add_argument("--name", help="Project name (kebab-case)")
    parser.add_argument("--type", choices=PROJECT_TYPES.keys(), help="Project type")
    parser.add_argument("--description", help="One-line project description")
    parser.add_argument("--goal", help="Project goal statement")
    parser.add_argument("--context", help="Business context")
    parser.add_argument("--architecture", help="Architecture notes")
    parser.add_argument("--daily-budget", type=float, help="Daily budget in USD (default: 5)")
    parser.add_argument("--monthly-budget", type=float, help="Monthly budget in USD (default: 50)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    parser.add_argument("--list-types", action="store_true", help="List available project types")

    args = parser.parse_args()

    if args.list_types:
        print("\n  Available project types:\n")
        for key, info in PROJECT_TYPES.items():
            print(f"    {key:10s}  {info['label']} -- {info['description']}")
        print()
        sys.exit(0)

    inputs = gather_inputs(args)
    target = scaffold_project(inputs, dry_run=args.dry_run)

    if not args.dry_run:
        print_summary(target, inputs)


if __name__ == "__main__":
    main()
