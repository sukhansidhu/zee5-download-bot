FROM python:3.10-slim

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the token via environment variable
ENV BOT_TOKEN=replace-with-default-or-set-in-koyeb

CMD ["python", "zee5_bot.py"]
