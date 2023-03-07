import socket

def remove(arr):
    del arr[3]

# # Decodes a string after transmission and returns the player list
# def decodePlayers(code):
#     playerList = []
#     players = code.split(" ")  # Split by double space to get each player
#     for player in players:
#         attributes = player.split(" ")  # Get all the attributes
#         # Create a new player from the attributes
#         p = Player(attributes[0], int(attributes[1]), True if attributes[2] == 1 else False, attributes[3])
#         playerList.append(p)  # Add the player to the player list
#     return playerList
#
#
# class Player:
#     def __init__(self, name, team, Ai=False, ip=None):
#         self.Ai = Ai
#         self.name = name
#         self.team = team
#         self.ip = ip
#




