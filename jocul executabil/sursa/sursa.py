import pygame, math, os, random #import la librarii
from pygame.locals import * #in localele pygame impor steluta (adica toate obiectele prezente in fisierele python chiar si modularele acesteia in programul curent)

#Culoarea_De_Baza
global e_colorkey #globalizeaza variabila
e_colorkey = (255, 255, 255) #variabila primeste o culoare/nonculoare in momentul acesta este nonculoarea alba

def set_global_colorkey(ALB):#acesta este un subprogram
    global e_colorkey
    e_colorkey = ALB #acum ALB are valoratea variabile e_culoare_cheie

#Coliziune_test
def collision_test(obiectul_1, obiectul_lista):
    collision_lista = [] #o lista se scrie in paranteze drepte
    for obi in obiectul_lista: #este un for loop, adica in C++ for(i=1; i<=n; i++)
       if obi.colliderect(obiectul_1): #este un if ca-n C++
           collision_lista.append(obi) #append = adauga/pentru obiectul_1 ce ii daruiesti
    return collision_lista #returneaza valoarea variabilei

#Fizici
class fizici_obi(object): #clasele pot avea variabile, liste, tuples, subprograme s.a.m.d
    def __init__(self, x, y, x_marime, y_marime):
        self.latime = x_marime
        self.inaltime = y_marime
        self.rect = pygame.Rect(x, y, self.latime, self.inaltime) #rect este o abreviere pentru rectangle, adica dreptunghi
        self.x = x
        self.y = y
    
    def miscare(self, miscare, platforma, rampe=[]):
        self.x += miscare[0]
        self.rect.x = int(self.x) #il face numar
        bloc_ciocnire_liste = collision_test(self.rect,platforma)
        tipuri_coliziuni = {'top':False,'bottom':False,'right':False,'left':False,'slant_bottom':False,'data':[]} #un dictionar se scrie in paranteze ondulate
        #Date pentru "tipuri_coliziuni"
        for bloc in bloc_ciocnire_liste:
            semne = [False,False,False,False]
            if miscare[0] > 0:
                self.rect.right = bloc.left
                tipuri_coliziuni['right'] = True
                semne[0] = True
            elif miscare[0] < 0: #elif este o abreviere de la else if
                self.rect.left = bloc.right
                tipuri_coliziuni['left'] = True
                semne[1] = True
            tipuri_coliziuni['data'].append([bloc, semne])
            self.x = self.rect.x
        self.y += miscare[1]
        self.rect.y = int(self.y)
        bloc_ciocnire_liste = collision_test(self.rect, platforma)
        for bloc in bloc_ciocnire_liste:
            semne = [False,False,False,False]
            if miscare[1] > 0:
                self.rect.bottom= bloc.top
                tipuri_coliziuni['bottom'] = True
                semne[2] = True
            elif miscare[1] < 0:
                self.rect.top = bloc.bottom
                tipuri_coliziuni['top'] = True
                semne[3] = True
            tipuri_coliziuni['data'].append([bloc, semne])
            self.schimba_y = 0
            self.y = self.rect.y
        return tipuri_coliziuni

#Entitati
def simpla_entitate(x, y, e_tip): #Inceputul
    return entitate(x, y, 1, 1, e_tip)

def flip(img, boolean=True): #boolean inseamna un o notatie algebrica ce este folosita pentru a reprezenta propozitii logice
    return pygame.transform.flip(img, boolean, False) #transforma ce este in paranteza

def blit_centru(suprafata, suprafata2, pozitie): #Centrarea suprafetei
    x = int(suprafata2.get_width()/2) #primeste suprafata doi latime
    y = int(suprafata2.get_height()/2) #primeste suprafata doi inaltime
    suprafata.blit(suprafata2,(pozitie[0]-x, pozitie[1]-y))

class entitate(object): #Crearea entitatii
    global animatii_date, animatii_superior_date

    def __init__(self, x, y, x_marime, y_marime, e_tip): #Valorile entitatii
        self.x = x
        self.y = y
        self.x_marime = x_marime
        self.y_marime = y_marime
        self.obi = fizici_obi(x, y, x_marime, y_marime)
        self.animatii = None
        self.imagine = None 
        self.animatii_frame = 0
        self.animatii_tags = []
        self.flip = False
        self.decalaj = [0,0]
        self.rotatii = 0
        self.tip = e_tip
        self.acitune_timer = 0
        self.actiune = ''
        self.set_action('idle')
        self.entitate_date = {}
        self.alfa = None
        self.stat = True
        self.vel = 5
        self.health = 10
        self.visible = True
    
    def set_pozitie(self, x, y): #Pozitiile
        self.x = x
        self.y = y
        self.obi.x = x 
        self.obi.y = y 
        self.obi.rect.x = x
        self.obi.rect.y = y 
    
    def miscare(self, moment, platforma, rampe=[]): #Cand entitatea se loveste de un obiect
        coliziuni = self.obi.miscare(moment, platforma, rampe)
        self.x = self.obi.x
        self.y = self.obi.y
        return coliziuni
    
    def hit(self):
        if self.health > 0:
            self.health -= 1
        else:
            self.visible = False
        print('hit')
    
    def rect(self): 
        return pygame.Rect(self.x, self.y, self.x_marime, self.y_marime)
    
    def set_flip(self, boolean): #Flip 
        self.flip = boolean
    
    def set_animatii_tags(self, tags): #Tiprui de animatii
        self.animatii_tags = tags
    
    def set_animatii(self, secventa): #Animatii
        self.animatii = secventa
        self.animatii_frame = 0
    
    def set_action(self, action_id, force=False): #Actiune
        if(self.actiune == action_id) and (force == False):
            pass #Trece
        else:
            self.actiune = action_id
            anim = animatii_superior_date[self.tip][action_id]
            self.animatii = anim[0]
            self.set_animatii_tags(anim[1])
            self.animatii_frame = 0
    
    def get_entitate_unghi(self, entitate_2): #Entitatea primeste un unghi
        x1 = self.x + int(self.x_marime/2)
        y1 = self.y + int(self.y_marime/2)
        x2 = entitate_2.x+int(entitate_2.x_marime/2)
        y2 = entitate_2.y+int(entitate_2.y_marime/2)
        unghi = math.atan((y2-y1)/(x2-x1))
        if x2 < x1:
            unghi += math.pi
        return unghi
    
    def get_centru(self): #Centreaza pozitiile
        x = self.x + int(self.x_marime/2)
        y = self.y + int(self.y_marime/2)
        return [x, y]
    
    def animatii_clare(self): #Pentru claritate
        self.animatii = None
    
    def set_imagine(self, imagine): #Primeste imagine
        self.imagine = imagine
    
    def set_decalaj(self, decalaj): #Ofset/decalaj
        self.decalaj = decalaj
    
    def set_frame(self, cantitate): #Primeste cadrul animatiei
        self.animatii_frame = cantitate
    
    def conduce(self): #Cum actioneaza
        self.acitune_timer += 1
        self.change_frame(1)
    
    def change_frame(self, cantitate): #Schimba cadrul animatiei
        self.animatii_frame += cantitate
        if self.animatii != None:
            while self.animatii_frame < 0:
                if 'loop' in self.animatii_tags:
                    self.animatii_frame += len(self.animatii)
                else:
                    self.animatii = 0
            while self.animatii_frame >= len(self.animatii):
                if 'loop' in self.animatii_tags:
                    self.animatii_frame -= len(self.animatii)
                else:
                    self.animatii_frame = len(self.animatii)-1
    
    def get_curent_img(self): #Primeste imaginea curenta
        if self.animatii == None:
            if self.animatii != None:
                return flip(self.animatii, self.flip)
            else:
                return None 
        else:
            return flip(animatii_date[self.animatii[self.animatii_frame]], self.flip)
    
    def get_desen_img(self): #Schimba desenul in imagine pentru display
        imagine_in_randare = None
        if self.animatii == None:
            if self.imagine != None:
                imagine_in_randare = flip(self.imagine, self.flip).copy()
        else:
            imagine_in_randare = flip(animatii_date[self.animatii[self.animatii_frame]], self.flip).copy()
        if imagine_in_randare != None:
            x_centru = imagine_in_randare.get_width()/2
            y_centru = imagine_in_randare.get_height()/2
            imagine_in_randare = pygame.transform.rotate(imagine_in_randare, self.rotatii)
            if self.alfa != None:
                imagine_in_randare.set_alpha(self.alfa)
            return imagine_in_randare, x_centru, y_centru
    
    def display(self, suprafata, scroll): #Acesta este display-ul
        imagine_in_randare = None 
        if self.animatii == None: 
            if self.imagine != None:
                imagine_in_randare = flip(self.imagine, self.flip).copy()
        else:
            imagine_in_randare = flip(animatii_date[self.animatii[self.animatii_frame]], self.flip).copy()
        if imagine_in_randare != None:
            x_centru = imagine_in_randare.get_width()/2
            y_centru = imagine_in_randare.get_height()/2
            imagine_in_randare = pygame.transform.rotate(imagine_in_randare, self.rotatii)
            if self.alfa != None:
                imagine_in_randare.set_alpha(self.alfa)
            blit_centru(suprafata, imagine_in_randare, (int(self.x)-scroll[0]+self.decalaj[0]+x_centru, int(self.y)-scroll[1]+self.decalaj[1]+y_centru))
    def display_return(self, suprafata, scroll): #Acesta este display-ul
            imagine_in_randare = None 
            if self.animatii == None: 
                if self.imagine != None:
                    imagine_in_randare = flip(self.imagine, self.flip).copy()
            else:
                imagine_in_randare = flip(animatii_date[self.animatii[self.animatii_frame]], self.flip).copy()
            if imagine_in_randare != None:
                x_centru = imagine_in_randare.get_width()/2
                y_centru = imagine_in_randare.get_height()/2
                imagine_in_randare = pygame.transform.rotate(imagine_in_randare, self.rotatii)
                if self.alfa != None:
                    imagine_in_randare.set_alpha(self.alfa)
                return (int(self.x)-scroll[0]+self.decalaj[0]+x_centru, int(self.y)-scroll[1]+self.decalaj[1]+y_centru)

class player():
    pass
#Animatii
animatii_date = {}
animatii_superior_date = {}

def animatii_secventa(secventa, cale_base, colorkey = (255, 255, 255), transparenta = 255): #Schimbarea animatiilor in timpul unor actiuni
    global animatii_date
    rezulta = []
    for frame in secventa:
        imagine_id = cale_base + cale_base.split('/')[-2] + '_' + str(frame[0])
        imagine = pygame.image.load(imagine_id + '.png').convert()
        imagine.set_colorkey(colorkey)
        imagine.set_alpha(transparenta)
        animatii_date[imagine_id] = imagine.copy()
        for i in range(frame[1]):
            rezulta.append(imagine_id)
    return rezulta

def get_frame(ID): #Primeste cadru
    global animatii_date
    return animatii_date[ID]

def load_animatii(cale): #Incarcarea animatiilor
    global animatii_superior_date, e_colorkey
    f = open(cale + 'animatia_entitatiilor.txt', 'r')
    date = f.read() #Intrarea in fisier
    f.close() #Iesirea din fisier
    for animatii in date.split('\n'):
        sectiune = animatii.split(' ')
        animatie_cale = sectiune[0]
        informatia_entitatii = animatie_cale.split('/')
        tipul_entitatii = informatia_entitatii[0]
        animatia_id = informatia_entitatii[1]
        timpul = sectiune[1].split(';')
        tags = sectiune[2].split(';')
        secventa = []
        n = 0
        for timp in timpul:
            secventa.append([n,int(timp)])
            n += 1 
        anim = animatii_secventa(secventa, cale + animatie_cale, e_colorkey)
        if tipul_entitatii not in animatii_superior_date:
            animatii_superior_date[tipul_entitatii] = {}
        animatii_superior_date[tipul_entitatii][animatia_id] = [anim.copy(), tags]

#Text
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

#Portiune
CHUNK_SIZE = 8
def generare_portiune(x,y):
    portiune_data = []
    for pozitia_y in range(CHUNK_SIZE):
        for pozitia_x in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + pozitia_x
            target_y = y * CHUNK_SIZE + pozitia_y
            tipul_suprafetei = 0 #Nu este nimica
            if target_y > 10:
                tipul_suprafetei = 2 #Este pamantul
            elif target_y == 10:
                tipul_suprafetei = 1 #Este suprafata pamantului
            elif target_y == 9:
                if random.randint(1,5) == 1:
                    tipul_suprafetei = 3 #Este iarba
            if tipul_suprafetei != 0:
                portiune_data.append([[target_x,target_y], tipul_suprafetei])
    return portiune_data

#Rezolutie
class rezolutie():
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def set_window(self):
        return pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
    
    def suprafata(self, zoom):
        return pygame.Surface((pygame.display.Info().current_w//zoom, pygame.display.Info().current_h//zoom))
    
    def display_hw(self, ecran):
        self.ecran = ecran
        ecran = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        return ecran
    

#Particule
def fisierul_particulelor_sortare(l):
    l2 = []
    for obi in l:
        l2.append(int(obi[:-4]))
    l2.sort()
    l3 = []
    for obi in l2:
        l3.append(str(obi) + '.png')
    return 13

global imagine_particule
imagine_particule = {}

def incarcare_particule_imagine(cale):
    global imagine_particule, e_colorkey
    lista_fisiere = os.listdir(cale)
    for fisier in lista_fisiere:
        try: #Incearca
            imagine_lista = os.listdir(cale + '/' + fisier)
            imagine_lista = fisierul_particulelor_sortare(imagine_lista)
            imagine = []
            for img in imagine_lista:
                imagine.append(pygame.image.load(cale + '/' + fisier + '/' + imagine).convert())
            for img in imagine:
                img.set_colorkey(e_colorkey)
            imagine_particule[fisier] = imagine.copy()
        except: #Cu exceptia
            pass

class particule(object):
    def __init__(self, x, y, tipul_particulei, miscare, rata_slabirii, frame_incepe, culoarea_personalizat = None):
        self.x = x 
        self.y = y
        self.tip = tipul_particulei
        self.miscare = miscare
        self.rata_slabirii = rata_slabirii
        self.culoare = culoarea_personalizat
        self.frame = frame_incepe
    
    def desen(self, suprafata, scroll):
        global imagine_particule
        if self.frame > len(imagine_particule[self.tip])-1:
            self.frame = len(imagine_particule[self.tip])-1
        if self.culoare == None:
            blit_centru(suprafata, imagine_particule[self.tip][int(self.frame)], (self.x - scroll[0], self.y - scroll[1]))
        else:
            blit_centru(suprafata, schimb_culoare(imagine_particule[self.tip][int(self.frame)], (255, 255, 255), self.culoare), (self.x - scroll[0], self.y - scroll[1]))

    def update(self):
        self.frame += self.rata_slabirii
        alearga = True
        if self.frame > len(imagine_particule[self.tip])-1:
            alearga = False
        self.x += self.miscare[0]
        self.y += self.miscare[1]
        return alearga

#Alte functii folositoare
def schimb_culoare(img, vechea_culoare, noua_culoare):
    global e_colorkey
    img.set_colorkey(vechea_culoare)
    surf = img.copy()
    surf.fill(noua_culoare)
    surf.blit(img, (0, 0))
    surf.set_colorkey(e_colorkey)
    return surf

