#!/usr/bin/env python3
"""
🐱 桌面宠物 - 一只会走路、眨眼、撒娇的小猫

使用 Python 标准库 tkinter，零额外依赖。
支持 Windows / macOS / Linux。
"""

import tkinter as tk
from tkinter import messagebox
import random
import math
import time

# ============================================================
#  配置
# ============================================================
ANIM_MS = 70                   # 动画帧间隔（毫秒）
MOVE_MS = 30                   # 移动更新间隔
MARGIN = 40                    # 屏幕边缘留白
WIN_W, WIN_H = 86, 90          # 窗口尺寸
SPEED = 1.8                    # 像素/帧（move loop 每帧）
TRANS_COLOR = "#FF00FF"        # 透明色（洋红）

# 颜色
SKIN  = "#F5DEB3"             # 猫毛色 － 小麦色
DARK  = "#D2B48C"             # 深色毛
PINK  = "#FFB6C1"             # 粉色（耳朵内、鼻子）
WHITE = "#FFFFFF"
BLACK = "#333333"
WHISK = "#999999"

# 每种状态的帧周期数
FRAMES = {
    "idle":    10,
    "blink":    4,
    "walk":     8,
    "stretch":  8,
    "sleep":    6,
    "wake":     4,
    "happy":    8,
}


# ============================================================
#  绘图引擎
# ============================================================
def draw_cat(canvas, frame: int, cx: int, cy: int,
             state: str = "idle", facing_right: bool = True) -> None:
    """
    在 canvas 的 (cx, cy) 处绘制小猫。
    (cx, cy) 是猫的腹部中心坐标。
    朝向由 facing_right 控制（尾巴、胡须偏向）。
    """
    f = frame
    blink  = state in ("blink", "sleep", "wake") and f % 2 == 0
    sleep  = state == "sleep"
    happy  = state == "happy"
    walk   = state == "walk"
    stretch = state.startswith("stretch")

    # ---- 呼吸 / 走路起伏 ----
    body_off = 0
    if walk:
        body_off = -1 if f % 2 == 0 else 1
    elif sleep:
        body_off = 2

    # ---- 尾巴（方向敏感） ----
    tw = math.sin(f * 0.4 + (0 if facing_right else 3.14)) * 7
    tail_dir = 1 if facing_right else -1
    tx = cx + 16 * tail_dir
    ty = cy - 26 + body_off
    canvas.create_line(
        tx, ty,
        tx + (10 + tw) * tail_dir, ty - 8 - abs(tw) * 0.3,
        fill=DARK, width=3, smooth=True, capstyle=tk.ROUND,
    )

    # ---- 身体 ----
    bx, by = cx - 20, cy - 18 + body_off
    canvas.create_oval(bx, by, bx + 40, by + 32, fill=SKIN, outline="", width=0)

    # ---- 前腿（走路交替） ----
    leg_step = 2 if walk else 0
    for i, lx in enumerate([-10, 3]):
        lo = leg_step if i == f % 2 else -leg_step
        canvas.create_oval(
            cx + lx + lo, cy - 4,
            cx + lx + 7 + lo, cy + 6,
            fill=SKIN, outline="",
        )

    # ---- 头 ----
    hx, hy = cx - 16, cy - 36 + body_off
    canvas.create_oval(hx, hy, hx + 32, hy + 28, fill=SKIN, outline="", width=0)

    # ---- 耳朵 ----
    ew = 2 if stretch and f < 4 else -2 if stretch else 0

    def _ear(p1, p2, p3):
        canvas.create_polygon(p1, p2, p3, fill=SKIN, outline=DARK, width=1)
        # 粉色内耳
        mx = (p1[0] + p2[0] + p3[0]) / 3
        my = (p1[1] + p2[1] + p3[1]) / 3 + 2
        s = 4
        canvas.create_polygon(
            (mx - s, my + 2), (mx + s, my + 2), (mx, my - s),
            fill=PINK, outline="",
        )

    _ear(
        (hx + 3 + ew, hy + 4),
        (hx + 7 - ew, hy - 11),
        (hx + 15, hy + 4),
    )
    _ear(
        (hx + 21 - ew, hy + 4),
        (hx + 25 + ew, hy - 11),
        (hx + 32, hy + 4),
    )

    # ---- 眼睛 ----
    eye_y = hy + 14
    if blink or sleep:
        canvas.create_line(cx - 5 - 4, eye_y, cx - 5 + 4, eye_y, fill=BLACK, width=2)
        canvas.create_line(cx + 5 - 4, eye_y, cx + 5 + 4, eye_y, fill=BLACK, width=2)
    else:
        for ex in (cx - 5, cx + 5):
            canvas.create_oval(ex - 3, eye_y - 3, ex + 3, eye_y + 3, fill=BLACK)
            canvas.create_oval(ex, eye_y - 2, ex + 2, eye_y - 1, fill=WHITE)

    # ---- 鼻子 ----
    nx, ny = cx, eye_y + 5
    canvas.create_polygon(nx, ny - 2, nx - 3, ny + 2, nx + 3, ny + 2, fill=PINK)

    # ---- 嘴巴 ----
    if happy:
        # 笑脸 ^_^
        canvas.create_arc(nx - 6, ny + 1, nx + 6, ny + 9,
                          start=0, extent=-180, style=tk.ARC, outline=BLACK, width=1)
    elif sleep:
        # 睡觉嘴 ～～
        for ox in (-3, 3):
            canvas.create_arc(nx + ox - 2, ny + 4, nx + ox + 2, ny + 8,
                              start=180, extent=-180, style=tk.ARC, outline=BLACK, width=1)
    else:
        canvas.create_line(nx - 3, ny + 2, nx - 1, ny + 6, fill=BLACK, width=1)
        canvas.create_line(nx + 3, ny + 2, nx + 1, ny + 6, fill=BLACK, width=1)

    # ---- 胡须（方向敏感） ----
    d = 1 if facing_right else -1
    wy = ny + 1
    for off, ym in [(-3, 1), (3, 1)]:
        canvas.create_line(nx + off, wy, nx + off + 12 * d, wy + ym * 2, fill=WHISK, width=1)
        canvas.create_line(nx + off, wy, nx + off + 12 * d, wy - ym * 1, fill=WHISK, width=1)


# ============================================================
#  桌面宠物应用
# ============================================================
class DesktopPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐱 桌面宠物")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", TRANS_COLOR)
        self.root.configure(bg=TRANS_COLOR)

        # 屏幕尺寸
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        # 窗口初始位置（右下角）
        self.px = self.sw - 220
        self.py = self.sh - 200
        self.root.geometry(f"{WIN_W}x{WIN_H}+{self.px}+{self.py}")

        # Canvas
        self.canvas = tk.Canvas(
            self.root, width=WIN_W, height=WIN_H,
            bg=TRANS_COLOR, highlightthickness=0,
        )
        self.canvas.pack()

        # 猫在窗口中的绘制坐标（居中偏下）
        self.cx = WIN_W // 2
        self.cy = WIN_H - 8

        # ---- 状态 ----
        self.state = "idle"
        self.frame = 0
        self.facing = True          # True → 朝右
        self.moving = False
        self.dragging = False

        # 目标坐标（屏幕坐标）
        self.tx = self.px
        self.ty = self.py

        # 计时
        self.next_act = time.time() + 1.0

        # ---- 鼠标事件 ----
        for widget in (self.canvas, self.root):
            widget.bind("<Button-1>",        self._drag_start)
            widget.bind("<B1-Motion>",       self._drag_move)
            widget.bind("<ButtonRelease-1>", self._drag_end)
            widget.bind("<Button-3>",        self._popup_menu)

        # ---- 启动循环 ----
        self.root.after(50, self._anim_loop)
        self.root.after(50, self._move_loop)
        self.root.after(50, self._think_loop)

    # ==================== 拖拽 ====================
    def _drag_start(self, e):
        self.dragging = True
        self.moving = False
        self._ox = e.x_root - self.root.winfo_x()
        self._oy = e.y_root - self.root.winfo_y()

    def _drag_move(self, e):
        if self.dragging:
            self.px = e.x_root - self._ox
            self.py = e.y_root - self._oy
            self.root.geometry(f"+{self.px}+{self.py}")

    def _drag_end(self, e):
        self.dragging = False
        if self.state == "walk":
            self._set_state("idle")
        self.next_act = time.time() + 1.0

    # ==================== 右键菜单 ====================
    def _popup_menu(self, e):
        menu = tk.Menu(self.root, tearoff=0, bg="#FFF8DC", fg="#333",
                       font=("Microsoft YaHei", 10),
                       activebackground="#FFD700", activeforeground="#333")
        sm = tk.Menu(menu, tearoff=0, bg="#FFF8DC", fg="#333",
                     activebackground="#FFD700")
        for lbl, st in [("😊 开心", "happy"), ("😴 睡觉", "sleep"),
                        ("🧘 伸懒腰", "stretch"), ("😐 正常", "idle")]:
            sm.add_command(label=lbl, command=lambda s=st: self._set_state(s))
        menu.add_cascade(label="🎭 切换状态", menu=sm)
        menu.add_separator()
        menu.add_command(label=" 关于", command=self._about)
        menu.add_command(label="❌ 退出", command=self._quit)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _about(self):
        messagebox.showinfo("🐱 桌面宠物",
                            "一只会眨眼、走路、撒娇的小猫\n"
                            "拖拽移动 · 右键菜单切换状态\n\n"
                            "Python + tkinter · 零依赖")

    def _set_state(self, s):
        """安全切换动画状态"""
        if self.state != s:
            self.state = s
            self.frame = 0

    # ==================== 行为决策 ====================
    def _think_loop(self):
        if not self.root.winfo_exists():
            return
        now = time.time()
        if not self.dragging and not self.moving and now >= self.next_act:
            self._decide()
        self.root.after(600, self._think_loop)

    def _decide(self):
        """自动行为选择器"""
        if self.state in ("sleep", "stretch"):
            if time.time() >= self.next_act:  # 睡/伸够久了
                self._set_state("idle")
                self.next_act = time.time() + random.uniform(1, 3)
            return

        if self.state == "idle":
            r = random.random()
            if r < 0.20:
                self._walk()
            elif r < 0.40:
                self._set_state("blink")
                self.next_act = time.time() + 0.4
            elif r < 0.55:
                self._set_state("happy")
                self.next_act = time.time() + 1.5
            elif r < 0.70:
                self._set_state("stretch")
                self.next_act = time.time() + 3.5
            elif r < 0.85:
                self._set_state("sleep")
                self.next_act = time.time() + random.uniform(4, 7)
            else:
                self.next_act = time.time() + 1.5
        elif self.state in ("blink", "happy"):
            self._set_state("idle")
            self.next_act = time.time() + random.uniform(1, 3)
        else:
            self.next_act = time.time() + 1.0

    def _walk(self):
        """走向随机目标"""
        self._set_state("walk")
        margin = 100
        self.tx = random.randint(margin, self.sw - WIN_W - margin)
        self.ty = random.randint(margin, self.sh - WIN_H - margin)
        self.moving = True
        dist = math.hypot(self.tx - self.px, self.ty - self.py)
        # 速度 = SPEED px/帧 × 1000ms/MOVE_MS 帧/s
        sec = dist / (SPEED * 1000 / MOVE_MS) + 0.5
        self.next_act = time.time() + max(sec, 2.0)

    # ==================== 移动 ====================
    def _move_loop(self):
        if not self.root.winfo_exists():
            return
        if not self.dragging and self.moving:
            dx, dy = self.tx - self.px, self.ty - self.py
            dist = math.hypot(dx, dy)
            if dist < 5:
                self.moving = False
                self._set_state("idle")
            else:
                step = min(SPEED, dist)
                self.px += (dx / dist) * step
                self.py += (dy / dist) * step
                # 朝向
                if abs(dx) > 2:
                    self.facing = dx > 0
                # 边界
                self.px = max(MARGIN, min(self.px, self.sw - WIN_W - MARGIN))
                self.py = max(MARGIN, min(self.py, self.sh - WIN_H - MARGIN))
                self.root.geometry(f"+{int(self.px)}+{int(self.py)}")
        self.root.after(MOVE_MS, self._move_loop)

    # ==================== 动画 ====================
    def _anim_loop(self):
        if not self.root.winfo_exists():
            return
        self.canvas.delete("all")
        max_f = FRAMES.get(self.state, 6)
        draw_cat(self.canvas, self.frame % max_f,
                  self.cx, self.cy, self.state, self.facing)
        self.frame += 1
        self.root.after(ANIM_MS, self._anim_loop)

    # ==================== 退出 ====================
    def _quit(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self._set_state("idle")
        self.root.mainloop()


# ============================================================
#  启动入口
# ============================================================
if __name__ == "__main__":
    DesktopPet().run()
