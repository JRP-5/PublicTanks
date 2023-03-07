import pygame
import ctypes
import guiUtils
import tankConstants


# This class can be used to create instances of the user list
class userListBox:

    def __init__(self, userList, x, y, width, height, renderYouTextIndex=-1, isClient=False):
        self.userList = userList  # Copying arguments to attributes
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        # This variable represents the player's index which means we should render "(You)" along with their name
        self.renderYouTextIndex = renderYouTextIndex
        self.userListEntries = []
        self.buttons = []
        # Calculating how tall one row should be based on the height of the box and the number of rows needed
        self.listEntryHeight = int(self.height / len(self.userList))
        # Adjusting the height of the box so that it perfectly fits all entries
        self.height = self.listEntryHeight * len(self.userList)

        # Creates an outer rectangle and inner rectangle to mimic the outline of a box
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.innerRect = pygame.Rect(x + 1, y + 1, self.width - 2, self.height - 2)

        for i in range(len(self.userList)):  # Cycle through every row in the table and render it at its appropriate position
            if i == renderYouTextIndex:
                self.userListEntries.append(userListEntry(userList[i], self.width, self.listEntryHeight, self.x, self.y + (self.listEntryHeight * i), True, isClient))
                self.buttons += self.userListEntries[i].buttons  # Add to the buttons array the buttons of the list entry
            else:
                self.userListEntries.append(userListEntry(userList[i], self.width, self.listEntryHeight, self.x, self.y + (self.listEntryHeight * i), False, isClient))
                self.buttons += self.userListEntries[i].buttons  # Add to the buttons array the buttons of the list entry

    def render(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)  # Draw the rectangle representing the outside in black
        pygame.draw.rect(surface, (255, 255, 255), self.innerRect)  # Draw the inner rectangle in white

        for i in range(len(self.userListEntries)):  # Iteratively render each row/entry
            self.userListEntries[i].render(surface)


# Class representing a row in the user list entry box
class userListEntry:

    def __init__(self, player, width, height, x, y, renderYouText, isClient):
        self.name = player.name  # Copying arguments given to the object
        self.team = player.team
        self.player = player
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.renderYouText = renderYouText
        self.textColour = tankConstants.colourList[self.team-1]  # Getting the team colour
        self.isClient = isClient

        # Creates an outer rectangle and inner rectangle to mimic the outline of a box
        self.rect = pygame.Rect(x, y, width, height)
        self.innerRect = pygame.Rect(x + 1, y + 1, width - 2, height - 2)

        ctypes.windll.user32.SetProcessDPIAware()
        screenWidth = ctypes.windll.user32.GetSystemMetrics(0)  # Getting accurate screen width
        self.textSize = int(screenWidth * 0.009)
        self.font = pygame.font.Font("arial.ttf", self.textSize)  # Creating a font object to let us render text

        # Creating the name text surface
        self.nameWidth, self.nameHeight = self.font.size(self.name)  # Getting the size in pixels of the area representing the text
        self.nameX = self.x + ((1/8) * self.width - (self.nameWidth/2))  # Determining the x and y of the text so that it is centred
        self.nameY = self.y + (self.height / 2) - (self.nameHeight / 2)
        # Creating a surface with the name text on it
        # If this entry represents the client then we render the "[You]" text
        self.nameSurface = self.font.render(self.name + " [You]" if self.renderYouText else self.name, True, self.textColour)

        # Creating the team number surface
        self.teamWidth, self.teamHeight = self.font.size(str(self.team))  # Getting the size in pixels of the area representing the text
        self.teamX = self.x + ((3/8) * self.width - (self.teamWidth/2))  # Determining the x and y of the text so that it is properly located
        self.teamY = self.y + (self.height / 2) - (self.teamHeight / 2)
        self.teamSurface = self.font.render(str(self.team), True, self.textColour)  # Creating a surface with the name text on it

        # Repurposing the input button to allow user to press a button to assign a user to a team
        self.changeTeamButton = guiUtils.Button(self.x + self.width * (5/8), self.y + 1, self.width * (1/4), self.height - 2, self.changeTeam, "Change Team", self.font)
        self.removeButton = guiUtils.Button(self.x + self.width * (7/8), self.y, self.width * (1/4), self.height, self.removeSelf, "Remove") if not self.isClient else None

        if not self.isClient:  # If we are the server
            self.buttons = [self.changeTeamButton, self.removeButton]  # Add all buttons
        else:
            self.buttons = []  # Else it should be empty

    # Renders all items in the user list
    def render(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.rect)  # Draw the rectangle representing the button in black
        pygame.draw.rect(surface, (255, 255, 255), self.innerRect)  # Draw the inner rectangle in white

        if not self.isClient:  # only render these buttons on the server
            self.removeButton.renderButton(surface)
            self.changeTeamButton.renderButton(surface)

        surface.blit(self.nameSurface, (self.nameX, self.nameY))  # Rendering the name text
        surface.blit(self.teamSurface, (self.teamX, self.teamY))  # Rendering the team number text

    # Changes the player's team to the next team in the list of teams
    def changeTeam(self):
        self.team = self.team % 10 + 1  # If the button is pressed swap to the next team
        self.player.team = self.team  # Set the actual player objects team
        self.textColour = tankConstants.colourList[self.team - 1]  # Update text colour
        self.updateTextSurfaces()

    def removeSelf(self):
        return self

    # A function which updates the player name and team surfaces when they have been changed (reduces repeated code)
    def updateTextSurfaces(self):
        # Creating the name text surface
        self.nameWidth, self.nameHeight = self.font.size(self.name)  # Getting the size in pixels of the area representing the text
        self.nameX = self.x + ((1 / 8) * self.width - (self.nameWidth / 2))  # Determining the x and y of the text so that it is centred
        self.nameY = self.y + (self.height / 2) - (self.nameHeight / 2)
        # Creating a surface with the name text on it
        # If this entry represents the client then we render the "[You]" text
        self.nameSurface = self.font.render(self.name + " [You]" if self.renderYouText else self.name, True, self.textColour)

        # Creating the team number surface
        self.teamWidth, self.teamHeight = self.font.size(str(self.team))  # Getting the size in pixels of the area representing the text
        self.teamX = self.x + ((3 / 8) * self.width - (self.teamWidth / 2))  # Determining the x and y of the text so that it is properly located
        self.teamY = self.y + (self.height / 2) - (self.teamHeight / 2)
        self.teamSurface = self.font.render(str(self.team), True, self.textColour)  # Creating a surface with the name text on it

    def updateName(self, newName):
        self.name = newName
        self.updateTextSurfaces()
