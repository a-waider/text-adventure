from classes.inventory import Inventory
from classes.npc import NPC
from main import CHARACTER, main
from world.items import Items
from world.rooms import Rooms


def execute_commands(commands: 'list[str]'):
    main(test_mode=True, user_commands=commands)


def test_unlock_front_door():
    Rooms.FRONT_YARD.value.locked = True
    CHARACTER.room = Rooms.CORRIDOR.value
    CHARACTER.inventory.add_item(Items.KEY_HOME.value)
    execute_commands(commands=[
        f"use {Items.KEY_HOME.value.name}"
    ])
    assert Rooms.FRONT_YARD.value.locked is False
    execute_commands(commands=[
        f"go {Rooms.FRONT_YARD.value.name}"
    ])
    assert CHARACTER.room == Rooms.FRONT_YARD.value


def test_cant_go_to_locked_room():
    Rooms.FRONT_YARD.value.locked = True
    CHARACTER.room = Rooms.CORRIDOR.value
    execute_commands(commands=[
        f"go {Rooms.FRONT_YARD.value.name}"
    ])
    assert CHARACTER.room == Rooms.CORRIDOR.value
    assert Rooms.FRONT_YARD.value.locked is True


def test_take_item():
    Rooms.CORRIDOR.value.loot = Inventory({
        Items.COIN.value: 1
    })
    CHARACTER.room = Rooms.CORRIDOR.value
    CHARACTER.inventory = Inventory()
    execute_commands(commands=[
        f"take {Items.COIN.value.name}"
    ])
    assert Items.COIN.value in CHARACTER.inventory


def test_drop_item():
    Rooms.CORRIDOR.value.loot = Inventory({
        Items.COIN.value: 1
    })
    CHARACTER.room = Rooms.CORRIDOR.value
    CHARACTER.inventory = Inventory(
        inventory={
            Items.ARMOR.value: 1
        },
        max_items=1)
    execute_commands(commands=[
        f"take {Items.COIN.value.name}"
    ])
    assert Items.COIN.value not in CHARACTER.inventory
    assert Items.COIN.value in CHARACTER.room.loot


def test_equip_melee_weapon():
    CHARACTER.melee_weapon = Items.FIST.value
    CHARACTER.inventory.add_item(Items.KNIFE.value)
    execute_commands(commands=[
        f"equip {Items.KNIFE.value.name}"
    ])
    assert CHARACTER.melee_weapon == Items.KNIFE.value
    assert Items.KNIFE.value not in CHARACTER.inventory.keys()
    assert Items.FIST.value in CHARACTER.inventory.keys()


def test_equip_ranged_weapon():
    CHARACTER.ranged_weapon = None
    CHARACTER.inventory.add_item(Items.BOW.value)
    execute_commands(commands=[
        f"equip {Items.BOW.value.name}"
    ])
    assert CHARACTER.ranged_weapon == Items.BOW.value
    assert len(CHARACTER.inventory) == 0


def test_use_armor():
    CHARACTER.inventory.add_item(Items.ARMOR.value)
    assert CHARACTER.armor == 0
    execute_commands(commands=[
        f"use {Items.ARMOR.value.name}"
    ])
    assert CHARACTER.armor == 1


def test_max_inventory():
    CHARACTER.inventory.max_items = 2
    assert CHARACTER.inventory.add_item(Items.ARMOR.value)
    assert CHARACTER.inventory.add_item(Items.COIN.value)
    assert not CHARACTER.inventory.add_item(Items.ARROW.value)


def test_npc_loot_drops_in_room_loot_if_inventory_full():
    CHARACTER.inventory.max_items = 1
    CHARACTER.inventory.add_item(Items.COIN.value)
    CHARACTER.room = Rooms.LOUNGE.value
    Rooms.KITCHEN.value.loot = Inventory()
    Rooms.KITCHEN.value.npc = NPC(
        "dummy",
        health=1,
        base_damage=3,
        loot=Inventory({
            Items.ARMOR.value: 1
        }))
    execute_commands(commands=[
        f"go {Rooms.KITCHEN.value.name}",
        "attack melee"
    ])
    assert Items.ARMOR.value not in list(CHARACTER.inventory.keys())
    assert Items.ARMOR.value in list(Rooms.KITCHEN.value.loot.keys())


def test_update_respawn_point():
    CHARACTER.room = Rooms.CORRIDOR.value
    CHARACTER.respawn_point = Rooms.BEDROOM.value
    Rooms.FRONT_YARD.value.locked = False
    execute_commands(commands=[
        f"go {Rooms.FRONT_YARD.value.name}"
    ])
    assert CHARACTER.respawn_point == Rooms.FRONT_YARD.value


def test_buy_item():
    CHARACTER.room = Rooms.GARAGE.value
    CHARACTER.inventory.add_item(Items.COIN.value, 100)
    execute_commands(commands=[
        f"buy {Items.ARMOR.value.name}"
    ])
    assert Items.ARMOR.value in CHARACTER.inventory


def test_use_on_pickup():
    CHARACTER.room = Rooms.GARAGE.value
    CHARACTER.inventory.add_item(Items.COIN.value, 100)
    assert CHARACTER.armor == 0
    execute_commands(commands=[
        f"buy {Items.ARMOR.value.name}"
    ])
    assert CHARACTER.armor == 1


def test_buy_multiple_items(items_to_buy: int = 5,):
    CHARACTER.room = Rooms.GARAGE.value
    CHARACTER.inventory.add_item(Items.COIN.value, items_to_buy*100)
    execute_commands(commands=[
        f"buy {Items.ARMOR.value.name} {items_to_buy}"
    ])
    assert CHARACTER.inventory[Items.ARMOR.value] == items_to_buy
    assert CHARACTER.inventory[Items.COIN.value] == items_to_buy*100 - \
        items_to_buy * Rooms.GARAGE.value.items_to_buy[Items.ARMOR.value]
    assert Items.ARMOR.value in CHARACTER.inventory


def test_fight():
    Rooms.KITCHEN.value.npc = NPC("dummy", health=1, base_damage=3)
    CHARACTER.room = Rooms.LOUNGE.value
    execute_commands(commands=[
        f"go {Rooms.KITCHEN.value.name}",
        "attack melee",
    ])
    assert CHARACTER.room.npc is None


def test_savepoints():
    execute_commands(commands=[
        "import savepoint",
        "create savepoint",
    ])


def test_view_map():
    CHARACTER.inventory.add_item(Items.MAP_HOME.value)
    execute_commands(commands=[
        f"view {Items.MAP_HOME.value.name}"
    ])
