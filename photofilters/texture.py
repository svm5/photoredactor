from PIL import Image


def texture_filter(img1, img2):
    img2 = img2.resize(img1.size)
    pixels_1 = img1.load()
    if len(pixels_1[0, 0]) != 3:
        new_img = Image.new("RGBA", img1.size, (0, 0, 0))
        pixels_new = new_img.load()
        pixels_2 = img2.load()
        x, y = img1.size
        for i in range(y):
            for j in range(x):
                r, g, b = pixels_2[j, i]
                *rest, a = pixels_1[j, i]
                pixels_new[j, i] = r, g, b, a
        img = Image.blend(img1, new_img, 0.5)
    else:
        img = Image.blend(img1, img2, 0.5)
    return img.copy()