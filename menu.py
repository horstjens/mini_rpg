# -*- coding: utf-8 -*-
"""
menu system for pygame
"""


import pygame 
#import simpledefense
import random
import sys
import os.path
import minirpg001
import textscroll1



class Menu(object):
    def __init__(self):
        self.menudict={"root":["Play","Difficulty", "Help", "Credits", "Options","Quit"],
        
                       "Options":["Turn music off","Turn sound off","Change screen resolution"],
                       "Difficulty":["easy","medium","elite","hardcore"],
                       "Change screen resolution":["650x400","800x650","1050x800"],
                       "Credits":["bla1","bla2"],
                       "Help":["how to play", "tips"]                       
                       } 
        self.menuname="root"
        self.oldnames = []
        self.oldnumbers = []
        self.items=self.menudict[self.menuname]
        self.active_itemnumber=0
    
    def nextitem(self):
        if self.active_itemnumber==len(self.items)-1:
            self.active_itemnumber=0
        else:
            self.active_itemnumber+=1
        return self.active_itemnumber
            
    def previousitem(self):
        if self.active_itemnumber==0:
            self.active_itemnumber=len(self.items)-1
        else:
            self.active_itemnumber-=1
        return self.active_itemnumber 
        
    def get_text(self):
        """ change into submenu?"""
        #try:
        text = self.items[self.active_itemnumber]
        #except:
        #   print("exception!")
        #   text = "root"
        if text in self.menudict:
            self.oldnames.append(self.menuname)
            self.oldnumbers.append(self.active_itemnumber)
            self.menuname = text
            self.items = self.menudict[text]
            # necessary to add "back to previous menu"?
            if self.menuname != "root":
                self.items.append("back")
            self.active_itemnumber = 0
            return None
        elif text == "back":
            #self.menuname = self.menuname_old[-1]
            #remove last item from old
            self.menuname =  self.oldnames.pop(-1)
            self.active_itemnumber= self.oldnumbers.pop(-1)
            print("back ergibt:", self.menuname)
            self.items = self.menudict[self.menuname]
            return None
            
        return self.items[self.active_itemnumber] 
        
        
        
            

class PygView(object):

  
    def __init__(self, width=640, height=400, fps=30):
        """Initialize pygame, window, background, font,...
           default arguments 
        """
        
        pygame.mixer.pre_init(44100, -16, 2, 2048) 

        pygame.init()
        
        #jump = pygame.mixer.Sound(os.path.join('data','jump.wav'))  #load sound
        #self.sound1 = pygame.mixer.Sound(os.path.join('data','Pickup_Coin.wav'))
        #self.sound2 = pygame.mixer.Sound(os.path.join('data','Jump.wav'))
        #self.sound3 = pygame.mixer.Sound(os.path.join('data','mix.wav'))
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()  
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 24, bold=True)

    def paint(self):
        """painting on the surface"""
        for i in  m.items:
            n=m.items.index(i)
            if n==m.active_itemnumber:
                self.draw_text("-->",50,  m.items.index(i)*30+10,(0,0,255))
                self.draw_text(i, 100, m.items.index(i)*30+10,(0,0,255))
            else:
                self.draw_text(i, 100, m.items.index(i)*30+10)
                

    def run(self):
        """The mainloop
        """
        #self.paint() 
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key==pygame.K_DOWN:
                        #print(m.active_itemnumber)
                        m.nextitem()
                        print(m.active_itemnumber)
                        #self.sound2.play()
                    if event.key==pygame.K_UP:
                        m.previousitem()
                        #self.sound1.play()
                    if event.key==pygame.K_RETURN:
                        #self.sound3.play()
                        result = m.get_text()
                        #print(m.get_text())
                        print(result)
                        if result=="how to play":
                            text = "Move with arrow keys\nShoot with space"
                            textscroll1.PygView(text).run()
                        if result=="tips":
                            text2 = "When your HP reaches 0, you die! \nYou can eat a Doenertier to get health.\nEvil dogs regenerate health when left alone\nEvil snowmen are stationary\nYou can summon enemy waves with x"
                            textscroll1.PygView(text2).run()    
                        if result=="Play":
                            minirpg001.PygView(width=self.width,height=self.height).run()
                            print("activating external program")
                            # save return 
                            #PygView().run()
                        elif result is not None and "x" in result:
                            
                            left = result.split("x")[0]
                            right = result.split("x")[1]
                            #print(left, str(int(left)))
                            if str(int(left)) == left and str(int(right)) == right:
                                self.width = int(left)
                                self.height = int(right)
                                self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
                                self.background = pygame.Surface(self.screen.get_size()).convert()  
                                self.background.fill((255,255,255)) # fill background white    
                        elif result=="Quit":
                            print("Bye")
                            pygame.quit()
                            sys.exit()
                        

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            self.draw_text("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
                           self.clock.get_fps(), " "*5, self.playtime), color=(30, 120 ,18))
            pygame.draw.line(self.screen,(random.randint(0,255),random.randint(0,255), random.randint(0,255)),(50,self.height - 80),(self.width -50,self.height - 80) ,3)             
            self.paint()
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            
        pygame.quit()


    def draw_text(self, text ,x=50 , y=0,color=(27,135,177)):
        if y==0:
            y= self.height - 50
        
        """Center text in window
        """
        fw, fh = self.font.size(text)
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x,y))

    
####

if __name__ == '__main__':

    # call with width of window and fps
    m=Menu()
    PygView().run()
