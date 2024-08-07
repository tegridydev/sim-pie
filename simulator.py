from typing import Tuple

import pygame

from entities import Entity, Species
from environment import Environment
from gui import Button, Slider, InputBox


class Simulator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.env = Environment(width - 300, height)  # Reserve 300 pixels for GUI
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Advanced Life Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        # GUI elements
        self.buttons = [
            Button(width - 290, 10, 280, 30, "Pause/Resume", (100, 100, 100)),
            Button(width - 290, 50, 280, 30, "Add Plant", (0, 200, 0)),
            Button(width - 290, 90, 280, 30, "Add Herbivore", (0, 0, 200)),
            Button(width - 290, 130, 280, 30, "Add Omnivore", (200, 100, 0)),
            Button(width - 290, 170, 280, 30, "Add Carnivore", (200, 0, 0)),
            Button(width - 290, 210, 280, 30, "Toggle Grid", (150, 150, 150)),
            Button(width - 290, 250, 280, 30, "Reset Simulation", (200, 0, 0)),
        ]
        self.sliders = [
            Slider(width - 290, 300, 280, 20, 0.1, 5.0, 1.0, "Simulation Speed"),
            Slider(width - 290, 350, 280, 20, 0, 40, 20, "Temperature"),
            Slider(width - 290, 400, 280, 20, 0, 1, 0.1, "Mutation Rate"),
        ]
        self.input_boxes = [
            InputBox(width - 290, 450, 280, 30, "Seed"),
        ]

        # Simulation settings
        self.show_grid = False
        self.grid_size = 20
        self.selected_entity = None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    for box in self.input_boxes:
                        box.handle_event(event)
                for slider in self.sliders:
                    slider.handle_event(event)

            self.update_simulation()
            self.draw()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()

    def update_simulation(self):
        self.env.simulation_speed = self.sliders[0].value
        self.env.average_temperature = self.sliders[1].value
        self.env.mutation_rate = self.sliders[2].value

        if not self.env.paused:
            for _ in range(int(self.env.simulation_speed)):
                self.env.tick()

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background

        if self.show_grid:
            self.draw_grid()

        # Draw entities
        for entity in self.env.entities:
            color = self.get_entity_color(entity)
            pygame.draw.circle(self.screen, color,
                               (int(entity.location.x), int(entity.location.y)),
                               int(entity.size * 5))

            # Highlight selected entity
            if entity == self.selected_entity:
                pygame.draw.circle(self.screen, (255, 255, 0),
                                   (int(entity.location.x), int(entity.location.y)),
                                   int(entity.size * 5) + 2, 2)

        # Draw GUI elements
        for button in self.buttons:
            button.draw(self.screen, self.font)
        for slider in self.sliders:
            slider.draw(self.screen, self.font)
        for box in self.input_boxes:
            box.draw(self.screen)

        # Display stats
        self.draw_stats()

        # Display selected entity info
        if self.selected_entity:
            self.draw_entity_info()

        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, self.env.width, self.grid_size):
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, self.env.height))
        for y in range(0, self.env.height, self.grid_size):
            pygame.draw.line(self.screen, (200, 200, 200), (0, y), (self.env.width, y))

    def draw_stats(self):
        stats = [
            f"Entities: {len(self.env.entities)}",
            f"Temperature: {self.env.temperature:.1f}",
            f"Time: {'Night' if self.env.night else 'Day'}",
            f"Plants: {sum(1 for e in self.env.entities if e.species == Species.PLANT)}",
            f"Herbivores: {sum(1 for e in self.env.entities if e.species == Species.HERBIVORE)}",
            f"Omnivores: {sum(1 for e in self.env.entities if e.species == Species.OMNIVORE)}",
            f"Carnivores: {sum(1 for e in self.env.entities if e.species == Species.CARNIVORE)}",
        ]
        for i, stat in enumerate(stats):
            text_surface = self.font.render(stat, True, (0, 0, 0))
            self.screen.blit(text_surface, (self.env.width + 10, 500 + i * 30))

    def draw_entity_info(self):
        info = [
            f"Species: {self.selected_entity.species.name}",
            f"Health: {self.selected_entity.health:.1f}",
            f"Energy: {self.selected_entity.energy:.1f}",
            f"Age: {self.selected_entity.age}",
            f"Size: {self.selected_entity.size:.2f}",
            f"Diet: {self.selected_entity.diet:.2f}",
            f"Task: {self.selected_entity.task.name}",
        ]
        for i, line in enumerate(info):
            text_surface = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text_surface, (10, 10 + i * 25))

    def handle_mouse_click(self, pos: Tuple[int, int]):
        for button in self.buttons:
            if button.is_clicked(pos):
                self.handle_button_click(button.text)
                return

        # Check if an entity was clicked
        for entity in self.env.entities:
            distance = ((entity.location.x - pos[0]) ** 2 + (entity.location.y - pos[1]) ** 2) ** 0.5
            if distance <= entity.size * 5:
                self.selected_entity = entity
                return

        # If no entity was clicked, deselect
        self.selected_entity = None

    def handle_button_click(self, button_text: str):
        if button_text == "Pause/Resume":
            self.env.paused = not self.env.paused
        elif button_text == "Add Plant":
            self.env.add_random_entity(Species.PLANT)
        elif button_text == "Add Herbivore":
            self.env.add_random_entity(Species.HERBIVORE)
        elif button_text == "Add Omnivore":
            self.env.add_random_entity(Species.OMNIVORE)
        elif button_text == "Add Carnivore":
            self.env.add_random_entity(Species.CARNIVORE)
        elif button_text == "Toggle Grid":
            self.show_grid = not self.show_grid
        elif button_text == "Reset Simulation":
            seed = self.input_boxes[0].text or None
            self.env = Environment(self.width - 300, self.height, seed)

    @staticmethod
    def get_entity_color(entity: Entity) -> Tuple[int, int, int]:
        if entity.species == Species.PLANT:
            return (0, 255, 0)  # Green
        elif entity.species == Species.HERBIVORE:
            return (0, 0, 255)  # Blue
        elif entity.species == Species.OMNIVORE:
            return (255, 165, 0)  # Orange
        elif entity.species == Species.CARNIVORE:
            return (255, 0, 0)  # Red
        return (128, 128, 128)  # Gray for unknown species
