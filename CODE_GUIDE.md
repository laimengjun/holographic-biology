# Code Guide

This repository contains research documents, simulation code, and a prototype agent implementation. This guide explains what code exists and how to run it.

---

## Requirements

```bash
pip install numpy matplotlib
```

Python ≥ 3.9 recommended. No other dependencies required.

---

## Code Inventory

### 1. Monte Carlo Simulation — `monte_carlo_8.5.py`

**Purpose**: Validates the 97.3% accuracy bound predicted by the Bayesian framework using 500,000 virtual patients.

**Location**: `technical/F-zhang-yingqing-holographic-biology/simulations/monte_carlo_8.5.py`

**What it does**:
- Generates 500K virtual patients with configurable disease prevalence (prior)
- Each patient has 5 independent sensors with realistic sensitivity/specificity
- Computes Bayesian posterior for each patient
- Reports accuracy, precision, recall, F1, specificity
- Runs sensitivity analysis: sensor count, correlation, prior, sensor quality
- Generates 5 publication-ready figures (saved to `simulations/`)

**Run**:
```bash
cd technical/F-zhang-yingqing-holographic-biology/simulations/
python monte_carlo_8.5.py
```

**Output**:
- Console: full metrics tables (accuracy, precision, recall, F1)
- Files: `fig1_accuracy_vs_positive_count.png`, `fig2_correlation_effect.png`, `fig3_sensor_count_vs_accuracy.png`, `fig4_prior_sensitivity.png`, `fig5_sensor_quality_comparison.png`

**Key parameters you can modify** (in the script):
- `PRIOR` — disease prevalence (default 0.05)
- `sensors_5` — list of (sensitivity, specificity) tuples
- `N` — number of virtual patients (default 500,000)
- `decision_thresh` — classification threshold (default 0.5)

---

### 2. Bayesian Fusion Demo — `bayes_inference_demo.py`

**Purpose**: Minimal (< 60 lines) demonstration of multi-sensor Bayesian fusion. Shows how the posterior probability updates as each sensor is added.

**Location**: `bayes_inference_demo.py` (root)

**Run**:
```bash
python bayes_inference_demo.py
```

**Output**:
- Step-by-step posterior update from 0 sensors → 5 sensors
- Information gain (bits) at each step
- Final accuracy bound

---

### 3. HoloAgent Prototype — `holo_agent_prototype.py`

**Purpose**: Reference implementation of the HAIS (Holographic Agent Information System) architecture. Demonstrates that an AI agent can be built using the "holographic embryo" principle — a single agent file contains all the information needed to define its identity, capabilities, and behavior.

**Location**: `business-plan/holo_agent_prototype.py`

**What it does**:
- Defines `KnowledgeSeed` — a 5-segment template (identity/capability/boundary/voice/escalation)
- Defines `HoloAgent` base class with 3 required + 4 optional APIs (≤ 7 total, following the second metacarpal principle)
- Implements two demo agents: `TranslatorAgent` and `ProofreaderAgent`
- Runs a HAIS self-check: verifies each component of the 4-cornerstone system
- Calls a local LLM via OpenClaw CLI (or returns mock responses if unavailable)

**Run**:
```bash
cd business-plan/
python holo_agent_prototype.py
```

**Note**: Requires OpenClaw CLI (`openclaw`) in PATH for real LLM calls. Without it, the script returns mock responses and still demonstrates the architecture.

**Architecture**:
```
KnowledgeSeed (5 segments)
  ├── identity      — who am I
  ├── capability    — what can I do
  ├── boundary      — what can't I do
  ├── voice         — how do I respond
  └── escalation    — when do I escalate

HoloAgent (7 APIs max)
  ├── act(input)        → required
  ├── observe(context)  → required
  ├── reflect(feedback) → required
  ├── escalate(reason)  → optional
  ├── remember(k, v)    → optional
  ├── forget(k)         → optional
  └── handoff(target)   → optional
```

---

## File Structure (Code Only)

```
holographic-biology/
├── bayes_inference_demo.py                    # ← 2. Bayesian fusion demo
├── business-plan/
│   ├── holo_agent_prototype.py                # ← 3. HoloAgent prototype
│   └── ...
└── technical/F-zhang-yingqing-holographic-biology/
    └── simulations/
        ├── monte_carlo_8.5.py                 # ← 1. Monte Carlo simulation
        ├── fig1_accuracy_vs_positive_count.png
        ├── fig2_correlation_effect.png
        ├── fig3_sensor_count_vs_accuracy.png
        ├── fig4_prior_sensitivity.png
        └── fig5_sensor_quality_comparison.png
```

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for contribution guidelines.
---

> © laimengjun@amoy 2026 — CC BY 4.0
