# Tasks: Personal Voice Changer

**Input**: `specs/001-voice-changer-core/spec.md` / `plan.md`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Constitution**: Test-First (NON-NEGOTIABLE) — all new tests MUST FAIL before implementation begins (Red Phase Gate)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（別ファイル・依存なし）
- **[US?]**: 対応ユーザーストーリー（US1〜US4）
- Setup / Foundational フェーズ: Story ラベルなし

---

## Phase 1: Setup（共有インフラ）

**Purpose**: プロジェクト初期化・ディレクトリ構造

- [X] T001 `voice-changer/requirements.txt` を作成する（sounddevice>=0.4, numpy>=1.24, pedalboard>=0.7, pyworld>=0.3, fastapi>=0.110, uvicorn[standard]>=0.29, PyYAML>=6.0, pytest>=8.0, pytest-asyncio>=0.23）

- [X] T002 [P] `voice-changer/` 以下のディレクトリ構造を作成する（src/effects/, src/quality_modes/, src/api/, tests/test_effects/, tests/test_quality_modes/, tests/benchmarks/, presets/）

- [X] T003 [P] `web/modules/voice_changer/` 以下のディレクトリ構造を作成する（src/Form/, templates/, js/, css/）

- [X] T004 [P] `voice-changer/start.sh` を作成する（Ubuntu開発用 — python -m venv .venv → pip install -r requirements.txt → uvicorn src.api.server:app --port 8000）

- [X] T005 [P] `voice-changer/start.bat` を作成する（Windows本番用 — .venv\Scripts\activate → uvicorn 起動 → start http://localhost:8080/voice-changer、Docker未起動時は警告して終了）

---

## Phase 2: Foundational（全US共通基盤）

**Purpose**: 全ユーザーストーリーが依存するコア処理の骨格

**CRITICAL**: この Phase が完了するまで、US1〜US4 の実装は開始できない

### Red Phase — テストを先に書く

> `pytest tests/ -v` で全件 **FAIL** を確認してから実装へ進む

- [X] T010 `tests/test_device.py` を作成する（list_devices() が非空リストを返す・detect_vb_cable() がVB-Cable未検出時 False・マイク0件時 NoMicrophoneError をモックで確認）

- [X] T011 `tests/test_pipeline.py` を作成する（sounddeviceをモック化 — パイプライン起動/パススルー/正常停止・出力モード切替・コールバック例外による安全停止を確認）

- [X] T012 [P] `tests/test_quality_modes/test_mode_b.py` を作成する（ピッチ+10半音で基本周波数が約1.78倍・ピッチ0半音で入出力ほぼ同一・処理時間50ms以内）

- [X] T013 [P] `tests/test_quality_modes/test_mode_a.py` を作成する（合成サイン波120Hz入力で出力基本周波数が200Hz以上・出力チャンク長が入力と同じ・処理時間1000ms以内）

- [X] T014 [P] `tests/test_quality_modes/test_mode_c.py` を作成する（出力チャンク長が入力と同じ・処理時間200ms以内）

- [X] T015 [P] `tests/benchmarks/test_latency.py` を作成する（モードA: 1024 samples/44100Hz を1000ms以内・モードB: 50ms以内・モードC: 200ms以内）

- [X] T016 **Red Phase Gate**: `pytest tests/ -v` で T010〜T015 が全件 **FAIL** であることを確認する（この確認が通らなければ実装タスクに進まない）

### 基盤実装

- [X] T017 `voice-changer/src/device.py` を実装する（list_devices() → dict: 入出力デバイス一覧・detect_vb_cable() → bool: "CABLE Input"の有無・マイク0件時 NoMicrophoneError 送出 → T010 をパスさせる）

- [X] T018 `voice-changer/src/quality_modes/base.py` を作成する（QualityMode 基底クラス: process(chunk: np.ndarray, sr: int) -> np.ndarray、params: dict プロパティ）

- [X] T019 [P] `voice-changer/src/quality_modes/mode_b.py` を実装する（T018依存 — pedalboard.PitchShift ラッパー、デフォルト pitch_shift_semitones=+10 → T012 をパスさせる）

- [X] T020 [P] `voice-changer/src/quality_modes/mode_a.py` を実装する（T018依存 — pyworld HARVEST で f0抽出→半音変換→D4C でSP/AP抽出→formant_scale でシフト→synthesis、デフォルト: pitch_semitones=+10, formant_scale=1.4 → T013 をパスさせる）

- [X] T021 [P] `voice-changer/src/quality_modes/mode_c.py` を実装する（T019依存 — PitchShift + 軽量フォルマント補正（スペクトル傾き調整）→ T014 をパスさせる）

- [X] T022 `voice-changer/src/quality_modes/__init__.py` を作成する（T019, T020, T021依存 — QualityModeRouter: "A"|"B"|"C" でモードを切替）

- [X] T023 `voice-changer/src/pipeline.py` を実装する（T017, T022依存 — sounddevice 非同期コールバック: マイク→QualityModeRouter→EffectChain→OutputRouter・出力モード切替（通話/テスト）・パススルーモード・コールバック内例外をキャッチして安全停止 → T011 をパスさせる）

**Checkpoint**: 基盤完了 — 各 US の実装を開始できる

---

## Phase 3: US1 — Voice Preview in Test Mode (Priority: P1) — MVP

**Goal**: マイクに話しかけると加工後の女声がヘッドフォンから聞こえる

**Independent Test**: テストモードを選択 → マイクに話す → ヘッドフォンから女声が聞こえれば成立（通話アプリ・VB-Cable 不要）

### Red Phase — テストを先に書く

- [X] T030 [P] [US1] `voice-changer/tests/test_effects/test_noise_gate.py` を作成する（閾値以下→出力ほぼゼロ・閾値以上→出力ほぼそのまま・enabled=False で入出力同一）

- [X] T031 [P] [US1] `voice-changer/tests/test_effects/test_reverb.py` を作成する（enabled=True: 出力長が入力と同じ・enabled=False: 入出力同一）

- [X] T032 [P] [US1] `voice-changer/tests/test_effects/test_robot_voice.py` を作成する（処理後の出力が入力と異なる・出力チャンク長が入力と同じ）

### 実装

- [X] T033 [US1] `voice-changer/src/effects/base.py` を作成する（AudioEffect 基底クラス: process(chunk: np.ndarray) -> np.ndarray、enabled: bool、params: dict）

- [X] T034 [P] [US1] `voice-changer/src/effects/noise_gate.py` を実装する（T033依存 — RMSベース閾値ゲート、デフォルト閾値: -40dB → T030 をパスさせる）

- [X] T035 [P] [US1] `voice-changer/src/effects/reverb.py` を実装する（T033依存 — pedalboard.Reverb ラッパー → T031 をパスさせる）

- [X] T036 [P] [US1] `voice-changer/src/effects/robot_voice.py` を実装する（T033依存 — FFT位相ランダム化によるボコーダー風加工 → T032 をパスさせる）

- [X] T037 [US1] `voice-changer/src/effects/chain.py` を実装する（T034, T035, T036依存 — EffectChain: NoiseGate→Reverb→RobotVoice の順に適用、各 enabled=False の場合スキップ）

- [X] T038 [US1] レイテンシベンチマーク実行（Ubuntu上）— `pytest voice-changer/tests/benchmarks/ -v` で T015 が全件 PASS することを確認する

**Checkpoint**: US1 完成 — テストモードで女声が聞こえる（Windows実機で確認）

---

## Phase 4: US2 — Female Voice in Discord Calls (Priority: P2)

**Goal**: 通話モードでVB-Cable経由にDiscordが女声を受信できる

**Independent Test**: 通話モード切替 → VB-CableをDiscordのマイクに設定 → 相手が女声を聞けば成立

### Red Phase — テストを先に書く

- [X] T040 [P] [US2] `voice-changer/tests/test_presets.py` を作成する（US3と共用・先行作成 — 保存→読み込みで同じ値が返る・存在しないプリセット名で PresetNotFoundError・破損YAMLで PresetCorruptError・不正YAML importで PresetInvalidError）

### 実装

- [X] T041 [US2] `voice-changer/src/api/server.py` を実装する（T022, T037依存 — CORSMiddleware: allow_origins=["http://localhost:8080"]・GET /devices・GET /state・PATCH /quality-mode・PATCH /output-mode・PATCH /effects/{name}・POST /passthrough・POST /presets/{name}・POST /presets/{name}/load・GET /presets/{name}/export・POST /presets/import・WebSocket /ws/level（音量レベル・稼働状態リアルタイム配信）・Python未起動時 503 ヘルスチェック）

- [X] T042 [US2] `web/modules/voice_changer/voice_changer.info.yml` を作成する（name: Voice Changer、type: module、core_version_requirement: ^10）

- [X] T043 [US2] `web/modules/voice_changer/voice_changer.routing.yml` を作成する（T042依存 — /voice-changer コントロールパネルルート・/admin/config/voice-changer バックエンドURL設定ルート）

- [X] T044 [P] [US2] `web/modules/voice_changer/voice_changer.links.menu.yml` を作成する（T043依存 — 管理メニューへのリンク）

- [X] T045 [US2] `web/modules/voice_changer/voice_changer.module` を作成する（T042依存 — hook_theme(): Twigテンプレートを登録・hook_page_attachments(): JS/CSSをアタッチ）

- [X] T046 [US2] `web/modules/voice_changer/src/Form/VoiceChangerSettingsForm.php` を作成する（T043依存 — PythonバックエンドのベースURL設定フォーム（デフォルト: http://localhost:8000）、Drupal State APIで保存）

- [X] T047 [US2] `web/modules/voice_changer/templates/voice-changer-control.html.twig` を作成する（T045依存 — 稼働中インジケーター（WebSocket連動）・Python未起動エラーバナー・VB-Cable未検出バナー（インストール案内・Discord設定手順）・品質モード切替（A/B/C）・出力モード切替（通話/テスト）・パススルーボタン・エフェクトON/OFF+スライダー・プリセット選択・保存・export/importボタン）

- [X] T048 [US2] `web/modules/voice_changer/js/voice-changer.js` を作成する（T041, T047依存 — 起動時 GET /devices でVB-Cable検出・マイク有無を確認しバナー制御・WebSocket /ws/level でインジケーター・レベルをリアルタイム更新・各コントロールを fetch() でPython APIに送信・バックエンドURLは drupalSettings.voiceChanger.apiBase から取得）

- [X] T049 [P] [US2] `web/modules/voice_changer/css/voice-changer.css` を作成する（T047依存 — 稼働中インジケーター（緑点滅）・エラーバナー・スライダーのスタイル）

**Checkpoint**: US2 完成 — Discordの相手が女声を聞ける（Windows実機で確認）

---

## Phase 5: US3 — Effect & Preset Management (Priority: P3)

**Goal**: プリセット保存・切替・エクスポートがリアルタイムに動作する

**Independent Test**: プリセット保存 → 別プリセットへ切替 → 元のプリセット読み込み → 設定が復元されれば成立

### 実装

- [X] T050 [US3] `voice-changer/src/presets.py` を実装する（save(name, state): presets/{name}.yaml に書き込み・load(name) -> dict: YAML読み込み（ファイルなし→PresetNotFoundError・破損YAML→PresetCorruptError）・export(name, dest_path): 指定パスにコピー・import_file(src_path): 検証してから presets/ に保存（不正→PresetInvalidError）→ T040 をパスさせる）

- [X] T051 [P] [US3] `voice-changer/presets/default.yaml` を作成する（quality_mode: A、pitch_semitones: 10、formant_scale: 1.4、effects: noise_gate: {enabled: false, threshold_db: -40}、reverb: {enabled: false, room_size: 0.3}、robot_voice: {enabled: false}）

- [X] T052 [P] [US3] `voice-changer/presets/female_voice.yaml` を作成する（ノイズゲートON版プリセット）

- [X] T053 [P] [US3] `voice-changer/presets/robot.yaml` を作成する（モードB・ロボットON・リバーブ軽め版プリセット）

**Checkpoint**: US3 完成 — プリセット切替が通話中にリアルタイムで動作する

---

## Phase 6: US4 — Easy Launch & Setup (Priority: P4)

**Goal**: ダブルクリックで起動しブラウザが自動で開く

**Independent Test**: `start.bat` ダブルクリック → `localhost:8080/voice-changer` が開けば成立

### 実装

- [X] T060 [US4] `voice-changer/README.md` を作成する（前提: Python 3.10+・Docker Desktop（Windows）・VB-Cableのダウンロード先・インストール手順・DiscordでVB-Cableをマイクに設定する手順・セットアップ手順: docker-compose up -d → drush en voice_changer → start.bat・品質モードA/B/Cの使い分け説明）

**Checkpoint**: US4 完成 — ダブルクリックでアプリが起動する

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: 複数USにまたがる品質向上

- [X] T070 [P] レイテンシベンチマーク全モード最終確認（Ubuntu）— `pytest voice-changer/tests/benchmarks/ -v` → モードA≤1000ms / B≤50ms / C≤200ms 全件PASS

- [ ] T071 Windows実機 エンドツーエンド統合確認（1. docker-compose up -d → drush en voice_changer / 2. start.bat → localhost:8080/voice-changer が自動で開く（US4） / 3. テストモードでマイクに話す → 女声がヘッドフォンから聞こえる（US1） / 4. 通話モードに切替 → Discordの相手が女声を聞ける（US2） / 5. 通話中にプリセットを切替 → 即座に声が変わる（US3） / 6. パススルーを押す → 即座に素の声に切り替わる（US3） / 7. 30分連続動作でクラッシュなし）

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup（T001〜T005）— 並列OK、即開始可能
    ↓
Phase 2: Foundational（T010〜T023）
  ├─ Red Phase（T010〜T015）— 並列OK
  ├─ T016: Red Phase Gate（全件FAIL確認 — 必須）
  └─ 実装（T017〜T023）— 一部並列OK
         ↓
  ┌──────┬──────┬──────┐
  │ US1  │ US3  │ US4  │  ← 並列実行可能
  │ US2  │      │      │  ← US1完成後に開始推奨
  └──────┴──────┴──────┘
         ↓
Phase 7: Polish（T070〜T071）
```

### User Story Dependencies

| US | 独立テスト方法 | 最小依存 |
|----|-------------|---------|
| US1（MVP） | テストモード + ヘッドフォン | Foundational（Phase 2） |
| US2 | 通話モード + VB-Cable + Discord | Foundational + US1推奨 |
| US3 | プリセット保存・切替 | Foundational（Phase 2） |
| US4 | start.bat のダブルクリック | Foundational（Phase 2） |

### Parallel Opportunities

- Phase 1 の [P] タスクは全て並列実行可能
- Phase 2 Red Phase の [P] タスクは並列実行可能
- Phase 2 実装の [P] タスク（T019, T020, T021）は T018 完了後に並列実行可能
- Phase 3〜6（各US）は Phase 2 完了後、並列実行可能
- 各 US 内の [P] タスク（エフェクト実装等）は並列実行可能

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup 完了
2. Phase 2: Foundational 完了（全US共通基盤 — CRITICAL）
3. Phase 3: US1 完了
4. STOP & VALIDATE: テストモードで女声確認（Windows実機）

### Incremental Delivery

1. Setup + Foundational → 基盤完了
2. US1 → テストモードで声確認（MVP）
3. US2 → Discord通話で女声配信
4. US3 → プリセット管理
5. US4 → 起動ファイルで簡単起動

---

**Total tasks**: 47（ゲートタスク T016 含む）
**Ubuntu単体テスト対象**: T010〜T015, T019〜T021, T030〜T037, T040, T050
**Windows実機必須**: T071
**Spec カバレッジ**: FR-001〜FR-013, SC-001〜SC-007, US1〜US4 全シナリオ
