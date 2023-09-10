from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.responses import JSONResponse, HTMLResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from analysis import AnalysisSingleton
from comments import CommentProcessor
from googleapiclient.errors import HttpError
import asyncio
import json


TIMEOUT_THRESHOLD = 10  # Threshold
templates = Jinja2Templates(directory="website")


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
            top_comments = await asyncio.wait_for(
                asyncio.to_thread(cp.get_comment_threads, video_id), timeout=TIMEOUT_THRESHOLD
            )
            out = await asyncio.wait_for(
                asyncio.to_thread(analyser.process_comment_list, top_comments), timeout=TIMEOUT_THRESHOLD
            )
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


middleware = [Middleware(CORSMiddleware, allow_origins=["*"])]


async def site_post(request):
    payload = await request.body()
    video_id = payload.decode("utf-8").replace("videoId=", "")
    response_queue = asyncio.Queue()
    await request.app.model_queue.put((video_id, response_queue))
    output: tuple = await response_queue.get()
    analysis = output[0]
    template_output = {}
    positive_count = analysis["sentiment_analysis"]["positive"][1]
    negative_count = analysis["sentiment_analysis"]["negative"][1]
    s_neutral_count = analysis["sentiment_analysis"]["neutral"][1]

    total_comments = positive_count + negative_count + s_neutral_count
    template_output["positive"] = round((positive_count / total_comments) * 100)
    template_output["negative"] = round((negative_count / total_comments) * 100)
    template_output["neutral"] = round((s_neutral_count / total_comments) * 100)
    template_output["sarcasm"] = round(analysis["sarcasm_analysis"] * 100)

    max_count = 0
    for key in analysis["emotion_analysis"].keys():
        # count of each emotion
        if analysis["emotion_analysis"][key][1] > max_count and key != "neutral":
            template_output["strongest_emotion"] = key.title()

    if template_output["strongest_emotion"] == "Anger":
        template_output["emotion_emoji"] = 128544
    elif template_output["strongest_emotion"] == "Joy":
        template_output["emotion_emoji"] = 128514
    elif template_output["strongest_emotion"] == "Disgust":
        template_output["emotion_emoji"] = 129314
    elif template_output["strongest_emotion"] == "Sadness":
        template_output["emotion_emoji"] = 128546
    elif template_output["strongest_emotion"] == "Fear":
        template_output["emotion_emoji"] = 128552

    return templates.TemplateResponse("popup-site.html", {"request": request, "analysis": template_output})


async def site_get(request):
    return templates.TemplateResponse("index.html", {"request": request})


app = Starlette(
    routes=[
        Route("/", root, methods=["POST"]),
        Route("/{videoId}", root, methods=["GET"]),
        Route("/display-stats", site_post, methods=["POST"]),
        Route("/", site_get, methods=["GET"]),
        Mount("/static", StaticFiles(directory="static"), name="static"),
    ],
    middleware=middleware,
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
