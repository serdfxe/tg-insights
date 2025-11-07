FROM python:3.12

WORKDIR /app/frontend/tgi-bot

COPY ./frontend/tgi-bot/requirements.txt /app/frontend/tgi-bot
RUN pip install --no-cache-dir -r requirements.txt

COPY ./frontend/tgi-bot /app/frontend/tgi-bot
COPY ./api /app/api

WORKDIR /app/frontend/tgi-bot/core/tgi_clients
RUN python generate_api_clients.py

WORKDIR /app/frontend/tgi-bot
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
