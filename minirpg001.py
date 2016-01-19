# -*- coding: utf-8 -*-
"""
003_static_blit_pretty.py
static blitting and drawing (pretty version)
url: http://thepythongamebook.com/en:part2:pygame:step003
author: horst.jens@spielend-programmieren.at
licence: gpl, see http://www.gnu.org/licenses/gpl.html

works with pyhton3.4 and python2.7

Blitting a surface on a static position
Drawing a filled circle into ballsurface.
Blitting this surface once.
introducing pygame draw methods
The ball's rectangular surface is black because the background
color of the ball's surface was never defined nor filled."""



##  to do fix buggy movement (up=down) ai movement for ketturkat ##



from __future__ import print_function, division
import pygame
import os
import random
import math

GRAD = math.pi / 180 # 2 * pi / 360   # math module needs Radiant instead of Grad 

def radians_to_degrees(radians):
    return(radians / math.pi) * 180.0

def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)    

def showkeys():
    lines = ["Movement = cursor keys",
             "v = Spawn snowman turret",
             "space = shoot"]
    return lines
    

def write(msg="paolo is cool", color=(0,0,0)):
        """write text into pygame surfaces"""
        myfont = pygame.font.SysFont("None", 32)
        mytext = myfont.render(msg, True, color)
        mytext = mytext.convert_alpha()
        return mytext

def elastic_collision(sprite1, sprite2):
        """elasitc collision between 2 sprites (calculated as disc's).
           The function alters the dx and dy movement vectors of both sprites.
           The sprites need the property .mass, .radius, .x, .y, .dx, dy
          
            physic function from Leonard Michlmayr
          """
        # here we do some physics: the elastic
        # collision
        #
        # first we get the direction of the push.
        # Let's assume that the sprites are disk
        # shaped, so the direction of the force is
        # the direction of the distance.
        dirx = sprite1.x - sprite2.x
        diry = sprite1.x - sprite2.y
        #
        # the velocity of the centre of mass
        sumofmasses = sprite1.mass + sprite2.mass
        sx = (sprite1.dx * sprite1.mass + sprite2.dx * sprite2.mass) / sumofmasses
        sy = (sprite1.dy * sprite1.mass + sprite2.dy * sprite2.mass) / sumofmasses
        # if we sutract the velocity of the centre
        # of mass from the velocity of the sprite,
        # we get it's velocity relative to the
        # centre of mass. And relative to the
        # centre of mass, it looks just like the
        # sprite is hitting a mirror.
        #
        bdxs = sprite2.dx - sx
        bdys = sprite2.dy - sy
        cbdxs = sprite1.dx - sx
        cbdys = sprite1.dy - sy
        # (dirx,diry) is perpendicular to the mirror
        # surface. We use the dot product to
        # project to that direction.
        distancesquare = dirx * dirx + diry * diry
        if distancesquare == 0:
            # no distance? this should not happen,
            # but just in case, we choose a random
            # direction
            dirx = random.randint(0,11) - 5.5
            diry = random.randint(0,11) - 5.5
            distancesquare = dirx * dirx + diry * diry
        dp = (bdxs * dirx + bdys * diry) # scalar product
        dp /= distancesquare # divide by distance * distance.
        cdp = (cbdxs * dirx + cbdys * diry)
        cdp /= distancesquare
        # We are done. (dirx * dp, diry * dp) is
        # the projection of the velocity
        # perpendicular to the virtual mirror
        # surface. Subtract it twice to get the
        # new direction.
        #
        # Only collide if the sprites are moving
        # towards each other: dp > 0
        if dp > 0:
            sprite2.dx -= 2 * dirx * dp 
            sprite2.dy -= 2 * diry * dp
            sprite1.dx -= 2 * dirx * cdp 
            sprite1.dy -= 2 * diry * cdp
    # ----------- classes ------------------------
    
class Text(pygame.sprite.Sprite):
        """a pygame Sprite displaying text"""
        def __init__(self, msg="The Ketturkat Game Book", color=(0,0,0)):
            self.groups = PygView.allgroup
            self._layer = 1
            pygame.sprite.Sprite.__init__(self, self.groups)
            self.newmsg(msg,color)
            
        def update(self, time):
            pass # allgroup sprites need update method that accept time
        
        def newmsg(self, msg, color=(0,0,0)):
            self.image =  write(msg,color)
            self.rect = self.image.get_rect()
            
class Lifebar(pygame.sprite.Sprite):
        """shows a bar with the hitpoints of a sprite by dirk ketturkat
           with a given bossnumber, the Lifebar class can 
           identify the BOSS (FLYING OBJECT sprite) with this codeline:
           FlyingObject.objects[bossnumber] """
           
        def __init__(self, boss):
            self.groups = PygView.allgroup
            self.boss = boss
            self._layer = self.boss._layer
            pygame.sprite.Sprite.__init__(self, self.groups)
            self.oldpercent = 0
            self.height=7
            self.color=(94,76,29)
            self.bossdistance=10
            self.paint()
            
        def paint(self):
            self.image = pygame.Surface((self.boss.rect.width,self.height))
            self.image.set_colorkey((0,0,0)) # black transparent
            pygame.draw.rect(self.image, self.color, (0,0,self.boss.rect.width,self.height),1)
            self.rect = self.image.get_rect()
 
        def update(self, seconds):
            self.percent = self.boss.hitpoints / self.boss.hitpointsfull * 1.0
            if self.percent != self.oldpercent:
                self.paint() # important ! boss.rect.width may have changed (because rotating)
                pygame.draw.rect(self.image, (0,0,0), (1,1,self.boss.rect.width-2,self.height-2)) # fill black
                pygame.draw.rect(self.image, self.color, (1,1,
                                 int(self.boss.rect.width * self.percent),self.height-2),0) # fill green
            self.oldpercent = self.percent
            self.rect.centerx = self.boss.rect.centerx
            self.rect.centery = self.boss.rect.centery - self.boss.rect.height /2 - self.bossdistance
            if self.boss.hitpoints < 1:   #check if boss is still alive
                self.kill() # kill the hitbar

    
        def draw_text(self, text):
            """Center text in window
            """
            fw, fh = self.font.size(text)
            surface = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(surface, (50,150))
            
class Fragment(pygame.sprite.Sprite):
        """generic Fragment class. Inherits to blue Fragment (implosion),
           red Fragment (explosion), smoke (black) and shots (purple)"""
        def __init__(self, x,y, layer = 9):
            self._layer = layer
            pygame.sprite.Sprite.__init__(self, self.groups)
            self.pos = [x,y]
            self.fragmentmaxspeed = 1500# try out other factors !
            self.dx = (random.random() - 0.5) * self.fragmentmaxspeed
            self.dy = (random.random() - 0.5) * self.fragmentmaxspeed
            self.init2()

        def init2(self):  # split the init method into 2 parts for better access from subclasses
            self.color=(128,0,0)
            self.lifetime = random.random() * 6
            self.image = pygame.Surface((10,10))
            self.image.set_colorkey((0,0,0)) # black transparent
            pygame.draw.circle(self.image, self.color, (5,5), random.randint(2,5))
            self.image = self.image.convert_alpha()
            self.rect = self.image.get_rect()
            self.rect.center = self.pos #if you forget this line the sprite sit in the topleft corner
            self.time = 0.0
            
        def update(self, seconds):
            self.time += seconds
            if self.time > self.lifetime:
                self.kill() 
            self.pos[0] += self.dx * seconds
            self.pos[1] += self.dy * seconds
            self.rect.centerx = round(self.pos[0],0)
            self.rect.centery = round(self.pos[1],0)
       
class EvilSnowman (pygame.sprite.Sprite):
    """an evil snowman turret"""
    def __init__(self):
        self._layer = 8
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = random.randint(0,PygView.width)
        self.y = random.randint(0,PygView.height)
        self.color = (200,20,200)
        self.image = pygame.Surface((30,60))
        pygame.draw.circle(self.image, self.color, (15,20), 7)
        pygame.draw.circle(self.image, self.color, (15,40), 15)
        self.image.set_colorkey((0,0,0)) # black transparent
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)        
        
        
        
    def update(self, seconds):
        if random.random()< 0.01:
            Bullet(self.x,self.y,"1") #0 silas #1 ferris
             
        
 
                   
            
class Bullet(pygame.sprite.Sprite):
    """A projectile"""
    def __init__(self, x,y ,direction):
        self._layer = 9
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        self.direction = direction
        self.speed = 10 + random.random() *100
        self.x = x
        self.y = y
        self.lifetime = 0.0
        self.maxtime = 6.0
        self.target = False
        if self.direction == "up":
            self.dx=0
            self.dy=-self.speed
        
        elif self.direction == "down":
            self.dx=0
            self.dy=self.speed

        elif self.direction == "left":
            self.dx=-self.speed
            self.dy=0
   
        elif self.direction == "right":
            self.dx=self.speed
            self.dy=0
        else:
            self.targetnr = int(direction)
            #self.dx=random.random()*self.speed
            #self.dy=random.random()*self.speed
            self.target = FlyingObject.objects[self.targetnr] 
            self.ix = self.target.x - self.x
            self.iy = self.target.y - self.y
            self.angle = radians_to_degrees(math.atan2(self.iy, -self.ix))+90
            self.ddx = - math.sin(self.angle * GRAD)
            self.ddy = - math.cos(self.angle * GRAD)
            self.dx = self.ddx * self.speed
            self.dy = self.ddy * self.speed
            
        self.color=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.lifetime = random.random() * 6
        self.image = pygame.Surface((10,10))
        self.image.set_colorkey((0,0,0)) # black transparent
        pygame.draw.circle(self.image, self.color, (5,5), 3)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
            
    def update(self, seconds):
        self.lifetime += seconds                                                                                                                                                                      # doppelpunkt de
        
        self.x += self.dx * seconds
        self.y += self.dy * seconds
        
        self.rect.center = (self.x, self.y)
        if self.lifetime > self.maxtime:
            self.kill()
            
            

class Ball(object):
    """this is not a native pygame sprite but instead a pygame surface made by dirk ketturkat"""
    def __init__(self, radius = 50, color=(0,0,255), x=320, y=240):
        """create a (black) surface and paint a blue ball on it"""
        self.radius = radius
        self.color = color
        self.x = x
        self.y = y
        # create a rectangular surface for the ball 50x50
        self.surface = pygame.Surface((2*self.radius,2*self.radius))    
        # pygame.draw.circle(Surface, color, pos, radius, width=0) # from pygame documentation
        pygame.draw.circle(self.surface, color, (radius, radius), radius) # draw blue filled circle on ball surface
        self.surface = self.surface.convert() # for faster blitting. 
        # to avoid the black background, make black the transparent color:
        # self.surface.set_colorkey((0,0,0))
        # self.surface = self.surface.convert_alpha() # faster blitting with transparent color
        
    def blit(self, background):
        """blit the Ball on the background"""
        background.blit(self.surface, ( self.x, self.y))

class FlyingObject(pygame.sprite.Sprite):
        """generic Bird class, to be called from SmallBird and BigBird"""
        image=[]  # list of all images
        number = 0
        objects={}
        
        def __init__(self, area, layer = 4,hitpoints=100,imagenr=0,grid=50,gridmaxx=13,gridmaxy=8,ai=0):
            #self.groups = PygView.allgroup, PygView.gravitygroup # assign groups 
            self._layer = layer                   # assign level
            #self.layer = layer
            pygame.sprite.Sprite.__init__(self,  self.groups  ) #call parent class. NEVER FORGET !
            #self.area = PygView.screen.get_rect()
            self.area = area
            self.rotatespeed = 10.0
            self.speed = 70.0
            self.x= 0
            self.y= 0
            self.ai = ai
            self.targetx = 0
            self.targety = 0
            self.oldx = 0
            self.oldy = 0
            self.automove = ""
            self.direction = "right"
            self.gridmaxx=gridmaxx
            self.gridmaxy=gridmaxy
            self.grid=grid
            self.ddx = 0.0
            self.ddy = 0.0
            self.image = FlyingObject.image[imagenr]
            self.image0 = FlyingObject.image[imagenr]
            self.hitpoints = float(hitpoints) # actual hitpoints
            self.hitpointsfull = float(hitpoints) # maximal hitpoints
            self.rect = self.image.get_rect()
            self.radius = max(self.rect.width, self.rect.height) / 2.0
            self.dx = 0   # wait at the beginning
            self.dy = 0            
            #self.waittime = Bird.waittime # 1.0 # one second
            #self.lifetime = 0.0
            self.rect.center = (-100,-100) # out of visible screen
            self.frags = 125 # number of framgents if Bird is killed
            self.number = FlyingObject.number # get my personal Birdnumber
            FlyingObject.number+= 1           # increase the number for next Bird
            FlyingObject.objects[self.number] = self # store myself into the Bird dictionary
            #print("my number %i Bird number %i and i am a %s " % (self.number, Bird.number, getclassname(self)))
            #-------------------physic------------------
            self.mass = 100.0
            self.angle = 0.0
            #self.boostspeed = 10 # speed to fly upward
            #self.boostmax = 0.9 # max seconds of "fuel" for flying upward
            #self.boostmin = 0.4 # min seconds of "fuel" for flying upward
            #self.boosttime = 0.0 # time (fuel) remaining
            #warpsound.play()
            #for _ in range(8):
            #    BlueFragment(self.pos) # blue Frags
      
        def left(self):
            self.oldx=self.x
            self.oldy=self.y
            #self.x -= self.grid 
            self.targetx = self.x - self.grid
            self.automove = "left" 
            
        def right(self):
            self.oldx=self.x
            self.oldy=self.y
            #self.x += self.grid
            self.targetx = self.x + self.grid
            self.automove = "right"
            
        def up(self):
            self.oldy=self.y
            self.oldx=self.x    
            #self.y -= self.grid
            self.targety = self.y - self.grid
            self.automove = "up"
                
        def down(self):
            self.oldy=self.y
            self.oldx=self.x
            #self.y += self.grid
            self.targety = self.y + self.grid
            self.automove = "down"       
      
        def kill(self):
            # a shower of red fragments, exploding outward
            #for _ in range(self.frags):
            #    RedFragment(self.pos)
            FlyingObject.objects.pop(self.number)
            pygame.sprite.Sprite.kill(self) # kill the actual Bird 
            
        def speedcheck(self):
            #if abs(self.dx) > BIRDSPEEDMAX:
            #   self.dx = BIRDSPEEDMAX * (self.dx/abs(self.dx)) # dx/abs(dx) is 1 or -1
            #if abs(self.dy) > BIRDSPEEDMAX:
            #   self.dy = BIRDSPEEDMAX * (self.dy/abs(self.dy))
            #if abs(self.dx) > 0 : 
            #    self.dx *= FRICTION  # make the Sprite slower over time
            #if abs(self.dy) > 0 :
            #    self.dy *= FRICTION
            pass
            
       
        def gridcheck(self):
           if self.x < self.grid //2:
               self.x = self.grid //2
           if self.x > self.grid * self.gridmaxx:
               self.x = self.grid * self.gridmaxx
           if self.y  < self.grid //2:
               self.y = self.grid //2
           if self.y > self.grid * self.gridmaxy:
               self.y = self.grid * self.gridmaxy       
            
                   
        def areacheck(self):
            if not self.area.contains(self.rect):
                self.crashing = True # change colour later
                # --- compare self.rect and area.rect
                if self.x + self.rect.width/2 > self.area.right:
                    self.x = self.area.right - self.rect.width/2
                    self.dx *= -0.5 # bouncing off but loosing speed
                if self.x - self.rect.width/2 < self.area.left:
                    self.x = self.area.left + self.rect.width/2
                    self.dx *= -0.5 # bouncing off the side but loosing speed
                if self.y + self.rect.height/2 > self.area.bottom:
                    self.y = self.area.bottom - self.rect.height/2
                    self.dy *= -0.5 # bouncing off the ground
                    #if reaching the bottom, the birds get a boost and fly upward to the sky
                    #at the bottom the bird "refuel" a random amount of "fuel" (the boostime)
                    #self.dy = 0 # break at the bottom
                    #self.dx *= 0.3 # x speed is reduced at the ground
                    #self.boosttime = self.boostmin + random.random()* (self.boostmax - self.boostmin)
                if self.y - self.rect.height/2 < self.area.top:
                    self.y = self.area.top + self.rect.height/2
                    self.dy *= -0.5 # stop when reaching the sky
                    #self.dy *= -1 
                    #self.hitpoints -= 1 # reaching the sky cost 1 hitpoint
                    
        def update(self, seconds):
            #---make Bird only visible after waiting time
            #self.lifetime += seconds
            #if self.lifetime > (self.waittime):
            #    self.waiting = False
            #if self.waiting:
            #    self.rect.center = (-100,-100)
            #else: # the waiting time (Blue Fragments) is over
                #if self.boosttime > 0:   # boost flying upwards ?
                #    self.boosttime -= seconds
                #    self.dy -= self.boostspeed # upward is negative y !
                #    self.ddx = -math.sin(self.angle*GRAD) 
                #    self.ddy = -math.cos(self.angle*GRAD) 
                #    Smoke(self.rect.center, -self.ddx , -self.ddy )
           
                #--- calculate actual image: crasing, bigbird, both, nothing ?
               # self.image = Bird.image[self.crashing+self.big] # 0 for not crashing, 1 for crashing
                #self.image0 = Bird.image[self.crashing+self.big] # 0 for not crashing, 1 for crashing
           keys=pygame.key.get_pressed()     
          
           self.ddx = 0.0
           self.ddy = 0.0
           if keys[pygame.K_w]: # forward
                    self.ddx = -math.sin(self.angle*GRAD) 
                    self.ddy = -math.cos(self.angle*GRAD) 
            #        Smoke(self.rect.center, -self.ddx , -self.ddy )
           if keys[pygame.K_s]: # backward
                    self.ddx = +math.sin(self.angle*GRAD) 
                    self.ddy = +math.cos(self.angle*GRAD) 
            #        Smoke(self.rect.center, -self.ddx, -self.ddy )
           if keys[pygame.K_e]: # right side
                    self.ddx = +math.cos(self.angle*GRAD)
                    self.ddy = -math.sin(self.angle*GRAD)
            #        Smoke(self.rect.center, -self.ddx , -self.ddy )
           if keys[pygame.K_q]: # left side
                    self.ddx = -math.cos(self.angle*GRAD) 
                    self.ddy = +math.sin(self.angle*GRAD) 
            #        Smoke(self.rect.center, -self.ddx , -self.ddy )                  
           
           # ------------- movement-------------------------------------
           if self.automove != "":
               if self.ai == 1:
                   self.automove = random.choice(("up","down","left","right"))
               if self.automove == "right":                
                   if self.x < self.targetx:
                       self.dx = self.speed
                   else:
                       self.dx = 0
                       self.x = self.targetx
                       self.automove = ""
                   
               elif self.automove == "left":                   
                   if self.x > self.targetx:
                       self.dx = -self.speed
                   else:
                       self.dx = 0
                       self.x = self.targetx
                       self.automove = ""
                       
               if self.automove == "up":                 
                   if self.y > self.targety:
                       self.dy = -self.speed
                   else:
                       self.dy = 0
                       self.y = self.targety
                       self.automove = ""
                       
               elif self.automove == "down":                   
                   if self.y < self.targety:
                       self.dy = self.speed
                   else:
                       self.dy = 0
                       self.y = self.targety
                       self.automove = ""      
                
        
           self.dx += self.ddx * self.speed
           self.dy += self.ddy * self.speed
           self.x += self.dx * seconds
           self.y += self.dy * seconds
           #self.speedcheck()
           
           self.areacheck() # ------- check if Bird out of screen
           self.oldangle = self.angle
           if keys[pygame.K_a]: # left turn , counterclockwise
               self.angle += self.rotatespeed
           if keys[pygame.K_d]: # right turn, clockwise
               self.angle -= self.rotatespeed 
           
           # ------------- rotate ------------------
           
           #if self.angle != self.oldangle:
           self.oldcenter = self.rect.center
           self.image = pygame.transform.rotate(self.image0, self.angle)
           self.rect = self.image.get_rect()
           self.rect.center = self.oldcenter    
          
           
           #--------- rotate into direction of movement ------------
           #self.angle = math.atan2(-self.dx, -self.dy)/math.pi*180.0 
           #self.image = pygame.transform.rotozoom(self.image0,self.angle,1.0)
           #--- calculate new position on screen -----
           
           
           
           self.gridcheck()
           self.rect.centerx = round(self.x,0)
           self.rect.centery = round(self.y,0)
           if self.hitpoints <= 0:
               self.kill()
        
class PygView(object):   
  
    def __init__(self, width=650, height=400, fps=60):
        """Initialize pygame, window, background, font,...
           default arguments 
        """
        pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        self.width = width
        self.height = height
        PygView.width = width
        PygView.height = height
        self.grid = 50
        self.gridmaxx=13
        self.gridmaxy=8
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()  
        self.background.fill((255,255,255)) # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 24, bold=True)
        self.folder="data"
        self.tiles = {}
        for x in range(self.grid // 2, self.width, self.grid):
            for y in range(self.grid // 2, self.height, self.grid):
                self.tiles[(x, y)] = True
        self.tiles[(self.grid//2 + 10*self.grid, self.grid//2 + 1*self.grid)] = False                 
        self.tiles[(self.grid//2 + 10*self.grid, self.grid//2 + 2*self.grid)] = False                 

        try: # ------- load sound -------
            self.crysound = pygame.mixer.Sound(os.path.join(self.folder,'claws.ogg'))  #load sound
            self.warpsound = pygame.mixer.Sound(os.path.join(self.folder,'wormhole.ogg'))
            self.bombsound = pygame.mixer.Sound(os.path.join(self.folder,'bomb.ogg'))
            self.lasersound = pygame.mixer.Sound(os.path.join(self.folder,'shoot.ogg'))
            self.hitsound = pygame.mixer.Sound(os.path.join(self.folder,'beep.ogg'))
        except:
            print("could not load one of the sound files from folder %s. no sound, sorry" %folder)
        
        #-----------------define sprite groups------------------------
        #birdgroup = pygame.sprite.Group() 
        #bulletgroup = pygame.sprite.Group()
        self.fragmentgroup = pygame.sprite.Group()
        self.gravitygroup = pygame.sprite.Group()
        self.bulletgroup = pygame.sprite.Group()
        self.snowmangroup = pygame.sprite.Group()
        # only the allgroup draws the sprite, so i use LayeredUpdates() instead Group()
        self.allgroup = pygame.sprite.LayeredUpdates() # more sophisticated, can draw sprites in layers 
        FlyingObject.groups=self.allgroup
        EvilSnowman.groups=self.allgroup,self.snowmangroup
        Fragment.groups=self.allgroup,self.fragmentgroup
        Bullet.groups=self.allgroup,self.bulletgroup

        #-------------loading files from data subdirectory -------------------------------
        try: # load images into classes (class variable !). if not possible, draw ugly images
            FlyingObject.image.append(pygame.image.load(os.path.join(self.folder,"babytux.png")))
            FlyingObject.image.append(pygame.image.load(os.path.join(self.folder,"babytux_neg.png")))
            self.bg1=pygame.image.load(os.path.join("data","background2.jpg"))
            self.bg2=pygame.image.load(os.path.join("data","background.jpg"))
        except:
            print("no image files 'babytux.png' and 'babytux_neg.png' in subfolder %s" % folder)
            print("therfore drawing incredibly ugly sprites instead")
        self.silas=FlyingObject(self.screen.get_rect(),imagenr=1)
        self.ferris=FlyingObject(self.screen.get_rect(),imagenr=0)
        self.ketturkat=FlyingObject(self.screen.get_rect(),imagenr=0,ai=1)
        self.ketturkat.x=425
        self.ketturkat.y=225
        self.background=self.bg1

    def paint(self):
        """painting on the surface"""
        
        #------- try out some pygame draw functions --------
        # pygame.draw.rect(Surface, color, Rect, width=0): return Rect
        pygame.draw.rect(self.background, (0,255,0), (50,50,100,25)) # rect: (x1, y1, width, height)
        # pygame.draw.circle(Surface, color, pos, radius, width=0): return Rect
        pygame.draw.circle(self.background, (0,200,0), (200,50), 35)
        # pygame.draw.polygon(Surface, color, pointlist, width=0): return Rect
        pygame.draw.polygon(self.background, (0,180,0), ((250,100),(300,0),(350,50)))
        # pygame.draw.arc(Surface, color, Rect, start_angle, stop_angle, width=1): return Rect
        pygame.draw.arc(self.background, (0,150,0),(400,10,150,100), 0, 3.14) # radiant instead of grad
        # ------------------- blitting a Ball --------------
        for x in range(0,self.width,self.grid):
            pygame.draw.line(self.background, (0,255,35), (x,0),(x,self.height))
        for y in range(0,self.height,self.grid):
            pygame.draw.line(self.background, (0,255,35), (0,y),(self.width,y))
        myball = Ball() # creating the Ball object
        myball.blit(self.background) # blitting it
    
    
    def tilecheck(self,x,y):
        try:
            result = self.tiles[(x,y)]
        except:
            return False
        return result
    
    def run(self):
        """The mainloop
        """
        self.paint() 
        running = True
        self.ferris.x=self.grid//2
        self.ferris.y=self.grid//2
        self.silas.x=self.grid*self.gridmaxx-self.grid//2
        self.silas.y=self.grid*self.gridmaxy-self.grid//2
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("BYE")
                        running = False
                    #  0 key (resets movement)
                    if event.key == pygame.K_UP:
                        self.ferris.direction = "up"
                        if self.tilecheck(int(self.ferris.x),int(self.ferris.y)-self.grid):
                        #if self.tiles[(int(self.ferris.x), int(self.ferris.y)-self.grid)]:
                            self.ferris.up()
                            self.silas.x=self.ferris.oldx
                            self.silas.y=self.ferris.oldy
                    elif event.key == pygame.K_DOWN:
                        self.ferris.direction = "down"
                        if self.tilecheck(int(self.ferris.x), int(self.ferris.y)+self.grid):
                        #if self.tiles[(int(self.ferris.x), int(self.ferris.y)+self.grid)]:
                            self.ferris.down()
                            self.silas.x=self.ferris.oldx
                            self.silas.y=self.ferris.oldy
                    elif event.key == pygame.K_LEFT:
                        self.ferris.direction = "left"
                        if self.tilecheck(int(self.ferris.x)-self.grid, int(self.ferris.y)):
                        #if self.tiles[(int(self.ferris.x)-self.grid, int(self.ferris.y))]:
                            #print(self.ferris.x)
                            if self.background == self.bg2 and (self.ferris.x - self.grid ) <= self.grid//2:
                                self.background = self.bg1
                                self.paint()
                                self.ferris.x = self.grid * self.gridmaxx - self.grid//2       
                            else:
                                self.ferris.left()
                                self.silas.x=self.ferris.oldx
                                self.silas.y=self.ferris.oldy
                            #if self.background == self.bg2 and self.ferris.x < self.width * 0.01:
                            #if self.background == self.bg2 and self.ferris.x < 0:
                            #    self.background = self.bg1
                            #    self.paint()
                            #    self.ferris.x = self.width        
                    elif event.key == pygame.K_RIGHT:
                        self.ferris.direction = "right"
                        #print(self.ferris.x, self.ferris.y, self.tiles.keys())
                        # tile right of ferris is allowed? 
                        
                        if self.tilecheck(int(self.ferris.x)+self.grid, int(self.ferris.y)):
                        #if self.tiles[(int(self.ferris.x)+self.grid, int(self.ferris.y))]:
                            if self.background == self.bg1 and self.ferris.x + self.grid >= self.grid * self.gridmaxx - self.grid//2:
                                self.background = self.bg2
                                self.paint()
                                self.ferris.x = 0
                            
                            else:
                                self.ferris.right()
                                self.silas.x=self.ferris.oldx
                                self.silas.y=self.ferris.oldy
                          #  if self.background == self.bg1 and self.ferris.x > self.width * 0.99:
                          #  if self.background == self.bg1 and self.ferris.x >self.width:
                                
                    #if event.key == pygame.K_0:
                    #    self.ferris.dx=0
                    #    self.ferris.dy=0    
                    #    self.ferris.ddx=0
                    #    self.ferris.ddy=0    
                    if event.key == pygame.K_i:
                        self.silas.up()
                    if event.key == pygame.K_k:
                        self.silas.down()
                    if event.key == pygame.K_j:
                        self.silas.left()        
                    if event.key == pygame.K_l:
                        self.silas.right()
                    if event.key == pygame.K_0: 
                        self.silas.dx=0
                        self.silas.dy=0    
                        self.silas.ddx=0
                        self.silas.ddy=0    
                    # Teleportation                    
                    if event.key == pygame.K_f:
                        self.silas.x=(random.randint(0,640))
                        self.silas.y=(random.randint(0,640)) 
                    elif event.key == pygame.K_g:
                        Fragment(self.silas.x,self.silas.y)
                    elif event.key == pygame.K_v:
                        EvilSnowman()    
                    #bullet
                    if event.key == pygame.K_SPACE:
                        Bullet(self.ferris.x,self.ferris.y,self.ferris.direction)             
            keys=pygame.key.get_pressed()
            #if keys[pygame.K_a]:
            #    self.silas.dx -= 1
            #if keys[pygame.K_d]:
            #    self.silas.dx += 1                   
            #if keys[pygame.K_w]:
            #    self.silas.dy -= 1
            #if keys[pygame.K_s]:
            #    self.silas.dy += 1                   
            #if keys[pygame.K_KP4]:
            #    self.ferris.dx -= 1
            #if keys[pygame.K_KP6]:
            #    self.ferris.dx += 1                   
            #if keys[pygame.K_KP8]:
            #    self.ferris.dy -= 1
            #if keys[pygame.K_KP2]:
            #    self.ferris.dy += 1 
            
            milliseconds = self.clock.tick(self.fps)
            seconds = milliseconds / 1000.0 # seconds passed since last frame
            
            self.playtime += milliseconds / 1000.0
            #self.draw_text("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
            #               self.clock.get_fps(), " "*5, self.playtime))
             # ----------- clear, draw , update, flip -----------------  
             
            # ferrris screenwechsel
            if self.background == self.bg1 and self.ferris.x > self.width * 0.9 and self.ferris.dx > 0:
                self.background = self.bg2
                self.paint()
                self.ferris.x = self.grid // 2
                
            if self.background == self.bg2 and self.ferris.x < self.width * 0.1 and self.ferris.dx < 0:
                self.background = self.bg1
                self.paint()
                self.ferris.x =  self.width // self.grid * self.grid - self.grid//2
            self.allgroup.clear(self.screen, self.background)
            self.allgroup.update(seconds)
            self.allgroup.draw(self.screen) 
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))
            
        pygame.quit()




####

if __name__ == '__main__':

    # call with width of window and fps
    for line in showkeys():
        print(line)
    i=raw_input("press enter")
    PygView().run()
