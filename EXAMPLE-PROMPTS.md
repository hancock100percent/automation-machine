# Example Prompts for Automation Machine

## Starting a New Session

### Full Handoff (Recommended)

```
Resume Automation Machine work at C:\automation-machine\

Read HANDOFF.md first, then:
1. Check auto_doc_state.json and usage_log.json
2. Read ACTIVE-PROJECTS.md for current status
3. State what you found and confirm next action
4. Execute
```

### Quick Resume

```
Continue Automation Machine. Check handoff protocol at C:\automation-machine\HANDOFF.md
```

### Minimal (If Context Already Exists)

```
Check C:\automation-machine\knowledge-base\ACTIVE-PROJECTS.md and continue next task.
```

---

## End of Day

### Update Projects with Summary

```
Run: python auto_doc.py --update-projects --eod "Completed X, Y, Z. Next: A, B"
```

### Just Update Timestamp

```
python auto_doc.py --update-projects
```

---

## Specific Task Prompts

### ComfyUI Integration

```
Continue Automation Machine. Focus on ComfyUI integration:
- Connect to The Machine at 100.64.130.71
- REST API integration for automation_brain.py
- Test with a simple workflow
```

### Fiverr Gig Setup

```
Continue Automation Machine. Focus on Fiverr launch:
- Review what demo images we need
- Define the two gig strategy specifics
- Don't over-build, ship fast
```

### Debug/Fix Something

```
Resume Automation Machine at C:\automation-machine\
Issue: [describe problem]
Check relevant files and fix.
```

---

## Command Reference

```bash
# Check system state
python auto_doc.py --status

# Update active projects
python auto_doc.py --update-projects
python auto_doc.py --update-projects --eod "Summary here"

# Run queries
python automation_brain.py "your query"
python automation_brain.py --tool perplexity "web research"
python automation_brain.py --tool local-qwen "code question"

# Check costs
python automation_brain.py --stats
```

---

## Anti-Patterns (Don't Do This)

**Bad:** "Help me build an automation system"
- No context, will rebuild from scratch

**Bad:** "Continue where we left off"
- No path, can't find files

**Bad:** "Make the Fiverr gigs"
- Too vague, will over-engineer

**Good:** "Continue Automation Machine at C:\automation-machine\. Check HANDOFF.md and ACTIVE-PROJECTS.md. Focus on [specific task]."

---

*Created: 2026-01-19*
