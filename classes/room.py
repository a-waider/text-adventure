from termcolor import colored
from utilities import print

from classes.inventory import Inventory
from classes.item import Item
from classes.npc import NPC

DEFAULT_NPC = None
DEFAULT_LOOT = None
DEFAULT_VISITED = False
DEFAULT_RESPAWN_POINT = False
DEFAULT_LOCKED = False
DEFAULT_LOCK_MESSAGE = None
DEFAULT_ITEMS_TO_BUY = None
DEFAULT_ITEMS_TO_SELL = None


class Room:
    def __init__(self,
                 name: str,
                 npc: NPC = DEFAULT_NPC,
                 loot: 'Inventory[Item,int]' = DEFAULT_LOOT,
                 visited: bool = DEFAULT_VISITED,
                 respawn_point: bool = DEFAULT_RESPAWN_POINT,
                 locked: bool = DEFAULT_LOCKED,
                 lock_message: str = DEFAULT_LOCK_MESSAGE,
                 enter_room_function=lambda: None,
                 items_to_buy: 'Inventory[Item,int]' = DEFAULT_ITEMS_TO_BUY,
                 items_to_sell: 'Inventory[Item,int]' = DEFAULT_ITEMS_TO_SELL):
        self.name = name
        self.connected_rooms = list()
        self.npc: NPC = npc
        self.loot: 'Inventory[Item,int]' = loot if loot is not None else Inventory(
        )
        self.visited: bool = visited
        self.respawn_point: bool = respawn_point
        self.enter_room_function = enter_room_function
        self.locked: bool = locked
        self.lock_message: str = lock_message
        self.items_to_buy: 'Inventory[Item,int]' = items_to_buy if items_to_buy is not None else Inventory(
        )
        self.items_to_sell: 'Inventory[Item,int]' = items_to_sell if items_to_sell is not None else Inventory(
        )

    def __str__(self) -> str:
        return colored(self.name, "blue")

    def to_json(self) -> dict:
        from world.items import Items

        return {
            "name": self.name,
            "npc": self.npc.to_json() if self.npc else None,
            "loot": self.loot.to_json(),
            "visited": self.visited,
            "respawn_point": self.respawn_point,
            "locked": self.locked,
            "lock_message": self.lock_message,
            "items_to_buy": self.items_to_buy.to_json(),
            "items_to_sell": self.items_to_sell.to_json()
        }

    @staticmethod
    def from_json(json_object: 'dict') -> 'Room':
        from world.rooms import Rooms

        room = Rooms.get_room_by_name(json_object["name"])
        room.npc = NPC.from_json(json_object["npc"])
        room.loot = Inventory.from_json(json_object["loot"])
        room.visited = json_object["visited"] if json_object["visited"] else DEFAULT_VISITED
        room.respawn_point = json_object["respawn_point"] if json_object["respawn_point"] else DEFAULT_RESPAWN_POINT
        room.locked = json_object["locked"] if json_object["locked"] else DEFAULT_LOCK_MESSAGE
        room.lock_message = json_object["lock_message"] if json_object["lock_message"] else None
        room.items_to_buy = Inventory.from_json(json_object["items_to_buy"])
        room.items_to_sell = Inventory.from_json(json_object["items_to_sell"])

    def enter_room(self):
        from main import CHARACTER
        from world.items import Items

        if self.locked and self.lock_message:
            print(f"{self.lock_message}\n")
            return
        if self.npc:
            if CHARACTER.kills == 0:
                print([
                    f"You approach your first enemy. Your only weapon is the {Items.REMOTE.value}.",
                    f"Attack {self.npc} by typing \"attack melee\" or \"attack ranged\"."
                ])
            max_name_length = max(len(self.npc.name), len(CHARACTER.name))
            print(f"----- {str(self.npc).center(max_name_length)} -----")
            print(self.npc.fighting_stats())
            print(f"----- {str(CHARACTER).center(max_name_length)} -----")
            print(CHARACTER.fighting_stats())
            print("-"*int(12+max_name_length))
            return
        if self.enter_room_function:
            self.enter_room_function()
        print(f"You are now in {self}.")
        if not self.visited and CHARACTER.room.respawn_point:
            CHARACTER.respawn_point = self
            print("Your respawn point has been updated.")
        self.visited = True
        if self.items_to_buy or self.items_to_sell:
            print(self.shop_menu(), sleep_time=0.0001)

    def buy_menu(self) -> 'list[str]':
        ret = []
        ret.append("Price".center(10)+"Item")
        for item, price in self.items_to_buy.items():
            ret.append(f"{str(price).center(10)}{str(item):20}")
        return ret

    def sell_menu(self) -> 'list[str]':
        ret = []
        ret.append("Returned Coins".center(18)+"Item")
        for item, price in self.items_to_sell.items():
            ret.append(f"{str(price).center(18)}{str(item):20}")
        return ret

    def shop_menu(self) -> str:
        ret = []
        if self.items_to_buy:
            ret.append(f"----- {self} store -----")
            ret.extend(self.buy_menu())
            if not self.items_to_sell:
                ret.append("-"*int(18+len(self.name)))
        if self.items_to_sell:
            ret.append(f"----- {self} buys these items -----")
            ret.extend(self.sell_menu())
            ret.append("-"*int(29+len(self.name)))
        return "\n".join(ret)

    def get_connected_rooms(self) -> 'list[Room]':
        from world.rooms import room_connections

        connected_rooms: 'set[Room]' = set()
        for room_connection in room_connections:
            if self in room_connection:
                if self == room_connection[0]:
                    connected_rooms.add(room_connection[1])
                elif self == room_connection[1]:
                    connected_rooms.add(room_connection[0])

        return [connected_room for connected_room in connected_rooms if not connected_room.locked]
