import os

from PIL import Image

indir = './samples'
outdir = './output'

def resize_image(img, max_width=None, max_height=None):
    '''
    Strips an image of everything but its basic data, first correcting orientation if necessary.

    'img' must be a PIL.Image.Image instance. Returns a new instance. Requires the PIL.Image (Python Image Library) or equivalent to be imported as Image; image formats supported depend on PIL prereqs installed on the system (see http://pillow.readthedocs.io/en/3.0.x/installation.html).

    If max_width and/or max_height are supplied (pixels as int), the image is proportionally downsized to fit the tighter of the two constraints using a high-quality downsampling filter.
    '''

    ORIENT = { # exif_val: (rotate degrees cw, mirror 0=no 1=horiz 2=vert); see http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/EXIF.html
              2: (0, 1),
              3: (180, 0),
              4: (0, 2),
              5: (90, 1),
              6: (270, 0),
              7: (270, 1),
              8: (90, 0),
             }

    assert isinstance(img, Image.Image), "Invalid 'img' parameter to resize_image()"
    img_format = img.format

    # fix img orientation (issue with jpegs taken by cams; phones in particular):
    exif_data = img._getexif() if hasattr(img, '_getexif') else None
    if exif_data is not None:
        try:
            orient = img._getexif()[274]
        except (AttributeError, KeyError, TypeError, ValueError):
            orient = 1 # default (normal)
        if orient in ORIENT:
            (rotate, mirror) = ORIENT[orient]
            if rotate:
                print('rotate with {}'.format(rotate))
                img = img.rotate(rotate)
            if mirror == 1:
                print('transpose with FLIP_LEFT_RIGHT')
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif mirror == 2:
                print('transpose with FLIP_TOP_BOTTOM')
                img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # strip image
    data = img.getdata()
    palette = img.getpalette()
    img = Image.new(img.mode, img.size)
    img.putdata(data)
    if palette:
        img.putpalette(palette)

    # resize image (if necessary):
    (width, height) = img.size
    if max_width and width > max_width and (not max_height or width*max_height >= height*max_width): # width is constraint
        img = img.resize((max_width, int(round(height*max_width/width))), Image.LANCZOS)
    elif max_height and height > max_height: # height is constraint
        img = img.resize((int((round(width*max_height/height))), max_height), Image.LANCZOS)

    img.format = img_format # preserve orig format
    return img

if __name__ == "__main__":
    for filename in os.listdir(indir):
        newfilename = os.path.join(outdir, filename)
        filename = os.path.join(indir, filename)
        filesize = os.path.getsize(filename)

        try:
            img = Image.open(filename)
        except:
            continue

        format = img.format
        imgsize = img.size

        # output filesize, format and width/height of the image
        print('{} size={} format={} width/height={}'.format(filename, filesize, format, imgsize))

        if format != 'GIF': # skip GIF
            exif_data = True if hasattr(img, '_getexif') else False
            print('{} size={} format={} width/height={} exif={}'.format(filename, filesize, format, imgsize, exif_data))
            # fix image
            img = resize_image(img, 1024, 1024)
            img.save(newfilename, img.format)
            filesize = os.path.getsize(newfilename)
            imgsize = img.size
            exif_data = True if hasattr(img, '_getexif') else False
            print('{} size={} format={} width/height={} exif={}'.format(newfilename, filesize, format, imgsize, exif_data))
