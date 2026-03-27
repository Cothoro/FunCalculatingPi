import numpy as np
import pyray as rl

TARGET_FPS = 60
TIME_PER_FRAME = 1.0 / TARGET_FPS

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# Simulation constants
DIGITS_TO_CALCULATE = 1

WALL_X = 50  # Visual wall position

SMALL_BLOCK_INITIAL_X = 400
SMALL_BLOCK_INITIAL_DX = 0

LARGE_BLOCK_INITIAL_X = 700
LARGE_BLOCK_INITIAL_DX = -125  # pixels per second

SMALL_BLOCK_MASS = 1
LARGE_BLOCK_MASS = 100 ** (DIGITS_TO_CALCULATE - 1)

SMALL_BLOCK_SIZE = 60
LARGE_BLOCK_SIZE = 100

FLOOR_Y = 610

# Global variables
total_collisions = 0
simulation_running = False
simulation_done = False
done_timer = 0.0    # Used to add a 3 second delay after the final collision occurs

class Block:
    def __init__(self, x, dx, mass, size):
        self.x = x
        self.dx = dx
        self.mass = mass
        self.size = size


def time_to_block_collision(small, large):
    """Time until the small block's right edge meets the large block's left edge."""
    gap = large.x - (small.x + small.size)
    relative_velocity = small.dx - large.dx
    if relative_velocity <= 0:
        return float('inf')
    t = gap / relative_velocity
    return t if t > 0 else float('inf')


def time_to_wall_collision(small):
    """Time until the small block's left edge hits the wall."""
    if small.dx >= 0:
        return float('inf')
    gap = small.x - WALL_X
    t = gap / (-small.dx)
    return t if t > 0 else float('inf')


def elastic_collision(b1, b2):
    """Apply elastic collision formulas to two blocks."""
    m1, m2 = b1.mass, b2.mass
    v1, v2 = b1.dx, b2.dx
    total = m1 + m2
    b1.dx = ((m1 - m2) * v1 + 2 * m2 * v2) / total
    b2.dx = ((m2 - m1) * v2 + 2 * m1 * v1) / total


def advance_frame(small, large, dt):
    """Advance the simulation by dt, processing all collisions within that time.
    Returns the number of collisions that occurred."""
    collisions = 0
    remaining = dt

    while remaining > 0:
        t_blocks = time_to_block_collision(small, large)
        t_wall = time_to_wall_collision(small)
        t_next = min(t_blocks, t_wall)

        if t_next > remaining:
            # No collision before frame ends so just advance positions
            small.x += small.dx * remaining
            large.x += large.dx * remaining
            remaining = 0
        else:
            # Advance to collision, process it, continue with remaining time
            small.x += small.dx * t_next
            large.x += large.dx * t_next
            remaining -= t_next

            if t_wall < t_blocks:
                small.x = WALL_X
                small.dx = -small.dx
            else:
                elastic_collision(small, large)

            collisions += 1

    return collisions


def is_simulation_done(small, large):
    """Check if no future collisions are possible."""
    return (time_to_block_collision(small, large) == float('inf') and
            time_to_wall_collision(small) == float('inf'))


def reset_simulation(small_block, large_block):
    """Reset blocks to initial conditions."""
    global total_collisions, simulation_running, simulation_done, done_timer
    small_block.x = SMALL_BLOCK_INITIAL_X
    small_block.dx = SMALL_BLOCK_INITIAL_DX
    small_block.mass = SMALL_BLOCK_MASS
    large_block.x = LARGE_BLOCK_INITIAL_X
    large_block.dx = LARGE_BLOCK_INITIAL_DX
    large_block.mass = LARGE_BLOCK_MASS
    total_collisions = 0
    simulation_running = False
    simulation_done = False
    done_timer = 0.0


def process_keybinds(small_block, large_block):
    """Process keybinds for controlling the simulation."""
    global DIGITS_TO_CALCULATE, LARGE_BLOCK_MASS, simulation_running

    if rl.is_key_pressed(rl.KEY_SPACE):
        simulation_running = not simulation_running
    if rl.is_key_pressed(rl.KEY_UP):
        DIGITS_TO_CALCULATE += 1
        LARGE_BLOCK_MASS = 100 ** (DIGITS_TO_CALCULATE - 1)
        reset_simulation(small_block, large_block)
    if rl.is_key_pressed(rl.KEY_DOWN):
        DIGITS_TO_CALCULATE = max(1, DIGITS_TO_CALCULATE - 1)
        LARGE_BLOCK_MASS = 100 ** (DIGITS_TO_CALCULATE - 1)
        reset_simulation(small_block, large_block)
    if rl.is_key_pressed(rl.KEY_R):
        reset_simulation(small_block, large_block)


def run_simulation(small_block, large_block):
    """Run one frame of the physics simulation."""
    global total_collisions, simulation_done, done_timer

    if simulation_running and not simulation_done:
        total_collisions += advance_frame(small_block, large_block, TIME_PER_FRAME)
        if is_simulation_done(small_block, large_block):
            simulation_done = True
            done_timer = 3.0

    # Keep blocks moving for 3 seconds after done
    if simulation_done and done_timer > 0:
        small_block.x += small_block.dx * TIME_PER_FRAME
        large_block.x += large_block.dx * TIME_PER_FRAME
        done_timer -= TIME_PER_FRAME


def draw_scene(small_block, large_block):
    """Draw the wall, floor, and blocks."""
    rl.draw_rectangle(0, FLOOR_Y - 300, WALL_X, 300, rl.DARKGRAY)
    rl.draw_line(0, FLOOR_Y, WINDOW_WIDTH, FLOOR_Y, rl.DARKGRAY)
    rl.draw_rectangle(int(small_block.x), FLOOR_Y - SMALL_BLOCK_SIZE,
                      SMALL_BLOCK_SIZE, SMALL_BLOCK_SIZE, rl.BLUE)
    rl.draw_rectangle(int(large_block.x), FLOOR_Y - LARGE_BLOCK_SIZE,
                      LARGE_BLOCK_SIZE, LARGE_BLOCK_SIZE, rl.RED)


def render_text_area(font):
    global total_collisions, simulation_done, simulation_running

    """Render the HUD text area with collision count, pi estimate, and controls."""
    if total_collisions > 0:
        pi_text = f"Estimated Pi: {total_collisions / (10 ** (DIGITS_TO_CALCULATE - 1)):.{DIGITS_TO_CALCULATE}f}"
    else:
        pi_text = "Estimated Pi: N/A"

    hud_y = FLOOR_Y + 10
    rl.draw_text_ex(font, f"Collisions: {total_collisions}",
                    (10, hud_y), 28, 1, rl.BLACK)
    rl.draw_text_ex(font, pi_text,
                    (10, hud_y + 32), 28, 1, rl.BLACK)
    rl.draw_text_ex(font, f"Mass ratio: {LARGE_BLOCK_MASS:.0e}:1",
                    (10, hud_y + 64), 28, 1, rl.BLACK)
    rl.draw_text_ex(font, f"Digits: {DIGITS_TO_CALCULATE}",
                    (10, hud_y + 96), 28, 1, rl.BLACK)

    if simulation_done:
        rl.draw_text_ex(font, "DONE", (10, hud_y + 128), 28, 1, rl.GREEN)
    elif not simulation_running:
        rl.draw_text_ex(font, "SPACE to start/pause | R to reset | UP/DOWN to change digits",
                        (10, hud_y + 128), 28, 1, rl.GRAY)


if __name__ == "__main__":
    rl.set_target_fps(TARGET_FPS)
    rl.init_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Collision Simulation")

    # Load monospace font
    font = rl.load_font_ex("font/SpaceMono-Regular.ttf", 96, None, 0)
    rl.set_texture_filter(font.texture, rl.TEXTURE_FILTER_BILINEAR)

    small_block = Block(SMALL_BLOCK_INITIAL_X, SMALL_BLOCK_INITIAL_DX, SMALL_BLOCK_MASS, SMALL_BLOCK_SIZE)
    large_block = Block(LARGE_BLOCK_INITIAL_X, LARGE_BLOCK_INITIAL_DX, LARGE_BLOCK_MASS, LARGE_BLOCK_SIZE)

    while not rl.window_should_close():
        process_keybinds(small_block, large_block)

        # Physics update
        run_simulation(small_block, large_block)

        # Drawing
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        draw_scene(small_block, large_block)
        render_text_area(font)
        rl.end_drawing()

    rl.unload_font(font)
    rl.close_window()