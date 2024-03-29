FROM python:3.11.7-bookworm
RUN apt-get update && apt-get install python3-tk tk-dev -y
COPY ./requirements.txt /usr/local/src/myscripts/requirements.txt
WORKDIR /usr/local/src/myscripts
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./code /usr/local/src/myscripts/code
WORKDIR /usr/local/src/myscripts/code
ENV PYTHONPATH "${PYTHONPATH}:/usr/local/src/myscripts"
EXPOSE 80
CMD ["streamlit", "run", "Home.py", "--server.port", "80", "--server.enableXsrfProtection", "false"]