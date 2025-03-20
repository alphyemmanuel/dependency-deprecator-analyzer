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
    if deprecated_libs:
        modified_files = scan_and_refactor_files("./cloned_repo", deprecated_libs)
        post_github_comment(deprecated_libs, modified_files)

def query():
    try:
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
                           "'Deprecated: <lib_name> -> Use: <alternative1>, <alternative2> -> Reason: <reason>'"
            }
        ]

        HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
        client = InferenceClient(provider="hyperbolic", api_key=HUGGINGFACE_TOKEN)
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1", 
            messages=messages, 
            temperature=0.5,
            max_tokens=2048,
            top_p=0.7,
        )
        ai_response = response.choices[0].message.get("content", "")
        
        deprecatedLibObject = {}
        for match in re.finditer(r"Deprecated:\s*(.*?)\s*->\s*Use:\s*(.*?)\s*->\s*Reason:\s*(.*)", ai_response):
            lib_name, alternatives, reason = match.groups()
            print(f"Extracted - Library: {lib_name}, Alternatives: {alternatives}, Reason: {reason}")  # Debugging
            alternative_list = [alt.strip() for alt in alternatives.split(",")]
            deprecatedLibObject[lib_name.strip()] = {
                "alternatives": alternative_list,
                "reason": reason.strip()
            }

        return deprecatedLibObject
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}

def scan_and_refactor_files(directory, deprecated_libs):
    modified_files = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.js', '.ts')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for lib, details in deprecated_libs.items():
                            escaped_lib = re.escape(lib)  # Escape special characters in lib
                            if re.search(rf'\b{escaped_lib}\b', content):
                                chosen_alternative = details["alternatives"][0]  # Pick first alternative
                                refactored_content = generate_refactored_code(content, lib, chosen_alternative)
                                modified_files[file_path] = {
                                    "deprecated": lib,
                                    "alternative": chosen_alternative,
                                    "updated_content": refactored_content
                                }
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return modified_files

def generate_refactored_code(content, deprecated_lib, alternative_lib):
    messages = [
        {
            "role": "user",
            "content": f"Refactor the following JavaScript/TypeScript code '{content}' by replacing '{deprecated_lib}' with '{alternative_lib}'. Provide only the final refactored implementation in the format of :\n"
                        "'Original Function is: <original_code> ->  <alternative_lib_name> Definition: <alternative_lib_definition> -> Refactored Code: <refactored_code>'.\n\n"
        }
    ]
    
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    client = InferenceClient(provider="hyperbolic", api_key=HUGGINGFACE_TOKEN)
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-R1", 
        messages=messages, 
        temperature=0.5,
        max_tokens=2048,
        top_p=0.7,
    )
    return response.choices[0].message.get("content", content)

def post_github_comment(deprecated_libs, modified_files):
    COMMIT_SHA = os.getenv("COMMIT_ID")
    comment_body = ""
    
    for lib, details in deprecated_libs.items():
        comment_body += (f"### `{lib}`\n"
                         f"- **Use:** {', '.join(details['alternatives'])}\n"
                         f"- **Reason:** {details['reason']}\n\n")
    
    if modified_files:
        comment_body += "## Code Refactoring Suggestions\n\n"
        for file, data in modified_files.items():
            comment_body += (f"### `{file}`\n"
                             f"#### Before\n"
                             f"```js\n"
                             f"// Uses {data['deprecated']}\n"
                             f"...\n"
                             f"```\n"
                             f"#### After\n"
                             f"```js\n"
                             f"{data['updated_content']}\n"
                             f"```\n")
    
    github_util.post_commit_comment(COMMIT_SHA, comment_body)

startAnalyzer()
