FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app/Actividad_Extra_Django/retos_django
COPY Actividad_Extra_Django/retos_django/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY Actividad_Extra_Django/retos_django .
COPY laboratorio /app/laboratorio
COPY proyectos/dataset-medios /app/proyectos/dataset-medios
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
