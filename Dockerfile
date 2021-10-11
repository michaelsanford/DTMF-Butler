FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK --interval=5s --timeout=1s --start-period=5s \
    CMD test -f /tmp/HEALTH_OK || exit 1

CMD [ "python", "./butler.py" ]