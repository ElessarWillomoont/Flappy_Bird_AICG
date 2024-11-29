import pyray as pr
import random

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 1080

PIP_POS_UP = 0
PIP_POS_DOWN = 1

SPEED_X = 5 #speed of pip move
GRAVITY = 5 #speed of bird decreace
FORCE = 3 #speed of bird decreace

#for game status

RUNING = 0
WAITING = 1
FAILED = 2

BIRD_SIZE = 30



# set configurations to MSAA and full screen
# pr.set_config_flags(pr.ConfigFlags.FLAG_MSAA_4X_HINT | pr.ConfigFlags.FLAG_FULLSCREEN_MODE)

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

# print(f"size is :{number_textures[0].width}")

#define the zoom size of each elements

bird_size = 2.5 
pip_size = 1.0

UI_size = 2.5
number_size = 1.0

# background_size_w = 1.0
# background_size_h = 1.0

# base_size_w = 1.0
# base_size_h = 1.0

background_size = 2.7

base_size = 2.5

#define the class of bird and pip
#bird class
class MyBird:
    def __init__(self, positionY):
        self.positionY = positionY

#pip class
class MyPip:
    def __init__(self, PositionX, HeadPositionY, Direction):
        self.HeadPositionY = HeadPositionY
        self.PositionX = PositionX
        self.Direction = Direction

def hit_the_pip (bird_obj, pip_obj):
    global game_status
    if pip_obj.Direction == PIP_POS_UP: #upper pip
        if bird_obj.positionY < pip_obj.HeadPositionY:
            game_status = FAILED
    elif pip_obj.Direction == PIP_POS_DOWN: #lower pip
        if bird_obj.positionY > pip_obj.HeadPositionY:
            game_status = FAILED

def draw_the_bird (PositionY, FrameControl):
    global bird_Fram_1, bird_Fram_2, bird_Fram_3, bird_size
    target_point = pr.Vector2(int(SCREEN_WIDTH /2 - bird_Fram_1.width / 2 * bird_size), int(PositionY - (bird_Fram_1.height/2 * bird_size)))
    if int(FrameControl/ 20) == 0:
        pr.draw_texture_ex(bird_Fram_1, target_point, 0.0,  bird_size, pr.WHITE)
    elif int(FrameControl/ 20) == 1:
        pr.draw_texture_ex(bird_Fram_2, target_point, 0.0,  bird_size, pr.WHITE)
    elif int(FrameControl/ 20) == 2:
        pr.draw_texture_ex(bird_Fram_3, target_point, 0.0,  bird_size, pr.WHITE)

def draw_the_pip (pip :MyPip):
    global image_Pip, pip_size
    if pip.Direction == PIP_POS_UP:
        target_point = pr.Vector2(int(pip.PositionX - image_Pip.width /2 * pip_size),int(image_Pip.height * pip_size - pip.HeadPositionY))
        pr.draw_texture_ex(image_Pip, target_point, 180.0, pip_size, pr.WHITE)
    if pip.Direction == PIP_POS_DOWN:
        target_point = pr.Vector2(int(pip.PositionX - image_Pip.width /2 * pip_size),int(SCREEN_HEIGHT - image_Pip.height * pip_size + pip.HeadPositionY))
        pr.draw_texture_ex(image_Pip, target_point, 0, pip_size, pr.WHITE)

def make_new_pip (pips: list):
    print("entered here ")
    distance_closest = SCREEN_WIDTH
    for i in pips:
        if i.PositionX < distance_closest:
            distance_closest = i.PositionX
    if len(pips) == 0 or distance_closest >= int(SCREEN_WIDTH/5):
        pos = random.randint(int(SCREEN_HEIGHT * 0.2), int(SCREEN_HEIGHT * 0.8))
        gap = random.randint(BIRD_SIZE, int(SCREEN_HEIGHT * 0.5))
        new_pip_upper = MyPip(SCREEN_WIDTH, int(pos - (gap / 2)), PIP_POS_UP)
        new_pip_lower = MyPip(SCREEN_WIDTH, int(pos + (gap / 2)), PIP_POS_DOWN)
        pips.append(new_pip_upper)
        pips.append(new_pip_lower)

def renew_score_digit (score):
    global score_digit
    score_digit = []
    score_str = str(score)
    for i in score_str:
        score_digit.append(int(i))
    while len(score_digit) < 4:
        score_digit.insert(0, 0)

def draw_the_UI (texture, point_x, point_y, multiper):
    point = pr.Vector2(point_x, point_y)
    pr.draw_texture_ex(texture, point, 0, multiper, pr.WHITE)

def fb_initialization ():
    global game_status, pips, temp_to_delete, score, score_real, score_prev, score_digit, fram_control, bird_play
    game_status = WAITING
    pips = []
    temp_to_delete = []

    score = 0 #current score
    score_real = 0 #there are two pips...
    score_prev = 0 #score before
    score_digit = []#digit of score

    fram_control = 0 #to control the bird animation

    bird_play.positionY = int(SCREEN_HEIGHT / 2)

def draw_the_score ():
    global SCREEN_HEIGHT, SCREEN_WIDTH, score_digit, number_textures, number_size
    gap = int(number_textures[0].width * number_size / 5 )
    length_of_digits = int(number_textures[0].width * number_size * 4 + gap * 3)
    start_point_x = int(SCREEN_WIDTH / 2 - length_of_digits / 2)
    start_point_y = int(SCREEN_HEIGHT / 10)
    for index, i in enumerate(score_digit):
        draw_the_UI(number_textures[i], int(start_point_x + index * (number_textures[0].width * number_size + gap)), start_point_y, number_size)

def draw_the_background():
    global SCREEN_HEIGHT, SCREEN_WIDTH,  image_Background, background_size
    draw_the_UI(image_Background, int(SCREEN_WIDTH/2 - image_Background.width * background_size / 2), int(SCREEN_HEIGHT/2 - image_Background.height * background_size / 2) ,background_size)
    # draw the background in the center
def draw_the_ground():
    global SCREEN_HEIGHT, SCREEN_WIDTH,  image_Base, base_size
    draw_the_UI(image_Base, int(SCREEN_WIDTH/2 - image_Base.width * base_size / 2), int(SCREEN_HEIGHT * 0.8) ,base_size)

bird_play = MyBird(int(SCREEN_HEIGHT/ 2))

game_status = WAITING
pips = []
temp_to_delete = []

score = 0 #current score
score_real = 0 #there are two pips...
score_prev = 0 #score before
score_digit = []#digit of score

fram_control = 0 #to control the bird animation

pr.set_target_fps(60)

while not pr.window_should_close():
    pr.begin_drawing()
    pr.clear_background(pr.BLACK)
    draw_the_background()
    if game_status == WAITING:
        draw_the_UI(image_Beging, int(SCREEN_WIDTH/2 - image_Beging.width * UI_size / 2), int(SCREEN_HEIGHT/2 - image_Beging.height * UI_size / 2), UI_size)
        if pr.is_key_pressed(pr.KEY_SPACE):
            fb_initialization ()
            game_status = RUNING
    if game_status == RUNING:
        #Game Logic
        if len(pips) <= 8:
            make_new_pip (pips)
        if pr.is_key_down(pr.KEY_SPACE): #don't know whether the key value is good
            bird_play.positionY = bird_play.positionY - FORCE
        else:
            bird_play.positionY = bird_play.positionY + GRAVITY
        draw_the_bird(bird_play.positionY, fram_control)
        for index, pip_i in enumerate(pips):
            pip_i.PositionX = pip_i.PositionX - SPEED_X
            draw_the_pip (pip_i)
            if pip_i.PositionX == int( SCREEN_WIDTH / 2): #pip overlap with bird
                hit_the_pip(bird_play, pip_i)
                score_real = score_real + 1
            if pip_i.PositionX <= 0:
                temp_to_delete.append(index)
        if (bird_play.positionY >= int(SCREEN_HEIGHT * 0.8)) or (bird_play.positionY <= 0):
            game_status = FAILED
        for i in temp_to_delete:
            del pips[i]
        temp_to_delete = []
        score = int(score_real /2)
        if score != score_prev:
            renew_score_digit(score)
            score_prev = score
        if fram_control == 60:
            fram_control = 0
        else:
            fram_control = fram_control + 1
        draw_the_score()
    if game_status == FAILED:
        draw_the_score()
        draw_the_UI(image_Over, int(SCREEN_WIDTH/2 - image_Over.width * UI_size / 2), int(SCREEN_HEIGHT/2 - image_Over.height * UI_size / 2), UI_size)
        if pr.is_key_pressed(pr.KEY_SPACE):
            fb_initialization()
    draw_the_ground()
    pr.end_drawing()




#     UpdatePhysics()  # Update physics system

#     if IsKeyPressed(KEY_R):  # Reset physics system
#         ResetPhysics()

#         floor = CreatePhysicsBodyRectangle((SCREEN_WIDTH/2, SCREEN_HEIGHT), 500, 100, 10)
#         floor.enabled = False

#         circle = CreatePhysicsBodyCircle((SCREEN_WIDTH/2, SCREEN_HEIGHT/2), 45, 10)
#         circle.enabled = False

#     # Physics body creation inputs
#     if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
#         CreatePhysicsBodyPolygon(GetMousePosition(), GetRandomValue(20, 80), GetRandomValue(3, 8), 10)
#     elif IsMouseButtonPressed(MOUSE_BUTTON_RIGHT):
#         CreatePhysicsBodyCircle(GetMousePosition(), GetRandomValue(10, 45), 10)

#     # Destroy falling physics bodies
#     bodies_count = GetPhysicsBodiesCount()
#     for i in reversed(range(bodies_count)):
#         body = GetPhysicsBody(i)

#         if body and body.position.y > SCREEN_HEIGHT * 2:
#             DestroyPhysicsBody(body)
#     # ----------------------------------------------------------------------

#     # Draw
#     # ----------------------------------------------------------------------
#     BeginDrawing()

#     ClearBackground(BLACK)
#     DrawFPS(SCREEN_WIDTH - 90, SCREEN_HEIGHT - 30)

#     # Draw created physics bodies
#     bodies_count = GetPhysicsBodiesCount()
#     for i in range(bodies_count):
#         body = GetPhysicsBody(i)

#         if body:
#             vertex_count = GetPhysicsShapeVerticesCount(i)
#             for j in range(vertex_count):
#                 # Get physics bodies shape vertices to draw lines
#                 # Note: GetPhysicsShapeVertex() already calculates rotation transformations
#                 vertexA = GetPhysicsShapeVertex(body, j)

#                 # Get next vertex or first to close the shape
#                 jj = (j + 1) if (j+1) < vertex_count else 0
#                 vertexB = GetPhysicsShapeVertex(body, jj)

#                 # Draw a line between two vertex positions
#                 DrawLineV(vertexA, vertexB, GREEN)

#     pr.draw_text(b'Left mouse button to create a polygon', 10, 10, 10, WHITE)
#     pr.draw_text(b'Right mouse button to create a circle', 10, 25, 10, WHITE)
#     pr.draw_text("Press 'R' to reset example", 10, 40, 10, WHITE)

#     pr.end_drawing()
#     # ----------------------------------------------------------------------

# ClosePhysics()
# CloseWindow()

pr.unload_texture(image_Background)
pr.unload_texture(image_Base)
pr.unload_texture(image_Pip)

pr.unload_texture(bird_Fram_1)
pr.unload_texture(bird_Fram_2)
pr.unload_texture(bird_Fram_3)

pr.unload_texture(image_Beging)
pr.unload_texture(image_Over)