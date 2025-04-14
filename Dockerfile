<<<<<<< HEAD
# 
FROM python:3.10

# Set the working directory
WORKDIR /app

COPY requirements.txt .

COPY /app .

# Install pip requirements
RUN apt-get update && apt-get install -y gcc
RUN apt-get install libodbc2
RUN apt -y install unixodbc


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get -y update; apt-get -y install curl

RUN curl https://public.dhe.ibm.com/software/ibmi/products/odbc/debs/dists/1.1.0/ibmi-acs-1.1.0.list | tee /etc/apt/sources.list.d/ibmi-acs-1.1.0.list

RUN apt-get update
RUN apt install ibm-iaccess -y

WORKDIR /

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
