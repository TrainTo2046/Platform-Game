import sys
import pygame

class Game:
    def __init__(self) -> None:   
        pygame.init()

        SCREEN_WIDTH = 640
        SCREEN_HEIGHT = 480

        pygame.display.set_caption('Platformer Game')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.img = pygame.image.load('data/images/clouds/cloud_1.png')
        # make the black background on the image transparent
        self.img.set_colorkey((0, 0, 0))
        self.img_pos = [160, 260]
        self.movement = [False, False]

        self.collision_area = pygame.Rect(50, 50, 300, 50)

    def run(self):
        # game loop
        while True:
            self.screen.fill((14, 219, 248))
            
            img_r = pygame.Rect(self.img_pos[0], self.img_pos[1], self.img.get_width(), self.img.get_height())
            # collision test
            # if true then two rect: img_r and collision_area are overlapping in some way
            # collision is true
            if img_r.colliderect(self.collision_area):
                # (0, 100, 255) -> color
                pygame.draw.rect(self.screen, (0, 100, 255), self.collision_area)
            else:
                # (0, 50, 155) -> color
                pygame.draw.rect(self.screen, (0, 50, 155), self.collision_area)
                 
            self.img_pos[1] += (self.movement[1] - self.movement[0]) * 5
            self.screen.blit(self.img, self.img_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    k = event.key
                    if (k == pygame.K_UP or k == pygame.K_w):
                        self.movement[0] = True
                    if (k == pygame.K_DOWN or k == pygame.K_s):
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    k = event.key
                    if (k == pygame.K_UP or k == pygame.K_w):
                        self.movement[0] = False
                    if (k == pygame.K_DOWN or k == pygame.K_s):
                        self.movement[1] = False
                
            pygame.display.update()
            # runs game at 60 fps - dynamic sleep
            self.clock.tick(60)

Game().run()