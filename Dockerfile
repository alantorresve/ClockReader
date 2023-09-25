FROM python:3.11-slim
RUN apt-get update -qq && apt-get upgrade -y
RUN apt-get install build-essential -y
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN python3 -m pip install --upgrade pip
ENV APP_HOME /app
WORKDIR $APP_HOME

# Production dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Proyect
COPY . .

CMD [ "python" ]
