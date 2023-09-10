![](assets/20230910_174550_logo.svg)

# MACathon 2023 Project Submission

youTubeCommentAnalyser is an extension/website that parses through the comments of a YouTube video, and utilises Natural Language Processing (NLP) to apply sentiment analysis and offer a reliable summary of the thoughts and feelings of the viewers. Three distinct machine learning models are applied to the comments data, providing insightful information about the amount of positive, neutral and negative comments, percentage of comments that fit a particular mood, and percentage of comments that are sarcastic.

![](assets/20230910_180112_image.png)

## How to Run

### Website

1. Visit our [http://158.179.17.136:8080](website)
2. Paste in a valid YouTube URL to a specific video
3. Get the sentiment analysis of the comments, with the link to the video!

### Extension

1. Download ZIP of GitHub, or run `git clone https://github.com/Kevin-Duignan/MACathon-noname`
2. Open Zip
3. Open Chrome, or a Chromium browser
4. Visit [chrome://extensions/]
5. Turn on Developer Mode
6. Load Unpacked
7. Select the _extension_ folder in the project directory
8. Visit any YouTube video
9. See the comment analysis above the comment section, and on the extension popup!

![](assets/20230910_183618_image.png)

### Running Server Locally

```
$ git clone https://github.com/Kevin-Duignan/MACathon-noname
$ cd MACathon-noname
$ pip install -r requirements.txt
$ uvicorn server:app
```

## Contributors

Kevin (Nguyen) Duignan

Daniel Arnould

Anthony Wilson
