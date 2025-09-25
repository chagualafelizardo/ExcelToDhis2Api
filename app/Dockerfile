FROM python:3.11-slim

WORKDIR /app

# Copia o requirements.txt direto (sem app/)
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do app
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
