FROM python:3.11

WORKDIR /app
COPY *.py *.txt /app

RUN apt-get update && apt-get install -y ffmpeg \
    && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "server.py"]
