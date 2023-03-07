import screen


# Super class to both game screens
class GameScreen(screen.Screen):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.font = None  # Variables required for the winning text
        self.textSurface = None
        self.winnerTicks = 0  # Tracks how long the winner text has been displayed for
        self.textDest = []  # An array of length 2 which stores the location of the text

    def getButtons(self):  # If get buttons is called on a screen which implements no buttons return an empty array
        return []

    def processShooting(self, projectile):
        pass
