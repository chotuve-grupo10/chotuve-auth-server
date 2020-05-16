FROM python:3
COPY requirements.txt .
COPY setup.py .
RUN apt-get update && apt-get install -y python3-pip python3-dev
RUN pip install --upgrade pip
RUN pip install -e .
EXPOSE 8000
COPY . .
CMD gunicorn --log-level=debug 'auth_server:create_app()'