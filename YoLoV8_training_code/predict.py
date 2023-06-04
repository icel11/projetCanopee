from ultralytics import YOLO

import cv2
import matplotlib as plt

model_path = './best.pt'

image_path = './test.tif'
print(image_path)

img = cv2.imread(image_path)

print("IMAGE:", img.shape)
H, W, _ = img.shape

model = YOLO(model_path)

results = model(img)

for result in results:
    for j, mask in enumerate(result.masks.data):
                
        mask = mask.numpy() * 255
        mask = cv2.resize(mask, (W, H))

        cv2.imwrite('./output.png', mask)

