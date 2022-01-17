# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 12:08:07 2022

@author: alton
"""

import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
#IMG_PATH = "C:\Users\alton\LocalDocuments\python scripts\AI Flappy Bird\imgs"

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

GEN = 0


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20 #ROTATION VELOCITY
    ANIMATION_TIME = 5 #ANIMATION TIME (HOW LONG WE SHOW EACH BIRDS ANIMATION)



    #initilazing
    def __init__(self,x,y):
        self.x = x #start position
        self.y = y #start position
        self.tilt = 0 #how much img is tilted (start at 0 since bird just started game)
        self.tick_count = 0 #used to figure out physics when moving bird
        self.vel = 0 #not moving when start
        self.height = self.y
        self.img_count = 0 #so we know which image is shown for bird
        self.img = self.IMGS[0] #references images to show correct bird



    #setting what happens when bird jumps
    def jump(self):
        self.vel = -10.5 #negative because 0,0 is at top left so need to degrees y cord to move up
        self.tick_count = 0 #keeps track of last jump
        self.height = self.y #keeps track of where bird started moving from



    #setting what happens when bird moves
    def move(self):
        self.tick_count += 1

        d = self.vel*self.tick_count + 1.5 * self.tick_count**2
        # -10.5 + 1.5 = -9 (on first tick moving up 9 changes after each tick)

        if d >= 16: #fail safe (also terminal velocity)
            d = 16

        if d < 0: #smooth out moving upward
            d -=2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50: #every time we jump keeping track of where our bird position is and if so will continue to move upward until below a certain point and then will tilt bird down
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL



    #drawing everything into window
    def draw(self,win):
        self.img_count += 1

        #this all checks which image to show based on animation time (less than 5,10,15,20,21) loops through 3 images for animation basiaclly 
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        #rotating image and reseting center to actual center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x,self.y)).center)
        #blit just means to draw
        win.blit(rotated_image, new_rect.topleft)


    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    GAP = 200
    VEL = 5
    
    def __init__(self,x):
        self.x = x
        self.height = 0
        #self.gap = 100
        
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.passed = False
        self.set_height()
        
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP
        
    def move(self):
        self.x -= self.VEL
        
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        #offset used to see how far objects are from each other and rounding y because cant have negative or decimals
        top_offset = (self.x - bird.x, self.top - round(bird.y))   
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        
        if t_point or b_point: 
            return True
        
        return False
    

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    # orginally had gap with just 2 so created third to overlay onto middle of two 
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = round(self.WIDTH / 2)
        self.x3 = self.WIDTH

        
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        self.x3 -= self.VEL
        
        if self.x1 + self.WIDTH <= 0:
            self.x1 = self.x3 + round(self.WIDTH / 2)

            
        if self.x2 + self.WIDTH <= 0:
            self.x2 = self.x1 + round(self.WIDTH / 2)
            
        if self.x3 + self.WIDTH <= 0:
            self.x3 = self.x2 + round(self.WIDTH / 2)
            
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        win.blit(self.IMG, (self.x3, self.y))
        


def draw_window(win, birds, pipes, base, score, gen):
#This is used to scale images not doing though cause distorts img need a higher resolution or something else =============================================================================
#     bg_img = BG_IMG
#     bg_img = pygame.transform.scale(bg_img, (1280, 720))
#     rect = bg_img.get_rect()
#     rect = rect.move((0,0))
#     win.blit(bg_img, rect)
# =============================================================================
   
    win.blit(BG_IMG, (0,0))
    
    for pipe in pipes:
        pipe.draw(win)
        
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    
    text = STAT_FONT.render("Gen: " + str(GEN), 1, (255,255,255))
    win.blit(text, (10, 10))
    
    text = STAT_FONT.render("Pop: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(text, (10 , 65))
    
    base.draw(win)
    
    for bird in birds:
        bird.draw(win)
    pygame.display.update()





def main(genomes,config): #can be called eval_fitness or genomes what ever is wanted
    global GEN 
    GEN += 1

    nets = []
    ge = []
    birds = []
    

    for _, g in genomes: #genomes is a topil has genome id and object
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
        

    #bird = Bird(230,350)
    base = Base(730)
    pipes = [Pipe(700)]
    win = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    pygame.display.set_caption('Test')
    #pygame.display.flip()
    #win.blit(BG_IMG, (0,0))
    clock = pygame.time.Clock()
    
    score = 0
    
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
                
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break
                
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.01 #should be += 0.1 changing to mess around
            
            #creates a list of output nerons
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            
            if output[0] > 0.5:
                bird.jump()
                
        #bird.move() 
        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    #birds.remove(bird)
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                    
            
                
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
                    
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
                
                
            pipe.move()
        
        if add_pipe:
            score += 1
            #print(str(score))
            for g in ge:
                g.fitness += 1 #Had at 5 to begin with but birds are too good
            pipes.append(Pipe(600))
            
        for r in rem:
            pipes.remove(r)
            
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                ge[x].fitness -= 1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
           
        if bird.y + bird.img.get_height() > 730:
            pass
        
        
        if score > 5 * len(birds):
            break
        
        base.move()
        draw_window(win, birds, pipes, base, score, GEN)
        
    #pygame.quit()
    
    
#main()

def run(configt_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(main,50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
    

    
    