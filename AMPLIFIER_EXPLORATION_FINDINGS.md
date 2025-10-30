# Amplifier Codebase Exploration: Actual vs Aspirational Architecture

## Executive Summary

Based on thorough exploration of both `/Users/michaeljabbour/dev/amplifier` (v0.2.0, current) and `/Users/michaeljabbour/dev/amplifier-dev` (v2/v3, in development), here's what **actually exists** versus what's **aspirational/roadmap**:

---

## 1. META-LEARNING / SELF-TEACHING LOOPS

### What ACTUALLY Exists:

#### Knowledge Synthesis System (WORKING)
- **Location**: `/amplifier/knowledge_synthesis/`
- **Status**: Operational, ~600 lines across 4 modules
- **What it does**:
  - `fingerprinter.py` (~140 lines): Creates semantic fingerprints for entity resolution across documents
  - `stream_reader.py` (~145 lines): Processes JSONL as temporal knowledge stream with sliding windows
  - `tension_detector.py` (~145 lines): Identifies contradictions and divergent ideas across articles
  - `synthesizer.py` (~145 lines): Generates 5 types of insights (convergence, divergence, evolution, emergence, bridges)
  
- **Example output**: Detects that "AI" and "automation" frequently co-occur, or finds relationship contradictions like "enables vs prevents"
- **Actual mechanism**: Statistical pattern emergence from semantic collisions, NOT symbolic reasoning

#### Pattern Mining (WORKING)
- **Location**: `/amplifier/knowledge_mining/pattern_finder.py` (~280 lines)
- **What it does**:
  - Finds recurring concepts across sources
  - Identifies concept clusters (3+ concepts frequently co-occurring)
  - Detects technique combinations
  - Maps principle applications
  - Returns patterns ranked by strength (0-1 confidence)

#### Memory/Learning System (PARTIAL)
- **Location**: `/amplifier/memory/core.py` (~260 lines)
- **What it does**:
  - Stores memories with access counts and rotation
  - Categorizes into: patterns, learnings, decisions, issues_solved
  - Tracks "most accessed" memories for query optimization
  - **Limitation**: Purely passive storage, no inference or active proposal generation
  - **Limitation**: No learning from success/failure patterns to generate improvements

### What's ASPIRATIONAL:

From ROADMAP.md and AMPLIFIER_VISION.md:
- **"Leveraging sessions for learning and improvement"** (ROADMAP line 39-41):
  - Proposed: Parse session data to extract patterns and propose improvements
  - Proposed: Enable "how would other users approach this" queries
  - Proposed: Feed learning back into metacognitive recipes
  - **Status**: Prototype exists (transcript parsing), but no automatic proposal system
  
- **"Meta-meta orchestration"** (mentioned by Sam):
  - **Proposed**: System that analyzes logs to extract patterns → generates recipes → proposes improvements
  - **Status**: NOT IMPLEMENTED - only aspirational in planning documents
  - **Current closest**: Knowledge synthesis detects patterns but doesn't propose new recipes

- **Automatic Recipe Generation**:
  - **Proposed**: System watches workflow, extracts successful sequences, packages as reusable recipes
  - **Status**: NOT IMPLEMENTED - recipe system exists but requires manual definition
  - **Current**: Recipes are human-authored; system doesn't auto-generate them

### Gap Analysis:
- ✅ Pattern detection works (knowledge synthesis)
- ✅ Memory persistence works (basic storage)
- ❌ NO feedback loop: patterns aren't analyzed to improve the system itself
- ❌ NO proposal mechanism: insights don't automatically suggest new practices
- ❌ NO recipe generation: patterns don't become executable recipes

---

## 2. EDUCATION VS TRAINING ARCHITECTURE

### What ACTUALLY Exists:

#### Expertise Encoding via Agents (WORKING)
- **Location**: `/directory/agents/` (25+ specialized agents)
- **What it does**:
  - Each agent is a `.md` file with explicit expertise instructions
  - Examples: `zen-architect.md`, `bug-hunter.md`, `security-guardian.md`
  - Agents encode practices, principles, and decision heuristics
  - **This is "education"**: Agents teach principles, not tools

#### Tool Usage / Practice Integration (WORKING)
- **Location**: `/.claude/tools/`, `/.claude/commands/`
- **What it does**:
  - Tools provide concrete capabilities (filesystem, bash, web)
  - Commands package tool sequences (e.g., `/commit` sequences multiple git operations)
  - **This is "training"**: Tools teach how to use capabilities
  - **Inversion pattern**: Agents don't USE tools directly; Claude Code orchestrates

#### Context Hierarchy (PARTIAL)
- **Location**: Implicitly in `.amplifier/config.yaml` and mode system
- **What exists**:
  - Global: `.amplifier/config.yaml` (model selection, data dirs, directory source)
  - Session: Mode selection (e.g., `amplifier-dev`, `backend-dev`)
  - Task: CLAUDE.md (project-specific context)
  - Call: Tool contexts and agent specializations
  
- **Actual implementation**:
  ```
  Global Config → Mode Selection → CLAUDE.md + AGENT.md → Agent Specializations → Tool Calls
  ```
  
- **Limitation**: No explicit per-session learning accumulation; each session starts fresh with same agents

#### Practice Persistence (PARTIAL)
- **How practices persist**:
  - Via memory system (learned lessons stored in `.data/memory.json`)
  - Via overlay system (team patterns committed to `.amplifier.local/`)
  - Via directory updates (best practices added to official directory)
  
- **Limitation**: Persistence is manual (explicit commit) not automatic

### What's ASPIRATIONAL:

From v0.2.0-what-and-why.md and ROADMAP.md:
- **"Metacognitive recipes and non-developer use"** (ROADMAP line 31-33):
  - Proposed: Recipes for non-developers combining procedures + philosophy + decision-making
  - Proposed: System helps non-developers leverage amplified capabilities
  - **Status**: Concept documented, not implemented
  - **Current**: Recipes only for developers, tool-focused, not principle-focused

- **Persistent session-based learning**:
  - **Proposed**: Each session learns and accumulates; subsequent sessions build on prior learning
  - **Status**: NO - each session gets fresh agent state
  - **Current**: Only async sharing via manual repo commits

### Gap Analysis:
- ✅ Education (agent expertise) works well
- ✅ Training (tool/command usage) works well  
- ⚠️ Context hierarchy exists but is implicit, not formalized
- ❌ NO within-session learning; learning only happens via manual practice documentation
- ❌ NO cross-session continuity; next session doesn't know what last session learned

---

## 3. OVERLAY/KERNEL SEPARATION

### What ACTUALLY Exists:

#### Overlay Resolution System (WORKING - 65 LINES!)
- **File**: `/amplifier/overlay.py` (65 lines exactly as mentioned)
- **How it works**:
  ```python
  resolver = create_overlay_resolver(
      custom_dir=Path(".amplifier.local/directory"),
      amplifier_base=Path(".amplifier/directory")
  )
  resolved = resolver(path)  # Returns custom if exists, official otherwise
  ```

- **Implementation**: Simple but elegant:
  1. Takes relative path from official directory
  2. Checks if custom override exists at same relative path
  3. Returns custom if found, official as fallback
  4. Handles ValueError gracefully if path not in directory
  
- **Usage across codebase**:
  - Mode switching (`amplifier mode set`) uses overlay resolver
  - Directory fetching preserves local customizations
  - Agent/command resolution checks overlay first
  - **Result**: Users can customize freely; updates never conflict

#### Mode Switching Implementation (WORKING)
- **File**: `/amplifier/cli.py` (lines 191-291)
- **What happens**:
  ```
  1. Validate mode exists (checks official + custom)
  2. UNSET existing mode first (clean state)
  3. Create symlinks from directory to .claude/
  4. Update Claude settings (permissions, hooks, MCP)
  5. Symlink mode-specific context files
  6. Save state
  ```

- **Key insight**: Uses filesystem symlinks (simple, debuggable) not complex state machine
- **Actual code size**: ~100 lines for complete mode switching

#### Kernel/Edges Architecture (IN DEVELOPMENT)
- **Location**: `/amplifier-dev/amplifier-core/`
- **Kernel components** (~1000 lines max):
  - `coordinator.py`: Module mounting/unmounting (~130 lines)
  - `hooks.py`: Hook registry with priority ordering (~150 lines)
  - `session.py`: Session management (~100+ lines)
  - `loader.py`: Module discovery and loading
  - `interfaces.py`: Stable public APIs (never break)
  
- **Mount points** (actual code in coordinator.py):
  ```python
  self.mount_points = {
      "orchestrator": None,        # Single orchestrator
      "providers": {},             # Multiple providers
      "tools": {},                 # Multiple tools  
      "agents": {},                # Multiple agents
      "context": None,             # Single context manager
      "hooks": HookRegistry(),      # Hook registry
  }
  ```

- **Edges** (replaceable modules):
  - `amplifier-mod-loop-basic`: Sequential agent execution
  - `amplifier-mod-provider-anthropic`: Claude API
  - `amplifier-mod-tool-filesystem`: File operations
  - `amplifier-mod-context-simple`: Message history management
  - (Each with independent versioning)

#### Individual → Team → Org Progression (WORKING)
**Layer 1: Individual Experimentation**
```
.amplifier.local/directory/agents/custom-agent.md → test locally
```

**Layer 2: Team Sharing**
```
git add .amplifier.local/ → git push → Team pulls → overlay applies automatically
```

**Layer 3: Official Contribution**
```
gh pr create → PR to official directory → merged → available to all users
```

**Actual mechanism**: Natural progression enabled by overlay system; no formal gates (!)

#### Promotion Gates (ASPIRATIONAL)
- **Proposed in ROADMAP**: Evaluation before official promotion
- **Status**: NOT IMPLEMENTED
- **Current reality**: PR-based approval (human judgment) is the only gate

### Gap Analysis:
- ✅ Overlay resolution: DONE, elegant (~65 lines)
- ✅ Mode switching: DONE, clean implementation
- ✅ Kernel/edges architecture: IMPLEMENTED in amplifier-dev (ultra-thin core)
- ✅ Individual→Team→Org flow: WORKING (natural progression)
- ❌ NO formal promotion gates/evaluation before official adoption
- ❌ NO automatic quality metrics or success prediction

---

## 4. ADVANCED MODULES (Not Directly Requested But Revealing)

### PRISM: Self-Improving Analytics (IN DEVELOPMENT)
- **Location**: `/amplifier-dev/amplifier-mod-prism/`
- **What it does** (Phases 0-1):
  - **Phase 0 (Current MVP)**: Individual developer behavior tracking
    - Monitors sessions, extracts patterns, analyzes tool usage
    - Identifies peak productivity times, context switches, convergence triggers
    - Provides local analytics: `amplifier prism analyze`
  
  - **Phase 1 (Proposed)**: Team collaboration analytics
  - **Phase 2 (Proposed)**: ML-based priority prediction
  - **Phase 3 (Proposed)**: Real-time dashboard

- **Actual mechanism** (from prism-framework.md):
  1. **Passive Observation**: Session tracking, calendar events, commits, chat patterns
  2. **Pattern Extraction**: Transformer models identify collaboration pairs, peak times
  3. **Dynamic Evaluation**: Real-time matrix updates (alignment scores, urgency weights)
  4. **Intelligent Intervention**: Targeted micro-questions during natural breaks
  5. **Recursive Improvement**: Updates own evaluation models based on outcomes

- **Current status**: Observational framework built, limited insight generation
- **Conceptually ambitious**: "PRISM knows what you do reveals more truth than what you say"

### BEAST: Behavioral Contract Validation (IN DEVELOPMENT)
- **Location**: `/amplifier-dev/amplifier-mod-beast/`
- **What it does**:
  - Behavioral contracts: Define expected system behavior
  - Observational scenarios: Run real workflows and observe actual behavior
  - Surprise tracking: Flag unexpected outcomes (reveals bugs or new patterns)
  - Hybrid validation: Combine contracts + observations for AI-resistant testing

- **Relevance to meta-learning**: Surprise detection could feed into improvement proposals
- **Current status**: Core framework operational, limited feedback integration

### IDEAS Module (IN DEVELOPMENT)
- **Location**: `/amplifier-dev/amplifier-mod-ideas/`
- **What it does**:
  - Persistent idea storage (YAML-based, cloud-resilient)
  - Multi-source (primary writable + secondary read-only)
  - AI-powered operations: goal-based reordering, theme detection
  - Tracks assignments, priorities, modification history

- **Relevance**: Could be foundation for recipe/proposal generation
- **Current status**: Tool/command framework, not AI-driven generation

---

## 5. IMPLEMENTATION PHILOSOPHY: RUTHLESS SIMPLICITY

Key architectural decisions reflected in actual code:

### Symlinks Over Complex State (WORKING)
- Mode switching uses filesystem symlinks, not database
- Overlay resolution is a simple function, not a complex registry
- **Result**: Debuggable, regeneratable, resilient to corruption

### Modular "Bricks" with Clear Contracts (WORKING)
- Each agent is ~500 words (regeneratable)
- Each command defines clear input/output
- Each tool has explicit contract (what it does, what it doesn't)
- **Result**: AI can regenerate modules, understand dependencies, compose systems

### Minimal Core, Innovative Edges (IN DEVELOPMENT)
- amplifier-core: ~1000 lines (coordinator, hooks, session, interfaces)
- Each module: Independent repository, independent versioning
- **Result**: Can update core rarely; modules evolve rapidly

### Git-Based Distribution (WORKING)
- Directory fetched from git repository
- Supports branching, tagging, sparse checkout
- **Result**: Version control on practices, easy rollback, natural collaboration

---

## 6. WHAT'S MISSING (The Gaps)

### Critical Gaps:

1. **No Auto-Proposal System**
   - System detects patterns but doesn't suggest how to act on them
   - Improvement proposals are manual (human spots pattern, writes recipe)
   - No "PRISM suggests you adopt this practice" → auto-implementation

2. **No Recursive Improvement Loop**
   - Patterns detected but don't feed back into system improvement
   - Each mode/recipe is static once created
   - No "this practice is now outdated" automation

3. **No Within-Session Learning**
   - Sessions don't accumulate knowledge across invocations
   - Each `amplifier mode set` resets agent state
   - No "session 1 taught us X, session 2 should know X"

4. **No Formal Promotion Gates**
   - Individual → Team → Official is human-gatekept only
   - No automatic quality metrics or success prediction
   - No "this pattern should only go official if X metric improves by Y%"

5. **No Cross-Tool Learning**
   - Pattern mining doesn't talk to memory system
   - Insights generated but don't update agent expertise
   - No feedback loop between discovery and practice

### Nice-to-Have Gaps:

6. **No Context Inheritance**
   - Task context doesn't automatically update global understanding
   - No "we learned Y in project A, apply to project B"

7. **No Confidence Scoring**
   - Patterns detected but confidence not formally tracked
   - Synthesizer returns strength (0-1) but synthesis doesn't accumulate confidence over time

8. **No Model Versioning**
   - Mode manifests reference items by name only (`agents: ["zen-architect.md"]`)
   - No version pinning if item changes (acknowledged as "accepted limitation" in v0.2.0 docs)

---

## 7. ROADMAP INSIGHTS: What's Actually Planned

### Core Workstream (Next)
- ✅ Done: Foundation (mode system, config, directory)
- 🔲 Current: Use Amplifier to improve Amplifier (metacognitive recipes, non-developer use)
- 🔲 Future: Kernel → module migration (splitting from Claude Code dependency)

### Usage Workstream (Parallel)
- 🔲 Leverage emergent capabilities (move beyond dev tools)
- 🔲 Improve non-developer onboarding
- 🔲 Automated content generation (use Amplifier to document itself)

### Specific Opportunities (from ROADMAP):
1. **Amplifier Agentic Loop** (instead of Claude Code dependency)
   - Status: In development (amplifier-core provides framework)
   - Impact: Would enable recipes to work offline, portable

2. **Multi-Amplifier "Modes"**
   - Status: DONE (mode system implemented)
   - Impact: Can switch between Amplifier-dev, Amplifier-app, user-custom modes

3. **Metacognitive Recipes**
   - Status: Conceptual (not yet implemented)
   - Impact: Would enable non-developers to use Amplifier

4. **Session Learning & Improvement**
   - Status: Prototype (transcript parsing exists, but not automatic analysis)
   - Impact: Would enable cross-session knowledge transfer

5. **Context Sharing** (team → cloud)
   - Status: Planned (architecture ready)
   - Impact: Would enable team collaboration across orgs

---

## 8. SYNTHESIS: Actual vs Aspirational by Category

| Feature | Actual | Aspirational | Gap |
|---------|--------|--------------|-----|
| **Pattern Detection** | ✅ Knowledge synthesis working | Per-session automatic improvements | Manual→Auto |
| **Pattern Encoding** | ✅ Via agent instructions | Auto-update agents from patterns | Static→Dynamic |
| **Recipe Generation** | ❌ Manual only | Auto-generate from workflows | None→Auto |
| **Expertise Persistence** | ✅ Via overlays & directory | Within-session accumulation | Manual→Auto |
| **Learning from Failure** | ❌ Not implemented | Track & prevent repeat failures | Passive→Active |
| **Promotion Gates** | ⚠️ PR review only | Automatic quality metrics | Human→Data-driven |
| **Overlay Resolution** | ✅ 65-line beauty | N/A | None |
| **Kernel/Edges Split** | ✅ In development | Publish & modularize | Internal→External |
| **Context Hierarchy** | ⚠️ Implicit | Formalized with learning | Loose→Tight |
| **Self-Improvement** | ❌ Not implemented | Full recursive loop | None→Implemented |

---

## 9. THE BIG PICTURE

### What Amplifier Actually Is Today:
1. **A powerful knowledge extraction system** that mines patterns from diverse sources
2. **A flexible context framework** (modes, overlays, hooks) that adapts AI to projects
3. **A modular architecture** enabling rapid innovation while maintaining stability
4. **A collaboration enabler** (individual → team → community) via overlays and git

### What Amplifier Aspirationally Is:
1. **A self-improving meta-system** that learns from usage and suggests improvements
2. **A recursive intelligence** that watches patterns, proposes practices, evaluates outcomes
3. **A knowledge marketplace** where individual discoveries become team practices become official standards
4. **A multiplier** that lets humans explore 10-100x more solution space

### The Unrealized Leap:
The missing piece isn't the foundation (it's solid) or the tools (they're comprehensive).  
The missing piece is the **automatic feedback loop**: patterns → proposals → evaluation → adoption → integration into expertise.

---

## 10. TECHNICAL EVIDENCE

### Files Confirming Analysis:

**Pattern Detection (Working)**:
- `/amplifier/knowledge_synthesis/ARCHITECTURE.md` - Describes 4-brick system
- `/amplifier/knowledge_mining/pattern_finder.py` - ~280 lines, 5 pattern types
- `/amplifier/memory/core.py` - Memory persistence with rotation

**Overlay System (Working, 65 lines)**:
- `/amplifier/overlay.py` - Exactly 65 lines, simple resolver function
- Confirmed by: `wc -l /Users/michaeljabbour/dev/amplifier/amplifier/overlay.py` → 65

**Mode Switching (Working)**:
- `/amplifier/cli.py` lines 191-291 - Complete mode switching implementation
- Confirms: unset existing, validate, create symlinks, update settings, save state

**Kernel/Edges (In Development)**:
- `/amplifier-dev/amplifier-core/coordinator.py` - Module coordination
- `/amplifier-dev/amplifier-core/hooks.py` - Hook registry (~150 lines)
- `/amplifier-dev/ARCHITECTURE.md` - Describes modular structure

**Aspirational Elements (Documented But Not Implemented)**:
- `/amplifier/ROADMAP.md` lines 39-41 - "Leveraging sessions for learning"
- `/amplifier/v0.2.0-what-and-why.md` - Describes aspirational education architecture
- `/amplifier-dev/amplifier-mod-prism/` - Self-improving analytics (MVP, limited)

---

## CONCLUSION

**The Amplifier architecture is real and sophisticated, but the self-teaching loop is aspirational.**

Current state: Strong foundation with pattern detection, context frameworks, and collaborative overlays.

Next frontier: Closing the feedback loop between pattern detection and system improvement.

The 65-line overlay resolver works beautifully. The knowledge synthesis detects real patterns. The mode system elegantly manages context. But none of these yet talk to each other to create recursive improvement.

That's the next layer to build.
