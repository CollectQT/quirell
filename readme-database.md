# Database

## Architecture

nodes themselves are first class objects, users and posts are represented in the database as nodes. Creating a new type of first class object is a lot of work and should be avoided at all costs.

All data attached to nodes must be of format `attribute = "string"`. Data to nodes in this way are second class objects. If the graph database itself needs to be aware of a value, then it should be a second class object. But second class objects should be kept sparse, because of their ability to clash with the contents of the `quirell.webapp.user.User` class. Nodes should always have an attribute identifying their `node\_type`, currently defined node\_types being `user` and `post`.

    node(
        node_type='user',
        username='@cyrin',
    )
    node(
        node_type='post',
        content='im a programmer omg!!!',
        creator='@cyrin',
    )

In the above example second class objects are `username`, `content`, `creator`

Anything that isn't logically represented as a string, should be stored as a python object of some sort and encoded as a json string. Data attached to nodes this way are third class objects. Create as many third class objects as you want, as they are easy to keep track of. Example:

    node(
        post_info={
            'display_name': 'lynn',
            'pronouns': 'she/her',
            'random': 'hi!!!!',
        }
    )

In the above example third class objects are `display\_name`, `pronouns`, etc...

The majority of the content for a node should be third class, and stored on a `data` variable. Here are some example nodes incorpating all of the above, in addition to all documented user data attributes (they become documented by adding them here!)

    node(
        node_type = 'user'
        username = '@cyrin'
        password = 'seekrit'
        data =
        {
            'email': 'rawr@rawr.rawr'
            'display_name': 'lynn',
            'pronouns': 'she/her',
            'description': 'computer femme!!!!',
            'profile_picture': 'rawr_catten.jpg'
            'pictures': {
                'amount': 2,
                0:
                    {
                        'date': <date_time_object>,
                        'visibility': 'friends',
                        'url': 'http://picture.url'
                    }
                1:
                    {
                        'date': <date_time_object>,
                        'visibility': 'friends',
                        'url': 'http://picture.url'
                    }
            }
        }
    )

    node(
        node_type = 'post'
        content = 'im a programmer :)'
        creator = <user_node>
        data =
        {
            'tags': ['tech', 'me'],
        }
    )
