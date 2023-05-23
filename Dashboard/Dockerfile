FROM python:3.10
WORKDIR /app

#################################
# Install the Python dependencies
#################################
ADD requirements.txt ./
RUN pip install -r requirements.txt

########################################################
# Copy all the application files inside of the container
########################################################
COPY pages pages
COPY assets assets
COPY dash_app.py .
COPY data.py .
COPY swearWords.txt .

########################################################################################
# Allow statements and log messages to immediately appear in the Knative CloudWatch logs
########################################################################################
ENV PYTHONUNBUFFERED True

CMD ["python", "dash_app.py"]