from huggingface_hub import InferenceClient
import os

def runQuery(message):
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    client = InferenceClient(
		provider="hyperbolic",
		api_key=HUGGINGFACE_TOKEN
	)

    response = client.chat.completions.create(
		model="deepseek-ai/DeepSeek-R1", 
		messages=message, 
		temperature=0.5,
		max_tokens=2048,
		top_p=0.7,
		# stream=True
	)

    return response