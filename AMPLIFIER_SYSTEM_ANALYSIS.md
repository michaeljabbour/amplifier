# Amplifier: Complete System Analysis

## Executive Summary

Amplifier is a revolutionary AI development environment framework that embodies the philosophy "kernel stays still, edges move fast". It's designed to supercharge AI coding assistants (like Claude Code) with structured knowledge, specialized expertise, modular architecture, and powerful automation capabilities.

**Core Mission**: "I have more ideas than time to try them out" — Amplifier multiplies human capability by enabling parallel exploration, knowledge synthesis, and accelerated development workflows.

---

## 1. Core Purpose & Architecture

### What Amplifier Actually Is

Amplifier is not a monolithic tool but rather **a complete ecosystem for amplifying human-AI development partnerships**. It operates across three distinct versions:

#### v0.2.0 (Current User-Facing): "Bring Amplifier to Your Projects"
- Installable Python package that integrates into existing projects
- Installation: `uv add amplifier && amplifier init`
- Works with Claude Code CLI for autonomous coding assistance
- Provides modes, configurations, knowledge extraction, and specialized agents

#### v0.1.0 (Previous): "Work Inside Amplifier"
- Required users to work within Amplifier's repository
- Now being phased out in favor of v0.2.0's cleaner architecture

#### v2/v3 (In Development - amplifier-dev): "Modular Core with Independent Repositories"
- Ultra-thin core with everything else as pluggable modules
- Following Linux kernel model: stable core, innovative edges
- Each component (agents, providers, tools) can be independently versioned/deployed
- Complete replacement for Claude Code dependency

### Architectural Philosophy: "Kernel Stays Still, Edges Move Fast"

This fundamental principle manifests across all three versions:

```
KERNEL (Stable)              EDGES (Innovative)
├── Core coordination         ├── Agents (20+)
├── Configuration system      ├── Custom modes
├── Module loading            ├── User overlays
├── Hook system              ├── Tools & scripts
└── Stable APIs              └── Experimental features
```

**Key Insight**: The core provides stability while everything else can evolve rapidly.

---

## 2. Key Components & How They Relate

### A. The v0.2.0 Architecture

#### 2.1 Mode System - Context-Aware AI

Modes are pre-configured development environments that package:
- 20+ specialized agents
- Custom commands
- Context files
- Development tools
- Hooks and automations

**How it works:**
```yaml
# .amplifier/directory/modes/amplifier-dev/amplifier.yaml
version: 0.2.0
agents:
  - zen-architect.md        # Architecture & design
  - modular-builder.md      # Implementation
  - bug-hunter.md           # Debugging
  - security-guardian.md    # Security
  - test-coverage.md        # Testing
  - [18 more specialized agents]
```

**Mode switching instantly reconfigures the AI environment:**
```bash
amplifier mode set amplifier-dev      # Python dev mode
amplifier mode set typescript-dev     # Frontend mode
amplifier mode set data-scientist     # ML mode
```

#### 2.2 Unified Configuration System

All Amplifier settings centralized in `.amplifier/config.yaml`:

```yaml
mode: amplifier-dev
directory: git+microsoft/amplifier/directory
paths:
  data_dir: ~/OneDrive/amplifier/data      # Shared knowledge base
  content_dirs:
    - .data/content
    - ~/Documents/project-specs
models:
  default: claude-sonnet-4-20250514
  fast: claude-3-5-haiku-20241022
```

**Why centralized?**
- Separation of concerns (project .env stays clean)
- Single source of truth
- Type-safe with validation
- Environment variable overrides (`AMPLIFIER__PATHS__DATA_DIR=...`)

#### 2.3 Directory System - Modular Resources

`.amplifier/directory/` contains all Amplifier resources organized by type:

```
.amplifier/directory/
├── agents/           # 25+ specialized AI agents
├── commands/         # Custom Claude commands
├── contexts/         # System context files
├── hooks/            # Automation triggers
├── modes/            # Pre-configured environments
└── tools/            # Python utilities & helpers
```

**Layers of Resolution:**
1. **Official Directory** (`git+microsoft/amplifier/directory`)
2. **Custom Overlay** (`.amplifier.local/directory/`) - your customizations
3. **Active Mode** - selected via `amplifier mode set`

#### 2.4 Overlay System - Non-Destructive Customization

The overlay system enables safe customization without modifying official resources:

```python
# amplifier/overlay.py - Simple but powerful
def create_overlay_resolver(custom_dir, amplifier_base):
    def resolver(source_path):
        relative = source_path.relative_to(amplifier_base)
        custom_path = custom_dir / relative
        if custom_path.exists():
            return custom_path  # Local override
        return source_path      # Official fallback
    return resolver
```

**Workflow:**
```bash
amplifier directory freeze          # Copy official to local
# Edit .amplifier.local/directory/agents/security-guardian.md
# Your version automatically overlays the official one!
```

**Benefits:**
- ✅ Non-destructive customization
- ✅ Gitignore-friendly
- ✅ Easy team sharing
- ✅ Simple merging of official updates

#### 2.5 CLI System - Command-Based Workflows

Modern CLI replacing Makefile approach:

```bash
amplifier init                      # Initialize in project
amplifier mode set <mode>           # Switch contexts
amplifier mode list                 # List available modes
amplifier directory fetch           # Update resources
amplifier directory freeze          # Freeze for customization
amplifier worktree create           # Parallel experiments
amplifier transcript list           # View past sessions
amplifier transcript restore        # Restore full history
```

---

### B. The v2/v3 Modular Architecture (amplifier-dev)

The development workspace reveals the **Linux kernel model** architecture:

```
Amplifier Architecture (v2/v3)

┌─────────────────────────────────────────────────────┐
│         User Interface Layer (Multiple Options)     │
│  ├─ CLI (amplifier-app-cli)                        │
│  ├─ Web UI (future)                                │
│  └─ Programmatic API                               │
└─────────────────────────────────────────────────────┘
           ↓↓↓ (Uses core APIs)
┌─────────────────────────────────────────────────────┐
│      KERNEL (Ultra-thin, Stable Core)              │
│  ├─ amplifier-core (~1000 lines max)               │
│  │  ├─ Module discovery & loading                  │
│  │  ├─ Hook system & lifecycle events              │
│  │  ├─ Session & context management                │
│  │  └─ Stable public APIs (never break)            │
└─────────────────────────────────────────────────────┘
           ↓↓↓ (Mount plugins via interfaces)
┌─────────────────────────────────────────────────────┐
│         MODULE LAYER (Independent, Replaceable)    │
│  ┌───────────────────────────────────────────────┐  │
│  │ ORCHESTRATORS  │ PROVIDERS    │ TOOLS        │  │
│  ├─ loop-basic   ├─ anthropic   ├─ filesystem  │  │
│  ├─ loop-stream  ├─ openai      ├─ bash        │  │
│  ├─ loop-parallel├─ local       ├─ web         │  │
│  └─ ...          └─ ...         ├─ git         │  │
│                                  └─ ...         │  │
│  ┌───────────────────────────────────────────────┐  │
│  │ CONTEXT MGR     │ AGENTS        │ HOOKS      │  │
│  ├─ simple        ├─ architect    ├─ formatter │  │
│  ├─ persistent    ├─ debugger     ├─ backup    │  │
│  ├─ compact       ├─ reviewer     ├─ security  │  │
│  └─ rag           └─ ...          └─ ...       │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### 2.6 Repository Structure

**Core Repos (microsoft/)**
- `amplifier` - User-facing entry point (installs via pip)
- `amplifier-core` - Ultra-thin kernel
- `amplifier-app-cli` - CLI implementation
- `amplifier-dev` - Development workspace (all repos as submodules)

**Module Repos (microsoft/amplifier-module-*)**
Each has independent:
- Versioning
- Release cycle
- Maintainers
- Documentation

**Reference Implementations:**
- **Orchestrators**: Control agent loop execution
- **Providers**: LLM connections (Anthropic, OpenAI, local)
- **Tools**: Capabilities (filesystem, bash, web, git)
- **Agents**: Specialized workers
- **Context Managers**: Message history management
- **Hooks**: Lifecycle extensions

---

## 3. Design Principles & Philosophy

### Ruthless Simplicity

Every component embodies Wabi-sabi minimalism:

```
DESIGN DECISIONS:

Every feature must answer:
1. Necessity:   "Do we actually need this right now?"
2. Simplicity:  "What's the simplest way to solve this?"
3. Directness:  "Can we solve this more directly?"
4. Value:       "Does complexity add proportional value?"
5. Maintenance: "How easy to understand and change?"
```

### Modular Design ("Bricks & Studs")

Modules are self-contained units (bricks) connected via standardized interfaces (studs):

```
Each Module Must:
✓ Define clear contract (inputs, outputs, side effects)
✓ Specify module boundaries and responsibilities
✓ Be self-contained in own directory
✓ Define public interfaces via __all__
✓ Plan for regeneration over patching
```

**Example - zen-architect agent:**
```
Purpose:     Ruthlessly simple architecture design
Contract:    Takes requirements → Returns specifications
Location:    .amplifier/directory/agents/zen-architect.md
Regenerable: Yes (can rebuild from scratch)
```

### Human-AI Partnership

Clear role separation:
- **Humans**: Vision, judgment, creative decisions
- **AI**: Exploration, implementation, pattern finding
- **Amplifier**: Enables this partnership at scale

---

## 4. "Kernel Stays Still, Edges Move Fast" - Detailed Explanation

This concept addresses the fundamental problem: **How do we maintain stability while enabling rapid innovation?**

### The Kernel (Stays Still)

**What is stable?**
- Core coordination logic (module loading, hooking, session management)
- Public APIs (never break, only extend)
- File formats and contracts
- Configuration structure

**Why stable?**
- Single maintainer can understand it all (~1000 lines)
- All modules depend on it
- Breaking changes = breaking all modules
- Changes require RFC process

**How small?**
- No business logic (pure coordination)
- Uses Python stdlib only (no heavy dependencies)
- Direct implementations (no complex abstractions)
- Focused solely on module hosting

### The Edges (Move Fast)

**What is unstable?**
- Individual agents and their instructions
- Tool implementations
- Provider implementations
- Context management strategies
- Hooks and automation

**Why fast?**
- Each module is independently versioned
- Community can contribute freely
- Easy to experiment and iterate
- Can compete with ideas (multiple implementations)

**How this works:**
```
Week 1:  User discovers new security pattern → Creates local agent
Week 2:  Team adopts and improves → Commits to shared directory
Week 4:  Submit PR to official directory → May be merged
Month 2: Official directory includes it → Everyone benefits

Meanwhile, core hasn't changed at all!
```

### The Critical Insight

```
STABLE CORE + INNOVATIVE EDGES = EXPONENTIAL CAPABILITY GROWTH

Without this architecture:
• Monolithic system - changes cascade everywhere
• Fear of breaking things - slow innovation
• Forking hell - customizations diverge
• Maintenance nightmare - nothing fits everyone

With Amplifier:
• Core rarely needs updates (boring is good!)
• Edges evolve rapidly (experiment freely!)
• Customizations layer on top (no conflicts)
• Community knowledge compounds (learning shared)
```

---

## 5. Implementation Details: What Makes It Work

### 5.1 Mode System Deep Dive

Modes provide **context-aware AI environments**. When you switch modes:

```bash
amplifier mode set amplifier-dev
```

This triggers a sophisticated resolution process:

```python
def set_mode(mode: str):
    # 1. Validate mode exists (checks official + custom directories)
    manifest = get_mode_manifest(mode)
    
    # 2. Unset existing mode first (clean state)
    unset_current_mode()
    
    # 3. Create symlinks from directory to .claude/
    for collection in ["agents", "commands", "contexts", "tools"]:
        for item in manifest[collection]:
            src = DIRECTORY / collection / item
            dst = CLAUDE_DIR / collection / item
            symlink(src, dst)
    
    # 4. Update Claude settings (permissions, hooks, MCP)
    update_claude_settings(manifest)
    
    # 5. Symlink mode-specific context files
    symlink_context_files(manifest)
    
    # 6. Save state
    state["mode"] = mode
    state_to_file(state)
```

**Key insight:** Uses simple filesystem operations (symlinks) not complex state management.

### 5.2 Git-Based Directory Distribution

Directories are fetched from git repositories using sparse checkout:

```bash
# Official directory reference
directory: git+microsoft/amplifier/directory

# Can pin to version
directory: git+microsoft/amplifier/directory@v0.2.0

# Can use custom directory
directory: /home/user/my-amplifier-directory
```

This enables:
- ✅ Centralized updates (`amplifier directory fetch`)
- ✅ Version pinning for stability
- ✅ Community sharing (use anyone's directory)
- ✅ Offline support (cached locally)

### 5.3 Overlay Resolution

The overlay system uses a simple but powerful resolver:

```python
# Creates resolver function that:
# 1. Takes a path in .amplifier/directory
# 2. Checks if override exists in .amplifier.local/directory
# 3. Returns custom if exists, official otherwise

resolve = create_overlay_resolver(
    custom_dir=Path(".amplifier.local/directory"),
    amplifier_base=Path(".amplifier/directory")
)

# Usage
actual_path = resolve(Path(".amplifier/directory/agents/security-guardian.md"))
# Returns .amplifier.local/directory/agents/security-guardian.md if it exists
# Otherwise returns original path
```

**Why this design?**
- Git-friendly (local overrides in .gitignore)
- No merge conflicts (local always wins)
- Easy to update official (just fetches)
- Progressive customization (customize as needed)

### 5.4 Knowledge System

Transforms unstructured documentation into queryable knowledge:

```
Knowledge Processing Pipeline:

Documentation Files
    ↓ (Summarization)
Key Concepts
    ↓ (Extraction)
Structured Knowledge
    ↓ (Synthesis)
Connections & Patterns
    ↓ (Graph Building)
Queryable Knowledge Graph
    ↓ (Embedding Search)
Instant Access to Relevant Context
```

Files process through three stages:
1. **Classification** - Document type detection
2. **Synthesis** - Concept extraction and connection
3. **Storage** - Graph and vector indexing

Claude then queries this continuously during development.

### 5.5 Specialized Agents (20+)

Each agent is an expert with:
- Clear responsibility
- Specialized instructions
- Preferred model (some use faster models, some use thinking models)
- Operating modes and context

**Architecture agents:**
- `zen-architect` - System design with ruthless simplicity
- `modular-builder` - Implementation following modular principles
- `api-contract-designer` - API design and contracts

**Quality agents:**
- `bug-hunter` - Systematic debugging
- `test-coverage` - Comprehensive testing
- `security-guardian` - Security analysis

**Knowledge agents:**
- `insight-synthesizer` - Finding hidden connections
- `knowledge-archaeologist` - Tracing idea evolution
- `concept-extractor` - Extracting knowledge from documents

**Each agent provides:** Clear prompt, context, examples, and collaboration patterns.

---

## 6. Relationship to "Kernel Stays Still, Edges Move Fast"

### How This Manifests Across All Three Versions

#### v0.2.0 User Version
- **Kernel**: Configuration system, CLI, directory loading, mode management
- **Edges**: Agents, custom modes, user overlays, project-specific contexts

#### v2/v3 Modular Version  
- **Kernel**: amplifier-core (module loading, hooking, session management)
- **Edges**: Each module type (tools, agents, providers) independently versioned

#### The Unifying Principle
```
Across all versions, the pattern is consistent:

STABLE & BORING        |  DYNAMIC & INNOVATIVE
─────────────────────────────────────────────
Config system         |  Mode configurations
CLI infrastructure    |  Custom commands
Module loading        |  Individual modules
Deployment framework  |  Tool implementations
```

### Why This Matters for Development

**Without this separation:**
- Users hesitate to customize (might break updates)
- Teams fork the project (diverge immediately)
- Updates are risky (might break customizations)
- Community contributions scattered

**With this architecture:**
- Users customize freely (local overlay)
- Teams share improvements (easy contribution)
- Updates are safe (never conflict)
- Community knowledge compounds

---

## 7. The Three-Layer Collaboration Model

Amplifier enables a natural knowledge-sharing flow:

### Layer 1: Individual Experimentation
```bash
# User discovers a better pattern
edit .amplifier.local/directory/agents/custom-agent.md

# Use immediately - overlays official version
amplifier mode set custom-mode
```

### Layer 2: Team Sharing
```bash
# Works great! Share with team
git add .amplifier.local/
git commit -m "Add OWASP checks to security agent"
git push

# Team gets it automatically via overlay
# Everyone gets consistent security practices
```

### Layer 3: Official Contribution
```bash
# Excellent pattern! Submit to community
gh pr create --title "Add OWASP security agent" \
  --body "Proposal to add this to official directory"

# If merged → becomes standard practice
# Available to all users
```

---

## 8. Key Architectural Decisions

### Decision 1: Layers, Not Monolith

**Why?** Monolithic systems have components stepping on each other.

```
Monolithic          →  Layered
Everything mixed      Official | Local | Active
Can't update safely   Updates never conflict
Hard to customize     Easy customization
```

### Decision 2: Symlinks, Not Complex State

**Why?** Simple operations are maintainable.

```
Symlinks            →  Complex Registry
Direct filesystem     Complicated state tracking
Easy to debug         Hard to understand
Regeneratable        Black box state
```

### Decision 3: YAML Manifests, Not Code-Based Config

**Why?** Manifest > Configuration > Code for contracts.

```yaml
# manifest = contract
agents:
  - zen-architect.md
  - modular-builder.md
commands:
  - commit.md
```

### Decision 4: Ultra-Thin Core

**Why?** Single maintainer can understand it all.

```
Core: ~1000 lines
├─ Module loading (~200 lines)
├─ Hook system (~200 lines)
├─ Session management (~300 lines)
├─ Stable APIs (~300 lines)
└─ Total: Understandable by one person
```

---

## 9. Actual Implementation - Kernel vs Modules vs User Spaces

### The Kernel (amplifier-core)

**Purpose:** Ultra-thin coordination layer

**Components:**
```python
amplifier_core/
├── coordinator.py         # Module discovery & loading
├── hook_system.py        # Event & lifecycle management
├── session.py            # Session & context coordination
├── config.py             # Configuration management
└── interfaces.py         # Stable public APIs
```

**Size:** ~1000 lines total

**Stability:** Never breaks, only extends

**Key Files:**
- Public APIs documented
- Module interface contracts
- Hook lifecycle events

### Module Layer Examples

**Tool Module (amplifier-module-tool-filesystem)**
```
Purpose: File operations
Interface: Mount as 'tools' collection
Provides: read_file, write_file, edit_file
Location: Own repository
Versioning: Independent semver
```

**Agent Module (amplifier-module-agent-architect)**
```
Purpose: System design expertise
Interface: Mount as 'agents' collection
Provides: analyze, design, review capabilities
Location: Own repository
Versioning: Independent semver
```

**Provider Module (amplifier-module-provider-anthropic)**
```
Purpose: Claude API integration
Interface: Mount as 'provider'
Provides: LLM connectivity
Location: Own repository
Versioning: Independent semver
```

### User Space

**What users control:**
- `.amplifier/config.yaml` - Configuration
- `.amplifier.local/` - Custom overrides
- Chosen mode - Development context
- Project-specific contexts

**What users cannot break:**
- Core stability (overlay-safe)
- Official resources (read-only by default)
- Other modules (independent)

---

## 10. Complete System Integration Example

**Scenario:** Developer starts new feature work

```
1. Developer initializes Amplifier
   $ cd my-project
   $ uv add amplifier && amplifier init

2. Chooses appropriate mode
   $ amplifier mode set backend-dev
   
   This activates:
   ├─ 20+ backend-focused agents
   ├─ Database architect
   ├─ API contract designer
   ├─ Security guardian
   └─ Test coverage

3. Opens Claude Code
   $ claude
   
   Automatically loads:
   ├─ CLAUDE.md (project context)
   ├─ AGENTS.md (available specialists)
   ├─ Implementation philosophy
   ├─ Known patterns & decisions
   └─ Custom team guidelines

4. Describes new feature
   "Create an authentication module with JWT tokens and refresh flow"
   
   Amplifier:
   ├─ zen-architect analyzes requirements
   ├─ Creates detailed specification
   ├─ modular-builder implements spec
   ├─ security-guardian reviews for vulnerabilities
   ├─ test-coverage ensures comprehensive tests
   └─ post-task-cleanup maintains hygiene

5. Developer reviews changes
   - All AI actions transparent
   - Can see agent reasoning
   - Can override if needed

6. Commits with style
   $ amplifier mode set amplifier-dev
   $ claude  # Access commit command
   
   /commit "Add JWT authentication module
   
   Implemented following zen-architect design with:
   - Clean separation of concerns
   - Comprehensive test coverage
   - Full security review
   - API contract compliance"

7. Developer can customize
   $ amplifier directory freeze
   
   Now edit .amplifier.local/directory/ for project-specific tweaks:
   ├─ Custom security agent with company standards
   ├─ Team-specific code review guidelines
   └─ Custom hooks for pre-commit checks

8. Share with team
   $ git add .amplifier.local/
   $ git commit "Add team customizations"
   $ git push
   
   Team members automatically get:
   ├─ Same agent configurations
   ├─ Same security standards
   ├─ Same code review checks
   └─ Consistent development experience

9. Contribute to community
   $ gh pr create --title "Add authentication patterns to Amplifier"
   
   If accepted:
   └─ Becomes part of official directory
   └─ Available to all users
   └─ Community benefits from discovery
```

---

## 11. Vision & Future Directions

### Phase 1: Foundation (Current - v0.2.0)
- ✅ Mode system
- ✅ Unified configuration
- ✅ Directory overlay
- ✅ Specialized agents
- ✅ Knowledge extraction

### Phase 2: Modular Architecture (In Development - v2/v3)
- Independent module repositories
- Ultra-thin core
- Plugin-based providers
- Community module ecosystem

### Phase 3: Ecosystem
- Module marketplace
- More provider implementations
- Community contributions
- Enterprise features

### Phase 4: Scale
- Distributed development
- Collective intelligence
- Knowledge marketplace
- Autonomous capabilities

---

## 12. Key Insights

### The Amplifier Difference

```
Traditional AI Tools        |  Amplifier
─────────────────────────────────────────
One-size-fits-all AI       |  Context-aware environments
Start from zero each time  |  Built-in knowledge & patterns
Isolated from codebase     |  Integrated into projects
No customization           |  Easy overlays
Updating breaks things     |  Updates never conflict
No team sharing            |  Natural knowledge flow
```

### Why "Kernel Stays Still" Works

```
The Problem: Innovation vs. Stability

Extreme A: Change everything constantly
├─ Exciting! ✓
├─ But: Nothing's stable ✗
├─ And: Users can't upgrade ✗
└─ Result: Fragmentation

Extreme B: Never change anything
├─ Stable! ✓
├─ But: Innovation stalled ✗
├─ And: Users stuck ✗
└─ Result: Irrelevance

Amplifier's Answer: Kernel stays still, edges move fast
├─ Core stable for reliability ✓
├─ Edges evolve for innovation ✓
├─ Updates never conflict ✓
├─ Customization always works ✓
└─ Community knowledge compounds ✓
```

---

## 13. Technology Stack Breakdown

### v0.2.0 (Current)
- **Language**: Python 3.11+
- **Package Manager**: uv
- **Config**: YAML
- **CLI**: Click
- **Validation**: Pydantic
- **Storage**: Local filesystem
- **AI Integration**: Claude Code SDK

### v2/v3 (Modular)
- **Core**: Python stdlib only
- **Module Discovery**: Dynamic import system
- **APIs**: Protocol-based interfaces
- **No Heavy Dependencies**: Keeps core thin

---

## 14. Summary: How It All Fits Together

```
┌─────────────────────────────────────────────────────────┐
│              AMPLIFIER COMPLETE SYSTEM                 │
└─────────────────────────────────────────────────────────┘

PHILOSOPHY: Kernel Stays Still, Edges Move Fast
         ↓
┌──────────────────────┬──────────────────────┐
│    STABLE CORE       │  INNOVATIVE EDGES    │
├──────────────────────┼──────────────────────┤
│ Config system        │  20+ agents          │
│ Mode management      │  Custom modes        │
│ Directory loading    │  User overlays       │
│ CLI infrastructure   │  Team customizations │
│ Module system        │  Community contribs  │
└──────────────────────┴──────────────────────┘
         ↓              ↓           ↓
    Individual   →  Team Sharing → Official
    Experiment      (git)            (PR)
         ↓           ↓           ↓
    Local Only → Shared Mode → Community
    
RESULT:
• Every innovation improves everyone
• Updates never break customizations
• Communities form around patterns
• System learns from usage
• Humanity amplified by AI
```

---

## Conclusion

Amplifier represents a fundamentally new approach to AI-assisted development: **not replacing humans, but multiplying their capability**. By separating stable coordination (kernel) from evolving innovation (edges), it creates an ecosystem where:

- Individual discoveries become team practices
- Team patterns become community standards
- Community knowledge becomes universal capability
- Humanity's imagination becomes the only limit

The "kernel stays still, edges move fast" principle isn't just an architecture—it's a philosophy for how knowledge compounds, how communities learn, and how exponential growth happens not through centralization but through distributed innovation with stable foundations.

This is what makes Amplifier not just a tool, but a platform for collective intelligence amplification.

