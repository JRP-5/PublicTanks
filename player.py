import uuid


class Player:
    def __init__(self, name, team, Ai=False, ip=None):
        self.Ai = Ai
        self.name = name
        self.team = team
        self.ip = ip
        self.uuid = uuid.uuid4().hex
