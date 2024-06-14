FROM ubuntu:22.04

# AWS-cli install
RUN apt update -y
RUN apt install curl unzip python3 python3-pip python3.10-venv  -y
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install

COPY . /app
WORKDIR /app

RUN python3 -m venv venv
RUN . ./venv/bin/activate
RUN pip install -r requirements.txt

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]