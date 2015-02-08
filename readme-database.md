# Database

!!! This is out of date as of updating to py2neo 2.X

## Architecture

nodes themselves are 'first class objects', users and posts are represented in the database as nodes. Creating a new type of first class object is a lot of work and should be avoided at all costs.

All data attached to nodes must be of format: attribute = 'string'. Data attached to nodes in this way are second class objects. If the graph database itself needs to be aware of a value, then it should be a second class object. But second class objects should be kept sparse, because of their ability to clash with the contents of the `quirell.webapp.user.User` class. Nodes should always have an attribute identifying their 'node_type', currently defined 'node_type's being 'user' and 'post'.

    node(
        node_type='user',
        userID='@cyrin',
    )
    node(
        node_type='post',
        content='im a programmer omg!!!',
        creator='@cyrin',
    )

In the above example second class objects are 'userID', 'content', 'creator'

Anything that isn't logically represented as a string, should be stored as a python object of some sort and encoded as a json string. Data attached to nodes this way are third class objects. Create as many third class objects as you want, as they are easy to keep track of. Example:

    node(
        post_info={
            'display_name': 'lynn',
            'pronouns': 'she/her',
            'random': 'hi!!!!',
        }
    )

In the above example third class objects are 'display_name', 'pronouns', etc... Also please note again that the contents of post_info are a json string, I'm just not bothing to write the example as json.

The majority of the content for a node should be third class, and stored on a `data` variable. Here are some example nodes incorpating all of the above:

    node(
        node_type = 'user'
        userID = '@cyrin'
        password = 'seekrit'
        data =
        {
            'display_name': 'lynn',
            'pronouns': 'she/her',
            'description': 'computer femme!!!!',
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

The previous example will also be used as the primary reference for what level any particular piece of data should reside on
