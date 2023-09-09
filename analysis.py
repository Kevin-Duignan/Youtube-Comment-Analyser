from collections import defaultdict
from optimum.onnxruntime import (
    AutoQuantizationConfig,
    AutoOptimizationConfig,
    ORTModelForSequenceClassification,
    ORTQuantizer,
    ORTOptimizer
)
from transformers import AutoTokenizer
from optimum.pipelines import pipeline
import time
import json

class AnalysisSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalysisSingleton, cls).__new__(cls)
            cls._instance.init_pipelines()
        return cls._instance
    
    def init_pipelines(self):
        self.sentiment_pipeline = pipeline(
            task="text-classification",
            # model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            accelerator="ort"
        )

        self.emotion_pipeline = pipeline(
            task="text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            accelerator="ort"
        )

        self.sarcasm_pipeline = pipeline(
            task="text-classification",
            model="jkhan447/sarcasm-detection-RoBerta-base-CR",
            accelerator="ort"
        )
        
    def calculate_sentiment_statistics(self, comment_list: list[str]) -> dict:
        """
        Calculate sentiment statistics for a list of comments.

        :comment_list: A list of comments.

        :returns: A dictionary containing sentiment statistics.
                The keys are sentiment labels, and the values are tuples
                (average score, count).
        """
        # Store sentiment scores and counts for each label
        sentiment_stats = defaultdict(lambda: [0, 0])
        sentiment_results = self.sentiment_pipeline(comment_list)

        # Process sentiment results and update sentiment statistics
        for result in sentiment_results:
            label, score = result["label"], result["score"]
            sentiment_stats[label] = [sentiment_stats[label][0] + score, sentiment_stats[label][1] + 1]

        # Calculate average scores for each sentiment label and adds count
        final_results = {}
        for label, values in sentiment_stats.items():
            average_score = values[0] / len(comment_list)
            final_results[label] = (average_score, values[1])

        return final_results
    
    def calculate_emotion_statistics(self, comment_list: list[str]) -> dict:
        """
        Calculate emotion class spread for a list of comments.

        :comment_list: A list of comments.

        :returns: A dictionary containing emotion statistics with classes
        anger, disgust, fear, joy, neutral, saddness, and surprise.
                The keys are emotion labels, and the values are tuples
                (average score, count).
        """
        # Store sentiment scores and counts for each label
        emotion_stats = defaultdict(lambda: [0, 0])
        emotion_results = self.emotion_pipeline(comment_list)

        # Process sentiment results and update sentiment statistics
        for result in emotion_results:
            label, score = result["label"], result["score"]
            emotion_stats[label] = [emotion_stats[label][0] + score, emotion_stats[label][1] + 1]

        # Calculate average scores for each sentiment label and adds count
        final_results = {}
        for label, values in emotion_stats.items():
            average_score = values[0] / len(comment_list)
            final_results[label] = (average_score, values[1])

        return final_results
    
    def calculate_sarcasm_score(self, comment_list: list[str]) -> float:
        """
        Calculates proportion of comments which are sarcastic

        :comment_list: A list of comments.

        :returns: A float, representing proportion of comments which are sarcastic
        """
        # Store number of comments that are sarcastic
        sarcasm_score = 0

        sarcasm_results = self.sarcasm_pipeline(comment_list)

        # Process sarcasm results and update derision statistics
        for result in sarcasm_results:
            label = result["label"]
            sarcasm_score += int(label == "LABEL_1")

        sarcasm_score /= len(comment_list)

        return sarcasm_score

