import ctypes
import pygame
import gameScreen
import inputUtils
import mainMenuScreen
import serverGameScreen


pygame.init()  # Initialises pygame's modules

name = "Tanks"  # The name of the window/game


ctypes.windll.user32.SetProcessDPIAware()  # Allows us to gather information about the user's screen
# Gets the width and height of the users monitor
sWidth, sHeight = int(ctypes.windll.user32.GetSystemMetrics(0)), int(ctypes.windll.user32.GetSystemMetrics(1) * 0.95)
# We take 5% off the height to show the task bar and window navigation buttons

surface = pygame.display.set_mode((sWidth, sHeight), pygame.RESIZABLE)  # Launches window of with our gathered sizes
# Screen is also set to the surface of the display for us to manipulate
pygame.display.set_caption(name)  # Sets the name of the window to "Tanks"
surface.fill((255, 255, 255))  # Fills the surface with white
pygame.display.update()  # Updates the display to show our changes

inputObj = inputUtils.Input()  # Creating an input object so we can use its methods

mMScreen = mainMenuScreen.MainMenu(sWidth, sHeight)  # Creates a new main menu screen
currentScreen = mMScreen  # Assigns the main menu screen to the current screen variable

lastTick = pygame.time.get_ticks()
tooLongTicks = 0
targetFPS = 40
notifyOnLongTick = True

# Main program loop
while not currentScreen.shouldClose:
    timeBetween = pygame.time.get_ticks() - lastTick
    if timeBetween > 1000/targetFPS:  # If the time between tick is greater than our desired times between ticks
        tooLongTicks += 1  # Increment the number of too long ticks that have occurred
        if notifyOnLongTick:
            print("Tick took longer than desired for the " + str(tooLongTicks) + " time")
    if isinstance(currentScreen, gameScreen.GameScreen) and currentScreen.thisTank.isHost:  # If we are the host
        while timeBetween < 1000/targetFPS:  # While it has been less than 33 milliseconds since the last tick don't tick
            timeBetween = pygame.time.get_ticks() - lastTick  # Update the time since last tick
        lastTick = pygame.time.get_ticks()  # Update the time of the last tick for the next tick

    # Gather user input and handle events, if a screen needs to be changed the screen is returned and set to current screen
    result = inputObj.handleEvents(currentScreen.getButtons(), currentScreen.captureKeyboard, currentScreen.getButtons()[currentScreen.focusedInput] if currentScreen.captureKeyboard else None)
    if result is not None and result[0] is not None:  # If null is not returned    
        if result[0] == pygame.WINDOWCLOSE:  # If window should be closed, we break out of the loop
            currentScreen.shouldClose = True
            break
        elif result[1] == "newScreen":  # If handleEvents() has returned something else it must be a new screen to swap to
            currentScreen = result[0]
        elif result[1] == "removeUser":
            currentScreen.removeUser(result[0])
            
    # If the keyboard has been captured in the current frame, tell the current focused input object to update its contents
    if currentScreen.captureKeyboard:
        currentScreen.getButtons()[currentScreen.focusedInput].updateInput(currentScreen)
    if inputObj.stopCaptureKeyboard:  # If a focused input box has been unfocused we stop capturing all keyboard input
        inputObj.stopCaptureKeyboard = False
        currentScreen.captureKeyboard = False
        currentScreen.getButtons()[currentScreen.focusedInput].isFocused = False
    if isinstance(currentScreen, gameScreen.GameScreen):  # If we are in the game screen
        # Tick the player tank
        res = currentScreen.thisTank.tickPlayerTank(inputObj.input, currentScreen.entityList, currentScreen.gameMap)
        # Add any new projectiles
        if res is not None:
            if res[1] == "newProj":
                currentScreen.processShooting(res[0])

    surface.fill((255, 255, 255))  # Clear the screen
    renderResult = currentScreen.renderScreen(surface)  # Renders the current screen object onto the surface/user's window
    if renderResult is not None:  # Incase a new screen is returned
        if renderResult[1] == "New screen":
            currentScreen = renderResult[0]  # Set the new screen, only used with clientLobbyScreen as tick is called in render
    pygame.display.update()  # Updates the display so we can see our surface

pygame.quit()  # Closes all of pygame's modules


