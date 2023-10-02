FROM python:3.10-alpine

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000

CMD ["python3", "main.py"]