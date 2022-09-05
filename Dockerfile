FROM python:3.10

# Fastapi deployment
# https://fastapi.tiangolo.com/deployment/docker/

WORKDIR /code

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./aas ./aas
COPY *.py ./

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "5"]
CMD ["python", "./main.py"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
