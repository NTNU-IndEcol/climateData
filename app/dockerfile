FROM python:slim-bullseye
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["gunicorn", "--workers", "5", "--threads", "1", "--bind", "0.0.0.0:5000", "--timeout", "90", "app:app"]
