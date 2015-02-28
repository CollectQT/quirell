'''
(stuff about notes, and how they are similar to timelines)
'''

from quirell.webapp.timeline import timeline

class Notes (timeline):

    def __init__ (self, *args, **kwargs):
        super(Notes, self).__init__(*args, **kwargs)
