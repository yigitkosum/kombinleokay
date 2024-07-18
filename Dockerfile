FROM python:3.12
EXPOSE 5000
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt 

ENV DATABASE_URL=postgresql://postgres:12345@db:5432/databasekom

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--reload"]
