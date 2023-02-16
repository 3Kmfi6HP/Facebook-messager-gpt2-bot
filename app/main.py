import os
import requests
import json
import re

from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# This function is used to send the message to GPT-2 API
def send_message_to_gpt2(text):
    headers = {
        "Content-Type": "application/json",
    }
    try:
        response =  requests.post(url='https://hf.space/embed/xibaozi/gpt2-chitchat/+/api/predict/', headers=headers, json={"data":[text]})
        response = json.loads(response.text)
        response = response["data"]
        response = re.sub(r"【.+】|\s+", "", str(response))
        response = re.sub(r"[^\w\s]", "", str(response))
    except Exception as e:
        response = e
    return response

# This function is used to send a message to the user
def send_message(recipient_id, message_text):
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
    }
    params = {"access_token": ACCESS_TOKEN}
    r = requests.post(
        "https://graph.facebook.com/v16.0/me/messages", headers=headers, params=params, json=data
    )
    print(r)
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)
# import facebook
# # import facebook sdk
# def send_message(sender_id, message_text, access_token):
#     graph = facebook.GraphAPI(access_token)
#     recipient = {"id": sender_id}
#     message = {"text": message_text}
#     graph.put_object(recipient["id"], "messages", message=message)

@app.route("/", methods=["GET", "POST"])
def receive_message():
    if request.method == "GET":
        # Check if the verify token is correct
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        else:
            return "Invalid verification token"
    elif request.method == "POST":
        # Get the message content from the request
        payload = request.json
        print(payload)
        for event in payload["entry"][0]["messaging"]:
            if "message" in event:
                try:
                    # Extract the message text and sender ID
                    text = event["message"]["text"]
                    # print(text)
                    sender_id = event["sender"]["id"]
                    # print(sender_id)
                    # Send the message to GPT-2 API and get the response
                    response_text = send_message_to_gpt2(text)
                    # print(response_text)
                    # Send the response back to the user
                    send_message(sender_id, response_text)
                    # send_message(sender_id, "response_text", ACCESS_TOKEN)
                except Exception as e:
                    pass
        return "OK"
