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