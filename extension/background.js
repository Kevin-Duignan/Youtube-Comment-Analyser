/**
 * Implements the background functionality of the extension:
 * * Send video ID to the server.
 * * Get analysis from server.
 */

// Server address information
const server_address = "158.179.17.136";
const server_port = "8080";


let commentData = null;

chrome.webNavigation.onCompleted.addListener(function (details) {
  // Check if the URL matches a YouTube video page
  if (details.url.startsWith("https://www.youtube.com/watch")) {
    const videoId = details.url.match(/v=([A-Za-z0-9_\-]+)/)[1];

    // Send a request to your server
    fetch("http://"+server_address+":"+server_port+"/" + videoId)
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
    
    // Message sent from popup
    if(message.video_id == undefined){
      sendResponse(commentData);
      console.log("Sent comment data to popup!");
      return true;
    }
    
    console.log("Got message from script with video ID: " + message.video_id);
    
    // Send a request to the server
    fetch("http://"+server_address+":"+server_port+"/" + message.video_id)
      .then((response) => response.json())
      .then((data) => {
        console.log("Got data from server:", data);
        sendResponse(data);
      })
      .catch((error) => {
        console.error("Error sending request to server:", error);
      });
    
    return true;
  }
  
});
