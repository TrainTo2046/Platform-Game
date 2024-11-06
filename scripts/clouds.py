import random

class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed

    def render(self, surf, offset = (0, 0)):
        # * self.depth = 0.5
        # if the camera moves 5 pixels to right,
        # the cloud only moves 2.5 pixels to left
        # gives paralax effect
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        
        # want a set amount of clouds to loop around
        # self.pos[0] += self.speed means that the cloud position will always increase

        # render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width()
        # % used for loop 5 % 10 = 5, 12 % 10 = 2
        # x % 10, when x hits 10, it will go back to 0 and loop again 

        # (surf.get_width() + self.img.get_width())
        # when the cloud touches the end of the surface + size of cloud
        # when the cloud moves to left and disappears form the screen

        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(),
                             render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))
        

class Clouds:
    def __init__(self, cloud_images, count=16):
        # set of clouds
        self.clouds = []

        for i in range(count):
            self.clouds.append(Cloud((random.random() * 99999, # x
                                      random.random() * 99999), # y
                                      random.choice(cloud_images),  # cloud image
                                      random.random() * 0.05 + 0.05, # speed of cloud
                                      random.random() * 0.6 + 0.2)) # depth of cloud
                                        # cloud in foreground move faster than the background

            # sorting cloud by depth
            # clouds closest to the camera will be rendered first
            # good for layering cloud
            self.clouds.sort(key = lambda x : x.depth)

    def update(self):
        for cloud in self.clouds:
            cloud.update()

    def render(self, surf, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)