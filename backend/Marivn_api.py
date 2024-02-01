import requests
import os
import json
from dotenv import load_dotenv
from Google_Calendar import calendar
from accuweather_api import getLocation, currentConditions

## Load environment variables from .env file
load_dotenv()

## Get Marvin API Token from the envioronment variable
MARVIN_API_TOKEN = os.getenv('MARVIN_API_KEY')
MARVIN_API_ENDPOINT = 'https://serv.amazingmarvin.com/api/'

headers = {
    'X-API-Token': MARVIN_API_TOKEN
}

FUNCTION_DESCRIPTIONS = [
    {
        "name": "add_task",
        "description": "Add a new task using Amazing Marvin API like Meeting with John on Monday('YYYY-MM-DD') at 'HH:mm'",
        "parameters":{
            "type": "object",
            "properties":{
                "title": {
                    "type": "string",
                    "description": "The task's title, like Go to market, book a doctor's appointment, Lab work, University(Uni),etc. on 'DAY' at 'HH:mm' hours(24 hours format)",
                },

                "date":{
                    "type": "string",
                    "description": "Which day the task is scheduled, in the format 'YYYY-MM-DD'.",

                },

                "time": {
                    "type": "string",
                    "description": "Time in 'HH:mm' format of the task. Convert to 24 hours format.",
                },

                "timeEstimate": {
                    "type": "string",
                    "description":"How long the user thinks the task will take, formatted as 'HH:mm' ",
                },

                 "dueDate"  : {
                     "type": "string",
                     "description": "When this project/task should be completed, formatted as 'YYYY-MM-DD'. Or null if no dueDate.",
                 },

                 "reviewDate" : {
                     "type": "string",
                     "description": "Date when user wants to review a task or when to remind the user of the task, formatted as 'YYYY-MM-DD'.",
                 },



            },
            "required": ["title", "date"],

        },
    },
    {
        "name":"scheduled_today",
        "description": "Get a list of tasks and projects for the given date.",
        "parameters": {
            "type": "object",
            "properties":{
                "schedule_date": {
                    "type": "string",
                    "description": " Date about which the user wants to know all of his scheduled task and projects. Formatted as 'YYYY-MM-DD'.",

                },
            },
            "required": ["schedule_date"],
    },
    },
    {
        "name" : "upcoming_tasks",
        "description": "Get a date or a range of dates( like next week) from the user from which upcoming tasks/events/projects will be displayed. For example: upcoming tasks from '2024-12-01' or upcoming tasks/ schedule from '2023-10-25' to '2023-11-02'. ",
        "parameters":{
            "type": "object",
            "properties": {
                "startDate" : {
                    "type": "string",
                    "description": " Start Date from which the user wants upcoming tasks to be shown. By default if said nothing. It's upcoming tasks from 'today'. And Always format it to 'YYYY-MM-DD'.",

                },
                "endDate":{
                    "type": "string",
                    "description": "End Date till which date the user wants to know upcoming tasks. Always format it to 'YYYY-MM-DD'.",
                },
            },
            "required": ["startDate"],

        },
    },
    {
        "name" : "weather",
        "description": " Get weather details/forecasts for a specific location given by the user.", 
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location, about which the user wants to know the weather details or forcasts. Just the name of the place like Berlin, Amsterdam , London etc.",
                
                },

                "forecastTime": {
                    "type": "string",
                    "description": " Time frame of forecast that the user wants information about. Only next (1-12 hours) OR (1-5 days) are possible. example: Return('2 days') or Return('4 hours').If nothing is mentioned or any other number is said send None.",
                },

            },
            "required": ["location"],
        },
    
    },
    
]

def scheduled_today(date):
    ## Pass the date as a string of the format YYYY-MM-DD
    endpoint = f"{MARVIN_API_ENDPOINT}todayItems"
    headers['X-Date'] = date  # Adding date to headers
    
    response = requests.get(endpoint, headers=headers)
    print("Response text is : ", response.text)
    
    return response.json()



def add_task(task_data):
    endpoint = f"{MARVIN_API_ENDPOINT}addTask"
    response = requests.post(endpoint, headers = headers , json= task_data)
    print("response satus : ", response.status_code)
    print("response text is : ",response.text)
    return response.json()

def execute_function_from_gpt(gpt_response):

    function_call = gpt_response.get("function_call")
    if function_call:
        function_name = function_call.get("name")
        arguments = json.loads(function_call.get("arguments"))

        if function_name == "add_task" and arguments:

            task_data ={"done": False,}

            ## Get the original title, date, and time from the arguments
            original_title = arguments.get("title")
            date = arguments.get("date")
            time =  arguments.get("time")

            ## Modify the title to include date and time. Which can be used for calandar sync with Marvin.
            modified_title = original_title
            if date:
                modified_title += f" on {date}"
                task_data["day"] = date
                task_data["firstScheduled"] = date
            if time:
                modified_title += f" at {time} hrs"
                task_data["taskTime"] = time

            ## Mapping the arguments to the task data dictionary
            task_data["title"] = modified_title

            ## List of Keys which are addTask date types for the endpoint
            keys = ["timeEstimate", "dueDate", "reviewDate"]

            ## Using dictionary to add only the keys that have values
            additional_data = {k : arguments.get(k) for k in keys if arguments.get(k) is not None}

            ## If timeEstimate exists in HH:mm format, convert it to milliseconds
            if "timeEstimate" in additional_data:
                hours, minutes = map(int, additional_data["timeEstimate"].split(':'))
                total_minutes = hours * 60 + minutes
                additional_data["timeEstimate"] = total_minutes * 60000  # converting to milliseconds


            ## Update task_data with the additional_data
            task_data.update(additional_data)

                
            print("Calling add_task with:", task_data)
            return add_task(task_data)


        if function_name == "scheduled_today" and arguments:
            schedule_date = str(arguments.get("schedule_date"))
            return scheduled_today(schedule_date)
        
        if function_name == "upcoming_tasks" and arguments:
            startDate = arguments.get("startDate")
            endDate = arguments.get("endDate")   
            return calendar(startDate,endDate)
        
        if function_name == "weather" and arguments:
            location = arguments.get("location")
            cityKey = getLocation(location)
            currentWeather = currentConditions(cityKey)
            return currentWeather

            
    return None
