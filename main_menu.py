import pygame as pg
import moderngl as mgl
from array import array
import sys
from settings import *

class MainMenu:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        self.win_size = int(WIN_RESOLUTION.x), int(WIN_RESOLUTION.y)
        self.width, self.height = self.win_size

        pg.font.init()

        font_path = "assets/fonts/pixel.ttf"

        self.font_title = pg.font.Font(font_path, 72)
        self.font_small = pg.font.Font(font_path, 24)

        self.bg_color = (0, 0, 0)
        self.text_color = (230, 230, 230)
        self.shadow_color = (90, 90, 90)

        self.program = self.ctx.program(
            vertex_shader="""
                #version 330 core

                in vec2 in_pos;
                in vec2 in_uv;

                out vec2 uv;

                void main() {
                    uv = in_uv;
                    gl_Position = vec4(in_pos, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330 core

                uniform sampler2D tex;

                in vec2 uv;
                out vec4 fragColor;

                void main() {
                    fragColor = texture(tex, uv);
                }
            """
        )

        vertices = array("f", [
            -1.0, -1.0,  0.0, 1.0,
             1.0, -1.0,  1.0, 1.0,
            -1.0,  1.0,  0.0, 0.0,

            -1.0,  1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 1.0,
             1.0,  1.0,  1.0, 0.0,
        ])

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, "2f 2f", "in_pos", "in_uv")]
        )

        self.program["tex"] = 0

        self.menu_texture = self.create_menu_texture()
        self.loading_texture = self.create_loading_texture("L o a d i n g . . .")

    def create_texture_from_surface(self, surface):
        texture_data = pg.image.tostring(surface, "RGBA", False)
        texture = self.ctx.texture(self.win_size, 4, texture_data)
        texture.filter = (mgl.NEAREST, mgl.NEAREST)
        return texture

    def create_menu_texture(self):
        surface = pg.Surface(self.win_size)
        surface.fill(self.bg_color)

        title_shadow = self.font_title.render("VOXEL ENGINE", True, self.shadow_color)
        title_shadow_rect = title_shadow.get_rect(
            center=(self.width // 2, self.height // 2 - 115)
        )
        surface.blit(title_shadow, title_shadow_rect)

        title = self.font_title.render("VOXEL ENGINE", True, self.text_color)
        title_rect = title.get_rect(
            center=(self.width // 2, self.height // 2 - 120)
        )
        surface.blit(title, title_rect)

        info = self.font_small.render("Press ENTER to start", True, self.text_color)
        info_rect = info.get_rect(
            center=(self.width // 2, self.height // 2 + 80)
        )
        surface.blit(info, info_rect)

        esc_info = self.font_small.render("ESC to quit", True, self.shadow_color)
        esc_info_rect = esc_info.get_rect(
            center=(self.width // 2, self.height - 80)
        )
        surface.blit(esc_info, esc_info_rect)

        return self.create_texture_from_surface(surface)

    def create_loading_texture(self, text=""):
        surface = pg.Surface(self.win_size)
        surface.fill(self.bg_color)

        loading_text = self.font_small.render(text, True, self.text_color)
        loading_text_rect = loading_text.get_rect(
            center=(self.width // 2, self.height // 2)
        )
        surface.blit(loading_text, loading_text_rect)

        return self.create_texture_from_surface(surface)

    def run(self):
        clock = pg.time.Clock()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.destroy()
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.destroy()
                        pg.quit()
                        sys.exit()

                    if event.key == pg.K_RETURN:
                        self.render_loading()
                        return

            self.render()
            clock.tick(60)

    def render_texture(self, texture, caption):
        pg.display.set_caption(caption)

        self.ctx.disable(mgl.DEPTH_TEST)
        self.ctx.disable(mgl.CULL_FACE)

        self.ctx.clear(color=(0.0, 0.0, 0.0))

        texture.use(location=0)
        self.vao.render()

        pg.display.flip()

    def render(self):
        self.render_texture(self.menu_texture, "Voxel Engine")

    def render_loading(self):
        self.render_texture(self.loading_texture, "Loading...")

    def destroy(self):
        if self.menu_texture is not None:
            self.menu_texture.release()
            self.menu_texture = None

        if self.loading_texture is not None:
            self.loading_texture.release()
            self.loading_texture = None

        if self.vao is not None:
            self.vao.release()
            self.vao = None

        if self.vbo is not None:
            self.vbo.release()
            self.vbo = None

        if self.program is not None:
            self.program.release()
            self.program = None