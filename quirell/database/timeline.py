'''
The timeline class
------------------

Is used to reformat a recordlist into something we actually want
to deal with.

The access chain is

    list dict dict X

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

    def __init__ (self, recordlist):
        content = [{'post':post, 'user':user} for user, post in recordlist]
        super().__init__(content)
