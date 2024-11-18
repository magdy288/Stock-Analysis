FROM python:3.12-slim

EXPOSE 8009



COPY app.py requirements.txt


WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/apt/lists/*


RUN pip install -upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "streamlit", "app.py", "--server.port=8009", "--server.address=0.0.0.0" ]
