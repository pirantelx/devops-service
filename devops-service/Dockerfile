FROM python:3.13

COPY ./ /opt/app/
WORKDIR /opt/app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

EXPOSE 8000

COPY . .

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/opt/app/entrypoint.sh"]