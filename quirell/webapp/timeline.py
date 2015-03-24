'''
The timeline class
------------------

A timeline is a read only list, where each item contains a post_node,
and the user_node of the user that made the post. It takes in a
parallel list of post nodes and user nodes, so really all this class
does is zip those lists and stick them in a dictionary.

Structure
---------

The access chain is

    timeline list dict dict X

Where X can be anything that neo4j can store. The structure can
also be represented like this

[
    {
        'post': post_node
            ['content'] = X
            ['datetime'] = X
        'user': user_node
            ['username']
            ['profile_picture']
    },
    {'post'..., 'user'...,}
    {},
    {},
    ...
]

Example Uses
------------

# python
for line in timeline:
    line['post']['content']
    line['user']['username']

# html
{% for line in timeline %}
    <div>{{ line.user.username }}</div>
    <div>{{ line.post.content }}</div>
{% endfor %}
'''

class Timeline (list):

    def __init__ (self, users, posts=[], *args, **kwargs):
        self._content = [
            {'post':post, 'user':user}
            for user, post in zip(users, posts)]

    def __getitem__ (self, key):
        return self.content[key]
