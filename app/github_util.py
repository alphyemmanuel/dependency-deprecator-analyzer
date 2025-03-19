from flask import Flask, request, jsonify
from huggingface_hub import InferenceClient
import os
import requests

def post_commit_comment(commit_sha, comment):
    GITHUB_TOKEN = os.getenv("GIT_TOKEN")  
    REPO_OWNER = os.getenv("REPO_OWNER") 
    print(GITHUB_TOKEN, REPO_OWNER)
    REPO_NAME = "node-dependency-deprecator-analyzer-sample-project"
    COMMENT_BODY = "🚀 This is an automated comment! Deprecated libraries detected."
    """ Posts a comment on a specific commit """
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{commit_sha}/comments"
    headers = {

        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        'X-GitHub-Api-Version': '2022-11-28'
    }
    data = {"body": comment}
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("✅ Comment posted successfully!")
        print(response.json())
    else:
        print(f"❌ Failed to post comment: {response.status_code}, {response.text}")

    return True