# AstroBaba: the whole app (API + web) in one container.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
# pyswisseph builds from source; newer setuptools breaks that build
RUN pip install --no-cache-dir "setuptools<70" wheel \
 && pip install --no-cache-dir --no-build-isolation pyswisseph \
 && pip install --no-cache-dir fastapi "uvicorn[standard]" tzdata
COPY . .
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
