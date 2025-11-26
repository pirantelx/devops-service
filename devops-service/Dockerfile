FROM python:3.13

COPY ./ /opt/app/
WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  apt-get update \
     && apt-get install -y --no-install-recommends \
        gcc libpq-dev \
     && rm -rf /var/lib/apt/lists/* \
     && pip install --upgrade pip \
     && pip install -r requirements.txt

EXPOSE 8000

COPY . .

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/opt/app/entrypoint.sh"]