from fastapi import FastAPI
from src.models.schemas import PipelineRequest, PipelineResponse
from src.core.pipeline import run_pipeline

app = FastAPI(title="Data Automation", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/run", response_model=PipelineResponse)
def run(req: PipelineRequest):
    path = run_pipeline(req.source_path, req.recipient)
    return PipelineResponse(report_path=path, rows=0)
