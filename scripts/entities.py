import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        # derivative of pos = velocity
        # derivative of velocity = acceleration
        # velocity = rate of change
        # acceleration = rate of change in velocity
        
        self.collision = {'up': False, 'down': False, 'right': False, 'left': False}

    # collision_rect
    def rect(self):
        # (x, y) (w, h)
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, tilemap, movement= (0, 0)):
        # resets the collision map
        self.collision = {'up': False, 'down': False, 'right': False, 'left': False}

        # how much the entity should move in this current frame
        frame_movement = (movement[0] + self.velocity[0],  movement[1] + self.velocity[1])

        # (x, y) movement change
        self.pos[0] += frame_movement[0]

        # collision detection x-axis
        """
        need to handle one axis at a time
        can't do both x and y at the same time
        """
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                # move right and collided with a tile
                if frame_movement[0] > 0:
                    # make right edge of the entity to left edge of tile
                    # player gets pushed back during collision
                    entity_rect.right = rect.left
                    self.collision['right'] = True
                # move left and collided with a tile
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collision['left'] = True

                # only modifying the entity_rect pos here and not player pos
                # have to go and upadate players pos
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]

        # collision detection y-axis
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                # move dowm and collided with a tile
                if frame_movement[1] > 0:
                    # make right edge of the entity to left edge of tile
                    # player gets pushed back during collision
                    entity_rect.bottom = rect.top
                    self.collision['down'] = True
                # move up and collided with a tile
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collision['up'] = True

                # only modifying the entity_rect pos here and not player pos
                # have to go and upadate players pos
                self.pos[1] = entity_rect.y
        
        # apply gravity to make the player fall
        # apply acceleration by modifying velocity
        # remeber the top left is (0, 0)
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collision['down'] or self.collision['up']:
            self.velocity[1] = 0


    def render(self, surf, offset= (0, 0)):
        surf.blit(self.game.assets['player'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))