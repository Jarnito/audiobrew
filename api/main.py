from fastapi import FastAPI

app = FastAPI(title="AudioBrew API")

@app.get("/")
async def root():
    return {"message": "AudioBrew API is running"}