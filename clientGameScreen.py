import clientPlayer
import aiTank
import gameScreen
import projectile
import player
import clientLobbyScreen
from datetime import datetime
import pygame


# Class represents the game screen for clients
class ClientGameScreen(gameScreen.GameScreen):
    def __init__(self, screenWidth, screenHeight, playerList, gameMap, selfTankIndex, tankCords, serverSocket):
        super().__init__(screenWidth, screenHeight)
        self.players = playerList
        self.gameMap = gameMap
        self.tankIndex = selfTankIndex
        self.serverSocket = serverSocket
        self.serverSocket.settimeout(1)
        # Create a list of "ClientPlayer" objects to represent all the tanks on the screen
        self.tanks = []
        self.entityList = []
        for i in range(len(self.players)):  # For each player in the game
            # Create a new "ClientPlayer" object and add it to the tanks array
            if self.players[i].Ai is False:
                self.tanks.append(clientPlayer.ClientPlayer(self.players[i], 0, 0, self.width, self.height, True if i == 0 else False))
            else:
                self.tanks.append(aiTank.AITank(self.players[i], 0, 0, self.width, self.width))
            self.tanks[i].x = tankCords[i][0]  # Set the co-ordinates as given by the server
            self.tanks[i].y = tankCords[i][1]  # Set the co-ordinates as given by the server
            self.tanks[i].uuid = tankCords[i][2]
            self.entityList.append(self.tanks[i])  # Also add to the entity list
        self.thisTank = self.tanks[self.tankIndex]  # Get our tank
        # Finding where the centre of our screen should be based on our tank's location
        self.centreScreen = [self.thisTank.x, self.thisTank.y]
        self.deltaX = -self.thisTank.x + self.width // 2  # The amount we must offset objects so that they are rendered in the right location
        self.deltaY = -self.thisTank.y + self.height // 2

    def renderScreen(self, surface):
        res = self.tickScreen()
        self.deltaX = -self.thisTank.x + self.width // 2   # The amount we must offset objects so that they are rendered in the right location
        self.deltaY = -self.thisTank.y + self.height // 2
        self.gameMap.render(surface, (self.deltaX, self.deltaY))  # Render the game map, currently a 1000x1000 square

        for ent in self.entityList:  # For each projectile
            if ent.type == "projectile":
                ent.render(surface, (self.deltaX, self.deltaY))
            elif ent.type == "tank":
                ent.renderTank(surface, (self.deltaX, self.deltaY))  # Render the tank

        if self.winnerTicks > 0:  # If we are the winner
            surface.blit(self.textSurface, self.textDest)  # Render the winner text
            if self.winnerTicks > 300:  # If the winner text has been displayed for more than 5 secs
                # Return a new client lobby screen which the screen should change to
                return clientLobbyScreen.ClientLobbyScreen(self.width, self.height, self.players, self.serverSocket, self.thisTank.name), "New screen"
            self.winnerTicks += 1

        if res is not None:
            return res

    def tickScreen(self):
        # Processing entities
        for entity in self.entityList:
            if entity.type == "projectile":
                # Process projectiles so they move
                res = entity.tickProjectile(self.gameMap.boundaryList)
                if res[1] == "destroyProj":  # If function has indicated we should destroy a projectile we should do it
                    #  Finding and removing the projectile
                    uuid = res[0]  # Getting the uuid
                    for i in range(len(self.entityList)):  # cycle through every entity
                        if self.entityList[i].uuid == uuid:  # If the UUIDs match
                            del self.entityList[i]  # Remove the entity with that UUID
                            break

        # Send the changes to the client's tank to the server
        # Tank string format:
        # "tank" x y rotation uuid
        data = "|!GT!tank " + str(self.thisTank.x) + " " + str(self.thisTank.y) + " " + str(self.thisTank.rotation) + " " + self.thisTank.uuid + "!GT!|"
        print("Sent", data)
        self.serverSocket.sendall(data.encode())
        now = datetime.now()  # get the time
        time = now.strftime("%H%M.%S%f")  # Extract the part we care about
        timeSent = float(time)  # The time at which we sent our game tick to the server
        # Send any other messages
        for message in self.thisTank.messageList:
            self.serverSocket.sendall(message.encode())

        doneGameTick = False
        while not doneGameTick:
            data = ""
            try:
                data = self.serverSocket.recv(1024).decode()
                print("Receive", data)
            except Exception as e:
                print("Failed to receive from server", e)
                pass
            messages = data.split("|")  # Split up into the different messages
            messages = [i for i in messages if i != ""]  # Remove all empty messages
            for message in messages:  # For every message
                if message[0:4] == "!GT!":  # If it is a game tick
                    message = message[4:]  # Remove the flags
                    message = message[:-4]
                    entities = message.split("  ")  # Split it into each entity
                    entities.pop()
                    recvTime = float(message.split("  ")[-1])  # And the time (the last element in the array)
                    # If we sent the game tick after the server transmitted the gametick then it is an old game tick and we discard it and wait for a new one
                    if timeSent > recvTime:
                        continue
                    for i in range(len(entities)):  # For each entity transmitted
                        attributes = entities[i].split(" ")  # Get each attribute
                        if attributes[0] == "tank":  # If a tank
                            if attributes[4] == self.entityList[i].uuid:  # If the UUIDs match
                                self.entityList[i].x = float(attributes[1])  # Change the attributes
                                self.entityList[i].y = float(attributes[2])
                                self.entityList[i].rotation = int(attributes[3])
                            # We don't update projectiles as they are processed by each client themselves
                    doneGameTick = True
                elif message[0:4] == "!AE!":  # If it is an add entity flag
                    message = message[4:]  # Remove the flags
                    message = message[:-4]
                    attributes = message.split(" ")
                    if attributes[0] == "projectile":  # If we should add a projectile
                        # Create the projectile from the transmitted info
                        proj = projectile.Projectile(float(attributes[1]), float(attributes[2]), int(attributes[3]), attributes[7], player.Player(attributes[5], int(attributes[6]), True if attributes[4] == 1 else False, attributes[7]))
                        proj.uuid = attributes[8]  # Change its uuid to the non-generated one so is the same as on the server side
                        proj.owner.uuid = attributes[9]
                        self.entityList.append(proj)  # Add it to the entity list
                elif message[0:4] == "!DE!":  # If it is a delete entity flag
                    message = message[4:]  # Remove the flags
                    message = message[:-4]
                    uuids = message.split("  ")  # Split it into each entity uuid

                    for uuid in uuids:  # For each uuid
                        if uuid == self.thisTank.uuid:  # If the client is being removed
                            return [clientLobbyScreen.ClientLobbyScreen(self.width, self.height, self.players, self.serverSocket, self.thisTank.name), "New screen"]
                        for i in range(len(self.entityList)):  # Search the entity list for an entity with a matching uuid
                            if self.entityList[i].uuid == uuid:  # If a match is found
                                del self.entityList[i]  # Delete that entity
                                break  # Don't complete the rest of the loop
                elif message[0:4] == "!WG!":  # If a win game flag is given
                    message = message[4:]  # Remove the flags
                    message = message[:-4]
                    # Display won text
                    if self.winnerTicks == 0:  # Execute this code only once
                        textSize = int(self.width * 0.0217)  # Setting the font size dependent on the screen size
                        self.font = pygame.font.Font("arial.ttf", textSize)
                        self.textSurface = self.font.render(message, True, (0, 128, 255))  # Creating a new surface
                        w, h = self.font.size(message)
                        self.textDest.append(self.width / 2 - w / 2)
                        self.textDest.append(self.height / 4 - h / 2)
                    self.winnerTicks += 1  # Increment the winner ticks

    def processShooting(self, projectile):
        # projectile should be a tuple containing the projectile object and the initial rotation
        message = "|!AE!"  # The add entity flag
        # Projectile string format:
        # "projectile" x y angle Ai name team ip uuid player_uuid
        # Add all the attributes separate by a space
        message += "projectile " + str(projectile[0].x) + " " + str(projectile[0].y) + " " + str(projectile[1]) + " "
        if projectile[0].owner.Ai is True:
            message += "1 "
        else:
            message += "0 "
        message += projectile[0].owner.name + " " + str(projectile[0].owner.team) + " " + projectile[0].owner.ip + " " + projectile[0].uuid + " " + self.thisTank.player.uuid
        message += "!AE!|"  # Add the ending flag
        self.serverSocket.sendall(message.encode())
