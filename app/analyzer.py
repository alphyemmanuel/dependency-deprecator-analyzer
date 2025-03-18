from flask import Flask, request, jsonify
from huggingface_hub import InferenceClient
import json
import os
import sys

def query():
    COMMIT_SHA = os.getenv("COMMIT_ID")
    print("COMMIT_SHA >>>", COMMIT_SHA, sys.argv[1])
    file_path = "./cloned_repo/package.json"

    with open(file_path, "r") as file:
        package_data = json.load(file)
        # file_content = file.read()

    dependencies = package_data.get("dependencies", {})
    package_list = "\n".join(dependencies.keys())

    client = InferenceClient(
		provider="hyperbolic",
		api_key="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"
	)

	# messages = [
	# 	{
	# 		"role": "user",
	# 		"content": "Identify deprecated npm libraries from the list. moment, request. Should be in very minimal words. If deprecated, suggest alternatives. Should be in minimal words"
	# 	}
	# ]
    messages = [
    {
        "role": "user",
        "content": f"Identify deprecated npm libraries from this list:\n{package_list}\n"
                   "If deprecated, suggest alternatives in the format:\n"
                   "'Deprecated: <lib_name> -> Use: <alternative>' -> Reason : <reason>"
    }
    ]

    response = client.chat.completions.create(
		model="deepseek-ai/DeepSeek-R1", 
		messages=messages, 
		temperature=0.5,
		max_tokens=2048,
		top_p=0.7,
		# stream=True
	)
    ai_response = response.choices[0].message["content"]

    # print(ai_response)
    # updated_content = file_content
    for line in ai_response.split("\n"):
        if "Deprecated:" in line and "-> Use:" in line and "-> Reason:" in line:
            print("Line here: ", line)
            deprecated, alternative = line.split("-> Use:")
            print(deprecated)
            print("*****************")
            print(alternative)
        #     deprecated_lib = deprecated.replace("Deprecated:", "").strip()
        #     alternative_lib = alternative.strip()
        # if deprecated_lib in dependencies:
        #     dependencies[alternative_lib] = dependencies.pop(deprecated_lib)

        # updated_content = updated_content.replace(deprecated_lib, alternative_lib)
    # message = []
    # for chunk in stream:
    #     print(chunk.choices[0].delta.content, end="")
    #     message.append(chunk.choices[0].delta.content)

    # print(deprecated_lib)
    # print(alternative_lib)
    # print("***************")
    # print(deprecated)
    # print(alternative)
    return True

query()