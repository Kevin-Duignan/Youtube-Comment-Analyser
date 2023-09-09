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
const response_timeout_error = "";

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
  
  // For testing purposes
  //displayResults(JSON.parse(`{
  //  "sentiment_analysis": {
  //    "neutral":[0.23193239296476045,39],
  //    "negative":[0.1323493428528309,22],
  //    "positive":[0.42666757603486377,59]
  //  },
  //  "emotion_analysis": {
  //    "neutral":[0.2952854464451472,50],
  //    "sadness":[0.06265809759497643,11],
  //    "joy":[0.19916577686866124,30],
  //    "surprise":[0.11126488372683525,19],
  //    "disgust":[0.026280804226795833,5],
  //    "anger":[0.02251772830883662,4],
  //    "fear":[0.003449420134226481,1]
  //  },
  //  "sarcasm_analysis": 0.0
  //}`));
  
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
  
  xmlhttp.open("GET", "http://"+server_address+":"+server_port + "/" + id, true);
  xmlhttp.send();
  
  console.log("[YouTube Comment Analyser]", xmlhttp);
  
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
    if(this.status == 504){
      console.error("Server timed out.");
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
    
  } else if(response_text == response_timeout_error) {
    console.error("Server reported timeout.");
    
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
  
  // Process the data
  var total_comments = results.sentiment_analysis.positive[1] + results.sentiment_analysis.neutral[1] + results.sentiment_analysis.negative[1];
  var percent_positive = Math.round(results.sentiment_analysis.positive[1] / total_comments * 100);
  var percent_neutral  = Math.round(results.sentiment_analysis.neutral[1]  / total_comments * 100);
  var percent_negative = Math.round(results.sentiment_analysis.negative[1] / total_comments * 100);
  
  var percent_emotion0 = Math.round(Object.values(results.emotion_analysis)[0][1] / total_comments * 100);
  var percent_emotion1 = Math.round(Object.values(results.emotion_analysis)[1][1] / total_comments * 100);
  var percent_emotion2 = Math.round(Object.values(results.emotion_analysis)[2][1] / total_comments * 100);
  
  // Create the container for the analysis results
  var analysis_container = document.createElement("div");
  analysis_container.id = "analyser-container";
  analysis_container.classList.add("style-scope");
  analysis_container.classList.add("ytd-comments-header-renderer");
  
  // Create the header
  var analysis_header = document.createElement("span");
  analysis_header.id = "analysis-header";
  analysis_header.classList.add("analyser-text");
  analysis_header.classList.add("analyser-header-text");
  analysis_header.innerHTML = "Comment Analysis:";
  analysis_container.appendChild(analysis_header);
  
  var analysis_container_h_flex = document.createElement("div");
  analysis_container_h_flex.classList.add("analysis-horizontal-flex");
  
  // Create the sentiment analysis container
  var analysis_sentiment_container = document.createElement("div");
  analysis_sentiment_container.id = "analysis-sentiment-display";
  analysis_sentiment_container.classList.add("analysis-data-container");
  
  var analysis_sentiment_text = document.createElement("span");
  analysis_sentiment_text.id = "analysis-sentiment-text";
  analysis_sentiment_text.classList.add("analyser-text");
  analysis_sentiment_text.classList.add("analyser-content-text");
  var sentiment_string =       percent_positive + "% of comments are positive.";
  sentiment_string += "<br>" + percent_neutral + "% of comments are neutral.";
  sentiment_string += "<br>" + percent_negative + "% of comments are negative.";
  analysis_sentiment_text.innerHTML = sentiment_string;
  analysis_sentiment_container.appendChild(analysis_sentiment_text);
  analysis_container_h_flex.appendChild(analysis_sentiment_container);
  
  // Create the emotion analysis container
  var analysis_emotion_container = document.createElement("div");
  analysis_emotion_container.id = "analysis-emotion-display";
  analysis_emotion_container.classList.add("analysis-data-container");
  
  var analysis_emotion_text = document.createElement("span");
  analysis_emotion_text.id = "analysis-emotion-text";
  analysis_emotion_text.classList.add("analyser-text");
  analysis_emotion_text.classList.add("analyser-content-text");
  var sentiment_string =       percent_emotion0 + "% of comments are " + Object.keys(results.emotion_analysis)[0] + ".";
  sentiment_string += "<br>" + percent_emotion1 + "% of comments are " + Object.keys(results.emotion_analysis)[1] + ".";
  sentiment_string += "<br>" + percent_emotion2 + "% of comments are " + Object.keys(results.emotion_analysis)[2] + ".";
  analysis_emotion_text.innerHTML = sentiment_string;
  analysis_emotion_container.appendChild(analysis_emotion_text);
  analysis_container_h_flex.appendChild(analysis_emotion_container);
  
  // Create the sarcasm analysis container
  var analysis_sarcasm_container = document.createElement("div");
  analysis_sarcasm_container.id = "analysis-emotion-display";
  analysis_sarcasm_container.classList.add("analysis-data-container");
  
  var analysis_sarcasm_text = document.createElement("span");
  analysis_sarcasm_text.id = "analysis-emotion-text";
  analysis_sarcasm_text.classList.add("analyser-text");
  analysis_sarcasm_text.classList.add("analyser-content-text");
  var sentiment_string = results.sarcasm_analysis + "% of comments are sarcastic.";
  analysis_sarcasm_text.innerHTML = sentiment_string;
  analysis_sarcasm_container.appendChild(analysis_sarcasm_text);
  analysis_container_h_flex.appendChild(analysis_sarcasm_container);
  
  analysis_container.appendChild(analysis_container_h_flex);
  
  // Add the analysis container to the DOM
  var comment_header = document.getElementById("sections").firstElementChild.firstElementChild;
  comment_header.insertBefore(analysis_container, comment_header.children[5]);
  
  console.log("[YouTube Comment Analyser] analysis_container:", analysis_container);
  
}



init();