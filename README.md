# Nexia - Multilingual Healthcare Assistant

Nexia is a multilingual virtual assistant (Portuguese, Spanish, English) that helps users to:
- Discover available healthcare services
- Schedule medical appointments
- Modify or cancel existing appointments


## Features

- 📅 Schedule appointments with available professionals
- 🔄 Modify scheduled times
- 🗑️ Cancel appointments
- 📱 Multilingual chat interface (Portuguese by default)
- 🧠 Conversational memory for a better experience
- 📅 Google Calendar integration
- 🔄 Professional availability checking

## How the assistant works

Nexia is implemented as a ReAct agent (Reason + Act), which works as follows:

- 📥 Receives a user query as input
- 🤔 Reasons about the query and decides the appropriate action
- 🛠️ Executes the chosen action using available tools (e.g., calendar, list of services)
- 👀 Observes the result of the action
- 🔁 Repeats steps 2-4 until it can provide a suitable final answer to the user

## Requirements

- Python 3.8+
- OpenAI API Key
- Google Calendar API Credentials

## Installation

1. Clone the repository:
```bash
git clone [REPOSITORY_URL]
cd nexia
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit the .env file with your credentials
```

## Usage

### Via Web Interface (Streamlit)

1. Start the server:
```bash
make run-streamlit
```

2. Access the application in your browser:
```
http://localhost:8501
```

### Via Telegram Interface

1. Start the Telegram bot:
```bash
make run-bot
```

2. Interact with the bot on Telegram: @NexiaAIBot.

### Via Python API

The assistant can be integrated via API:
```python
from app.agent import agent

response = agent.chat("I want to schedule a psychology appointment")
print(response)
```

## Tests

To run unit tests:
```bash
make test
```

## Project Structure

```
nexia/
├── app/
│   ├── agent.py         # Main assistant logic
│   ├── calendar.py      # Google Calendar integration
│   ├── fallback.py      # Fallback and clarification logic
│   ├── memory.py        # Conversational memory management
│   ├── prompts.py       # Prompts and multilingual messages
│   ├── scheduler.py     # Scheduling management
│   └── services.py      # Service management
├── config/
│   └── services.yaml    # Services configuration
├── frontend/
│   ├── streamlit_app.py # Web interface with Streamlit
│   └── telegram_app.py  # Telegram interface with Aiogram
├── tests/
│   └── test_nexia.py    # Unit tests
├── requirements.txt      # Project dependencies
└── README.md            # Documentation
```

## Contribution

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for more details.