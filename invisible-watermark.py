import random
import argparse
from argparse import RawTextHelpFormatter
from PIL import Image, ImageDraw, ImageFont

def convert_to_png(image_to_convert):
    print('Image {} is not in PNG format. Converting...'.format(image_to_convert))
    try:  # ensure the image exists on disk
        temp = Image.open(image_to_convert)
        temp.save(image_to_convert + '.png')
        image_to_convert = image_to_convert + '.png'

    except FileNotFoundError as err:
        print(err)
        exit(1)

    return image_to_convert

def generate_template(original_img, text_to_add, path_to_image, font_size, num_of_watermarks, font_to_use):

    #Opening Image & Creating New Text Layer
    new_img = Image.new('RGB', original_img.size, (255, 255, 255))

    #Creating Text
    try:
        font = ImageFont.truetype(font_to_use, font_size)
    except OSError as e:
        print('[Font Error] {}'.format(e))
        print('[Font Error] Font not found or it has an error')
        exit(1)

    #Creating Draw Object
    #this is what tells the draw tool which image to use
    draw = ImageDraw.Draw(new_img)

    #Positioning of Text
    width, height = original_img.size

    #Loop for Multiple Watermarks
    y = 1
    bo = 0 #this is a check to see if we have reached the top or bottom
    for i in range(num_of_watermarks):

        if y > height: #if y is past the top of the image start subracting instead of adding
            bo = 1
        elif y < 0:
            bo = 0

        if bo == 0:
            y += random.randrange(0, int(height / 8), 19) + random.randint(0, 100)

        else:
            y -= random.randrange(0, int(height / 8), 19) + random.randint(0, 100)

        x = random.randint(0, width - 200)
        draw.text((x, y), text_to_add, fill=(0, 0, 0), font=font)

    #Combining both layers and saving new image
    #watermarked = Image.alpha_composite(original_img, new_img)
    new_img.save('template_' + path_to_image)
    return new_img

def generate_watermark(path_to_image, text_to_add, font_size, num_of_watermarks, custom_template, font):
    #read all the data from the image
    try: #ensure the image exists on disk
        original_img = Image.open(path_to_image)

    except FileNotFoundError as e:
        print(e)
        exit(1)

    print("Image mode is: " + str(original_img.mode)  + " for " + path_to_image)
    if original_img.mode != 'RGB': #check to see if image is rgb
        original_img = original_img.convert('RGB')
        print("Image mode is NOW: " + str(original_img.mode) + " for " + path_to_image)

    #get the size of the image
    width, height = original_img.size

    if custom_template is not None: # did they give us a custom template
        print('Using custom template: {}'.format(custom_template))
        if custom_template.lower().endswith('.png') == False: # ensure its a png
            custom_template = convert_to_png(custom_template)

        try:  # ensure the image exists on disk
            custom_template_image = Image.open(custom_template)

        except FileNotFoundError as e:
            print(e)
            exit(1)

        print("Image mode is: " + str(custom_template_image.mode) + " for " + custom_template)
        if custom_template_image.mode != 'RGB':  # check to see if image is rgb
            custom_template_image = custom_template_image.convert('RGB')
            print("Image mode is NOW: " + str(custom_template_image.mode) + " for " + custom_template)

        ct_width, ct_height = custom_template_image.size

        if ct_width != width or ct_height != height: # ensure the template matches the original image
            print('Custom template\'s width/height does not match that of the original image')
            print('Custom Template Width/height\n{}/{}\nOriginal Image\'s Width/height\n{}/{}'.format(ct_width,ct_height, width, height))
            tmp = Image.new('RGB', original_img.size, (255, 255, 255))
            tmp.save('custom_template_' + path_to_image)
            print('Generated a blank template that is the correct size')
            exit(1)



    #generate the template to use
    if custom_template is not None:
        template = custom_template_image
    else:
        template = generate_template(original_img, text_to_add, path_to_image, font_size, num_of_watermarks, font)

    #loop through each pixel checking the template for white or black pixels and
    #modifying the original_img to reflect those changes
    #key white oi_r needs to be even black oi_r needs to be odd
    #oi_r = original_image red make sense?
    for row in range(height):
        for col in range(width):
            r, g, b = template.getpixel((col, row)) #r g b is for the template image
            oi_r, oi_g, oi_b = original_img.getpixel((col, row)) #oi_r oi_g oi_b is for the original image

            if r > 150: #logic tree if the r value is over 150 (closer to black than white) were making it a black pixel
                if oi_r % 2 == 0: #check if the pixel is odd or even and if it is odd we need to add or subtract 1
                    if oi_r + 1 > 255: #if adding 1 pushes over 255 (the max limit for rgb) subtract one
                        oi_r = oi_r - 1
                    else:
                        oi_r = oi_r + 1

            else: # make it a white pixel
                if oi_r % 2 != 0: #if the r value is even we need to make it odd by adding or subtracting 1
                    if oi_r + 1 > 255: #if adding 1 pushes over 255 (the max limit for rgb) subtract one
                        oi_r = oi_r - 1
                    else:
                        oi_r = oi_r + 1

            #no put the pixel on the image
            original_img.putpixel((col, row), (oi_r, oi_g , oi_b))

    original_img.save('download_' + str(path_to_image))
    print('Successfully watermarked {}. Watermarked image is download_{}'.format(path_to_image, path_to_image))

def check_watermark(path_to_image):

    #open the image
    try:  #ensure the image exists on disk
        original_img = Image.open(path_to_image)

    except FileNotFoundError as err:
        print(err)
        exit(1)

    print("Image mode is: " + str(original_img.mode) + " for " + path_to_image)
    if original_img.mode != 'RGB': #check to see if image is rgb
        original_img = original_img.convert('RGB') #if its not make it rgb
        print("Image mode is NOW: " + str(original_img.mode) + " for " + path_to_image)

    #generate a white canvas that will hold the extracted watermark
    water_check = Image.new('RGB', original_img.size, (255, 255, 255))

    #get the width and height
    width, height = original_img.size

    #loop through each pixel in the image if the r value is even it is white if it is odd it is black
    #then append these color changes to the new image water_check
    for row in range(height):
        for col in range(width):
            r, g, b = original_img.getpixel((col, row)) #r g b is for the original_img

            if r % 2 == 0: #check to see if the red pixel is odd (if it is add a black pixel to water_check)
                water_check.putpixel((col, row), (0, 0, 0))

    #save the watermark
    water_check.save('reterived_watermark_' + str(path_to_image))

def main():

    #arguments
    parser = argparse.ArgumentParser(description='Image Watermarker\n\n#Requires an RGB or RGBA formatted PNG or BMP image', epilog="modes:\n  0 : Watermark\n  1 : Check Watermark", formatter_class=RawTextHelpFormatter)
    parser.add_argument('-i', '--input', action='store', help='Input file name to be watermarked', required=False)
    parser.add_argument('-iF', '--input-file', action='store', help='Input for multiple files in a text file to be watermarked', required=False)
    parser.add_argument('-ct', '--custom-template', action='store', help='Custom watermark template (MUST BE THE SAME SIZE AS THE IMAGE)', required=False)
    parser.add_argument('-m', '--mode', action='store', choices=['0', '1'], help='Mode for the script', required=False)
    parser.add_argument('-t', '--text', action='store', help='Watermark text', required=False)
    parser.add_argument('-f', '--font-size', action='store', type=int, help='Font size (Default 30)', required=False)
    parser.add_argument('--font', action='store', default='arial.ttf', help='Font to use (Default=arial.ttf)')
    parser.add_argument('-w', '--watermark-num', action='store', type=int, help='Number of times to watermark the image (Default 10)', required=False)
    parser.add_argument('--gen-blank-template', action='store_true', help='Generates a blank template for an image and exits')
    args = parser.parse_args()

    if args.gen_blank_template:
        if args.input is None:
            print('Gotta give an image to make a blank template')
            exit(1)
        if args.input.lower().endswith('.png') == False:
            args.input = convert_to_png(args.input)
        print('Generating a blank template for {}'.format(args.input))
        try:  # ensure the image exists on disk
            temp = Image.open(args.input)
            tmp = Image.new('RGB', temp.size, (255, 255, 255))
            tmp.save('custom_template_' + args.input)

        except FileNotFoundError as err:
            print(err)
            exit(1)

        exit(0)

    #Checking and setting default values
    if args.font_size is None:
        args.font_size = 30

    if args.watermark_num is None:
        args.watermark_num = 10

    if args.input is not None: #if the input exists
        if args.mode == '0': #if we are watermarking the image
            if args.text is not None or args.custom_template is not None: #check to see if they supplied us text
                if args.input.lower().endswith('.png') == False: # ensure the image is a png
                    args.input = convert_to_png(args.input)
                generate_watermark(args.input, args.text, args.font_size, args.watermark_num, args.custom_template, args.font)

            else:
                print("Error: No watermark text supplied.")
                exit(1)

        elif args.mode == '1': #if were just extracting the watermark
            check_watermark(args.input)

        else:
            print('Gotta enter a mode with -m')
            exit(1)

    elif args.input_file is not None: #if we are doing multiple images
        items = []

        try:#ensure there are no errors
            with open(args.input_file, 'r') as f: #open the input file
                items = f.readlines() #read its contents into an array
                f.close()

        except FileNotFoundError as err:
            print(err)
            exit(1)

        if args.mode == '0': #if were watermarking images
            if args.text is not None or args.custom_template is not None: #and we have text
                for item in items: #loop through them
                    if item.lower().endswith('.png') == False:
                       item = convert_to_png(item)


                    generate_watermark(item.strip('\n'), args.text, args.font_size, args.watermark_num)

            else:
                print("Error: No watermark text supplied.")
                exit(1)

        elif args.mode == '1': #if were checking
            for item in items: #loop through them
                check_watermark(item.strip('\n'))

        else:
            print('Gotta enter a mode with -m')
            exit(1)

    else: #no file :(
        print("Error: No file to watermark or check")
        exit(1)

if __name__ == "__main__":
    main()
