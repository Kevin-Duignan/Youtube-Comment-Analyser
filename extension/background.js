/**
 * Implements the background functionality of the extension:
 * * Send video ID to the server.
 * * Get analysis from server.
 */

// Server address information
const server_address = "158.179.17.136";
const server_port = "8080";

chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  
  if (message.method == "getCommentData") {
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
