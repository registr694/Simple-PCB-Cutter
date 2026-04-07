import tkinter as tk
from tkinter import filedialog, messagebox

def generate_gcode():
    try:
        # 1. Сбор данных
        x = float(entries["X (мм)"].get())
        y = float(entries["Y (мм)"].get())
        tool_d = float(entries["Фреза D (мм)"].get())
        depth = float(entries["Глубина (мм)"].get())
        step = float(entries["Шаг Z (мм)"].get())
        feed = float(entries["Подача"].get())
        tab_h = float(entries["Высота мостика"].get())
        use_tabs = var_tabs.get()

        offset = tool_d / 2
        gcode = ["(Happy Cutter v1.2 - Конструктор и Печкин)", "G21", "G90", "M3 S10000", "G0 Z5"]

        # Координаты сторон
        x_min, y_min = -offset, -offset
        x_max, y_max = x + offset, y + offset

        curr_z = 0
        while curr_z > -depth:
            curr_z -= step
            if curr_z < -depth: curr_z = -depth
            
            # Проверяем, последний ли это слой для мостиков
            is_last_layer = (curr_z <= -depth + 0.01) and use_tabs
            
            gcode.append(f"\n(Слой Z: {curr_z:.3f})")
            gcode.append(f"G1 Z{curr_z:.3f} F100")
            
            # Обход сторон
            sides = [
                (x_max, y_min), (x_max, y_max), (x_min, y_max), (x_min, y_min)
            ]
            
            for next_x, next_y in sides:
                if is_last_layer:
                    # Логика мостика: подпрыгиваем в середине пути
                    curr_x = float(gcode[-1].split('X')[1].split()[0]) if 'X' in gcode[-1] else x_min
                    curr_y = float(gcode[-1].split('Y')[1].split()[0]) if 'Y' in gcode[-1] else y_min
                    
                    mid_x = (curr_x + next_x) / 2
                    mid_y = (curr_y + next_y) / 2
                    
                    # Едем до начала мостика, прыгаем, едем дальше
                    gcode.append(f"G1 X{mid_x:.3f} Y{mid_y:.3f} Z{-depth + tab_h:.3f} F{feed} (Мостик)")
                    gcode.append(f"G1 X{next_x:.3f} Y{next_y:.3f} Z{curr_z:.3f}")
                else:
                    gcode.append(f"G1 X{next_x:.3f} Y{next_y:.3f} F{feed}")

        gcode.append("G0 Z5\nM5\nM30")
        text_preview.delete(1.0, tk.END)
        text_preview.insert(tk.END, "\n".join(gcode))
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Печкин, проверь цифры! ({e})")

# Интерфейс
root = tk.Tk(); root.title("Happy Cutter v1.2")
fields = [("X (мм)", "50"), ("Y (мм)", "50"), ("Фреза D (мм)", "2.0"), 
          ("Глубина (мм)", "1.6"), ("Шаг Z (мм)", "0.5"), ("Подача", "500"), ("Высота мостика", "0.8")]
entries = {}
for i, (txt, val) in enumerate(fields):
    tk.Label(root, text=txt).grid(row=i, column=0)
    en = tk.Entry(root); en.insert(0, val); en.grid(row=i, column=1)
    entries[txt] = en

var_tabs = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Включить мостики", variable=var_tabs).grid(row=7, columnspan=2)
tk.Button(root, text="СГЕНЕРИРОВАТЬ", command=generate_gcode).grid(row=8, columnspan=2)
text_preview = tk.Text(root, height=10, width=40); text_preview.grid(row=9, columnspan=2)
root.mainloop()
