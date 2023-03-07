import pygame


# This class contains several methods and classes to help render, store and interact with the map as well as the map itself
class Boundary:  # A superclass which both types of boundaries inherit from, should never be called by anythin else
    def __init__(self, boundType):
        self.boundType = boundType


# Class representing a vertical boundary
class VerticalBoundary(Boundary):
    def __init__(self, x, minY, maxY):
        super().__init__("vertical")
        self.x = x
        self.minY = minY
        self.maxY = maxY
        
    def getStartPoint(self):  # Returns the co-ordinates of the start point of the boundary
        return [self.x,  self.minY]
    
    def getEndPoint(self):  # Returns the co-ordinates of the end point of the boundary
        return [self.x, self.maxY]


# Class representing a horizontal boundary
class HorizontalBoundary(Boundary):
    def __init__(self, y, minX, maxX):
        super().__init__("horizontal")
        self.y = y
        self.minX = minX
        self.maxX = maxX
    
    def getStartPoint(self):  # Returns the co-ordinates of the start point of the boundary
        return [self.minX, self.y]
    
    def getEndPoint(self):  # Returns the co-ordinates of the end point of the boundary
        return [self.maxX, self.y]


class Map:
    def __init__(self, boundaryList):
        self.backgroundSurface = pygame.image.load("BackgroundImage.png")
        self.boundaryList = boundaryList

        self.lines = []
        for i in range(100, 2000, 100):
            self.lines.append([(i, 0), (i, 2000)])  # Generate the background lines parallel to the y axis
            self.lines.append([(0, i), (2000, i)])  # Generate the background lines parallel to the x axis
        
    def render(self, surface, offset=(0, 0)):
        # draw background image/gridlines
        for line in self.lines:
            pygame.draw.line(surface, (220, 220, 220), (line[0][0] + offset[0], line[0][1] + offset[1]), (line[1][0] + offset[0], line[1][1] + offset[1]))

        for i in range(len(self.boundaryList)):
            start = self.boundaryList[i].getStartPoint()
            end = self.boundaryList[i].getEndPoint()
            start[0] += offset[0]  # Adding the offset before rendering
            start[1] += offset[1]
            end[0] += offset[0]
            end[1] += offset[1]
            pygame.draw.aaline(surface, (0, 0, 0), start, end)


def getMap():
    v1 = VerticalBoundary(0, 0, 2000)
    v2 = VerticalBoundary(2000, 0, 2000)
    h1 = HorizontalBoundary(0, 0, 2000)
    h2 = HorizontalBoundary(2000, 0, 2000)
    li = [v1, v2, h1, h2]
    gameMap = Map(li)
    return gameMap


