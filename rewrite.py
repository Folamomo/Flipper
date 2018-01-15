import pygame
vect1=pygame.math.Vector2(1, 0)
vect2=pygame.math.Vector2(1, 0)

for i in range(365):
    print(vect1.angle_to(vect2))
    vect2=vect2.rotate(1)
    