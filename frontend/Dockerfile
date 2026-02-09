FROM python:3.10

WORKDIR /app

COPY ./ /app

RUN pip install -r requirements.txt

EXPOSE 1300

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "1300", "--reload"]
