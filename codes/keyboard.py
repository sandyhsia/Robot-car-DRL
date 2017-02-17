import pygame
from pygame.locals import *
from sys import exit

pygame.init()

while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			exit()
		elif event.type == KEYDOWN:
			if event.key == K_a:
				print "K_a"
			elif event.key == K_RIGHT:
				print "K_right"
		elif event.type == KEYUP:
			print "stopping"