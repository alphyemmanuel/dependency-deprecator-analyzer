from flask import Flask, request, jsonify
from huggingface_hub import InferenceClient
import json
import os
import requests
import re
import deepseek_util
import github_util

def startAnalyzer():
    deprecated_libs = query()
    print("deprecated_libs >>>",deprecated_libs)
    return
    # scannedFileResponse = scan_files()

def query():
    COMMIT_SHA = os.getenv("COMMIT_ID")
    file_path = "./cloned_repo/package.json"
    with open(file_path, "r") as file:
        package_data = json.load(file)

    dependencies = package_data.get("dependencies", {})
    package_list = "\n".join(dependencies.keys())
    messages = [
    {
        "role": "user",
        "content": f"Identify deprecated npm libraries from this list:\n{package_list}\n"
                   "If deprecated, suggest alternatives in the format:\n"
                   "'Deprecated: <lib_name> -> Use: <alternative>' -> Reason: <reason>"
    }
    ]

    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    client = InferenceClient(
		provider="hyperbolic",
		api_key=HUGGINGFACE_TOKEN
	)

    response = client.chat.completions.create(
		model="deepseek-ai/DeepSeek-R1", 
		messages=messages, 
		temperature=0.5,
		max_tokens=2048,
		top_p=0.7,
		# stream=True
	)
    ai_response = response.choices[0].message["content"]
    # print("ai_response >>>",ai_response)
    deprecatedLibComments = []
    deprecatedLibObject = {}
    for line in ai_response.split("\n"):
        print("Line here: ", line)
        if "Deprecated:" in line and "-> Use:" in line:
            print("Line here: ", line)
            deprecatedLibComments.append(line)
            deprecated, alternative = line.split("-> Use:")
            deprecatedLibObject[deprecated] = alternative.split("-> Reason:")[0]
            print(deprecatedLibObject)
            print("*****************")
            # print(alternative)
    print("deprecatedLibObject >>>",deprecatedLibObject)
    github_util.post_commit_comment(COMMIT_SHA,"\n".join(deprecatedLibComments))
    # return {deprecated, alternative}
    return deprecatedLibObject


# def scan_files(directory):
#     moment_files = []
#     for root, _, files in os.walk(directory):
#         for file in files:
#             if file.endswith(('.js', '.ts')):
#                 file_path = os.path.join(root, file)
#                 try:
#                     with open(file_path, 'r', encoding='utf-8') as f:
#                         content = f.read()
#                         if re.search(r'\bmoment\b', content):
#                             moment_files.append(file_path)
#                 except Exception as e:
#                     print(f"Error reading {file_path}: {e}")
    
#     return moment_files

# project_folder = "./cloned_repo"
# moment_files = scan_files(project_folder)
# print(moment_files)
# messages = []
# if moment_files:
#     print("Files using moment:")
#     for file in moment_files:
#         print(f"- {file}")
#         with open(file, 'r', encoding='utf-8') as f:
#             # print(f.read())  # Print file content
#             print("-" * 50)
#             contents = f.read()
#             messages.append({
#         "role": "user",
#         "content": f"{contents} send the corresponding code using dayjs"
#     })
# else:
#     print("No files using moment were found.")
# print("*****",messages)

# query()
startAnalyzer()