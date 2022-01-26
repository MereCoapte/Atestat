import pygame, sys, os, random #Importa librariile
from pygame.locals import * #in localele pygame impor steluta (adica toate obiectele prezente in fisierele python chiar si modularele acesteia in programul curent)
import data.sursa as s #Importa sursa ca variabila "s" 
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
background = pygame.image.load("data/imagini/background/background.png").convert()
background = pygame.transform.scale(background, ecran)
screenground = pygame.image.load("data/imagini/background/screenground.png").convert()
screenground = pygame.transform.scale(screenground, ecran)

#Crearea Portiunii
CHUNK_SIZE = 8 #Cat de mare sa fie portiunea
mapa_jocului = {}

#Incarca imagini
s.load_animatii('data/imagini/entitati/')
imagine_suprafata = pygame.image.load('data/imagini/straturi/suprafata.png')
imagine_pamant = pygame.image.load('data/imagini/straturi/pamant.png') 
imagine_iarba = pygame.image.load('data/imagini/straturi/iarba.png').convert()
imagine_iarba.set_colorkey((255, 255, 255)) #Si-l converteste pentru display

tile_index = {1:imagine_suprafata, #Acest index(dictionar) defineste imaginile ca si numere
              2:imagine_pamant,
              3:imagine_iarba
              }

#Text
font = pygame.font.SysFont(None, 20)

#Jucatorul si inamicul
jucator = s.entitate(100, 100, 5, 13, 'player')
inamicul = []
for i in range(5):
    inamicul.append([0, s.entitate(random.randint(0, 600) - 300, 80, 13, 13, 'enemy')])

#Meniul
def main_menu():
    while True:
        global screen, Window_display
        Window_display.fill((0,0,0))
        Window_display.blit(screenground, (0, 0))
        screen.blit(pygame.transform.scale(Window_display,(pygame.display.Info().current_w, pygame.display.Info().current_h)), (0, 0))
        s.draw_text('main menu', font, (255, 255, 255), screen, 20, 20)
 
        mx, my = pygame.mouse.get_pos()
 
        button_1 = pygame.Rect(50, 100, 200, 50)
        button_2 = pygame.Rect(50, 200, 200, 50)
        if button_1.collidepoint((mx, my)):
            if click:
                game()
        if button_2.collidepoint((mx, my)):
            if click:
                options()
        joc = pygame.draw.rect(screen, (255, 0, 0), button_1)
        optiuni = pygame.draw.rect(screen, (255, 0, 0), button_2)
        system_font = pygame.font.SysFont('arial', 50)
        joc_text = system_font.render("Joc", True, (255, 255, 255))
        optiune_text = system_font.render("Optiuni", True, (255, 255, 255))
        screen.blit(joc_text, (joc.width//1.75, joc.height*2))
        screen.blit(optiune_text, (optiuni.width//2.50, optiuni.height*4))
 
        click = False
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
 
        pygame.display.update()
        clock.tick(60)

#Jocul
def game():
    running = True
    while running:
        #FILL
        display.fill((255, 255, 255))

        #Globalizare
        global mobil_dreapta, mobil_stanga, impuls_vertical, timp_aer, jucator_flip

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

                if jucator.obi.rect.colliderect(inamic[1].obi.rect):
                    impuls_vertical = -4
        
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
        
        screen.blit(pygame.transform.scale(display,(pygame.display.Info().current_w, pygame.display.Info().current_h)),(0,0))
        pygame.display.update()
        clock.tick(60)

#Optinuile
def options():
    running = True
    while running:
        Window_display.fill((0,0,0))
        Window_display.blit(screenground, (0, 0))
        screen.blit(pygame.transform.scale(Window_display,(pygame.display.Info().current_w, pygame.display.Info().current_h)),(0,0))
 
        s.draw_text('options', font, (255, 255, 255), screen, 20, 20)
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