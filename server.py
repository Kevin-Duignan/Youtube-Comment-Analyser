from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.status import HTTP_504_GATEWAY_TIMEOUT
from transformers import pipeline
from analysis import AnalysisSingleton
from comments import CommentProcessor
import asyncio
import json
import time

REQUEST_TIMEOUT_ERROR = 10  # Threshold


def raise_timeout(_, frame):
    raise TimeoutError


async def root(request):
    if request.method == "POST":
        payload = await request.body()
        video_id = payload.decode("utf-8")
    elif request.method == "GET":
        video_id = request.path_params["videoId"]
    response_queue = asyncio.Queue()

    await request.app.model_queue.put((video_id, response_queue))

    output = await response_queue.get()
    return JSONResponse(output)


async def server_loop(model_queue: asyncio.Queue, analyser: AnalysisSingleton, cp: CommentProcessor):
    while True:
        (video_id, response_queue) = await model_queue.get()
        top_comments = cp.get_comment_threads(video_id)
        out = {
            "sentiment_analysis": analyser.calculate_sentiment_statistics(top_comments),
            "emotion_analysis": analyser.calculate_emotion_statistics(top_comments),
            "sarcasm_analysis": analyser.calculate_sarcasm_score(top_comments),
        }
        await response_queue.put(out)


app = Starlette(routes=[Route("/", root, methods=["POST"]), Route("/{videoId}", root, methods=["GET"])])


# Adding a middleware returning a 504 error if the request processing time is above a certain threshold
@app.middleware("http")
async def timeout_middleware(request, call_next):
    try:
        start_time = time.time()
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT_ERROR)

    except asyncio.TimeoutError:
        process_time = time.time() - start_time
        return JSONResponse(
            {"detail": "Request processing time excedeed limit", "processing_time": process_time},
            status_code=HTTP_504_GATEWAY_TIMEOUT,
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
