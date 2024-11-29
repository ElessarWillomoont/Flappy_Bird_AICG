import pyray as pr

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


# set configurations to MSAA and full screen
pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT | pr.ConfigFlags.FLAG_FULLSCREEN_MODE)

# init the window, but will be changed latter
pr.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, 'flappy bird')

# load the resources


image_Background = pr.load_texture("source/Game_Objects/background-day.png")
image_Base = pr.load_texture("source/Game_Objects/base.png")
image_Pip = pr.load_texture("source/Game_Objects/pip-green.png")

bird_Fram_1 = pr.load_texture("source/Game_Objects/yellowbird-upflap.png")
bird_Fram_2 = pr.load_texture("source/Game_Objects/yellowbird-midflap.png")
bird_Fram_3 = pr.load_texture("source/Game_Objects/yellowbird-downflap.png")

image_Beging = pr.load_texture("source/UI/message.png")
image_Over = pr.load_texture("source/UI/gameover.png")
number_textures = []
for i in range(0,10):
    tex = pr.load_texture(f"source/UI/Numbers/{i}.png")
    number_textures.append(tex)

#define the zoom size of each elements

bird_size = 1.0
pip_size = 1.0

UI_size = 1.0
number_size = 1.0

background_size_w = 1.0
background_size_h = 1.0

base_size_w = 1.0
base_size_h = 1.0

# parameter to store the previous window size, check whether the window size is changed

window_size_pre_w = 1920
window_size_pre_h = 1080

# a function to renew the zoom scale for each elements when window size changed

def calculate_zoom_ratio (window_size_w, window_size_h):
    global bird_size, pip_size, UI_size, background_size_w, background_size_h, base_size_w, base_size_h, number_size
    global image_Background, image_Base, image_Pip, image_Beging, number_textures, bird_Fram_1 #assume that every bird and number texture are same sized
    
    over_all_size = min(window_size_h, window_size_w)

    bird_size = 0,1 * over_all_size / min(bird_Fram_1.height, bird_Fram_1.width)
    pip_size = 0.1 * window_size_w/ image_Pip.width

pr.set_target_fps(60)

while not pr.window_should_close():
    UpdatePhysics()  # Update physics system

    if IsKeyPressed(KEY_R):  # Reset physics system
        ResetPhysics()

        floor = CreatePhysicsBodyRectangle((SCREEN_WIDTH/2, SCREEN_HEIGHT), 500, 100, 10)
        floor.enabled = False

        circle = CreatePhysicsBodyCircle((SCREEN_WIDTH/2, SCREEN_HEIGHT/2), 45, 10)
        circle.enabled = False

    # Physics body creation inputs
    if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
        CreatePhysicsBodyPolygon(GetMousePosition(), GetRandomValue(20, 80), GetRandomValue(3, 8), 10)
    elif IsMouseButtonPressed(MOUSE_BUTTON_RIGHT):
        CreatePhysicsBodyCircle(GetMousePosition(), GetRandomValue(10, 45), 10)

    # Destroy falling physics bodies
    bodies_count = GetPhysicsBodiesCount()
    for i in reversed(range(bodies_count)):
        body = GetPhysicsBody(i)

        if body and body.position.y > SCREEN_HEIGHT * 2:
            DestroyPhysicsBody(body)
    # ----------------------------------------------------------------------

    # Draw
    # ----------------------------------------------------------------------
    BeginDrawing()

    ClearBackground(BLACK)
    DrawFPS(SCREEN_WIDTH - 90, SCREEN_HEIGHT - 30)

    # Draw created physics bodies
    bodies_count = GetPhysicsBodiesCount()
    for i in range(bodies_count):
        body = GetPhysicsBody(i)

        if body:
            vertex_count = GetPhysicsShapeVerticesCount(i)
            for j in range(vertex_count):
                # Get physics bodies shape vertices to draw lines
                # Note: GetPhysicsShapeVertex() already calculates rotation transformations
                vertexA = GetPhysicsShapeVertex(body, j)

                # Get next vertex or first to close the shape
                jj = (j + 1) if (j+1) < vertex_count else 0
                vertexB = GetPhysicsShapeVertex(body, jj)

                # Draw a line between two vertex positions
                DrawLineV(vertexA, vertexB, GREEN)

    pr.draw_text(b'Left mouse button to create a polygon', 10, 10, 10, WHITE)
    pr.draw_text(b'Right mouse button to create a circle', 10, 25, 10, WHITE)
    pr.draw_text("Press 'R' to reset example", 10, 40, 10, WHITE)

    pr.end_drawing()
    # ----------------------------------------------------------------------

ClosePhysics()
CloseWindow()