from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"


def polygon_mask(shape, polygons):
    mask = np.zeros(shape[:2], dtype=np.uint8)
    for points in polygons:
        cv2.fillPoly(mask, [np.asarray(points, dtype=np.int32)], 255)
    return mask


def silver_fabric(image, mask, strength=1.0):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    light, green_red, blue_yellow = cv2.split(lab)
    neutral = np.full_like(green_red, 128)
    softened = cv2.addWeighted(green_red, 1 - strength, neutral, strength, 0)
    softened_blue = cv2.addWeighted(blue_yellow, 1 - strength, neutral, strength, 0)
    recolored = cv2.cvtColor(cv2.merge((light, softened, softened_blue)), cv2.COLOR_LAB2BGR)

    alpha = cv2.GaussianBlur(mask, (0, 0), 2.0).astype(np.float32) / 255
    alpha = (alpha * strength)[..., None]
    result = image.astype(np.float32) * (1 - alpha) + recolored.astype(np.float32) * alpha
    return np.clip(result, 0, 255).astype(np.uint8)


def recolor_men():
    path = ASSETS / "baju-melayu-muzium.jpg"
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    outfit = [
        [
            (444, 232), (445, 212), (455, 202), (480, 202), (491, 215), (526, 214),
            (541, 232), (566, 236), (592, 242), (611, 256), (622, 285), (636, 310),
            (637, 562), (626, 587), (611, 598), (590, 534), (594, 454), (568, 447),
            (355, 447), (354, 495), (347, 567), (338, 583), (319, 576), (312, 560),
            (333, 463), (339, 292), (351, 267), (371, 251), (408, 239),
        ],
        [(352, 443), (594, 443), (598, 516), (352, 516)],
        [
            (354, 509), (421, 515), (481, 521), (585, 513), (587, 557), (579, 627),
            (562, 677), (570, 722), (558, 743), (535, 744), (524, 731), (503, 738),
            (477, 745), (449, 746), (429, 737), (404, 750), (380, 748), (357, 729),
            (348, 686), (349, 625), (340, 586),
        ],
        [(400, 738), (450, 746), (450, 1080), (439, 1095), (417, 1097), (402, 1081), (397, 1062)],
        [(451, 746), (502, 740), (561, 731), (569, 756), (569, 1078), (554, 1098), (522, 1099), (502, 1080)],
    ]
    mask = polygon_mask(image.shape, outfit)
    mask = cv2.erode(mask, np.ones((3, 3), dtype=np.uint8), iterations=1)
    mask = cv2.GaussianBlur(mask, (0, 0), 0.8)
    print("Men recolor mask:", round(float(np.count_nonzero(mask)) / mask.size * 100, 2), "% of image")
    result = silver_fabric(image, mask)
    output = ASSETS / "baju-melayu-soft-gray.jpg"
    if not cv2.imwrite(str(output), result, [cv2.IMWRITE_JPEG_QUALITY, 94]):
        raise OSError(f"Could not save {output}")


def recolor_women():
    path = ASSETS / "baju-kurung.jpg"
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    height, width = image.shape[:2]
    scale_x, scale_y = width / 960, height / 1440

    jacket = [
        (232, 279), (290, 245), (380, 252), (444, 269), (510, 265), (602, 293),
        (643, 359), (700, 469), (693, 570), (659, 634), (686, 739), (641, 873),
        (578, 922), (473, 895), (415, 820), (376, 744), (309, 725), (253, 674),
        (217, 605), (228, 509), (195, 414),
    ]
    skirt = [
        (468, 737), (555, 719), (664, 731), (756, 772), (817, 927), (842, 1102),
        (818, 1246), (785, 1320), (628, 1334), (552, 1280), (517, 1155), (480, 1002),
    ]
    polygons = [
        [[round(x * scale_x), round(y * scale_y)] for x, y in points]
        for points in (jacket, skirt)
    ]
    region = polygon_mask(image.shape, polygons) > 0
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv)
    is_fabric_color = (
        (((hue >= 145) | (hue <= 9)) & (saturation > 36))
        | ((hue >= 10) & (hue <= 35) & (saturation > 105))
    )
    red_channel, green_channel, blue_channel = cv2.split(image)
    skin = (
        (hue <= 22)
        & (saturation < 150)
        & (red_channel > green_channel * 1.06)
        & (red_channel > blue_channel * 1.12)
        & ((red_channel - blue_channel) > 17)
    )
    mask = (region & is_fabric_color & (value > 34) & ~skin).astype(np.uint8) * 255

    for center_x, center_y, radius_x, radius_y in [(420, 157, 86, 112), (419, 281, 39, 42)]:
        cv2.ellipse(
            mask,
            (round(center_x * scale_x), round(center_y * scale_y)),
            (round(radius_x * scale_x), round(radius_y * scale_y)),
            0,
            0,
            360,
            0,
            thickness=-1,
        )
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), dtype=np.uint8))
    mask = cv2.GaussianBlur(mask, (0, 0), 1.2)
    print("Women recolor mask:", round(float(np.count_nonzero(mask)) / mask.size * 100, 2), "% of image")
    result = silver_fabric(image, mask)
    output = ASSETS / "baju-kurung-soft-gray.jpg"
    if not cv2.imwrite(str(output), result, [cv2.IMWRITE_JPEG_QUALITY, 94]):
        raise OSError(f"Could not save {output}")


recolor_men()
recolor_women()
