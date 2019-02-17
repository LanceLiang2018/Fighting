import imageio
from PIL import Image, ImageGrab, ImageDraw, ImageFont, ImageColor
import win32gui
import win32console
import win32con
import time
import sys
import os
import numpy as np
from tqdm import trange
import random
import copy

char_blank, char_filled = '　', '；'
strings_blank = '莫堕英雄之志 三年当有无双 六月搏击登天堑 俯瞰神州 磨剑十年 不淬安能成大器'
strings_enter = '莫堕英雄之志\n三年当有无双\n六月搏击登天堑\n\n\n俯瞰神州\n磨剑十年\n不淬安能成大器\n'
strings = '莫堕英雄之志三年当有无双六月搏击登天堑俯瞰神州磨剑十年不淬安能成大器'
single = []
welcome = ['''CKH ASCII Art [版本 2019.02.17 03:39]
(R) 2019 CKH Group。保留所有权利。
C:\\Users\\Lance>''', 'F', 'ighting']
frame = (512 * 2, 512 * 2)
frame_char = 460 * 2


class Point:
    def __init__(self, char: str = char_filled, x: int = 0, y: int = 0, mode: str = "normal", to_index: int = 0):
        if mode == 'rand':
            self.x = random.randint(0, x-1)
            self.y = random.randint(0, y-1)
        else:
            self.x = x
            self.y = y
        self.char = char
        self.to_index = to_index

    def set_char(self, char: str):
        self.char = char


class Single:
    def __init__(self, char: str, chars: str):
        self.filled = 0
        self.chars = get_one(char, chars)
        self.char = char
        self.points = []
        for i in self.chars:
            if i == self.char:
                self.filled = self.filled + 1
        split = self.chars.split('\n')
        count = 0
        fix = frame_char // 46
        for y in range(len(split)):
            for x in range(len(split[y])):
                if not split[y][x] == char_blank:
                    self.points.append(Point(x=x*fix, y=y*fix, char=split[y][x], to_index=count))
                    count = count + 1

    def __str__(self):
        return "[\n%s, filled=%d]" % (self.chars, self.filled)


def put_one(char: str, chars: str):
    for i in chars.split('\n'):
        for j in i:
            if j == char_filled:
                print(char, end='')
            else:
                print(char_blank, end='')
        print()


def get_one(char: str, chars: str):
    res = ''
    for i in chars.split('\n'):
        for j in i:
            if j == char_filled:
                res = res + char
            else:
                res = res + char_blank
        res = res + '\n'
    return res


def init_chars():
    global single
    with open('text.txt', encoding='utf-8') as f:
        split = f.read().split('\n\n')
    for i in range(len(split)):
        single.append(Single(strings[i], split[i]))


def form_video():
    writer = imageio.get_writer('result.mp4', 'ffmpeg', fps=60)

    li = os.listdir('imgs/')
    li.sort()
    for f in trange(len(li)):
        file = li[f]
        im = Image.open('imgs/%s' % file)
        stime = 20
        if f < 3:
            stime = 10
        for i in range(stime):
            writer.append_data(np.array(im))

    writer.close()


def form_images():
    count = 1

    os.system("cls")
    time.sleep(0.1)
    hwnd = int(win32console.GetConsoleWindow())
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, 30, 0, 1294, 727, win32con.SWP_SHOWWINDOW)
    left_start = 37

    for w in welcome:
        print(w, end='')
        sys.stdout.flush()
        time.sleep(0.1)
        img = ImageGrab.grab(bbox=(left_start, 0, 1280 + left_start, 720))
        img.save('imgs/%02d.bmp' % count)
        count = count + 1
        time.sleep(0.1)

    print("\n\n")

    blank_num = 20
    print(char_blank * blank_num, end='')
    sys.stdout.flush()
    for c in strings_enter:
        if c == '\n':
            print("")
            print(char_blank * blank_num, end='')
            sys.stdout.flush()
            continue
        print(c, end='')
        sys.stdout.flush()
        time.sleep(0.1)
        img = ImageGrab.grab(bbox=(left_start, 0, 1280 + left_start, 720))
        img.save('imgs/%02d.bmp' % count)
        count = count + 1
        time.sleep(0.1)


def make_alpha(image):
    im = image.copy()
    limit = 254
    imd = np.array(im)
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            if imd[y][x][0] > limit or imd[y][x][1] > limit or imd[y][x][2] > limit:
                im.putpixel((x, y), (255, 255, 255, 0))
            else:
                im.putpixel((x, y), (imd[y][x][0], imd[y][x][1], imd[y][x][2], 255))
    return im


def set_to_index(points: list):
    new_points = points
    new_index = []
    for i in range(len(points)):
        new_index.append(i)
    random.shuffle(new_index)
    for i in range(len(new_points)):
        new_points[i].to_index = new_index[i]
    return new_points


img_tmp = {}


def draw_one(img_src, points: list):
    global img_tmp
    im = img_src.copy()

    draw = ImageDraw.Draw(im)
    for p in points:
        char = p.char

        if char not in img_tmp:
            box0 = draw.textsize(char, font=font)
            box = list(map(lambda x: int(x), (box0[0] * 1.45, box0[1] * 1.45)))
            im_char = Image.new("RGBA", box, color=ImageColor.getcolor("#FFFFFF", "RGBA"))
            draw = ImageDraw.Draw(im_char)

            draw.ink = 0 + 0 * 256 + 0 * 256 * 256
            draw.text(((box[0] - box0[0]) // 2, (box[0] - box0[0]) // 2), char, font=font)
            # im_char = im_char.rotate(random.randint(0, 360), fillcolor="white")
            im_char = make_alpha(im_char)

            img_tmp[char] = im_char.copy()

        im_char = img_tmp[char]

        r, g, b, a = im_char.split()
        im.paste(r, (p.x, p.y), mask=a)

    return im


def make_point():
    directions = [(frame[0], 0), (-frame[0], 0), (0, frame[1]), (0, -frame[1])]

    # 初始化点，把点初始化到画布之外
    point = Point(x=frame[0], y=frame[1], mode='rand', char=strings[0])
    rand_direction = random.randint(0, 4 - 1)
    point.x = point.x + directions[rand_direction][0]
    point.y = point.y + directions[rand_direction][1]

    return point


def patch_animation(img_src, points: list, sindex: int, frame_count: int = 30):
    patch = []

    fun = lambda x: (1 / (frame_count - x) + 0.8)
    fix = 0.9

    for i in range(frame_count):
        img_res = draw_one(img_src, points)
        patch.append(img_res.copy())
        for p in range(len(points)):
            points[p].x = int(points[p].x + (single[sindex].points[points[p].to_index].x - points[p].x + 1) / (frame_count / 10))
            points[p].y = int(points[p].y + (single[sindex].points[points[p].to_index].y - points[p].y + 1) / (frame_count / 10))

    return patch


def make_animation():
    writer = imageio.get_writer('anima/animation.mp4', 'ffmpeg', fps=30)

    count = len(single[0].points)
    points = []
    im = blank.crop((0, 0, frame[0], frame[1]))

    for i in range(count):
        points.append(make_point())

    for s in trange(len(single)):
        points = set_to_index(points)
        patch = patch_animation(im, points=points, sindex=s, frame_count=15)
        for p in patch:
            writer.append_data(np.array(p))
        if s != len(single) - 1:
            points = copy.deepcopy(single[s+1].points)

    writer.close()


def make_animation_test():
    writer = imageio.get_writer('anima/animation.mp4', 'ffmpeg', fps=60)

    im = blank.crop((0, 0, frame[0], frame[1]))

    for i in trange(60 * 1):
        draw = ImageDraw.Draw(im)
        char = strings[random.randint(0, len(strings) - 1)]

        box0 = draw.textsize(char, font=font)
        box = list(map(lambda x: int(x), (box0[0] * 1.45, box0[1] * 1.45)))
        im_char = Image.new("RGBA", box, color=ImageColor.getcolor("#FFFFFF", "RGBA"))
        draw = ImageDraw.Draw(im_char)

        draw.ink = 0 + 0 * 256 + 0 * 256 * 256
        draw.text(((box[0] - box0[0]) // 2, (box[0] - box0[0]) // 2), char, font=font)
        im_char = im_char.rotate(random.randint(0, 360), fillcolor="white")
        im_char = make_alpha(im_char)

        r, g, b, a = im_char.split()
        im.paste(r, (random.randint(0, frame[0]), random.randint(0, frame[1])), mask=a)
        writer.append_data(np.array(im))

    writer.close()


# font = ImageFont.truetype("YaheiMono.ttf", 10)
font = ImageFont.truetype("msyhbd.ttc", 20)
blank = Image.new("RGBA", (1920 * 4, 1080 * 4), color="white")


if __name__ == '__main__':
    init_chars()
    # print(single[3])

    # form_images()

    form_video()

    # make_animation()
