# Database

!!! This is out of date as of updating to py2neo 2.X

## Architecture

nodes themselves are 'first class objects', users and posts are represented in
the database as nodes. Creating a new type of first class object is a lot of
work and should be avoided at all costs.

All data attached to nodes must be of format: attribute = 'string'. Data
attached to nodes in this way are second class objects. Nodes should always have
an attribute identifying their 'node_type', currently defined 'node_type's being
'user' and 'post'. 'user' 'node_type's need a userID, and 'post's 'node_type'
need 'content' and a 'creator'.

    node(node_type='user', userID='@cyrin')
    node(node_type='post', content='im a programmer omg!!!' creator='@cyrin')

In the above example second class objects are 'userID', 'content', 'creator'

Anything that isn't logically represented as a string, should be stored as a
python object of some sort and encoded as a json string. Data attached to nodes
this way are third class objects. Create as many third class objects as you
want, as they are easy to keep track of. Example:

    node(
        post_info={
            'display_name': 'lynn',
            'pronouns': 'she/her',
            'random': 'hi!!!!',
        }
    )

In the above example third class objects are 'display_name', 'pronouns', etc...
Also please note again that the contents of post_info are a json string, I'm
just not bothing to write the example as json.

The majority of the content for a node should be third class, for users that
would be user_info, for posts that would be post_info. Here are some example
nodes incorpating all of the above:

    node(
        node_type='user'
        userID='@cyrin'
        user_info=
        {
            'display_name': 'lynn',
            'pronouns': 'she/her',
            'description': 'computer femme!!!!'
        }
    )

    node(
        node_type='post'
        content='im a programmer :)'
        creator='@cyrin'
        post_info=
        {
            'tags'=['tech', 'me'],
            'visibility'='friends',
        }
    )

---

posts

top level:
    content
    visibility
    owner
    secondary:
        tags

    node(
        node_type='post'
        content='rawr'
        visibility=''
        creator='<node>'
        post_info
    )
