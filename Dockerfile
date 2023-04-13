FROM python:3.9.16

WORKDIR /

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8086

CMD ["python", "server/server.py"]
