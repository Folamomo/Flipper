
import pygame

class Ball(pygame.sprite.Sprite):
    def __init__ (self, position, velocity=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.add(balls)
        self.position=pygame.math.Vector2(position)
        self.velocity=pygame.math.Vector2(velocity)
        self.image, self.rect=load_image("ball.png", -1)
        self.radius=self.rect.w/2
    def bounce (self, normal, material):
        if self.velocity.angle_to(normal)>90 or self.velocity.angle_to(normal)<-90:
            self.velocity-=normal*self.velocity.dot(normal)*(1+material.bouncines) #using analitic geometry (magic)
     
    def colision_detection (self, coliders): 
        for colider in coliders.sprites(): 
            if type(colider) is Edge:
                if self.radius > colider.normal.x*(self.position.x-colider.start.x)+colider.normal.y*(self.position.y-colider.start.y): #distance from enge<radius
                    if 0<colider.normal.y*(self.position.x-colider.start.x)-colider.normal.x*(self.position.y-colider.start.y):         #inside box
                        if 0<-colider.normal.y*(self.position.x-colider.end.x)+colider.normal.x*(self.position.y-colider.end.y):
                            if 0 < colider.normal.x*(self.position.x-colider.start.x)+colider.normal.y*(self.position.y-colider.start.y):
                                self.bounce(colider.normal, colider.material)
                            
            elif type(colider) is Circle: 
                if self.radius+colider.radius>(self.position-colider.position).length():
                    self.bounce((self.position-colider.position).normalize(), colider.material)
                    
    def update (self):
        self.gravity()
        
        #colision check
        self.colision_detection(coliders)
        
        self.position+=self.velocity*dt*options.speed
        self.rect.center=self.position
    def gravity (self):
        self.velocity+=pygame.math.Vector2(0, options.g)*dt*options.speed