import pygame
import math
import random
from scripts.particle import Particle

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

        # For Animation
        self.action = ''
        """
        in animations, each frame image will have varying dimension so you add padding to the
        edges so they have space to animate the changing sizes of images in animation
        """
        self.anim_offset = (-3, -3)
        # player should be able to look right and left
        self.flip = False
        # set current animation to idle
        self.set_action('idle')

        self.last_movement = [0, 0]
    # collision_rect
    def rect(self):
        # (x, y) (w, h)
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

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
        
        # if you are moving right, player is facing right
        if movement[0] > 0:
            self.flip = False
        # if you are moving left, player is facing left
        if movement[0] < 0:
            self.flip = True

        # movement is the input to the update
        # not the acutal movement that was executed upon
        # if you are moving into the wall, movement is the intent to move into the wall
        # not actutally hitting the wall
        self.last_movement = movement

        # apply gravity to make the player fall
        # apply acceleration by modifying velocity
        # remeber the top left is (0, 0)
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collision['down'] or self.collision['up']:
            self.velocity[1] = 0

        # update the animation image
        self.animation.update()

    def render(self, surf, offset= (0, 0)):
        """
        get current frame of the animation
        self.flip   is the x-axis flip
        False       is the y-axis flip
            -> don't want to flip the player upside down
        """
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                  (self.pos[0] - offset[0] + self.anim_offset[0],  # x- axis
                  self.pos[1] - offset[1] + self.anim_offset[1]))  # y- axis
        #surf.blit(self.game.assets['player'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    
class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        # check how long we have been in the air
        self.air_time = 0
        """
        a player will have one jump
        a wall jump will consume that one jump
        if you are on a wall and run out of jumps, can still jump

        2:
            jump
            jump off a wall
        """
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        # different entity will have different animation logic
        # this air time animation logic is only for the player
        self.air_time += 1
        if self.collision['down']:
            self.air_time = 0
            # when you hit the floor, the jumps resets
            self.jumps = 1

        self.wall_slide = False
        # if we hit a wall on either side and we are on the air, we should slide on the wall
        if (self.collision['right'] or self.collision['left']) and self.air_time > 4:
            self.wall_slide = True
            # capping the down velocity at 0.5
            self.velocity[1] = min(self.velocity[1], 0.5)
            # For animation of the player
            # if hit the right wall, don't want to flip the player
            if self.collision['right']:
                self.flip = False
            else:
                self.flip = True
            # updating the animation for the player
            self.set_action('wall_slide')

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        """ create a brust of particle while the player is dashing """
        # if we are at the start or end of the dash
        if abs(self.dashing) in {60, 50}:
            # create 20 particles for the brust
            for i in range(20):
                # gives you a random angle from a full circle (math.pi * 2) in radians 
                angle = random.random() * math.pi * 2
                # gives you a random speed from 0 to 1
                speed = random.random() * 0.5 + 0.5
                # cos is for x-axis
                # sin is for y-axis
                # generating a velocity based on the angle
                # Reason: Allows you to spread the particles in a circle instead of a square
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
                
        # normalizing dashing
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)

        # take the first 10 frame of the dash
        if abs(self.dashing) > 50:
            # (1 or -1) * 8
            # on the horizontal velocity will be 8 or -8 on first 10 frame
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            # at the end of the 10 frame dash, horizontal velocity goes down
            # sudden stop to the dash
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            # what about rest of the 50 frame?
            # there is a cooldown period between dash, you can't dash as much as you want
            # have to wait some time between the dashes
            # 50 frame is for cooling down
            """ create a stream of particle while the player is dashing """
            angle = random.random() * math.pi * 2
            # gives you a random speed from 0 to 1
            speed = random.random() * 0.5 + 0.5
            # x-axis (1 or -1) * random * 3
            # particles moving with the movement of the player
            # movment of the y-axis
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        # normalizaiton on the horizontal velocity
        # bring the velocity toward 0
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
    
    def render(self, surf, offset=(0, 0)):
        # when dashing, makes player invisible
        if abs(self.dashing) <= 50:
            # calls the Physics entity function
            super().render(surf, offset = offset)

    def jump(self):
        # for wall slide
        if self.wall_slide:
            # facing left and movement is going to the left
            if self.flip and self.last_movement[0] < 0:
                # push you to the right, push you away from the wall
                self.velocity[0] = 3.5
                # push you up
                self.velocity[1] = -2.5
                # jump animation
                self.air_time = 5
                # allows you to wall jump with 0 jumps left
                # prevents jumps < 0
                self.jumps = max(0, self.jumps - 1)
                return True
            # facing right and movement is going to the rigg=ht
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                # push you up
                self.velocity[1] = -2.5
                # jump animation
                self.air_time = 5
                # allows you to wall jump with 0 jumps left
                # prevents jumps < 0
                self.jumps = max(0, self.jumps - 1)
                return True

        # for regualr jump
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            # it will set the jump animation in motion
            self.air_time = 5
            return True
    
    def dash(self):
        if not self.dashing:
            # if facing left
            if self.flip:
                self.dashing = -60
            
            # if facing right
            else:
                self.dashing = 60