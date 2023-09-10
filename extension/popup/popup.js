// popup.js
document.addEventListener("DOMContentLoaded", function () {
  originalContent = document.querySelector(".popup-content").innerHTML;

  const server_address = "158.179.17.136";
  const server_port = "8080";
  chrome.tabs.query({active: true, lastFocusedWindow: true}, tabs => {
    let url = tabs[0].url;
    console.log(url)

    if (!url.includes("youtube.com/watch?v=")) {
      displayMessage("Please visit a YouTube video")
    } else {
      displayMessage("Loading...")
      const videoId = url.match(/v=([A-Za-z0-9_\-]+)/)[1];
      let commentData = null
  
      // Send a request to your server
      fetch("http://"+server_address+":"+server_port+"/" + videoId)
        .then((response) => response.json())
        .then((data) => {
          console.log("Response data collected!");
          commentData = data;

          document.querySelector(".popup-content").innerHTML = originalContent;
  
          const emotionAnalysis = commentData.emotion_analysis;
      
          const barChartData = Object.entries(emotionAnalysis).map(
            ([emotion, [value, count]]) => ({
              label: emotion,
              value: value * 100, 
            })
          );
      
          // Add bars to the bar chart
          const barChart = document.querySelector(".bar-chart");
          barChartData.forEach((data) => {
            const bar = document.createElement("div");
            bar.className = "bar";
            bar.style.width = `${data.value}%`;
            bar.style.backgroundColor = "#008cff";
      
            const label = document.createElement("div");
            label.className = "label";
            label.textContent = `${data.label}: ${data.value.toFixed(0)}%`;
      
            barChart.appendChild(label);
            barChart.appendChild(bar);
          });
      
          // Update the sarcasm detection bar
          const filler = document.querySelector(".filler");
          const sarcasmPercentage = commentData.sarcasm_analysis * 100;
          filler.style.width = `${sarcasmPercentage}%`;
          document.querySelector(
            ".progress-label"
          ).textContent = `${sarcasmPercentage.toFixed(0)}% Sarcasm Detection`;
      
          const sentimentAnalysis = commentData.sentiment_analysis;
      
          // Update circles for sentiment analysis
          const sentimentValues = Object.values(sentimentAnalysis);
      
          // Calculate the total sum of values
          const totalCount = sentimentValues.reduce(
            (acc, [value, count]) => acc + count,
            0
          );
      
          // Calculate percentages based on values
          const percentages = sentimentValues.map(
            ([value, count]) => (count / totalCount) * 100
          );

          const confidences = sentimentValues.map(
            ([value, count]) => value * 100
          )
      
          const rings = document.querySelectorAll(".ring circle");
          const spans = document.querySelectorAll(".circle span");
          const circleTexts = document.querySelectorAll(".circle-text");
          const lables = ["Positive", "Negative", "Neutral"]
      
          rings.forEach((ring, index) => {
            const percentage = percentages[index];
            const confidence = confidences[index]
            const circumference = 2 * Math.PI * 40; // Radius is 40
            const offset = ((100 - percentage) / 100) * circumference;
      
            ring.style.strokeDashoffset = offset;
            spans[index].textContent = `${percentage.toFixed(0)}%`;
            circleTexts[index].innerHTML = `<strong>${lables[index]}</strong> Comments : <strong>${confidence.toFixed(0)}%</strong> Confidence`;
            circleTexts[index].style.fontFamily = "Helvetica";
          });
        })
        .catch((error) => {
          console.error("Error sending request to server:", error);
          displayMessage("Error sending request to server...")
        });
    }
  });
});

// Function to display an error message
function displayMessage(message) {
  const errorMessage = document.createElement("div");
  errorMessage.className = "error-message";
  errorMessage.textContent = message;
  errorMessage.style.fontFamily = "Helvetica";
  errorMessage.style.fontWeight = "bold";
  errorMessage.style.fontSize = "18pt";

  // Append the error message to the popup content
  const popupContent = document.querySelector(".popup-content");
  popupContent.innerHTML = "";
  popupContent.appendChild(errorMessage);
}