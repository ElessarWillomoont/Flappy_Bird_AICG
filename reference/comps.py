from __future__ import annotations

from assets import Assets
from pathlib import Path

import assets
import pyray as ray
import random


TITLE = "Flappy Bird"
WIDTH = 288
HEIGHT = 512
FPS = 60

MUL = 200
JUMP = MUL
GRAVITY = 2 * MUL
BG = 20
GR = 80


class Component:
    def __init__(self, entity: Entity | None = None) -> None:
        self.entity = entity

    def update(self, dt: float) -> None: ...
    def draw(self) -> None: ...


class Entity:
    counter = 0

    def __init__(self) -> None:
        self.comps: dict[str, Component] = {}
        self.id = Entity.counter
        Entity.counter += 1

    def remove_component(self, name: str) -> None: del self.comps[name]
    def add_component(self, name: str, comp: Component) -> Component:
        comp.entity = self
        self.comps[name] = comp
        return self.comps[name]

    def update(self, dt: float) -> None: [comp.update(dt) for comp in self.comps.values()]
    def draw(self) -> None: [comp.draw() for comp in self.comps.values()]


class Scene:
    def __init__(self, *entities: Entity) -> None:
        self.ents = entities

    def update(self, dt: float) -> None: [ent.update(dt) for ent in self.ents]
    def draw(self) -> None: [ent.draw() for ent in self.ents]


class Sprite(Component):
    def __init__(self, tex: ray.Texture, anchor: ray.Vector2 | None = None, tint: ray.Color = ray.WHITE) -> None:
        super().__init__()
        self.tex = tex
        self.anchor = anchor if anchor is None else ray.Vector2(0, 0)
        self.width = tex.width
        self.height = tex.height
        self.tint = tint


class Transform(Component):
    def __init__(self, pos: ray.Vector2 | None = None) -> None:
        super().__init__()
        self.pos = ray.Vector2(0, 0) if pos is None else pos


class Renderer(Component):
    def __init__(self, transform: Transform, sprite: Sprite) -> None:
        super().__init__()
        self.transform = transform
        self.sprite = sprite
        self.debug = False

    def update(self, dt: float) -> None:
        if ray.is_key_pressed(ray.KEY_D):
            self.debug = not self.debug

    def draw(self) -> None:
        pos = ray.vector2_add(self.transform.pos, self.sprite.anchor)
        ray.draw_texture(self.sprite.tex, int(pos.x), int(pos.y), self.sprite.tint)
        if self.debug:
            rec = ray.Rectangle(pos.x, pos.y, self.sprite.width, self.sprite.height)
            ray.draw_rectangle_lines_ex(rec, 2, ray.GREEN)
            ray.draw_rectangle(int(self.transform.pos.x - 8), int(self.transform.pos.y - 1), 16, 2, ray.BLUE)
            ray.draw_rectangle(int(self.transform.pos.x - 1), int(self.transform.pos.y - 8), 2, 16, ray.BLUE)


class HorizontalRepeat(Component):
    def __init__(self, ents: tuple[Entity, Entity]) -> None:
        super().__init__()
        self.ents = ents

        self.tr_0, self.tr_1 = self.ents[0].comps["tr"], self.ents[1].comps["tr"]
        self.sp_0, self.sp_1 = self.ents[0].comps["sp"], self.ents[1].comps["sp"]

        self.tr_1.pos.x += self.sp_0.width

    def update(self, dt: float) -> None:
        if self.tr_0.pos.x <= -self.sp_0.width: self.tr_0.pos.x = self.tr_1.pos.x + self.sp_1.width
        if self.tr_1.pos.x <= -self.sp_1.width: self.tr_1.pos.x = self.tr_0.pos.x + self.sp_0.width


class RigidBody(Component):
    def __init__(self, transform: Transform, vel: ray.Vector2 | None = None, kinetic: bool = False, impulse: ray.Vector2 | None = None) -> None:
        super().__init__()
        self.transform = transform
        self.vel = ray.Vector2(0, 0) if vel is None else vel
        self.kinetic = kinetic
        self.impulse = impulse

    def update(self, dt: float) -> None:
        if self.kinetic: self.vel.y += GRAVITY * dt
        if self.impulse is not None:
            self.vel = self.impulse
            self.impulse = None
        self.transform.pos = ray.vector2_add(self.transform.pos, ray.vector2_scale(self.vel, dt))


class Pipe(Component):
    def __init__(self, pipes: tuple[Entity, Entity], ground_h: float, gap: float, transform: Transform) -> None:
        super().__init__()
        self.pipes = pipes
        self.ground_h = ground_h
        self.gap = gap
        self.transform = transform

        self.pipe_b_tr, self.pipe_t_tr = self.pipes[0].comps["tr"], self.pipes[1].comps["tr"]
        self.pipe_sp = self.pipes[0].comps["sp"]

    def update(self, dt: float) -> None:
        if self.transform.pos.x <= -0.5 * self.pipe_sp.width:
            rand = 0.25 + 0.5 * random.random()
            self.transform.pos.x = WIDTH + 0.5 * self.pipe_sp.width
            self.transform.pos.y = (1 - rand) * (HEIGHT - self.ground_h)
            self.entity.comps["pt"].passed = False

        self.pipe_b_tr.pos.x = self.transform.pos.x
        self.pipe_t_tr.pos.x = self.transform.pos.x
        self.pipe_b_tr.pos.y = self.transform.pos.y + 0.5 * self.gap
        self.pipe_t_tr.pos.y = self.transform.pos.y - 0.5 * self.gap


class Points(Component):
    def __init__(self, pi_tr: Pipe, pi_w: int, fl: Entity) -> None:
        super().__init__()
        self.pi_tr = pi_tr
        self.pi_w = pi_w
        self.fl = fl

        self.passed = False
        self.points = 0

        self.fl_tr = fl.comps["tr"]
        self.fl_sp = fl.comps["sp"]

    def update(self, dt: float) -> None:
        if not self.passed and self.fl_tr.pos.x + 0.5 * self.fl_sp.width >= self.pi_tr.pos.x + 0.5 * self.pi_w:
            self.points += 1
            self.passed = True
            ray.play_sound(Assets.sounds.swoosh)
            ray.play_sound(Assets.sounds.point)


class Controller(Component):
    def __init__(self, tr: Transform, rb: RigidBody, sp: Sprite, pi: Pipe, gr_tr: Transform, go_sp: Sprite) -> None:
        super().__init__()
        self.tr = tr
        self.rb = rb
        self.sp = sp
        self.pi = pi
        self.gr_tr = gr_tr
        self.go_sp = go_sp

        self.dead = False
        self.dead_since = 0

    def update(self, dt: float) -> None:
        if self.dead:
            self.dead_since += dt
            return

        pi_h_hit = self.tr.pos.y + 0.4 * self.sp.width >= self.pi.pipe_b_tr.pos.y or self.tr.pos.y - 0.4 * self.sp.width <= self.pi.pipe_t_tr.pos.y
        pi_w_hit = self.tr.pos.x - 0.4 * self.sp.width <= self.pi.pipe_b_tr.pos.x + 0.5 * self.pi.pipe_sp.width and self.tr.pos.x + 0.4 * self.sp.width >= self.pi.pipe_b_tr.pos.x - 0.5 * self.pi.pipe_sp.width
        gr_h_hit = self.tr.pos.y + 0.4 * self.sp.width >= self.gr_tr.pos.y

        self.dead = gr_h_hit or (pi_h_hit and pi_w_hit)
        if self.dead:
            self.sp.tex = Assets.objects.yellowbird_downflap
            self.sp.tint = ray.RED
            self.rb.vel = ray.Vector2(-GR, 0)
            self.rb.kinetic = False
            self.go_sp.tint = ray.WHITE
            ray.play_sound(Assets.sounds.die)

        jump = ray.is_key_pressed(ray.KEY_SPACE)
        if jump:
            self.rb.impulse = ray.Vector2(0, -JUMP)
            ray.play_sound(Assets.sounds.wing)

        if self.rb.vel.y < 0: self.sp.tex = Assets.objects.yellowbird_downflap
        if self.rb.vel.y > 0: self.sp.tex = Assets.objects.yellowbird_upflap
        if self.rb.vel.y == 0 or jump: self.sp.tex = Assets.objects.yellowbird_midflap


class SceneGame(Scene):
    def __init__(self):
        super().__init__()

        bg = Entity()
        bg_tiles = []
        for i in range(2):
            tile = Entity()
            sp = tile.add_component("sp", Sprite(Assets.objects.background_day))
            tr = tile.add_component("tr", Transform())
            tile.add_component("re", Renderer(tr, sp))
            tile.add_component("rb", RigidBody(tr, ray.Vector2(-BG, 0)))
            bg_tiles.append(tile)
        bg.add_component("hr", HorizontalRepeat(tuple(bg_tiles)))

        gr = Entity()
        gr_tiles = []
        for i in range(2):
            tile = Entity()
            sp = tile.add_component("sp", Sprite(Assets.objects.base))
            tr = tile.add_component("tr", Transform(ray.Vector2(0, HEIGHT - sp.height)))
            tile.add_component("re", Renderer(tr, sp))
            tile.add_component("rb", RigidBody(tr, ray.Vector2(-GR, 0)))
            gr_tiles.append(tile)
        gr.add_component("hr", HorizontalRepeat(tuple(gr_tiles)))

        fl = Entity()
        tex = Assets.objects.yellowbird_midflap
        sp = fl.add_component("sp", Sprite(tex, ray.Vector2(-0.5 * tex.width, -0.5 * tex.height)))
        tr = fl.add_component("tr", Transform(ray.Vector2(0.5 * WIDTH, (1 - 0.5) * (HEIGHT - gr_tiles[0].comps["sp"].height) + 0.5 * sp.height)))
        rb = fl.add_component("rb", RigidBody(tr, kinetic=True, impulse=ray.Vector2(0, -JUMP)))
        fl.add_component("re", Renderer(tr, sp))

        pi_b = Entity()
        tex = Assets.objects.pipe_b_green
        sp = pi_b.add_component("sp", Sprite(tex, ray.Vector2(-0.5 * tex.width, 0)))
        tr = pi_b.add_component("tr", Transform())
        pi_b.add_component("re", Renderer(tr, sp))

        pi_t = Entity()
        tex = Assets.objects.pipe_t_green
        sp = pi_t.add_component("sp", Sprite(tex, ray.Vector2(-0.5 * tex.width, -tex.height)))
        tr = pi_t.add_component("tr", Transform())
        pi_t.add_component("re", Renderer(tr, sp))

        pi = Entity()
        tr = pi.add_component("tr", Transform(ray.Vector2(WIDTH + 0.5 * Assets.objects.pipe_b_green.width, (1 - 0.5) * (HEIGHT - gr_tiles[0].comps["sp"].height))))
        pi.add_component("rb", RigidBody(tr, ray.Vector2(-GR, 0)))
        pi.add_component("pi", Pipe((pi_b, pi_t), gr_tiles[0].comps["sp"].height, 4 * fl.comps["sp"].height, tr))
        pi.add_component("pt", Points(tr, pi_b.comps["sp"].width, fl))

        go = Entity()
        tex = Assets.ui.gameover
        sp = go.add_component("sp", Sprite(tex, ray.Vector2(-0.5 * tex.width, -0.5 * tex.height), ray.Color(0, 0, 0, 0)))
        tr = go.add_component("tr", Transform(ray.Vector2(0.5 * WIDTH, (1 - 0.5) * (HEIGHT - gr_tiles[0].comps["sp"].height))))
        go.add_component("re", Renderer(tr, sp))

        fl.add_component("co", Controller(
            fl.comps["tr"],
            fl.comps["rb"],
            fl.comps["sp"],
            pi.comps["pi"],
            gr_tiles[0].comps["tr"],
            go.comps["sp"],
        ))

        super().__init__(*bg_tiles, bg, go, pi, pi_b, pi_t, *gr_tiles, gr, fl)


class SceneMenu(Scene):
    def __init__(self):
        super().__init__()

        bg = Entity()
        sp = bg.add_component("sp", Sprite(Assets.objects.background_day))
        tr = bg.add_component("tr", Transform())
        bg.add_component("re", Renderer(tr, sp))

        gr = Entity()
        sp = gr.add_component("sp", Sprite(Assets.objects.base))
        tr = gr.add_component("tr", Transform(ray.Vector2(0, HEIGHT - sp.height)))
        gr.add_component("re", Renderer(tr, sp))

        ms = Entity()
        tex = Assets.ui.message
        sp = ms.add_component("sp", Sprite(tex, ray.Vector2(-0.5 * tex.width, -0.5 * tex.height)))
        tr = ms.add_component("tr", Transform(ray.Vector2(0.5 * WIDTH, (1 - 0.5) * (HEIGHT - gr.comps["sp"].height))))
        ms.add_component("re", Renderer(tr, sp))

        super().__init__(bg, gr, ms)


class SceneManager:
    def __init__(self) -> None:
        super().__init__()
        self.scene = SceneMenu()
        self.playing = False
        self.debug = False
        self.co: Controller | None = None

    def update(self, dt: float) -> None:
        self.scene.update(dt)
        if ray.is_key_pressed(ray.KEY_D):
            self.debug = not self.debug

        if not self.playing and ray.is_key_pressed(ray.KEY_SPACE):
            self.scene = SceneGame()
            self.playing = True
            self.co = next(filter(lambda co: co, (e.comps.get("co", None) for e in self.scene.ents)))

        if self.playing and self.co:
            if self.co.dead_since > 5:
                self.co = None
                self.playing = False
                self.scene = SceneMenu()

    def draw(self) -> None:
        self.scene.draw()
        if self.debug:
            ray.draw_text(f"MS: {int(ray.get_frame_time() * 1_000)}", 20, 20, 20, ray.WHITE)
            ray.draw_text(f"FPS: {ray.get_fps()}", 20, 45, 20, ray.WHITE)


# def obj_points(points: int) -> list[Object]:
#     objs = []
#     sprites = [n_sprites[int(c)] for c in f"{points}"]
#     offset = 0.5 * WIDTH - 0.5 * sum(map(lambda s: s.width, sprites))
#     for i, sprite in enumerate(sprites):
#         transform = Transform(ray.Vector2(offset + i * sprite.width, 0.1 * HEIGHT))
#         objs.append(Object(sprite, transform))
#     return objs

ray.set_target_fps(FPS)
ray.init_window(WIDTH, HEIGHT, TITLE)
ray.init_audio_device()
assets.load(Path("./assets"))

# n_textures = [Assets.ui.numbers[f"{i}"] for i in range(10)]
# n_sprites = [Sprite(n_texture, ray.Vector2(-0.5 * n_texture.width, -0.5 * n_texture.height)) for n_texture in n_textures]

scene = SceneManager()
while not ray.window_should_close():
    dt = ray.get_frame_time()

    scene.update(dt)
    ray.begin_drawing()
    ray.clear_background(ray.BLACK)
    scene.draw()
    ray.end_drawing()

assets.unload()
ray.close_audio_device()
ray.close_window()
