import os
import random

import numpy as np
import torch
from skimage.io import imread
from torch.utils.data import Dataset
from skimage.io import imsave

from utils import crop_sample_canopee, pad_sample_canopee, resize_sample_canopee, normalize_volume_canopee


class CanopeeDataset(Dataset):
    """Brain MRI dataset for FLAIR abnormality segmentation"""

    in_channels = 1
    out_channels = 1

    def __init__(
        self,
        images_dir,
        transform=None,
        image_size=256,
        subset="train",
        random_sampling=True,
        validation_cases=10,
        seed=42,
    ):
        assert subset in ["all", "train", "validation"]

        # read images
        volumes = {}
        masks = {}
        print("reading {} images...".format(subset))
        image_slices = []
        mask_slices = []
        for (dirpath, dirnames, filenames) in os.walk(images_dir):
            for filename in sorted(
                filter(lambda f: ".tif" in f, filenames),
                key=lambda x: int(x.split("/")[-1].split(".")[-2].split("_")[-1]),
            ):
                filepath = os.path.join(dirpath, filename)
                if "mask" in filename:
                    mask_slices.append(imread(filepath, as_gray=True))
                else:
                    image_slices.append(imread(filepath))
            if len(image_slices) > 0:
                #corolle_id = dirpath.split("/")[-1]
                #volumes[corolle_id] = np.array(image_slices[1:-1])
                #masks[corolle_id] = np.array(mask_slices[1:-1])
                for i in range(0,len(image_slices)):
                    volumes[i] = np.array(image_slices[i])
                    masks[i] = np.array(mask_slices[i])

        #self.corolles = sorted(volumes)
        self.corolles = [i for i in range(0,len(image_slices))]

        # select cases to subset
        if not subset == "all":
            random.seed(seed)
            validation_corolles = random.sample(self.corolles, k=min(len(self.corolles), validation_cases))
            if subset == "validation":
                self.corolles = validation_corolles
            else:
                self.corolles = sorted(
                    list(set(self.corolles).difference(validation_corolles))
                )
        
        #filepath_test = "/Users/Mel/PycharmProjects/image_segmentation_3/UNet_canopee/test.png"
        #imsave(filepath_test,volumes[0])
        print("preprocessing {} volumes...".format(subset))
        # create list of tuples (volume, mask)
        self.volumes = [(volumes[k], masks[k]) for k in self.corolles]
        #print("0ici l'array volume est de la forme :", np.array(self.volumes).shape)

        #print("cropping {} volumes...".format(subset))
        # crop to smallest enclosing volume
        #self.volumes = [crop_sample_canopee(v) for v in self.volumes]

        #print("padding {} volumes...".format(subset))
        # pad to square
        #self.volumes = [pad_sample_canopee(v) for v in self.volumes]

        print("resizing {} volumes...".format(subset))
        # resize
        self.volumes = [resize_sample_canopee(v, size=image_size) for v in self.volumes]
        #print("1ici l'array volume est de la forme :", np.array(self.volumes).shape)

        #print("normalizing {} volumes...".format(subset))
        # normalize channel-wise
        self.volumes = normalize_volume_canopee(self.volumes)
        #print("2ici l'array volume est de la forme :", np.array(self.volumes).shape)

        # probabilities for sampling slices based on masks
        self.slice_weights = [np.sum(np.sum(m,axis=-1),axis=-1) for [v, m] in self.volumes]
        #print(self.slice_weights)
        #self.slice_weights = [ (s + (s.sum() * 0.1 / len(s))) / (s.sum() * 1.1) for s in self.slice_weights
        sum_s = abs(np.sum(self.slice_weights))
        self.slice_weights =  [ (abs(s) + sum_s * 0.1) / (sum_s * 1.1) for s in self.slice_weights ]
        #print(self.slice_weights)

        # add channel dimension to masks
        self.volumes = [(v, m[..., np.newaxis]) for [v, m] in self.volumes]
        #print("volumes :",np.array(self.volumes).shape)

        print("done creating {} dataset".format(subset))

        # create global index for patient and slice (idx -> (p_idx, s_idx))
        num_slices = [v.shape[0] for [v, m] in self.volumes]
        #print("num slices ",len(num_slices))
        """
        self.corolles_slice_index = list(
            zip(
                sum([[i] * num_slices[i] for i in range(len(num_slices))], []),
                sum([list(range(x)) for x in num_slices], []),
            )
        )
        """
        print("COROLLES:", self.corolles)
        self.corolles_slice_index = self.corolles

        self.random_sampling = random_sampling
        self.transform = transform

    def __len__(self):
        return len(self.corolles_slice_index)

    def __getitem__(self, idx):
        #corolle = self.corolles_slice_index[idx][0]
        #slice_n = self.corolles_slice_index[idx][1]
        corolle  = idx
        #print("corolle",corolle)
        #print("volumes",len(self.volumes))
        v, m = self.volumes[corolle]
        """
        if self.random_sampling:
            corolle = np.random.randint(len(self.volumes))
            print("corolle", corolle)
            print("slice_weihths ",np.array(self.slice_weights).shape)
            p = list(np.array(self.slice_weights))
            slice_n = np.random.choice(
                range(len(self.volumes))
            )
            image = v[slice_n]
            mask = m[slice_n]
        else :
            image = v
            mask = m
        """
        image = v
        mask = m

        if self.transform is not None:
            image, mask = self.transform((image, mask))

        # fix dimensions (C, H, W), Ici aucune chanel donc useless
        #image = image.transpose(2, 0, 1)
        #mask = mask.transpose(2, 0, 1)
        image_tensor = torch.from_numpy(image.astype(np.float32))
        mask_tensor = torch.from_numpy(mask.astype(np.float32))
        #print(image_tensor.size)
        # return tensors
        return image_tensor, mask_tensor
