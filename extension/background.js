// background.js
let commentData = null;

chrome.webNavigation.onCompleted.addListener(function (details) {
  // Check if the URL matches a YouTube video page
  if (details.url.startsWith("https://www.youtube.com/watch")) {
    const videoId = details.url.match(/v=([A-Za-z0-9_\-]+)/)[1];

    // Send a request to your server
    fetch("http://158.179.17.136:8080/" + videoId)
      .then((response) => response.json())
      .then((data) => {
        console.log("Response data collected!");
        commentData = data;
      })
      .catch((error) => {
        console.error("Error sending request to server:", error);
      });
  } else {
    commentData = null;
  }
});

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  if (message.method == "getCommentData") {
    sendResponse(commentData);
    console.log("Sent comment data to popup!");
    return true;
  }
});
