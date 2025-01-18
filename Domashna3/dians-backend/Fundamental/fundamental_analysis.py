"""
    This module contains the class FundamentalAnalysis which contains the function get_fund_analysis which is used to get the sentiment of a given text.
    The function translates given text in some language using the translator and returns the sentiment of the translated text using the pipe.
    The function returns 1 if the sentiment is positive and 0 otherwise (neutral or negative).
"""
class FundamentalAnalysis:
    def __init__(self, text, translator, pipe):
        self.text = text
        self.translator = translator
        self.pipe = pipe

    def get_fund_analysis(self):
        text = self.translator(self.text)[0]["translation_text"]
        sentiment = self.pipe(text)
        return 1 if sentiment[0]["label"] == "positive" else 0