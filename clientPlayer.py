import math
import pygame
import tank
import projectile
import tankConstants


# This class represents a real player's tank on the game Screen
# An instance of the player class from the createGameScreen file should be passed to the object in the constructor
class ClientPlayer(tank.Tank):
    def __init__(self, player, x, y, screenWidth, screenHeight, isHost):
        super().__init__(x, y, player, "tank", screenWidth, screenHeight, isHost)
        self.ip = player.ip

    # Method called every tick on every player tank to process its input and movement etc
    def tickPlayerTank(self, inpDict, entityList, gameMap):
        result = None
        self.handleRotationInput(inpDict)  # Handling rotation input
        self.handleMovementInput(inpDict, entityList, gameMap)
        if inpDict[pygame.K_SPACE]:  # If the space key is pressed
            if self.shootCooldown <= 0 and self.isAlive:
                proj = self.shoot()  # Shoot
                result = (proj, self.rotation, self.player.uuid), "newProj"
                self.shootCooldown = 40  # Reset the shoot cooldown
        if self.shootCooldown > 0:  # If shoot still on cooldown, decrement the cooldown
            self.shootCooldown -= 1
        return result

    # Method which handles user input with respect to tank movement
    def handleMovementInput(self, inpDict, entityList, gameMap):  # Setting a default movement speed
        yMove = 0
        if inpDict[pygame.K_w]:
            yMove -= 1  # If W key pressed move forward
        if inpDict[pygame.K_s]:
            yMove += 1  # If S key pressed move backwards

        # Rotating the tank's movement with respect to its rotation
        theta = self.rotation
        self.velocityX = -math.sin(math.radians(theta)) * yMove * self.moveSpeed
        self.velocityY = math.cos(math.radians(theta)) * yMove * self.moveSpeed

        # Check for any collisions that could happen when applying the velocity
        xVel, yVel = self.checkForCollisions(entityList, gameMap)
        if xVel:  # Apply the velocities if they don't cause collisions
            self.x += self.velocityX
        if yVel:
            self.y += self.velocityY

    # Handles rotation input of the tank
    def handleRotationInput(self, inpDict):
        rotationSpeed = self.rotationSpeed  # Rendering at 30 FPS causes the tank to rotate 360 degrees in 6 seconds
        self.addedRotation = 0
        if inpDict[pygame.K_d]:
            self.addedRotation += 1  # If d is pressed rotate the tank to the right
        if inpDict[pygame.K_a]:
            self.addedRotation -= 1  # If a is pressed rotate to the left
        self.rotation += self.addedRotation * rotationSpeed  # Rotate the tank by the calculated amount
        self.rotation = self.rotation % 360

    #  Method called whenever the user presses the space bar and shoots a projectile
    def shoot(self):
        return projectile.Projectile(self.x, self.y, self.rotation, self.ip, self.player)

    def renderTank(self, surface, offset=(0, 0)):  # Method to easily render a tank anywhere on the screen
        # if self.addedRotation != 0:  # If rotation has been added this tick generate the new points
        #     self.hullPoints = [[self.hull[i][0] * math.cos(math.radians(self.rotation)) - self.hull[i][1] * math.sin(math.radians(self.rotation)) + self.x + offset[0], self.hull[i][1] * math.cos(math.radians(self.rotation)) + self.hull[i][0] * math.sin(math.radians(self.rotation)) + self.y + offset[1]] for i in range(len(self.hull))]
        #     self.turretPoints = [[self.turret[i][0] * math.cos(math.radians(self.rotation)) - self.turret[i][1] * math.sin(math.radians(self.rotation)) + self.x + offset[0], self.turret[i][1] * math.cos(math.radians(self.rotation)) + self.turret[i][0] * math.sin(math.radians(self.rotation)) + self.y + offset[1]] for i in range(len(self.turret))]
        # pygame.draw.aalines(surface, tankConstants.colourList[self.team - 1], True, self.hullPoints)  # Render the tank's hull
        # pygame.draw.aalines(surface, tankConstants.colourList[self.team - 1], True, self.turretPoints)  # Render the turret
        # # Render the hatch
        # pygame.draw.circle(surface, tankConstants.colourList[self.team - 1], (self.x + offset[0], self.y + offset[1]), self.hatchRadius)
        # surface.blit(self.nameSurface, (self.textX, self.textY))

        # If rotation has been added this tick generate the new points (to avoid lots of maths each tick)
        self.hullPoints = [[self.hull[i][0] * math.cos(math.radians(self.rotation)) - self.hull[i][1] * math.sin(math.radians(self.rotation)), self.hull[i][1] * math.cos(math.radians(self.rotation)) + self.hull[i][0] * math.sin(math.radians(self.rotation))] for i in range(len(self.hull))]
        self.turretPoints = [[self.turret[i][0] * math.cos(math.radians(self.rotation)) - self.turret[i][1] * math.sin(math.radians(self.rotation)), self.turret[i][1] * math.cos(math.radians(self.rotation)) + self.turret[i][0] * math.sin(math.radians(self.rotation))] for i in range(len(self.turret))]

        hull = []
        turret = []

        for i in range(len(self.hullPoints)):   # Add the offsets
            hull.append([self.hullPoints[i][0] + self.x + offset[0], self.hullPoints[i][1] + self.y + offset[1]])
            turret.append([self.turretPoints[i][0] + self.x + offset[0], self.turretPoints[i][1] + self.y + offset[1]])

        pygame.draw.aalines(surface, tankConstants.colourList[self.team - 1], True, hull)  # Render the tank's hull
        pygame.draw.aalines(surface, tankConstants.colourList[self.team - 1], True, turret)  # Render the turret
        # Render the hatch
        pygame.draw.circle(surface, tankConstants.colourList[self.team - 1], (self.x + offset[0], self.y + offset[1]), self.hatchRadius)
        self.textX = self.x + offset[0] - (self.textWidth / 2)
        self.textY = self.y + offset[1] - self.sizeX - self.turretHeight - (self.textHeight / 2)
        surface.blit(self.nameSurface, (self.textX, self.textY))
