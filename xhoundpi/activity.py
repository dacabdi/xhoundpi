""" Activity tracing context module """

import uuid

class Activity:
    """ Represents the activity context of a dataflow operation """
    activity_id_zero = uuid.UUID('00000000-0000-0000-0000-000000000000')

    def __init__(self,
    activity_id: uuid.UUID=uuid.uuid4(),
    related_activity_id: uuid.UUID=activity_id_zero):
        self.related_activity_id = related_activity_id
        self.activity_id = activity_id

    def next(self):
        """ Create child activity """
        return Activity(
            activity_id=uuid.uuid4(),
            related_activity_id=self.activity_id)

    def __enter__(self):
        return self.next()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return exc_type is not None
