FROM python:3.11.4-slim-bookworm

RUN mkdir /app

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]