
import pygame

NEIGHBOR_OFFSETS = [(-1 , 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size = 16):
        self.game = game
        self.tile_size = tile_size
        # every tiles in the grid
        # {(0, 0): 'grass', (0, 1): 'dirt', ...., (999, 0): 'grass'}
        # {'0;0': 'grass', '0;1': 'dirt', ...., '999;0': 'grass'}
        self.tilemap = {}
        # tiles that doesn't line up with the grid
        self.offgrid_tiles = []

        for i in range(10):
            # x -> 3-12
            # y -> 10
            # horizontal line of grass tiles
            self.tilemap[str(3 + i) + ';10'] = {'type': 'grass', 'variant':1, 'pos':(3 + i, 10)}

            # vertical line of stone tiles
            self.tilemap['10;' + str(5 + i)] = {'type': 'stone', 'variant':1, 'pos':(10, 5 + i)}
    
    # get all the tiles around the player
    # you pass in a pixel pos
    def tiles_around(self, pos):
        tiles = []

        # grid tiles are not pixels so have to convert the pixel pos to a grid pos
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        
        return tiles
    
    # get all the tiles you can collide with
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))

        return rects
    


    def render(self, surf):
         # off grid
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], tile['pos'])

        # on grid
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            """
            tilemap is dict(dict())
            tile is the inside dict()

            tile['type'] = 'grass' or 'stone'
            tile['variant'] = 1 or ...
            game.assets['stone']['variant'] = loads the 'variant'th image of stone

            (x, y) coordinates
            tile['pos'][0], tile['pos'][1]
            
            * self.tile_size
            tile[pos] is pixel position
            need them to be in grid position
            we need to multiply by the size of tiles in terms of pixels
            """
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size))

       