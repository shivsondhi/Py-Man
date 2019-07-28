'''
PACMAN Game!
First Final Draft.
'''

import pygame
import sys
import random
import time


# Declaring all constants
# general variables
FPS = 5
LIVES = 3
SCORE = 0

# general dimesnions
WINDOWWIDTH 	= 700
WINDOWHEIGHT 	= 820
CELLSIZE 		= 25
BORDERX 		= 25
BORDERY 		= 35
sprite_dims 	= (45, 45)				# (x, y)
logo_topcoords 	= [0, 0] 				# PACMAN "logo"
logo_botcoords 	= [0, 0]


# assert that window and game dimensions don't create any problems for the code
assert (WINDOWWIDTH - (2*BORDERX)) / CELLSIZE == 26, 'Error 101 - Make sure that the width of the main game area (excluding borders) is big enough for 30 cells of size=CELLSIZE.'
assert (WINDOWHEIGHT - (2*BORDERY)) / CELLSIZE == 30, 'Error 102 - Make sure that the height of the main game area (excluding borders) is big enough for 26 cells of size=CELLSIZE'
assert (sprite_dims[0] - (2*CELLSIZE)) <= 0, 'Error 201 - Sprite width is too big relative to the CELLSIZE. Please make sure the sprites are at most two times the CELLSIZE.'
assert (sprite_dims[1] - (2*CELLSIZE)) <= 0, 'Error 202 - Sprite height is too big relative to the CELLSIZE. Please make sure the sprites are at most two times the CELLSIZE.'


# color codes	=	(  R,   G,   B, alpha)
WHITE 			= 	(255, 255, 255)									# used for most text
GREEN_SEA 		= 	( 22, 160, 133)									# game background
LIGHTGREEN_SEA	= 	( 25, 182, 152)									# grid line color
BLACK 			= 	(  0,   0,   0)									# alternate background color
LIGHTGRAY 		= 	(236, 240, 241)									# alternate grid line color
SAND 			= 	(194, 178, 128)									# wall color light
DARKSAND		= 	(166, 145,  80)									# wall color dark
YELLOW 			= 	(241, 196,  15)									# food color
RED 			= 	(192,  57,  43)									# food color
PURPLE 			= 	(162, 155, 254)									# PACMAN background color
PINK 			= 	(252,  66, 123)									# PACMAN font color
BLINK_COLOR 	= 	(129, 236, 236)									# win animation alternate color
DARKRED 		= 	(179,  57,  57, 225)							# display message background color


# sprite image paths
SPRITES_DICT 	= 	{ 'pacman' 		: pygame.image.load("Media\\pacman.png"),
					  'ghost_red'	: pygame.image.load("Media\\ghost1.png"),
					  'ghost_green' : pygame.image.load("Media\\ghost2.png"),
					  'ghost_blue'	: pygame.image.load("Media\\ghost3.png"),
					  'cherries'	: pygame.image.load("Media\\cherry.png")
					}


def main():
	global DISPLAYSURF, FPSCLOCK, LOGOFONT, STATFONT, INSTFONT, gameSTART, GRID

	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	# the main game Surface 
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
	# define fonts of different sizes
	LOGOFONT = pygame.font.Font('freesansbold.ttf', 50)				# Big font for PACMAN logo and Game Won / Over messages
	STATFONT = pygame.font.Font('freesansbold.ttf', 15)				# Small font for score and lives meters
	INSTFONT = pygame.font.Font('freesansbold.ttf', 25)				# Medium font for game instructions

	# global game variables
	gameSTART = False
	GRID = False													# GRID controls the background style of the game

	getStartScreen()
	# main game loop
	gameLoop()


def gameLoop():
	'''
	This function contains the main game loop within which the entire game runs.
	'''
	global GRID, gameSTART, IMMORTAL, startTIME

	# sets to True for  seconds immediately after pacman loses a life
	IMMORTAL = False

	# main game loop
	while True:
		# get all events from the event queue
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				# shut window if the cross button is clicked
				terminate()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_s and not gameSTART:				# START GAME W/O GRID
					# s to start the game level w/o
					GRID = False
					gameSTART = True								# gets set once the countdown is finished
					# get initial pacman and ghost data
					sprites = startGame()
					# original state of the map, remains constant
					origin_state = getCountdownScreen(sprites['pacman'])
					# current state of the map, keeps updating
					current_state = deep_copy(origin_state)
				elif event.key == pygame.K_g and not gameSTART:				# START GAME W GRID
					# g to start the game level w GRID
					# More or less same as game start 
					GRID = True
					gameSTART = True
					sprites = startGame()
					origin_state = getCountdownScreen(sprites['pacman'])
					current_state = deep_copy(origin_state)
				elif (event.key == pygame.K_r) and gameSTART:				# RESTART GAME
					# r to restart the game from countdown 
					# only if the game has started
					# more or less same as game start
					sprites = startGame()
					origin_state = getCountdownScreen(sprites['pacman'])
					current_state = deep_copy(origin_state)
				elif event.key == pygame.K_p and gameSTART:					# PAUSE GAME
					# p to pause the game
					# only works if the game has started
					getPauseScreen(current_state, sprites['pacman'])
				elif event.key == pygame.K_q:								# QUIT GAME
					# t to go back to title screen
					GRID = False
					gameSTART = False								# this is correctly placed
					getStartScreen()
				
				# check if any of the direction keys have been pressed after game has started
				elif event.key == pygame.K_LEFT and gameSTART:
					# left key pressed -> store pacman's current direction and if legit, change current direction to left
					if sprites['pacman'][0] not in ("left", "right") and isLegitMove("left", 1, current_state):
						if sprites['pacman'][0] is not None:					# this is used so that the previous state is never set to None
							sprites['pacman'][4] = sprites['pacman'][0]
						sprites['pacman'][0] = "left"
				elif event.key == pygame.K_RIGHT and gameSTART:
					# right key pressed -> store pacman's current direction and if legit, change current direction to right
					if sprites['pacman'][0] not in ("right", "left") and isLegitMove("right", 1, current_state):
						if sprites['pacman'][0] is not None:
							sprites['pacman'][4] = sprites['pacman'][0]
						sprites['pacman'][0] = "right"
				elif event.key == pygame.K_UP and gameSTART:
					# up key pressed -> store pacman's current direction and if legit, change current direction to up
					if sprites['pacman'][0] not in ("up", "down") and isLegitMove("up", 1, current_state):
						if sprites['pacman'][0] is not None:
							sprites['pacman'][4] = sprites['pacman'][0]
						sprites['pacman'][0] = "up"
				elif event.key == pygame.K_DOWN and gameSTART:
					# down key pressed -> store pacman's current direction and if legit, change current direction to down
					if sprites['pacman'][0] not in ("down", "up") and isLegitMove("down", 1, current_state):
						if sprites['pacman'][0] is not None:
							sprites['pacman'][4] = sprites['pacman'][0]
						sprites['pacman'][0] = "down"						
				
				elif event.key == pygame.K_ESCAPE:
					# if ESC key pressed, shut the game window
					terminate()

		# moving around the sprites if the game has started
		if gameSTART:
			# move pacman and the ghosts and update the map
			current_state = gameplay(current_state, sprites)
			# check if the game has been won -> display the winning screen
			if gameWon(current_state):
				winAnimation(current_state, sprites['pacman'])
			# check if pacman has lost all lives -> display the losing screen
			if sprites['pacman'][3] == 0:
				gameOverAnimation(current_state, sprites['pacman'])
			# change the immortal status to mortal after 2 seconds have elapsed
			if IMMORTAL:
				current_time = time.time()
				elapsed = current_time - startTIME
				if elapsed > 2:
					IMMORTAL = False

		# update the display
		pygame.display.update()
		FPSCLOCK.tick()
	return


def getBackgroundScreen(color=GREEN_SEA):
	'''
	Adds a wash of Green to the game background by default or creates a Black and White grid for the game screen if GRID = True.
	'''
	DISPLAYSURF.fill(color)
	pygame.draw.rect(DISPLAYSURF, BLACK, (0, 0, WINDOWWIDTH, BORDERY))
	pygame.draw.rect(DISPLAYSURF, BLACK, (0, WINDOWHEIGHT-BORDERY, WINDOWWIDTH, BORDERY))

	if GRID:
		# GRID screen
		pygame.draw.rect(DISPLAYSURF, BLACK, (BORDERX, BORDERY, WINDOWWIDTH-(2*BORDERX), WINDOWHEIGHT-(2*BORDERY)))

		# GRIDs
		for x in range(BORDERY, WINDOWHEIGHT-BORDERY+1, CELLSIZE):
			pygame.draw.line(DISPLAYSURF, LIGHTGRAY, (BORDERX, x), (WINDOWWIDTH-BORDERX, x), 1)
		for y in range(BORDERX, WINDOWWIDTH-BORDERX+1, CELLSIZE):
			pygame.draw.line(DISPLAYSURF, LIGHTGRAY, (y, BORDERY), (y, WINDOWHEIGHT-BORDERY), 1)
	return


def getStartScreen():
	'''
	Displays the start-up screen on the window. 
	The start-up screen is divided into three equal parts -
		The topmost part has the Pacman official logo (an image) drawn onto it.
		The middle part has a few lines of instructions (text) drawn over it. 
		The bottommost part has a game image (image) drawn onto it. 
	Since pygame does not have any built-in method of inserting a newline while blitting text to screen, a for loop with inncreasing y-coordinates is used to get the desired effect.
	'''
	# background screen is the color of the background
	getBackgroundScreen()
	image_dims = (WINDOWWIDTH - (2*BORDERX), (WINDOWHEIGHT - (2*BORDERY)) // 3)
	# Game logo in the top part
	gameLogo = pygame.image.load("Media\\game-logo.png").convert_alpha()
	gameLogo.set_colorkey(WHITE)
	gameLogo = pygame.transform.scale(gameLogo, image_dims)
	gameLogoRect = gameLogo.get_rect()
	gameLogoRect.topleft = (BORDERX, BORDERY)
	gameLogoRect.width = image_dims[0]
	gameLogoRect.height = image_dims[1]

	# Instructions in the middle part
	instructions = ["INSTRUCTIONS -  1. Press 's' to start game in color",
		"2. Press 'g' to start game with B&W background",
		"3. Press 'r'' to restart game",
		"4. Press 'p' to pause game",
		"5. Press 'q' to return to main menu",
		"6. Press 'ESC' to shut game",
		"It's probably best to press the arrow keys many times"]
	i = 0
	for x in range(35, 220, 30):
		inst = INSTFONT.render(instructions[i], True, BLACK)
		instRect = inst.get_rect()
		instRect.centerx = (WINDOWWIDTH//2)
		instRect.centery = ((WINDOWHEIGHT//3) + x)
		# blit each line of instructions to the surface
		DISPLAYSURF.blit(inst, instRect)
		i += 1

	# Game photo in the bottom part
	banner = pygame.image.load("Media\\banner.png").convert_alpha()
	banner.set_colorkey(BLACK)
	banner = pygame.transform.scale(banner, image_dims)
	bannerRect = banner.get_rect()
	bannerRect.bottomleft = (BORDERX, WINDOWHEIGHT-BORDERY)
	bannerRect.width = image_dims[0]
	bannerRect.height = image_dims[1]

	# blit the images to the surface
	DISPLAYSURF.blit(gameLogo, gameLogoRect)
	DISPLAYSURF.blit(banner, bannerRect)
	
	pygame.display.update()
	FPSCLOCK.tick()
	return


def startGame():
	'''
	Creates and returns the sprites data structures with necessary variables which will be used throughout the game.
	One list for each ghost and one for pacman.
	The DS are given below:
		pacman_ds => [direction, speed, score, remaining-lives, previous-direction]
		ghosts_ds => [direction, speed, ghost-color, displaced-object]
	A few variables are set initially to start the game faster.
	'''
	sprites = {'pacman' : ['right', 1, SCORE, LIVES, None],
			   'ghosts' : {'ghostr' : ['right', 1, 'r', 'x'],
			   			   'ghostg' : ['up', 1, 'g', 'x'],
			   			   'ghostb' : ['left', 1, 'b', 'x']}
			  }
	return sprites


def getCountdownScreen(pacman):
	'''
	Called when the game has started. 
	Loads the game map from file and returns if the file is empty. 
	Displays the starting layout of the game map.
	Starts a couontdown on the screen after which the game starts.
	'''
	getBackgroundScreen()
	x = readLevelMap()
	if x is not None:
		# x is None if the file is empty 
		drawMap(x, pacman)
	else:
		print("Error 201 - Empty level file.")
		return
	dispCountdown(x, pacman)
	return x


def dispCountdown(x, pacman):
	'''
	Displays the countdown on the center of the game map.
	Displayed on a semi-transparent surface over the main game surface. 
	Till the countdown happens, control remains in this function itself. 
	'''
	global gameSTART, GRIDq
	start_time = time.time()
	elapsed = 0
	num = 3
	while elapsed < 4:
		getBackgroundScreen()
		drawMap(x, pacman)

		# not set to exactly 3 seconds because that seems a little too slow
		current_time = time.time()
		elapsed = current_time - start_time
		if 0.8 < elapsed < 1.6:
			num = 2
		elif 1.6 < elapsed < 2.3:
			num = 1
		elif elapsed > 2.4:
			break

		# creating the background surface with the countdown value
		rect_width = 250
		rect_height = 200
		timemsg = LOGOFONT.render("{}".format(num), True, WHITE)
		timeRect = timemsg.get_rect()
		timeRect.center = (rect_width//2, rect_height//2)
		timeSurf = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
		timeSurf.fill(DARKRED)
		timeSurf.blit(timemsg, timeRect)
		DISPLAYSURF.blit(timeSurf, ((WINDOWWIDTH-rect_width)//2, (WINDOWHEIGHT-rect_height)//2))
		pygame.display.update()

		# checking for only certain allowed events while the countdown is underway -> quit to main screen, exit game.
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				terminate()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					gameSTART = False
					GRID = False
					getStartScreen()
					return
				elif event.key == pygame.K_ESCAPE:
					terminate()
		# clear the event queue so that none of the keystrokes in the countdown have any effect on the game
		pygame.event.clear()
	return


def getPauseScreen(state, pacman):
	'''
	Called if the p key is pressed while the game is running. 
	This will pause the gameplay and freeze the sprites on screen. 
	It displays a pause message in the center of the screen.
	Game can be resumed by pressing any key.
	Control remains in this function tiil a key is pressed to resume the game.
	'''
	while True:
		# draw the same map over and over again
		drawMap(state, pacman)
		pausemsg1 = LOGOFONT.render("Paused", True, WHITE, BLACK)
		pausemsg2 = LOGOFONT.render("Press any key to continue", True, WHITE, BLACK)

		pausemsg1Rect = pausemsg1.get_rect()
		pausemsg2Rect = pausemsg2.get_rect()
		pausemsg1Rect.centerx = pausemsg2Rect.centerx = WINDOWWIDTH//2
		pausemsg1Rect.centery = (WINDOWHEIGHT//2) - 25
		pausemsg2Rect.centery = (WINDOWHEIGHT//2) + 25

		DISPLAYSURF.blit(pausemsg1, pausemsg1Rect)
		DISPLAYSURF.blit(pausemsg2, pausemsg2Rect)		

		pygame.display.update()
		FPSCLOCK.tick()

		# if ESC key is pressed shut down game. If any other key is pressed, resume game
		if pygame.event.get(pygame.QUIT):
			terminate()
		for event in pygame.event.get(pygame.KEYDOWN):
			if event.key == pygame.K_ESCAPE:
				terminate()
			else:
				getBackgroundScreen()
				drawMap(state, pacman)
				return


def isLegitMove(dirn, speed, mapObj, sprite='p'):
	'''
	Checks if a given move is allowed by the rules of the game. 
	Since the accessibility rules are different for pacman and the ghosts (the ghosts cannot re-enter their box once their out), the function changes with the sprite that is sent as an argument.
	The box placement is hard-coded and can be easily automated by changing the map.txt file and adding a few extra lines of code.
	Two loops are run over the map object till the given sprite is found. The given direction and speed is then checked to see if the resulting move is legitimate.
	Returns a boolean value.
	'''
	accessible = ['.', 'o', 'f', 'c', '_']
	if sprite != 'p':
		accessible.append('p')
	else:
		accessible.append('x')
		accessible.extend(['r', 'g', 'b'])
	for row, line in enumerate(mapObj):
		for col, cell in enumerate(line):
			if cell == sprite:
				if (sprite != 'p') and (13<row<17) and (9<col<17):
					# only ghosts inside the box can move around in the box. The numbers above are the box-coordinates -. hard-coded.
					accessible.append('x')
				else:
					if dirn is None:
						return True
				if dirn == "right" and mapObj[row][col+speed] in accessible:
					return True
				elif dirn == "left" and mapObj[row][col-speed] in accessible:
					return True
				elif dirn == "up" and mapObj[row-speed][col] in accessible:
					return True
				elif dirn == "down" and mapObj[row+speed][col] in accessible:
					return True
	return False


def getLegitMoves(mapObj, ghost):
	'''
	To move the ghosts, this function checks all the available legitimate moves for a single ghost and returns the legal moveset.
	If no legal moves are available it returns None. 
	Ghosts cannot turn around midway i.e. if they're going right they cannot suddenly go left. They must stop before changing to the opposite direction.
	'''
	directions = ['left', 'right', 'up', 'down']
	moves = []
	# find all directions that the ghost can move in and create a list
	for dirn in directions:
		if isLegitMove(dirn, ghost[1], mapObj, ghost[2]):
			moves.append(dirn)
	if not moves:
		return None
	else:
		# remove the opposite of the current direction
		if ghost[0] == "left" and "right" in moves:
			moves.remove("right")
		elif ghost[0] == "right" and "left" in moves:
			moves.remove("left")
		elif ghost[0] == "down" and "up" in moves:
			moves.remove("up")
		elif ghost[0] == "up" and "down" in moves:
			moves.remove("down")
		if not moves:
			return None
		else:
			return moves


def gameplay(mapObj, sprites):
	'''
	The pacman and ghosts data structures are extracted as separate vairable to make it easier to pass values along to other functions. 
	Since this is not a deep copy, changes made reflect in the copies as well as the originals. (The copies are just pointers), to create separate copies we can create a deep_copy() as defined below.
	The main movements of the sprites occur here. First the ghosts move and then pacman moves. 
	The statistics (remaining lives and score) are also updated here.
	After every change in position the map is redrawn.
	'''
	pacman = sprites['pacman']
	ghosts = sprites['ghosts']
	# move the ghosts
	mapObj = moveGhosts(mapObj, sprites)
	# move pacman
	mapObj = movePacman(mapObj, pacman)
	if not isLegitMove(pacman[0], pacman[1], mapObj):
		if pacman[0] is not None:									# this is used so that the previous direction is never set to None
			pacman[4] = pacman[0]
		pacman[0] = None
	# draw changes to the map object
	drawMap(mapObj, pacman)
	# display any change in stats
	dispStats(pacman[2], pacman[3])
	pygame.display.update()
	FPSCLOCK.tick(FPS)
	return mapObj


def movePacman(mapObj, pacman):
	'''
	This is where the movement of pacman is done on the map object. 
	If pacman has legitimate moves in its current direction, it will move forward in that direction till it cannot move any further.
	Once it cannot move any further, the direction is reset to None, denoting that it is now at rest. 
	If it moves over any cell containing food items, they get "eaten" and are counted in the score. 
	Other effects of these food items can also be added.
	After items are eaten they leave behind an "_" symbol denoting empty space that pacman can move on later.
	If pacman runs into a ghost instead and is not immortal, it loses a life.
	'''
	food = ['.', 'o', 'f', 'c']
	ghosts = ['r', 'g', 'b']
	for row, line in enumerate(mapObj):
		for col, cell in enumerate(line):
			if cell == 'p':
				if not pacman[0]:
					# if direction is None
					return mapObj
				if pacman[0] == "right" and isLegitMove(pacman[0], pacman[1], mapObj):
					mapObj[row][col], mapObj[row][col+pacman[1]] = mapObj[row][col+pacman[1]], mapObj[row][col]
				elif pacman[0] == "left" and isLegitMove(pacman[0], pacman[1], mapObj):
					mapObj[row][col], mapObj[row][col-pacman[1]] = mapObj[row][col-pacman[1]], mapObj[row][col]
				elif pacman[0] == "down" and isLegitMove(pacman[0], pacman[1], mapObj):
					mapObj[row][col], mapObj[row+pacman[1]][col] = mapObj[row+pacman[1]][col], mapObj[row][col]
				elif pacman[0] == "up" and isLegitMove(pacman[0], pacman[1], mapObj):
					mapObj[row][col], mapObj[row-pacman[1]][col] = mapObj[row-pacman[1]][col], mapObj[row][col]
				if mapObj[row][col] in food:
					if mapObj[row][col] == ".":
						points = 1
					elif mapObj[row][col] in ["o", "f"]:
						points = 2
					elif mapObj[row][col] in ["c"]:
						points = 5
					pacman = updateStats(pacman, points, 0)
					mapObj[row][col] = '_'
				elif mapObj[row][col] in ghosts and not IMMORTAL: 
					loseLife(pacman)
				return mapObj
	return mapObj


def moveGhosts(mapObj, sprites):
	'''
	This is where the movement of the ghosts is initiated. 
	The available moveset is determined for each ghost and any one direction is selected on random.
	If the returned moveset is None, the ghost remains where it is and waits for legal moves to open up.
	The ghosts are shifted on the map in another function.
	'''
	ghosts = sprites['ghosts']
	# randomly selecting ghost directions
	for ghost in ghosts.keys():
		moves = getLegitMoves(mapObj, ghosts[ghost])
		if moves:
			dirn = random.choice(moves)
			ghosts[ghost][0] = dirn
		else:
			ghosts[ghost][0] = None
		mapObj = shiftGhostsOnMap(mapObj, ghosts[ghost], sprites['pacman'])
	return mapObj


def shiftGhostsOnMap(mapObj, ghost, pacman):
	'''
	Separate function because break does not break completely out of nested for or while loops, but return can technically.
	Similar to the movePacman function, but here no food is eaten and the ghost must not accidently remove any object that was originally present at a given spot. 
	The ghost data structure stores the value of the displaced item and replaces it when the ghost moves to another spot on the map. 
	If the ghost intercepts pacman while he is mortal, lose life.
	'''
	for row, line in enumerate(mapObj):
		for col, cell in enumerate(line):
			if cell == ghost[2]:
				# swap the displaced-object with the current position of the ghost
				if ghost[0] == "right":
					mapObj[row][col], ghost[3] = ghost[3], mapObj[row][col]
					ghost[3], mapObj[row][col+ghost[1]] = mapObj[row][col+ghost[1]], ghost[3]
				elif ghost[0] == "left":
					mapObj[row][col], ghost[3] = ghost[3], mapObj[row][col]
					ghost[3], mapObj[row][col-ghost[1]] = mapObj[row][col-ghost[1]], ghost[3]
				elif ghost[0] == "down":
					mapObj[row][col], ghost[3] = ghost[3], mapObj[row][col]
					ghost[3], mapObj[row+ghost[1]][col] = mapObj[row+ghost[1]][col], ghost[3]
				elif ghost[0] == "up":
					mapObj[row][col], ghost[3] = ghost[3], mapObj[row][col]
					ghost[3], mapObj[row-ghost[1]][col] = mapObj[row-ghost[1]][col], ghost[3]
				if (ghost[3] == 'p') and not IMMORTAL:
					loseLife(pacman)
				return mapObj
	return mapObj


def loseLife(pacman):
	'''
	This function updates the remaining lives stat of pacman.
	It reduces one life and the immortality timer begins here. 
	'''
	global IMMORTAL, startTIME
	pacman = updateStats(pacman, 0, 1)
	IMMORTAL = True
	startTIME = time.time()
	return


def updateStats(pacman, points, lives):
	'''
	This function updates the score and remaining lives stats.
	'''
	pacman[2] += points
	pacman[3] -= lives
	return pacman


def dispStats(score, lives):
	'''
	This function blits the score and remaining lives to the main game screen. 
	'''
	# Score in the top-right
	score = STATFONT.render("Score - {0}".format(score), True, WHITE)
	scoreRect = score.get_rect()
	scoreRect.topleft = (WINDOWWIDTH-100, 10)
	# Remaining lives in the bottom-right
	lives = STATFONT.render("Lives - {0}".format(lives), True, WHITE)
	livesRect = lives.get_rect()
	livesRect.topleft = (20, WINDOWHEIGHT-20)

	DISPLAYSURF.blit(score, scoreRect)
	DISPLAYSURF.blit(lives, livesRect)
	return


def gameWon(mapObj):
	'''
	Checks to see if any eatable items are left.
	If not then returns True, else False.
	'''
	food = ['.', 'o', 'f', 'c'] 
	for line in mapObj:
		for cell in line:
			if cell in food:
				return False
	return True


def winAnimation(mapObj, pacman):
	'''
	If game is won, it blits and displays the game won text messages in the center of the screen. 
	For 9 x FPS seconds the background screen blinks (alternates between two colors) as a win animation.
	The game start variables are reset, start screen is displayed and control is returned to the main game loop to await further instructions.
	'''
	global GRID, gameSTART
	blink = True

	rect_width = 550
	rect_height = 300
	winmsg1 = LOGOFONT.render("CONGRATULATIONS", False, WHITE)
	winRect1 = winmsg1.get_rect()
	winRect1.center = ((rect_width//2), (rect_height//2))
	winmsg2 = LOGOFONT.render("YOU WIN!", False, WHITE)
	winRect2 = winmsg2.get_rect()
	winRect2.center = ((rect_width//2), (rect_height//2) + 50)
	winSurf = pygame.Surface((rect_width, rect_height))
	winSurf.fill(DARKRED)
	winSurf.blit(winmsg1, winRect1)
	winSurf.blit(winmsg2, winRect2)
	
	for x in range(9):
		if blink:
			drawMap(mapObj, pacman, BLINK_COLOR)
		else:
			drawMap(mapObj, pacman)
		DISPLAYSURF.blit(winSurf, ((WINDOWWIDTH-rect_width)//2, (WINDOWHEIGHT-rect_height)//2))
		blink = not blink
		pygame.display.update()
		FPSCLOCK.tick(FPS)
	GRID = False
	gameSTART = False
	getStartScreen()
	return


def gameOverAnimation(mapObj, pacman):
	'''
	If the ghost bumps into pacman, the game over animation plays.
	Unlike the win animation, there is not blinking, instead the backgrouund color becomes black and the game over message is displayed for 9 x FPS seconds.
	Vairables are reset and control is returned back to the main game loop again. 
	'''
	global GRID, gameSTART
	rect_width = 550
	rect_height = 300
	winmsg = LOGOFONT.render("GAME OVER", False, WHITE)
	winRect = winmsg.get_rect()
	winRect.center = ((rect_width//2), (rect_height//2))
	winSurf = pygame.Surface((rect_width, rect_height))
	winSurf.fill(DARKRED)
	winSurf.blit(winmsg, winRect)

	for x in range(9):
		drawMap(mapObj, pacman, BLACK)
		DISPLAYSURF.blit(winSurf, ((WINDOWWIDTH-rect_width)//2, (WINDOWHEIGHT-rect_height)//2))
		pygame.display.update()
		FPSCLOCK.tick(FPS)
	GRID = False
	gameSTART = False
	getStartScreen()
	return


def getPixels(row, col):
	'''
	Gets the window pixel values given the row and column number on the main game screen.
	'''
	# when only the row changes, the x_coord stays constant and vice versa.
	x_coord = BORDERX + (col * 25)
	y_coord = BORDERY + (row * 25)
	return x_coord, y_coord


def readLevelMap():
	'''
	Given the filepath, it reads in the game map into the levelMap vairable as a 2D list. It uses the map.txt rules to ably extract the map from the txt file.
	LEGEND FOR THE MAPFILE: 
		//		-		Comments
		~ 		- 		End of level.
	Rest of the symbols are in the drawMap function.
	'''
	filepath = "Maps\\beginner.txt"
	f = open(filepath, "r")

	levelMap = []
	for x in f:
		if x[0] == "\n":
			# empty line
			continue
		elif x[0] == '/' and x[1] == '/':
			# if line begins with // it tells the level number
			x = x.strip()
			levelNum = x[-1]
		elif x[0] == '~':
			# end of level
			return levelMap
		else:
			x = x.strip()
			levelMap.append(x)
	return None


def drawMap(levelMap, pacman, color=GREEN_SEA):
	'''
	Uses the symbology of the map file to draw the map onto the game screen as the pacman world. 
	Also draws the word PACMAN on the top half of the game map.
	LEGEND OF THE MAPFILE: 
		r 		-		Red ghost
		g 		- 		Green ghost
		b 		- 		Blue ghost
		p 		- 		PacMan
		. 		- 		Small food
		o 		-		Big food (yellow dots)
		f 		- 		Big food (red dots)
		c 		- 		Cherry
		# 		- 		Walls
		l 		- 		Text area for PACMAN
		- 		- 		Empty space not accessible by sprites
		_ 		- 		Empty space accessible by sprites
		x 		- 		Empty space accessible by PacMan but not by the ghosts
	'''
	# line is the equivalent to row number and cell is the equivalent to column number
	getBackgroundScreen(color)
	for row, line in enumerate(levelMap):
		for col, cell in enumerate(line):
			drawCellHighlight(row, col)
	for row, line in enumerate(levelMap):
		for col, cell in enumerate(line):
			if cell == "#":
				drawWall(row, col)
			elif cell in (".", "o", "f"):
				drawFood(row, col, cell)
			elif cell in ("r", "g", "b"):
				drawGhost(row, col, cell)
			elif cell == "p":
				drawPacMan(row, col, pacman)
			elif cell == "l":
				updateLogoCoords(row, col)
			elif cell == "c":
				drawCherry(row, col)
			elif cell is "-":
				pass
	drawLogo()
	return


def loadSprite(x_coord, y_coord, index, pacman=None):
	'''
	This function is used to load all of the sprites / images onto the game map. 
	Make sure that the sprite images have a WHITE or otherwise common background. The set_colorkey() function is used to not blit any part of the image of that color (i.e the squarish background)
	Depending on the direction that pacman is facing, the pacman sprite is rotated or flipped accordingly.
	If pacman's current direction is None, transform the sprite to the last direction that it was in.
	'''
	img = SPRITES_DICT[index].convert() 							# convert() converts the loaded image to the format that it will be displayed in (RGB in this case)
	img.set_colorkey(WHITE)
	img = pygame.transform.scale(img, sprite_dims)					# transform.scale() is used for resizing
	if pacman:
		#print(pacman[0], pacman[4])
		if pacman[0]:
			if pacman[0] == "left":
				img = pygame.transform.flip(img, True, False)
			elif pacman[0] == "up":
				img = pygame.transform.rotate(img, 90)
			elif pacman[0] == "down":
				img = pygame.transform.rotate(img, -90)
		else:
			if pacman[4] == "left":
				img = pygame.transform.flip(img, True, False)
			elif pacman[4] == "up":
				img = pygame.transform.rotate(img, 90)
			elif pacman[4] == "down":
				img = pygame.transform.rotate(img, -90)
	imgRect = img.get_rect()
	imgRect.centerx = x_coord
	imgRect.centery = y_coord
	DISPLAYSURF.blit(img, imgRect)
	return


def drawCellHighlight(row, col):
	# Draws the light cell boundaries to give a better look to the game background when GRID = False.
	x_coord, y_coord = getPixels(row, col)
	if GRID:
		pass
	else:
		pygame.draw.rect(DISPLAYSURF, LIGHTGREEN_SEA, (x_coord, y_coord, 25, 25), 1)
	return


def drawPacMan(row, col, pacman):
	# Draws Pacman
	x_coord, y_coord = getPixels(row, col)
	x_coord += CELLSIZE//2
	y_coord += CELLSIZE//2
	loadSprite(x_coord, y_coord, 'pacman', pacman)
	return


def drawWall(row, col):
	# Draws the wall as two different colored, different sized squares.
	x_coord, y_coord = getPixels(row, col)
	pygame.draw.rect(DISPLAYSURF, DARKSAND, (x_coord, y_coord, 25, 25))
	pygame.draw.rect(DISPLAYSURF, SAND, (x_coord+5, y_coord+5, 15, 15))
	return


def drawFood(row, col, food_type):
	# Draws the "food" items of different types and sizes
	x_coord, y_coord = getPixels(row, col)

	if food_type == ".":
		pygame.draw.circle(DISPLAYSURF, YELLOW, (x_coord+(CELLSIZE//2), y_coord+(CELLSIZE//2)), 2)
	elif food_type == "o":
		pygame.draw.circle(DISPLAYSURF, YELLOW, (x_coord+(CELLSIZE//2), y_coord+(CELLSIZE//2)), 5)
	elif food_type == "f":
		pygame.draw.circle(DISPLAYSURF, RED, (x_coord+(CELLSIZE//2), y_coord+(CELLSIZE//2)), 5)
	return


def drawGhost(row, col, cell):
	# Draws the different ghosts according to their sprite symbols
	x_coord, y_coord = getPixels(row, col)
	x_coord += CELLSIZE//2
	y_coord += CELLSIZE//2
	if cell == "r":
		x = "red"
	elif cell == "g":
		x = "green"
	elif cell == "b":
		x = "blue"
	loadSprite(x_coord, y_coord, "ghost_{}".format(x))
	return


def drawCherry(row, col):
	# Draws the cherry sprite
	x_coord, y_coord = getPixels(row, col)
	loadSprite(x_coord, y_coord, 'cherries')
	return

	
def updateLogoCoords(row, col):
	'''
	This function is used to find the coordinates on the game map, of the entire area marked by the symbol 'l'.
	This portion is where PACMAN is displayed on the game map.
	'''
	x_coord, y_coord = getPixels(row, col)
	if logo_topcoords == [0, 0]:
		logo_topcoords[0] = x_coord
		logo_topcoords[1] = y_coord
	else: 
		logo_botcoords[0] = x_coord + 25
		logo_botcoords[1] = y_coord + 25
	return


def drawLogo():
	# Draws the game's name PACMAN on the game map
	w = logo_botcoords[0] - logo_topcoords[0]
	h = logo_botcoords[1] - logo_topcoords[1]
	logo = LOGOFONT.render('PACMAN', True, PINK, PURPLE)
	logoRect = logo.get_rect()
	logoRect.topleft = logo_topcoords
	logoRect.width = w
	logoRect.height = h
	DISPLAYSURF.blit(logo, logoRect)
	return


def terminate():
	# Shuts and quits the game.
	pygame.quit()
	sys.exit()


def deep_copy(l):
	'''
	Creates a deep copy of the map Object so that changes to the copy will not affect the original object.
	'''
	outlist = []
	for i in l:
		inlist = []
		for j in i:
			inlist.append(j)
		outlist.append(inlist)
	return outlist


if __name__ == "__main__":
	main()