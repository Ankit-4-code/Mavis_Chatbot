# Mavis Chatbot

Mavis Chatbot is a Flask-based application designed to act as a personal assistant. It integrates with various APIs, including the OpenAI's ChatGPT, Amazing Marvin's productivity app, AccuWeather, and Google Calendar, to offer a wide range of functionalities. The bot specializes in scheduling tasks, managing calendars, providing weather updates, and answering a variety of user inquiries, aiming to streamline productivity and planning.

## Features

- **Task Scheduling and Management**: Seamlessly integrates with Amazing Marvin's API to create, schedule, and manage tasks.
- **Weather Updates**: Fetches and provides weather updates by integrating with the AccuWeather API.
- **Calendar Management**: Manages and schedules events with Google Calendar integration.
- **Conversational AI**: Utilizes OpenAI's ChatGPT to maintain a natural and intuitive conversational flow, answering queries and performing tasks as requested.

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.8 or above
- Flask
- Requests library
- Dotenv for managing environment variables

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Sun-of-a-beach/Mavis_Chatbot.git
    cd mavis-chatbot
    ```

2. **Set up a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/macOS
    venv\Scripts\activate  # For Windows
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Rename the `.env_example` file to `.env` and update the variables with your respective API keys and tokens.

### Running the Application

1. **Start the Flask server:**

    ```bash
    python app.py
    ```

    The server should start, and you should see the output indicating that it's running on `http://127.0.0.1:9000/` or a similar local address.

## Usage

- Send POST requests to `http://127.0.0.1:9000/api` with a JSON payload containing the `message` and optionally the `conversation_id`.
- Use the `/conversations` endpoint to retrieve the history of conversations.

## Integrations

### Amazing Marvin

- **Task Management**: Add, schedule, and retrieve tasks.
- **Daily Schedule**: Get an overview of scheduled tasks and events for the day.
- `Amazing Marvin API` : Add task with title, date, time, duration, due date, review date.


### Google Calendar
- **Retrieve upcoming tasks**: Get upcoming tasks from the calendar. Keep your Amazing Marvin and Google calendar in a 2-way sync for better experience.
- `Google Calendar API` : Get scheduled tasks for the day, get upcoming tasks with a start date and end date.

### AccuWeather

- **Current Conditions**: Get the current weather conditions for a specified location.
- **Weather Forecasts**: Fetch weather forecasts for different time frames.
- `Accu Weather API` : Get weather updates of a place like temperature in Celsius, Realfeel temperature, Wind Speed in Kmh.
