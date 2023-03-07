import entity
import tankConstants
import pygame
import pdb


# Superclass to the AI tank and player  tank classes, mainly to maintain uniform constants
class Tank(entity.Entity):
    def __init__(self, x, y, player, type, screenWidth, screenHeight, isHost):
        super().__init__(x, y, type)
        self.isAlive = True  # Represents whether the tank is still in the game and hasn't been killed
        self.player = player  # Save arguments
        self.name = player.name
        self.team = player.team
        self.ip = player.ip
        self.isHost = isHost
        self.sizeX = 61
        self.sizeY = 61
        self.moveSpeed = 5
        self.rotationSpeed = 5
        self.rotation = 0
        self.turretWidth = 17
        self.turretHeight = 80
        self.hatchRadius = 24
        self.velocityX = 0
        self.velocityY = 0
        self.shootCooldown = 0   # Represents how long until the tank can shoot again
        self.addedRotation = 0  # Keeps track of how much rotation has been added in a tick, so we don't always have to recalculate points
        self.uuidDeleteList = []  # List of indexes in the entity list to be deleted
        self.messageList = []  # A list of messages to be sent to the server, only used for clients

        self.textSize = int(screenWidth * 0.0117)  # Setting the font size dependent on the screen size
        # Creating a font object so we can render it to the screen
        self.font = pygame.font.Font("arial.ttf", self.textSize)
        # Creating a surface with the tank name on and the team colour
        self.nameSurface = self.font.render(self.name, True, tankConstants.colourList[self.team - 1])
        self.textWidth, self.textHeight = self.font.size(self.name)
        self.textX = (screenWidth / 2) - (self.textWidth / 2)
        self.textY = (screenHeight / 2) - self.sizeX - self.turretHeight - (self.textHeight / 2)

        # Generate all the corners of the tank's hull, around 0, 0
        self.hull = [(- self.sizeX // 2, - self.sizeY // 2),  # Top left
                     (self.sizeX // 2, - self.sizeY // 2),  # Top right
                     (self.sizeX // 2, self.sizeY // 2),  # Bottom right
                     (- self.sizeX // 2, self.sizeY // 2)]  # Bottom left
        # Generate the corners of the turret
        self.turret = [(- self.turretWidth // 2, - self.turretHeight - (self.turretWidth // 2)),  # Top left
                       (self.turretWidth // 2, - self.turretHeight - (self.turretWidth // 2)),  # Top right
                       (self.turretWidth // 2, self.turretWidth // 2),  # Bottom right
                       (- self.turretWidth // 2, self.turretWidth // 2)]  # Bottom left
        # Generate the actual points of the hull from the unit square points
        deltaX = -self.x + screenWidth // 2  # The amount we must offset objects so that they are rendered in the right location
        deltaY = -self.y + screenHeight // 2
        self.hullPoints = [[self.hull[i][0], self.hull[i][1]] for i in range(len(self.hull))]
        self.turretPoints = [[self.turret[i][0], self.turret[i][1]] for i in range(len(self.turret))]

    # Checks for collisions due to movement
    def checkForCollisions(self, entities, gameMap):
        self.uuidDeleteList = []  # Clear the uuid delete list
        self.messageList = []
        indexDeleteList = []  # List of entities to be deleted by their index in the entity list
        applyXVelocity = True
        applyYVelocity = True

        # These two loops compare all the entities in the game in the most efficient way
        for i in range(len(entities)):
            for j in range(i+1, len(entities)):

                if entities[i].type == "projectile" and entities[j].type == "projectile" and self.isHost:
                    # If the projectiles are touching (using pythagoras' theorem)
                    if (self.isHost and entities[i].x - entities[j].x)**2 + (entities[i].y - entities[j].y)**2 < (entities[i].sizeX//2)**2:
                        indexDeleteList.append(i)  # Destroy both projectiles
                        indexDeleteList.append(j)

                # If we are comparing our projectile and an enemy tank
                elif (entities[i].type == "projectile" and entities[i].owner.uuid == self.player.uuid and entities[j].type == "tank" and entities[j].team != self.team) or (entities[j].type == "projectile" and entities[j].owner.uuid == self.player.uuid and entities[i].type == "tank" and entities[i].team != self.team):
                    # If they are touching in the x plane
                    touchingX = entities[i].x + (entities[i].sizeX // 2) >= entities[j].x - (entities[j].sizeX // 2) and entities[i].x - (entities[i].sizeX // 2) <= entities[j].x + (entities[j].sizeX // 2)
                    # If they are touching in the y plane
                    touchingY = entities[i].y + (entities[i].sizeY // 2) >= entities[j].y - (entities[j].sizeY // 2) and entities[i].y - (entities[i].sizeY // 2) <= entities[j].y + (entities[j].sizeY // 2)
                    # TODO improve using SAT
                    if touchingX and touchingY:
                        # TODO figure out what AI tanks should do here
                        if not self.isHost:
                            message = "|!RD!"  # Add the "request destroy flag"
                            message += entities[i].uuid + " " + entities[j].uuid  # Add the uuids of the 2 entities in question
                            message += "!RD!|"
                            self.messageList.append(message)
                        else:
                            indexDeleteList.append(i)  # Remove the projectile
                            indexDeleteList.append(j)  # Remove the tank

                # If we are comparing our tank and another tank
                elif (entities[i].type == "tank" and entities[i].player == self.player and entities[j].type == "tank") or (entities[j].type == "tank" and entities[j].player == self.player and entities[i].type == "tank"):
                    self.x += self.velocityX  # Apply the movement for this tick
                    # If applying this movement causes a collision
                    if self.tanksColliding(entities[i], entities[j]):
                        applyXVelocity = False  # Remove the movement
                    self.x -= self.velocityX  # Remove the movement afterwards

                    # Doing the same for the y-axis
                    self.y += self.velocityY
                    # If applying this movement causes a collision
                    if self.tanksColliding(entities[i], entities[j]):
                        applyYVelocity = False  # Remove the movement
                    self.y -= self.velocityY  # Remove the movement afterwards

                    # Now we must test whether applying both together causes a collision
                    self.x += self.velocityX
                    self.y += self.velocityY
                    if self.tanksColliding(entities[i], entities[j]):
                        self.y -= self.velocityY
                        # Determining whether a collision is caused after applying the X velocity
                        touchingAfterX = self.tanksColliding(entities[i], entities[j])
                        self.y += self.velocityY
                        # Determining whether a collision is caused after applying the Y velocity
                        touchingAfterY = self.tanksColliding(entities[i], entities[j])
                        # If applying the y velocity causes the collision we can apply the X velocity
                        if not touchingAfterX and touchingAfterY:
                            applyYVelocity = False
                        else:
                            # Otherwise the X velocity must cause the collision so we don't apply that
                            applyXVelocity = False
                    self.x -= self.velocityX
                    self.y -= self.velocityY

        filteredDeleteList = []  # Represents the delete list without duplicates
        for index in indexDeleteList:  # Remove any duplicates
            if index not in filteredDeleteList:
                filteredDeleteList.append(index)
        filteredDeleteList.sort(reverse=True)  # Sort the list backwards to avoid index out of bounds errors

        for index in filteredDeleteList:
            self.uuidDeleteList.append(entities[index].uuid)  # Add the uuid to the delete list
            del entities[index]  # Delete the entity

        # Checking for OUR tank collisions against boundaries
        bnds = gameMap.boundaryList
        for x in range(len(bnds)):
            self.x += self.velocityX  # Temporarily apply the movement
            # If the tank is now touching the boundary
            if self.tankCollidingBoundary(self, bnds[x]):
                applyXVelocity = False  # Cancel the x velocity as it will cause an intersection
            self.x -= self.velocityX

            # Now checking whether the y velocity could cause an intersection
            self.y += self.velocityY  # Temporarily apply the movement
            if self.tankCollidingBoundary(self, bnds[x]):
                applyYVelocity = False  # Cancel the y velocity as it will cause an intersection
            self.y -= self.velocityY  # Remove the velocity

            # Now we must test whether applying both together causes a collision
            self.x += self.velocityX
            self.y += self.velocityY
            if self.tankCollidingBoundary(self, bnds[x]):
                self.y -= self.velocityY
                # Determining whether a collision is caused after applying the X velocity
                touchingAfterX = self.tankCollidingBoundary(self, bnds[x])
                self.y += self.velocityY
                # Determining whether a collision is caused after applying the Y velocity
                touchingAfterY = self.tankCollidingBoundary(self, bnds[x])
                # If applying the y velocity causes the collision we can apply the X velocity
                if not touchingAfterX and touchingAfterY:
                    applyYVelocity = False
                else:
                    # Otherwise the X velocity must cause the collision so we don't apply that
                    applyXVelocity = False
            self.x -= self.velocityX
            self.y -= self.velocityY

        return applyXVelocity, applyYVelocity

    # Method takes in 2 tanks and returns whether they are colliding or not
    def tanksColliding(self, tank1, tank2):
        return tank1.x + (tank1.sizeX // 2) >= tank2.x - (tank2.sizeX // 2) and tank1.x - (
                    tank1.sizeX // 2) <= tank2.x + (tank2.sizeX // 2) and tank1.y + (
                    tank1.sizeY // 2) >= tank2.y - (tank2.sizeY // 2) and tank1.y - (
                    tank1.sizeY // 2) <= tank2.y + (tank2.sizeY // 2)

    # Method which takes in a tank and a boundary and returns whether they are colliding or not
    def tankCollidingBoundary(self, tank, bound):
        if bound.boundType == "vertical":  # Dealing with a vertical boundary
            return tank.x - (tank.sizeX // 2) <= bound.x <= tank.x + (tank.sizeX // 2) and tank.y - (tank.sizeY // 2) <= bound.maxY and tank.y + (tank.sizeY // 2) >= bound.minY
        else:  # Dealing with a horizontal boundary
            return tank.y - (tank.sizeY // 2) <= bound.y <= tank.y + (tank.sizeY // 2) and tank.y - (tank.sizeY // 2) <= bound.maxX and tank.y + (tank.sizeY // 2) >= bound.minX

