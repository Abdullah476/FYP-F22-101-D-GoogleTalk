FROM python:3.9.16

WORKDIR /

COPY . .

RUN make install

EXPOSE 8086

CMD ["python", "server/server.py"]
