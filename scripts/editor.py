import sys
import pygame
from utils import load_images, Animation
from tilemap import Tilemap

# how much we multiply the size of the tile pixels
RENDER_SCALE = 2.0

class Editor:
    def __init__(self) -> None:   
        pygame.init()

        SCREEN_WIDTH = 640
        SCREEN_HEIGHT = 480

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.assets = {
            'large_decor'   : load_images('tiles/large_decor'),
            'grass'         : load_images('tiles/grass'),
            'decor'         : load_images('tiles/decor'),
            'stone'         : load_images('tiles/stone')
        }

        # instead of moving player, move the whole camera
        self.movement = [False, False, False, False]
        
        # create tilemap
        self.tilemap = Tilemap(self, tile_size=16)
        # opens the map if it exists on the file
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass

        # camera
        self.scroll = [0, 0]

        # get a list of self.assets key
        self.tile_list = list(self.assets)
        # which group = which key
        self.tile_group = 0
        # which variant of the key: [img2, img3]
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

    def run(self):
        # game loop
        while True:
            # black background
            self.display.fill((0, 0, 0, 0))

            # move camera using keyboard
            # x- axis
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            # y - axis
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            self.tilemap.render(self.display, offset=render_scroll)

            tile_type = self.tile_list[self.tile_group]
            # ith variant of tile_type
            curr_tile_img = self.assets[tile_type][self.tile_variant].copy()
            # makes the curr_tile_img bit transparent
            curr_tile_img.set_alpha(100)

            # gets you position of the mouse with respect to your window
            mpos = pygame.mouse.get_pos()
            # we are scaling our images x2
            # need to scale the mouse position to get accurate reading
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            # gives coordinates of mouse in terms of the tiles
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size),
                        int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            """
            allows you to see where the next tile is going to go
            takes tile pos -> converts it back to pixel coordinates -> 
            adjust that position based on the camera -> render
            """
            if self.ongrid:
                self.display.blit(curr_tile_img, 
                                  (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(curr_tile_img, mpos)

            # Allows you to place tiles on the screen/ grid
            if self.clicking and self.ongrid:
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos':tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]
                
                # bad code, remove tiles from offgrid
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            self.display.blit(curr_tile_img, (5, 5))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # when you activate the mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # left click
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type' : self.tile_list[self.tile_group], 'variant':self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    # right click
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                         # scroll up
                        if event.button == 4:
                            # loops around
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        # scroll down
                        if event.button == 5:
                            # loops around
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        # scroll up
                        if event.button == 4:
                            # loops around
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        # scroll down
                        if event.button == 5:
                            # loops around
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    k = event.key
                    if (k == pygame.K_LEFT or k == pygame.K_a):
                        self.movement[0] = True
                    if (k == pygame.K_RIGHT or k == pygame.K_d):
                        self.movement[1] = True
                    if (k == pygame.K_UP or k == pygame.K_w):
                        self.movement[2] = True
                    if (k == pygame.K_DOWN or k == pygame.K_s):
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                    if event.key == pygame.K_g:
                        # filps the value
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                if event.type == pygame.KEYUP:
                    k = event.key
                    if (k == pygame.K_LEFT or k == pygame.K_a):
                        self.movement[0] = False
                    if (k == pygame.K_RIGHT or k == pygame.K_d):
                        self.movement[1] = False
                    if (k == pygame.K_UP or k == pygame.K_w):
                        self.movement[2] = False
                    if (k == pygame.K_DOWN or k == pygame.K_s):
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)

Editor().run()