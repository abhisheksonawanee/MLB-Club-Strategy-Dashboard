setup:
	python -m pip install -r requirements.txt

pipeline:
	python -m src.pipeline

app:
	streamlit run app/app.py

test:
	pytest -q
