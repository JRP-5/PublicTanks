import uuid


class Entity:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.uuid = uuid.uuid4().hex  # Get hexadecimal string part of the uuid (Universally unique identifier)
