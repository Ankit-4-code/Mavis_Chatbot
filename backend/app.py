## Importing all the libraries and dependecies

from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime
import uuid
from Marivn_api import execute_function_from_gpt
from Marivn_api import FUNCTION_DESCRIPTIONS
import json
## Load Dotenv
load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPEN_AI_KEY")

## Generate Conversation_id

def generate_conversation_id():
    return str(uuid.uuid4())

## FLASK

app = Flask(__name__)
CORS(app)

## Store Conversations in a dictionary
conversations = {}
def extract_titles(json_obj):
    titles = []
    
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            if k == 'title':
                titles.append(v)
            elif isinstance(v, (dict, list)):
                titles.extend(extract_titles(v))
                
    elif isinstance(json_obj, list):
        for item in json_obj:
            titles.extend(extract_titles(item))
            
    return titles

def chat_with_gpt(conversation_id, message):
    ## Get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M')

    ## Initialize an empty list if the conversation_id is not present
    if conversation_id not in conversations:
        conversations[conversation_id]= []
    
    ## Append the new user message to the conversations dict with same id
    conversations[conversation_id].append({"role": "user", "content": message})


    ## Call the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f" Your name is Mavis. You are a helpful personal assistant. Your main function is to assist the user in scheduling tasks, confirming the scheduled task back to the user, and potentially asking for more details if necessary.Always reply with a confirmation message along with executing the required function call. Always answer in the format 'YYYY-MM-DD' for dates and 'HH:mm' for times. Today's date is {current_date} and the current time is {current_time}. You will also answer any general questions regardless of the subject as best as you can."
            },
            *conversations[conversation_id]
    ],
    functions = FUNCTION_DESCRIPTIONS,
    function_call = "auto",
        max_tokens=200,
        temperature=0.7
    )
    print(f"GPT-3 Raw Response: {response}") 

    assistant_response = response.choices[0].message
    assistant_message =  assistant_response['content']
    function_call = assistant_response.get("function_call")
    print(f"Assistant Message: {assistant_message}")
    print(f"Function Call: {function_call}")

    if function_call:
        function_name = function_call["name"]
        function_args = json.loads(function_call["arguments"])

        ## Execute the function and get the result
        function_result = execute_function_from_gpt(assistant_response)

        print("function_result :", function_result)

        if function_result and function_call["name"]=="add_task" and function_result.get("createdAt"):
            title_string = str(function_result.get("title"))
            if function_result.get("timeEstimate"):
                title_string += f" ETA {function_result.get('timeEstimate')}."
            if function_result.get("dueDate"):
                title_string += f" Due Date on {function_result.get('dueDate')}."
            if function_result.get("reviewDate"):
                title_string += f" Will be Reminded on {function_result.get('reviewDate')}."

        if function_result and function_call["name"] == "scheduled_today":
            #print("function_result for schedule_date :", function_result)
            titles = extract_titles(function_result)

             
             ## Joining all the titles by , 
            title_string = ', '.join([str(title) for title in titles])

            print(" Title String : ",title_string)

        if function_result and function_name == "upcoming_tasks":
            print("10 upcoming tasks : ",function_result)
            title_string = function_result

        if function_result and function_name == "weather":
            print("Current Weather Conditions are like", function_result)
            title_string = function_result
            
            
        
        ## Append the function result to the conversation
        conversations[conversation_id].append({
            "role": "function",
            "name": function_name,
            "content": title_string  ## a string
        })
        
        ## Get a second response from GPT-3 with the updated conversation
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversations[conversation_id],
            functions=FUNCTION_DESCRIPTIONS,
            function_call="auto",
            max_tokens=200,
            temperature=0.7
        )

        ## Update the assistant_response to be the new message from the second response
        assistant_response = second_response.choices[0].message
        assistant_message = assistant_response['content']

        ## Append this new assistant message to the conversation
        conversations[conversation_id].append({"role":"assistant", "content": assistant_message})


    return {
        "message": assistant_message,
        "function_call": function_call
    }


@app.route('/api', methods=['POST'])
def gpt3_endpoint():
    data = request.get_json()
    user_message = data['message']
    
    ## Check if conversation_id is provided, if not generate a new one
    conversation_id = data.get('conversation_id')
    if conversation_id is None:
        conversation_id = generate_conversation_id()  # You should implement this function
    
    
    ## Use the chat_with_gpt function to get the response
    gpt_response = chat_with_gpt(conversation_id, user_message)
    print(gpt_response)


    ## Debug: Print all conversation_ids and their respective conversations
    print("All Conversations:")
    for id, conversation in conversations.items():
        print(f"Conversation ID: {id}")
        print(conversation)
        print("\n")

    return jsonify({
        "message": gpt_response,
        "conversation_id": conversation_id
    })

@app.route('/conversations', methods=['GET'])
def get_conversations():
    return jsonify(conversations)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)

