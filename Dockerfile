FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# Pasta para os arquivos enviados
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "app.py"]
