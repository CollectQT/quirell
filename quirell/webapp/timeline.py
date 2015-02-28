'''
The timeline class
------------------
a timeline is a subclass of lists, used to store
a list of user posts in a timeline format. In the most basic
implementation it is a list of post nodes.

About timeline creation
-----------------------
timeline creation is modeled after the idea that whenever a post
is created that would belong on a user's timeline, that post is
then pushed to all applicable `timeline`s. Also whenever
there is a relationship state change.

Structure
---------
timeline
    [
        post_node,
            .properties['datetime']
        post_node,
        post_node,
        ...,
    ]
accesing:
    (:user)-[READS]->(:timeline)
'''

class Timeline (list):

    max_entries = 300

    def __init__ (self, content=[], *args, **kwargs):
        import json
        if type(content) == str: content = json.loads(content)
        super(Timeline, self).__init__(content, *args, **kwargs)

    def replace_id (self, post_id, node):
        '''for when a node has been edited'''
        for index, node in enumerate(self):
            if node.properties['post_id'] == post_id: self[index] = node

    def clean (self):
        '''sort it and clip it'''
        self.sort(key=lambda node: node.properties['datetime'], reverse=True)
        self = self[:self.max_entries]

    def refresh (self):
        del self[:]
        '''
        the cypher query looks something like :

        MATCH (:user {username:\"{username}\"})-[FOLLOWING]->(:user)-[CREATED]->(n:post)
        RETURN n ORDER BY n.datetime desc LIMIT {limit}
        '''
