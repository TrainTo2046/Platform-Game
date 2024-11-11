import sys
import random
import math
import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark

class Game:
    def __init__(self):
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
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle' : Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run' : Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun' : load_image('gun.png'),
            'projectile' : load_image('projectile.png'),
        }
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.load_level(0)
        
        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.scroll = [0, 0]
        self.dead = 0

        self.screenshake = 0  
    
    def load_level(self, map_id):
        self.dead = 0
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        # hardcoding a hit box because there is only one type of tile that can spawn leaves
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        
        self.enemies = []
        # spawn, no keep because we don't want it on tilemap. just need location
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

    def run(self):
        # game loop
        while True:
            self.display.blit(self.assets['background'], (0, 0))

            # screenshake value goes down to 0
            self.screenshake = max(0, self.screenshake - 1)

            # timer starts soon as you die
            # when timer runs out 40 frames -> the level is restarted
            if self.dead:
                self.dead += 1
                if self.dead > 40:
                    self.load_level(0)
            
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
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            # removes jitter on the player
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    # gives us any position in the rect
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    # spawns our particles
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], 
                                                   frame=random.randint(0, 20)))
            
            # update and render clouds
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            # update and render tile map
            self.tilemap.render(self.display, offset=render_scroll)
            
            # want to render the tiles before the player
            # so the tile doesn't hide the player

            # want to render enemies before player
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)

                if kill:
                    self.enemies.remove(enemy)

            # update and render player
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # want the projectiles to be on top of the player
            # [(x, y), direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                # adding projectile on the display
                # img.get_width() / 2 = top center
                # render_scroll -> to apply the camera
                # if the projectile doesn't appear, you got the camera stuff wrong
                # think about how the camera should apply to the thing you are working on
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))

                # check if the location of the projectile is a solid tile (wall)
                if self.tilemap.solid_check(projectile[0]):
                    # if it hits the wall, we remove it
                    self.projectiles.remove(projectile)

                    # spark go off when projectile hits a solid tile (wall)
                    # spawns 4 sparks
                    for i in range(4):
                        # (math.pi if projectile[1] > 0 else 0)
                        # -> shoot the spark left only if the projectile is going right, vice versa
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))

                # if time is greater than 6 secs, we remove the porjectile
                # when the projectile flies off the map
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)

                # if it hits the player
                # if you are in cooldown part of dashing or not dashing
                # if you dash, you are invincible
                elif abs(self.player.dashing) < 50:
                    # if the projectile hits the player
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        # when player is hit by projectile
                        self.dead += 1
                        # when player gets shot, screen shake is applied
                        self.screenshake = max(16, self.screenshake)

                        # spark go off when projectile hits a player
                        # # spawns 30 sparks
                        for i in range(30):
                            # gives random angle in a circle in radians
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))

                            # add particles -> 30 particles as well
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
    
            # sparks is below particles
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    # passing in animation frame to sin function
                    # sin() gives a num between [-1, 1]
                    # makes the particle move back and forth over time in smooth pattern
                    # 0.035 is to slow down the sin function so you don't loop fast
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            
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
                        self.player.jump()
                    # player dashes when you press x
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    k = event.key
                    if (k == pygame.K_LEFT or k == pygame.K_a):
                        self.movement[0] = False
                    if (k == pygame.K_RIGHT or k == pygame.K_d):
                        self.movement[1] = False
            
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            # we first scale the display with pygame.transform.scale to fit the screen
            # we put the scaled display on top of the screen
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)
            # this updates the screen
            pygame.display.update()
            # runs game at 60 fps - dynamic sleep
            self.clock.tick(60)

Game().run()