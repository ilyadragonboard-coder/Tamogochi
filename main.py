from tkinter import *
import random

IMG_SIZE = 320
CANVAS_W, CANVAS_H = IMG_SIZE, IMG_SIZE + 20
BG = "#dfe8d8"
IMAGE_FILES = {
    "happy": "1_kotik_radostny.png",
    "hungry": "6_kotik_golodny.png",
    "sick": "5_kotik_boleet.png",
    "dead": "7_kotik_umer.png",
    "eating": "2_kotik_est.png",
    "sleeping": "4_kotik_spit.png",
    "playing": "3_kotik_igraet.png",
}


class Pet:
    def __init__(self):
        self.fullness = 80
        self.happiness = 80
        self.energy = 80
        self.health = 100
        self.age_ticks = 0
        self.sleeping = False
        self.sick = False
        self.dead = False
        self.temp_state = None
        self.temp_ticks = 0

    def tick(self):
        if self.dead:
            return
        self.age_ticks += 1
        if self.sleeping:
            self.energy = min(100, self.energy + 6)
            self.fullness = max(0, self.fullness - 1)
            self.happiness = max(0, self.happiness - 1)
        else:
            self.fullness = max(0, self.fullness - 3)
            self.happiness = max(0, self.happiness - 2)
            self.energy = max(0, self.energy - 2)

        if not self.sick:
            risk = 0
            if self.fullness < 20: risk += 4
            if self.happiness < 20: risk += 4
            if self.energy < 15: risk += 3
            if risk and random.randint(1, 100) <= risk:
                self.sick = True

        if self.fullness == 0 or self.happiness == 0:
            self.health = max(0, self.health - 5)
        if self.sick:
            self.health = max(0, self.health - 3)
        if self.fullness > 60 and self.happiness > 60 and not self.sick:
            self.health = min(100, self.health + 2)
        if self.health <= 0:
            self.dead = True

        if self.dead or self.sleeping or self.sick:
            self.temp_state = None
            self.temp_ticks = 0
        elif self.temp_state:
            self.temp_ticks -= 1
            if self.temp_ticks <= 0:
                self.temp_state = None

    def feed(self):
        if self.dead or self.sleeping:
            return
        self.fullness = min(100, self.fullness + 30)
        self.happiness = min(100, self.happiness + 3)
        self.temp_state, self.temp_ticks = "eating", 3

    def play(self):
        if self.dead or self.sleeping or self.energy < 10:
            return
        self.happiness = min(100, self.happiness + 25)
        self.energy = max(0, self.energy - 12)
        self.fullness = max(0, self.fullness - 6)
        self.temp_state, self.temp_ticks = "playing", 3

    def toggle_sleep(self):
        if not self.dead:
            self.sleeping = not self.sleeping

    def heal(self):
        if not self.dead and self.sick:
            self.sick = False
            self.health = min(100, self.health + 10)

    def get_state(self):
        if self.dead:
            return "dead"
        if self.temp_state:
            return self.temp_state
        if self.sleeping:
            return "sleeping"
        if self.sick:
            return "sick"
        if self.fullness < 25:
            return "hungry"
        else:
            return "happy"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Kotik Tamagotchi")
        self.root.configure(bg=BG)
        self.pet = Pet()
        self.frame = 0
        self.image_cache = {}

        self.canvas = Canvas(root, width=CANVAS_W, height=CANVAS_H, bg=BG, highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.photo_item = self.canvas.create_image(CANVAS_W // 2, IMG_SIZE // 2, image=None)

        stats_frame = Frame(root, bg=BG)
        stats_frame.pack(pady=(0, 8))
        self.bars = {}
        for key, label, color in [
            ("fullness", "Еда", "#e0a83e"), ("happiness", "Настр", "#e85fa0"),
            ("energy", "Энерг", "#4faee0"), ("health", "Здор", "#e05f5f"),
        ]:
            row = Frame(stats_frame, bg=BG)
            row.pack(anchor="w")
            Label(row, text=label, width=6, anchor="w", bg=BG,
                  font=("Courier", 10, "bold")).pack(side="left")
            bc = Canvas(row, width=120, height=14, bg="#ffffff",
                        highlightthickness=1, highlightbackground="#333333")
            bc.pack(side="left", padx=4)
            self.bars[key] = (bc, color)

        self.status_label = Label(root, text="", bg=BG, font=("Courier", 11, "bold"))
        self.status_label.pack()

        btn_frame = Frame(root, bg=BG)
        btn_frame.pack(pady=10)
        self.feed_btn = Button(btn_frame, text="Кормить", width=10, command=self.feed)
        self.feed_btn.grid(row=0, column=0, padx=4)
        self.play_btn = Button(btn_frame, text="Играть", width=10, command=self.play)
        self.play_btn.grid(row=0, column=1, padx=4)
        self.sleep_btn = Button(btn_frame, text="Спать", width=10, command=self.sleep)
        self.sleep_btn.grid(row=0, column=2, padx=4)
        self.heal_btn = Button(btn_frame, text="Лечить", width=10, command=self.heal)
        self.heal_btn.grid(row=0, column=3, padx=4)

        self.logic_tick()
        self.anim_tick()

    def feed(self): self.pet.feed()
    def play(self): self.pet.play()
    def sleep(self): self.pet.toggle_sleep()
    def heal(self): self.pet.heal()

    def logic_tick(self):
        self.pet.tick()
        self.update_ui_text()
        self.root.after(3000, self.logic_tick)

    def anim_tick(self):
        self.frame += 1
        self.draw()
        self.root.after(120, self.anim_tick)

    def draw_bar(self, canvas, value, color):
        canvas.delete("all")
        segments = 12
        filled = round(value / 100 * segments)
        seg_w = 120 / segments
        for i in range(segments):
            x0 = i * seg_w
            fill = color if i < filled else "#eeeeee"
            canvas.create_rectangle(x0, 1, x0 + seg_w - 1, 13, fill=fill, outline="#cccccc")

    def update_ui_text(self):
        p = self.pet
        state = p.get_state()
        for key in ["fullness", "happiness", "energy", "health"]:
            canvas, color = self.bars[key]
            self.draw_bar(canvas, getattr(p, key), color)
        status_text = {
            "dead": "Питомец умер...",
            "sick": "Плохо себя чувствует! Нажми Лечить.",
            "hungry": "Мяу, он голоден!",
            "sleeping": "Спит...",
            "happy": "Мурррчит от счастья!",
            "eating": "Ням-ням!",
            "playing": "Гоняется за мышЪяком ой за мышкой!",
        }.get(state, "")
        self.status_label.config(text=f"{status_text}   (возраст: {p.age_ticks})")
        for b in (self.feed_btn, self.play_btn, self.sleep_btn, self.heal_btn):
            b.config(state="disabled" if state == "dead" else "normal")

    def get_photo(self, filename):
        if filename in self.image_cache:
            return self.image_cache[filename]
        try:
            photo = PhotoImage(file=filename)
            w, h = photo.width(), photo.height()
            if w > 0 and h > 0:
                factor_x = max(1, w // IMG_SIZE)
                factor_y = max(1, h // IMG_SIZE)
                if factor_x > 1 or factor_y > 1:
                    photo = photo.subsample(factor_x, factor_y)
        except TclError:
            photo = None
        self.image_cache[filename] = photo
        return photo

    def draw_placeholder(self, filename):
        self.canvas.itemconfig(self.photo_item, image="")
        self.canvas.create_rectangle(0, 0, CANVAS_W, IMG_SIZE, fill="#bbbbbb",outline="", tags="overlay")
        self.canvas.create_text(CANVAS_W // 2, IMG_SIZE // 2,
                                 text=f"нета файла:\n{filename}\n(нужон .png или .gif!!!!!)",
                                 fill="#333333", font=("Courier", 11, "bold"),
                                 justify="center", tags="overlay")

    def draw(self):
        p = self.pet
        state = p.get_state()
        f = self.frame

        self.canvas.delete("overlay")

        filename = IMAGE_FILES.get(state, "kotik.png")
        photo = self.get_photo(filename)
        if photo is not None:
            self.canvas.itemconfig(self.photo_item, image=photo)
            self.canvas.image = photo
        else:
            self.draw_placeholder(filename)

        if state == "sleeping":
            for i in range(3):
                phase = (f * 1.6 + i * 22) % 90
                t = phase / 90
                x = CANVAS_W - 60 + phase * 0.4
                y = 40 - phase * 0.5
                size = 10 + int(t * 8)
                self.canvas.create_text(x, y, text="Z", font=("Comic Sans MS", size, "bold"),
                                         fill="#5577aa", tags="overlay")
        elif state == "eating":
            bounce = abs((f % 10) - 5)
            self.canvas.create_text(CANVAS_W // 2, IMG_SIZE - 10 - bounce, text="ням-ням",
                                     font=("Courier", 12, "bold"), fill="#7a3d1a", tags="overlay")
        elif state in ("happy", "playing"):
            pulse = 12 + (f % 10)
            self.canvas.create_text(30, 20, text="♥", font=("Arial", pulse, "bold"),
                                     fill="#e85fa0", tags="overlay")
            self.canvas.create_text(CANVAS_W - 30, 20, text="♥", font=("Arial", pulse, "bold"),
                                     fill="#e85fa0", tags="overlay")
        elif state == "sick":
            self.canvas.create_text(CANVAS_W - 30, 20, text="+", font=("Arial", 20, "bold"),
                                     fill="#3388aa", tags="overlay")
        elif state == "dead":
            self.canvas.create_text(CANVAS_W // 2, 15, text="R.I.P.", font=("Courier", 16, "bold"),
                                     fill="#555555", tags="overlay")


def main():
    root = Tk()
    root.resizable(False, False)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()