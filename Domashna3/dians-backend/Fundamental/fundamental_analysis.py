from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

def get_fundamental_analysis(text):
    model_name = "tabularisai/multilingual-sentiment-analysis"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mk-en")

    def predict_sentiment(texts):
        inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        sentiment_map = {0: "Very Negative", 1: "Negative", 2: "Neutral", 3: "Positive", 4: "Very Positive"}
        return [sentiment_map[p] for p in torch.argmax(probabilities, dim=-1).tolist()]
    
    text = translator(text)[0]["translation_text"]
    sentiment = predict_sentiment(text)
    
    print(text, sentiment)
    
    return sentiment
