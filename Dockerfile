FROM python:3.8.14 as base

FROM base as installer
RUN apt-get update && apt-get install --assume-yes postgresql-client libffi-dev postgresql-server-dev-all gcc python3-dev musl-dev make redis tzdata xvfb wget gfortran libjpeg-dev zlib1g-dev fontconfig fonts-dejavu
RUN pip install setuptools pep517
RUN apt-get install -y xvfb
RUN apt-get install -y openssl build-essential libfontconfig
ENV XDG_RUNTIME_DIR=/tmp
ENV TZ Europe/London

FROM installer as main-app

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY entrypoint.sh .
COPY . .
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
