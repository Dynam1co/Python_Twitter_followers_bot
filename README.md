# Python Twitter followers Bot

Using Python, the program analyzes a Twitter user's followers and stores information about followers gained or lost.

It sends via Telegram a summary of the followers gained and lost during the day.



## How it works

By means of two Dockerfiles and a docker-compose two containers are raised, one with the Python script and the other with a PostgreSQL database.

Port 5432 is also mapped to have access to the tables from a local client.

In order not to lose the data when the containers are deleted, it is necessary to create a volume. How to do this is explained in the **Use** section.



## Setup

It is necessary to create a configuration file to parameterize the fields related to Postgres, Telegram and Twitter.

The file will be called **config.py** and will go inside the **app** folder.

It will have the following structure:

```python
# Telegram
TELEGRAM_TOKEN = "AAAAAAA1234567890"
TELEGRAM_GROUP_ID = -44444444

# Database
POSTGRE_PORT = "5432"
POSTGRE_USER = "fjasensi"
POSTGRE_HOST = "db"
POSTGRE_PASS = "cgFxx6sRa8Yge3T"
POSTGRE_DATABASE = "Atlas"

# Twitter
CONSUMER_KEY = 'your_consumer_key'
CONSUMER_SECRET = 'your_consumer_secret'
ACCESS_KEY = 'your_access_key'
ACCESS_SECRET = 'your_access_secret'
TWITTER_USER = 'your_twitter_user'
```



## Database

Inside the **database** folder there is a file named **create_fixtures.sql**. This file contains an sql script to generate the necessary data structure. It will be executed automatically when docker-compose is launched.



## Use

Create volume:
```bash
$ docker volume create --name=postgresql-volume
```

Using docker:
```bash
docker-compose up --build
```

Stop containers:

```bash
docker-compose down
```

Docker volumes path:

```
\\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes
```



## TODOS

- Allow to receive the summary through a Telegram bot command.
- Generate weekly profit/loss report