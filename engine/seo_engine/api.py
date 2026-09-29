from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Agentic SEO Growth Engine")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/runs/{run_id}")
    def run_status(run_id: str) -> dict[str, str]:
        return {"run_id": run_id, "status": "not_loaded"}

    return app
