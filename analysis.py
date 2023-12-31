from collections import defaultdict
from optimum.onnxruntime import (
    AutoQuantizationConfig,
    AutoOptimizationConfig,
    ORTModelForSequenceClassification,
    ORTQuantizer,
    ORTOptimizer,
)
from transformers import AutoTokenizer
from optimum.pipelines import pipeline
from pathlib import Path


class AnalysisSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalysisSingleton, cls).__new__(cls)
            cls._instance.init_pipelines()
        return cls._instance

    def init_pipelines(self):
        """
        Initializes text classification pipelines for sentiment analysis, emotion analysis, and sarcasm detection.

        Downloads, optimizes, and quantizes the required models if they do not exist locally and initialises
        the pipelines using the optimized and quantized models.
        """
        sentiment_path = Path("onnx", "sentiment")
        emotion_path = Path("onnx", "emotion")
        sarcasm_path = Path("onnx", "sarcasm")

        if not sentiment_path.exists():
            self._optimize_and_quantize_model("cardiffnlp/twitter-roberta-base-sentiment-latest", sentiment_path)

        sentiment_model = ORTModelForSequenceClassification.from_pretrained(
            sentiment_path, file_name="model_optimized_quantized.onnx"
        )
        sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_path)

        self.sentiment_pipeline = pipeline(
            "text-classification", model=sentiment_model, tokenizer=sentiment_tokenizer, accelerator="ort"
        )

        if not emotion_path.exists():
            self._optimize_and_quantize_model("j-hartmann/emotion-english-distilroberta-base", emotion_path)

        emotion_model = ORTModelForSequenceClassification.from_pretrained(
            emotion_path, file_name="model_optimized_quantized.onnx"
        )
        emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_path)

        self.emotion_pipeline = pipeline(
            "text-classification", model=emotion_model, tokenizer=emotion_tokenizer, accelerator="ort"
        )

        if not sarcasm_path.exists():
            self._optimize_and_quantize_model("jkhan447/sarcasm-detection-RoBerta-base-CR", sarcasm_path)

        sarcasm_model = ORTModelForSequenceClassification.from_pretrained(
            sarcasm_path, file_name="model_optimized_quantized.onnx"
        )
        sarcasm_tokenizer = AutoTokenizer.from_pretrained(sarcasm_path)

        self.sarcasm_pipeline = pipeline(
            "text-classification", model=sarcasm_model, tokenizer=sarcasm_tokenizer, accelerator="ort"
        )

    def _optimize_and_quantize_model(self, model_id: str, export_path: Path):
        """
        Downloads, optimizes, and quantizes a model using ONNX Runtime (ORT).

        :model_id (str): The ID or name of the pretrained model to download.
        :export_path (Path): The path where the optimized and quantized model will be saved.
        """
        print(f"{export_path} missing! Downloading {model_id}...")

        model = ORTModelForSequenceClassification.from_pretrained(model_id, export=True)
        tokenizer = AutoTokenizer.from_pretrained(model_id)

        model.save_pretrained(export_path)
        tokenizer.save_pretrained(export_path)

        print(f"{model_id} downloaded! Optimizing...")

        optimizer = ORTOptimizer.from_pretrained(model)
        optimization_config = AutoOptimizationConfig.O3()
        optimizer.optimize(save_dir=export_path, optimization_config=optimization_config)

        print(f"{model_id} optimized! Quantizing...")

        quantizer = ORTQuantizer.from_pretrained(export_path, file_name="model_optimized.onnx")
        qconfig = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=True)

        quantizer.quantize(save_dir=export_path, quantization_config=qconfig)

        model = ORTModelForSequenceClassification.from_pretrained(
            export_path, file_name="model_optimized_quantized.onnx"
        )
        tokenizer = AutoTokenizer.from_pretrained(export_path)

        print(f"{model_id} optimized in quantized into {export_path} !")

    def process_comment_list(self, comment_list: list[str]) -> dict:
        """
        Process a list of comments and perform sentiment analysis, emotion analysis, and sarcasm analysis.

        :comment_list (list[str]): A list of comments to analyse.

        :returns:
            tuple: A tuple containing the analysis results as a dictionary and an HTTP status code.
                The dictionary contains the following keys:
                - "sentiment_analysis": Result of sentiment analysis.
                - "emotion_analysis": Result of emotion analysis.
                - "sarcasm_analysis": Result of sarcasm analysis.
                The HTTP status code is 200, a successful operation.
        """
        content = {
            "sentiment_analysis": self.calculate_sentiment_statistics(comment_list),
            "emotion_analysis": self.calculate_emotion_statistics(comment_list),
            "sarcasm_analysis": self.calculate_sarcasm_score(comment_list),
        }

        return (content, 200)

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
            final_results[label] = [average_score, values[1]]

        # Ensure 0% stats still return
        final_results["positive"] = final_results.get("positive", [0, 0])
        final_results["negative"] = final_results.get("negative", [0, 0])
        final_results["neutral"] = final_results.get("neutral", [0, 0])

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
            final_results[label] = [average_score, values[1]]

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
