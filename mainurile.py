import pygame, random, sys
from pygame.locals import *

#FPS
clock = pygame.time.Clock()

#Intrare
pygame.init()

#Size
WINDOW_SIZE = (600, 400)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
pygame.display.set_caption('Mingea')
test_rect = pygame.Rect(100,100,100,50)

#Player
player = pygame.image.load("Imagini JOC/player/run/run_0.png")
player_y_momentum = 0
air_timer = 0
player_rect = pygame.Rect(50, 50, player.get_width(), player.get_height())


#Asezari
moving_right = False
moving_left = False

#Desene
iarba = pygame.image.load("Imagini JOC/strat/iarba.png")
pamant = pygame.image.load("Imagini JOC/strat/pamant.png")
planta = pygame.image.load("Imagini JOC/strat/iarba_frum.png")

#Tile
TILE_SIZE = iarba.get_width()

#Coliziuni si miscari
def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top' : False, 'bottom' : False, 'right' : False, 'left' : False}
    rect.x += movement[0]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types

#Animatii
global animation_frames
animation_frames = {}

def load_animation(path,frame_duration):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0

    for frame in frame_duration:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((0,0,0))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

animation_database = {}
animation_database['stanga'] = load_animation('Imagini JOC/player/stanga', [12,12,12,12])
animation_database['run'] = load_animation('Imagini JOC/player/run', [12,12,12,12])
animation_database['idle'] = load_animation('Imagini JOC/player/idle', [20,20])
animation_database['sare'] = load_animation('Imagini JOC/player/sare',[7])

#Actiuni Noi
def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame

player_action = 'idle'
player_frame = 0
player_flip = False

#Background 
background = pygame.image.load("Imagini JOC/Background/background.png").convert()
backgroundx = 0

#Inamic
# enemies = []
# for i in range(5):
#     enemies.append([0,e.entity(random.randint(0,600)-300,80,13,13,'Imagini JOC/inamic/inamic.png')])

#Mapa 2.0
game_map = {}
CHUNK_SIZE = 8

#Index
tile_index ={1:iarba,
             2:pamant,
             3:planta
            }

def generate_chunk(x, y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE+ x_pos
            target_y = y * CHUNK_SIZE+ y_pos
            tile_type = 0
            if target_y > 10:
                tile_type = 2
            elif target_y == 10:
                tile_type = 1
            elif target_y == 9:
                if random.randint(1, 5) == 1:
                    tile_type = 3
            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])
    return chunk_data


#Scaling
display = pygame.Surface((300,200))
true_scroll = [0,0]

#Pornire
while True:
   
    #FILL
    display.fill((255, 255, 255))

    #Scroll
    true_scroll[0] += (player_rect.x - true_scroll[0] - 158)/20
    true_scroll[1] += (player_rect.y - true_scroll[1] - 108)/20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])
    display.blit(background, (backgroundx, 0))

    # Rendering 2.0
    tile_rects = []
    for y in range (3):
        for x in range (4):
            target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*16)))
            target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE*16)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x,target_y)
            for tile in game_map[target_chunk]:
                display.blit(tile_index[tile[1]], (tile[0][0] * 16 - scroll[0], tile[0][1] * 16 - scroll[1]))
                if tile[1] in [1,2]:
                    tile_rects.append(pygame.Rect(tile[0][0]* 16, tile[0][1]*16,16, 16))

    #Merge2
    player_movement = [0, 0]
    if moving_right == True:
        player_movement[0] += 2
    if moving_left == True:
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if player_movement[0] == 0:
         player_action,player_frame = change_action(player_action,player_frame,'idle')
    if player_movement[0] > 0:
        player_flip = False
        player_action,player_frame = change_action(player_action,player_frame,'run')
    if player_movement[0] < 0:
        player_flip = True
        player_action,player_frame = change_action(player_action,player_frame,'stanga')
    if player_y_momentum <= 0 or player_y_momentum == 3:
         player_action,player_frame = change_action(player_action,player_frame,'sare')

    player_rect, collision = move(player_rect, player_movement, tile_rects)

    #Sare
    if collision['bottom'] == True:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1

    #Frame
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    
    display.blit(pygame.transform.flip(player_img,player_flip,False),(player_rect.x-scroll[0],player_rect.y-scroll[1]))

    #Merge 
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
    
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))

    pygame.display.update()
    clock.tick(60)