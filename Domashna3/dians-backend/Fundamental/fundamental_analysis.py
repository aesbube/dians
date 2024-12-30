def get_fund_analysis(text, translator, pipe):    
    text = translator(text)[0]["translation_text"]
    sentiment = pipe(text)
    return 1 if sentiment[0]["label"] == "positive" else 0