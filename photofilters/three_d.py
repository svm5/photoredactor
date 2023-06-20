from PIL import Image
from photofilters.grey import grey_filter


MAX_OPACITY = 255


def three_d_filter(img):
    img = grey_filter(img)
    img_red = img.copy()
    pixels_red = img_red.load()
    img_blue = img.copy()
    pixels_blue = img_blue.load()
    delta = 10
    x, y = img.size
    new_img = Image.new("RGBA", (x, y), (0, 0, 0))
    pixels_new = new_img.load()
    for i in range(y):
        for j in range(x):
            if len(pixels_blue[j, i]) == 4:
                _, g, b, a = pixels_blue[j, i]
            else:
                _, g, b = pixels_blue[j, i]
            r, *rest = pixels_red[max(j - delta, 0), i]
            if len(pixels_blue[j, i]) == 4:
                pixels_new[j, i] = r, g, b, a
            else:
                pixels_new[j, i] = r, g, b, MAX_OPACITY
    return new_img.copy()