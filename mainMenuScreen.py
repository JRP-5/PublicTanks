# This file contains a class which contains all the methods and attributes needed to create a main menu screen
import pygame
import guiUtils
import tutorialScreen
import createGameScreen
from screen import Screen


# This class can be instantiated to easily create a main menu screen
class MainMenu(Screen):

    def __init__(self, screenWidth, screenHeight):
        super().__init__(screenWidth, screenHeight)  # Passing width and height to super constructor
        self.buttonW = 200  # Setting the button's width and height
        self.buttonH = 70

        self.buttons = [
            # Creating a button which runs the tutorialScreenSwitch function on press with the label "Tutorial" aligned to the left third of the screen
            guiUtils.Button((screenWidth / 3) - (self.buttonW / 2), (screenHeight / 2) - (self.buttonH / 2), self.buttonW, self.buttonH, self.tutorialScreenSwitch, "Tutorial"),

            # Creating a button which runs the createScreenSwitch function on press with the label "Create Game" aligned to the left third of the screen
            guiUtils.Button((2 * screenWidth / 3) - (self.buttonW / 2), (screenHeight / 2) - (self.buttonH / 2), self.buttonW, self.buttonH, self.createScreenSwitch, "Create Game")
        ]
        self.shouldClose = False

        # Creates a new surface with our image on and stores it, it can then be "blitted" onto our main surface
        self.imageSurface = pygame.image.load("BackgroundImage.png")

        # Represents whether the user's keyboard input should be captured as they are typing in an input box (always false on this screen)
        self.captureKeyboard = False
        self.focusedInput = None  # Corresponds to the index in the buttons array of the focused input box (if any)
        # this may have a value even if nothing is focused, capture keyboard is used as an indicator

    def getButtons(self):  # Getter to allow the buttons to be checked if they are pressed
        return self.buttons

    def renderScreen(self, surface):
        surface.fill((255, 255, 255))  # Clears the surface by filling it with white

        # Renders the background image onto the surface
        surface.blit(self.imageSurface, ((self.width / 2) - (self.imageSurface.get_width() / 2), (self.height / 2) - (self.imageSurface.get_height() / 2)))

        for i in range(len(self.buttons)):  # Cycles through every button and renders them
            self.buttons[i].renderButton(surface)

    # A functon which is called when the tutorial button is pressed
    def tutorialScreenSwitch(self):
        # Create a new tutorial screen with the parameters given to this object
        newScreen = tutorialScreen.TutorialScreen(self.width, self.height)
        return newScreen  # Return the new screen so it can be set to current screen

    # Function which is called when the create game button is pressed
    def createScreenSwitch(self):
        # Create a new create game screen with the parameters given to this object
        newScreen = createGameScreen.CreateGameScreen(self.width, self.height)
        return newScreen



