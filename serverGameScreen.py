import random
from datetime import datetime
import aiTank
import gameScreen
import clientPlayer
import player
import projectile
import pygame
import createGameScreen
import math


# This is a screen class which represents the player's screen when they are actually in the game and moving around etc
class ServerGameScreen(gameScreen.GameScreen):
    
    def __init__(self, screenWidth, screenHeight, playerList, gameMap, selfTankIndex, clientSocks=None):
        super().__init__(screenWidth, screenHeight)  # Passing width and height to super constructor
        self.players = playerList  # Saving arguments given to us
        self.gameMap = gameMap
        self.tankIndex = selfTankIndex  # This represents which index contains the user's tank
        self.clientSocks = clientSocks
        self.isLAN = True if clientSocks is not None else False

        # Create a list of "ClientPlayer" objects to represent all the tanks on the screen
        self.tanks = []
        self.entityList = []
        for i in range(len(self.players)):  # For each player in the game
            # Create a new "ClientPlayer" object and add it to the tanks array
            if self.players[i].Ai is False:
                self.tanks.append(clientPlayer.ClientPlayer(self.players[i], 1000 + (math.sin(2 * math.pi * i / len(self.players)) * 900), 1000 - (math.cos(2 * math.pi * i / len(self.players)) * 900), self.width, self.height, True if i == 0 else False))
            else:
                self.tanks.append(aiTank.AITank(self.players[i], 1000 + (math.sin(2 * math.pi * i / len(self.players)) * 900), 1000 - (math.cos(2 * math.pi * i / len(self.players)) * 900), self.width, self.width))
            self.entityList.append(self.tanks[i])  # Also add to the entity list
        self.thisTank = self.tanks[self.tankIndex]  # Get our tank
        # Finding where the centre of our screen should be based on our tank's location
        self.centreScreen = [self.thisTank.x, self.thisTank.y]
        self.deltaX = -self.thisTank.x + self.width // 2  # The amount we must offset objects so that they are rendered in the right location
        self.deltaY = -self.thisTank.y + self.height // 2
        if self.isLAN:
            string = encodeStartGame(self.tanks)
            for socket in clientSocks:
                socket[0].sendall(string.encode())

    def renderScreen(self, surface):
        self.tickScreen()
        self.deltaX = -self.thisTank.x + self.width // 2   # The amount we must offset objects so that they are rendered in the right location
        self.deltaY = -self.thisTank.y + self.height // 2
        self.gameMap.render(surface, (self.deltaX, self.deltaY))  # Render the game map, currently a 1000x1000 square
        for ent in self.entityList:  # For each projectile
            if ent.type == "projectile":
                ent.render(surface, (self.deltaX, self.deltaY))
            elif ent.type == "tank":
                ent.renderTank(surface, (self.deltaX, self.deltaY))  # Render the tank
        if self.winnerTicks > 0 and self.thisTank.isAlive:  # If we are rendering the winner text (we won)
            surface.blit(self.textSurface, self.textDest)  # Blit the text onto the surface
        if self.winnerTicks > 200:  # If the winner text has been displayed for more than 5 secs
            # Return a new create game screen which the screen should change to
            return createGameScreen.CreateGameScreen(self.width, self.height, self.players, self.clientSocks), "New screen"

    def tickScreen(self):
        # Processing entities
        for entity in self.entityList:
            if entity.type == "projectile":
                res = entity.tickProjectile(self.gameMap.boundaryList)
                if res[1] == "destroyProj":  # If function has indicated we should destroy a projectile we should do it
                    #  Finding and removing the projectile
                    uuid = res[0]  # Getting the uuid
                    for i in range(len(self.entityList)):  # cycle through every entity
                        if self.entityList[i].uuid == uuid:  # If the UUIDs match
                            self.entityList.pop(i)  # Remove the entity with that UUID
                            break

            elif entity.type == "tank" and entity.player.Ai:  # If it is an AI tank
                entity.tickAITank(self.entityList, self.gameMap)
        if self.isLAN:
            for socket in self.clientSocks:
                # doneGameTick = False
                # while doneGameTick is False:
                data = ""
                try:
                    data = socket[0].recv(1024).decode()  # Receive the messages
                except Exception as e:
                    print(e)
                    pass
                messages = data.split("|")

                messages = [i for i in messages if i != ""]  # Remove all empty messages
                for message in messages:  # For every message
                    if message[0:4] == "!GT!":  # If it is a game tick
                        message = message[4:]  # Remove the flags
                        message = message[:-4]
                        attributes = message.split(" ")  # Split into separate attributes
                        for i in range(len(self.entityList)):  # Find the entity with the corresponding uuid
                            if self.entityList[i].uuid == attributes[4]:
                                # Update its attributes
                                self.entityList[i].x = float(attributes[1])
                                self.entityList[i].y = float(attributes[2])
                                self.entityList[i].rotation = int(attributes[3])
                        # doneGameTick = True

                    elif message[0:4] == "!AE!":  # If remove entity flag
                        message = message[4:]  # Remove the flags
                        message = message[:-4]
                        attributes = message.split(" ")
                        if attributes[0] == "projectile":  # If we should add a projectile
                            # Create the projectile from the transmitted info
                            proj = projectile.Projectile(float(attributes[1]), float(attributes[2]), int(attributes[3]), attributes[7], player.Player(attributes[5], int(attributes[6]), True if attributes[4] == 1 else False, attributes[7]))
                            proj.owner.uuid = attributes[9]
                            self.processShooting((proj, attributes[3], attributes[9]))  # Send the new entity to all the clients
                    elif message[0:4] == "!RD!":  # Request death flag
                        message = message[4:]  # Remove the flags
                        message = message[:-4]
                        uuids = message.split(" ")  # Split into the individual uuids
                        e1, e2 = None, None
                        i1, i2 = None, None
                        for i in range(len(self.entityList)):  # Search the entity list for the
                            if self.entityList[i].uuid == uuids[0]:  # If the corresponding uuid is found
                                e1 = self.entityList[i]  # Save the entity
                                i1 = i  # And save its index
                            elif self.entityList[i].uuid == uuids[1]:
                                e2 = self.entityList[i]
                                i2 = i
                        # If both have been found and are a tank and projectile duo
                        if i1 is not None and i2 is not None and ((e1.type == "tank" and e2.type == "projectile") or (e2.type == "tank" and e1.type == "projectile")):
                            # If they are touching in the x plane
                            touchingX = e1.x + (e1.sizeX // 2) >= e2.x - (e2.sizeX // 2) and e1.x - (e1.sizeX // 2) <= e2.x + (e2.sizeX // 2)
                            # If they are touching in the y plane
                            touchingY = e1.y + (e1.sizeY // 2) >= e2.y - (e2.sizeY // 2) and e1.y - (e1.sizeY // 2) <= e2.y + (e2.sizeY // 2)
                            if touchingX and touchingY:  # If they are both colliding
                                self.thisTank.uuidDeleteList.append(uuids[0])  # Delete them for clients
                                self.thisTank.uuidDeleteList.append(uuids[1])
                                if self.thisTank.uuid in uuids:  # If the server player's tank is being deleted
                                    self.thisTank.isAlive = False  # Indicate it is dead
                                # Delete them for the server
                                if i1 > i2:
                                    del self.entityList[i1]
                                    del self.entityList[i2]
                                else:
                                    del self.entityList[i2]
                                    del self.entityList[i1]

            # Send changes to clients
            if len(self.thisTank.uuidDeleteList) > 0:  # if there are entities to be deleted
                message = "|!DE!"
                for uuid in self.thisTank.uuidDeleteList:
                    message += uuid + "  "  # Add the entity and a double space between entities
                message = message[:-2]  # Remove the last double space
                message += "!DE!|"
                # Send the uuids to each client
                for socket in self.clientSocks:
                    socket[0].sendall(message.encode())
            strEntList = encodeEntityList(self.entityList)  # Get the encoded entity list
            for socket in self.clientSocks:  # Send it to all clients
                socket[0].sendall(strEntList.encode())

        # Detecting whether someone/team has won
        teams = []
        for ent in self.entityList:
            if ent.type == "tank":
                teams.append(ent.team)
        if len(teams) == 1:
            self.winnerTicks += 1  # Increment the winner ticks
            if self.entityList[0].uuid == self.thisTank.uuid:  # If the server's tank has won
                # Display won text
                if self.winnerTicks == 1:  # Execute this code only once
                    textSize = int(self.width * 0.0217)  # Setting the font size dependent on the screen size
                    self.font = pygame.font.Font("arial.ttf", textSize)
                    self.textSurface = self.font.render("WINNER!", True, (0, 128, 255))  # Creating a new surface
                    w, h = self.font.size("WINNER!")
                    self.textDest.append(self.width / 2 - w / 2)
                    self.textDest.append(self.height / 4 - h / 2)

            elif self.entityList[0].player.Ai is False and self.isLAN:
                # Search for the socket with the same ip as the winner
                for socket in self.clientSocks:  # For every socket
                    for ent in self.entityList:  # Find the entity with a matching IP
                        if socket[1][0] == ent.ip: # If the ips match
                            message = "|!WG!WINNER!!WG!|"  # Create a winner message
                            socket[0].sendall(message.encode())  # Send it to the winning socket

    # Sends a newly added projectile to all clients
    def processShooting(self, projectile):
        # projectile should be a tuple containing the projectile object and the initial rotation
        self.entityList.append(projectile[0])
        if self.isLAN:  # If it is a network game
            message = "|!AE!"  # The add entity flag
            # Projectile string format:
            # "projectile" x y angle Ai name team ip uuid player_uuid
            # Add all the attributes separate by a space
            message += "projectile " + str(projectile[0].x) + " " + str(projectile[0].y) + " " + str(projectile[1]) + " "
            if projectile[0].owner.Ai is True:
                message += "1 "
            else:
                message += "0 "
            message += projectile[0].owner.name + " " + str(projectile[0].owner.team) + " " + projectile[0].owner.ip + " " + projectile[0].uuid + " " + projectile[2]
            message += "!AE!|"  # Add the ending flag
            for socket in self.clientSocks:  # Send to all clients
                socket[0].sendall(message.encode())


def encodeStartGame(tankList):
    result = "|!SG!"
    for tank in tankList:
        result += str(tank.x) + " " + str(tank.y) + " " + tank.uuid + "  "
    result = result[:-2]  # Remove the final 2 spaces
    result += "!SG!|"  # Add another string at the end to indicate the end of the string
    return result


# Converts a list of entities into a string object
def encodeEntityList(entityList):
    # "|" Indicates the start and end of a message
    # "!GT!" Indicates it is a game tick and an entity list will be sent after
    result = "|!GT!"
    for entity in entityList:
        result += entity.type + " " + str(entity.x) + " " + str(entity.y)
        if entity.type == "tank":
            # Tank string format:
            # "tank" x y rotation uuid
            result += " " + str(entity.rotation) + " " + entity.uuid
        elif entity.type == "projectile":
            # Projectile string format:
            # "projectile" x y velocityX velocityY uuid
            result += " " + str(entity.velocityX) + " " + str(entity.velocityY) + " " + entity.uuid
        result += "  "  # Add a double space separator between entities
    result = result[:-2]  # Remove the last double space
    now = datetime.now()  # get the time
    time = now.strftime("%H%M.%S%f")  # Extract the part we care about
    result += "  " + time  # Only get the seconds and ms part
    result += "!GT!|"  # Add the flag at the end
    return result
