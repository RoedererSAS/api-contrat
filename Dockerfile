# 
FROM python:3.10

# Set the working directory
WORKDIR /app

COPY requirements.txt .

COPY /app .

RUN apt-get update && apt-get install -y gcc
RUN apt-get install libodbc2
RUN apt -y install unixodbc


RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get -y update; apt-get -y install curl

# RUN curl -O https://download.microsoft.com/download/fae28b9a-d880-42fd-9b98-d779f0fdd77f/msodbcsql18_18.5.1.1-1_amd64.apk
# RUN curl -O https://download.microsoft.com/download/7/6/d/76de322a-d860-4894-9945-f0cc5d6a45f8/mssql-tools18_18.4.1.1-1_amd64.apk
RUN curl https://public.dhe.ibm.com/software/ibmi/products/odbc/debs/dists/1.1.0/ibmi-acs-1.1.0.list | tee /etc/apt/sources.list.d/ibmi-acs-1.1.0.list

RUN apt-get update
RUN apt install ibm-iaccess -y

WORKDIR /

CMD ["fastapi", "run", "app/main.py", "--port", "8000"]