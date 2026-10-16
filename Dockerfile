FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 BRIDGE_STATE_DIR=/persist
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 liblapack3 libopenmpi3 && rm -rf /var/lib/apt/lists/*
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-hosted.txt && python -c "import openseespy.opensees as ops; print('OpenSees', ops.version())"
COPY . .
CMD ["python", "hosted.py"]
