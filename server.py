from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from transformers import pipeline
from analysis import AnalysisSingleton
from comments import CommentProcessor
import asyncio
import json


async def root(request):
    payload = await request.body()
    video_id = payload.decode("utf-8")
    response_queue = asyncio.Queue()

    await request.app.model_queue.put((video_id, response_queue))

    output = await response_queue.get()
    return JSONResponse(output)


async def server_loop(model_queue: asyncio.Queue, analyser: AnalysisSingleton, cp: CommentProcessor):
    while True:
        (video_id, response_queue) = await model_queue.get()
        top_comments = cp.get_comment_threads(video_id)
        out = [
            analyser.calculate_sentiment_statistics(top_comments),
            analyser.calculate_emotion_statistics(top_comments),
            analyser.calculate_sarcasm_score(top_comments),
        ]
        await response_queue.put(out)


app = Starlette(
    routes=[
        Route("/", root, methods=["POST"]),
    ],
)


@app.on_event("startup")
async def startup_event():
    analyser = AnalysisSingleton()
    with open("config.json", "r") as jsonfile:
        data = json.load(jsonfile)

    cp = CommentProcessor(data["api_key"])

    model_queue = asyncio.Queue()
    app.model_queue = model_queue
    asyncio.create_task(server_loop(model_queue, analyser, cp))
