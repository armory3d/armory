import bpy

img = bpy.data.images.new(name="img", width=256, height=256)
for x in range(256):
    for y in range(256):
        x2 = (x - 37) & 255
        y2 = (y - 17) & 255
        img.pixels[(y * 255 + x) * 4 + 1] = img.pixels[(y2 * 255 + x2) * 4]
        img.pixels[(y * 255 + x) * 4 + 3] = img.pixels[(y2 * 255 + x2) * 4 + 2]
