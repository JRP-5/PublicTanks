# This file contains useful classes and methods for rendering and the user's screen
import pygame
import ipaddress
import ctypes


# This class represents buttons on the user's screen, pygame does not provide any button facilities directly
# As outlined in the design section we must create our own methods which I have encapsulated within this class
class Button:

    # Constructor which initialises all our attributes from the arguments
    def __init__(self, x, y, width, height, action, text, font=None):
        # Taking the arguments and assigning them to attributes of the class
        self.x = x  # Represents x co-ordinate of top left pixel of button
        self.y = y  # Represents y co-ordinate of top left pixel of button
        self.width = width  # Represents the width in pixels of the button
        self.height = height  # Represents the height in pixels of the button

        # Creating a pygame Rect object with our arguments so that we can easily draw the button
        self.rect = pygame.Rect(x, y, width, height)
        self.innerRect = pygame.Rect(x + 1, y + 1, width - 2, height - 2)  # A smaller rectangle to give the button a border

        self.text = text  # This represents the text that should render on top of the button
        ctypes.windll.user32.SetProcessDPIAware()
        screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
        self.textSize = int(screenWidth * 0.0117)  # Setting the font size dependent on the screen size
        # Creating a font object so we can render it to the screen
        # If one is passed as argument we use that instead
        self.font = pygame.font.Font("arial.ttf", self.textSize) if font is None else font
        self.textWidth, self.textHeight = self.font.size(text)  # Getting the size in pixels of the area representing the text
        self.textX = x + (width/2) - (self.textWidth/2)  # Determining the x and y of the text so that it is centred
        self.textY = y + (height/2) - (self.textHeight/2)

        # Pygame does not allow us to render text onto an existing surface so we must create a new one and blit() it onto
        # our existing surface
        self.textSurface = self.font.render(self.text, True, (0, 0, 0))  # Creating a new surface

        self.action = action  # Save the function which should be called on its press

    # Function which draws the button including border and text
    def renderButton(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)  # Draw the rectangle representing the button in black
        pygame.draw.rect(surface, (255, 255, 255), self.innerRect)  # Draw the inner rectangle in white

        surface.blit(self.textSurface, (self.textX, self.textY))  # Rendering the surface created in the constructor

    # Function which when given the mouse co-ordinates determines whether the mouse is over the button
    def isPressed(self, mousePos):
        mouseX = mousePos[0]
        mouseY = mousePos[1]
        if self.x <= mouseX <= self.x + self.width - 1:  # Checking for collision in the x plane
            if self.y <= mouseY <= self.y + self.height - 1:  # Checking for collision in the y plane
                return True  # If the mouse is in line with the button in both planes it must be touching it
        return False

    # This function is run whenever the button is pressed
    def runAction(self):
        return self.action()


# This is a class representing an input box on the user's screen, it inherits useful methods from the Button class
class inputButton(Button):

    # Constructor which initialises the super constructor and changes the text from black to gray
    def __init__(self, x, y, width, height, action, text):
        super().__init__(x, y, width, height, action, text)
        self.defaultText = text  # The default text to be rendered if the box is empty
        self.textSurface = self.font.render(self.text, True, (156, 156, 156))  # Changing the text to grey instead of black
        self.isFocused = False
        # Rect to render if the button is focused
        self.focusedRect = pygame.Rect(x - 4, y - 4, width + 8, height + 8)
        self.invalidRect = pygame.Rect(x - 2, y - 2, width + 4, height + 4)  # Rect to render if contents is invalid
        self.textInput = ""  # Stores what the user has entered into the box
        self.isValid = False  # Represents whether the inputText is valid for that box or not

    def changeText(self, newText, isDefault):
        if isDefault:  # If the default text should be rendered, simply render it
            # Update the text location
            self.textWidth, self.textHeight = self.font.size(self.defaultText)  # Getting the size in pixels of the area representing the text
            self.textX = self.x + (self.width / 2) - (self.textWidth / 2)  # Determining the x and y of the text so that it is centred
            self.textY = self.y + (self.height / 2) - (self.textHeight / 2)
            # Render the text onto the surface
            self.textSurface = self.font.render(self.defaultText, True, (156, 156, 156))
        else:
            # Update the text location
            self.textWidth, self.textHeight = self.font.size(self.textInput)  # Getting the size in pixels of the area representing the text
            self.textX = self.x + (self.width / 2) - (self.textWidth / 2)  # Determining the x and y of the text so that it is centred
            self.textY = self.y + (self.height / 2) - (self.textHeight / 2)
            # Render the text onto the surface
            self.textSurface = self.font.render(newText, True, (0, 0, 0))

    # Function which draws the button including border and text
    # It has been overriden from its super class to allow it to be highlighted when focused
    def renderButton(self, surface):
        if self.isFocused:  # If focused render grey rectangle to make it appear focused
            pygame.draw.rect(surface, (156, 156, 156), self.focusedRect)

        # If the button is not empty and is not valid (contains invalid input) render the outside as red
        if self.isValid is False and self.textInput != "":
            pygame.draw.rect(surface, (255, 0, 0), self.invalidRect)

        pygame.draw.rect(surface, (0, 0, 0), self.rect)  # Draw the rectangle representing the button in black
        pygame.draw.rect(surface, (255, 255, 255), self.innerRect)  # Draw the inner rectangle in white

        surface.blit(self.textSurface, (self.textX, self.textY))  # Rendering the surface created in the constructor


# Class used to create instances of the nickname input box with all its required validation
class NicknameInput(inputButton):

    def __init__(self, x, y, width, height, action, text):
        # Creating the super class and creating a blank input string
        super().__init__(x, y, width, height, action, text)
        self.isLocked = False  # Can be used to prevent changes to the button

    def updateInput(self, currentScreen):
        if self.isLocked:  # Don't do anything if it is locked
            return

        if self.textInput != "" and len(self.textInput) <= 14:  # If all rules are followed update the label
            self.changeText(self.textInput, False)  # Change the label
            self.isValid = True
        elif self.textInput == "":  # If empty enter default string
            self.changeText(None, True)
            self.isValid = False
        else:  # If string too long slice it
            self.textInput = self.textInput[0:14]
            self.changeText(self.textInput, False)
            self.isValid = True

        currentScreen.updatePlayerName(0, self.textInput)


# Class used to create instances of the IP input box and requires all the validation it needs
class IpInputBox(inputButton):

    def __init__(self, x, y, width, height, action, text):
        # Creating the super class and creating a blank input string
        super().__init__(x, y, width, height, action, text)

    def updateInput(self, currentScreen):
        if self.textInput == "":  # If empty render default text
            self.changeText(None, True)
            self.isValid = False
        else:
            try:  # Attempt to create an ip address with input
                ip = ipaddress.ip_address(self.textInput)
            except ValueError:  # If IP address is not valid outline the box in red
                self.isValid = False
            else:  # If valid IP address do nothing extra
                self.isValid = True
            if self.textInput == "localhost":
                self.isValid = True  # If local host is the IP allow it
            self.changeText(self.textInput, False)


# Class used to create instances of the port input box and validate its input
class PortInputBox(inputButton):
    def __init__(self, x, y, width, height, action, text):
        # Creating the super class and creating a blank input string
        super().__init__(x, y, width, height, action, text)

    def updateInput(self, currentScreen):
        if self.textInput == "":  # If empty render default text
            self.changeText(None, True)
            self.isValid = False
        else:
            self.isValid = True
            if not (2 <= len(self.textInput) <= 5):  # Ensure port is between 4 and 5 digits long
                self.isValid = False  # Indicate it is invalid
                self.textInput = self.textInput[0:6]  # Slice it so it's not longer than 5 digits
            for digit in self.textInput:  # Cycle through every digit
                if not digit.isdigit():  # If there is a character which is not a digit
                    self.isValid = False  # Indicate it is invalid
            self.changeText(self.textInput, False)  # Update the text

