import pygame, sys, os, random, shelve #Importa librariile
from pygame.locals import * #in localele pygame impor steluta (adica toate obiectele prezente in fisierele python chiar si modularele acesteia in programul curent)
import sursa.sursa as s #Importa sursa ca variabila "s" 
pygame.mixer.pre_init(44100, -16, 2, 512) #Pentru muzica
clock = pygame.time.Clock() #Frame-ul

pygame.init() #Asa incepe libraria
pygame.mixer.set_num_channels(64) #Muzica
pygame.display.set_caption('Mingea') #Titlul jocului

#Marimea ecranului
WINDOW_SIZE = s.rezolutie(600,400)
screen = WINDOW_SIZE.set_window() #Il initializeaza pe ecran
display = WINDOW_SIZE.suprafata(2) #Il foloseste ca si suprafata pentru a incarca datele si pentru scalarea ecranului
Window_display = WINDOW_SIZE.suprafata(1) #Da zoom la ecran
ecran = WINDOW_SIZE.display_hw(1)

#Miscari
mobil_dreapta = False #Merge spre dreapta
mobil_stanga = False #Merge spre stanga 
impuls_vertical = 0 #Sare 
timp_aer = 0 #Cat timp sta in aer
true_scroll = [0,0] #Traiectoria camerei

#Background 
background = pygame.image.load("sursa/imagini/background/background.png").convert()
background = pygame.transform.scale(background, ecran)
screenground = pygame.image.load("sursa/imagini/background/screenground.png").convert()
screenground = pygame.transform.scale(screenground, ecran)
tutorialscreen = pygame.image.load("sursa/imagini/background/tutorial.png").convert()
tutorialscreen = pygame.transform.scale(tutorialscreen, ecran)

#Crearea Portiunii
CHUNK_SIZE = 8 #Cat de mare sa fie portiunea
mapa_jocului = {}

#Incarca imagini
s.load_animatii('sursa/imagini/entitati/')
imagine_suprafata = pygame.image.load('sursa/imagini/straturi/suprafata.png')
imagine_pamant = pygame.image.load('sursa/imagini/straturi/pamant.png') 
imagine_iarba = pygame.image.load('sursa/imagini/straturi/iarba.png').convert()
imagine_iarba.set_colorkey((255, 255, 255)) #Si-l converteste pentru display

tile_index = {1:imagine_suprafata, #Acest index(dictionar) defineste imaginile ca si numere
              2:imagine_pamant,
              3:imagine_iarba
              }

#Text
font = pygame.font.SysFont(None, 20)
font2 = pygame.font.SysFont("comicsans", 20, True)

#Jucatorul si inamicul
jucator = s.entitate(100, 100, 5, 13, 'player')
inamicul = []
id_inamic = 0
counter_inamic = 0
bullet_collide = False
player_damage = 3

#Glont
class projectil(object):
    def __init__(self,x,y,radiani,culoare,indreptat):
        self.x = x
        self.y = y
        self.radiani = radiani
        self.culoare= culoare
        self.indreptat = indreptat
        self.vel = 8 * indreptat

    def draw(self,win):
        pygame.draw.circle(win, self.culoare, (self.x,self.y), self.radiani)
bullets = []

#Score & Health Bar
jucator.health = 10+1.5

# Valul inamicilor
wave_round = 0
def wave(wave_round, inamic_list):
    id_inamic = 0
    wave_round_var = wave_round+1
    for _ in range(wave_round_var):
        inamic_list.append([0, s.entitate(jucator.x+random.randint(-75,75), 80, 13, 13, 'enemy'),f"id: {id_inamic}", 100])
        id_inamic += 1
    for inamic in inamic_list:
        inamic[1].health = 10+1.5
    return id_inamic, inamic_list, wave_round_var


#Meniul
def main_menu():
    while True:
        global screen, Window_display
        click = None
        Window_display.fill((0,0,0))
        Window_display.blit(screenground, (0, 0))
        screen.blit(pygame.transform.scale(Window_display,(pygame.display.Info().current_w, pygame.display.Info().current_h)), (0, 0))
        s.draw_text('main menu', font, (255, 255, 255), screen, 20, 20)
 
        mx, my = pygame.mouse.get_pos()
 
        button_1 = pygame.Rect(50, 100, 200, 50)
        button_2 = pygame.Rect(50, 200, 200, 50)
        joc = pygame.draw.rect(screen, (255, 0, 0), button_1)
        optiuni = pygame.draw.rect(screen, (255, 0, 0), button_2)
        system_font = pygame.font.SysFont('arial', 50)
        joc_text = system_font.render("Joc", True, (255, 255, 255))
        optiune_text = system_font.render("Tutorial", True, (255, 255, 255))
        screen.blit(joc_text, (joc.width//1.75, joc.height*2))
        screen.blit(optiune_text, (optiuni.width//2.50, optiuni.height*4))
 
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            if event.type == VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        if button_1.collidepoint((mx, my)):
            if click:
                game()
        if button_2.collidepoint((mx, my)):
              if click:
                options()
        click = False

        pygame.display.update()
        clock.tick(60)

#Jocul
def game():
    running = True
    scorul = 0
    while running:
        #FILL
        display.fill((255, 255, 255))

        #Globalizare
        global mobil_dreapta, mobil_stanga, impuls_vertical, timp_aer, jucator_flip, id_inamic, counter_inamic, inamicul, bullets, bullet_collide, wave_round, player_damage

        #Scroll
        true_scroll[0] += (jucator.x-true_scroll[0]-158)/20
        true_scroll[1] += (jucator.y-true_scroll[1]-108)/20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])
        display.blit(background, (0, 0))

        #Randare
        tile_rects = []
        for y in range(3):
            for x in range(4):
                target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*16)))
                target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE*16)))
                target_chunk = str(target_x) + ';' + str(target_y)
                if target_chunk not in mapa_jocului:
                    mapa_jocului[target_chunk] = s.generare_portiune(target_x,target_y)
                for tile in mapa_jocului[target_chunk]:
                    display.blit(tile_index[tile[1]],(tile[0][0]*16-scroll[0],tile[0][1]*16-scroll[1]))
                    if tile[1] in [1,2]:
                        tile_rects.append(pygame.Rect(tile[0][0]*16,tile[0][1]*16,16,16)) 
        #Inamic
        if counter_inamic == 0:
            counter_inamic, inamicul, wave_round = wave(wave_round, inamicul)

        #Glont
        # Variabile care o sa ajute la rularea programului
        bullet_selectat = None
        for bullet in bullets:
            if bullet.x < WINDOW_SIZE.width and bullet.x > 0:
                bullet.x += bullet.vel
            else:
                bullets.pop(bullets.index(bullet))
                
        # Un loop mic la care determina cand glontul loveste inamicul
        for bullet in bullets:
            for inamic in inamicul:
                if (bullet.x >=inamic[1].x-scroll[0]) and (bullet.x<=(inamic[1].x-scroll[0]+15)):
                    if (bullet.y >= (inamic[1].y-35)) and (bullet.y <= (inamic[1].y-28)):
                        inamic[1].health -= player_damage
                        bullet_selectat = bullet
                        bullet_collide = True
                        scorul += 1
        if bullet_collide:
            bullets.remove(bullet_selectat)
            for inamic in inamicul:
                if inamic[1].health <= 0:
                    inamicul.remove(inamic)
                    jucator.health += 1
                    counter_inamic -= 1
            bullet_collide = False
       
       #Merge2
        jucator_movement = [0,0]
        if mobil_dreapta == True:
            jucator_movement[0] += 2
        if mobil_stanga == True:
            jucator_movement[0] -= 2
        jucator_movement[1] += impuls_vertical
        impuls_vertical += 0.2
        if impuls_vertical > 3:
            impuls_vertical = 3

        if jucator_movement[0] == 0:
            jucator.set_action('idle')
        if jucator_movement[0] > 0:
            jucator.set_flip(False)
            jucator.set_action('run')
        if jucator_movement[0] < 0:
            jucator_flip = True
            jucator.set_action('run')

        tipul_coliziunii = jucator.miscare(jucator_movement, tile_rects)
        jucator_movement = [0,0]

        #Sare
        if tipul_coliziunii['bottom'] == True:
            impuls_vertical = 0
            timp_aer = 0
        else:
            timp_aer += 1
        
        jucator.change_frame(1)
        jucator.display(display, scroll)

        #Inamic
        display_r = pygame.Rect(scroll[0], scroll[1], 300, 200)
        for inamic in inamicul:
            if display_r.colliderect(inamic[1].obi.rect):
                inamic[0] += 0.2 
                if inamic[0] > 3:
                    inamic[0] = 3
                inamic_movement = [0, inamic[0]]
                if jucator.x > inamic[1].x + 5:
                    inamic_movement[0] = 1 
                if jucator.x < inamic[1].x -5:
                    inamic_movement[0] = -1
                tipul_coliziunii = inamic[1].miscare(inamic_movement, tile_rects)
                if tipul_coliziunii['bottom'] == True:
                    inamic[0] = 0
                
                inamic[1].display(display, scroll)
                jucator_rect_collide = jucator.obi.rect
                jucator_rect_collide.x = jucator_rect_collide.x +4


                if jucator_rect_collide.colliderect(inamic[1].obi.rect):
                    impuls_vertical = -3
                    scorul -= 1
                    jucator.health -= 0.5
                if scorul < 0:
                    scorul = 0
                if jucator.health > 10:
                    jucator.health = 10
                if jucator.health < 0:
                    pygame.quit()
                    sys.exit()      
                jucator_hp = round((jucator.health-10)/1.5)
                jucator_hp_bar = (1-jucator_hp)
                jucator_rect1 = pygame.Rect(0, jucator.y-scroll[1] - 15, 50 - (15+5*(wave_round-wave_round)), 10)
                jucator_rect2 = pygame.Rect(0, jucator.y-scroll[1] - 15, 50 - (15+5*jucator_hp_bar-5), 10)
                jucator_rect1.centerx = jucator.rect().centerx-scroll[0]
                jucator_rect2.centerx = jucator.rect().centerx-scroll[0]
                pygame.draw.rect(display, (255,0,0), jucator_rect1)
                pygame.draw.rect(display, (0,128,0), jucator_rect2)

        keys = pygame.key.get_pressed()
        tipul_coliziunii = jucator.miscare(jucator_movement, tile_rects)

        #Tastatura 
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    mobil_dreapta = True
                if event.key == K_LEFT:
                    mobil_stanga = True
                if event.key == K_UP:
                    if timp_aer < 6:
                        impuls_vertical = -5
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    mobil_dreapta = False
                if event.key == K_LEFT:
                    mobil_stanga = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            if keys[pygame.K_d]:
                indreptat = 1
                if len(bullets) < 5:
                    bullets.append(projectil(round((jucator.x+jucator.x_marime//2)-scroll[0]), round((jucator.y + jucator.y_marime//2)-scroll[1]), 3, (0,0,0), indreptat))  
            if keys[pygame.K_a]:
                indreptat = -1
                if len(bullets) < 5:
                    bullets.append(projectil(round((jucator.x+jucator.x_marime//2)-scroll[0]), round((jucator.y + jucator.y_marime//2)-scroll[1]), 3, (0,0,0), indreptat)) 
        
        for bullet in bullets:
            bullet.draw(display)
        text_scor = font.render(f"Scor: {scorul}", 1, (0, 0, 0))
        text_wave = font.render(f"Wave: {wave_round}", 1, (0, 0, 0))

        # Aici arata pe ecran viata inamicului
        for inamic in inamicul:
            inamic_hp = round((inamic[1].health-10)/1.5)
            hp_bar = (1-inamic_hp)
            rect1 = pygame.Rect(0, inamic[1].y-scroll[1] - 15, 50 - (15+5*(wave_round-wave_round)), 10)
            rect2 = pygame.Rect(0, inamic[1].y-scroll[1] - 15, 50 - (15+5*hp_bar-5), 10)
            rect1.centerx = inamic[1].rect().centerx-scroll[0]
            rect2.centerx = inamic[1].rect().centerx-scroll[0]
            pygame.draw.rect(display, (255,0,0), rect1)
            pygame.draw.rect(display, (0,128,0), rect2)

        display.blit(text_scor, (0, 0))
        display.blit(text_wave, (0, 20))

        # Se arata pe ecran ce este in "display"

        screen.blit(pygame.transform.scale(display,(pygame.display.Info().current_w, pygame.display.Info().current_h)),(0,0))
        pygame.display.update()
        clock.tick(60)

#Optinuile
def options():
    running = True
    while running:
        Window_display.fill((0,0,0))
        Window_display.blit(tutorialscreen, (0, 0))
        screen.blit(pygame.transform.scale(Window_display,(pygame.display.Info().current_w, pygame.display.Info().current_h)),(0,0))
 
        s.draw_text('Tutorial', font, (255, 255, 255), screen, 20, 20)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        
        pygame.display.update()
        clock.tick(60)
main_menu()