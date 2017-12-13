FROM python:3.5.3

WORKDIR /app

ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8081

ENV NAME dev

CMD ["python", "whatflix.py"]