import cv2
import numpy as np
import os
import sys
import landing
from mrcnn import utils
from mrcnn import model as modellib

ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")

COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)

LANDING_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_landing.h5")

class InferenceConfig(landing.LandingConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    BACKBONE = 'resnet101'


config = InferenceConfig()

model = modellib.MaskRCNN(
    mode="inference", model_dir=MODEL_DIR, config=config
)

# Load last trained weights
model_path = model.find_last()[1]
# Load trained weights (fill in path to trained weights here)
assert model_path != "", "Provide path to trained weights"
print("Loading weights from ", model_path)
model.load_weights(model_path, by_name=True)

# Load weights on initial landing weights
# model.load_weights(LANDING_MODEL_PATH, by_name=True)

class_names = [
    'BG', 'safe', 'unsafe'
]

# def random_colors(N):
#     np.random.seed(1)
#     colors = [tuple(255 * np.random.rand(3)) for _ in range(N)]
#     return colors

def defined_colors(N):
    colors = [
                (255,0,0),
                (0,225,0),
                (0,0,225)
            ]
    return colors


colors = defined_colors(len(class_names))

class_dict = {
    name: color for name, color in zip(class_names, colors)
}


def apply_mask(image, mask, color, alpha=0.5):
    """apply mask to image"""
    for n, c in enumerate(color):
        image[:, :, n] = np.where(
            mask == 1,
            image[:, :, n] * (1 - alpha) + alpha * c,
            image[:, :, n]
        )
    return image


def display_instances(image, boxes, masks, ids, names, scores, show_bbox=True):
    """
        take the image and results and apply the mask, box, and Label
    """
    n_instances = boxes.shape[0]

    if not n_instances:
        print('NO INSTANCES TO DISPLAY')
    else:
        assert boxes.shape[0] == masks.shape[-1] == ids.shape[0]

    for i in range(n_instances):
        
        if not np.any(boxes[i]):
            continue

        y1, x1, y2, x2 = boxes[i]

        label = names[ids[i]]

        color = class_dict[label]

        score = scores[i] if scores is not None else None

        caption = '{} {:.2f}'.format(label, score) if score else label

        mask = masks[:, :, i]

        image = apply_mask(image, mask, color)

        if show_bbox:
            image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        image = cv2.putText(
            image, caption, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2
        )

    return image



