# Amplifier: Key Files & Where to Find Them

## Understanding Amplifier Requires Reading These Files

This guide shows you exactly which files contain the core insights about Amplifier's architecture and design.

---

## Essential Reading (Start Here)

### 1. Top-Level Vision Documents

**File:** `/amplifier/README.md` (21KB)
- **What:** User-facing introduction and quick start
- **Key sections:** Features, quick start, core concepts, modes, knowledge base
- **Why read:** Understand what Amplifier provides to users
- **Time:** 15 minutes

**File:** `/amplifier/AMPLIFIER_VISION.md` (9KB)
- **What:** The philosophical foundation
- **Key sections:** Core problem, amplification building blocks, design principles, target outcomes
- **Why read:** Understand WHY Amplifier exists
- **Time:** 10 minutes
- **Key quote:** "The bottleneck isn't the AI's capability — it's that vanilla AI lacks your domain knowledge"

**File:** `/amplifier/v0.2.0-what-and-why.md` (26KB)
- **What:** Complete architecture documentation for v0.2.0
- **Key sections:** Paradigm shift (v0.1 to v0.2), major changes, architectural improvements, team collaboration
- **Why read:** Understand the design decisions and how they solve problems
- **Time:** 20 minutes
- **Star section:** "The Big Picture: Conceptual Shifts" - explains why separation of concerns matters

---

## Architecture Deep-Dives

### 2. Current Version (v0.2.0) Implementation

**File:** `/amplifier/amplifier/overlay.py` (66 lines)
- **What:** How customization works without conflicts
- **Why read:** Core pattern: overlay resolution
- **Key concept:** `create_overlay_resolver()` - incredibly simple but powerful
- **Time:** 5 minutes
- **Core insight:** Uses just path checking, no complex state

**File:** `/amplifier/amplifier/cli.py` (27KB)
- **What:** Command-line implementation
- **Key commands:** mode management, directory operations, init
- **Why read:** See how mode switching actually works
- **Key functions:** `set_mode()`, `unset_mode()`, `get_mode_manifest()`
- **Time:** 10 minutes

**File:** `/amplifier/amplifier/config/config.py` (80+ lines shown)
- **What:** Configuration system implementation
- **Why read:** Understand how settings are managed
- **Key classes:** `PathsConfig`, `ModelsConfig`, `AmplifierConfig`
- **Philosophy:** Type-safe, validating configuration
- **Time:** 5 minutes

**File:** `/amplifier/amplifier/directory_fetcher.py` (50+ lines)
- **What:** How directories are fetched from git
- **Why read:** Understand git-based resource distribution
- **Functions:** `fetch_directory()`, `fetch_git()`, `fetch_local()`
- **Time:** 5 minutes

---

### 3. Next Generation (v2/v3) Modular Architecture

**File:** `/amplifier-dev/ARCHITECTURE.md` (232 lines)
- **What:** Linux kernel model for Amplifier
- **Key sections:** Repository structure, architecture principles, usage patterns
- **Why read:** Understand how Amplifier will evolve
- **Key insight:** Ultra-thin core + replaceable modules
- **Time:** 15 minutes
- **Essential diagram:** How core, modules, and UIs relate

**File:** `/amplifier-dev/IMPLEMENTATION_REPORT.md` (392 lines)
- **What:** v2 implementation progress and feature parity status
- **Key sections:** Implemented modules, testing results, architecture alignment
- **Why read:** See what modularity looks like in practice
- **Time:** 20 minutes
- **Star section:** "Feature Comparison" table shows evolution

**File:** `/amplifier-dev/README.md` (104 lines)
- **What:** Development workspace overview
- **Why read:** Quick summary of modular structure
- **Time:** 5 minutes

---

## Design Philosophy Documents

### 4. How Amplifier Thinks About Building Software

**File:** `/amplifier/.amplifier/directory/agents/zen-architect.md` (360 lines)
- **What:** The zen-architect agent's complete instructions
- **Key sections:** Three operating modes (ANALYZE, ARCHITECT, REVIEW), design guidelines, decision framework
- **Why read:** Understand Amplifier's design philosophy in depth
- **Key concepts:** Ruthless simplicity, modular design, contracts, decision frameworks
- **Time:** 20 minutes
- **Most important:** Decision Framework section - asks 5 questions for every decision

**File:** `/amplifier/DISCOVERIES.md` (220 lines)
- **What:** Lessons learned during development
- **Key sections:** OneDrive sync issues, tool generation patterns, LLM response handling
- **Why read:** Learn from mistakes and solutions
- **Time:** 10 minutes
- **Value:** Practical patterns for defensive coding

---

## Understanding Key Components

### 5. Modes System

**File:** `/amplifier/.amplifier/directory/modes/amplifier-dev/amplifier.yaml` (104 lines)
- **What:** Example mode manifest
- **Key sections:** agents list, commands, contexts, tools, hooks, allow/deny
- **Why read:** Understand mode structure
- **Time:** 5 minutes
- **Key insight:** Manifest = contract that mode declares

**File:** `/amplifier/amplifier/cli.py` - look at functions:
- `list_modes()` - Shows both official and custom directories
- `get_mode_manifest()` - Shows overlay resolution in practice
- `set_mode()` - Complete mode switching orchestration

---

### 6. Knowledge System

**Conceptual:** `/amplifier/docs/KNOWLEDGE_WORKFLOW.md`
- How knowledge extraction works end-to-end

**Conceptual:** `/amplifier/docs/KNOWLEDGE_SYNTHESIS_PATHS.md`
- Different approaches to synthesizing knowledge

---

## The Three-Layer Model

### Understanding Individual → Team → Community Flow

**Files that show this:**

1. **v0.2.0-what-and-why.md** - "Team Collaboration & Community Ecosystem" section
   - Shows the three-layer architecture
   - Explains collaboration flow with examples
   - Pages 419-638

2. **DISCOVERIES.md** - Shows how learning compounds
   - Each discovery documents a pattern
   - Patterns become best practices

---

## Recommended Reading Order

### For Understanding Amplifier Completely (2 hours)

1. **Start here (5 min):**
   - `AMPLIFIER_QUICK_REFERENCE.md` - You're reading this!

2. **Philosophy (15 min):**
   - `AMPLIFIER_VISION.md` - Why Amplifier exists
   - `README.md` - What it does

3. **Architecture (30 min):**
   - `v0.2.0-what-and-why.md` - Current design decisions
   - `ARCHITECTURE.md` - Future modular design

4. **Implementation (20 min):**
   - `cli.py` - Read mode-related functions
   - `overlay.py` - Core customization pattern
   - `config/config.py` - Configuration system

5. **Design Philosophy (20 min):**
   - `zen-architect.md` - Design thinking
   - `DISCOVERIES.md` - Lessons learned

6. **Practical Understanding (10 min):**
   - `amplifier-dev/amplifier.yaml` - Mode structure
   - Real examples in `amplifier-dev/` modules

---

## Quick Lookup Reference

### "How does mode switching work?"
1. Read: `v0.2.0-what-and-why.md` - Mode System section (pages ~100-141)
2. See code: `amplifier/cli.py` - `set_mode()` function
3. Understand: Symlinks are created, not complex state

### "How does customization not break updates?"
1. Read: `overlay.py` - Complete file (66 lines)
2. Read: `v0.2.0-what-and-why.md` - Overlay System section (pages ~190-214)
3. Concept: Custom overrides official, never conflict

### "What's the kernel vs edges philosophy?"
1. Read: `AMPLIFIER_VISION.md` - Design Principles section
2. Read: `v0.2.0-what-and-why.md` - Architectural Improvements section
3. Compare: `ARCHITECTURE.md` - Shows same principle in v2/v3

### "How do knowledge and patterns flow through the community?"
1. Read: `v0.2.0-what-and-why.md` - Team Collaboration section (pages ~419-637)
2. See example: `DISCOVERIES.md` - Shows compounding knowledge

### "What agents are available?"
1. Browse: `/amplifier/.amplifier/directory/agents/` - 25 agent files
2. Key agents: `zen-architect.md`, `modular-builder.md`, `bug-hunter.md`
3. Start with: `zen-architect.md` - Most comprehensive

### "How will Amplifier evolve?"
1. Read: `ARCHITECTURE.md` - Full picture of v2/v3
2. Read: `IMPLEMENTATION_REPORT.md` - What's already working
3. Understand: Linux kernel model - stable core, innovative edges

---

## File Locations Summary

```
/amplifier/
├── README.md                                    # User entry point
├── AMPLIFIER_VISION.md                          # Why it exists
├── v0.2.0-what-and-why.md                       # Current architecture
├── DISCOVERIES.md                               # Lessons learned
├── amplifier/
│   ├── cli.py                                   # Command implementation
│   ├── overlay.py                               # Customization pattern
│   ├── config/config.py                         # Configuration
│   └── directory_fetcher.py                     # Git-based loading
└── .amplifier/directory/
    ├── agents/
    │   ├── zen-architect.md                     # Design philosophy
    │   ├── modular-builder.md
    │   ├── bug-hunter.md
    │   └── [20+ more agents]
    ├── contexts/
    │   ├── IMPLEMENTATION_PHILOSOPHY.md
    │   └── MODULAR_DESIGN_PHILOSOPHY.md
    └── modes/
        └── amplifier-dev/
            └── amplifier.yaml                   # Mode manifest

/amplifier-dev/
├── ARCHITECTURE.md                              # Future vision (v2/v3)
├── IMPLEMENTATION_REPORT.md                     # Current progress
└── amplifier-core/
    └── amplifier_core/                          # Ultra-thin kernel (~1000 lines)
```

---

## Three Key Files to Always Return To

### 1. For Understanding Purpose: `AMPLIFIER_VISION.md`
- The "why" behind every design decision
- The problem Amplifier solves
- The compounding effect architecture enables

### 2. For Understanding Current State: `v0.2.0-what-and-why.md`
- The "what" of current architecture
- Trade-offs and decisions
- How it enables team collaboration

### 3. For Understanding Future: `ARCHITECTURE.md`
- The "how" for long-term vision
- Linux kernel model
- Module ecosystem design

---

## Reading Progression

**Level 1 (User):** README.md → QUICK_REFERENCE.md

**Level 2 (Developer):** + AMPLIFIER_VISION.md → v0.2.0-what-and-why.md

**Level 3 (Contributor):** + cli.py → overlay.py → zen-architect.md

**Level 4 (Architect):** + ARCHITECTURE.md → IMPLEMENTATION_REPORT.md → amplifier-core code

---

## The Single Most Important Insight

**From AMPLIFIER_VISION.md:**

> "The bottleneck isn't the AI's capability — modern AI like Claude Code is incredibly powerful. The bottleneck is that vanilla AI lacks:
> - Your specific domain knowledge
> - Understanding of your patterns and preferences
> - Context from your previous work
> - Ability to work on multiple things simultaneously
> - Integration with your development workflow"

**Amplifier solves ALL of these.**

Every architectural decision traces back to solving these bottlenecks.

