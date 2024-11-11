import math

import pygame

class Spark:
    def __init__(self, pos, angle,speed):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed

    def update(self):
        """
        when we did particles, we converted polar coord to cartesian coord
        using cos and sin

        this time instead of doing just one conversion
        -> store pos in catresian
        -> angle is polar
        -> speed is length of polar corrdiante

        angle and speed is the polar coord for the velocity vector

        polar to cartesian
        -> cos(angle) for x-axis * speed (for length)
        -> sin(angle) for y-axis * speed (for length)
        """
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        # speed shrinks to 0
        self.speed = max(0, self.speed - 0.1)

        # once the speed is zero, we return true which removes it from the list of sparks
        return not self.speed
    
    def render(self, surf, offset=(0, 0)):
        # creating a thin diamond shape based on the angle of the spark
        # facing right -> horizontal spark
        # facing up -> verticle spark
        # other directions
        render_points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),
            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * 3 - offset[0], self.pos[1] + math.sin(self.angle + math.pi) * self.speed * 3 - offset[1]),
            (self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0], self.pos[1] + math.sin(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[1])
        ]

        """
        takes a surface to render to            -> surf
        takes a color                           -> white
        list of points that creates the polygon -> render_points
        """
        pygame.draw.polygon(surf, (255, 255, 255), render_points)
