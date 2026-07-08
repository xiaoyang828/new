#!/usr/bin/env python3
"""
🌸 Pixel Pet — ins风像素女孩桌宠
每个状态改面部表情，不遮黑。
"""

import tkinter as tk
from tkinter import messagebox
import random
import math
import time
import os
import sys

try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    print("pip install Pillow")
    sys.exit(1)

ANIM_MS = 100
MOVE_MS = 30
SPEED = 3.0
MARGIN = 40
TRANS_COLOR = "#FF00FF"
PET_HEIGHT = 150
CHARACTER_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "pet_character.png")

STATES = ["idle", "sing", "cute", "sleep", "cheer", "fly", "walk"]
STATE_DURATION = {
    "idle": (2, 4), "sing": (3, 6), "cute": (3, 5), "sleep": (5, 10),
    "cheer": (3, 5), "fly": (3, 6), "walk": (0, 0),
}

PALETTE = {
    "rose": "#E8B4C8", "lavender": "#C4B5D4", "sky": "#B8D4E3",
    "mint": "#C5D8C0", "cream": "#F5E8D8", "blush": "#F4D0D4",
    "slate": "#8A9AA8",
}


# ── 图片处理 ──

def load_base(image_path):
    """缩放 + 去白底"""
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    scale = PET_HEIGHT / h
    nw, nh = int(w * scale), int(h * scale)
    img = img.resize((nw, nh), Image.NEAREST)

    bg = set()
    stack = [(0, 0), (nw - 1, 0), (0, nh - 1), (nw - 1, nh - 1)]
    seen = set()
    while stack:
        x, y = stack.pop()
        if (x, y) in seen:
            continue
        if x < 0 or x >= nw or y < 0 or y >= nh:
            continue
        r, g, b, a = img.getpixel((x, y))
        if r < 250 or g < 250 or b < 250:
            continue
        seen.add((x, y))
        bg.add((x, y))
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            stack.append((x + dx, y + dy))

    px = img.load()
    for x, y in bg:
        px[x, y] = (255, 0, 255, 255)
    return img


def find_face_region(img):
    """找脸部区域：上半部中间的非白非透明区域"""
    px = img.load()
    w, h = img.size
    mid_x = w // 2

    # 在脸部区域采样肤色
    face_y_range = range(h // 4, h * 3 // 5)
    face_x_range = range(w // 5, w * 4 // 5)

    skin_colors = []
    for y in face_y_range:
        for x in face_x_range:
            r, g, b, a = px[x, y]
            if a > 200 and not (r > 248 and g > 248 and b > 248):
                skin_colors.append((r, g, b))

    if not skin_colors:
        return None, None, None, None

    # 取最常用的肤色
    avg_skin = tuple(sum(c[i] for c in skin_colors) // len(skin_colors) for i in range(3))

    # 找深色像素（眼睛、眉毛、嘴巴）
    dark = []
    for y in face_y_range:
        for x in face_x_range:
            r, g, b, a = px[x, y]
            if r < 100 and g < 100 and b < 100 and a > 200:
                dark.append((x, y))

    if not dark:
        return None, None, None, avg_skin

    # 分左右眼（上半部）
    left = [(x, y) for x, y in dark if x < mid_x and y < h * 2 // 4]
    right = [(x, y) for x, y in dark if x >= mid_x and y < h * 2 // 4]

    # 嘴巴（下半部中间）
    mouth = [(x, y) for x, y in dark
             if w // 4 < x < w * 3 // 4 and h * 3 // 7 < y < h * 3 // 5]

    def center(pts):
        if not pts:
            return None
        return (sum(p[0] for p in pts) // len(pts),
                sum(p[1] for p in pts) // len(pts))

    return center(left), center(right), center(mouth), avg_skin


def make_faces(base_img, left_eye, right_eye, mouth_pos, skin_color):
    """预生成各状态的面部表情（像素级修改）"""
    w, h = base_img.size
    faces = {}

    for state in STATES:
        img = base_img.copy()
        px = img.load()
        draw = ImageDraw.Draw(img)

        # 各状态的眼部修改参数
        if state == "idle":
            pass  # 原图

        elif state == "blink":
            # 闭眼：取肤色涂掉瞳孔
            if left_eye and right_eye:
                for ex, ey in [left_eye, right_eye]:
                    for dy in range(-3, 4):
                        for dx in range(-4, 5):
                            xx, yy = ex + dx, ey + dy
                            if 0 <= xx < w and 0 <= yy < h:
                                r, g, b, a = px[xx, yy]
                                if r < 120 and g < 120 and b < 120 and a > 200:
                                    px[xx, yy] = (*skin_color, 255)
                    # 眼睑线
                    lx = ex
                    for ly in range(ey - 1, ey + 1):
                        if 0 <= ly < h:
                            for lx2 in range(ex - 5, ex + 6):
                                if 0 <= lx2 < w:
                                    px[lx2, ly] = (max(0, skin_color[0] - 50),
                                                   max(0, skin_color[1] - 40),
                                                   max(0, skin_color[2] - 30), 255)

        elif state == "sing":
            # 笑眯眼 ^_^
            if left_eye and right_eye:
                for ex, ey in [left_eye, right_eye]:
                    for dy in range(-3, 4):
                        for dx in range(-4, 5):
                            xx, yy = ex + dx, ey + dy
                            if 0 <= xx < w and 0 <= yy < h:
                                r, g, b, a = px[xx, yy]
                                if r < 120 and g < 120 and b < 120 and a > 200:
                                    px[xx, yy] = (*skin_color, 255)
                    # 弧形眯眼
                    for dx in range(-5, 6):
                        dy = -abs(dx) // 2
                        yy = ey + dy
                        if 0 <= yy < h and 0 <= ex + dx < w:
                            px[ex + dx, yy] = (60, 50, 45, 255)

            # 画话筒（右侧手持位置）
            mic_x = w - 18
            mic_y = h - 70
            for my in range(mic_y - 5, mic_y + 14):
                if 0 <= mic_x < w and 0 <= my < h:
                    px[mic_x, my] = (100, 100, 100, 255)
                    px[mic_x - 1, my] = (80, 80, 80, 255)
                    px[mic_x + 1, my] = (80, 80, 80, 255)
            head_y = mic_y - 6
            for dy in range(-5, 6):
                for dx in range(-6, 7):
                    if dx * dx + dy * dy <= 30:
                        xx, yy = mic_x + dx, head_y + dy
                        if 0 <= xx < w and 0 <= yy < h:
                            px[xx, yy] = (60, 60, 60, 255)
            for dy in range(-3, 4):
                for dx in range(-4, 5):
                    if dx * dx + dy * dy <= 14:
                        xx, yy = mic_x + dx, head_y + dy
                        if 0 <= xx < w and 0 <= yy < h:
                            r, g, b, a = px[xx, yy]
                            px[xx, yy] = (90, 90, 90, 255)
            for hdx, hdy in [(-2, -2), (2, -2)]:
                xx, yy = mic_x + hdx, head_y + hdy
                if 0 <= xx < w and 0 <= yy < h:
                    px[xx, yy] = (160, 160, 160, 255)

        elif state == "cute":
            # >_< 大眼闪亮
            if left_eye:
                # 加大眼睛：加亮圈
                for dy in range(-4, 5):
                    for dx in range(-5, 6):
                        xx, yy = left_eye[0] + dx, left_eye[1] + dy
                        if 0 <= xx < w and 0 <= yy < h:
                            r, g, b, a = px[xx, yy]
                            if r < 120 and g < 120 and b < 120 and a > 200:
                                px[xx, yy] = (min(255, r + 60), min(255, g + 60), min(255, b + 60), 255)
                # 高光点
                for hy, hx in [(left_eye[1] - 2, left_eye[0] - 2)]:
                    if 0 <= hx < w and 0 <= hy < h:
                        px[hx, hy] = (255, 255, 255, 255)

        elif state == "sleep":
            # 闭眼 + 微弯
            if left_eye and right_eye:
                for ex, ey in [left_eye, right_eye]:
                    for dy in range(-3, 4):
                        for dx in range(-4, 5):
                            xx, yy = ex + dx, ey + dy
                            if 0 <= xx < w and 0 <= yy < h:
                                r, g, b, a = px[xx, yy]
                                if r < 120 and g < 120 and b < 120 and a > 200:
                                    px[xx, yy] = (*skin_color, 255)
                    # 向下弯的弧线（放松闭眼）
                    for dx in range(-5, 6):
                        dy = abs(dx) // 2 + 1
                        yy = ey + dy
                        if 0 <= yy < h and 0 <= ex + dx < w:
                            px[ex + dx, yy] = (80, 70, 60, 255)

        elif state == "cheer":
            # 星星眼
            if left_eye:
                # 眼睛亮点
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        xx, yy = left_eye[0] + dx, left_eye[1] + dy
                        if 0 <= xx < w and 0 <= yy < h:
                            r, g, b, a = px[xx, yy]
                            if r < 150 and g < 150 and b < 150 and a > 200:
                                px[xx, yy] = (min(255, r + 80), min(255, g + 80), min(255, b + 80), 255)
                # 十字星高光
                star_offsets = [(0, -3), (0, 3), (-3, 0), (3, 0)]
                for dx, dy in star_offsets:
                    xx, yy = left_eye[0] + dx, left_eye[1] + dy
                    if 0 <= xx < w and 0 <= yy < h:
                        px[xx, yy] = (255, 255, 255, 255)

        elif state == "fly":
            pass  # 保持原表情

        elif state == "walk":
            pass  # 保持原表情

        faces[state] = img

    return faces


# ── 桌宠 ──

class PixelPet:
    def __init__(self, image_path):
        self.root = tk.Tk()
        self.root.title("pixel pet")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", TRANS_COLOR)
        self.root.configure(bg=TRANS_COLOR)

        base = load_base(image_path)
        w, h = base.size

        # 找面部特征 + 生成各个状态的脸
        le, re, mp, skin = find_face_region(base)
        faces = make_faces(base, le, re, mp, skin)
        self._photos = {s: ImageTk.PhotoImage(faces[s]) for s in STATES}

        self.img_w, self.img_h = w, h
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.px = sw - w - 15
        self.py = sh - h - 50
        self.root.geometry(f"{w}x{h}+{self.px}+{self.py}")

        self.canvas = tk.Canvas(
            self.root, width=w, height=h,
            bg=TRANS_COLOR, highlightthickness=0,
        )
        self.canvas.pack()

        self.state = "idle"
        self.frame = 0
        self.dragging = False
        self.next_act = time.time() + 1.0
        self.bob = 0
        self.fly_y = 0
        self.fly_base = self.py
        self.facing = True  # True → 朝右
        self.moving = False
        self.tx = self.px
        self.ty = self.py

        # 生成水平翻转版图片
        self._photos_flip = {}
        for s, img in faces.items():
            self._photos_flip[s] = ImageTk.PhotoImage(img.transpose(Image.FLIP_LEFT_RIGHT))

        for wi in (self.canvas,):
            wi.bind("<Button-1>", self._drag_start)
            wi.bind("<B1-Motion>", self._drag_move)
            wi.bind("<ButtonRelease-1>", self._drag_end)
            wi.bind("<Button-3>", self._popup)

        self.root.after(50, lambda: self._safe(self._anim))
        self.root.after(50, lambda: self._safe(self._think))
        self.root.after(50, lambda: self._safe(self._move_loop))

    def _safe(self, fn):
        try:
            fn()
        except:
            import traceback
            traceback.print_exc()
            self.root.destroy()

    def _drag_start(self, e):
        self.dragging = True
        self._ox = e.x_root - self.root.winfo_x()
        self._oy = e.y_root - self.root.winfo_y()

    def _drag_move(self, e):
        if self.dragging:
            self.px = e.x_root - self._ox
            self.py = e.y_root - self._oy
            self.fly_base = self.py
            self.root.geometry(f"+{self.px}+{self.py}")

    def _drag_end(self, e):
        self.dragging = False
        self.moving = False
        self.fly_base = self.py
        if self.state == "walk":
            self._set(random.choice([s for s in STATES if s != "walk"]))
        self.next_act = time.time() + 1.0

    def _move_loop(self):
        if not self.root.winfo_exists():
            return
        if not self.dragging and self.moving:
            dx = self.tx - self.px
            dy = self.ty - self.py
            dist = math.hypot(dx, dy)
            if dist < 8:
                self.moving = False
                if self.state == "walk":
                    self._set(random.choice([s for s in STATES if s != "walk"]))
                    d = STATE_DURATION.get(self.state, (3, 6))
                    self.next_act = time.time() + random.uniform(*d)
            else:
                step = min(SPEED, dist)
                new_px = self.px + (dx / dist) * step
                new_py = self.py + (dy / dist) * step
                # 边界限制
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
                new_px = max(MARGIN, min(new_px, sw - self.img_w - MARGIN))
                new_py = max(MARGIN, min(new_py, sh - self.img_h - MARGIN))
                # 如果被边界卡住走不动了，取消行走
                if abs(new_px - self.px) < 0.5 and abs(new_py - self.py) < 0.5:
                    self.moving = False
                    if self.state == "walk":
                        self._set(random.choice([s for s in STATES if s != "walk"]))
                        d = STATE_DURATION.get(self.state, (3, 6))
                        self.next_act = time.time() + random.uniform(*d)
                else:
                    self.px, self.py = new_px, new_py
                    if abs(dx) > 2:
                        self.facing = dx > 0
                    self.root.geometry(f"+{int(self.px)}+{int(self.py)}")
        self.root.after(MOVE_MS, lambda: self._safe(self._move_loop))

    def _popup(self, e):
        m = tk.Menu(self.root, tearoff=0, bg="#FAF6F0", fg="#5A4A3A",
                     font=("Microsoft YaHei", 10),
                     activebackground="#E8D0C8", activeforeground="#3A2A1A")
        for k in STATES:
            m.add_command(label=k.capitalize(), command=lambda s=k: self._set(s))
        m.add_separator()
        m.add_command(label="About", command=self._about)
        m.add_command(label="Exit", command=self._quit)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    def _about(self):
        messagebox.showinfo("pixel pet", "a tiny pixel girl on your desktop")

    def _set(self, s):
        if self.state == "fly":
            self.root.geometry(f"+{self.px}+{self.fly_base}")
        self.state = s
        self.frame = 0
        if s == "fly":
            self.fly_y = 0

    def _think(self):
        if not self.root.winfo_exists():
            return
        if not self.dragging and time.time() >= self.next_act:
            self._decide()
        self.root.after(600, lambda: self._safe(self._think))

    def _walk_to(self):
        """选一个随机水平位置走过去"""
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        margin = 40
        self.tx = random.randint(margin, sw - self.img_w - margin)
        self.ty = sh - self.img_h - 50 + random.randint(-10, 10)
        self.moving = True
        self._set("walk")
        dist = abs(self.tx - self.px)
        sec = dist / (SPEED * 1000 / MOVE_MS) + 0.5
        self.next_act = time.time() + max(sec, 2.0)

    def _decide(self):
        if self.state == "walk":
            return
        r = random.random()
        if r < 0.35:
            # 35% 概率走路
            self._walk_to()
            return
        # 其他地方选非 walk 的状态
        pool = [s for s in STATES if s != "walk"]
        if self.state in pool:
            pool.remove(self.state)
            pool.append(self.state)
            pool.append(self.state)
        next_s = random.choice(pool)
        self._set(next_s)
        d = STATE_DURATION.get(next_s, (3, 6))
        self.next_act = time.time() + random.uniform(*d)

    def _anim(self):
        if not self.root.winfo_exists():
            return
        self.canvas.delete("all")

        # float
        fy = 0
        if self.state == "cheer":
            fy = math.sin(self.bob * 0.15) * 2
        else:
            fy = math.sin(self.bob * 0.05) * 1.5
        self.bob += 1

        # 当前状态对应的面部图片（根据朝向选翻转版）
        if self.facing:
            photo = self._photos.get(self.state, self._photos["idle"])
        else:
            photo = self._photos_flip.get(self.state, self._photos_flip["idle"])
        self.canvas.create_image(
            self.img_w // 2, self.img_h // 2 + int(fy),
            image=photo, anchor=tk.CENTER,
        )

        f = self.frame

        # ── 轻量特效（置于角色之上） ──
        if self.state == "sing":
            # 飘浮音符
            for i in range(3):
                note_x = (f * 2 + i * 40) % self.img_w
                note_y = 6 + (f * 3 + i * 30) % (self.img_h // 2)
                note = ["♪", "♫", "♩"][i]
                alpha = 1.0 - (note_y / (self.img_h // 2))
                self.canvas.create_text(
                    note_x, note_y,
                    text=note, fill=PALETTE["rose"],
                    font=("Microsoft YaHei", 8 + i * 2),
                )

        elif self.state == "cute":
            # 飘心
            hx, hy = self.img_w // 2, 10 + (f % 12) * 1.5
            s = 5 + math.sin(f * 0.2) * 1
            pts = []
            for ang in range(0, 360, 30):
                a = math.radians(ang)
                # heart shape
                hs = s * math.sqrt(abs(math.sin(a * 2)))
                pts += [hx + hs * math.sin(a) * 1.2,
                        hy - hs * math.cos(a)]
            self.canvas.create_polygon(
                pts, outline=PALETTE["rose"],
                fill="", width=1, smooth=True,
            )

        elif self.state == "sleep":
            # 只飘 Zzz，不遮黑
            z = "z" * (1 + (f // 8) % 3)
            for i, ch in enumerate(z):
                self.canvas.create_text(
                    self.img_w - 12, 6 + i * 8 + (f % 8) * 1.5,
                    text=ch, fill=PALETTE["lavender"],
                    font=("Microsoft YaHei", 7 + i * 2),
                )

        elif self.state == "cheer":
            # 小星星
            cx, cy = self.img_w // 2, 8 + (f % 10) * 1.5
            self.canvas.create_text(
                cx, cy,
                text="✦", fill=PALETTE["cream"],
                font=("Microsoft YaHei", 10),
            )

        elif self.state == "walk":
            # 走路不需要额外特效，用原图
            pass

        elif self.state == "fly":
            # 翅膀（几何线框）
            wf = math.sin(f * 0.3) * 5
            cx, cy = self.img_w // 2, self.img_h // 2
            for flip in (-1, 1):
                bx = cx + flip * 22
                by = cy - 10
                self.canvas.create_polygon(
                    bx, by,
                    bx + flip * (14 + wf), by - 6,
                    bx + flip * (12 + wf), by + 14,
                    bx + flip * 3, by + 6,
                    fill="", outline=PALETTE["lavender"], width=1,
                )
                self.canvas.create_line(
                    bx, by,
                    bx + flip * (8 + wf * 0.5), by - 3,
                    fill=PALETTE["lavender"], width=1,
                )
            self.fly_y = math.sin(f * 0.05) * 40
            self.root.geometry(
                f"+{self.px}+{int(self.fly_base + self.fly_y)}"
            )

        self.frame += 1
        self.root.after(ANIM_MS, lambda: self._safe(self._anim))

    def _quit(self):
        try:
            self.root.destroy()
        except:
            pass

    def run(self):
        self.next_act = time.time() + 3.0
        self.root.mainloop()


if __name__ == "__main__":
    for p in [CHARACTER_IMAGE,
              "C:/Users/Lenovo/Desktop/f94fbcb8c1d65c1a966a73f68abeab16.png"]:
        if os.path.exists(p):
            PixelPet(p).run()
            break
    else:
        print("[X] image not found")
        sys.exit(1)
