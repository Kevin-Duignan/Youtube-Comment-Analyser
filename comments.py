from googleapiclient.discovery import build
import json
from analysis import AnalysisSingleton
import time
from analysis import AnalysisSingleton


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
                if len(comment_data["textOriginal"]) < 512: # Smallest Bert model can only take tokens of 512 chars
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
    with open("config.json", "r") as jsonfile:
        data = json.load(jsonfile)
    cp = CommentProcessor(data["api_key"])
    comments = cp.get_comment_threads("OYS3rUZFyM4")
    analyser = AnalysisSingleton()

    start = time.time()
    res = [
            analyser.calculate_sentiment_statistics(comments),
            analyser.calculate_emotion_statistics(comments),
            analyser.calculate_sarcasm_score(comments),
        ]
    end = time.time()
    
    print(res)
    
    print(f"Took {end-start} seconds!")

