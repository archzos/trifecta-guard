from __future__ import annotations

from typing import Any

from trifecta_guard.taint_engine import TaintEngine


def create_dashboard_app(engine: TaintEngine) -> Any:
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
    except Exception as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install dashboard dependencies: pip install -e .[dashboard]") from exc

    app = FastAPI(title="trifecta-guard dashboard", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sessions")
    def list_sessions() -> JSONResponse:
        payload = []
        for session_id, state in engine._sessions.items():
            payload.append(
                {
                    "session_id": session_id,
                    "capabilities": sorted(c.value for c in state.capabilities),
                    "trace": [
                        {
                            "tool_name": call.tool_name,
                            "capabilities": sorted(c.value for c in call.capabilities),
                        }
                        for call in state.trace
                    ],
                }
            )
        return JSONResponse(payload)

    return app
