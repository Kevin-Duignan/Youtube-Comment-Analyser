from googleapiclient.discovery import build
import json
import time
from optimum.onnxruntime import (
    AutoQuantizationConfig,
    AutoOptimizationConfig,
    ORTModelForSequenceClassification,
    ORTQuantizer,
    ORTOptimizer
)
from transformers import AutoTokenizer
from optimum.pipelines import pipeline
from pathlib import Path


class CommentProcessor:
    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self.youtube_service = build("youtube", "v3", developerKey=api_key)

    def get_comment_threads(self, videoID: str, pages: int = 1, rich_comment: bool = False) -> list[str]:
        comments_list = []

        request = self.youtube_service.commentThreads().list(
            part="snippet,replies",
            videoId=videoID,
            maxResults=100,  # Google's API has a limit on the max results
        )
        response = request.execute()

        comments_list += self._process_comments(response, rich_comment)

        # if nextPageToken, call API again, until pages is reached
        i = 0
        while i < pages and response.get("nextPageToken", None):
            request = self.youtube_service.commentThreads().list(
                part="snippet", videoId=videoID, pageToken=response["nextPageToken"]
            )
            response = request.execute()
            comments_list += self._process_comments(response, rich_comment)
            i += 1

        print(f"Finished fetching comments for {videoID}. {len(comments_list)} comment threads found.")

        return comments_list

    def _process_comments(self, response: dict, rich_comment: bool = False) -> list[str]:
        res = []
        for item in response["items"]:
            comment_data = item["snippet"]["topLevelComment"]["snippet"]

            if not rich_comment:
                res.append(comment_data["textOriginal"])
                continue

            comment = {
                "author": comment_data["authorDisplayName"],
                "publishedAt": comment_data["publishedAt"],
                "text": comment_data["textOriginal"],
                "likes": comment_data["likeCount"],
                "replies": [],
            }
            if item.get("replies"):
                for reply in item["replies"]["comments"]:
                    reply_data = reply["snippet"]
                    reply = {
                        "author": reply_data["authorDisplayName"],
                        "publishedAt": reply_data["publishedAt"],
                        "text": reply_data["textOriginal"],
                        "likes": reply_data["likeCount"],
                    }
                    comment["replies"].append(reply)
            res.append(comment)

        return res


if __name__ == "__main__":
    # with open("config.json", "r") as jsonfile:
    #     data = json.load(jsonfile)
    # cp = CommentProcessor(data["api_key"])
    # comments = cp.get_comment_threads("lSD_L-xic9o")
    
    # model_id = "j-hartmann/emotion-english-distilroberta-base"
    # onnx_path = Path("onnx")
    # task = "text-classification"

    # model = ORTModelForSequenceClassification.from_pretrained(model_id)
    # tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # model.save_pretrained(onnx_path)
    # tokenizer.save_pretrained(onnx_path)
    
    # optimizer = ORTOptimizer.from_pretrained(model_id)
    # optimization_config = AutoOptimizationConfig.O3()
    # optimizer.optimize(save_dir=save_dir, optimization_config=optimization_config)
    # optimizer.(
    #     onnx_model_path=onnx_path / "model.onnx",
    #     onnx_optimized_model_output_path=onnx_path / "model-optimized.onnx",
    #     optimization_config=optimization_config,
    # )

    # qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=True)
    # quantizer = ORTQuantizer.from_pretrained(model)

    # quantizer.quantize(save_dir=save_dir, quantization_config=qconfig)

    # model = ORTModelForSequenceClassification.from_pretrained(save_dir)

    # onnx_clx = pipeline("text-classification", model=model, accelerator="ort")
    # start = time.time()
    # pred = onnx_clx(comments)
    # print(pred)
    # end = time.time()
    # print(str(end - start) + "seconds")
    
    # model.save_pretrained("test2")
    
    # # optimization 
    
    # model = ORTModelForSequenceClassification.from_pretrained("test2", from_pt=True)
    
    # optimization_config = AutoOptimizationConfig.O3()
    # optimizer = ORTOptimizer.from_pretrained(model)
    
    # save_dir = "test3"
    
    # optimizer.optimize(save_dir=save_dir, optimization_config=optimization_config)
    
    # model = ORTModelForSequenceClassification.from_pretrained(save_dir)
    
    # onnx_clx = pipeline("text-classification", model=model, accelerator="ort")
    
    # start = time.time()
    # pred = onnx_clx(comments)
    # print(pred)
    # end = time.time()
    # print(str(end - start) + "seconds")
    
    # tokenizer.save_pretrained("test4")
    # model.save_pretrained("test4")
