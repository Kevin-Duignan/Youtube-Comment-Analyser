// popup.js
document.addEventListener("DOMContentLoaded", function () {
  originalContent = document.querySelector(".popup-content").innerHTML;

  chrome.runtime.sendMessage({ method: "getCommentData" }, function (response) {
    commentData = response;

    // Check if commentData is null or does not contain the required attributes
    if (
      !commentData ||
      !commentData.emotion_analysis ||
      !commentData.sarcasm_analysis ||
      !commentData.sentiment_analysis
    ) {
      const errorMessage = document.createElement("div");
      errorMessage.className = "error-message";
      errorMessage.textContent = "Please visit a YouTube video";
      errorMessage.style.fontFamily = "Helvetica";
      errorMessage.style.fontWeight = "bold";
      errorMessage.style.fontSize = "18pt";

      // Append the error message to the popup content
      const popupContent = document.querySelector(".popup-content");
      popupContent.innerHTML = "";
      popupContent.appendChild(errorMessage);
    } else {
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
        bar.style.backgroundColor = "#3498db";

        const label = document.createElement("div");
        label.className = "label";
        label.textContent = `${data.label}: ${data.value.toFixed(2)}%`;

        barChart.appendChild(label);
        barChart.appendChild(bar);
      });

      // Update the sarcasm detection bar
      const progressBar = document.querySelector(".progress-bar");
      const filler = document.querySelector(".filler");
      const sarcasmPercentage = commentData.sarcasm_analysis * 100;
      progressBar.style.width = `${sarcasmPercentage}%`;
      filler.style.width = `${sarcasmPercentage}%`;
      document.querySelector(
        ".progress-label"
      ).textContent = `${sarcasmPercentage.toFixed(2)}% Sarcasm Detection`;

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

      const rings = document.querySelectorAll(".ring circle");
      const spans = document.querySelectorAll(".circle span");

      rings.forEach((ring, index) => {
        const percentage = percentages[index];
        const circumference = 2 * Math.PI * 40; // Radius is 40
        const offset = ((100 - percentage) / 100) * circumference;

        ring.style.strokeDashoffset = offset;
        spans[index].textContent = `${percentage.toFixed(2)}%`;
      });
    }
  });
});
