import math
import random
from typing import List

from entities import Entity, Species, DNA, Coordinate, TaskType


class Environment:
    def __init__(self, width: int, height: int, seed: str = "aaaaaa"):
        self.seed = seed
        random.seed(seed)
        self.width = width
        self.height = height
        self.average_temperature = 20
        self.temperature = 20
        self.time = 0
        self.night = False
        self.entities: List[Entity] = []
        self.paused = False
        self.simulation_speed = 1

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def tick(self):
        self.time = (self.time + 1) % 10000
        self.night = self.time >= 7500
        self.update_temperature()

        entities_to_remove = []

        for entity in self.entities:
            direction_x, direction_y, task = entity.think()

            if entity.species != Species.PLANT:
                # Move the entity
                speed = entity.locomotion.walking_speed if task != TaskType.EATING else entity.locomotion.sprinting_speed
                new_x = max(0, min(self.width, entity.location.x + direction_x * speed))
                new_y = max(0, min(self.height, entity.location.y + direction_y * speed))
                entity.location = Coordinate(new_x, new_y)

            # Perform the chosen task
            if task == TaskType.EATING:
                potential_food = [e for e in self.entities if self.can_eat(entity, e)]
                if potential_food:
                    food = min(potential_food, key=lambda e: self.distance(entity, e))
                    if self.distance(entity, food) < entity.size + food.size:
                        entity.eat(food)
                        if food.health <= 0:
                            entities_to_remove.append(food)
            elif task == TaskType.REPRODUCING:
                partners = [e for e in self.entities if e.species == entity.species and e.sex != entity.sex]
                if partners:
                    partner = min(partners, key=lambda e: self.distance(entity, e))
                    if self.distance(entity, partner) < entity.size + partner.size:
                        child = entity.reproduce(partner)
                        self.add_entity(child)

            # Update entity state
            entity.energy = max(0, entity.energy - 1)  # Basic energy consumption
            entity.age += 1
            if entity.species == Species.PLANT:
                entity.energy += entity.growth_rate
            if entity.health <= 0 or entity.energy <= 0 or entity.age > 1000:
                entities_to_remove.append(entity)

        # Remove entities after processing all of them
        for entity in entities_to_remove:
            if entity in self.entities:
                self.entities.remove(entity)

        # Spontaneous plant growth
        if random.random() < 0.1:  # 10% chance each tick
            self.add_entity(Entity(DNA.random(Species.PLANT),
                                   Coordinate(random.uniform(0, self.width), random.uniform(0, self.height))))

    def update_temperature(self):
        target_temp = self.average_temperature / 2 if self.night else self.average_temperature
        self.temperature += (target_temp - self.temperature) * 0.1

    def add_random_entity(self, species: Species):
        dna = DNA.random(species)
        location = Coordinate(random.uniform(0, self.width), random.uniform(0, self.height))
        self.add_entity(Entity(dna, location))

    @staticmethod
    def can_eat(predator: Entity, prey: Entity) -> bool:
        if predator.species == Species.HERBIVORE:
            return prey.species == Species.PLANT
        elif predator.species == Species.CARNIVORE:
            return prey.species in [Species.HERBIVORE, Species.OMNIVORE]
        elif predator.species == Species.OMNIVORE:
            return prey.species in [Species.PLANT, Species.HERBIVORE]
        return False

    @staticmethod
    def distance(entity1: Entity, entity2: Entity) -> float:
        return math.sqrt(
            (entity1.location.x - entity2.location.x) ** 2 + (entity1.location.y - entity2.location.y) ** 2)
