FROM python:3.9.16

WORKDIR /

COPY ./server ./server

COPY ./extension ./extension

COPY ./model-last ./server/ner_model/model-last

RUN mkdir ./server/speech_model

RUN make install

EXPOSE 8086

CMD ["python", "server/server.py"]
