import pygame as pg
import sys
from settings import *

class MainMenu:
	def __init__(self):
		self.win_size = int(WIN_RESOLUTION.x), int(WIN_RESOLUTION.y)

		self.screen = pg.display.set_mode(self.win_size)
		pg.display.set_caption("Voxel Engine")

		font_path = "assets/fonts/pixel.ttf"

		self.font_title = pg.font.Font(font_path, 72)
		self.font_small = pg.font.Font(font_path, 24)

		self.bg_color = (0, 0, 0)
		self.text_color = (230, 235, 255)

	def run(self):
		while True:
			mouse_pos = pg.mouse.get_pos()

			for event in pg.event.get():
				if event.type == pg.QUIT:
					pg.quit()
					sys.exit()

				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						pg.quit()
						sys.exit()

					if event.key == pg.K_RETURN:
						return

			self.draw(mouse_pos)

	def draw(self, mouse_pos):
		self.screen.fill(self.bg_color)

		title_shadow = self.font_title.render("VOXEL ENGINE", True, (80, 80, 80))
		title_shadow_rect = title_shadow.get_rect(center=(self.win_size[0] // 2, self.win_size[1] // 2 - 115))
		self.screen.blit(title_shadow, title_shadow_rect)

		title_surface = self.font_title.render("VOXEL ENGINE", True, self.text_color)
		title_rect = title_surface.get_rect(center=(self.win_size[0] // 2, self.win_size[1] // 2 - 120))
		self.screen.blit(title_surface, title_rect)

		info_surface = self.font_small.render("Press ENTER to start / ESC to quit", True, self.text_color)
		info_rect = info_surface.get_rect(center=(self.win_size[0] // 2, self.win_size[1] - 80))
		self.screen.blit(info_surface, info_rect)

		pg.display.flip()