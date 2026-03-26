import numpy as np
import pyray as rl

# Global constants and variables
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 1000

# Simulation parameters
SIMULATION_RUNNING = False
NEEDLE_LENGTH = 50  # Length of the needle in pixels
LINE_SPACING = 75   # Distance between the parallel lines in pixels
NEEDLES_PER_FRAME = 10  # Number of needles to drop per frame

total_needles = 0
crossing_needles = 0

def gen_random_needle():
    """Generate a random needle position and angle."""
    x = np.random.uniform(0, WINDOW_WIDTH)
    y = np.random.uniform(0, WINDOW_WIDTH)  # We only drop needles in the upper square area
    angle = np.random.uniform(0, np.pi)     # Angle in radians between 0 and π

    global total_needles
    total_needles += 1

    if is_needle_crossing_line(x, y, angle):
        global crossing_needles
        crossing_needles += 1

    draw_needle(x, y, angle)

def is_needle_crossing_line(x, y, angle):
    """Check if the needle crosses a line given its center position and angle."""
    # Calculate the distance from the center of the needle to the nearest line
    distance_to_nearest_line = min(y % LINE_SPACING, LINE_SPACING - (y % LINE_SPACING))
    
    # Calculate the vertical component of the needle's half-length
    half_length_vertical = (NEEDLE_LENGTH / 2) * np.sin(angle)

    # The needle crosses a line if the vertical component is greater than the distance to the nearest line
    return half_length_vertical >= distance_to_nearest_line

def draw_needle(x, y, angle):
    """Draw a needle at position (x, y) with a given angle."""
    # Calculate the endpoints of the needle based on the center position and angle
    half_length = NEEDLE_LENGTH / 2
    x1 = x + half_length * np.cos(angle)
    y1 = y + half_length * np.sin(angle)
    x2 = x - half_length * np.cos(angle)
    y2 = y - half_length * np.sin(angle)

    rl.draw_line(int(x1), int(y1), int(x2), int(y2), rl.BLACK)

def draw_parallel_lines():
    """Draw the parallel lines on the screen."""
    for y in range(0, WINDOW_HEIGHT, LINE_SPACING):
        rl.draw_line(0, y, WINDOW_WIDTH, y, rl.GRAY)

if __name__ == "__main__":
    rl.set_target_fps(60)
    rl.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Buffon's Needle Simulation")

    # This should just be a square so we have room for text at the bottom.
    simulation_texture = rl.load_render_texture(WINDOW_WIDTH, WINDOW_WIDTH)
    rl.begin_texture_mode(simulation_texture)
    rl.clear_background(rl.RAYWHITE)
    rl.end_texture_mode()

    # Load monospace font
    font = rl.load_font_ex("font/SpaceMono-Regular.ttf", 96, None, 0)
    rl.set_texture_filter(font.texture, rl.TEXTURE_FILTER_BILINEAR)

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)

        if rl.is_key_pressed(rl.KEY_SPACE):
            SIMULATION_RUNNING = not SIMULATION_RUNNING

        # Simulation rendering
        rl.begin_texture_mode(simulation_texture)
        draw_parallel_lines()

        if SIMULATION_RUNNING:
            for _ in range(NEEDLES_PER_FRAME):
                gen_random_needle()

        rl.end_texture_mode()

        rl.draw_texture_ex(simulation_texture.texture, (0, 0), 0, 1, rl.WHITE)

        # Total needles text
        total_text = f"Total Needles: {total_needles}"
        rl.draw_text_ex(font, total_text, (10, WINDOW_WIDTH + 10), 24, 1, rl.BLACK)
        # Crossing needles text
        crossing_text = f"Crossing Needles: {crossing_needles}"
        rl.draw_text_ex(font, crossing_text, (10, WINDOW_WIDTH + 40), 24, 1, rl.BLACK)
        # Pi estimation text
        if crossing_needles > 0:
            pi_estimation = (2 * NEEDLE_LENGTH * total_needles) / (LINE_SPACING * crossing_needles)
            pi_text = f"Estimated Pi: {pi_estimation:.6f}"
        else:
            pi_text = "Estimated Pi: N/A"
        rl.draw_text_ex(font, pi_text, (10, WINDOW_WIDTH + 70), 24, 1, rl.BLACK)

        rl.end_drawing()

    rl.unload_font(font)
    rl.close_window()