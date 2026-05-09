from fastapi import FastAPI


app = FastAPI(title="BahnOps")


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
