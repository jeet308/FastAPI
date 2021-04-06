FROM python:3.8.8

RUN pip3 install --upgrade pip

COPY . ./marshmallow
WORKDIR ./marshmallow

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["daphne", "main:app" ,"-b", "0.0.0.0", "-p", "8000" ]
