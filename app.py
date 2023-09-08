from flask import Flask, jsonify
from googleapiclient.discovery import build
import json

app = Flask(__name__)
api_key = "AIzaSyBtxJEet5gIXlbXD2gtCKwcss98JnT-Am0"  # Replace with your YouTube API key
youtube_service = build("youtube", "v3", developerKey=api_key)


@app.route("/<video_id>")
def get_comments(video_id):
    request = youtube_service.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        maxResults=100,  # Google's API has a limit on the max results
    )
    response = request.execute()

    comments = []
    for item in response["items"]:
        comment_data = item["snippet"]["topLevelComment"]["snippet"]
        comment = {
            "author": comment_data["authorDisplayName"],
            "publishedAt": comment_data["publishedAt"],
            "text": comment_data["textDisplay"],
            "likes": comment_data["likeCount"],
            "replies": [],
        }
        if item.get("replies"):
            for reply in item["replies"]["comments"]:
                reply_data = reply["snippet"]
                reply = {
                    "author": reply_data["authorDisplayName"],
                    "publishedAt": reply_data["publishedAt"],
                    "text": reply_data["textDisplay"],
                    "likes": reply_data["likeCount"],
                }
                comment["replies"].append(reply)
        comments.append(comment)
    # Writes comments to JSON file
    with open("comments.json", "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)

    return jsonify(comments)


if __name__ == "__main__":
    app.run(port=8080)
