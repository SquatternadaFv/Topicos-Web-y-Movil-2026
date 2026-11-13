FROM python:3.12-slim
WORKDIR /app
COPY microservicios-entregas/recomendar/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY laboratorio ./laboratorio
COPY proyectos/dataset-medios ./proyectos/dataset-medios
COPY microservicios-entregas/recomendar/app.py ./microservicios-entregas/recomendar/app.py
ENV PYTHONPATH=/app
WORKDIR /app/microservicios-entregas/recomendar
EXPOSE 8002
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8002", "--workers", "1", "--threads", "2", "--preload"]
