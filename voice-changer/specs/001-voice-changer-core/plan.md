# Implementation Plan: Personal Voice Changer

**Date**: 2026-06-26 | **Spec**: `specs/001-voice-changer-core/spec.md`

## Summary

男性ユーザーが女声で通話できるリアルタイム音声変換アプリ。Pythonの音声処理エンジン（FastAPI）とDrupalのWebUI（カスタムモジュール）を組み合わせ、VB-Cable経由でDiscordに仮想マイクとして接続する。

---

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**:
- `sounddevice` — リアルタイム音声I/O（Windows/Linux対応・非同期コールバック）
- `pyworld` — WORLDボコーダー（ピッチ+フォルマント同時変換、QualityMode A用）
- `pedalboard` — Spotify製DSPライブラリ（PitchShift・Reverb、QualityMode B/C用）
- `numpy` — 音声データ処理（全モジュールの入出力型）
- `fastapi` + `uvicorn` — REST API + WebSocket（UIなし・CORS設定でDrupalと連携）
- `PyYAML` — プリセット永続化

**UI Layer**: Drupal（カスタムモジュール `voice_changer`）
- 既存リポジトリのDockerで動作（ポート8080）
- JavaScript（Fetch API + WebSocket）でPython API（localhost:8000）に通信
- PHP側はAPIコールを代理しない（クライアントサイド通信のみ）

**Storage**: YAMLファイル（`presets/` ディレクトリ）、Drupal設定はState API

**Testing**: `pytest` + `pytest-asyncio`

**Target Platform**: 実行環境=Windows 10/11、開発環境=Ubuntu/WSL2

**Performance Goals**:
- QualityMode A: 1チャンク（1024 samples / 44100Hz）≤ 1000ms
- QualityMode B: 同 ≤ 50ms
- QualityMode C: 同 ≤ 200ms

**Constraints**:
- 音声エフェクトモジュールはnumpy配列を入出力とし、OS非依存で単体テスト可能にする
- `sounddevice`・VB-Cable依存はWindowsでのみ検証（Ubuntu上ではモック）
- CORSはlocalhost:8080のみ許可

**Scale/Scope**: 個人利用（1ユーザー）

---

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| Module-First: 各エフェクトが独立テスト可能 | ✓ | numpy配列I/Oで設計 |
| Streaming Pipeline: ≤50ms/chunk（モードB） | ✓ | pedalboardはC++実装で達成可能 |
| Test-First: テストをFAILしてから実装 | ✓ | tasks.mdのRed Phaseゲートで強制 |
| Dual Environment: Ubuntu単体テスト可能 | ✓ | sounddeviceをモック化 |
| Simplicity: 不要な抽象化なし | ✓ | YAGNI徹底 |

**Constitution補足**: Constitution v1.0.0の「UI: FastAPI + plain HTML/JS」は、Drupalの既存Docker環境を活用する方針に変更済み（合意済み）。

---

## Architecture

```
[Windows実機]
  [Microphone]
       ↓  (sounddevice callback)
  [AudioPipeline]          ← src/pipeline.py
       ↓
  [QualityModeRouter]      ← src/quality_modes/__init__.py
    ├─ Mode A: WORLDVocoder (pyworld) — 自然さ重視 ≤1000ms
    ├─ Mode B: PitchShifter (pedalboard) — 低遅延 ≤50ms
    └─ Mode C: PitchShifter + LightFormant — バランス ≤200ms
       ↓
  [EffectChain]            ← src/effects/chain.py
    ├─ NoiseGate
    ├─ Reverb（オプション）
    └─ RobotVoice（オプション）
       ↓
  [OutputRouter]
    ├─ 通話モード → VB-Cable（CABLE Input）
    └─ テストモード → スピーカー/ヘッドフォン
       ↑↓ HTTP + WebSocket（port 8000）
  [FastAPI Server]         ← src/api/server.py
       ↑↓ REST API
[Docker環境]
  [Drupal port 8080]       ← web/modules/voice_changer/
    ├─ voice-changer.js（Fetch + WebSocket → localhost:8000）
    └─ voice-changer-control.html.twig
  [MariaDB]
```

**通信フロー**:
1. ユーザーが `http://localhost:8080/voice-changer` を開く
2. ページのJavaScriptがPython API（localhost:8000）にHTTPリクエスト
3. WebSocket `/ws/level` でレベル・稼働状態をリアルタイム受信
4. Pythonがsounddeviceで音声を処理しVB-Cable/スピーカーへ出力

---

## Project Structure

### Documentation (this feature)

```
specs/001-voice-changer-core/
├── spec.md
├── plan.md              ← このファイル
├── tasks.md
└── checklists/
    └── requirements.md
```

### Source Code

```
（リポジトリルート）
├── web/
│   └── modules/
│       └── voice_changer/               # Drupalカスタムモジュール
│           ├── voice_changer.info.yml
│           ├── voice_changer.routing.yml
│           ├── voice_changer.links.menu.yml
│           ├── voice_changer.module     # hook_theme / hook_page_attachments
│           ├── src/Form/
│           │   └── VoiceChangerSettingsForm.php  # バックエンドURL設定
│           ├── templates/
│           │   └── voice-changer-control.html.twig
│           ├── js/
│           │   └── voice-changer.js     # Fetch + WebSocket
│           └── css/
│               └── voice-changer.css
└── voice-changer/
    ├── src/
    │   ├── pipeline.py                  # メインパイプライン
    │   ├── device.py                    # デバイス一覧・VB-Cable検出
    │   ├── presets.py                   # プリセットCRUD
    │   ├── effects/
    │   │   ├── base.py
    │   │   ├── noise_gate.py
    │   │   ├── reverb.py
    │   │   ├── robot_voice.py
    │   │   └── chain.py
    │   ├── quality_modes/
    │   │   ├── base.py
    │   │   ├── mode_a.py                # pyworld WORLD vocoder
    │   │   ├── mode_b.py                # pedalboard PitchShift
    │   │   ├── mode_c.py                # Hybrid
    │   │   └── __init__.py              # QualityModeRouter
    │   └── api/
    │       └── server.py                # FastAPI REST + WebSocket
    ├── tests/
    │   ├── test_device.py
    │   ├── test_pipeline.py
    │   ├── test_presets.py
    │   ├── test_effects/
    │   │   ├── test_noise_gate.py
    │   │   ├── test_reverb.py
    │   │   └── test_robot_voice.py
    │   ├── test_quality_modes/
    │   │   ├── test_mode_a.py
    │   │   ├── test_mode_b.py
    │   │   └── test_mode_c.py
    │   └── benchmarks/
    │       └── test_latency.py
    ├── presets/
    │   ├── default.yaml
    │   ├── female_voice.yaml
    │   └── robot.yaml
    ├── requirements.txt
    ├── start.bat                        # Windows用（venv + uvicorn + ブラウザ起動）
    ├── start.sh                         # Ubuntu用（開発・APIのみ）
    └── README.md
```

---

## API Endpoints (FastAPI port 8000)

| Method | Path | 役割 |
|--------|------|------|
| GET | `/devices` | デバイス一覧・VB-Cable検出状態 |
| GET | `/state` | 現在の全設定 |
| PATCH | `/quality-mode` | A/B/C切替 |
| PATCH | `/output-mode` | 通話/テスト切替 |
| PATCH | `/effects/{name}` | エフェクトパラメータ更新 |
| POST | `/passthrough` | パススルーON/OFF |
| POST | `/presets/{name}` | 現在の設定を保存 |
| POST | `/presets/{name}/load` | プリセット読み込み |
| GET | `/presets/{name}/export` | YAMLダウンロード |
| POST | `/presets/import` | YAMLアップロード |
| WS | `/ws/level` | 音量レベル・稼働状態リアルタイム配信 |

**CORS**: `allow_origins=["http://localhost:8080"]`（Drupalオリジンのみ）

---

## Key Design Decisions

**pyworldをMode Aに使う**: ピッチとフォルマントを独立して変換できる唯一の実用的な手法。pedalboardはピッチシフトのみで声質変換不可。男→女変換の自然さに直結する。

**DrupalをUIに使う**: リポジトリに既存のDocker環境があり最新Drupalが即利用可能。PHPのフォーム・ルーティング・管理機能を活用し、FastAPIはAPI専念。

**2層テスト戦略**:
- Ubuntu: numpyの合成音声でエフェクト処理の正確さ・レイテンシを計測
- Windows実機: 実際のマイク・VB-Cable・Discord連携を手動確認

**VB-Cable検出をアプリ内に持つ**: ユーザーはVB-Cableを知らない状態で始めるため、未検出時にUI上で案内する。

---

**Version**: 2.0.0 | **Created**: 2026-06-26 | **Revised**: 2026-06-26 (speckit-plan format)
