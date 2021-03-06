import random

from termcolor import colored
from utilities import colored_health, print
from world.items import Items
from world.rooms import Rooms

from classes.inventory import Inventory
from classes.item import Item, Weapon, WeaponMelee, WeaponRanged
from classes.room import Room

MAX_LUCK = 10


class Person:
    def __init__(
            self,
            name: str = None,
            health: int = 100,
            max_health: int = 100,
            luck: int = random.randint(1, MAX_LUCK),
            armor: int = 0,
            melee_weapon: WeaponMelee = Items.REMOTE.value,
            ranged_weapon: WeaponRanged = None,
            inventory: 'Inventory[Item,int]' = None,
            max_inventory_items: int = 10,
            intelligence: int = 100,
            room: Room = Rooms.BEDROOM,
            respawn_point: Room = Rooms.BEDROOM,
            kills: int = 0,
            cures: int = 0,
            deaths: int = 0):
        self.name: str = name
        self.health: int = health
        self.max_health: int = max_health
        self.luck: int = luck
        self.armor: float = armor
        self.melee_weapon: WeaponMelee = melee_weapon
        self.ranged_weapon: WeaponRanged = ranged_weapon
        self.inventory: 'Inventory[Item,int]' = inventory if inventory is not None else Inventory(
            max_items=5)
        self.max_inventory_items: int = max_inventory_items
        self.intelligence: int = intelligence
        self.room: Room = room
        self.respawn_point: Room = respawn_point
        self.kills: int = kills
        self.cures: int = cures
        self.deaths: int = deaths

    def __str__(self) -> str:
        return self.name

    def stats(self, ammunition: bool = False, prev_health: int = None, prev_armor: int = None):
        return f"""{self.fighting_stats(ammunition=ammunition, prev_health=prev_health, prev_armor=prev_armor)}
{'Cures: ':15}💉 {self.cures}
{'Luck: ':15}🍀 {self.luck}"""

    def fighting_stats(self,
                       ammunition: bool = False,
                       prev_health: int = None,
                       prev_armor: int = None,
                       critical: bool = False) -> str:
        heart_icon, health_color = colored_health(self.health, self.max_health)
        health_lost_string: str = f"{prev_health} - {prev_health-self.health} \
{'(critical hit)' if critical else ''} = " if prev_health and prev_health != self.health else ""
        armor_damage_string: str = f"{prev_armor} - {round(prev_armor-self.armor,1)} \
= " if prev_armor and prev_armor != self.armor else ""
        ret = f"""{'Health: ':15}{heart_icon} {health_lost_string}\
{colored(f'{max(self.health,0)} / {self.max_health}', health_color)}
{'Armor: ':15}🛡  {armor_damage_string}{colored(self.armor, 'blue')}
{'Kills: ':15}🔪 {self.kills}
{'Deaths: ':15}💀 {self.deaths}"""
        if ammunition:
            ret += f"\n{'Ammunition: ':15}: {self.ranged_weapon.ammunition}"
        return ret

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "luck": self.luck,
            "armor": self.armor,
            "melee_weapon": self.melee_weapon.to_json() if self.melee_weapon else None,
            "ranged_weapon": self.ranged_weapon.to_json() if self.ranged_weapon else None,
            "inventory": self.inventory.to_json(),
            "max_inventory_items": self.max_inventory_items,
            "intelligence": self.intelligence,
            "room": self.room.name,
            "respawn_point": self.respawn_point.name,
            "kills": self.kills,
            "deaths": self.deaths
        }

    @staticmethod
    def from_json(json_object: 'dict'):
        from main import CHARACTER

        CHARACTER.name = json_object["name"]
        CHARACTER.health = json_object["health"] if json_object["health"] else 100
        CHARACTER.max_health = json_object["max_health"] if json_object["max_health"] else 100
        CHARACTER.luck = json_object["luck"] if json_object["luck"] else 0
        CHARACTER.armor = json_object["armor"] if json_object["armor"] else 0
        CHARACTER.melee_weapon = WeaponMelee.from_json(
            json_object["melee_weapon"])
        CHARACTER.ranged_weapon = WeaponRanged.from_json(
            json_object["ranged_weapon"])
        CHARACTER.inventory = Inventory.from_json(json_object["inventory"])
        CHARACTER.max_inventory_items = json_object["max_inventory_items"]
        CHARACTER.intelligence = json_object["intelligence"] if json_object["intelligence"] else 0
        CHARACTER.room = Rooms.get_room_by_name(json_object["room"])
        CHARACTER.respawn_point = Rooms.get_room_by_name(
            json_object["respawn_point"])
        CHARACTER.kills = json_object["kills"] if json_object["kills"] else 0
        CHARACTER.deaths = json_object["deaths"] if json_object["deaths"] else 0

    def attack(self, weapon: Weapon) -> int:
        if isinstance(weapon, WeaponMelee):
            return int(self.melee_weapon.attack() * self.intelligence / 100)
        if isinstance(weapon, WeaponRanged):
            try:
                return int(self.ranged_weapon.attack() * self.intelligence / 100)
            except TypeError:
                return None
        print("TODO: ")
        return None

    def attack_melee(self) -> int:
        return int(self.melee_weapon.attack() * self.intelligence / 100)

    def attack_ranged(self) -> int:
        return int(self.ranged_weapon.attack() * self.intelligence / 100)

    def defend(self, damage: int):
        if self.armor == 0:
            self.health = max(self.health-damage, 0)
        else:
            for _ in range(int(self.armor)):
                damage *= 0.98
            self.health = max(self.health - int(damage), 0)
        self.armor = round(max(self.armor - int(damage)*0.18, 0), 1)

    def add_health(self, health_points: int):
        self.health = min(self.health+health_points, self.max_health)
