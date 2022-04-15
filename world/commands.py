import json

from classes.command import Command
from classes.item import Item, Map, Weapon, WeaponMelee, WeaponRanged
from classes.npc import NPC
from classes.room import Room

# pylint: disable=unused-argument


def help_menu(args: 'list[str]'):
    print("----- Help -----")
    print(
        f"{'Command':20}{'Arguments':19}: {'Description':70}{'Aliases':20}")
    for command in commands:
        print(
            f"{command.keyword:20}{', '.join(command.args):19}: {command.description:70}{', '.join(command.aliases):20}")
    print("-----")


def show_statistics(args: 'list[str]'):
    from main import CHARACTER

    print("----- Statistics -----")
    print(f"Kills: {CHARACTER.kills}")
    print(f"Deaths: {CHARACTER.deaths}")
    print("-----")


def show_inventory(args: 'list[str]'):
    from main import CHARACTER

    if str(CHARACTER).endswith("s"):
        print(f"----- {CHARACTER}' Inventory -----")
    else:
        print(f"----- {CHARACTER}'s Inventory -----")
    print(f"Melee weapon: {CHARACTER.melee_weapon}")
    if CHARACTER.ranged_weapon:
        print(f"Ranged weapon: {CHARACTER.ranged_weapon}")
    for item, amount in CHARACTER.inventory.items():
        if amount > 1:
            print(f"{amount} {item.plural}")
        else:
            print(item)
    print("-----")


def show_health(args: 'list[str]'):
    from main import CHARACTER

    print(f"----- {CHARACTER} -----")
    print(CHARACTER.fighting_stats)
    print("-----")


def take(args: 'list[str]'):
    from main import CHARACTER

    from world.items import Items

    item_name = " ".join(args)
    item = Items.get_item_by_name(item_name)
    amount = CHARACTER.room.loot[item]
    if item:
        CHARACTER.room.loot.pop(item, None)
        CHARACTER.add_to_inventory(item, amount)
    else:
        print("This item does not exist")


def search_room(args: 'list[str]'):
    from main import CHARACTER

    loot: 'dict[Item]' = CHARACTER.room.loot
    for loot_item, amount in loot.items():
        if amount > 1:
            print(f"{amount} {loot_item.plural}")
        else:
            print(loot_item)


def use(args: 'list[str]'):
    from main import CHARACTER

    from world.items import Items

    item_name = " ".join(args)
    item = Items.get_item_by_name(item_name)
    if item in CHARACTER.inventory:
        item.use()
    else:
        print("You don't have this item in your inventory")


def view(args: 'list[str]'):
    from main import CHARACTER

    from world.items import Items

    map_name = " ".join(args)
    map_object = Map.get_map_by_name(map_name)
    if map_object in CHARACTER.inventory.keys():
        map_object.view()
    else:
        print("You don't have this map in your inventory")


def where_am_i(args: 'list[str]'):
    from main import CHARACTER

    print(f"You are in {CHARACTER.room}")


def where_can_i_go(args: 'list[str]'):
    from main import CHARACTER

    print(", ".join(str(room)
          for room in CHARACTER.room.get_connected_rooms()))


def go(args: 'list[str]'):
    # pylint: disable=invalid-name
    from main import CHARACTER

    from world.rooms import Rooms, room_connections

    current_room: Room = CHARACTER.room
    next_room: Room = Rooms.get_room_by_name(" ".join(args))
    for room_connection in room_connections:
        if current_room in room_connection and next_room in room_connection:
            if next_room.locked:
                print(next_room.lock_message)
            else:
                CHARACTER.room = next_room
                CHARACTER.room.enter_room()
            return
    print("You can't go in this room")


def equip(args: 'list[str]'):
    from main import CHARACTER

    weapon = Weapon.get_weapon_by_name(" ".join(args))
    if weapon in CHARACTER.inventory.keys():
        if CHARACTER.inventory[weapon] > 1:
            raise Exception("Should never enter this branch")
        if isinstance(weapon, WeaponMelee):  # Melee Weapon
            if CHARACTER.melee_weapon:
                if CHARACTER.melee_weapon in CHARACTER.inventory.keys():
                    CHARACTER.inventory[CHARACTER.melee_weapon] += 1
                else:
                    CHARACTER.inventory[CHARACTER.melee_weapon] = 1
            CHARACTER.melee_weapon = weapon
        elif isinstance(weapon, WeaponRanged):  # Ranged Weapon
            if CHARACTER.ranged_weapon:
                if CHARACTER.ranged_weapon in CHARACTER.inventory.keys():
                    CHARACTER.inventory[CHARACTER.ranged_weapon] += 1
                else:
                    CHARACTER.inventory[CHARACTER.ranged_weapon] = 1
            CHARACTER.ranged_weapon = weapon
        CHARACTER.remove_from_inventory(weapon)
    print(
        f"You have now {weapon} equipped. Your previous equipped weapon is in your inventory.")


def inspect(args: 'list[str]'):
    from main import CHARACTER

    weapon = Weapon.get_weapon_by_name(" ".join(args))
    weapons = []
    if CHARACTER.melee_weapon:
        weapons.append(CHARACTER.melee_weapon)
    if CHARACTER.ranged_weapon:
        weapons.append(CHARACTER.ranged_weapon)
    for item in CHARACTER.inventory:
        if isinstance(item, Weapon):
            weapons.append(item)

    if weapon in weapons:
        print(f"----- {weapon} -----")
        print(f"Base damage: {weapon.base_damage}")
        print(f"Damage variation: {weapon.damage_variation}")
        if isinstance(weapon, WeaponRanged):
            print(f"Ammunition: {weapon.ammunition}")
        print("-----")
    else:
        print("You don't have this weapon equipped or in your inventory")


def attack(args: 'list[str]'):
    from main import CHARACTER
    from world.commands import create_savepoint
    from world.rooms import respawn_rooms

    npc: NPC = CHARACTER.room.npc
    if npc:
        character_attack_damage: int = 0
        if args[0] == "melee":
            if CHARACTER.melee_weapon:
                character_attack_damage = CHARACTER.attack_melee()
            else:
                print("You don't have a melee weapon")
                return
        elif args[0] == "ranged":
            if CHARACTER.ranged_weapon:
                character_attack_damage = CHARACTER.attack_ranged()
            else:
                print("You don't have a ranged weapon")
                return
        else:
            print("You must define which weapon you want to use.")
            return
        npc_attack_damage = npc.attack()
        npc.defend(character_attack_damage)
        CHARACTER.defend(npc_attack_damage)
        if npc.health <= 0:
            print(f"You defeated {npc}")
            print(f"----- {CHARACTER} ----")
            print(CHARACTER.fighting_stats())
            print("-----")
            for item, amount in npc.loot.items():
                if item in CHARACTER.inventory:
                    CHARACTER.inventory[item] += amount
                else:
                    CHARACTER.inventory[item] = amount
            if npc.loot:
                print("New items in your inventory")
            CHARACTER.room.npc = None
        elif CHARACTER.health <= 0:
            CHARACTER.deaths += 1
            CHARACTER.health = 100
            CHARACTER.room = [
                room for room in respawn_rooms if room.visited].pop(0)
            print(
                f"You have been killed by {npc} and respawn in {CHARACTER.room}")
            create_savepoint([""])
        else:
            print(f"----- {npc} -----")
            print(npc.fighting_stats())
            print(f"----- {CHARACTER} ----")
            print(CHARACTER.fighting_stats())
            print("-----")
    else:
        print("There are no npc's to fight.")


def create_savepoint(args: 'list[str]'):
    from main import CHARACTER

    from world.rooms import Rooms

    filename = args[0] if args[0] else "savepoint.json"
    json_output = {
        "character": CHARACTER.to_json(),
        "rooms": Rooms.to_json()
    }
    with open(filename, "w") as file:
        file.write(json.dumps(json_output, indent=4, ensure_ascii=True))
    print(f"Successfully created savepoint at \"{filename}\"")


def import_savepoint(args: 'list[str]'):
    from main import CHARACTER

    from world.items import Items
    from world.rooms import Rooms

    filename = args[0] if args[0] else "savepoint.json"
    try:
        with open(filename) as file:
            json_import = json.loads(file.read())
            # Character
            json_character = json_import["character"]
            melee_weapon: WeaponMelee = Items.get_item_by_name(
                json_character["melee_weapon"]["name"]) if json_character["melee_weapon"] else None
            if json_character["melee_weapon"]:
                melee_weapon.base_damage = json_character["melee_weapon"]["base_damage"]
                melee_weapon.damage_variation = json_character["melee_weapon"]["damage_variation"]
            ranged_weapon: WeaponRanged = Items.get_item_by_name(
                json_character["ranged_weapon"]["name"]) if json_character["ranged_weapon"] else None
            if json_character["ranged_weapon"]:
                ranged_weapon.base_damage = json_character["ranged_weapon"]["base_damage"]
                ranged_weapon.damage_variation = json_character["ranged_weapon"]["damage_variation"]
                ranged_weapon.ammunition = json_character["ranged_weapon"]["ammunition"]
            CHARACTER.name = json_character["name"]
            CHARACTER.health = json_character["health"] if json_character["health"] else 100
            CHARACTER.luck = json_character["luck"] if json_character["luck"] else 0
            CHARACTER.armor = json_character["armor"] if json_character["armor"] else 0
            CHARACTER.melee_weapon = melee_weapon
            CHARACTER.ranged_weapon = ranged_weapon
            CHARACTER.inventory = {Items.get_item_by_name(
                item_name): amount for item_name, amount in json_character["inventory"]}
            CHARACTER.intelligence = json_character["intelligence"] if json_character["intelligence"] else 0
            CHARACTER.room = Rooms.get_room_by_name(json_character["room"])
            CHARACTER.kills = json_character["kills"] if json_character["kills"] else 0
            CHARACTER.deaths = json_character["deaths"] if json_character["deaths"] else 0

            # Rooms
            json_rooms = json_import["rooms"]
            for json_room in json_rooms:
                room = Rooms.get_room_by_name(json_room["name"])
                room.npc = NPC(
                    name=json_room["npc"]["name"],
                    health=json_room["npc"]["health"] if json_room["npc"]["health"] else 100,
                    base_damage=json_room["npc"]["base_damage"] if json_room["npc"]["base_damage"] else 10,
                    krit_damage=json_room["npc"]["krit_damage"] if json_room["npc"]["krit_damage"] else 0,
                    krit_chance=json_room["npc"]["krit_chance"] if json_room["npc"]["krit_chance"] else 0,
                    armor=json_room["npc"]["armor"] if json_room["npc"]["armor"] else 0,
                    loot={Items.get_item_by_name(
                        item_name): amount for item_name, amount in json_room["npc"]["loot"].items()} if json_room["npc"]["loot"] else None
                ) if json_room["npc"] else None
                room.loot = {}
                room.visited = json_room["visited"] if json_room["visited"] else False
                room.locked = json_room["locked"] if json_room["locked"] else False
                room.lock_message = json_room["lock_message"] if json_room["lock_message"] else None
    except FileNotFoundError:
        print(f"\"{filename}\" does not exist")

    print(
        f"Successfully importet savepoint from \"{filename}\". Welcome back, {CHARACTER.name}. You are now in {CHARACTER.room}")


commands: 'list[Command]' = [
    Command("help",
            description="Shows this help message",
            available_in_fight=True,
            command=help_menu),
    Command("show statistics",
            aliases=["show stats"],
            description="Shows the statistics to your character",
            available_in_fight=True,
            command=show_statistics),
    Command("show inventory",
            aliases=["show inv"],
            description="Shows the inventory of your character",
            available_in_fight=True,
            command=show_inventory),
    Command("show health",
            description="Shows the health of your character",
            available_in_fight=True,
            command=show_health),
    Command("where am i",
            description="Shows your current room",
            available_in_fight=True,
            command=where_am_i),
    Command("where can i go",
            description="Shows the rooms you can enter from your current position",
            command=where_can_i_go),
    Command("go",
            args=["room"],
            description="Move your character to another room",
            command=go),
    Command("search room",
            aliases=["search", "look"],
            description="Searches the room for loot",
            command=search_room),
    Command("take",
            args=["item"],
            description="Takes an item into the inventory",
            command=take),
    Command("use",
            args=["item"],
            description="Uses an item from your inventory",
            command=use),
    Command("view",
            args=["map name"],
            description="Displays the map",
            command=view),
    Command("equip",
            args=["weapon name"],
            description="Equips a weapon",
            available_in_fight=True,
            command=equip),
    Command("inspect",
            args=["weapon name"],
            description="Shows the specs of a equipped weapon or a weapon in your inventory",
            available_in_fight=True,
            command=inspect),
    Command("attack",
            args=["weapon type"],
            description="Attacks an enemy. Valid types are \"melee\" or \"ranged\"",
            available_in_fight=True,
            command=attack),
    Command("create savepoint",
            args=["filename"],
            aliases=["save"],
            description="Creates a savepoint",
            available_in_fight=True,
            command=create_savepoint),
    Command("import savepoint",
            args=["filename"],
            description="Imports a savepoint",
            available_in_fight=True,
            command=import_savepoint)
]