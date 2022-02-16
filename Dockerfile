FROM python:3.7-buster

ARG PIP_USERNAME
ARG PIP_PASSWORD

WORKDIR /usr/src/app

ENV TZ=America/Toronto

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && apt-get update && \
apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev vim-tiny less && \
ln -s /usr/bin/vim.tiny /usr/bin/vim && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir poetry==1.1.12
RUN poetry config virtualenvs.create false && poetry config http-basic.pilot ${PIP_USERNAME} ${PIP_PASSWORD}
RUN poetry install --no-dev --no-root --no-interaction

RUN chmod +x gunicorn_starter.sh

CMD ["./gunicorn_starter.sh"]
