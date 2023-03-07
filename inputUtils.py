# This file includes classes and methods which are useful for gathering and processing user input
import pygame
from screen import Screen
from userList import userListEntry


class Input:
    # This dictionary stores the state of several useful keys where the value True indicates the key is pressed
    input = {
        pygame.K_w: False,
        pygame.K_a: False,
        pygame.K_s: False,
        pygame.K_d: False,
        pygame.K_SPACE: False
    }

    # This function handles user input events
    # If the screen should change it returns the new screen
    # If the screen should close it returns pygame.WINDOWCLOSE
    # If no extra action needs to be taken it returns None
    def __init__(self):
        self.stopCaptureKeyboard = None

    def handleEvents(self, buttons, captureKeyboard, inputBox):
        # If an input box is hovered we only care if the alphanumeric, backspace and enter keys have been pressed
        # Additionally if the mouse button is pressed outside of the button we should stop capturing input
        if captureKeyboard:
            event = pygame.event.poll()  # Pygame stores events in a queue which we must remove and process ourselves
            while event.type != pygame.NOEVENT:  # Cycles through every event in the queue until there are none left
                if event.type == pygame.KEYDOWN:  # If a key was pressed
                    if event.key == pygame.K_SPACE:  # If space is pressed add a blank character
                        inputBox.textInput += " "
                    elif event.key == pygame.K_BACKSPACE:
                        inputBox.textInput = inputBox.textInput[:-1]  # If backspace pressed remove the last character
                    elif event.key == pygame.K_RETURN:  # If enter pressed de focus the input box
                        self.stopCaptureKeyboard = True  # Stop capturing keyboard
                        return None
                    # If the key is alphanumeric character
                    elif pygame.K_0 <= event.key <= pygame.K_9 or pygame.K_a <= event.key <= pygame.K_z:
                        if event.mod & pygame.KMOD_SHIFT or event.mod & pygame.KMOD_CAPS:
                            # If shift or caps lock pressed add an upper case character
                            inputBox.textInput += pygame.key.name(event.key).upper()
                        else:
                            inputBox.textInput += pygame.key.name(event.key)
                    elif event.key == pygame.K_PERIOD:
                        inputBox.textInput += "."  # If the full stop key is pressed, add it, to allow IP entry
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # If mouse button pressed de focus the input box
                    self.stopCaptureKeyboard = True  # Stop capturing keyboard
                    return None
                elif event.type == pygame.WINDOWCLOSE:  # User is closing the window
                    return [pygame.WINDOWCLOSE, "closeWindow"]
                event = pygame.event.poll()  # Get the next event ready for the next loop
        else:
            event = pygame.event.poll()  # Pygame stores events in a queue which we must remove and process ourselves
            while event.type != pygame.NOEVENT:  # Cycles through every event in the queue until there are none left
                if event.type == pygame.KEYDOWN:  # If the event is a key down event we set the corresponding key to true
                    if event.key in self.input:  # Checking whether the key is useful to us i.e. in the input dictionary
                        self.input[event.key] = True  # Set the corresponding key to be pressed

                elif event.type == pygame.KEYUP:  # If the event is a key up event we set the corresponding key to false
                    if event.key in self.input:  # Checking # Checking whether the key is useful to us i.e. in the input dictionary
                        self.input[event.key] = False

                elif event.type == pygame.MOUSEBUTTONDOWN:  # If one of the mouse buttons has been pressed
                    if event.button == 1:  # If the left mouse button has been pressed
                        mousePos = pygame.mouse.get_pos()  # Returns a tuple with the mouse position on the screen
                        for button in buttons:  # Cycles through every button currently on the screen
                            if button.isPressed(mousePos):  # Checks whether the mouse is over each button
                                result = button.runAction()  # If the mouse is over the button we run its action
                                if isinstance(result, Screen):
                                    return [result, "newScreen"]  # If it returns a new screen inform the main function to swap the screen
                                elif isinstance(result, userListEntry):
                                    # If a user is returned then inform the main function to remove them from the game
                                    return [result.player, "removeUser"]
        
                elif event.type == pygame.WINDOWCLOSE:
                    return [pygame.WINDOWCLOSE, "closeWindow"]

                event = pygame.event.poll()  # Get the next event ready for the next loop

        return [None, "null"]






