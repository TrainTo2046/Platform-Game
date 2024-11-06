import sys
import pygame
from scripts.utils import load_image, load_images
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds

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
        4) blit display  on top of the screen
        """
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
       
        self.movement = [False, False]

        self.assets = {
            'player'        : load_image('entities/player.png'),
            'large_decor'   : load_images('tiles/large_decor'),
            'grass'         : load_images('tiles/grass'),
            'decor'         : load_images('tiles/decor'),
            'stone'         : load_images('tiles/stone'),
            'background'    : load_image('background.png'),
            'clouds'        : load_images('clouds')
        }
        self.clouds = Clouds(self.assets['clouds'], count = 16)
        
        # creating a player entity
        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))

        # create tilemap
        self.tilemap = Tilemap(self, tile_size=16)

        # camera
        self.scroll = [0, 0]

    def run(self):
        # game loop
        while True:
            self.display.blit(self.assets['background'], (0, 0))
            # how far the camera is from where we want it to be
            # gets the place where player will be at the center
            # self.player.rect().centerx - self.display.get_width() / 2

            # were the camera is at right now
            # ... - self.scroll[0]

            # add it to the scroll
            # self.scroll[0] += ...

            # further the player is, the faster the camera will move
            # / 30
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_width() / 2 - self.scroll[1]) / 30
            # removes jitter on the player
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # update and render clouds
            self.clouds.update()
            self.clouds.render(self.display, offset = render_scroll)

            # update and render tile map
            self.tilemap.render(self.display, offset = render_scroll)

            # want to render the tiles before the player
            # so the tile doesn't hide the player

            # update and render player
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset = render_scroll)

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