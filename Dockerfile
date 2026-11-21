FROM python:3.13-slim
WORKDIR /bot
COPY bot.py mechfight.py ./
ENV PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["python3", "-u", "/bot/bot.py"]
