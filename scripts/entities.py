import pygame
import math
import random
from scripts.particle import Particle
from scripts.spark import Spark


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
        # x-axis movement change
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

                # above -> only modifying the entity_rect pos here and not player pos
                # now -> have to go and upadate players pos
                self.pos[0] = entity_rect.x

        # y-axis movement change
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

                # above -> only modifying the entity_rect pos here and not player pos
                # now -> have to go and upadate players pos
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

        # apply gravity to make the player fall (vertical axis)
        # apply acceleration by modifying velocity
        # remember the top left is (0, 0)
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # if you hit a tile above you or below you, reset the velocity
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

        # if you are in the air more than 2 secs, you dies
        # when you fall off the map
        if self.air_time > 120:
            self.game.dead += 1
            # when player falls out of map, screen shake is applied
            self.game.screenshake = max(16, self.game.screenshake)

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

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        # Enemies should be able to walk around but only to the edge of the island
        # Cannot walk off the map
        # Shoot at the player, horizontally
        # Need to see player to shoot horizontally

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        # if walking
        if self.walking:

            # looking ahead
            # x-axis (-7 if self.flip else 7) from the center of rectange
            # if facing right then + 7, left then - 7
            # y-axis (+23 below into the ground)
            # takes the location to see if there is a tile there
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                # if enemy runs into a wall on right or left side, turn around
                if (self.collision['right'] or self.collision['left']):
                    self.flip = not self.flip
                else:
                    # keep y-axis movement
                    # x-axis movement:
                    # if enemy facing right, move right
                    # if enemy facing left, move left
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])

            # if there is no tile, you flip the enemy direction so they go back
            else:
                self.flip = not self.flip
            
            # move walking to 0 over time
            self.walking = max(0, self.walking - 1)
            # when the enemy stops moving, then it shoots
            if not self.walking:
                # calculate the distance between enemy and player
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                # y-axis offset btw player and the enemy is less than 16 pixels
                if (abs(dis[1]) < 16):
                    # if player is to left of enemy and enemy is facing left
                    if (self.flip and dis[0] < 0):
                        # spawn projectile to the left
                         # [(x, y), direction, timer]
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])

                        # spawn the spark for the projectile
                        # spawns 4 sparks
                        for i in range(4):
                            # give Sparks 
                            # pos, angle = rand number btw (0, 0.5) because it is shooting left + math.pi
                            # speed between 0, 2
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    # if player is to the right of enemy and enemy is facing right
                    if (not self.flip and dis[0] > 0):
                        # spawn projectile to the right
                         # [(x, y), direction, timer]
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        # spawn the spark for the projectile
                        for i in range(4):
                            # give Sparks 
                            # pos, angle = rand number btw (0, 0.5) because it is shooting right no math.pi
                            # speed between 0, 2
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
                    

        # has 1 in 100 chance of occuring, 60fps -> 1 in 1.67 secs
        # if not walking
        elif random.random() < 0.01:
            #  walking set to random number between 30 and 120 -> 0.5 to 2 secs
            #  number of frames the the enemy will continue to walk for
            self.walking = random.randint(30, 120)
        
        # with new parameters, we update the enemy movement
        super().update(tilemap, movement=movement)


        # Animation for enemy
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        """ player kills enemy """
        # when player is dashing
        if abs(self.game.player.dashing) >= 50:
            # if rect of the enemy collides with rect of the player
            if self.rect().colliderect(self.game.player.rect()):
                # when enemy gets killed, screen shake is applied
                self.game.screenshake = max(16, self.game.screenshake)

                # spark go off when projectile hits a player
                # # spawns 30 sparks
                for i in range(30):
                    # gives random angle in a circle in radians
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))

                    # add particles -> 30 particles as well
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

                # add big spark when the enemy dies
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                
                # removes the enemy on the game.py side
                return True
    
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        # show enemy gun
        # gun needs to flip based on the direction the player is facing
        # if player is facing left
        # pygame.transorm.flip, True, False -> flips the gun image only on x-axis, and not y-axis
        # rest is  where we are going to put the gun
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        
        # don't need to flip in this case
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))
