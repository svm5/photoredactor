from PIL import Image


def sepia_filter(img):
    pixels = img.load()
    x, y = img.size
    for i in range(x):
        for j in range(y):
            if len(pixels[i, j]) == 4:
                r, g, b, a = pixels[i, j]
            else:
                r, g, b = pixels[i, j]
            n_r = int(0.393 * r + 0.769 * g + 0.189 * b)
            n_g = int(0.349 * r + 0.686 * g + 0.168 * b)
            n_b = int(0.272 * r + 0.534 * g + 0.131 * b)
            if len(pixels[i, j]) == 4:
                pixels[i, j] = n_r, n_g, n_b, a
            else:
                pixels[i, j] = n_r, n_g, n_b
    return img.copy()