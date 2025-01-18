"""
    This module contains the function get_fund_analysis which is used to get the sentiment of a given text.
    The function translates given text in some language using the translator and returns the sentiment of the translated text using the pipe.
    The function returns 1 if the sentiment is positive and 0 otherwise (neutral or negative).
"""
def get_fund_analysis(text, translator, pipe):
    text = translator(text)[0]["translation_text"]
    sentiment = pipe(text)
    return 1 if sentiment[0]["label"] == "positive" else 0