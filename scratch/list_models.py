import os
from google import genai
from google.genai import types

def list_models():
    api_key = "AIzaSyAc8-1ZXEToPM23p8BMO3Q3yZaCYrPBMXw"
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    
    print("Available models:")
    for model in client.models.list():
        print(f" - {model.name}")

if __name__ == "__main__":
    list_models()
