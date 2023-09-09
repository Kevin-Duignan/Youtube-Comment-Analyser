/**
 * Implements the main functionality of the extension:
 * * Make requests to server via background script.
 * * Display results on the YouTube webpage.
 */

"use strict";

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
  
  // Request information from the server via the background worker
  chrome.runtime.sendMessage({ method: "getCommentData", video_id: video_id }, function (response) {
    console.log("[YouTube Comment Analyser] Got server response:", response);
    if(response != undefined){
      displayResults(response);
    }else{
      console.error("[YouTube Comment Analyser] Invalid response from background script.");
    }
    
  });
  
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
  var sentiment_string = Math.round(results.sarcasm_analysis*100) + "% of comments are sarcastic.";
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