# TODO make projectile detection better
import math
import tank
import tankConstants
import pygame


# Class which represents an AI tank
class AITank(tank.Tank):
    def __init__(self, player, x, y, screenWidth, screenHeight):
        super().__init__(x, y, player, "tank", screenWidth, screenHeight, False)  # Pass args to super class

    # Processes everything to do with the tank
    def tickAITank(self, entityList, gameMap):
        moveVector = self.getMoveVector(entityList, gameMap)  # Get the move vector for this tick
        moveVector[0] = -moveVector[0]  # Rotate the move vector by 180 degrees
        moveVector[1] = -moveVector[1]

        self.addedRotation = 0
        if moveVector[0] == 0 and moveVector[1] == 0:  # No danger in immediate area
            self.moveForward(entityList, gameMap)
        else:
            if moveVector[1] == 0:
                # Prevent dividing by zero
                movementRotation = 270 if moveVector[0] < 0 else 90
            else:
                # Find the rotation of the movement vector (add 180 as up is negative)
                movementRotation = math.atan(math.radians(abs(moveVector[0] / moveVector[1])))
                # Depending on the quadrant find the correct bearing
                if moveVector[0] >= 0 and moveVector[1] >= 0:
                    movementRotation = 90 + movementRotation
                elif moveVector[0] <= 0 and moveVector[1] <= 0:
                    movementRotation = 360 - movementRotation
                elif moveVector[0] <= 0 and moveVector[1] >= 0:
                    movementRotation = 180 + movementRotation
            if abs(self.rotation - movementRotation) < 20:  # If the tank is roughly at the desired rotation, move the tank forward
                self.moveForward(entityList, gameMap)  # Move the tank forward
            # Rotate towards the target rotation
            if self.rotation > movementRotation:
                # Rotate anti-clockwise
                self.rotation -= self.rotationSpeed  # Rotate the tank by the rotation speed
                self.rotation = self.rotation % 360
                self.addedRotation = -self.rotationSpeed
            else:
                # Rotate the tank clockwise
                self.rotation += self.rotationSpeed  # Rotate the tank by the rotation speed
                self.rotation = self.rotation % 360
                self.addedRotation = self.rotationSpeed

    # Gets the average direction and distance of all the threats on the map to the tank
    def getMoveVector(self, entityList, gameMap):
        moveVectorX = 0
        moveVectorY = 0
        dangerDist = 200
        for ent in entityList:
            if ent.type == "projectile" and ent.owner.team != self.team:
                intersectionX, intersectionY = (0, 0)
                if ent.velocityX == 0:  # Prevents dividing by zero when finding the intersection
                    intersectionX = ent.x
                    intersectionY = self.y
                else:
                    grad = ent.velocityY / ent.velocityX
                    intersectionX = (grad * ent.x - ent.y + (self.x / grad) + self.y) / (grad + (1 / grad))
                    intersectionY = grad * (intersectionX - ent.x) + ent.y
                    # The above lines find the shortest path from the tank to the projectile's path via substitution
                    # This is so we can find the shortest distance from the tank to the projectile

                if (self.x - intersectionX) ** 2 + (self.y - intersectionY) ** 2 < dangerDist ** 2:
                    # If the shortest distance to the projectile's path is less than 20
                    if intersectionX - self.x < 0:  # Finding the 2d vector from the tank to the bullet's path
                        moveVectorX -= dangerDist + (intersectionX - self.x)
                    elif intersectionX - self.x > 0:
                        moveVectorX += dangerDist - (intersectionX - self.x)
                    # Adjusting the size of the direction vector based on how far the danger is
                    if intersectionY - self.y < 0:
                        moveVectorY -= dangerDist + (intersectionY - self.y)
                    elif intersectionY - self.y > 0:
                        moveVectorY += dangerDist - (intersectionY - self.y)
                    if intersectionX - self.x == 0 and intersectionY - self.y == 0:  # If they are both zero
                        moveVectorX += 20
                        moveVectorY += 20
            elif ent.type == "tank" and ent.team != self.team:
                dist = math.sqrt((ent.x - self.x) ** 2 + (ent.y - self.y) ** 2)  # Finding the distance between the 2 tanks
                if dist < dangerDist:  # If the distance between the 2 tanks is less than 20
                    if ent.x - self.x < 0:
                        moveVectorX -= dangerDist + (ent.x - self.x)  # same as with projectiles above
                    elif ent.x - self.x > 0:
                        moveVectorX += dangerDist - (ent.x - self.x)
                    # Adjusting the size of the direction vector based on how far the danger is
                    if ent.y - self.y < 0:
                        moveVectorY -= dangerDist + (ent.y - self.y)
                    elif ent.y - self.y > 0:
                        moveVectorY += dangerDist - (ent.y - self.y)
        for bound in gameMap.boundaryList:
            # Finds the point on the boundary closest to the tank
            point = self.getShortestPointToBoundary(bound)
            if (point[0] - self.x) ** 2 + (point[1] - self.y) ** 2 < dangerDist ** 2:
                deltaX = point[0] - self.x  # Finding the distance between the 2 points on the boundary and tank
                deltaY = point[1] - self.y
                if deltaX < 0:
                    moveVectorX -= dangerDist + deltaX
                elif deltaX > 0:
                    moveVectorX += dangerDist - deltaX
                if deltaY < 0:
                    moveVectorY -= dangerDist + deltaY
                elif deltaY > 0:
                    moveVectorY += dangerDist - deltaY
        return [moveVectorX, moveVectorY]

    def getShortestPointToBoundary(self, bound):
        if bound.boundType == "vertical":
            # Finding the closest distance from the tank to an infinitely long boundary
            closestY = self.y
            if closestY <= bound.minY:
                # IF the tank's Y value is less than the boundary's minimum value the closest point must be the boundary's minimum value
                closestY = bound.minY
            elif closestY >= bound.maxY:
                # If the tank's Y value is past the max boundary Y the closest Y value is the boundary's max Y value
                closestY = bound.maxY
            return [bound.x, closestY]
        else:  # Dealing with a horizontal boundary
            # Same as with a vertical boundary but rotated 180 degrees in the x plane
            closestX = self.x
            if closestX <= bound.minX:
                closestX = bound.minX
            elif closestX >= bound.maxX:
                closestX = bound.maxX
            return [closestX, bound.y]

    def moveForward(self, entityList, gameMap):
        yMove = -1
        # Rotating the tank's movement with respect to its rotation
        theta = self.rotation
        self.velocityX = -math.sin(math.radians(theta)) * yMove * self.moveSpeed  # change the velocity for this tick
        self.velocityY = math.cos(math.radians(theta)) * yMove * self.moveSpeed
        # Check for any collisions that could happen when applying the velocity
        xVel, yVel = self.checkForCollisions(entityList, gameMap)
        if xVel:  # Apply the velocities if they don't cause collisions
            self.x += self.velocityX
        if yVel:
            self.y += self.velocityY

    def renderTank(self, surface, offset=(0, 0)):  # Method to easily render a tank anywhere on the screen
        if self.addedRotation != 0:  # If rotation has been added this tick generate the new points (to avoid lots of maths each tick)
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
        self.textX = self.x + offset[0] - (self.sizeX / 2)
        self.textY = self.y + offset[1] - self.sizeX - self.turretHeight - (self.textHeight / 2)
        surface.blit(self.nameSurface, (self.textX, self.textY))
