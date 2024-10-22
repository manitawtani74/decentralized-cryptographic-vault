###########
# BUILDER #
###########

# pull official base image
FROM python:3.9-slim as builder

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-psycopg2 apache2 apache2-dev

RUN pip install --upgrade pip

# install python dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels mod_wsgi newrelic
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.9-slim

# install psycopg2 dependencies
RUN apt update -y && apt-get install -y python3-psycopg2 apache2 build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

ENV user app

# create directory for the app user
RUN mkdir -p /home/${user}

RUN addgroup --system ${user} && adduser --system --group ${user}

# create the appropriate directories
ENV HOME=/home/${user}
ENV APP_HOME=/code
RUN mkdir $APP_HOME
WORKDIR $APP_HOME
ENV PATH="/home/${user}/.local/bin:${PATH}"

# Debug mode
ENV DEBUG=True

# install dependencies
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*
RUN pip install psycopg2

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R ${user}:${user} $APP_HOME

# change to the app user
USER ${user}

EXPOSE 8080

RUN ["chmod", "+x", "./start.sh"]

CMD ["sh", "-c", "./start.sh"]