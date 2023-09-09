from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from transformers import pipeline
from analysis import AnalysisSingleton
from comments import CommentProcessor
from googleapiclient.errors import HttpError
import asyncio
import json
import time

TIMEOUT_THRESHOLD = 10  # Threshold

async def root(request):
    if request.method == "POST":
        payload = await request.body()
        video_id = payload.decode("utf-8")
    elif request.method == "GET":
        video_id = request.path_params["videoId"]
    response_queue = asyncio.Queue()

    await request.app.model_queue.put((video_id, response_queue))

    output: tuple = await response_queue.get()
    return JSONResponse(output[0], status_code=output[1])


async def server_loop(model_queue: asyncio.Queue, analyser: AnalysisSingleton, cp: CommentProcessor):
    while True:
        (video_id, response_queue) = await model_queue.get()
        try:
            top_comments = await asyncio.wait_for(asyncio.to_thread(cp.get_comment_threads, video_id), timeout=TIMEOUT_THRESHOLD)
            out = await asyncio.wait_for(asyncio.to_thread(analyser.process_comment_list, top_comments), timeout=TIMEOUT_THRESHOLD)
            await response_queue.put(out)
        except asyncio.TimeoutError:
            failed_request = {"error": "Request or processing timed out"}
            await response_queue.put((failed_request, 504))
        except HttpError:
            failed_request = {"error": "Failed to crawl YouTube comments"}
            await response_queue.put((failed_request, 404))
        except Exception as e:
            print(f"Error occurred processing {video_id}: {e}")
            failed_request = {"error": "Unhandled exception encountered!"}
            await response_queue.put((failed_request, 500))

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"])
]

app = Starlette(routes=[Route("/", root, methods=["POST"]), Route("/{videoId}", root, methods=["GET"])], middleware=middleware)

@app.on_event("startup")
async def startup_event():
    analyser = AnalysisSingleton()
    with open("config.json", "r") as jsonfile:
        data = json.load(jsonfile)

    cp = CommentProcessor(data["api_key"])

    model_queue = asyncio.Queue()
    app.model_queue = model_queue
    asyncio.create_task(server_loop(model_queue, analyser, cp))
