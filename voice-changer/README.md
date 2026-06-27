# Personal Voice Changer

Real-time voice changer that transforms male voice to female voice for Discord calls.

## Prerequisites

- **Python 3.10+** (Windows or Ubuntu/WSL2)
- **Docker Desktop** (Windows) — for running Drupal UI
- **VB-Cable** — virtual audio cable (free): https://vb-audio.com/Cable/

## VB-Cable Installation

1. Download VB-Cable from https://vb-audio.com/Cable/
2. Run `VBCABLE_Setup_x64.exe` as Administrator
3. Reboot if prompted

## Discord Setup

1. Open Discord → User Settings → Voice & Video
2. Under **Input Device**, select **CABLE Output (VB-Audio Virtual Cable)**
3. Your contacts will now hear your processed voice

## Setup

```bash
# 1. Start Drupal (Docker)
docker-compose up -d

# 2. Enable the Drupal module
docker-compose exec drupal drush en voice_changer -y

# 3. Start the voice changer (Windows)
start.bat
```

The browser opens automatically at http://localhost:8080/voice-changer

## Quality Modes

| Mode | Latency | Description |
|------|---------|-------------|
| **A — Natural** | ≤1000ms | WORLD vocoder: best voice quality, pitch + formant shift |
| **B — Low Latency** | ≤50ms | PitchShift only: minimal delay, good for fast-paced calls |
| **C — Balanced** | ≤200ms | PitchShift + light formant correction: balance of quality and speed |

**Recommended**: Start with Mode B to verify everything works, then switch to Mode A for best quality.

## Development (Ubuntu/WSL2)

```bash
cd voice-changer
bash start.sh
```

API runs at http://localhost:8000 — no browser auto-open in dev mode.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python backend offline" banner | Run `start.bat` or `start.sh` |
| "VB-Cable not detected" banner | Install VB-Cable (see above) and reboot |
| No sound in test mode | Check headphones are set as default playback device |
| Discord contacts hear original voice | Set Discord input to "CABLE Output" (not microphone) |
