from collections import defaultdict
from transformers import pipeline
from multiprocessing import Pool, cpu_count


class AnalysisSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalysisSingleton, cls).__new__(cls)
            cls._instance.init_pipelines()
        return cls._instance

    def init_pipelines(self):
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )

        self.emotion_pipeline = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base")

        self.sarcasm_pipeline = pipeline("text2text-generation", model="mrm8488/t5-base-finetuned-sarcasm-twitter")

    def run_analysis(self, comment_list):
        # with Pool(cpu_count()) as pool:
        #     sentiment_results = pool.apply_async(self.calculate_sentiment_statistics, (comment_list,))
        #     emotion_results = pool.apply_async(self.calculate_emotion_statistics, (comment_list,))
        #     derision_results = pool.apply_async(self.calculate_derision_statistics, (comment_list,))
        #     pool.close()
        #     pool.join()

        sentiment_results = self.calculate_sentiment_statistics(comment_list)
        emotion_results = self.calculate_emotion_statistics(comment_list)
        derision_results = self.calculate_derision_statistics(comment_list)

        # Combine the results from all the analysis into a single dictionary
        combined_results = {
            "sentiment": sentiment_results,
            "emotion": emotion_results,
            "derision": derision_results,
        }

        return combined_results

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

    def calculate_derision_statistics(self, comment_list: list[str]) -> dict:
        """
        Calculate spread of sarcasm in a comment list.

        :comment_list: A list of comments.

        :returns: A dictionary containing counts for derision and normal comments.
                Keys are "normal", "derision", and the values are ints
        """
        # Store derision counts
        sarcasm_stats = defaultdict(lambda: 0)

        sarcasm_results = self.sarcasm_pipeline(comment_list)

        # Process sarcasm results and update derision statistics
        for result in sarcasm_results:
            label = result["generated_text"]
            # Model produces a spelling error
            label = "derision" if "derison" in label else "normal"
            sarcasm_stats[label] += 1

        final_results = dict(sarcasm_stats)

        return final_results
