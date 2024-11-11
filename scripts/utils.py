import os
import pygame

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    """
    .convert() 
    converts internal representation of the image
    to make it more effecient for rendering

    good for performence
    """
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    # make background of img transparent
    # current background is black
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):
    images = []
    # os.listdir(PATH) gives you list of paths in from the folder PATH parameter points to
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        # we take each image from the PATH and then load it and put it in images list
        images.append(load_image(path + '/' + img_name))

    return images

class Animation:
    def __init__(self, images, img_dur= 5, loop=True):
        self.images = images
        # animation to loop
        self.loop = loop
        self.img_duration = img_dur
        # set to true if not looping and reach end
        self.done = False
        # keep track of where we are on our animation
        self.frame = 0

    # we create animation for each animation in the file
    # have it somewhere it is easy to reach
    # anytime something wants to use that animation, copy its own instance of the animation

    # in python, if you assign an object to the list, its a reference to the object instead of a copy
    def copy(self):
        # instead of returning a copy, it returns a reference
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            # % will force the animation to loop around
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            # when no loop, stops at the last image of the animation
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        # dividing the frame by how long the image is supposed to show for
        return self.images[int(self.frame / self.img_duration)]
