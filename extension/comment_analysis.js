/**
 * Implements the main functionality of the extension:
 * * Send video ID to the server.
 * * Get analysis from server.
 * * Display results on the YouTube webpage.
 */

"use strict";

// Server address information
const server_address = "158.179.17.136";
const server_port = "8080";

// Server responses to compare against
const response_wait_str = "";

// How long to wait in between requests to the server, in milliseconds
const request_time_interval = 1000;
// How long to wait in between checking if the DOM is loaded, in milliseconds
const dom_check_interval = 400;

// Store the current video ID we're working on
var video_id = "";


function init(){
  console.log("[YouTube Comment Analyser] Script is starting...");
  
  var url = new URL(window.location.href);
  video_id = url.searchParams.get("v");
  console.log("[YouTube Comment Analyser] Video ID:", video_id);
  
  sendVideoID(video_id);
  
}

/**
 * Send the YouTube video ID to the server.
 * @param {String} id YouTube video ID
 */
function sendVideoID(id){
  
  const xmlhttp = new XMLHttpRequest();
  
  //xmlhttp.onload = function() {
  //  handleServerResponse(this.responseText);
  //}
  xmlhttp.onreadystatechange = function(){
    if(this.readyState == 4 && this.status == 200){
      handleServerResponse(this.responseText);
    }
    if(this.status == 500){
      console.error("A server error occurred.");
    }
  };
  
  xmlhttp.open("GET", server_address+":"+server_port + "?videoId="+id, true);
  xmlhttp.send();
  
}

/**
 * Check is the server is done analysing the comments of the most recently sent video.
 */
function checkServerStatus(){
  
  const xmlhttp = new XMLHttpRequest();
  
  //xmlhttp.onload = function() {
  //  handleServerResponse(this.responseText);
  //}
  xmlhttp.onreadystatechange = function(){
    if(this.readyState == 4 && this.status == 200){
      handleServerResponse(this.responseText);
    }
    if(this.status == 500){
      console.error("A server error occurred.");
    }
  };
  
  xmlhttp.open("GET", server_address+":"+server_port + "?videoId="+video_id, true);
  xmlhttp.send();
  
}

/**
 * Wait for a while, then ping the serve again if it isn't done analysing the comments of the most recently sent video.
 * @param {String} response_text The analysis data from the server.
 */
function handleServerResponse(response_text){
  
  if(response_text == response_wait_str) {
    setTimeout(
      function(){
        checkServerStatus();
      },
      request_time_interval
    );
    
  } else {
    // Assume that if a particular response was not given, then the server returned valid JSON data which contains the sentiment analysis results.
    displayResults(JSON.parse(response_text));
  }
  
}


/**
 * Modify the DOM of the YouTube page to display the results of the comment analysis.
 * @param {Object} results The sentiment analysis results.
 */
function displayResults(results){
  var comments_container = document.getElementById("comments");
  console.log("comments_container:", comments_container);
  
  // Wait for a while if the DOM isn't ready.
  if(comments_container == null){
    setTimeout(
      function(){
        displayResults(results);
      },
      dom_check_interval
    );
    return;
  }
  
  // Add the data to the comments container
  
}



init();