from flask import Flask, request, jsonify
from huggingface_hub import InferenceClient

def query():

	client = InferenceClient(
		provider="hyperbolic",
		api_key="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"
	)

	messages = [
		{
			"role": "user",
			"content": "Identify deprecated npm libraries from the list. moment, request. Should be in very minimal words. If deprecated, suggest alternatives. Should be in minimal words"
		}
	]

	stream = client.chat.completions.create(
		model="deepseek-ai/DeepSeek-R1", 
		messages=messages, 
		temperature=0.5,
		max_tokens=2048,
		top_p=0.7,
		stream=True
	)
	message = []
	for chunk in stream:
		print(chunk.choices[0].delta.content, end="")
		message.append(chunk.choices[0].delta.content)
	print(message)
	return True

query()