import numpy as np
from skimage.transform import rescale, rotate
from torchvision.transforms import Compose


def transforms(scale=None, angle=None, flip_prob=None):
    transform_list = []

    if scale is not None:
        transform_list.append(Scale(scale))
    if angle is not None:
        transform_list.append(Rotate(angle))
    if flip_prob is not None:
        transform_list.append(HorizontalFlip(flip_prob))

    return Compose(transform_list)


class Scale(object):

    def __init__(self, scale):
        self.scale = scale

    def __call__(self, sample):
        image, mask = sample

        img_size = image.shape[0]

        scale = np.random.uniform(low=1.0 - self.scale, high=1.0 + self.scale)

        image = rescale(
            image,
            scale,
            channel_axis=True,
            preserve_range=True,
            mode="constant",
            anti_aliasing=False,
        )
        #print(np.array(mask).shape)
        mask = rescale(
            mask,
            scale,
            order=0,
            channel_axis=True,
            preserve_range=True,
            mode="constant",
            anti_aliasing=False,
        )

        if scale < 1.0:
            diff = (img_size - image.shape[0]) / 2.0
            if len(image.shape) > 2:
                image.squeeze(-1)
            if len(mask.shape) > 2:
                mask = mask.squeeze(2)
                #print("mask squeezed")
            #print("shape of the mask", mask.shape)
            padding = ((int(np.floor(diff)), int(np.ceil(diff))),(0,0))
            image = np.pad(image, padding, mode="constant", constant_values=0)
            mask = np.pad(mask, padding, mode="constant", constant_values=0)
        else:
            x_min = (image.shape[0] - img_size) // 2
            x_max = x_min + img_size
            image = image[x_min:x_max, x_min:x_max, ...]
            mask = mask[x_min:x_max, x_min:x_max, ...]
        if len(mask.shape) > 2:
            mask = mask.squeeze(2)
            #print("mask squeezed")
        #print("after transform we get the shape :", image.shape, "et pour le mask :", mask.shape)
        return image, mask


class Rotate(object):

    def __init__(self, angle):
        self.angle = angle

    def __call__(self, sample):
        image, mask = sample

        angle = np.random.uniform(low=-self.angle, high=self.angle)
        image = rotate(image, angle, resize=False, preserve_range=True, mode="constant")
        mask = rotate(
            mask, angle, resize=False, order=0, preserve_range=True, mode="constant"
        )
        return image, mask


class HorizontalFlip(object):

    def __init__(self, flip_prob):
        self.flip_prob = flip_prob

    def __call__(self, sample):
        image, mask = sample

        if np.random.rand() > self.flip_prob:
            return image, mask

        image = np.fliplr(image).copy()
        mask = np.fliplr(mask).copy()

        return image, mask
