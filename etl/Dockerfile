FROM python:3.9.16

RUN mkdir wd
WORKDIR wd
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . ./


CMD [ "python", "scraper.py"]