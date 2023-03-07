class Screen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.captureKeyboard = False
        self.shouldClose = False
        
    def getButtons(self):  # If get buttons is called on a screen which implements no buttons return an empty array
        return []
