import random
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Tuple


class Sex(Enum):
    MALE = auto()
    FEMALE = auto()


class DamageType(Enum):
    BLUNT = auto()
    SHARP = auto()


class TaskType(Enum):
    IDLE = auto()
    MOVING = auto()
    EATING = auto()
    REPRODUCING = auto()
    ATTACKING = auto()


class Species(Enum):
    PLANT = auto()
    HERBIVORE = auto()
    OMNIVORE = auto()
    CARNIVORE = auto()


@dataclass
class Coordinate:
    x: float
    y: float


@dataclass
class Locomotion:
    walking_speed: float
    sprinting_speed: float


@dataclass
class Resistance:
    blunt_resist: float
    sharp_resist: float


@dataclass
class DNA:
    genes: Dict[str, float]
    species: Species

    @classmethod
    def random(cls, species: Species):
        base_genes = {
            "size": random.uniform(0.5, 2.0),
            "damage": random.uniform(1, 10),
            "walking_speed": random.uniform(1, 5),
            "sprinting_speed": random.uniform(3, 10),
            "blunt_resist": random.uniform(0, 1),
            "sharp_resist": random.uniform(0, 1),
            "nocturnal": random.choice([True, False]),
        }

        if species == Species.PLANT:
            base_genes["growth_rate"] = random.uniform(0.1, 0.5)
        elif species == Species.HERBIVORE:
            base_genes["diet"] = random.uniform(0, 0.3)
        elif species == Species.OMNIVORE:
            base_genes["diet"] = random.uniform(0.3, 0.7)
        elif species == Species.CARNIVORE:
            base_genes["diet"] = random.uniform(0.7, 1.0)

        return cls(base_genes, species)

    def mutate(self, mutation_rate: float = 0.1):
        for gene in self.genes:
            if random.random() < mutation_rate:
                self.genes[gene] *= random.uniform(0.8, 1.2)


class Entity:
    def __init__(self, dna: DNA, location: Coordinate):
        self.dna = dna
        self.species = dna.species
        self.sex = random.choice(list(Sex)) if self.species != Species.PLANT else None
        self.health = 100
        self.energy = 100
        self.age = 0
        self.damage = dna.genes.get("damage", 0)
        self.damage_type = random.choice(list(DamageType)) if self.species != Species.PLANT else None
        self.diet = dna.genes.get("diet", 0)
        self.locomotion = Locomotion(dna.genes.get("walking_speed", 0), dna.genes.get("sprinting_speed", 0))
        self.task = TaskType.IDLE
        self.location = location
        self.body_temp = 33
        self.nocturnal = dna.genes["nocturnal"]
        self.size = dna.genes["size"]
        self.resistance = Resistance(dna.genes["blunt_resist"], dna.genes["sharp_resist"])
        self.growth_rate = dna.genes.get("growth_rate", 0)

    def reproduce(self, partner: 'Entity') -> 'Entity':
        child_dna = DNA({
            gene: (self.dna.genes[gene] + partner.dna.genes[gene]) / 2
            for gene in self.dna.genes
        }, self.species)
        child_dna.mutate()
        return Entity(child_dna, Coordinate(self.location.x, self.location.y))

    def attack(self, enemy: 'Entity'):
        damage = self.damage * (
            1 - enemy.resistance.blunt_resist if self.damage_type == DamageType.BLUNT else 1 - enemy.resistance.sharp_resist)
        enemy.health -= damage

    def eat(self, food: 'Entity'):
        if self.species == Species.PLANT:
            self.energy += self.growth_rate * 5
        else:
            energy_gain = food.size * 10 * (1 - abs(self.diet - food.diet))
            self.energy = min(100, self.energy + energy_gain)
            food.health -= energy_gain

    def think(self) -> Tuple[float, float, TaskType]:
        if self.species == Species.PLANT:
            return 0, 0, TaskType.IDLE

        if self.energy < 20:
            return random.uniform(-1, 1), random.uniform(-1, 1), TaskType.EATING
        elif self.health < 50:
            return 0, 0, TaskType.IDLE
        elif random.random() < 0.05:  # 5% chance to attempt reproduction
            return random.uniform(-1, 1), random.uniform(-1, 1), TaskType.REPRODUCING
        else:
            return random.uniform(-1, 1), random.uniform(-1, 1), TaskType.MOVING
