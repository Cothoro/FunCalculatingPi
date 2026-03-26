import numpy as np
import pyray as rl

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


if __name__ == "__main__":
    rl.set_target_fps(60)
    rl.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Collision Simulation")

    # Load monospace font
    font = rl.load_font_ex("font/SpaceMono-Regular.ttf", 96, None, 0)
    rl.set_texture_filter(font.texture, rl.TEXTURE_FILTER_BILINEAR)

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        # Here you would implement the logic for simulating collisions and drawing them

        rl.end_drawing()

    rl.unload_font(font)
    rl.close_window()