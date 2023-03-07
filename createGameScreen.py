# This file contains a class which contains all the methods and attributes needed to create and render a create game screen
import random
import socket
import threading
import gameMap
import serverGameScreen
import guiUtils
import pygame
import mainMenuScreen
import userList
from screen import Screen
import clientLobbyScreen
import player


# This class can be instantiated to easily create a create Game screen
class CreateGameScreen(Screen):

    def __init__(self, screenWidth, screenHeight, oldPlayerList=None, oldSocketList=None):
        super().__init__(screenWidth, screenHeight)  # Passing width and height to super constructor
        self.buttonW = int(screenWidth * 0.078)  # Setting button sizes relative to the user's screen size
        self.buttonH = int(screenHeight * 0.049)
        self.inputBoxW = int(screenWidth * 0.12)
        self.inputBoxH = self.buttonH
        self.ip = socket.gethostbyname(socket.gethostname())
        p1 = player.Player("", 1, False, self.ip)  # Add the player representing the host
        self.players = oldPlayerList if oldPlayerList is not None else [p1]  # Use the old player list if it is there
        self.playerListBox = userList.userListBox(self.players, screenWidth * 0.05, screenHeight * 0.2, screenWidth * 0.3, screenHeight * 0.4, 0, False)
        self.clientSocks = oldSocketList if oldSocketList is not None else []  # A 2D array containing the sockets and addresses of connected clients
        self.serverSock = None  # Stores the servers socket which clients connect to
        self.connThread = None  # Should store any active threads which wait for connections
        self.shouldThread = True

        self.buttons = [
            # Return to main menu button
            guiUtils.Button((screenWidth / 2) - (self.buttonW / 2), (screenHeight * 0.9) - (self.buttonH / 2), self.buttonW, self.buttonH, self.mainMenuSwitch, "Main Menu"),

            # Start game button
            guiUtils.Button((screenWidth / 2) - (self.buttonW / 2), (screenHeight * 0.75) - (self.buttonH / 2), self.buttonW, self.buttonH, self.startGame, "Start Game"),
            # Nickname input box button
            guiUtils.NicknameInput((screenWidth / 2) - (self.inputBoxW / 2), (screenHeight / 2) - (self.inputBoxH / 2), self.inputBoxW, self.inputBoxH, self.nicknamePress, "Enter Nickname"),

            # IP address input box
            guiUtils.IpInputBox((screenWidth / 2) - (self.inputBoxW / 2), (screenHeight * 0.1) - (self.inputBoxH / 2), self.inputBoxW, self.inputBoxH, self.ipAddressPress, "Host IP address"),

            # Join network game button
            guiUtils.Button((screenWidth / 2) - (self.buttonW / 2), (screenHeight * 0.25) - (self.buttonH / 2), self.buttonW, self.buttonH, self.joinGamePress, "Join Game"),

            # Increase AI tank button
            guiUtils.Button((screenWidth / 5) - (self.buttonW/2), (screenHeight * 0.7) - (self.buttonH / 2), self.buttonW * 1.2, self.buttonH, self.addAiTank, "Increase AI Tanks"),

            # Open game to network user's button
            guiUtils.Button((screenWidth * 0.8) - (self.buttonW / 2), (screenHeight * 0.7) - (self.buttonH / 2), self.buttonW * 1.5, self.buttonH, self.openGame, "Open game to network"),

            # Port input box
            guiUtils.PortInputBox((screenWidth / 2) - (self.inputBoxW / 2), (screenHeight * 0.18) - (self.inputBoxH / 2), self.inputBoxW, self.inputBoxH, self.portPress, "Port"),
        ]
        self.texts = []
        self.nonRenderButtons = self.playerListBox.buttons
        self.shouldClose = False

        # Creates a new surface with our image on and stores it, it can then be "blitted" onto our main surface
        self.backgroundImageSurface = pygame.image.load("BackgroundImage.png")

        # Represents whether the user's keyboard input should be captured as they are typing in an input box
        self.captureKeyboard = False
        self.focusedInput = None  # Corresponds to the index in the buttons array of the focused input box (if any)

        if oldSocketList is not None:  # If this is a screen after a previous round
            self.openGame()  # Allow network connections and transmit data to clients
        if oldPlayerList is not None:  # If we have ended a round
            self.buttons[2].changeText(oldPlayerList[0].name, False)  # Set the nickname input box to the server's name
            self.buttons[2].isLocked = True
            self.buttons[2].isValid = True

    def getButtons(self):
        return self.buttons + self.nonRenderButtons  # Merging the list of all buttons

    def renderScreen(self, surface):
        self.tickScreen()

        # Renders the background image onto the surface
        surface.blit(self.backgroundImageSurface, ((self.width / 2) - (self.backgroundImageSurface.get_width() / 2), (self.height / 2) - (self.backgroundImageSurface.get_height() / 2)))

        for i in range(len(self.buttons)):  # Cyclically renders all buttons in the class onto the surface
            self.buttons[i].renderButton(surface)
        self.playerListBox.render(surface)
        for i in range(len(self.texts)):
            surface.blit(self.texts[i][0], (self.texts[i][1][0], self.texts[i][1][1]))

    # Mainly network processing
    def tickScreen(self):
        if self.connThread is not None:  # If the game is opened to LAN
            for clientSocket in self.clientSocks:
                try:
                    clientSocket[0].sendall(("|!PL!" + encodePlayers(self.players) + "!PL!|").encode())
                except socket.error as e:
                    pass

    # A functon which is called when the main menu button is pressed
    def mainMenuSwitch(self):
        # Create a new main menu screen with the parameters given to this object
        newScreen = mainMenuScreen.MainMenu(self.width, self.height)
        return newScreen  # Return the new screen so it can be set to current screen

    # A functon which is called when the start game button is pressed i.e. it starts the round
    def startGame(self):
        for i in range(len(self.players)):  # Checking if all names are valid
            if not(1 <= len(self.players[i].name) <= 10):  # If their names are not between 1 and 10 characters
                print("Error starting game, some player names are not valid.")  # Print an error
                return  # Prevent the game from being started
        if self.serverSock is not None:
            self.shouldThread = False  # Stops the thread from running
            self.serverSock.close()  # Close the socket
            self.serverSock = None  # Delete the socket
        # Create a new game screen with the current screen's width and height
        newScreen = serverGameScreen.ServerGameScreen(self.width, self.height, self.players, gameMap.getMap(), 0, self.clientSocks)
        return newScreen  # Return it so it changes the current screen

    # Function called when nickname input box is pressed
    def nicknamePress(self):
        self.captureKeyboard = True
        self.focusedInput = 2
        self.buttons[2].isFocused = True

    # Function called when ip address input box is pressed
    def ipAddressPress(self):
        self.captureKeyboard = True  # Capture user's key pressed
        self.focusedInput = 3  # Set the focused input the IP address box
        self.buttons[3].isFocused = True

    # Method called when port address input box is pressed
    def portPress(self):
        self.captureKeyboard = True
        self.focusedInput = 7
        self.buttons[7].isFocused = True

    # Function called when join game button is pressed
    def joinGamePress(self):
#         addr = socket.gethostbyname(socket.gethostname())
#         port = 56600
#         name = "Client"
        addr = self.buttons[3]  # Get the address
        if not addr.isValid:  # Check if it is valid
            print("Input is not an IP address")
            return
        addr = addr.textInput
        if addr == "localhost" or addr == "127.0.0.1":  # If localhost or equivalent is used
            addr = socket.gethostbyname(socket.gethostname())  # Use the real LAN address

        port = self.buttons[7]  # Get the port
        if not port.isValid:  # Check if it is valid
            print("Input is not a port")
            return
        port = port.textInput

        name = self.buttons[2]  # Same for the name
        if not name.isValid:
            print("Nickname is invalid")
            return
        name = name.textInput

        mySock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:  # Attempt to connect
            mySock.connect((addr, int(port)))  # Attempt to connect to the connected port
        except socket.error as error:
            print("Connection failed: %s" % error)  # Print any error raised
            return  # Stop executing the function

        mySock.sendall(name.replace(" ", "_").encode())  
        playerList = decodePlayers(mySock.recv(1024).decode())
        newScreen = clientLobbyScreen.ClientLobbyScreen(self.width, self.height, playerList, mySock, name)
        return newScreen  # Return it so it changes the current screen
        
    # Function which removes a player from the player list
    def removeUser(self, user):
        if user == self.players[0]:  # If the user is the first one in the list it must be the host so dont remove them
            return
        self.players.remove(user)  # Remove the player
        # Update the player list
        self.playerListBox = userList.userListBox(self.players, self.width * 0.05, self.height * 0.2, self.width * 0.3, self.height * 0.4, 0, False)
        self.nonRenderButtons = self.playerListBox.buttons

    # Function called when increase AI tank button is pressed
    def addAiTank(self):
        if len(self.players) >= 10:  # If there are 10 players do not add another tank
            return
        # Creating a name for the tank from a random 1-2 digit number
        name = "AI " + str(random.randint(1, 99))
        nameTaken = False
        for i in range(len(self.players)):  # Checking whether that name is taken
            if self.players[i].name == name:
                nameTaken = True
                break

        while nameTaken:  # While name is taken continually generated a new one and check if it is taken
            nameTaken = False
            name = "AI " + str(random.randint(1, 99))
            for i in range(len(self.players)):  # Checking whether that name is taken
                if self.players[i].name == name:
                    nameTaken = True
                    break

        self.players.append(player.Player(name, 1, True, self.ip))
        self.playerListBox = userList.userListBox(self.players, self.width * 0.05, self.height * 0.2, self.width * 0.3, self.height * 0.4, 0, False)
        self.nonRenderButtons = self.playerListBox.buttons

    # Function called which changes a particular player's name and updates everything needed
    def updatePlayerName(self, playerIndex, newName):
        self.players[playerIndex].name = newName  # Update the name in the player list
        self.playerListBox.userListEntries[playerIndex].updateName(newName)  # Update the name in the player list box/table

    # Function called when the open game button is pressed
    def openGame(self):
        if self.serverSock is not None:
            return   # If we are already listening for connections don't execute the code
        for i in range(len(self.players)):  # Checking if all names are valid
            if not(1 <= len(self.players[i].name) <= 10):  # If their names are not between 1 and 10 characters
                print("Error starting game, some player names are not valid.")  # Print an error
                return  # Prevent the game from being started
        self.buttons[2].isLocked = True  # Lock the nickname input box

        port = 56600  # Use a random unregistered port
        serverIP = socket.gethostbyname(socket.gethostname())  # Get the IP of the host computer
        textSize = int(self.width * 0.0117)  # Set the text size depending on screen size
        font = pygame.font.Font("arial.ttf", textSize)  # Create a font object
        portSurface = font.render("Port: " + str(port), True, (0, 0, 0))  # Create a surface with the port text on
        ipSurface = font.render("Local IP: " + serverIP, True, (0, 0, 0))  # Create a surface with the ip text on
        openGameBtn = self.buttons[6]  # Making a local copy of the button which has been pressed to make code more readable
        # Append to the text array an array containing the port surface object and a tuple with its location so it can be rendered
        self.texts.append([portSurface, (openGameBtn.x + (openGameBtn.width / 2) - (font.size("Port: " + str(port))[0] / 2), openGameBtn.y + openGameBtn.height + self.width * 0.02)])
        # Append to the text array an array containing the ip surface object and a tuple with its location so it can be rendered
        self.texts.append([ipSurface, (openGameBtn.x + (openGameBtn.width / 2) - (font.size("Local IP: " + serverIP)[0] / 2), (self.texts[0][1][1]) + self.width * 0.02)])

        self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a socket for clients to connect to
        self.serverSock.bind(("", port))  # Bind the socket to our port
        # Below line causes the error 
        self.serverSock.listen(9)  # Set the port to listen but only for a maximum number of connections
        self.connThread = threading.Thread(target=self.waitForConnections)
        self.connThread.start()

    # Adds a new player (from a connection) and updates the screen etc
    def addNewPlayer(self, name, addr):
        self.players.append(player.Player(name, 1, False, addr))  # Add to the list of players
        # Update the player list box
        self.playerListBox = userList.userListBox(self.players, self.width * 0.05, self.height * 0.2, self.width * 0.3, self.height * 0.4, 0, False)
        self.nonRenderButtons = self.playerListBox.buttons  # Update the buttons

    # Run in parallel, waits for connecting users to connect and then adds them to the player list
    def waitForConnections(self):
        while self.shouldThread:
            clientSocket, address = self.serverSock.accept()  # Accept connections
            print("Received a connection", clientSocket, address)
            if len(self.players) >= 10:
                clientSocket.close()
                continue  # Skip to the next loop
            name = clientSocket.recv(1024)  # Receive the name
            clientSocket.settimeout(0.001)
            self.addNewPlayer(name.decode().replace("_", " "), address[0])  # Add the player to the player list
            clientSocket.sendall(encodePlayers(self.players).encode())  # Send the player list to the player so they can display it
            self.clientSocks.append([clientSocket, address])  # Add the socket and address to the lis of sockets


# Encodes the player list into a string object for transmission
def encodePlayers(playerList):
    result = ""
    for player in playerList:
        result += player.name.replace(" ", "_") + " " + str(player.team) + " "  # Add the name and team
        result += "1 " if player.Ai else "0 "  # Add whether it is AI or not
        result += player.ip  # Add the ip address
        result += " " + player.uuid
        result += "  "  # Add a double space between players in the string
    result = result[:-2]  # Remove the last 2 characters
    return result


# Decodes a string after transmission and returns the player list
def decodePlayers(code):
    playerList = []
    players = code.split("  ")  # Split by double space to get each player
    for ply in players:
        attributes = ply.split(" ")  # Get all the attributes
        # Create a new player from the attributes
        p = player.Player(attributes[0], int(attributes[1]), True if attributes[2] == 1 else False, attributes[3])
        playerList.append(p)  # Add the player to the player list
    return playerList

