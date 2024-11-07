
import pygame
import json

AUTOTILE_MAP = {
    # if these are neighbors, use tile 0
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8
}

NEIGHBOR_OFFSETS = [(-1 , 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}

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
    
    def render(self, surf, offset=(0, 0)):
         # off grid
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        # on grid optimization
        """
        without optimization:
        rendering all the tiles on the screen
        with optimization:
        determining which tiles should be on the screen
        rendering only those tiles
        
        start = offset[0] // self.tile_size
        dividing the offset of camera by the tile size
        gives us the top left tiles x position

        end = (offset[0] + surf.get_width()) // self.tile_size + 1
        tile coordinate of the right edge + 1

        range(start, end)
        """
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

       
        # on grid
        # for loc in self.tilemap:
        #    tile = self.tilemap[loc]
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
        #    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

    def save(self, path):
        f = open(path, 'w')
        # dump the map object onto the f file as json
        json.dump({'tilemap': self.tilemap, 
                   'tile_size': self.tile_size, 
                   'offgrid': self.offgrid_tiles}, f)
        f.close()

    # using json to store maps for level editior (java script object notations)
    # json doesn't support tuples
    # all keys in a dict() must be a string
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    def autotile(self):
        # iterate through tiles on grid
        for loc in self.tilemap:
            # get the tile
            tile = self.tilemap[loc]
            neighbors = set()
            # look through all the neighbors
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                # get the neighbour tile
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                # if neighbour tile exists
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]