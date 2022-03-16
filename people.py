class People(object):
    """docstring for People."""

    def __init__(self, username, pin):
        super(People, self).__init__()
        self.username = username
        self.pin = pin

    def auth(self, pin):
        if self.pin == pin:
            return True

        return False
