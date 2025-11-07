FROM python:3.12

WORKDIR /app/tgi-bot

COPY ./tgi-bot/requirements.txt /app/tgi-bot
RUN pip install --no-cache-dir -r requirements.txt

COPY ./tgi-bot /app/tgi-bot
COPY ./api /app/api

WORKDIR /app/tgi-bot/core/tgi_clients
RUN python generate_api_clients.py

WORKDIR /app/tgi-bot
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
