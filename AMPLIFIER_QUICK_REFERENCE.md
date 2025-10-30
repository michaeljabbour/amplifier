# Amplifier: Quick Reference Guide

## The One-Sentence Essence

**Amplifier multiplies human capability by providing AI assistants with structured knowledge, specialized expertise, and context-aware environments—all orchestrated around the principle: "kernel stays still, edges move fast".**

---

## What Is Amplifier? (TL;DR)

Amplifier is a framework that turns generic AI coding assistants into specialized, context-aware development partners. It does this by:

1. **Providing pre-configured environments** (modes) for different types of work
2. **Organizing 20+ specialized agents** for specific tasks
3. **Enabling safe customization** without breaking updates
4. **Facilitating knowledge sharing** from individuals → teams → community
5. **Maintaining stability** in the core while allowing rapid innovation at the edges

---

## The Architecture in 3 Diagrams

### 1. Three Versions Exist

```
┌─────────────────────────────────────────┐
│ v0.1.0 (Legacy): Work Inside Amplifier │
│ "Your project goes into our repo"       │
└─────────────────────────────────────────┘
              ↓ (Evolved to)
┌─────────────────────────────────────────┐
│ v0.2.0 (Current): Bring Amplifier Out  │
│ "Our tool goes into your project"       │
│ uv add amplifier && amplifier init       │
└─────────────────────────────────────────┘
              ↓ (Evolving to)
┌─────────────────────────────────────────┐
│ v2/v3 (In Development): Modular Core    │
│ "Everything as replaceable modules"     │
│ Linux kernel model                      │
└─────────────────────────────────────────┘
```

### 2. Kernel Stays Still, Edges Move Fast

```
STABLE (Never Changes)    |  DYNAMIC (Always Innovating)
─────────────────────────────────────────────────────────
Configuration system      |  Custom modes
Mode management           |  User overlays
CLI infrastructure        |  Specialized agents
Module loading            |  Team customizations
Hook system              |  Community contributions
Directory fetching       |  Individual experiments
```

### 3. How Customization Works (No Conflicts!)

```
┌─────────────────────────────────────────┐
│  Official Directory (Read-Only)         │
│  .amplifier/directory/agents/           │
│  .amplifier/directory/contexts/         │
│  .amplifier/directory/modes/            │
└─────────────────────────────────────────┘
         ↓ Overlaid by ↓
┌─────────────────────────────────────────┐
│  Your Customizations (Your Control)     │
│  .amplifier.local/directory/agents/     │
│  .amplifier.local/directory/contexts/   │
│  .amplifier.local/directory/modes/      │
└─────────────────────────────────────────┘
         ↓ Combined into ↓
┌─────────────────────────────────────────┐
│  Your Active Environment                │
│  Everything merged, your changes win    │
└─────────────────────────────────────────┘

Result: Updates never break your changes!
```

---

## Key Components Explained

### 1. Modes: Context-Aware AI Environments

**What:** Pre-configured development contexts
**Why:** Different work needs different AI expertise
**How:**
```bash
amplifier mode set amplifier-dev      # Python/testing focus
amplifier mode set typescript-dev     # Frontend focus
amplifier mode set data-scientist     # ML/analysis focus
```

**Each mode includes:**
- 20+ specialized agents
- Custom commands
- Context files
- Development tools
- Automation hooks

### 2. Specialized Agents (20+)

**Design Agents:**
- `zen-architect` - Ruthlessly simple architecture
- `api-contract-designer` - Clean API contracts
- `database-architect` - Database optimization

**Quality Agents:**
- `bug-hunter` - Systematic debugging
- `test-coverage` - Comprehensive testing
- `security-guardian` - Security analysis

**Knowledge Agents:**
- `insight-synthesizer` - Find connections
- `knowledge-archaeologist` - Trace evolution
- `concept-extractor` - Extract patterns

**Implementation Agents:**
- `modular-builder` - Build following principles
- `post-task-cleanup` - Maintain hygiene

### 3. Unified Configuration

**Single file:** `.amplifier/config.yaml`

```yaml
mode: amplifier-dev
directory: git+microsoft/amplifier/directory
paths:
  data_dir: ~/amplifier/data          # Shared knowledge
  content_dirs:
    - .data/content
models:
  default: claude-sonnet-4-20250514
  fast: claude-3-5-haiku-20241022
```

**Benefits:**
- Keeps your project's `.env` clean
- Single source of truth
- Environment variable overrides work
- Type-safe with validation

### 4. Directory System

```
.amplifier/
├── config.yaml                  # All settings
├── state.json                   # Current mode
├── directory/
│   ├── agents/                  # 25+ agents
│   ├── commands/                # Custom /commands
│   ├── contexts/                # System context
│   ├── hooks/                   # Automation
│   ├── modes/                   # Environments
│   └── tools/                   # Python helpers
└── .amplifier.local/            # YOUR STUFF
    └── directory/
        ├── agents/
        ├── contexts/
        └── modes/
```

### 5. Knowledge System

**Transforms documentation into queryable insights:**

```
Your docs     → Summarization → Key concepts
   ↓              ↓                   ↓
Structured    → Synthesis      → Connections
knowledge        ↓              ↓
              Graph Building → Vector Index
                                 ↓
              Claude has instant access!
```

---

## The Three-Layer Collaboration Model

Shows how individual discoveries become universal capability:

### Layer 1: Individual Experimentation
```bash
# You discover a pattern
edit .amplifier.local/directory/agents/my-agent.md
# It immediately overlays the official version
# No one else affected, just you experiment
```

### Layer 2: Team Sharing
```bash
# It works! Share with team
git add .amplifier.local/
git commit -m "Add pattern X"
git push
# Team members get it automatically
# Everyone gets consistent practices
```

### Layer 3: Official Contribution
```bash
# Excellent pattern! Propose to community
gh pr create --title "Add pattern X to Amplifier"
# If merged → everyone benefits
# Individual discovery → universal capability
```

---

## Actual Implementation: Kernel vs Edges

### The Kernel (Stays Still)
- **Configuration management** - YAML-based
- **Mode switching** - Symlink-based
- **Directory loading** - Git-based fetching
- **Overlay resolution** - Simple path checking
- **CLI infrastructure** - Click-based commands

**Size:** ~6,000 lines for all of v0.2.0
**Philosophy:** Ruthless simplicity, no heavy dependencies

### The Edges (Move Fast)
- **Agents** - Specialized instructions
- **Modes** - Pre-configured combos
- **Commands** - Custom /slash commands
- **Hooks** - Automation triggers
- **Tools** - Python utilities

**Philosophy:** Easy to replace, experiment, improve

### User Space (What You Control)
- `.amplifier/config.yaml` - Your configuration
- `.amplifier.local/` - Your customizations
- Mode choice - Your context
- Project contexts - Your knowledge

---

## Why "Kernel Stays Still" Matters

### The Problem It Solves

```
Without separation:
✗ Updates might break your customizations
✗ Can't experiment freely
✗ Team changes conflict with official
✗ Community contributions cause chaos

With kernel/edges separation:
✓ Updates never conflict (overlay system)
✓ Experiment freely (local is isolated)
✓ Team shares safely (git-friendly)
✓ Community grows naturally (easy to contribute)
```

### The Benefit: Compounding Knowledge

```
Individual discovers pattern
    ↓
Team adopts & improves
    ↓
Community contributes
    ↓
Becomes standard practice
    ↓
Everyone benefits

WITHOUT conflict, WITHOUT forking, WITHOUT fragmentation!
```

---

## Installation & Basic Use

### Install
```bash
cd /path/to/your/project
uv add amplifier
amplifier init
```

### Configure
```bash
# Choose a mode
amplifier mode set amplifier-dev

# Check available modes
amplifier mode list

# Customize (freeze official to local)
amplifier directory freeze
```

### Develop
```bash
# Open Claude Code with Amplifier
claude

# Access 20+ agents, custom commands, context
# Agents available: zen-architect, modular-builder, etc.
# Commands: /commit, /ultrathink-task, etc.
```

### Experiment
```bash
# Work in parallel worktrees
amplifier worktree create feature-auth
amplifier worktree create feature-cache

# Later, remove ones you don't need
amplifier worktree remove feature-auth
```

### Maintain Knowledge
```bash
# Extract knowledge from your docs
uv run python .amplifier/directory/tools/knowledge_update.py

# Query what you've learned
uv run python .amplifier/directory/tools/knowledge_query.py "auth patterns"
```

---

## The Big Picture

```
AMPLIFIER = Context-Aware AI Amplification Platform

Core Mechanism: Kernel Stays Still, Edges Move Fast

Three Versions:
├─ v0.1.0 (Legacy): Monolithic workspace
├─ v0.2.0 (Current): Package-based integration
└─ v2/v3 (Future): Ultra-thin core + modular plugins

Five Key Components:
├─ Modes: Context-appropriate environments
├─ Agents: 20+ specialized experts
├─ Configuration: Centralized & clean
├─ Directory: Modular resources
└─ Overlay: Safe customization

Three Collaboration Layers:
├─ Individual: Local experiments
├─ Team: Shared improvements
└─ Community: Official contributions

Result: Humanity × AI = Exponential Capability
```

---

## Common Workflows

### Workflow 1: New Feature Development
```
1. amplifier mode set backend-dev
2. claude "Design auth system"
3. zen-architect analyzes & designs
4. modular-builder implements
5. security-guardian reviews
6. test-coverage ensures testing
7. git commit -m "..."
```

### Workflow 2: Debugging Production Issue
```
1. amplifier mode set amplifier-dev
2. claude "Debug the timeout"
3. bug-hunter systematically investigates
4. security-guardian checks if it's a vulnerability
5. performance-optimizer finds bottleneck
6. git commit fix
```

### Workflow 3: Team Standardization
```
1. amplifier directory freeze
2. Customize agents in .amplifier.local/
3. git add .amplifier.local/
4. Team pulls → automatic overlay
5. Everyone has same practices
```

### Workflow 4: Parallel Experiments
```
1. amplifier worktree create approach-a
2. amplifier worktree create approach-b
3. Both implement different solutions
4. Compare results
5. Keep winner: amplifier worktree remove approach-b
```

---

## Success Metrics

You know Amplifier is working when:

- ✅ AI understands your project context automatically
- ✅ Updates never break your customizations
- ✅ Team practices are consistent without meetings
- ✅ Good patterns compound across projects
- ✅ Development speed increases noticeably
- ✅ Knowledge doesn't get lost between sessions
- ✅ Parallel experiments become normal
- ✅ Team shares discoveries naturally

---

## Key Files to Know

| File | Purpose |
|------|---------|
| `.amplifier/config.yaml` | All configuration |
| `.amplifier/state.json` | Current mode |
| `.amplifier/directory/` | Official resources |
| `.amplifier.local/` | Your customizations |
| `CLAUDE.md` | Project context (auto-loaded) |
| `AGENTS.md` | Available agents (auto-loaded) |

---

## Key Commands

```bash
# Initialization
amplifier init                    # Initialize in project

# Mode management
amplifier mode set <mode>         # Switch context
amplifier mode list               # See available modes
amplifier mode unset              # Clear current mode

# Directory management
amplifier directory fetch         # Get latest resources
amplifier directory freeze        # Copy official to local

# Parallel development
amplifier worktree create <name>  # New experiment
amplifier worktree list           # See all
amplifier worktree remove <name>  # Clean up

# Knowledge management
amplifier transcript list         # See past sessions
amplifier transcript restore      # Restore full history
```

---

## The Vision

**Current:** Amplifier amplifies your development in your projects

**Near-term:** Modular ecosystem with 100+ community modules

**Medium-term:** Module marketplace, enterprise features

**Long-term:** Collective intelligence platform where every discovery improves everyone

---

## Remember

The fundamental insight:

> "Kernel stays still, edges move fast" 
> 
> Stability in coordination + Innovation everywhere else = Exponential growth

This isn't just architecture. It's a philosophy for how knowledge compounds, how communities learn, and how humanity + AI partnership creates exponential capability.

