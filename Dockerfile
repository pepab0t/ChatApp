FROM python:3.10-alpine

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir eventlet
COPY . .

EXPOSE 8000

CMD ["python3", "main.py"]