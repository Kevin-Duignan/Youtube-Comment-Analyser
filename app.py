from flask import Flask, jsonify
from googleapiclient.discovery import build
import googleapiclient
from analysis import AnalysisSingleton
import json

app = Flask(__name__)
api_key = "AIzaSyBtxJEet5gIXlbXD2gtCKwcss98JnT-Am0"
youtube = build("youtube", "v3", developerKey=api_key)


@app.route("/<video_id>")
def get_comments(video_id: str):
    request = youtube.commentThreads().list(part="snippet, replies", videoId=video_id, maxResults=100)
    response = request.execute()

    all_comments = []
    all_top_comments = []

    comments, top_comments = process_comments(response)
    all_comments += comments
    all_top_comments += top_comments

    # if nextPageToken, call API again, until max size is reached
    i = 0
    while i < 5 and response.get("nextPageToken", None):
        request = youtube.commentThreads().list(part="snippet", videoId=video_id, pageToken=response["nextPageToken"])
        response = request.execute()
        comments, top_comments = process_comments(response)
        all_comments += comments
        all_top_comments += top_comments
        i += 1

    # Writes comments to JSON file
    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(all_comments, f, ensure_ascii=False, indent=4)

    for i, val in enumerate(all_top_comments):
        print(str(i) + "--->" + val)

    # sentiment_analysis(top_comments)
    return jsonify(all_comments)


def process_comments(response):
    comments = []
    top_comments = []
    for item in response["items"]:
        comment_data = item["snippet"]["topLevelComment"]["snippet"]
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
        comments.append(comment)
        top_comments.append(comment["text"])
    return comments, top_comments


def sentiment_analysis(comments: list[str]):
    analyser = AnalysisSingleton()
    print(analyser.calculate_sentiment_statistics(comments))
    print(analyser.calculate_emotion_statistics(comments))
    print(analyser.calculate_derision_statistics(comments))


if __name__ == "__main__":
    app.run(port=8080)
