import random

from exceptions import NotEnoughInInventory, NotInInventory
from termcolor import colored
from world.items import Items
from world.rooms import Rooms

from classes.item import Item, WeaponMelee, WeaponRanged
from classes.room import Room


class Person:
    def __init__(
            self,
            name: str = None,
            health: int = 100,
            luck: int = random.randint(1, 10),
            armor: int = 0,
            melee_weapon: WeaponMelee = Items.FIST.value,
            ranged_weapon: WeaponRanged = None,
            inventory: 'dict[Item]' = None,
            intelligence: int = 100,
            room: Room = Rooms.BEDROOM,
            kills: int = 0,
            deaths: int = 0):
        self.name: str = name
        self.health: int = health
        self.luck: int = luck
        self.armor: int = armor
        self.melee_weapon: WeaponMelee = melee_weapon
        self.ranged_weapon: WeaponRanged = ranged_weapon
        self.inventory: 'dict[Item]' = inventory if inventory is not None else dict(
        )
        self.intelligence: int = intelligence
        self.room: Room = room
        self.kills: int = kills
        self.deaths: int = deaths

    def __str__(self) -> str:
        return self.name

    def fighting_stats(self, ammunition: bool = False) -> str:
        if self.health < 30:
            health_color = "yellow"
        elif self.health < 10:
            health_color = "red"
        else:
            health_color = "green"
        ret = f"Health: {colored(self.health, health_color)}\nArmor: {colored(self.armor, 'blue')}"
        if ammunition:
            ret += f"Ammunition: {self.ranged_weapon.ammunition}"
        return ret

    def to_json(self) -> dict:
        inventory_dict = {}
        for item, amount in self.inventory:
            inventory_dict[str(item)] = amount
        ranged_weapon = self.ranged_weapon.to_json() if self.ranged_weapon else None
        return {
            "name": self.name,
            "health": self.health,
            "luck": self.luck,
            "armor": self.armor,
            "melee_weapon": self.melee_weapon.to_json(),
            "ranged_weapon": ranged_weapon,
            "inventory": inventory_dict,
            "intelligence": self.intelligence,
            "room": str(self.room),
            "kills": self.kills,
            "deaths": self.deaths
        }

    def attack_melee(self) -> int:
        return int(self.melee_weapon.attack() * self.intelligence / 100)

    def attack_ranged(self) -> int:
        return int(self.ranged_weapon.attack() * self.intelligence / 100)

    def defend(self, damage: int):
        self.armor = max(self.armor - damage*0.25, 0)
        if self.armor == 0:
            self.health -= damage
        else:
            self.health = max(self.health - int(damage / self.armor * 10), 0)

    def add_to_inventory(self, item: Item, amount: int = 1):
        if item in self.inventory:
            self.inventory[item] += amount
        else:
            self.inventory[item] = amount

    def remove_from_inventory(self, item: Item, amount: int = 1):
        if item in self.inventory:
            if amount > self.inventory[item]:
                self.inventory[item] -= amount
            elif amount == self.inventory[item]:
                self.inventory.pop(item, None)
            else:
                raise NotEnoughInInventory
        else:
            raise NotInInventory
