# backend/app.py
import asyncio
import json
import sys
import os
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Windows fix for asyncio subprocess support
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ROOT = Path(__file__).parent.resolve()
app = FastAPI(title="ColdVault Backend (Terminal)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # in prod: replace "*" with your frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# map the simple button keys to script filenames
SCRIPT_MAP = {
    "create_key": "1create_key.py",
    "get_wallet": "2get_wallet.py",
    "sign_hash": "3test_sign_hash.py",
    "broadcast_tx": "4broadcast_tx.py",
}


@app.websocket("/ws/run")
async def ws_run(ws: WebSocket):
    """Accepts a single JSON message like {"cmd":"create_key"} then streams live output."""
    await ws.accept()
    process = None
    try:
        msg = await ws.receive_text()
        try:
            payload = json.loads(msg)
            cmd = payload.get("cmd")
        except Exception:
            await ws.send_text("[error] invalid JSON command")
            await ws.close()
            return

        if cmd not in SCRIPT_MAP:
            await ws.send_text(f"[error] unknown command: {cmd}")
            await ws.close()
            return

        script_path = ROOT / SCRIPT_MAP[cmd]
        if not script_path.exists():
            await ws.send_text(f"[error] script not found: {script_path}")
            await ws.close()
            return

        # Use the Python that runs uvicorn (so environment matches)
        python_exe = sys.executable
        # -u ensures unbuffered stdout/stderr (very important for live streaming)
        argv = [python_exe, "-u", str(script_path)]

        await ws.send_text(f"> Running {SCRIPT_MAP[cmd]} ...")
        print("[DEBUG] launching:", argv)

        # start subprocess
        try:
            process = await asyncio.create_subprocess_exec(
                *argv,
                cwd=str(ROOT),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except Exception as e:
            await ws.send_text(f"[error] failed to start process: {repr(e)}")
            print("[ERROR] spawn failed:", repr(e))
            await ws.close()
            return

        # stream output line-by-line
        try:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                # decode safely and forward
                try:
                    text = line.decode("utf-8", errors="replace").rstrip()
                except Exception:
                    text = str(line)
                await ws.send_text(text)
            await process.wait()
            await ws.send_text(f"\n[exit] code {process.returncode}")
        except WebSocketDisconnect:
            # client disconnected — terminate process
            print("Client disconnected — killing process")
            if process and process.returncode is None:
                process.kill()
        except Exception as e:
            await ws.send_text(f"[error] streaming failed: {repr(e)}")
            print("[ERROR] streaming:", repr(e))
        finally:
            # safe close of process
            if process and process.returncode is None:
                process.kill()
            # do not call ws.close() here unconditionally — client may close already
            try:
                await ws.close()
            except Exception:
                pass

    except WebSocketDisconnect:
        print("WebSocket disconnected before command")
        if process and process.returncode is None:
            process.kill()
    except Exception as e:
        print("Unhandled error in ws_run:", repr(e))
        try:
            await ws.send_text(f"[error] {repr(e)}")
            await ws.close()
        except:
            pass
