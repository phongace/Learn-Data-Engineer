from fastapi import FastAPI, HTTPException
from recommend import recommender

app = FastAPI()

@app.get("/recommend")
def recommend(track_id: str, top_k: int = 5):
    try:
        results = recommender.recommend(track_id, top_k)
        return {"recommendations": results}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))