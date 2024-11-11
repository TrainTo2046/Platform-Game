  # spark go off when projectile hits a player
                        # # spawns 30 sparks
                        for i in range(30):
                            # gives random angle in a circle in radians
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))

                            # add particles -> 30 particles as well
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))