import json
import requests
import multiprocessing
#
from quirell.config import *
from quirell.webapp import runserver
from quirell.database import Database

def update_all_posts (db):
    LOG.info('Altering all posts')
    recordlist = db.db.cypher.execute('MATCH (post:post) RETURN post')
    all_posts = [record['post'] for record in recordlist]
    for post in all_posts:
        post.push()

def update_all_users (db):
    from quirell.webapp.models import Relationships
    LOG.info('Altering all users')
    recordlist = db.db.cypher.execute('MATCH (user:user) RETURN user')
    all_users = [record['user'] for record in recordlist]
    for user in all_users:
        # LOG.info('Before:\n{}'.format(user))
        # user['relationships'] = json.dumps(Relationships.defaults)
        # LOG.info('After:\n{}\n'.format(user))
        user.push()


if __name__ == "__main__":
    db = Database()
    web_server = multiprocessing.Process(target=runserver.run).start()
    # update_all_users(db)
    requests.post('http://0.0.0.0:{}/shutdown'.format(CONFIG['PORT']))
    LOG.info('Migration Complete')
