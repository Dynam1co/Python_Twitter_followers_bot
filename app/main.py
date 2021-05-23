from sqlalchemy import create_engine
import conf_management as conf
from datetime import date, datetime
import time
import tweepy
from telegram.ext import Updater


# Connecto to the database
db_string = conf.get_connection_string()
db = create_engine(db_string)

# Twiter setup
CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET = conf.get_twitter_data()


def add_new_row(follower_name, number, follower_screen_name, follower_id):
    # Insert a new rew into the 'followers_history' table.
    follower_name = follower_name.replace("'", '')
    follower_name = follower_name.replace("%", '')
    follower_screen_name = follower_screen_name.replace("'", '')
    follower_screen_name = follower_screen_name.replace("%", '')

    query = "INSERT INTO followers_history (insert_date,follower_name,number,follower_screen_name,follower_id) "+\
        "VALUES ("+\
        "'" + str(date.today()) + "'," +\
        "'" + follower_name + "'," +\
        str(number) + "," + \
        "'" + follower_screen_name + "'," + \
        "'" + str(follower_id) + "'" + \
        ");"

    try:
        db.execute(query)
    except TypeError:
        print('ERROR\n')
        print(query)
        send_telegram(f'Twitter Bot Followers: Insert Error\n\n{query}')
    except:
        print('ERROR\n')
        print(query)
        send_telegram(f'Twitter Bot Followers: Insert Error\n\n{query}')


def add_to_lost_gained(insert_date, follower_name, follower_screen_name, follower_id, lost):
    # Depends on "lost" param add a record in different tables to resume of the day.
    tablename = 'followers_gained'

    if lost:
        tablename = 'followers_lost'

    query = f"INSERT INTO {tablename} (insert_date, follower_id, follower_name, follower_screen_name) VALUES ('{str(insert_date)}', '{follower_id}', '{follower_name}', '{follower_screen_name}'); "

    try:
        db.execute(query)
    except TypeError:
        print('ERROR\n')
        print(query)
        send_telegram(f'Twitter Bot Followers: Insert Error\n\n{query}')
    except:
        print('ERROR\n')
        print(query)
        send_telegram(f'Twitter Bot Followers: Insert Error\n\n{query}')


def get_last_row():
    # Retrieve the last number inserted in a date inside the 'followers_history'
    query = "" + \
            "SELECT number " + \
            "FROM followers_history " + \
            "WHERE number >= (SELECT max(number) FROM followers_history)" + \
            " LIMIT 1"

    result_set = db.execute(query)
    for (r) in result_set:
        return r[0]

    return 0


def get_follower_data(follower_id):
    # Get data from unique follower.
    query = f"SELECT follower_name, follower_screen_name, follower_id FROM followers_history WHERE follower_id = '{follower_id}' LIMIT 1"

    try:
        result_set = db.execute(query)
    except:
        print('ERROR\n')
        print(query)
        return "", "", ""

    for (r) in result_set:
        return r[0], r[1], r[2]


def get_data(insert_date, number):
    # Retrieve data with specific insert_date and number
    query = "" + \
            "SELECT follower_id " + \
            "FROM followers_history " + \
            "WHERE number = " + str(number) + " and insert_date = '" + str(insert_date) + "'"

    result_set = db.execute(query)

    return result_set


def follower_exists(follower_id, insert_date, number):
    query = f"SELECT COUNT(*) FROM followers_history WHERE follower_id = '{follower_id}' AND insert_date = '{insert_date}' AND number = {number}"

    result_set = db.execute(query)

    for (r) in result_set:
        if r[0] > 0:
            return True

    return False


def get_followers(user):
    # Get followers from Twitter API.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    fws = []
    ids = []

    try:
        for fid in tweepy.Cursor(api.followers_ids, screen_name=user, count=5000).items():
            ids.append(fid)
    except:
        import traceback
        traceback.print_exc()

    for i in range(0, len(ids), 100):
        try:
            chunk = ids[i:i + 100]
            fws.extend(api.lookup_users(user_ids=chunk))
        except:
            import traceback
            traceback.print_exc()
            print('Something went wrong, skipping...')

    return fws


def insert_followers(number, followers):
    # Insert followers in history table.
    for profile_data in followers:
        add_new_row(profile_data._json['name'], number, profile_data._json['screen_name'], profile_data._json['id'])


def compare_followers(old_number, new_number, insert_date):
    # Compare new folowers agains old followers. Insert gained and lost in different tables.
    old_followers = get_data(insert_date, old_number)
    new_followers = get_data(insert_date, new_number)

    for row in old_followers:
        old_id = row[0]

        if not follower_exists(old_id, insert_date, new_number):
            print(f"Follower lost: {old_id}")
            follower_name, follower_screen_name, follower_id = get_follower_data(old_id)
            add_to_lost_gained(date.today(), follower_name, follower_screen_name, follower_id, True)

    for new_row in new_followers:
        new_id = new_row[0]

        if not follower_exists(new_id, insert_date, old_number):
            print(f"New follower: {new_id}")
            follower_name, follower_screen_name, follower_id = get_follower_data(new_id)
            add_to_lost_gained(date.today(), follower_name, follower_screen_name, follower_id, False)


def send_telegram(texto_enviar):
    # Send text to telegram
    update = Updater(token=conf.get_telegram_token())
    update.bot.send_message(chat_id=conf.get_telegram_group_id(), text=texto_enviar)


def notificate_telegram_followers():
    # Send to telegram resume for today
    gained_followers = 0
    lost_followers = 0

    query = f"SELECT count(*) FROM followers_gained WHERE insert_date = '{date.today()}'"

    try:
        result_set = db.execute(query)
    except:
        print('ERROR\n')
        print(query)
        return "", "", ""

    for (r) in result_set:
        gained_followers = r[0]

    query = f"SELECT count(*) FROM followers_lost WHERE insert_date = '{date.today()}'"

    try:
        result_set = db.execute(query)
    except:
        print('ERROR\n')
        print(query)
        return "", "", ""

    for (r) in result_set:
        lost_followers = r[0]

    telegram_message = f'Twitter followers bot\n\nToday:\n  - Followers gained: {gained_followers}\n  - Followers lost: {lost_followers}'
    send_telegram(telegram_message)


if __name__ == '__main__':
    print('Application started')

    while True:
        print(f'Executing job {datetime.today()}')

        send_telegram(f'Twitter Bot Followers: Executing job {datetime.today()}')

        last_value = get_last_row()
        next_value = last_value + 1

        fws = get_followers(conf.get_twitter_user())
        insert_followers(next_value, fws)

        if last_value != 0:
            compare_followers(last_value, next_value, date.today())
            notificate_telegram_followers()

        print(f'Job finished {datetime.today()}')
        send_telegram(f'Twitter Bot Followers: Job finished {datetime.today()}')

        time.sleep(21600)  # 5 hours
