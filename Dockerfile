FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

COPY .env .

RUN pip install -r requirements.txt

COPY . .

CMD ["./startup.sh"]