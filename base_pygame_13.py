"""
author: Horst JENS
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download:

based on: http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_4

field of view and exploration
also see http://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds

field of view improving, removing of artifacts:
https://sites.google.com/site/jicenospam/visibilitydetermination

"""
import pygame
import random
# import inspect

import os



# TODO: cursor darf nicht in unerforschte zellen gehen
# TODO diagonal movement for player ? or not allowing diagonal movement for monsters...
# TODO monster speed > 1 tile possible ?

class NaturalWeapon():

    def __init__(self, ):
        # self.number = NaturalWeapon.number
        # NaturalWeapon.number += 1
        # NaturalWeapon.store[self.number] = self
        self.damage_bonus = 0
        self.attack_bonus = 0
        self.defense_bonus = 0

        self.overwrite_parameters()

    def overwrite_parameters(self):
        pass


class Fist(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 0
        self.attack_bonus = 0
        self.defense_bonus = 0


class Kick(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 3
        self.attack_bonus = -2
        self.defense_bonus = 2


class YetiSnowBall(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 1
        self.attack_bonus = 4
        self.defense_bonus = 1


class YetiSlap(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 4
        self.attack_bonus = -1
        self.defense_bonus = 0


class SnakeBite(NaturalWeapon):

    def overwrite_parameters(self):
        self.damage_bonus = 1
        self.attack_bonus = 2
        self.defense_bonus = 2


class WolfBite(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 1
        self.attack_bonus = 2
        self.defense_bonus = 2


class GolemArm(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 2
        self.attack_bonus = 0
        self.defense_bonus = 0


class DragonBite(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 9
        self.attack_bonus = -3
        self.defense_bonus = -3


class DragonClaw(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 2
        self.attack_bonus = -1
        self.defense_bonus = -1


class DragonTail(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 3
        self.attack_bonus = 0
        self.defense_bonus = 0


class FireBreath(NaturalWeapon):
    def overwrite_parameters(self):
        self.damage_bonus = 4
        self.attack_bonus = 3
        self.defense_bonus = -4


def roll(dice, bonus=0, reroll=True):
    """simulate a dice throw, and adding a bonus
       reroll means that if the highest number is rolled,
       one is substracted from the score and
       another roll is added, until a not-hightest number is rolled.
       e.g. 1D6 throws a 6, and re-rolls a 2 -> (6-1)+2= 7"""
    # TODO format-micro-language for aligning the numbers better
    rolls = dice[0]
    sides = dice[1]
    total = 0
    print("------------------------")
    print("rolling {}{}{} + bonus {}".format(rolls, "D" if reroll else "d", sides, bonus))
    print("------------------------")
    i = 0
    verb = "rolls   "
    #for d in range(rolls):
    while True:
        i += 1
        if i > rolls:
            break
        value = random.randint(1, sides)

        if reroll and value == sides:
            total += value - 1
            print("die #{} {} {}  ∑: {} (count as {} and rolls again)".format(i, verb, value, total, value-1 ))

            verb = "re-rolls"
            i -= 1
            continue
        else:
            total += value
            print("die #{} {} {}  ∑: {}".format(i, verb, value, total))
            verb = "rolls   "

    print("=========================")
    print("=result:    {}".format(total))
    print("+bonus:     {}".format(bonus))
    print("=========================")
    print("=total:     {}".format(total + bonus))
    return total + bonus


def minmax(value, lower_limit=-1, upper_limit=1):
    """constrains a value inside two limits"""
    value = max(lower_limit, value)
    value = min(upper_limit, value)
    return value

def randomizer(list_of_chances=[1]):
    """gives back an integer depending on chance.
       e.g. randomizer((.75, 0.15, 0.05, 0.05)) gives in 75% 0, in 15% 1, and in 5% 2 or 3"""
    total = sum(list_of_chances)
    v = random.random() * total  # a value between 0 and total
    edge = 0
    for i, c in enumerate(list_of_chances):
        edge += c
        if v <= edge:
            return i
    else:
        raise SystemError("problem with list of chances:", list_of_chances)


def make_text(text="@", font_color=(255, 0, 255), font_size=48, font_name="mono", bold=True, grid_size=None):
    """returns pygame surface with text and x, y dimensions in pixel
       grid_size must be None or a tuple with positive integers.
       Use grid_size to scale the text to your desired dimension or None to just render it
       You still need to blit the surface.
       Example: text with one char for font_size 48 returns the dimensions 29,49
    """
    myfont = pygame.font.SysFont(font_name, font_size, bold)
    size_x, size_y = myfont.size(text)
    mytext = myfont.render(text, True, font_color)
    mytext = mytext.convert_alpha()  # pygame surface, use for blitting
    if grid_size is not None:
        # TODO error handler if grid_size is not a tuple of positive integers
        mytext = pygame.transform.scale(mytext, grid_size)
        mytext = mytext.convert_alpha()  # pygame surface, use for blitting
        return mytext, (grid_size[0], grid_size[1])

    return mytext, (size_x, size_y)


def write(background, text, x=50, y=150, color=(0, 0, 0),
          font_size=None, font_name="mono", bold=True, origin="topleft"):
    """blit text on a given pygame surface (given as 'background')
       the origin is the alignement of the text surface
    """
    if font_size is None:
        font_size = 24
    font = pygame.font.SysFont(font_name, font_size, bold)
    width, height = font.size(text)
    surface = font.render(text, True, color)

    if origin == "center" or origin == "centercenter":
        background.blit(surface, (x - width // 2, y - height // 2))
    elif origin == "topleft":
        background.blit(surface, (x, y))
    elif origin == "topcenter":
        background.blit(surface, (x - width // 2, y))
    elif origin == "topright":
        background.blit(surface, (x - width, y))
    elif origin == "centerleft":
        background.blit(surface, (x, y - height // 2))
    elif origin == "centerright":
        background.blit(surface, (x - width, y - height // 2))
    elif origin == "bottomleft":
        background.blit(surface, (x, y - height))
    elif origin == "bottomcenter":
        background.blit(surface, (x - width // 2, y))
    elif origin == "bottomright":
        background.blit(surface, (x - width, y - height))


def get_line(start, end):
    """Bresenham's Line Algorithm
       Produces a list of tuples from start and end
       source: http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python
       see also: https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm

       #>>> points1 = get_line((0, 0), (3, 4))
       # >>> points2 = get_line((3, 4), (0, 0))
       #>>> assert(set(points1) == set(points2))
       #>>> print points1
       #[(0, 0), (1, 1), (1, 2), (2, 3), (3, 4)]
       #>>> print points2
       #[(3, 4), (2, 3), (1, 2), (1, 1), (0, 0)]
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True

    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1

    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


class Rect():
    """a rectangle object (room) for the dungeon
       x,y is the topleft coordinate
    """

    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def center(self):
        """returns the center coordinate of a room"""
        center_x = (self.x1 + self.x2) // 2  # TODO: // instead of / ?
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        """returns true if this rectangle intersects with another one"""
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tile():
    """# a tile of the map and its properties
       block_movement means blocking the movement of Monster/Player, like a wall
       block_sight means blocking the field of view
    """

    # number = 0  # "globale" class variable

    def __init__(self, char, block_movement=None, block_sight=None, explored=False):
        # self.number = Tile.number
        # Tile.number += 1 # each tile instance has a unique number
        # generate a number that is mostly 0,but very seldom 1 and very rarely 2 or 3
        # see randomizer
        self.decoration = randomizer((.75, 0.15, 0.05, 0.05))
        self.char = char
        self.block_movement = block_movement
        self.block_sight = block_sight
        self.explored = explored
        # graphic_index is a random number to choose one of several graphical tiles
        #self.graphic_index = random.randint(1, 4)
        # --- some common tiles ---
        if char == "#":  # wall
            self.block_movement = True
            self.block_sight = True
            self.i = random.randint(1, 10)
        elif char == ".":  # floor
            self.block_movement = False
            self.block_sight = False
            # self.i = random.randint(1,10)


class Object():
    """this is a generic dungeon object: the player, a monster, an item, a stair..
       it's always represented by a character (for text representation).
       NOTE: a dungeon tile (wall, floor, water..) is represented by the Tile class
    """

    number = 0  # current object number. is used as a key for the Game.objects dictionary

    def __init__(self, x, y, z=0, char="?", color=None, **kwargs):
        self.number = Object.number
        Object.number += 1
        Game.objects[self.number] = self
        self.x = x
        self.y = y
        self.z = z
        self.hint = None # longer description and hint for panel
        self.image_name = None
        self.char = char
        self.color = color
        self.hitpoints = 1  # objects with 0 or less hitpoints will be deleted
        self.look_direction = 0  # 0 -> looks to left, 1 -> looks to right
        # --- make attributes out of all named arguments. like Object(hp=33) -> self.hp = 33
        for key, arg in kwargs.items():
            setattr(self, key, arg)
        # ---- some default values ----
        if "explored" not in kwargs:
            self.explored = False
        if "stay_visible_once_explored" not in kwargs:
            self.stay_visible_once_explored = False
        # --- child classes can do stuff in the _overwrite() method  without needing their own __init__ method
        self._overwrite()
        # --- update legend ---
        if self.char not in Game.legend:
            Game.legend[self.char] = self.__class__.__name__


    def _overwrite(self):
        pass

    def is_member(self, name):
        """returns True if the instance is a member of the 'name' class or a child of it"""
        class_names = [c.__name__ for c in self.__class__.mro()]  # if c.__name__ != "object"]
        if name in class_names:
            return True
        return False

class Gold(Object):
    """a heap of gold"""

    def _overwrite(self):
        self.color = (200,200,0)
        self.char="*"
        self.value = random.randint(1,100)

class Shop(Object):
    """a shop to trade items"""
    def _overwrite(self):
        self.color= ( 200,200,0)
        self.stay_visible_once_explored = True
        self.char = "$"
        self.hint = "press Space to buy hp"

class Stair(Object):
    """a stair, going upwards < or downwards >"""

    def _overwrite(self):
        self.color = (128, 0, 128)  # violet
        self.stay_visible_once_explored = True
        self.hint = "press PgUp/PgDown to change level"


class Monster(Object):
    """a (moving?) dungeon Monster, like the player, a boss, a NPC..."""

    def _overwrite(self):
        self.aggro = 3
        self.char = "M"
        if self.color is None:
            self.color = (255, 255, 0)

    def ai(self, player):
        """returns dx, dy toward the player (if distance < aggro) or randomly"""
        distance = ((self.x - player.x)**2 + (self.y-player.y)**2)**0.5
        if distance < self.aggro:
            dx = player.x - self.x
            dy = player.y - self.y
            dx = minmax(dx, -1, 1)
            dy = minmax(dy, -1, 1)
        else:
            dx = random.choice((-1,0,1))
            dy = random.choice((-1,0,1))
        try:
            target = Game.dungeon[self.z][self.y + dy][self.x + dx]
        except:
            print("monster trying illegally to leave dungeon")
            return 0, 0
            ##raise SystemError("out of dungeon?", self.x, self.y, self.z)
        if target.block_movement:
            print("monster trying to move into a wall")
            return 0, 0
        print("dx dy", self.__class__.__name__, dx, dy)
        return dx, dy


    def move(self, dx, dy, dz=0):
        if dx > 0:
            self.look_direction = 1
        elif dx < 0:
            self.look_direction = 0
        try:
            target = Game.dungeon[self.z + dz][self.y + dy][self.x + dx]
        except:
            raise SystemError("out of dungeon?", self.x, self.y, self.z)
        # --- check if monsters is trying to run into a wall ---
        if target.block_movement:
            if self.is_member("Player"):
                self.hitpoints -= 1
                Game.log.append("ouch!")  # movement is not possible
            return

        self.x += dx
        self.y += dy
        self.z += dz


class Wolf(Monster):

    def _overwrite(self):
        self.char = "W"
        self.aggro = 5
        self.hitpoints = 30
        self.attack = (2, 6)
        self.defense = (2, 5)
        self.damage = (2, 4)
        self.agility = 0.4
        self.natural_weapons = [WolfBite()]
        self.image_name = "direwolf"


class Snake(Monster):

    def _overwrite(self):
        self.char = "S"
        self.aggro = 2
        self.hitpoints = 20
        self.attack = (2, 4)
        self.defense = (3, 3)
        self.damage = (3, 4)
        self.natural_weapons = [SnakeBite()]
        self.image_name = "snake"


class Yeti(Monster):

    def _overwrite(self):
        self.char = "Y"
        self.aggro = 4
        self.hitpoints = 20
        self.attack = (8, 2)
        self.defense = (4, 3)
        self.damage = (4, 5)
        self.natural_weapons = [YetiSnowBall(), YetiSlap()]
        self.image_name = "yeti"


class Dragon(Monster):

    def _overwrite(self):
        self.char = "D"
        self.aggro = 6
        self.hitpoints = 50
        self.attack = (6, 3)
        self.defense = (6, 3)
        self.damage = (5, 3)
        self.natural_weapons = [DragonBite(), DragonClaw(), DragonTail(), FireBreath()]
        self.image_name = "dragon"


class Player(Monster):

    def _overwrite(self):
        self.char = "@"
        self.color = (0, 0, 255)
        self.hitpoints = 100
        self.hitpoints_max = 100
        self.attack = (3, 6)
        self.defense = (3, 5)
        self.damage = (4, 5)
        self.natural_weapons = [Fist(), Kick()]
        self.items = {}
        self.gold = 100
        self.image_name = "arch-mage"


class Game():
    dungeon = []  # list of list of list. 3D map representation, using text chars. z,y,x ! z=0: first level. z=1: second level etc
    fov_map = []  # field of vie map, only for current level!
    objects = {}  # container for all Object instances in this dungeon
    #legend = {} # fills itself because of class Object's __init__ method
    legend = {"@": "player",
              "#": "wall tile",
              ".": "floor tile",
              ">": "stair down",
              "<": "stair up",
              }
    tiles_x = 0
    tiles_y = 0
    torch_radius = 10
    log = []  # message log
    game_over = False
    cursor_x = 0
    cursor_y = 0
    #friend_image = "arch-mage-idle"
    #foe_image = None

    def __init__(self, tiles_x=80, tiles_y=40):
        Game.tiles_x = tiles_x  # max. width of the level in tiles
        Game.tiles_y = tiles_y  # max. height of the level in tiles, top row is 0, second row is 1 etc.
        # self.checked = set()   # like a list, but without duplicates. for fov calculation
        self.player = Player(x=1, y=1, z=0)
        Game.cursor_x = self.player.x
        Game.cursor_y = self.player.y
        # Monster(2,2,0)
        Wolf(2, 2, 0)
        Snake(3, 3, 0)
        Yeti(4, 4, 0)
        Dragon(5, 5, 0)
        Shop(7,1,0)
        self.log.append("Welcome to the first dungeon level (level 0)!")
        self.log.append("Use cursor keys to move around")
        self.load_level(0, "level001.txt", "data")
        #self.load_level(1, "level002.txt", "data")
        #self.load_level(2, "level003.txt", "data")
        # TODO join create_empty_dungeon_level mit create_rooms_tunnels
        self.create_empty_dungeon_level(tiles_x, tiles_y, filled=True, z=1)  # dungoen is full of walls,
        # carve out some rooms and tunnels in this new dungeon level
        self.create_rooms_and_tunnels(z=1)  # carve out some random rooms and tunnels
        # append empty dungeon level
        self.turn = 1

    def new_turn(self):
        self.turn += 1
        for o in Game.objects.values():
            if o.z == self.player.z and o != self.player and o.hitpoints > 0 and o.is_member("Monster"):
                self.move_monster(o)

    def player_has_new_position(self):
        """called after postion change of player,
        checks if the player can pick up something or stays
        on an interesting tile"""
        myfloor = []
        for o in Game.objects.values():
            if (o.z == self.player.z and o.hitpoints > 0 and
                not o.is_member("Monster") and
                o.x == self.player.x and o.y == self.player.y):
                myfloor.append(o)
        if len(myfloor) > 0:
            for o in myfloor:
                if o.is_member("Gold"):
                    Game.log.append("You found {} gold!".format(o.value))
                    self.player.gold += o.value
                    # kill gold from dungeon
                    del Game.objects[o.number]




    def checkfight(self, x, y, z):
        """wir gehen davon aus dass nur der player schaut (checkt) ob er in ein Monster läuft"""
        #Game.foe_image = None
        for o in Game.objects.values():
            if o == self.player:
                continue
            if o.hitpoints <= 0:
                continue
            if not o.is_member("Monster"):
                continue
            if o.z == z:
                if o.x > self.player.x:
                    o.look_direction = 0
                elif o.x < self.player.x:
                    o.look_direction = 1
            #if o.x == x and o.y == y and o.z == z:
                if o.x == x and o.y == y:
                    # monster should now look toward player
                    #if o.x > self.player.x:
                    #    o.look_direction = 0
                    #elif o.x < self.player.x:
                    #    o.look_direction = 1
                    self.fight(self.player, o)
                    return True
        return False

    def move_player(self, dx=0, dy=0):
        if not self.checkfight(self.player.x +dx, self.player.y + dy, self.player.z):
            self.player.move(dx, dy)
            self.make_fov_map()
            self.player_has_new_position()

    def move_monster(self, m):
        """moves a monster randomly, but not into another monster (or wall etc.).
           starts a fight with player if necessary"""
        dx, dy = m.ai(self.player)
        # ai checked already that the move is legal (inside dungeon and not blocked by wall)
        # now only needed to check i running in another monster or into the player
        for o in Game.objects.values():
            if o.z != self.player.z:
                continue
            if o.hitpoints < 1:
                continue
            if not o.is_member("Monster"):
                continue
            if o.x == m.x + dx and o.y == m.y + dy:
                dx, dy = 0, 0
                if o == self.player:
                    self.fight(m, self.player)
                break
        m.x += dx
        m.y += dy





    def fight(self, a, b):
        self.strike(a, b)
        if b.hitpoints > 0:
            self.strike(b, a)
        # big images
        #if a == self.player:
        #    Game.friend_image = "arch-mage-attack"
        #    if b.image_name is not None:
        #        Game.foe_image = b.image_name + "-attack"
        #elif b == self.player:
        #    Game.friend_image = "arch-mage-defend"
        #    if a.image is not None:
        #        Game.foe_image = a.image_name + "-attack"

    def strike(self, a, b):
        # print("{} strikes at {}".format(a, b))
        # Game.log.append("{} strikes at {}".format(a.__class__.__name__, b.__class__.__name__))
        print("----strike test -----")
        print("{} strikes at {}".format(a.__class__.__name__, b.__class__.__name__))
        wa = random.choice(a.natural_weapons)
        print("{} attacks with {} ".format(a.__class__.__name__, wa.__class__.__name__))
        attack_value = roll(a.attack, wa.attack_bonus)
        wd = random.choice(b.natural_weapons)
        print("{} defense with {} ".format(b.__class__.__name__, wd.__class__.__name__))
        defense_value = roll(b.defense, wd.defense_bonus)
        print(attack_value, defense_value)
        if attack_value > defense_value:
            damage_value = roll(a.damage, wa.damage_bonus)
            b.hitpoints -= damage_value
            # print("{} has {} hitpoints left".format(b.__class__.__name__, b.hitpoints))
        else:
            damage_value = 0
        Game.log.append("{} ({}hp) strikes at {} ({}hp) using {} against {}".format(
            a.__class__.__name__,
            a.hitpoints,
            b.__class__.__name__,
            b.hitpoints,
            wa.__class__.__name__,
            wd.__class__.__name__))
        Game.log.append("{}d{}{}{}={}  vs  {}d{}{}{}={} damage: {} hp ({}d{}{}{}) {} --> has {}hp left".format(
            a.attack[0], a.attack[1], "+" if wa.attack_bonus >= 0 else "", wa.attack_bonus, attack_value,
            b.defense[0], b.defense[1], "+" if wd.defense_bonus >= 0 else "", wd.defense_bonus, defense_value,
            damage_value, a.damage[0], a.damage[1], "+" if wa.damage_bonus >= 0 else "", wa.damage_bonus,
            b.__class__.__name__, b.hitpoints))
        # TODO: damage calculation only if hit occurs, else "no hit"

    def check_player(self):
        if self.player.hitpoints <= 0:
            Game.game_over = True

    def load_level(self, z, name, folder="data"):
        """load a text file and return a list of non-empty lines without newline characters"""
        lines = []
        with open(os.path.join(folder, name), "r") as f:
            for line in f:
                if line.strip() != "":
                    lines.append(line[:-1])  # exclude newline char
        # return lines
        level = []
        for y, line in enumerate(lines):
            row = []
            for x, char in enumerate(line):
                if char == "#" or char == ".":
                    row.append(Tile(char))
                if char == "<" or char == ">":
                    row.append(Tile("."))
                    Stair(x, y, z, char)
                if char == "$":
                    row.append(Tile("."))
                    Shop(x,y,z,char)
                if char == "*":
                    row.append(Tile("."))
                    Gold(x,y,z, char)
            level.append(row)
        try:
            Game.dungeon[z] = level
        except:
            Game.dungeon.append(level)
        print("level loaded:", self.dungeon[z])

    def create_rooms_and_tunnels(self, z=0, room_max_size=10, room_min_size=6, max_rooms=30):
        """carve out some random rooms and connects them by tunnels. player is placed in the first room"""
        rooms = []
        num_rooms = 0
        self.room_max_size = room_max_size
        self.room_min_size = room_min_size
        self.max_rooms = max_rooms

        for r in range(self.max_rooms):
            print("carving out room number {}...".format(r))
            # random width and height
            w = random.randint(self.room_min_size, self.room_max_size)
            h = random.randint(self.room_min_size, self.room_max_size)
            # random topleft position without going out of the boundaries of the map
            x = random.randint(0, Game.tiles_x - w - 1)
            y = random.randint(0, Game.tiles_y - h - 1)
            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)
            # run through the other rooms and see if they intersect with this one
            # failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    # failed = True
                    break
            # if not failed:
            else:  # for loop got through without a break
                # this means there are no intersections, so this room is valid
                # carve out this room!
                self.create_room(new_room, z)
                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    # create tunnel from player position to this room
                    prev_x, prev_y = self.player.x, self.player.y
                else:
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()
                self.create_tunnel(prev_x, prev_y, new_x, new_y, z)
                ### draw a coin (random number that is either 0 or 1)
                ##if random.choice([0,1]) == 1:
                ##    # first move horizontally, then vertically
                ##    self.create_h_tunnel(prev_x, new_x, prev_y, z)
                ##    self.create_v_tunnel(prev_y, new_y, new_x, z)
                ##else:
                ##    # first move vertically, then horizontally
                ##    self.create_v_tunnel(prev_y, new_y, prev_x, z)
                ##    self.create_h_tunnel(prev_x, new_x, new_y, z)
                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1
        # --------- all rooms added. check stairs now -------
        # ---------- stairs up ---------------
        # check if this is level 0, add a single stair up
        if z == 0:
            # place stair up in a random room
            r = random.choice(rooms)
            Stair(r.center()[0], r.center()[1], z, char="<")
        else:
            # collect all stairs down from previous level,
            # make at same position a stair up, carve a tunnel to a random room if necessary
            stairlist = [(o.x, o.y) for o in Game.objects.values() if
                         o.char == ">" and o.z == z - 1 and o.is_member("Stair")]
            print("creating prev stairlist:", stairlist)
            for (x, y) in stairlist:
                if Game.dungeon[z][y][x].char != ".":
                    # carve tunnel to random room center
                    r = random.choice(rooms)
                    self.create_tunnel(x, y, r.center()[0], r.center()[1], z)
                # make a stair!
                Stair(x, y, z, char="<")
        # ------------------ stairs down ----------------
        # select up to 3 random rooms and place a stair down in it's center
        num_stairs = 0
        stairs = random.randint(1, 3)
        print("creating stairs down...")
        while num_stairs < stairs:
            r = random.choice(rooms)
            x, y = r.center()
            # is there already any object at this position?
            objects_here = [o for o in Game.objects.values() if o.z == z and o.x == x and o.y == y]
            if len(objects_here) > 0:
                continue
            Stair(x, y, z, char=">")
            num_stairs += 1
        # -------------create monsters in rooms ------------------
        # print("rooms", rooms)
        for r in rooms:
            if random.random() < 0.66:
                Wolf(random.randint(r.x1 + 1, r.x2 - 1), random.randint(r.y1 + 1, r.y2 - 1), z)

    def ascend(self):
        """go up one dungeon level (or leave the game if already at level 0)"""
        # check if player is staying on a stair up, otherwise cancel
        for o in Game.objects.values():
            if o.is_member("Stair") and o.char=="<" and o.z == self.player.z and o.y == self.player.y and o.x == self.player.x:
                break # all ok, correct stair
        else:
            Game.log.append("You must find a stair up to ascend")
            return
        if self.player.z == 0:
            Game.log.append("You climb back to the surface and leave the dungeon. Good Bye!")
            print(Game.log[-1])
            Game.game_over = True
        else:
            Game.log.append("climbing up one level....")
            self.player.z -= 1
            self.make_fov_map()
            self.player_has_new_position()

    def descend(self):
        """go down one dungeon level. create this level if necessary """
        # first check if staying on a stair down, otherwise return
        for o in Game.objects.values():
            if o.is_member("Stair") and o.char==">" and o.z == self.player.z and o.y == self.player.y and o.x == self.player.x:
                break # all ok, correct stair
        else:
            Game.log.append("You must find a stair down to descend")
            return
        Game.log.append("climbing down one level, deeper into the dungeon...")
        try:
            l = Game.dungeon[self.player.z + 1]
        except:
            Game.log.append("please wait a bit, i must create this level...")
            self.create_empty_dungeon_level(Game.tiles_x, Game.tiles_y,
                                            z=self.player.z + 1)
            self.create_rooms_and_tunnels(z=self.player.z + 1)
        self.player.z += 1
        self.make_fov_map()
        self.player_has_new_position()
        # return True

    def create_empty_dungeon_level(self, max_x, max_y, filled=True, z=0):
        """creates empty dungeon level and append it to Game.dungeon
           if "filled" is False with floor tiles ('.') and an outer wall ('#')
           otherwise all is filled with walls
        """
        # TODO: check max x,y from doors in previous level, randomize level dimension
        # TODO: create tunnel from stair to closest room, not to random room
        floor = []
        for y in range(max_y):
            line = []
            for x in range(max_x):
                if filled:
                    line.append(Tile("#"))  # fill the whole dungeon level with walls
                else:
                    # outer walls only
                    line.append(Tile("#") if y == 0 or y == max_y - 1 or x == 0 or x == max_x - 1 else Tile("."))
            floor.append(line)
        try:
            Game.dungeon[z] = floor
        except:
            Game.dungeon.append(floor)
        # print(Game.dungeon)

    def create_room(self, rect, z=0):
        """needs a rect object and carves a room out of this (z) dungeon level. Each room has a wall"""
        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                # replace the tile at this position with an floor tile
                Game.dungeon[z][y][x] = Tile(".")  # replace whatever tile that was there before with a floor

    def create_h_tunnel(self, x1, x2, y, z=0):
        """create an horizontal tunnel in dungeon level z (filled with floor tiles)"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            Game.dungeon[z][y][x] = Tile(".")  # replace whatever tile that was there before with a floor

    def create_v_tunnel(self, y1, y2, x, z=0):
        """create an vertical tunnel in dungeon level z (filled with floor tiles)"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            Game.dungeon[z][y][x] = Tile(".")  # replace whatever tile that was there before with a floor

    def create_tunnel(self, x1, y1, x2, y2, z=0):
        if random.choice([0, 1]) == 1:
            # first move horizontally, then vertically
            self.create_h_tunnel(x1, x2, y1, z)
            self.create_v_tunnel(y1, y2, x2, z)
        else:
            # first move vertically, then horizontally
            self.create_v_tunnel(y1, y2, x1, z)
            self.create_h_tunnel(x1, x2, y2, z)

    def make_fov_map(self):
        Game.fov_map = []
        # self.checked = set() # clear the set of checked coordinates
        px, py, pz = self.player.x, self.player.y, self.player.z
        # set all tiles to False
        for line in Game.dungeon[pz]:
            row = []
            for tile in line:
                row.append(False)
            Game.fov_map.append(row)
        # set player's tile to visible
        Game.fov_map[py][px] = True
        # get coordinates form player to point at end of torchradius / torchsquare
        endpoints = set()
        for y in range(py - Game.torch_radius, py + Game.torch_radius + 1):
            if y == py - Game.torch_radius or y == py + Game.torch_radius:
                for x in range(px - Game.torch_radius, px + Game.torch_radius + 1):
                    endpoints.add((x, y))
            else:
                endpoints.add((px - Game.torch_radius, y))
                endpoints.add((px + Game.torch_radius, y))
        for coordinate in endpoints:
            # a line of points from the player position to the outer edge of the torchsquare
            points = get_line((px, py), (coordinate[0], coordinate[1]))
            self.calculate_fov_points(points)
        # print(Game.fov_map)
        # ---------- the fov map is now ready to use, but has some ugly artifacts ------------
        # ---------- start post-processing fov map to clean up the artifacts ---
        # -- basic idea: divide the torch-square into 4 equal sub-squares.
        # -- look of a invisible wall is behind (from the player perspective) a visible
        # -- ground floor. if yes, make this wall visible as well.
        # -- see https://sites.google.com/site/jicenospam/visibilitydetermination
        # ------ north-west of player
        for xstart, ystart, xstep, ystep, neighbors in [
            (-Game.torch_radius, -Game.torch_radius, 1, 1, [(0, 1), (1, 0), (1, 1)]),
            (-Game.torch_radius, Game.torch_radius, 1, -1, [(0, -1), (1, 0), (1, -1)]),
            (Game.torch_radius, -Game.torch_radius, -1, 1, [(0, -1), (-1, 0), (-1, -1)]),
            (Game.torch_radius, Game.torch_radius, -1, -1, [(0, 1), (-1, 0), (-1, 1)])]:

            for x in range(px + xstart, px, xstep):
                for y in range(py + ystart, py, ystep):
                    # not even in fov?
                    try:
                        visible = Game.fov_map[y][x]
                    except:
                        continue
                    if visible:
                        continue  # next, i search invisible tiles!
                    # oh, we found an invisble tile! now let's check:
                    # is it a wall?
                    if Game.dungeon[pz][y][x].char != "#":
                        continue  # next, i search walls!
                    # --ok, found an invisible wall.
                    # check south-east neighbors

                    for dx, dy in neighbors:
                        # does neigbor even exist?
                        try:
                            v = Game.fov_map[y + dy][x + dx]
                            t = Game.dungeon[pz][y + dy][x + dx]
                        except:
                            continue
                        # is neighbor a tile AND visible?
                        if t.char == "." and v == True:
                            # ok, found a visible floor tile neighbor. now let's make this wall
                            # visible as well
                            Game.fov_map[y][x] = True
                            break  # other neighbors are irrelevant now

    def calculate_fov_points(self, points):
        """needs a points-list from Bresham's get_line method"""
        for point in points:
            x, y = point[0], point[1]
            # player tile always visible
            if x == self.player.x and y == self.player.y:
                Game.fov_map[y][x] = True  # make this tile visible and move to next point
                continue
            # outside of dungeon level ?
            try:
                tile = Game.dungeon[self.player.z][y][x]
            except:
                continue  # outside of dungeon error
            # outside of torch radius ?
            distance = ((self.player.x - x) ** 2 + (self.player.y - y) ** 2) ** 0.5
            if distance > Game.torch_radius:
                continue

            Game.fov_map[y][x] = True  # make this tile visible
            if tile.block_sight:
                break  # forget the rest


class Cursor():

    def __init__(self):
        self.create_image()

    def create_image(self):
        self.image = pygame.surface.Surface((Viewer.grid_size[0],
                                             Viewer.grid_size[1]))
        c = random.randint(100, 200)
        pygame.draw.rect(self.image, (c, c, c), (0, 0, Viewer.grid_size[0],
                                                 Viewer.grid_size[1]), 3)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()


class Viewer():
    width = 0  # screen x resolution in pixel
    height = 0  # screen y resolution in pixel
    panel_width = 200
    log_height = 100
    grid_size = (32, 32)

    def __init__(self, game, width=640, height=400, grid_size=(32, 32), fps=60, ):
        """Initialize pygame, window, background, font,...
           default arguments """
        self.game = game
        self.fps = fps
        Viewer.grid_size = grid_size  # make global readable
        Viewer.width = width
        Viewer.height = height
        pygame.init()
        # player center in pixel
        self.pcx = (width - Viewer.panel_width) // 2  # set player in the middle of the screen
        self.pcy = (height - Viewer.log_height) // 2
        self.radarblipsize = 4  # pixel
        self.logscreen_fontsize = 15
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        self.playtime = 0.0
        # ------ surfaces for radar, panel and log ----
        # all surfaces are black by default
        self.radarscreen = pygame.surface.Surface((Viewer.panel_width,
                                                   Viewer.panel_width))  # same width and height as panel, sits in topright corner of screen
        self.panelscreen = pygame.surface.Surface((Viewer.panel_width, Viewer.height - Viewer.panel_width))
        self.logscreen = pygame.surface.Surface((Viewer.width - Viewer.panel_width, Viewer.log_height))
        # radar screen center
        self.rcx = Viewer.panel_width // 2
        self.rcy = Viewer.panel_width // 2

        # ------ background images ------
        self.backgroundfilenames = []  # every .jpg or .jpeg file in the folder 'data'
        self.make_background()
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        # ------ create bitmaps for player and dungeon tiles ----
        # print("fontsize dim values")
        # test = make_text("@")
        self.images = {}
        #self.load_images()
        self.create_tiles()
        self.wall_and_floor_theme()
        self.cursor = Cursor()
        self.run()

    def load_images(self):
        """single images. char looks to the right by default?"""
        #self.images["arch-mage-attack"] = pygame.image.load(
        #    os.path.join("data", "arch-mage-attack.png")).convert_alpha()
        #self.images["arch-mage-defend"] = pygame.image.load(
        #    os.path.join("data", "arch-mage-defend.png")).convert_alpha()
        #self.images["arch-mage-idle"] = pygame.image.load(os.path.join("data", "arch-mage-idle.png")).convert_alpha()
        #self.images["direwolf-attack"] = pygame.image.load(os.path.join("data", "direwolf-attack.png")).convert_alpha()
        #self.images["direwolf-defend"] = pygame.image.load(os.path.join("data", "direwolf-defend.png")).convert_alpha()
        #self.images["direwolf-idle"] = pygame.image.load(os.path.join("data", "direwolf-idle.png")).convert_alpha()
        #self.images["snake-attack"] = pygame.image.load(os.path.join("data", "snake-attack.png")).convert_alpha()
        #self.images["snake-defend"] = pygame.image.load(os.path.join("data", "snake-defend.png")).convert_alpha()
        #self.images["snake-idle"] = pygame.image.load(os.path.join("data", "snake-idle.png")).convert_alpha()
        #self.images["yeti-attack"] = pygame.image.load(os.path.join("data", "yeti-attack.png")).convert_alpha()
        #self.images["yeti-defend"] = pygame.image.load(os.path.join("data", "yeti-defend.png")).convert_alpha()
        #self.images["yeti-idle"] = pygame.image.load(os.path.join("data", "yeti-idle.png")).convert_alpha()
        #self.images["dragon-attack"] = pygame.image.load(os.path.join("data", "yeti-attack.png")).convert_alpha()
        #self.images["dragon-defend"] = pygame.image.load(os.path.join("data", "yeti-defend.png")).convert_alpha()
        #self.images["dragon-idle"] = pygame.image.load(os.path.join("data", "yeti-idle.png")).convert_alpha()

    def move_cursor(self, dx=0, dy=0):
        """moves the cursor dx, dy tiles away from the current position"""
        target_x, target_y = self.game.player.x + Game.cursor_x + dx, self.game.player.y + Game.cursor_y + dy
        # check if the target tile is inside the current level dimensions
        level_width = len(Game.dungeon[self.game.player.z][0])
        level_height = len(Game.dungeon[self.game.player.z])
        print("level dimension in tiles:", level_width, level_height, Game.cursor_x, Game.cursor_y, dx, dy)
        if target_x < 0 or target_y < 0 or target_x >= level_width or target_y >= level_height:
            return  # cursor can not move outside of the current level
        # check if the target tile is outside the current game window
        x = self.pcx + (Game.cursor_x + dx) * self.grid_size[0]
        y = self.pcy + (Game.cursor_y + dy) * self.grid_size[1]
        if x < 0 or y < 0 or x > (self.width - self.panel_width) or y > (self.height - self.log_height):
            return  # cursor can not move outside of the game window
        # ---- finally, move the cursor ---
        Game.cursor_x += dx
        Game.cursor_y += dy
        # self.screen.blit(self.background, (0, 0))

    def make_background(self):
        """scans the subfolder 'data' for .jpg files, randomly selects
        one of those as background image. If no files are found, makes a
        white screen"""
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:].lower() == ".jpg" or file[-5:].lower() == ".jpeg":
                        self.backgroundfilenames.append(os.path.join(root, file))
            random.shuffle(self.backgroundfilenames)  # remix sort order
            self.background = pygame.image.load(self.backgroundfilenames[0])

        except:
            print("no folder 'data' or no jpg files in it")
            self.background = pygame.Surface(self.screen.get_size()).convert()
            self.background.fill((255, 255, 255))  # fill background white

        self.background = pygame.transform.scale(self.background,
                                                 (Viewer.width, Viewer.height))
        self.background.convert()

    def create_tiles(self):
        """load tilemap images and create tiles for blitting"""

        player_img = pygame.image.load(
            os.path.join("data", "player.png"))  # spritesheed, mostly 32x32, figures looking to the left
        player_img.convert_alpha()
        self.walls_img = pygame.image.load(os.path.join("data", "wall.png"))  # spritesheet 32x32 pixel
        self.floors_img = pygame.image.load(os.path.join("data", "floor.png"))  # spritesheet 32x32 pixel
        self.walls_dark_img = self.walls_img.copy()
        self.floors_dark_img = self.floors_img.copy()
        feats_img = pygame.image.load(os.path.join("data", "feat.png"))
        feats_dark_img = feats_img.copy()
        main_img = pygame.image.load(os.path.join("data", "main.png"))
        main_dark_img = main_img.copy()
        # blit a darker picture over the original to darken
        darken_percent = .50
        for (original, copy) in [(self.walls_img, self.walls_dark_img), (self.floors_img, self.floors_dark_img),
                                 (feats_img, feats_dark_img), (main_img, main_dark_img)]:
            dark = pygame.surface.Surface(original.get_size()).convert_alpha()
            dark.fill((0, 0, 0, darken_percent * 255))
            copy.blit(dark, (0, 0))  # blit dark surface over original

        # ---- tiles for Monsters are tuples. first item looks to the left, second item looks to the right
        # self.wolf_tile = make_text("W", font_color=(100, 100, 100), grid_size=self.grid_size)[0]
        self.wolf_tile = pygame.Surface.subsurface(player_img, (823, 607, 32, 32))
        self.wolf_tile_r = pygame.transform.flip(self.wolf_tile, True, False)
        self.wolf_tiles = (self.wolf_tile, self.wolf_tile_r)
        ##self.snake_tile = make_text("S", font_color=(0, 200, 0), grid_size=self.grid_size)[0]
        #                                                        x y breit höhe
        self.snake_tile = pygame.Surface.subsurface(player_img, (256, 894, 32, 28))
        self.snake_tile_r = pygame.transform.flip(self.snake_tile, True, False)
        self.snake_tiles = (self.snake_tile, self.snake_tile_r)
        # dragon
        self.dragon_tile = pygame.Surface.subsurface(player_img, (747, 559, 33, 49))
        self.dragon_tile_r = pygame.transform.flip(self.dragon_tile, True, False)
        self.dragon_tiles = (self.dragon_tile, self.dragon_tile_r)
        self.monster_tile = make_text("M", font_color=(139, 105, 20), grid_size=self.grid_size)[0]
        self.monster_tiles = (self.monster_tile, self.monster_tile)
        ##self.player_tile = make_text("@", font_color=self.game.player.color, grid_size=self.grid_size)[0]
        self.player_tile = pygame.Surface.subsurface(player_img, (153, 1087, 27, 33))
        self.player_tile_r = pygame.transform.flip(self.player_tile, True, False)
        self.player_tiles = (self.player_tile, self.player_tile_r)
        ##self.floor_tile_dark = make_text(".", font_color=(50, 50, 150), grid_size=self.grid_size)[0]
        ##self.floor_tile_light = make_text(".", font_color=(200, 180, 50), grid_size=self.grid_size)[0]
        # self.floor_tile_dark = self.darkfloors[0]
        # self.floor_tile_light = self.lightfloors[0]
        # self.yeti_tile = make_text("Y", font_color=(200, 180, 50), grid_size=self.grid_size)[0]
        self.yeti_tile = pygame.Surface.subsurface(player_img, (193, 1279, 32, 32))
        self.yeti_tile_r = pygame.transform.flip(self.yeti_tile, True, False)
        self.yeti_tiles = (self.yeti_tile, self.yeti_tile_r)
        ##self.floor_tile_dark = self.darkfloors[4*32+0]
        ##self.floor_tile_light = self.lightfloors[4*32+0]
        # self.wall_tile_dark = make_text("#", font_color=(0, 0, 100), grid_size=self.grid_size)[0]
        # self.wall_tile_dark = self.darkwalls[0]   # 0
        # self.wall_tile_light = make_text("#", font_color=(200, 180, 50), grid_size=self.grid_size)[0]
        # self.wall_tile_light = self.lightwalls[0]  # 0
        self.unknown_tile = make_text(" ", font_color=(14, 14, 14), grid_size=self.grid_size)[0]
        #self.stair_up_tile = make_text("<", font_color=(128, 0, 128), grid_size=self.grid_size)[0]

        ##self.stair_up_tile = self.lightfeats[5*35+2]
        ### stair tiles: index 0 -> light tile, index 1 -> dark tile
        self.stair_up_tiles =  ( pygame.Surface.subsurface(feats_img, (32,192,32,32)),
                                 pygame.Surface.subsurface(feats_dark_img, (32, 192, 32, 32)) )
        #self.stair_up_tile_dark = pygame.Surface.subsurface(feats_dark_img, (32,192,32,32))
        ##self.stair_down_tile = make_text(">", font_color=(128, 255, 128), grid_size=self.grid_size)[0]
        ### stair tiles: index 0 -> light tile, index 1 -> dark tile
        self.stair_down_tiles = ( pygame.Surface.subsurface(feats_img, (0,192,32,32)) ,
                                  pygame.Surface.subsurface(feats_dark_img, (0, 192, 32, 32)) )
        #self.stair_down_tile_dark = pygame.Surface.subsurface(feats_dark_img, (0,192,32,32))

        self.shop_tiles = ( pygame.Surface.subsurface(feats_img,      (439, 192, 32, 32)) ,
                            pygame.Surface.subsurface(feats_dark_img, (439, 192, 32, 32)) )
        self.gold_tiles = ( pygame.Surface.subsurface(main_img,       (207, 655, 26, 20)),
                            pygame.Surface.subsurface(main_dark_img,  (207, 655, 26, 20)) )





        self.legend = {"@": self.player_tiles,
                       " ": self.unknown_tile,
                       "<": self.stair_up_tiles,
                       ">": self.stair_down_tiles,
                       "$": self.shop_tiles,
                       "M": self.monster_tiles,
                       "W": self.wolf_tiles,
                       "S": self.snake_tiles,
                       "Y": self.yeti_tiles,
                       "D": self.dragon_tiles,
                       "*": self.gold_tiles,

                       }  # rest of legend in wall_and_floor_theme

    def wall_and_floor_theme(self):
        """select a set of floor/walltiles, depending on level number (z)"""
        # floors: x(topleft), y(topleft), how many elements
        floors = [(25, 225, 4),
                  (55, 257, 4),
                  (55, 288, 4)]
        # walls: x(topleft), y(topleft), how many elements
        walls = [(0, 0, 4),
                 (0, 65, 8),
                 (0, 225, 4),
                 (127, 255, 4)]
        # ---- add single subimages to darkwalls and lightwalls---
        # x1,y1, x2,y2: 0,225, 32 , 256
        # see class floor, attribute decoration for probability. first img comes most often
        self.darkwalls = []
        self.lightwalls = []
        for (x, y) in ((0, 255), (32, 255), (64, 255), (96, 255)):
            self.lightwalls.append(pygame.Surface.subsurface(self.walls_img, (x, y, 32, 32)))
            self.darkwalls.append(pygame.Surface.subsurface(self.walls_dark_img, (x, y, 32, 32)))
        self.darkfloors = []
        self.lightfloors = []
        for (x, y) in ((0, 352), (32, 352), (64, 352), (96, 352)):
            self.lightfloors.append(pygame.Surface.subsurface(self.floors_img, (x, y, 32, 32)))
            self.darkfloors.append(pygame.Surface.subsurface(self.floors_dark_img, (x, y, 32, 32)))
        # now set the legend for this level!
        self.legend["."] = self.lightfloors
        self.legend["#"] = self.lightwalls
        self.legend[":"] = self.darkfloors,
        self.legend["X"] = self.darkwalls,

    def tile_blit(self, surface, x_pos, y_pos, corr_x=0, corr_y=0):
        """correctly blits a surface at tile-position x,y, so that the player is always centered at pcx, pcy"""
        x = (x_pos - self.game.player.x) * self.grid_size[0] + self.pcx + corr_x
        y = (y_pos - self.game.player.y) * self.grid_size[1] + self.pcy + corr_y
        # check if the tile is inside the game screen, otherwise ignore
        if (x > (Viewer.width - Viewer.panel_width)) or (y > (Viewer.height - Viewer.log_height)):
            return
        if (x + self.grid_size[0]) < 0 or (y + self.grid_size[1]) < 0:
            return


        self.screen.blit(surface, (x, y))

    def draw_dungeon(self):
        z = self.game.player.z
        px, py = self.game.player.x, self.game.player.y
        for y, line in enumerate(Game.dungeon[z]):
            for x, map_tile in enumerate(line):
                distance = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
                # ---- check if tiles is outside torch radius of player ----
                # ---- or otherwise (mostly) invisible
                #print("dist, x, y", distance, x, y)
                if distance > Game.torch_radius or Game.fov_map[y][x] == False:
                    # -- only blit (dark) if tile is explored. only draw explored Items (stairs)
                    if map_tile.explored:
                        if map_tile.char == "#":
                            c = self.darkwalls[map_tile.decoration]
                            # print(map_tile.i)
                            # c = self.darkwalls[map_tile.i]
                        elif map_tile.char == ".":
                            c = self.darkfloors[map_tile.decoration]
                        else:
                            raise SystemError("strange tile in map:", c)
                    else:
                        c = self.unknown_tile
                    # self.screen.blit(c, (x * self.grid_size[0], y * self.grid_size[1]))  # * self.grid_size[0], y * self.grid_size[1]))
                    # self.screen.blit(c, (x * self.grid_size[0], y * self.grid_size[1]))  # * self.grid_size[0], y * self.grid_size[1]))
                    self.tile_blit(c, x, y)
                    # ---- maybe a perma-visible objects lay here ? ---
                    olist = [o for o in Game.objects.values() if
                             o.explored and o.stay_visible_once_explored and o.z == z and o.y == y and o.x == x]
                    for o in olist:
                        #print("blitting....", o.char)
                        #if o.char in "<>":
                        self.tile_blit(self.legend[o.char][1], x, y)
                        #else:
                        #    self.tile_blit(self.legend[o.char], x, y)
                    continue  # next tile, please
                # ==============================================
                # ---- we are inside the torch radius ---
                # ---- AND we are visible! ----
                # explore if this tile is not yet explored
                if not map_tile.explored:
                    map_tile.explored = True
                # --- blit dungeon tile ----
                # TODO: option to skip blitting dungeon tile if Monster or object is here
                # print(self.game.player.z, map_tile.char)
                c = self.legend[map_tile.char][map_tile.decoration]  # light tiles
                # self.screen.blit(c, (x * self.grid_size[0], y * self.grid_size[1]))
                # self.screen.blit(c, (x * self.grid_size[0], y * self.grid_size[1]))
                self.tile_blit(c, x, y)  # first, blit the dungeon tile
                self.draw_non_monsters(x, y)  # then, blit any items (stairs) on it
                # self.draw_monsters(x, y)  # then, blit any monsters
                # ----- alles nochmal, damit monster größer sein können als tiles ohne abgeschnitten zu werden

        for y, line in enumerate(Game.dungeon[z]):
            for x, map_tile in enumerate(line):
                if Game.fov_map[y][x]:
                    self.draw_monsters(x, y)  # then, blit any monsters

    def draw_non_monsters(self, x, y):
        """inside sight radius and explored"""
        z = self.game.player.z
        for o in Game.objects.values():
            if o.z == z and o.y == y and o.x == x:  # only care if in the correct dungeon level
                # -- only care if NOT: Monster class instances or instances that are a child of the Monster class
                if not o.is_member("Monster"):
                    #if o.char in "<>$*": # TODO check if tuple instead surface
                        c=self.legend[o.char][0] # light tile
                    #else:
                    #    print("ALAAAAAAAAAAAAAAARRRRRMMM")
                    #    c = self.legend[o.char]
                    #print("c = ", c, o.char)
                        o.explored = True   # redundant ?
                    # self.screen.blit(c, (m.x * self.grid_size[0], m.y * self.grid_size[1]))
                        self.tile_blit(c, o.x, o.y)

    def draw_monsters(self, x, y):
        z = self.game.player.z
        for o in Game.objects.values():
            if o.z == z and o.y == y and o.x == x:  # only care if in the correct dungeon level
                # -- only care for Monster class instances or instances that are a child of the Monster class --
                if o.is_member("Monster") and o.hitpoints > 0:
                    c = self.legend[o.char][o.look_direction]  # looks left or right
                    # self.screen.blit(c, (o.x * self.grid_size[0], o.y * self.grid_size[1]))
                    # correction so that if monster surface != size of tile surface monster is centered on tile
                    corr_x, corr_y = 0, 0
                    if c.get_size() != self.grid_size:
                        corr_x = (self.grid_size[0] - c.get_size()[0])//2
                        corr_y = (self.grid_size[1] - c.get_size()[1])//2


                    if o == self.game.player:
                        self.screen.blit(c, (self.pcx+corr_x, self.pcy+corr_y))  # blit the player always in middle of screen
                    else:
                        o.explored = True
                        self.tile_blit(c, o.x, o.y, corr_x, corr_y)
                    break  # one monster per tile is enough

    def draw_radar(self):
        # make black square in top of panel
        self.radarscreen.fill((10, 10, 10))  # clear radarscreen
        delta_tiles = int(self.panel_width / 2 // self.radarblipsize)
        # make a radar blit for each explored dungeong tile
        for x in range(self.game.player.x - delta_tiles, self.game.player.x + delta_tiles + 1):
            if x < 0:
                continue
            for y in range(self.game.player.y - delta_tiles, self.game.player.y + delta_tiles + 1):
                if y < 0:
                    continue
                try:
                    t = Game.dungeon[self.game.player.z][y][x]
                except:
                    continue
                if t.explored:
                    if t.block_movement:
                        color = (50, 50, 250)  # blue wall
                    else:
                        color = (150, 150, 150)  # light grey corridor
                    dx = -(x - self.game.player.x) * self.radarblipsize
                    dy = -(y - self.game.player.y) * self.radarblipsize
                    pygame.draw.rect(self.radarscreen, color,
                                     (self.rcx - dx, self.rcy - dy, self.radarblipsize, self.radarblipsize))
                # ---if a stair is there, paint it (if explored) ---
                for o in Game.objects.values():
                    if o.z == self.game.player.z and o.y == y and o.x == x and o.is_member("Stair") and o.explored:
                        if o.char == ">":
                            color = (128, 255, 128)
                        else:
                            color = (128, 0, 128)
                        pygame.draw.rect(self.radarscreen, color,
                                         (self.rcx - dx, self.rcy - dy, self.radarblipsize, self.radarblipsize))
        # make withe glowing dot at center of radarmap
        white = random.randint(200, 255)
        color = (white, white, white)
        pygame.draw.rect(self.radarscreen, color, (self.rcx, self.rcy, self.radarblipsize, self.radarblipsize))
        # blit radarscreen on screen
        self.screen.blit(self.radarscreen, (Viewer.width - Viewer.panel_width, 0))

    def draw_panel(self):
        # fill panelscreen with color
        self.panelscreen.fill((64, 128, 64))
        # write stuff in the panel
        # -y5------------
        write(self.panelscreen, text="dungeon: {}".format(self.game.player.z), x=5, y=5, color=(255, 255, 255))
        # cheering = ["go, Hero, go!",
        #            "come on, man!",
        #            "Yeah!", "That's cool!"]
        # write(self.panelscreen, text=random.choice(cheering),
        #        x=5, y=25)
        # - hitpoint bar in red, starting left
        pygame.draw.rect(self.panelscreen, (200, 0, 0),
                         (0, 35, self.game.player.hitpoints * Viewer.panel_width / self.game.player.hitpoints_max, 28))
        # -y35--------------------
        write(self.panelscreen, text="hp: {}/{}".format(
            self.game.player.hitpoints, self.game.player.hitpoints_max), x=5, y=35,
              color=(255, 255, 255), font_size=24)
        # -y65 ----------------------
        write(self.panelscreen, text="Gold: {}".format(
              self.game.player.gold), x=5, y=65, color=(255, 255, 0), font_size=24)

        # --- write cursor information into panel ---
        # - y95 ------

        tilex, tiley = self.game.player.x + Game.cursor_x, self.game.player.y + Game.cursor_y
        t = Game.dungeon[self.game.player.z][tiley][tilex]
        write(self.panelscreen, text="x:{} y:{} turn:{}".format(tilex, tiley, self.game.turn), x=5, y=95, color=(255, 255, 255),
              font_size=16)
        # tile information
        # - y115
        write(self.panelscreen, text=Game.legend[t.char] if t.explored else "not yet explored", x=5, y=115,
              color=(255, 255, 255), font_size=16)
        # objects on top of that tile ?
        here = []
        hints = []
        for o in Game.objects.values():
            # print("object:",o)
            if o.z == self.game.player.z and o.x == tilex and o.y == tiley and o.hitpoints > 0:
                here.append(o)
                if o.hint is not None:
                    hints.append(o.hint)
        # print(here)
        dy = 0
        for dy, thing in enumerate(here):
            # -y135 + 20*dy
            # TODO: blit text in variable fontsize/panel width with word wrap
            write(self.panelscreen, text=Game.legend[thing.char], x=5, y=135 + 20 * dy, color=(255, 255, 255),
                  font_size=16)

        # --- print hints ----
        y = 135 + 20 * dy + 50
        for h in hints:
            write(self.panelscreen, text=h, x=5, y=y, color=(0,0,0), font_size=10)
            y += 20

        # blit panelscreen
        # ----- friend and foe ----
        #self.panelscreen.blit(self.images[Game.friend_image], (10, 400))
        #if Game.foe_image is not None:
        #    self.panelscreen.blit(self.images[Game.foe_image], (100, 400))#

        self.screen.blit(self.panelscreen, (Viewer.width - self.panel_width, self.panel_width))

    def draw_log(self):
        # fill logscreen with color
        self.logscreen.fill((150, 150, 150))

        # write the log lines, from bottom (last log line) to top.
        for i in range(-1, -25, -1):  # start, stop, step
            try:
                text = "{}: {}".format(len(Game.log) + i, Game.log[i])
                c = (0, 0, 0) if (len(Game.log) + i) % 2 == 0 else (87, 65, 0)
            except:
                continue
            # ungerade und gerade Zeilennummern sollen verschiedenen
            # farben haben

            textsf, (w, h) = make_text(text, font_color=c,
                                       font_size=self.logscreen_fontsize)
            self.logscreen.blit(textsf, (5, self.log_height + i * h))
        # ---- blit logscreen ------
        self.screen.blit(self.logscreen, (0, Viewer.height - self.log_height))

    def new_turn(self):
        """new turn in Viewer, calls new turn in Game and updates graphics that may have changed, plays animations etc"""
        self.game.new_turn()
        self.redraw = True
        #self.redraw = True

    def run(self):
        """The mainloop"""
        running = True
        pygame.mouse.set_visible(True)
        oldleft, oldmiddle, oldright = False, False, False
        self.game.make_fov_map()
        self.redraw = True
        # exittime = 0
        old_z = 999  # old z position of player
        show_range = False
        animation = 0
        reset_cursor = True
        while running:

            self.game.check_player()
            if Game.game_over:
                running = False
            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000
            # --- redraw whole screen if animation has ended ----
            if animation > self.playtime and animation < (self.playtime + seconds):
                self.redraw = True

            self.playtime += seconds
            # --- check if the player has changed the dungeon level
            #if old_z != self.game.player.z:
            #    recalculate_fov = True
            #else:
            #    recalculate_fov = False
            old_z = self.game.player.z
            # ---------animation -------
            if animation > self.playtime:
                # --- draw laser beam -----
                c = (0, 0, random.randint(10, 250))
                w = random.randint(1, 4)
                d = 8  # distance from corner of grid toward center for laser start points
                startpoints = [(d, d),
                               (self.grid_size[0] - d, d),
                               (d, self.grid_size[1] - d),
                               (self.grid_size[0] - d, self.grid_size[1] - d)]
                for x, y in startpoints:
                    pygame.draw.line(self.screen, c,
                                     (self.pcx + x, self.pcy + y),
                                     (self.pcx + self.grid_size[0] // 2 + lasertarget[0] * self.grid_size[0],
                                      self.pcy + self.grid_size[1] // 2 + lasertarget[1] * self.grid_size[1]),
                                     w)

                pygame.display.flip()
                self.screen.blit(self.background, (0, 0))
                # --- order of drawing (back to front) ---
                self.draw_dungeon()
                self.draw_radar()
                self.draw_panel()
                self.draw_log()
                continue
            # self.oldscreen = self.screen
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # ---- move the game cursor with wasd ----
                    if event.key == pygame.K_a:
                        self.move_cursor(-1, 0)
                        self.redraw = True
                        reset_cursor = False
                        # Game.cursor_x -= 1
                    if event.key == pygame.K_d:
                        self.move_cursor(1, 0)
                        self.redraw = True
                        reset_cursor = False

                        # Game.cursor_x += 1
                    if event.key == pygame.K_w:
                        self.move_cursor(0, -1)
                        self.redraw = True
                        reset_cursor = False

                        # Game.cursor_y -= 1
                    if event.key == pygame.K_s:
                        self.move_cursor(0, 1)
                        self.redraw = True
                        reset_cursor = False

                        # Game.cursor_y += 1
                    # ---- shoot laser beam to cursor -----
                    if event.key == pygame.K_1:
                        # laser = 1
                        lasertarget = (Game.cursor_x, Game.cursor_y)
                        animation = self.playtime + 1
                    # ---- -simple player movement with cursor keys -------
                    if event.key == pygame.K_RIGHT:
                        self.new_turn()
                        recalculate_fov = True
                        self.game.move_player(1, 0)
                        #if not self.game.checkfight(self.game.player.x + 1, self.game.player.y, self.game.player.z):
                        #    self.game.player.move(1, 0)

                    if event.key == pygame.K_LEFT:
                        #Game.turn += 1
                        self.new_turn()
                        recalculate_fov = True
                        self.game.move_player(-1,0)
                        #if not self.game.checkfight(self.game.player.x - 1, self.game.player.y, self.game.player.z):
                        #    self.game.player.move(-1, 0)

                    if event.key == pygame.K_UP:
                        #Game.turn += 1
                        self.new_turn()
                        recalculate_fov = True
                        self.game.move_player(0,-1)
                        #if not self.game.checkfight(self.game.player.x, self.game.player.y - 1, self.game.player.z):
                        #    self.game.player.move(0, -1)
                            # recalculate_fov = True
                    if event.key == pygame.K_DOWN:
                        #Game.turn += 1
                        self.new_turn()
                        recalculate_fov = True
                        self.game.move_player(0,1)
                        #print("redraw after move", self.redraw)
                        #if not self.game.checkfight(self.game.player.x, self.game.player.y + 1, self.game.player.z):
                        #    self.game.player.move(0, 1)
                            # recalculate_fov = True
                    if event.key == pygame.K_SPACE:
                        #Game.turn += 1  # wait a turn
                        self.new_turn()
                        # wenn auf shop buy one hp for one gold
                        for o in Game.objects.values():
                            if (o.z == self.game.player.z and
                                o.x == self.game.player.x and
                                o.y == self.game.player.y and
                                self.game.player.gold > 0 and
                                o.__class__.__name__=="Shop"):
                                self.game.player.gold -= 1
                                self.game.player.hitpoints += 1

                        self.redraw = True
                    if event.key == pygame.K_PAGEUP:
                        self.new_turn()
                        # go up a level
                        self.game.ascend()
                        self.redraw = True
                    if event.key == pygame.K_PAGEDOWN:
                        self.new_turn()
                        self.game.descend()
                        self.redraw = True

                    if event.key == pygame.K_r:
                        # zoom out radar
                        self.radarblipsize *= 0.5
                        self.radarblipsize = int(max(1, self.radarblipsize))  # don't become zero
                        print("radarblip:", self.radarblipsize)

                        self.redraw = True
                    if event.key == pygame.K_t:
                        # zoom in radar
                        self.radarblipsize *= 2
                        self.radarblipsize = min(64, self.radarblipsize)  # don't become absurd large
                        self.redraw = True
                    # --- increase torch radius ---
                    if event.key == pygame.K_PLUS:
                        Game.torch_radius += 1
                        #recalculate_fov = True
                        self.game.make_fov_map()
                        self.redraw = True
                    # --- decrease torch radius ----
                    if event.key == pygame.K_MINUS:
                        Game.torch_radius -= 1
                        #recalculate_fov = True
                        self.game.make_fov_map()
                        self.redraw = True

            # ============== draw screen =================
            #if recalculate_fov:
            #    self.redraw = True
            #    self.game.make_fov_map()

            if self.redraw:
                if reset_cursor:
                    Game.cursor_x, Game.cursor_y = 0, 0
                reset_cursor = True
                # delete everything on screen
                self.screen.blit(self.background, (0, 0))
                # --- order of drawing (back to front) ---
                self.draw_dungeon()

                self.draw_radar()
                # self.draw_panel()
            self.draw_log()
            ##for i in range(32):
            ##    print("i", i, i * 32)
            ##    self.screen.blit(self.lightfloors[i+320], (i * 32, 0))
            ##    self.screen.blit(self.darkfloors[i+320], (i * 32, 32))
            ##    self.screen.blit(self.lightwalls[i], (i * 32, 64))
            ##    self.screen.blit(self.darkwalls[i], (i * 32, 96))
            # elif Game.cursor_x != 0 or Game.cursor_y != 0:
            #    self.draw_panel()
            self.draw_panel()  # always draw panel

            self.redraw = False

            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()
            if pressed_keys[pygame.K_LSHIFT]:
                show_range = True
            else:
                show_range = False
            # if pressed_keys[pygame.K_SPACE]:
            #    pass

            # ------ mouse handler ------
            left, middle, right = pygame.mouse.get_pressed()
            # if oldleft and not left:
            #    self.launchRocket(pygame.mouse.get_pos())
            oldleft, oldmiddle, oldright = left, middle, right

            # ------ joystick handler -------
            for number, j in enumerate(self.joysticks):
                if number == 0:
                    x = j.get_axis(0)
                    y = j.get_axis(1)
                    buttons = j.get_numbuttons()
                    for b in range(buttons):
                        pushed = j.get_button(b)

            # write text below sprites
            fps_text = "FPS: {:5.3}".format(self.clock.get_fps())
            pygame.draw.rect(self.screen, (64, 255, 64), (Viewer.width - 110, Viewer.height - 20, 110, 20))
            write(self.screen, text=fps_text, origin="bottomright", x=Viewer.width - 2, y=Viewer.height - 2,
                  font_size=16, bold=True, color=(0, 0, 0))

            if show_range:
                pygame.draw.circle(self.screen, (200, 0, 0),
                                   (self.pcx, self.pcy),
                                   Game.torch_radius * self.grid_size[0], 1)
            # ------ Cursor -----
            self.cursor.create_image()
            if Game.cursor_y != 0 or Game.cursor_x != 0:
                self.screen.blit(self.cursor.image, (
                    self.pcx + Game.cursor_x * self.grid_size[0],
                    self.pcy + Game.cursor_y * self.grid_size[1]))
            # -------- next frame -------------
            pygame.display.flip()
        # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()


if __name__ == '__main__':
    g = Game(tiles_x=80, tiles_y=40)
    Viewer(g, width=1200, height=800, grid_size=(32, 32))  # , (35,35))
