<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0 (MINOR: architecture constraint updates + principle clarifications)

Modified principles:
  - II. Streaming Pipeline: "<50ms end-to-end" redefined to three-mode latency model
    (Mode A ≤1000ms / Mode B ≤50ms / Mode C ≤200ms)
  - III. Test-First: latency benchmark updated from fixed "<50ms" to per-mode thresholds

Architecture Constraints updated:
  - UI: "FastAPI + plain HTML/JS" → "Drupal custom module (port 8080)" [confirmed in plan.md]
  - DSP effects: removed "librosa as fallback", added "pyworld for Mode A (WORLD vocoder)"

Templates reviewed:
  - .specify/templates/plan-template.md ✅ (generic template, no project-specific refs)
  - .specify/templates/spec-template.md ✅ (generic template, no project-specific refs)
  - .specify/templates/tasks-template.md ✅ (generic template, no project-specific refs)

Deferred TODOs: none
-->

# Voice Changer Constitution

## Core Principles

### I. Module-First
Every processing feature (pitch shift, formant shift, noise reduction, etc.) MUST start as a
standalone, independently testable Python module. No feature is implemented directly in the
main pipeline without first being abstracted as a module with a clean interface.
Input and output MUST be numpy arrays so the module is OS-independent and unit-testable without
real audio hardware.

### II. Streaming Pipeline
All audio processing MUST operate as a streaming pipeline. No batch processing on the real-time
path. Each module receives a numpy audio chunk and returns a processed chunk of the same length.

Latency MUST satisfy the quality mode selected by the user:
- **Mode A** (Quality): ≤ 1000 ms per 1024-sample chunk at 44100 Hz (pyworld WORLD vocoder)
- **Mode B** (Low-latency): ≤ 50 ms per chunk (pedalboard PitchShift, C++ backend)
- **Mode C** (Balanced): ≤ 200 ms per chunk (PitchShift + lightweight formant correction)

### III. Test-First (NON-NEGOTIABLE)
TDD mandatory: unit tests written first, confirmed to FAIL, then implementation. Every module
MUST have:
- Unit test with synthetic audio input (no real microphone required)
- Latency benchmark that asserts the per-mode threshold above
- Effect correctness assertion (e.g., f0 shift ratio, output length equals input length)

A Red Phase Gate task MUST be completed before any implementation task in the same phase.

### IV. Dual Environment Strategy
- **Development env**: Ubuntu/WSL2 — all effect modules, API, and UI development and testing
- **Runtime env**: Windows 10/11 — mic I/O, VB-Cable, and Discord integration final testing

`sounddevice` and VB-Cable dependent code MUST be isolated behind mockable interfaces.
All effect and API logic MUST be testable on Ubuntu without real audio devices.

### V. Simplicity
- No premature abstraction (YAGNI)
- No over-engineering
- Minimum viable pipeline: mic → QualityModeRouter → EffectChain → OutputRouter
- Add features only after the baseline pipeline works

## Architecture Constraints

- **Language**: Python 3.10+
- **Audio I/O**: `sounddevice` (Windows runtime only; mock on Ubuntu)
- **DSP — Quality Mode A**: `pyworld` (WORLD vocoder: independent pitch + formant shift)
- **DSP — Quality Mode B/C**: `pedalboard` (Spotify) PitchShift
- **API**: `fastapi` + `uvicorn` (port 8000, CORS restricted to `http://localhost:8080`)
- **UI**: Drupal custom module `voice_changer` (existing Docker environment, port 8080);
  client-side JS communicates directly with the Python API via Fetch + WebSocket
- **Config/Presets**: YAML files (`presets/` directory); no database for audio state
- **Virtual device**: VB-Cable ("CABLE Input") for call mode on Windows

## Development Workflow

1. Spec → Plan → Tasks → Implement (speckit workflow)
2. Each task MUST reference a spec requirement (FR-xxx or SC-xxx)
3. No task is "done" without a passing test
4. Red Phase Gate: run `pytest tests/ -v` and confirm all new tests FAIL before implementing
5. Virtual device and Discord integration tested last (requires Windows environment)

## Governance

This constitution supersedes all other development practices for this project. Amendments
require explicit documentation of rationale and MUST increment the version following semver:
- MAJOR: principle removal or backward-incompatible redefinition
- MINOR: new principle, section, or material expansion of existing guidance
- PATCH: clarifications, wording, typo fixes

The pipeline latency constraints (per-mode thresholds in Principle II) are non-negotiable.
Any proposed change to latency targets requires a rationale and updated benchmark evidence.

**Version**: 1.1.0 | **Ratified**: 2026-06-26 | **Last Amended**: 2026-06-26
