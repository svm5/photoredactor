from PIL import Image


def grey_filter(img):
    pixels = img.load()
    x, y = img.size
    for i in range(x):
        for j in range(y):
            if len(pixels[i, j]) == 4:
                r, g, b, a = pixels[i, j]
                sr = int((r + g + b) / 2)
                pixels[i, j] = sr, sr, sr, a
            else:
                r, g, b = pixels[i, j]
                sr = int((r + g + b) / 2)
                pixels[i, j] = sr, sr, sr
    return img.copy()