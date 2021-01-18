import urllib.parse
import psycopg2
import os

env = os.environ.get('ENVIRONMENT', 'local')
if (env == 'local'):
    from meetupbot_data import database_url
    url = urllib.parse.urlparse(database_url)
else:
    url = urllib.parse.urlparse(os.environ["HEROKU_POSTGRESQL_RED_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port)
