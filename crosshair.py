import numpy as np
import moderngl as mgl

class Crosshair:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        self.program = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec2 in_position;

                void main() {
                    gl_Position = vec4(in_position, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                out vec4 fragColor;

                void main() {
                    fragColor = vec4(1.0, 1.0, 1.0, 1.0);
                }
            '''
        )

        size_x = 0.01
        size_y = 0.018
        gap_x = 0.0
        gap_y = 0.0

        vertices = np.array([
            # horizontal left
            -size_x, 0.0,
            -gap_x,  0.0,

            # horizontal right
            gap_x,  0.0,
            size_x, 0.0,

            # vertical top
            0.0, gap_y,
            0.0, size_y,

            # vertical bottom
            0.0, -gap_y,
            0.0, -size_y,
        ], dtype = "f4")

        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, "2f", "in_position")])

    def render(self):
        self.ctx.disable(mgl.DEPTH_TEST)
        self.vao.render(mgl.LINES)
        self.ctx.enable(mgl.DEPTH_TEST)