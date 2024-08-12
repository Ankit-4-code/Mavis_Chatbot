## app.py
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
import tempfile
import pyaudio
import wave

## Load Dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

openai.api_key = os.getenv("OPEN_AI_KEY")

## Generate Conversation_id

def generate_conversation_id():
    return str(uuid.uuid4())

## FLASK

app = Flask(__name__)
app.debug = True 
#CORS(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

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

def transcribe_audio(audio_file):
    try:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript['text']
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return None
    
def chat_with_gpt(conversation_id, message, is_audio=False):
    ## Get the current date and time
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M')
    current_day = datetime.now().strftime('%A')

    ## Initialize an empty list if the conversation_id is not present
    if conversation_id not in conversations:
        conversations[conversation_id]= []
    
    transcribed_text = None
    
    if is_audio:
        transcribed_text = transcribe_audio(message)
        if not transcribed_text:
            return {"error": "Failed to transcribe audio"}
        message = transcribed_text
        
    ## Append the new user message to the conversations dict with same id
    conversations[conversation_id].append({"role": "user", "content": message})

    

    ## Call the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f" Your name is Mavis. You are a helpful personal assistant. Your main function is to assist the user in scheduling tasks, confirming the scheduled task back to the user, and potentially asking for more details if necessary. Always reply with a confirmation message along with executing the required function call. Always answer in the format 'YYYY-MM-DD' for dates and 'HH:mm' for times. Today, day of the week is {current_day}, date is {current_date} and the current time is {current_time}. You will also answer any general questions regardless of the subject as best as you can."
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
            # Format the weather data into a readable string
            weather_message = (
                f"Current conditions are like:\n"
                f"Weather: {function_result['LocalObservationDateTime']}\n"
                f"Weather: {function_result['WeatherText']}\n"
                f"Temperature: {function_result['TemperatureC']}°C\n"
                f"Real Feel Temperature: {function_result['RealFeelTemperatureC']}°C ({function_result['RealFeelTemperaturePhrase']})\n"
                f"Wind Speed: {function_result['WindSpeedKmh']} km/h"
            )
            print("weather_message is this ",weather_message)
            title_string = weather_message
            
            
        
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
        "function_call": function_call,
        "transcribed_text": transcribed_text
    }


@app.route('/api', methods=['POST'])
def gpt3_endpoint():
    if request.content_type.startswith('multipart/form-data'):
        # Handle audio input
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        conversation_id = request.form.get('conversation_id', generate_conversation_id())
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        gpt_response = chat_with_gpt(conversation_id, temp_file_path, is_audio=True)
        
        os.unlink(temp_file_path)  # Delete the temporary file
    else:

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

@app.route('/api/speech-to-text', methods=['POST'])

def speech_to_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        conversation_id = request.form.get('conversation_id', generate_conversation_id())
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        gpt_response = chat_with_gpt(conversation_id, temp_file_path, is_audio=True)
        
        os.unlink(temp_file_path)  # Delete the temporary file

        return jsonify({
            "message": gpt_response,
            "conversation_id": conversation_id
        })


@app.route('/conversations', methods=['GET'])
def get_conversations():
    return jsonify(conversations)
def record_audio(filename, duration=5, sample_rate=44100, channels=1, chunk=1024):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    print("Recording...")

    frames = []
    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def test_audio_input():
    audio_file = "test_recording.wav"
    record_audio(audio_file)
    
    with open(audio_file, "rb") as file:
        conversation_id = generate_conversation_id()
        response = chat_with_gpt(conversation_id, file, is_audio=True)
    
    print("GPT Response:", response)
    print("Transcribed text:", response.get("transcribed_text", "No transcription available"))
    print("Transcribed text and assistant's reply:", response.get("message", "No message available"))
    print("Function call (if any):", response.get("function_call", "No function call"))

    os.remove(audio_file)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'test_audio':
        test_audio_input()
    else:
        app.run(host='0.0.0.0', port=9000, debug=True)


