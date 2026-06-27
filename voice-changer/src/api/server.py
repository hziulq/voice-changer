"""T041: FastAPI REST + WebSocket server for voice changer control."""
import asyncio
import io
import time
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.pipeline import AudioPipeline
from src.presets import PresetManager, PresetNotFoundError, PresetCorruptError, PresetInvalidError
from src.device import list_devices, detect_vb_cable, NoMicrophoneError


app = FastAPI(title="Voice Changer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = AudioPipeline()
preset_manager = PresetManager()


class QualityModeRequest(BaseModel):
    mode: str

class QualityModeParamsRequest(BaseModel):
    params: dict = {}


class OutputModeRequest(BaseModel):
    mode: str


class EffectUpdateRequest(BaseModel):
    enabled: bool
    params: dict = {}


class PassthroughRequest(BaseModel):
    enabled: bool


@app.get("/devices")
async def get_devices():
    try:
        devices = list_devices()
        vb_cable = detect_vb_cable()
        return {"devices": devices, "vb_cable_detected": vb_cable}
    except NoMicrophoneError as e:
        return {"devices": {"inputs": [], "outputs": []}, "vb_cable_detected": False, "error": str(e)}


@app.get("/state")
async def get_state():
    return {
        "quality_mode": pipeline.quality_mode.current_mode,
        "output_mode": pipeline.output_mode,
        "passthrough": pipeline._passthrough,
        "effects": pipeline.effect_chain.get_state(),
        "is_running": pipeline.is_running,
    }


@app.patch("/quality-mode")
async def set_quality_mode(request: QualityModeRequest):
    try:
        pipeline.quality_mode.set_mode(request.mode)
        return {"quality_mode": pipeline.quality_mode.current_mode}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/quality-mode/params")
async def set_quality_mode_params(request: QualityModeParamsRequest):
    pipeline.quality_mode.set_params(request.params)
    return {"quality_mode": pipeline.quality_mode.current_mode,
            "params": pipeline.quality_mode.get_params()}


@app.patch("/output-mode")
async def set_output_mode(request: OutputModeRequest):
    try:
        pipeline.set_output_mode(request.mode)
        return {"output_mode": pipeline.output_mode}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/effects/{name}")
async def update_effect(name: str, request: EffectUpdateRequest):
    effect_map = {
        "noise_gate": pipeline.effect_chain.noise_gate,
        "reverb": pipeline.effect_chain.reverb,
        "robot_voice": pipeline.effect_chain.robot_voice,
    }
    if name not in effect_map:
        raise HTTPException(status_code=404, detail=f"Effect '{name}' not found.")
    effect = effect_map[name]
    effect.enabled = request.enabled
    for k, v in request.params.items():
        if hasattr(effect, f"_{k}"):
            setattr(effect, f"_{k}", v)
    return {"effect": name, "params": effect.params}


@app.post("/start")
async def start_pipeline():
    try:
        pipeline.start()
        return {"is_running": pipeline.is_running}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stop")
async def stop_pipeline():
    pipeline.stop()
    return {"is_running": pipeline.is_running}


@app.post("/passthrough")
async def toggle_passthrough(request: PassthroughRequest):
    pipeline.set_passthrough(request.enabled)
    return {"passthrough": pipeline._passthrough}


@app.post("/presets/{name}")
async def save_preset(name: str):
    state = {
        "quality_mode": pipeline.quality_mode.current_mode,
        "output_mode": pipeline.output_mode,
        "effects": pipeline.effect_chain.get_state(),
    }
    preset_manager.save(name, state)
    return {"saved": name}


@app.post("/presets/{name}/load")
async def load_preset(name: str):
    try:
        state = preset_manager.load(name)
        if "quality_mode" in state:
            pipeline.quality_mode.set_mode(state["quality_mode"])
        if "output_mode" in state:
            pipeline.set_output_mode(state["output_mode"])
        return {"loaded": name, "state": state}
    except PresetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PresetCorruptError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/presets/{name}/export")
async def export_preset(name: str):
    import tempfile, os
    try:
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp:
            tmp_path = tmp.name
        preset_manager.export(name, tmp_path)
        with open(tmp_path, "rb") as f:
            content = f.read()
        os.unlink(tmp_path)
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/x-yaml",
            headers={"Content-Disposition": f'attachment; filename="{name}.yaml"'},
        )
    except PresetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/presets/import")
async def import_preset(file: UploadFile = File(...)):
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="wb") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        name = preset_manager.import_file(tmp_path)
        return {"imported": name}
    except PresetInvalidError as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        os.unlink(tmp_path)


@app.websocket("/ws/level")
async def ws_level(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            level = pipeline._level if pipeline.is_running else 0.0
            await websocket.send_json({"level": level, "is_running": pipeline.is_running})
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        pass
