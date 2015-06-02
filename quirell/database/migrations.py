from quirell.database import Database

def update_all_posts (db):
    recordlist = db.db.cypher.execute('MATCH (post:post) RETURN post')
    all_posts = [record['post'] for record in recordlist]
    for post in all_posts:
        continue

def update_all_users (db):
    import json
    from quirell.webapp.models import Relationships
    recordlist = db.db.cypher.execute('MATCH (user:user) RETURN user')
    all_users = [record['user'] for record in recordlist]
    for user in all_users:
        print('Before:\n{}\n\n'.format(user))
        user['relationships'] = json.dumps(Relationships.defaults)
        print('After:\n{}\n\n'.format(user))
    db.db.push()

if __name__ == "__main__":
    db = Database()
    db.update_all_users(db)
