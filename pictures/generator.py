# -*- coding: utf-8

from PIL import Image, ImageFont, ImageDraw
from settings import settings


class ALIGN:
    LEFT = 1
    CENTER = 2
    RIGHT = 3


LINE_DISTANCE = 60
COMMON_COLOR = (0, 0, 0)
COMMON_FONT_SIZE = 50
SIGN_FONT_SIZE = 34
MAX_TEXT_WIDTH = 2000


TEMPLATES = {
    720 : {
        'image': Image.open('pictures/small.jpg'),
        'start_pos_y': 140,
        'min_offset_x': 40,
        'align': ALIGN.CENTER,
    },
    880 : {
        'image': Image.open('pictures/middle.jpg'),
        'start_pos_y': 140,
        'min_offset_x': 40,
        'align': ALIGN.CENTER,
    },
    MAX_TEXT_WIDTH: {
        'image': Image.open('pictures/big.jpg'),
        'start_pos_y': 140,
        'min_offset_x': 40,
        'align': ALIGN.CENTER,
    },
}


_common_font = ImageFont.truetype("pictures/tahoma.ttf", COMMON_FONT_SIZE)
_sign_font = ImageFont.truetype("pictures/tahoma.ttf", SIGN_FONT_SIZE)
_draw = ImageDraw.Draw(TEMPLATES[MAX_TEXT_WIDTH]['image'])


def up_and_dot(title):
    title = title.strip()
    title = title[0].upper() + title[1:]
    title = ' '.join(title.split())
    if title[-1] not in '!?).':
        title += '.'
    return title


def generate_image(lines, sign=None, title=None, result_file=None):
    widths = [_draw.textsize(line, font=_common_font)[0] for line in lines]
    max_width = max(widths)
    for size in sorted(TEMPLATES.keys()):
        if size >= max_width:
            template = TEMPLATES[size]
            break
    else:
        template = TEMPLATES[MAX_TEXT_WIDTH]

    min_offset_x = template['min_offset_x']
    img = template['image'].copy()
    draw = ImageDraw.Draw(img)
    max_text_width = img.size[0]
    align = template['align']
    fixed_x = None if align == ALIGN.CENTER else (max_text_width - max_width) / 2

    if title:
        w = _draw.textsize(title, font=_common_font)[0]
        x = (max_text_width - w) / 2
        draw.text((x, 60), up_and_dot(title), COMMON_COLOR, font=_common_font)


    for i, line in enumerate(lines):
        y = template['start_pos_y'] + i * LINE_DISTANCE
        if align == ALIGN.LEFT:
            x = fixed_x
        elif align == ALIGN.CENTER:
            x = (max_text_width - widths[i]) / 2
        elif align == ALIGN.RIGHT:
            x = (max_width - widths[i]) + fixed_x
        draw.text((x, y), line, COMMON_COLOR, font=_common_font)

    y = img.size[1] - 80
    draw.text((min_offset_x, y), 'https://vk.com/%s' % settings['group_id'],  COMMON_COLOR, font=_sign_font)
    if sign:
        y -= 40
        draw.text((min_offset_x, y), sign + u' ©', COMMON_COLOR, font=_sign_font)

    if result_file:
        img.save(result_file)
    else:
        img.show()