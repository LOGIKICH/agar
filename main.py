from pygame import*
from random import randint

init()

WINDOW_SIZE = 800,600
FPS = 60

running = True
lose =  False

screen = display.set_mode(WINDOW_SIZE)
display.set.caption("AGAR.IO")

class Player:
    def __init__(self,x,y,r,name,color=(255,0,0)):
        self.x = x
        self.y = y
        self.r = r
        self.color = color

    def move(self):
        keys = key.get_pressed()
        if keys[K_w]:
            self.y -= 5
        if keys[K_s]:
            self.y += 5
        if keys[K_a]:
            self.y -= 5
        if keys[K_d]:
            self.x += 5

    def draw(self):
        draw.circle(screen,self.color,(self.x,self.y), self.r)

class Food:
    def __init__(self):
        self.x
        self.y
        self.r
        self.color = (randint(10,255),randint(10,255),randint(10,255))
    
    def check_colision(self,player):
        dx = self.x - player.x
        dy = self.y - player.y
        return hypot(dx,dy) < self.r + player.r
    def draw(self):
        draw.circle(screen,self.color,(self.x,self.y), self.r)




clk = time.Clock()
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
    screen.fill((255,255,255))
    scale = max(0.3,min(my_Player.r / 50))
    my_player.move()
    my_player

to_remove = []
for f in Foods:
    if f.check_colision(my_Player):
    my_Player.r += int(f.r * 0.2)
    to_remove.append(f)

else:
    sx

display.update()
clk.tick(FPS)