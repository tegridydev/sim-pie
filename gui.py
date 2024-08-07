from typing import Tuple

import pygame


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class Slider:
    def __init__(self, x: int, y: int, width: int, height: int, min_value: float, max_value: float,
                 initial_value: float, label: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.dragging = False
        self.label = label

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        # Draw the slider background
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        # Calculate the position of the slider handle
        pos = self.rect.x + (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width
        # Draw the slider handle
        pygame.draw.circle(screen, (100, 100, 100), (int(pos), self.rect.centery), 10)
        # Draw the label and current value
        label_surf = font.render(f"{self.label}: {self.value:.2f}", True, (0, 0, 0))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 20))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos = (event.pos[0] - self.rect.x) / self.rect.width
            self.value = self.min_value + pos * (self.max_value - self.min_value)
            self.value = max(self.min_value, min(self.max_value, self.value))


class InputBox:
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = pygame.font.Font(None, 32).render(text, True, self.color)
        self.active = False
        self.text_content = ""

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text_content)
                    self.text_content = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text_content = self.text_content[:-1]
                else:
                    self.text_content += event.unicode
                # Re-render the text.
                self.txt_surface = pygame.font.Font(None, 32).render(self.text_content, True, self.color)

    def draw(self, screen: pygame.Surface):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
