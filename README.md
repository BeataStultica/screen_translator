# An application for recognising text on the screen, translating it and displaying the translation over the original text. 
PaddleOCR is used for recognition (https://github.com/PaddlePaddle/PaddleOCR), which shows much better accuracy than tesseractOCR, 
but is slower. I will add other OCRs for comparison later on. For translation, DeepL is used. Because of a blockage due to frequent 
requests for free api and the lack of possibility to buy premium in my country, the translation works via selenium. 
For weak computers ipynb notepad was created to run the recognition server in google colab, to recognize locally you need 
to change the argument server_mode=False in the function output.
