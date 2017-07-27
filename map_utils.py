from tdl.map import Map

from random import randint, choice

from components.ai import BasicMonster, BasicNPC
from components.fighter import Fighter
from components.humanoid import Humanoid, Races, Professions
from components.item import Item
from entity import Entity
from item_functions import heal
from render_functions import RenderOrder


class GameMap(Map):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.explored = [[False for y in range(height)] for x in range(width)]


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return center_x, center_y

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


def create_room(game_map, room):
    # go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            game_map.walkable[x, y] = True
            game_map.transparent[x, y] = True


def create_h_tunnel(game_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        game_map.walkable[x, y] = True
        game_map.transparent[x, y] = True


def create_v_tunnel(game_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        game_map.walkable[x, y] = True
        game_map.transparent[x, y] = True


def place_entities(room, entities, max_monsters_per_room, max_items_per_room, colors):
    # Get a random number of monsters
    number_of_monsters = randint(0, max_monsters_per_room)
    # Get a random number of items
    number_of_items = randint(0, max_items_per_room)

    for i in range(number_of_monsters):
        # Choose a random location in the room
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            chance = randint(0, 100)
            if chance < 50:
                humanoid_component = Humanoid(race=Races.Goblin, profession=Professions.Monster, level=1)
                fighter_component = Fighter(hp=8, defense=0, power=2)
                ai_component = BasicMonster()
                monster = Entity(x, y, 'g', colors.get(
                    'red'), 'Goblin', blocks=True, render_order=RenderOrder.ACTOR,
                                 humanoid=humanoid_component, fighter=fighter_component, ai=ai_component)
            elif chance < 80:
                humanoid_component = Humanoid(race=Races.Orc, profession=Professions.Monster, level=1)
                fighter_component = Fighter(hp=10, defense=1, power=3)
                ai_component = BasicMonster()
                monster = Entity(x, y, 'o', colors.get(
                    'desaturated_green'), 'Orc', blocks=True, render_order=RenderOrder.ACTOR,
                                 humanoid=humanoid_component, fighter=fighter_component, ai=ai_component)
            else:
                humanoid_component = Humanoid(race=Races.Troll, profession=Professions.Monster, level=1)
                fighter_component = Fighter(hp=16, defense=2, power=4)
                ai_component = BasicMonster()
                monster = Entity(x, y, 'T', colors.get(
                    'darker_green'), 'Troll', blocks=True, render_order=RenderOrder.ACTOR, humanoid=humanoid_component,
                                 fighter=fighter_component, ai=ai_component)

            entities.append(monster)

    for i in range(number_of_items):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not any([entity for entity in entities if entity.x == x and entity.y == y]):
            item_component = Item(use_function=heal, amount=4)
            item = Entity(x, y, '!', colors.get('violet'), 'Healing Potion', render_order=RenderOrder.ITEM,
                          item=item_component)

            entities.append(item)


def place_npcs(rooms, entities, colors):
    room = choice(rooms)
    x = randint(room.x1 + 1, room.x2 - 1)
    y = randint(room.y1 + 1, room.y2 - 1)
    humanoid_component = Humanoid(race=Races.Human, profession=Professions.Mage, level=8)
    ai_component = BasicNPC()
    sultan = Entity(x, y, 'H', colors.get(
        'white'), 'Sultan', blocks=True, render_order=RenderOrder.ACTOR, humanoid=humanoid_component,
                    ai=ai_component)
    entities.append(sultan)


def make_map(game_map, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities,
             max_monsters_per_room, max_items_per_room, colors):
    rooms = []
    num_rooms = 0

    for r in range(max_rooms):
        # random width and height
        w = randint(room_min_size, room_max_size)
        h = randint(room_min_size, room_max_size)
        # random position without going out of the boundaries of the map
        x = randint(0, map_width - w - 1)
        y = randint(0, map_height - h - 1)

        # "Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)

        # run through the other rooms and see if they intersect with this one
        for other_room in rooms:
            if new_room.intersect(other_room):
                break
        else:
            # this means there are no intersections, so this room is valid

            # "paint" it to the map's tiles
            create_room(game_map, new_room)

            # center coordinates of  new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                # this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
            else:
                # all rooms after the first:
                # connect it to the previous room with a tunnel

                # center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # flip a coin (random number that is either 0 or 1)
                if randint(0, 1) == 1:
                    # first move horizontally, then vertically
                    create_h_tunnel(game_map, prev_x, new_x, prev_y)
                    create_v_tunnel(game_map, prev_y, new_y, new_x)
                else:
                    # first move vertically, then horizontally
                    create_v_tunnel(game_map, prev_y, new_y, prev_x)
                    create_h_tunnel(game_map, prev_x, new_x, new_y)

            place_entities(new_room, entities, max_monsters_per_room, max_items_per_room, colors)

            # finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    place_npcs(rooms, entities, colors)
