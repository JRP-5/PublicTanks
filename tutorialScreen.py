# This file contains a class which contains all the methods and attributes needed to create and render a tutorial screen
import pygame.image
import guiUtils
import mainMenuScreen
from screen import Screen


# This class can be instantiated to easily create a tutorial screen
class TutorialScreen(Screen):

    def __init__(self, screenWidth, screenHeight):
        super().__init__(screenWidth, screenHeight)  # Passing width and height to super constructor
        self.buttonW = 200
        self.buttonH = 70

        self.buttons = [
            guiUtils.Button((screenWidth / 2) - (self.buttonW / 2), (screenHeight * 0.9) - (self.buttonH / 2), self.buttonW, self.buttonH, self.mainMenuSwitch, "Main Menu"),
        ]
        self.shouldClose = False

        # Creates a new surface with our image on and stores it, it can then be "blitted" onto our main surface
        self.tutorialImageSurface = pygame.image.load("TutorialImage.png")
        imageScale = screenWidth/2560  # Finding the size of the window with respect to a 2k screen
        # Scale the image with respect to the screen's width
        self.tutorialImageSurface = pygame.transform.scale(self.tutorialImageSurface, (int(1800 * imageScale), int(859 * imageScale)))
        self.backgroundImageSurface = pygame.image.load("BackgroundImage.png")

        # Represents whether the user's keyboard input should be captured as they are typing in an input box (always false on this screen)
        self.captureKeyboard = False
        self.focusedInput = None  # Corresponds to the index in the buttons array of the focused input box (if any)

    def getButtons(self):
        return self.buttons

    def renderScreen(self, surface):
        surface.fill((255, 255, 255))  # Clears the surface by filling it with white

        # Renders the background image onto the surface
        surface.blit(self.backgroundImageSurface, ((self.width / 2) - (self.backgroundImageSurface.get_width() / 2), (self.height / 2) - (self.backgroundImageSurface.get_height() / 2)))
        # Renders the tutorial image onto the surface
        surface.blit(self.tutorialImageSurface, ((self.width / 2) - (self.tutorialImageSurface.get_width() / 2), (self.height / 2) - (self.tutorialImageSurface.get_height() / 2)))
        for i in range(len(self.buttons)):  # Cyclically renders all buttons in the class onto the surface
            self.buttons[i].renderButton(surface)

    # A functon which is called when the main menu button is pressed
    def mainMenuSwitch(self):
        # Create a new main menu screen with the parameters given to this object
        newScreen = mainMenuScreen.MainMenu(self.width, self.height)
        return newScreen  # Return the new screen so it can be set to current screen


