import sys
import pygame
from scripts.utils import load_image, load_images
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap

class Game:
    def __init__(self) -> None:   
        pygame.init()

        SCREEN_WIDTH = 640
        SCREEN_HEIGHT = 480

        pygame.display.set_caption('Platformer Game')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        """
        .Surface()
        generates an empty image with (w, h) dimension
        it is in black color

        we render on to this display and scale it up to the screen

        Steps
        1) create a display half the size of the screen
        2) render everything onto the display
        3) scale the display to fit the screen
        4) blit disply  on top of the screen
        """
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
       
        self.movement = [False, False]

        self.assets = {
            'player'        : load_image('entities/player.png'),
            'large_decor'   : load_images('tiles/large_decor'),
            'grass'         : load_images('tiles/grass'),
            'decor'         : load_images('tiles/decor'),
            'stone'         : load_images('tiles/stone')
        }

        # creating a player entity
        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))

        # create tilemap
        self.tilemap = Tilemap(self, tile_size=16)

    def run(self):
        # game loop
        while True:
            self.display.fill((14, 219, 248))
            # update and render tile map
            self.tilemap.render(self.display)

            # want to render the tiles before the player
            # so the tile doesn't hide the player

            # update and render player
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display)

            print(self.tilemap.physics_rects_around(self.player.pos))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    k = event.key
                    if (k == pygame.K_LEFT or k == pygame.K_a):
                        self.movement[0] = True
                    if (k == pygame.K_RIGHT or k == pygame.K_d):
                        self.movement[1] = True
                    if (k == pygame.K_UP or k == pygame.K_w):
                        # jumps
                        # velocity is pointing upwards -> anti-gravity
                        self.player.velocity[1] = -3
                if event.type == pygame.KEYUP:
                    k = event.key
                    if (k == pygame.K_LEFT or k == pygame.K_a):
                        self.movement[0] = False
                    if (k == pygame.K_RIGHT or k == pygame.K_d):
                        self.movement[1] = False
            
            # we first scale the display with pygame.transform.scale to fit the screen
            # we put the scaled display on top of the screen
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            # this updates the screen
            pygame.display.update()
            # runs game at 60 fps - dynamic sleep
            self.clock.tick(60)

Game().run()