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
  
  //sendVideoID(video_id);
  
  // For testing purposes
  displayResults([
    {
      'positive': (0.6062167062092636, 81),
      'negative': (0.061384336928189814, 11),
      'neutral': (0.1496163114147671, 26)},
    {
      'joy': (0.25913033192440615, 40),
      'neutral': (0.2532283413713261, 44),
      'fear': (0.01478036834021746, 2),
      'anger': (0.03627788161827346, 7),
      'surprise': (0.10265902593984443, 18),
      'sadness': (0.027251392350358478, 5),
      'disgust': (0.009597580059100006, 2)
    },
    {'normal': 95, 'derision': 23}
  ]);
  
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
  
  xmlhttp.open("GET", "http://"+server_address+":"+server_port + "?videoId="+id, true);
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
 * Check if the relevant parts of the DOM are available to insert the comment analysis.
 * @returns {Boolean} True if the relevant parts of the DOM are available.
 */
function checkIfCommentsLoaded(){
  var comment_sections_container = document.getElementById("sections");
  if(comment_sections_container == null){
    return false;
  }
  
  var comment_header = comment_sections_container.firstElementChild.firstElementChild;
  if(comment_header == null){
    return false;
  }
  
  return true;
}

/**
 * Modify the DOM of the YouTube page to display the results of the comment analysis.
 * @param {Object} results The sentiment analysis results.
 */
function displayResults(results){
  
  // Wait for a while if the DOM isn't ready.
  if(!checkIfCommentsLoaded()){
    setTimeout(
      function(){
        displayResults(results);
      },
      dom_check_interval
    );
    return;
  }
  
  // Create the container for the analysis results
  var analysis_container = document.createElement("div");
  analysis_container.id = "analyser-container";
  analysis_container.classList.add("style-scope");
  analysis_container.classList.add("ytd-comments-header-renderer");
  
  // Create the header
  var analysis_header = document.createElement("span");
  analysis_header.is = "analysis-header";
  analysis_header.classList.add("analyser-text");
  analysis_header.classList.add("analyser-header-text");
  analysis_header.innerHTML = "Comment Analysis:";
  analysis_container.appendChild(analysis_header);
  
  // Add the analysis container to the DOM
  var comment_header = document.getElementById("sections").firstElementChild.firstElementChild;
  comment_header.insertBefore(analysis_container, comment_header.children[5]);
  
  console.log("[YouTube Comment Analyser] analysis_container:", analysis_container);
  
}



init();