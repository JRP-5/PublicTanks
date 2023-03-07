import screen
import userList
import socket
import pygame
import player
import clientGameScreen
import gameMap


# Class represents a screen on the client's side when they are in a lobby
class ClientLobbyScreen(screen.Screen):

    def __init__(self, screenWidth, screenHeight, playerList, serverSocket, name):
        super().__init__(screenWidth, screenHeight)
        self.name = name
        self.serverSocket = serverSocket
        self.players = playerList
        playersIndex = self.getIndexInPlayers()  # Get the index of the client in the player list
        # Create the player list box
        self.playerListBox = userList.userListBox(self.players, (screenWidth / 2) - (screenWidth * 0.15), screenHeight / 2 - (screenHeight * 0.2), screenWidth * 0.3, screenHeight * 0.4, playersIndex, True)
        # Creates a new surface with our image on and stores it, it can then be "blitted" onto our main surface
        self.backgroundImageSurface = pygame.image.load("BackgroundImage.png")

        self.nonRenderButtons = self.playerListBox.buttons

    def renderScreen(self, surface):
        res = self.tickScreen()
        if res is not None:
            return res
        surface.fill((255, 255, 255))  # Clears the surface by filling it with white

        # Renders the background image onto the surface
        surface.blit(self.backgroundImageSurface, ((self.width / 2) - (self.backgroundImageSurface.get_width() / 2), (self.height / 2) - (self.backgroundImageSurface.get_height() / 2)))
        self.playerListBox.render(surface)

    # gets the index of the array players which corresponds to the client
    def getIndexInPlayers(self):
        thisIP = socket.gethostbyname(socket.gethostname())
        for i in range(len(self.players)):
            if (self.players[i].ip == thisIP) and self.players[i].name == self.name:
                return i
        return -1

    def tickScreen(self):
        data = ""
        try:
            data = self.serverSocket.recv(1024).decode()
        except Exception as e:
            print(e)
        data = data.split("|")  # Split into the individual messages
        messages = [x for x in data if (x != "")]  # Remove empty entries
        for message in messages:
            if message[0:4] == "!SG!":
                message = message[4:]  # Remove the flag
                message = message[:-4]
                cords = message.split("  ")  # The array contains strings with 2 numbers separate by a space
                for i in range(len(cords)):
                    cords[i] = [float(cords[i].split(" ")[0]), float(cords[i].split(" ")[1]), cords[i].split(" ")[2]]  # Split the string into the two co-ords

                # Create the new screen
                newScreen = clientGameScreen.ClientGameScreen(self.width, self.height, self.players, gameMap.getMap(), self.getIndexInPlayers(), cords, self.serverSocket)

                return [newScreen, "New screen"]
            elif message[0:4] == "!PL!":  # Must be a new player list
                message = message[4:]  # Remove the flags
                message = message[:-4]
                if self.players != decodePlayers(message):  # If the player list has changed
                    self.players = decodePlayers(message)  # Decode the player list
                    self.playerListBox = userList.userListBox(self.players, (self.width / 2) - (self.width * 0.15), self.height / 2 - (self.height * 0.2), self.width * 0.3, self.height * 0.4, self.getIndexInPlayers(), True)
                    self.nonRenderButtons = self.playerListBox.buttons


# Decodes a string after transmission and returns the player list
def decodePlayers(code):
    playerList = []
    players = code.split("  ")  # Split by double space to get each player
    for ply in players:
        attributes = ply.split(" ")  # Get all the attributes
        # Create a new player from the attributes
        p = player.Player(attributes[0].replace("_", " "), int(attributes[1]), True if attributes[2] == 1 else False, attributes[3])
        p.uuid = attributes[4]
        playerList.append(p)  # Add the player to the player list
    return playerList
