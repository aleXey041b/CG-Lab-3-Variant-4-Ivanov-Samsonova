import math
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk

class CGLab3:

    def __init__(self, root):
        self.root = root
        self.root.title("Растеризация отрезков прямых")
        self.root.geometry("900x780")

        self.img = None
        self.base_img = None
        self.line_pixels = set()
        self.tk_img = None
        self.methods = ["ЦДА", "Брезенхем (вещественный)",
                        "Брезенхем (целочисленный)", "Встроенный метод"]
        self.colors = [(255, 60, 60), (40, 160, 70),
                       (40, 90, 240), (195, 60, 185)]

        top_frame = tk.Frame(root, padx=10, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text="Width").grid(row=0, column=0, padx=3, pady=3)
        self.entry_w = tk.Entry(top_frame, width=6)
        self.entry_w.insert(0, "100")
        self.entry_w.grid(row=0, column=1)

        tk.Label(top_frame, text="Height").grid(row=1, column=0, padx=3, pady=3)
        self.entry_h = tk.Entry(top_frame, width=6)
        self.entry_h.insert(0, "100")
        self.entry_h.grid(row=1, column=1)

        tk.Label(top_frame, text="x1").grid(row=0, column=2, padx=3)
        self.entry_x1 = tk.Entry(top_frame, width=6)
        self.entry_x1.insert(0, "45")
        self.entry_x1.grid(row=0, column=3)

        tk.Label(top_frame, text="y1").grid(row=1, column=2, padx=3)
        self.entry_y1 = tk.Entry(top_frame, width=6)
        self.entry_y1.insert(0, "15")
        self.entry_y1.grid(row=1, column=3)

        tk.Label(top_frame, text="x2").grid(row=0, column=4, padx=3)
        self.entry_x2 = tk.Entry(top_frame, width=6)
        self.entry_x2.insert(0, "55")
        self.entry_x2.grid(row=0, column=5)

        tk.Label(top_frame, text="y2").grid(row=1, column=4, padx=3)
        self.entry_y2 = tk.Entry(top_frame, width=6)
        self.entry_y2.insert(0, "85")
        self.entry_y2.grid(row=1, column=5)

        tk.Label(top_frame, text="Диагональ 2").grid(row=0, column=6, padx=3)
        self.entry_d = tk.Entry(top_frame, width=6)
        self.entry_d.insert(0, "70")
        self.entry_d.grid(row=0, column=7)

        tk.Button(top_frame, text="Создать", command=self.create_canvas, width=12).grid(
            row=0, column=8, padx=5)
        self.button_draw = tk.Button(top_frame, text="Построить ромб",
                                     command=self.draw_rhombus, width=15, state=tk.DISABLED)
        self.button_draw.grid(row=1, column=8, padx=5)
        tk.Button(top_frame, text="Открыть", command=self.open_image, width=14).grid(
            row=1, column=9, padx=5)
        tk.Button(top_frame, text="Сохранить", command=self.save_image, width=14).grid(
            row=0, column=9, padx=5)
        tk.Button(top_frame, text="Сохранить PBM", command=self.save_pbm, width=15).grid(
            row=0, column=10, padx=5)

        legend = tk.Frame(root, padx=10)
        legend.pack(fill=tk.X)
        for i, method in enumerate(self.methods):
            color = "#%02x%02x%02x" % self.colors[i]
            tk.Label(legend, text="■ " + method, fg=color).pack(side=tk.LEFT, padx=9)
        tk.Label(root, text="Тёмно-серый - совпадающие пиксели.").pack()

        self.info_label = tk.Label(root, text="")
        self.info_label.pack(pady=4)

        self.image_label = tk.Label(root, bg=root.cget("bg"))
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def get_size(self):
        return int(self.entry_w.get()), int(self.entry_h.get())

    def create_canvas(self):
        w, h = self.get_size()
        self.base_img = Image.new("RGB", (w, h), "white")
        self.img = self.base_img.copy()
        self.line_pixels = set()
        self.info_label.config(text="")
        self.button_draw.config(state=tk.NORMAL)
        self.update_display()

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp"), ("Все файлы", "*.*")])
        if file_path:
            self.base_img = Image.open(file_path).convert("RGB")
            self.img = self.base_img.copy()
            self.line_pixels = set()
            w, h = self.img.size
            self.entry_w.delete(0, tk.END)
            self.entry_w.insert(0, str(w))
            self.entry_h.delete(0, tk.END)
            self.entry_h.insert(0, str(h))
            self.info_label.config(text="")
            self.button_draw.config(state=tk.NORMAL)
            self.update_display()

    def dda(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return [(x1, y1)]
        x_step = dx / steps
        y_step = dy / steps
        x, y = x1, y1
        points = []
        for i in range(steps + 1):
            points.append((math.floor(x + 0.5), math.floor(y + 0.5)))
            x += x_step
            y += y_step
        return points

    def bresenham_float(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        if dx == 0 and dy == 0:
            return [(x1, y1)]
        steep = dy > dx
        if steep:
            dx, dy = dy, dx
        m = dy / dx
        error = m - 0.5
        x, y = x1, y1
        points = []
        for i in range(dx + 1):
            points.append((x, y))
            if error >= 0:
                if steep:
                    x += sx
                else:
                    y += sy
                error -= 1
            if steep:
                y += sy
            else:
                x += sx
            error += m
        return points

    def bresenham_int(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        if dx == 0 and dy == 0:
            return [(x1, y1)]
        steep = dy > dx
        if steep:
            dx, dy = dy, dx
        error = 2 * dy - dx
        x, y = x1, y1
        points = []
        for i in range(dx + 1):
            points.append((x, y))
            if error >= 0:
                if steep:
                    x += sx
                else:
                    y += sy
                error -= 2 * dx
            if steep:
                y += sy
            else:
                x += sx
            error += 2 * dy
        return points

    def get_rhombus_points(self):
        x1 = int(self.entry_x1.get())
        y1 = int(self.entry_y1.get())
        x2 = int(self.entry_x2.get())
        y2 = int(self.entry_y2.get())
        d = float(self.entry_d.get())
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        offset_x = -dy / length * d / 2
        offset_y = dx / length * d / 2
        return [(x1, y1),
                (round(cx + offset_x), round(cy + offset_y)),
                (x2, y2),
                (round(cx - offset_x), round(cy - offset_y))]

    def draw_rhombus(self):
        if self.base_img is None:
            return
        points = self.get_rhombus_points()
        lines = [(*points[i], *points[(i + 1) % 4]) for i in range(4)]
        self.draw_lines(lines, "Ромб")

    def draw_lines(self, lines, title):
        w, h = self.base_img.size

        all_pixels = []
        for method in self.methods:
            current = set()
            if method == "Встроенный метод":
                temp = Image.new("1", (w, h), 0)
                draw = ImageDraw.Draw(temp)
                for x1, y1, x2, y2 in lines:
                    draw.line([(x1, y1), (x2, y2)], fill=1, width=1)
                current = {(x, y) for y in range(h) for x in range(w)
                           if temp.getpixel((x, y))}
            else:
                for x1, y1, x2, y2 in lines:
                    if method == "ЦДА":
                        points = self.dda(x1, y1, x2, y2)
                    elif method == "Брезенхем (вещественный)":
                        points = self.bresenham_float(x1, y1, x2, y2)
                    else:
                        points = self.bresenham_int(x1, y1, x2, y2)
                    current.update((x, y) for x, y in points
                                   if 0 <= x < w and 0 <= y < h)
            all_pixels.append(current)

        self.img = self.base_img.copy()
        pixels = self.img.load()
        common = set.intersection(*all_pixels)
        union = set.union(*all_pixels)
        self.line_pixels = union
        for x, y in union:
            if (x, y) in common:
                pixels[x, y] = (65, 65, 65)
            else:
                indices = [i for i in range(4) if (x, y) in all_pixels[i]]
                pixels[x, y] = tuple(sum(self.colors[i][k] for i in indices) // len(indices)
                                     for k in range(3))

        counts = [len(all_pixels[i] ^ all_pixels[2]) for i in range(4)]
        self.info_label.config(text=f"{title} | совпало у всех: {len(common)} | "
                                    f"Различий: ЦДА - {counts[0]}, "
                                    f"вещественный - {counts[1]}, встроенный - {counts[3]}")
        self.update_display()

    def save_image(self):
        if self.img is None:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
        if file_path:
            self.img.save(file_path)

    def save_pbm(self):
        if self.img is None:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pbm", filetypes=[("PBM", "*.pbm")])
        if file_path:
            w, h = self.img.size
            pixels = self.img.load()
            with open(file_path, "w", encoding="ascii") as f:
                f.write(f"P1\n{w} {h}\n")
                for y in range(h):
                    row = []
                    for x in range(w):
                        r, g, b = pixels[x, y]
                        brightness = (r + g + b) // 3
                        pixel = 1 if (x, y) in self.line_pixels or brightness < 128 else 0
                        row.append(str(pixel))
                    f.write(" ".join(row) + "\n")

    def update_display(self):
        if self.img is None:
            return
        preview = self.img.copy()

        scale = min(7, 760 / preview.width, 590 / preview.height)
        if scale != 1:
            preview = preview.resize((max(1, int(preview.width * scale)),
                                      max(1, int(preview.height * scale))),
                                     Image.Resampling.NEAREST)
        self.tk_img = ImageTk.PhotoImage(preview)
        self.image_label.config(image=self.tk_img)


if __name__ == "__main__":
    root = tk.Tk()
    app = CGLab3(root)
    root.mainloop()
