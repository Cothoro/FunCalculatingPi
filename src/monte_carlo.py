import numpy as np
import pyray as rl

# Global constants and variables
RENDER_SIZE = 900
TEXT_AREA_SIZE = 100

SIMULATION_RUNNING = False
TOTAL_POINTS = 500_000 
POINTS_PER_FRAME = 500
num_points = 0          # Number of points generated so far
points_in_circle = 0 

STATE_RANDOM = 0        # Will generate points completely randomly
STATE_UNIFORM = 1       # Will generate points in a uniform grid pattern
current_state = STATE_RANDOM

# Step size to fill a -1 to 1 square with TOTAL_POINTS points
# in a uniform grid
DX = 2 / (TOTAL_POINTS ** 0.5)
DY = 2 / (TOTAL_POINTS ** 0.5) 


def is_point_in_circle(x, y):
    """Check if the point (x, y) is inside the unit circle."""
    return x**2 + y**2 <= 1


def gen_random_point():
    """Generate a random point (x, y) in the range [-1, 1]."""
    global num_points

    x = np.random.uniform(-1, 1)
    y = np.random.uniform(-1, 1)

    if is_point_in_circle(x, y):
        global points_in_circle
        points_in_circle += 1
    
    num_points += 1

    color = rl.BLACK if is_point_in_circle(x, y) else rl.RED
    plot_point(x, y, color)


def gen_uniform_point():
    """Generate a point (x, y) in a uniform grid pattern."""
    global num_points

    # Calculate the x and y coordinates based on the current number
    # of points drawn
    number_of_columns = int(2 / DX)
    row = num_points // number_of_columns
    col = num_points % number_of_columns

    # subtract 1 to map [0, 2] to [-1, 1]
    # then add half a step to center the point in its column/row
    x = -1 + (col * DX + DX / 2)

    # We take away from 1 instead here because in graphics libraries
    # the y-axis is flipped
    y = 1 - (row * DY + DY / 2)

    if is_point_in_circle(x, y):
        global points_in_circle
        points_in_circle += 1
    
    num_points += 1

    color = rl.BLACK if is_point_in_circle(x, y) else rl.RED
    plot_point(x, y, color)


def estimate_pi():
    """Estimate the value of pi using the ratio of points inside the circle."""
    if num_points == 0:
        return 0
    return (points_in_circle / num_points) * 4


def plot_point(x, y, color):
    """Map the point (x, y) to the window coordinates and draw it."""
    screen_x = int(x * (RENDER_SIZE / 2) + (RENDER_SIZE / 2))
    screen_y = int(y * (RENDER_SIZE / 2) + (RENDER_SIZE / 2))
    rl.draw_circle(screen_x, screen_y, 2, color)


def reset_simulation():
    """Reset the simulation to its initial state."""
    global num_points, points_in_circle
    num_points = 0
    points_in_circle = 0

    rl.begin_texture_mode(render_texture)
    rl.clear_background(rl.RAYWHITE)
    rl.end_texture_mode()


def process_keybinds():
    """Process keybinds for controlling the simulation."""
    global SIMULATION_RUNNING, current_state

    if rl.is_key_pressed(rl.KEY_SPACE):
        SIMULATION_RUNNING = not SIMULATION_RUNNING
    if rl.is_key_pressed(rl.KEY_M):
        if current_state == STATE_RANDOM:
            current_state = STATE_UNIFORM
        else:
            current_state = STATE_RANDOM

        SIMULATION_RUNNING = False
        reset_simulation()
    if rl.is_key_pressed(rl.KEY_R):
        SIMULATION_RUNNING = False
        reset_simulation()


def run_simulation(render_texture):
    """Run the simulation by generating points and drawing them on the render texture."""
    global num_points

    rl.begin_texture_mode(render_texture)
    for _ in range(POINTS_PER_FRAME):
        if current_state == STATE_RANDOM:
            gen_random_point()
        elif current_state == STATE_UNIFORM:
            gen_uniform_point()
    rl.end_texture_mode()


def render_text_area(font):
    """Render the text area with the current estimation of pi and the mode."""
    pi_text = estimate_pi()
    text = f"Estimated Pi: {pi_text:.6f} (Points: {num_points})"
    rl.draw_text_ex(font, text, (10, RENDER_SIZE + 10), 32, 0, rl.BLACK)
    mode_text = "Mode: Random" if current_state == STATE_RANDOM else "Mode: Uniform"
    rl.draw_text_ex(font, mode_text, (10, RENDER_SIZE + 50), 32, 0, rl.BLACK)


if __name__ =="__main__":

    rl.set_target_fps(60)
    rl.init_window(RENDER_SIZE, RENDER_SIZE + TEXT_AREA_SIZE, "Monte Carlo Pi Estimation")

    # Load monospace font
    font = rl.load_font_ex("font/SpaceMono-Regular.ttf", 96, None, 0)
    rl.set_texture_filter(font.texture, rl.TEXTURE_FILTER_BILINEAR)

    # Load the render texture where we will draw the points
    render_texture = rl.load_render_texture(RENDER_SIZE, RENDER_SIZE)
    rl.begin_texture_mode(render_texture)
    rl.clear_background(rl.RAYWHITE)
    rl.end_texture_mode()

    while not rl.window_should_close():
        process_keybinds()
        
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        
        # Run the simulation
        if SIMULATION_RUNNING and num_points < TOTAL_POINTS:
            run_simulation(render_texture)

        # Draw render texture of the simulation
        rl.draw_texture(render_texture.texture, 0, 0, rl.WHITE)

        # Render the text area
        render_text_area(font)
        rl.end_drawing()

    rl.unload_font(font)
    rl.close_window()