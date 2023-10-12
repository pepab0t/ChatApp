FROM python:3.10-alpine

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir eventlet gunicorn

COPY . .

EXPOSE 8000

# CMD ["python3", "main.py"]
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:8000", "main:app"]