'''
(stuff about notes, and how they are similar to timelines)
'''

from quirell.webapp.timeline import timeline

class notes (timeline):

    def __init__ (self, *args, **kwargs):
        super(notes, self).__init__(*args, **kwargs)
