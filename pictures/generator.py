# -*- coding: utf-8

import io
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
    700 : {
        'image': Image.open('pictures/small.jpg').copy(),
        'start_pos_y': 140,
        'sign_offset_x': 40,
        'left_offset_x': 0,
        'align': ALIGN.CENTER,
    },
    854 : {
        'image': Image.open('pictures/middle.jpg').copy(),
        'start_pos_y': 140,
        'sign_offset_x': 40,
        'left_offset_x': 50,
        'align': ALIGN.CENTER,
    },
    MAX_TEXT_WIDTH: {
        'image': Image.open('pictures/big.jpg').copy(),
        'start_pos_y': 140,
        'sign_offset_x': 20,
        'left_offset_x': 80,
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


def check_dot(line):
    sentence = list(line)
    if sentence[-1] in ',:':
        sentence[-1] = '.'
        return ''.join(sentence)
    return line


def generate_image(lines, sign=None, title=None, show=False):
    lines[-1] = check_dot(lines[-1])
    widths = [_draw.textsize(line, font=_common_font)[0] for line in lines]
    max_width = max(widths)
    for size in sorted(TEMPLATES.keys()):
        if size >= max_width:
            template = TEMPLATES[size]
            break
    else:
        template = TEMPLATES[MAX_TEXT_WIDTH]

    sign_offset_x = template['sign_offset_x']
    left_offset_x = template['left_offset_x']
    img = template['image'].copy()
    draw = ImageDraw.Draw(img)
    max_text_width = img.size[0]
    align = template['align']
    fixed_x = None if align == ALIGN.CENTER else (max_text_width - max_width) / 2 - 40

    if title:
        w = _draw.textsize(title, font=_common_font)[0]
        x = (max_text_width - w) / 2 - left_offset_x
        draw.text((x, 60), up_and_dot(title), COMMON_COLOR, font=_common_font)


    for i, line in enumerate(lines):
        y = template['start_pos_y'] + i * LINE_DISTANCE
        x = 0
        if align == ALIGN.LEFT:
            x = fixed_x
        elif align == ALIGN.CENTER:
            x = (max_text_width - widths[i]) / 2
        elif align == ALIGN.RIGHT:
            x = (max_width - widths[i]) + fixed_x

        x -= left_offset_x
        draw.text((x, y), line, COMMON_COLOR, font=_common_font)

    y = img.size[1] - 80
    draw.text((sign_offset_x, y), 'https://vk.com/%s' % settings['group_id'],  COMMON_COLOR, font=_sign_font)
    if sign:
        y -= 40
        draw.text((sign_offset_x, y), sign + u' ©', COMMON_COLOR, font=_sign_font)

    if not show:
        b_arr = io.BytesIO()
        img.save(b_arr, format='PNG')
        return b_arr.getvalue()
    else:
        img.show()

if __name__ == '__main__':
    lines = [u'Ё' * 30]*3
    lines.append(u'я' * 32)
    generate_image(lines, sign='Ogneslav Arlovsky', title='Title', show=True)