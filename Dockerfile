FROM python:3.8.3
COPY requirements.txt .
COPY setup.py .
RUN apt-get update && apt-get install -y python3-pip python3-dev
RUN pip install --upgrade pip
RUN pip install -e .
RUN pip install -r requirements.txt
ENV DATABASE_URL="postgres://mnigwkzorbukjg:f8d628d71867b3206dfcfa0bfd889844a5bacaf871dcafc5c72a4bd43ff16786@ec2-3-91-139-25.compute-1.amazonaws.com:5432/ddelbso61aigs8"
ENV APP_SERVER_URL="https://chotuve-app-server-dev.herokuapp.com"
EXPOSE 8000
COPY . .
CMD gunicorn --log-level=debug 'auth_server:create_app()'