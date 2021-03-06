from classes.item import Item


class Inventory(dict):
    def __init__(self, inventory: dict = None, max_items: int = None):
        super().__init__(inventory if inventory else dict())
        self.max_items = max_items

    def to_json(self) -> 'dict':
        return {
            "max_items": self.max_items,
            "items": {item.name: amount for item, amount in self.items()}
        }

    @staticmethod
    def from_json(json_object: 'dict') -> 'Inventory':
        from world.items import Items

        if json_object:
            return Inventory(
                inventory={Items.get_item_by_name(
                    item): amount for item, amount in json_object["items"].items()},
                max_items=json_object["max_items"])
        return Inventory()

    def add_item(self, item: Item, amount: int = 1) -> bool:
        from main import CHARACTER

        if item in self:
            self[item] += amount
        elif self.max_items is None or (self.max_items is not None and len(self) < self.max_items):
            self[item] = amount
        else:
            if self == CHARACTER.inventory:
                print(
                    f"Couldn't add {item.__str__(amount=amount)} to your inventory. \
The maximum capacity of {self.max_items} item types is reached. It dropped in the room.")
                CHARACTER.room.loot.add_item(item, amount)
            return False
        if self == CHARACTER.inventory:
            if item.use_on_pickup:
                item.use(amount)
            else:
                print(
                    f"Added {item.__str__(amount=amount)} to your inventory.")
        return True

    def remove_item(self, item: Item, amount: int = 1) -> bool:
        if item in self:
            if amount < self[item]:
                self[item] -= amount
                return True
            if amount == self[item]:
                self.pop(item, None)
                return True
            return False
        return False
