FROM python:3.8.8

RUN mkdir frslabs
RUN pip3 install --upgrade pip
RUN python3 -m venv env

COPY ./app ./
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["daphne", "main:app" ,"-b", "0.0.0.0", "-p", "8000" ]
