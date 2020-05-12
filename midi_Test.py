import pygame.midi
import time

pygame.midi.init()
player = pygame.midi.Output(1)
# player.set_instrument(0)
player.note_on(64, 64)
time.sleep(1)
player.note_off(64, 64)
del player
pygame.midi.quit()