.PHONY: test run-bot run-streamlit

# Run all unit tests
test:
	pytest tests/

# Run the Telegram bot
run-bot:
	PYTHONPATH=. python -m frontend.telegram_app

# Run Streamlit app
run-streamlit:
	PYTHONPATH=. streamlit run frontend.streamlit_app
