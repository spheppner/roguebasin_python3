"""
author: Horst JENS
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download:

based on: http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_4

field of view and exploration
also
see http://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds

field of view improving, removing of artifacts:
https://sites.google.com/site/jicenospam/visibilitydetermination

"""
import pygame
import random
# import inspect

import os

# declare constants
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


#  TODO monster speed > 1 tile possible ?
#  TODO rework NaturalWeapon
#  TODO Item
#  TODO Equipment
#  TODO Consumable


class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {}  # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        self._overwrite_parameters()
        pygame.sprite.Sprite.__init__(self, self.groups)  # call parent class. NEVER FORGET !
        self.number = VectorSprite.number  # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        self.create_image()
        self.distance_traveled = 0  # in pixel
        self.rect.center = (-300, -300)  # avoid blinking image in topleft corner
        if self.angle != 0:
            self.set_angle(self.angle)

    def _overwrite_parameters(self):
        """change parameters before create_image is called"""
        pass

    def _default_parameters(self, **kwargs):
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        # if "static" not in kwargs:
        #    self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(150, 150)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(0, 0)
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "color" not in kwargs:
            # self.color = None
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        # if "hitpoints" not in kwargs:
        #    self.hitpoints = 100
        # self.hitpointsfull = self.hitpoints # makes a copy
        # if "mass" not in kwargs:
        #    self.mass = 10
        # if "damage" not in kwargs:
        #    self.damage = 10
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0  # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0  # age in seconds

    def kill(self):
        if self.number in self.numbers:
            del VectorSprite.numbers[self.number]  # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((self.color))
        # self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        # position and move are pygame.math.Vector2 objects
        # ----- kill because... ------
        # if self.hitpoints <= 0:
        #    self.kill()
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss:
                boss = VectorSprite.numbers[self.bossnumber]
                # self.pos = v.Vec2d(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(boss.pos.x, boss.pos.y)
        self.pos += self.move * seconds
        self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        self.wallbounce()
        self.rect.center = (round(self.pos.x, 0), round(self.pos.y, 0))

    def wallbounce(self):
        # ---- bounce / kill on screen edge ----
        # ------- left edge ----
        if self.pos.x < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = 0
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = Viewer.width
        # -------- upper edge -----
        if self.pos.y < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = 0
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = Viewer.height
        # -------- right edge -----
        if self.pos.x > Viewer.width:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = Viewer.width
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = 0
        # --------- lower edge ------------
        if self.pos.y > Viewer.height:
            if self.kill_on_edge:
                self.hitpoints = 0
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = Viewer.height
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = 0



class Flytext(VectorSprite):
    def __init__(self, text, fontsize=22, acceleration_factor=1.02, max_speed=300, **kwargs):
        """a text flying upward and for a short time and disappearing"""

        VectorSprite.__init__(self, **kwargs)
        ##self._layer = 7  # order of sprite layers (before / behind other sprites)
        ##pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.acceleartion_factor = acceleration_factor
        self.max_speed = max_speed
        self.kill_on_edge = True
        self.image = make_text(self.text, self.color, fontsize)[0]  # font 22
        self.rect = self.image.get_rect()

    def update(self, seconds):
        self.move *= self.acceleartion_factor
        if self.move.length() > self.max_speed:
            self.move.normalize_ip()
            self.move *= self.max_speed
        VectorSprite.update(self, seconds)

class FlyingObject(VectorSprite):
    image = None  # will be set from Viewer.create_tiles

    def _overwrite_parameters(self):

        self.move = pygame.math.Vector2(self.endpos[0] - self.startpos[0], self.endpos[1] - self.startpos[1])
        self.picture = self.image
        self.create_image()
        distance = self.max_distance = self.move.length()
        if distance > 0:
            self.move.normalize_ip()  # reduce to lenght 1
        else:
            self.max_age = 0  # kill this arrow as soon as possible
        self.move *= self.speed  #
        self.duration = distance / self.speed  # in seconds
        # arrow shall start in the middle of tile, not in the topleft corner
        self.pos = pygame.math.Vector2(self.startpos[0] + Viewer.grid_size[0] // 2,
                                       self.startpos[1] + Viewer.grid_size[1] // 2)

        self.set_angle(self.move.angle_to(pygame.math.Vector2(1, 0)))


class ArrowSprite(FlyingObject):
    """ a sprite flying from startpos to endpos with fixed speed
        startpos and endpos are in pixel
    """
    image = None

    def _overwrite_parameters(self):
        self.speed = 150  # pixel / second
        super()._overwrite_parameters()  # FlyingObject


class MagicSprite(FlyingObject):
    """ a sprite flying from startpos to endpos with fixed speed
            startpos and endpos are in pixel
        """
    image = None

    def _overwrite_parameters(self):
        self.speed = 50  # pixel / second
        super()._overwrite_parameters()  # FlyingObject

    def update(self, seconds):
        # rotate image
        self.set_angle(self.angle + 10)
        super().update(seconds)


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


def megaroll(dicestring="1d6 1d20", bonus=0):
    """roll all the dice in the dicestring and adds a bonus to the sum
    1d6 means one 6-sided die without re-roll
    1D6 means one 6-sided die with re-roll.
    re-roll: 1D6 means that when hightest side (6) is rolled, 5 (=6-1) is added and he rolls again"""
    dlist = dicestring.split(" ")
    total = 0
    print("calculating: ", dicestring, "+", bonus)
    for code in dlist:
        print("---processing", code)
        if "d" in code:
            # reroll = False
            rolls = int(code.split("d")[0])
            sides = int(code.split("d")[1])
            total += roll((rolls, sides), bonus=0, reroll=False)
        elif "D" in code:
            # reroll = True
            rolls = int(code.split("D")[0])
            sides = int(code.split("D")[1])
            total += roll((rolls, sides), bonus=0, reroll=True)
        else:
            raise SystemError("unknow dice type: {} use 1d6, 1D20 etc".format(code))
        print("---result of", code, "is :", str(total))
    print("adding " + str(bonus) + "=", str(total + bonus))
    return total + bonus


def roll(dice, bonus=0, reroll=True):
    """simulate a dice throw, and adding a bonus
       reroll means that if the highest number is rolled,
       one is substracted from the score and
       another roll is added, until a not-hightest number is rolled.
       e.g. 1D6 throws a 6, and re-rolls a 2 -> (6-1)+2= 7"""
    # TODO format-micro-language for aligning the numbers better
    # TODO: accepting string of several dice, like '2D6 3d4' where 'd' means no re-roll, 'D' means re-roll
    rolls = dice[0]
    sides = dice[1]
    total = 0
    print("------------------------")
    print("rolling {}{}{} + bonus {}".format(rolls, "D" if reroll else "d", sides, bonus))
    print("------------------------")
    i = 0
    verb = "rolls   "
    # for d in range(rolls):
    while True:
        i += 1
        if i > rolls:
            break
        value = random.randint(1, sides)

        if reroll and value == sides:
            total += value - 1
            print("die #{} {} {}  ∑: {} (count as {} and rolls again)".format(i, verb, value, total, value - 1))
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


def randomizer(list_of_chances=[1.0,]):
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


class Rect:
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
       block_movement means blocking the movement of Monster/Player, like a wall or water
       block_sight means blocking the field of view
       block_flying means the tile blocks flying objects like arrows or flying monsters
    """

    # number = 0  # "globale" class variable

    def __init__(self, char, block_movement=None, block_sight=None, explored=False, block_flying=None):
        # self.number = Tile.number
        # Tile.number += 1 # each tile instance has a unique number
        # generate a number that is mostly 0,but very seldom 1 and very rarely 2 or 3
        # see randomizer
        self.decoration = randomizer((.30, 0.15, 0.15, 0.15, 0.1, 0.1, 0.025, 0.025))  # 8
        self.char = char
        self.block_movement = block_movement
        self.block_sight = block_sight
        self.block_flying = block_flying
        self.explored = explored
        # graphic_index is a random number to choose one of several graphical tiles
        # self.graphic_index = random.randint(1, 4)
        # --- some common tiles ---
        if char == "#":  # wall
            self.block_movement = True
            self.block_flying = True
            self.block_sight = True
            # self.i = random.randint(1, 10)
            # self.decoration = randomizer((.55, 0.25, 0.15, 0.05))
        elif char == ".":  # floor
            self.decoration = randomizer((.15, 0.15, 0.15, 0.15, 0.15, 0.1, 0.1, 0.025, 0.025))  # 9
            self.block_movement = False
            self.block_flying = False
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
        self.hint = None  # longer description and hint for panel
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

    def kill(self):
        # delete this object from Game.objects dictionary
        del Game.objects[self.number]

    def _overwrite(self):
        pass


class Item(Object):
    """an item that you can pick up"""

    def _overwrite(self):
        self.color = (255, 165, 0)  # orange
        self.weight = 0


class Scroll(Item):
    """a scroll with a spell on it"""

    def _overwrite(self):
        super()._overwrite()
        self.color = (200, 200, 0)
        self.char = "i"
        self.hint = "consumable magic scroll "
        self.spell = random.choice(("blink", "blink", "fear", "fear", "bleed", "bleed",
                                    "bleed", "magic map", "magic map", "magic map", "magic map", "magic map",
                                    "magic map",
                                    "magic missile", "magic missile", "magic missile",
                                    "fireball", "fireball", "fireball"))
        # disarm onfuse hurt bleed combat bless defense bless bull strenght dragon strenght superman


class Gold(Item):
    """a heap of gold"""

    def _overwrite(self):
        super()._overwrite()
        self.color = (200, 200, 0)
        self.char = "*"
        self.value = random.randint(1, 100)


class Shop(Object):
    """a shop to trade items"""

    def _overwrite(self):
        self.color = (200, 200, 0)
        self.stay_visible_once_explored = True
        self.char = "$"
        self.hint = "press Space to buy hp"


class Stair(Object):
    """a stair, going upwards < or downwards >"""

    def _overwrite(self):
        self.color = (128, 0, 128)  # violet
        self.stay_visible_once_explored = True
        self.hint = "press < or > to change level"


class Monster(Object):
    """a (moving?) dungeon Monster, like the player, a boss, a NPC..."""

    def _overwrite(self):
        self.aggro = 3
        self.char = "M"
        self.immobile = False
        self.shoot_arrows = False

        if self.color is None:
            self.color = (255, 255, 0)

    def ai(self, player):
        """returns dx, dy toward the player (if distance < aggro) or randomly"""
        if self.immobile:
            return 0, 0
        distance = ((self.x - player.x) ** 2 + (self.y - player.y) ** 2) ** 0.5

        if distance < self.aggro:
            dx = player.x - self.x
            dy = player.y - self.y
            dx = minmax(dx, -1, 1)
            dy = minmax(dy, -1, 1)
        else:
            dx = random.choice((-1, 0, 1))
            dy = random.choice((-1, 0, 1))
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
            if isinstance(self, Player):
                self.hitpoints -= 1
                Game.log.append("ouch!")  # movement is not possible
            return

        self.x += dx
        self.y += dy
        self.z += dz


class Wolf(Monster):

    def _overwrite(self):
        super()._overwrite()
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
        super()._overwrite()
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
        super()._overwrite()
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
        super()._overwrite()
        self.char = "D"
        self.aggro = 6
        self.immobile = True
        self.shoot_arrows = True
        self.arrow_range = random.randint(10, 15)
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
        self.scrolls = {}
        self.scroll_list = []
        self.victims = {}
        self.image_name = "arch-mage"
        self.sniffrange_monster = 4
        self.sniffrange_items = 6

    def calculate_scroll_list(self):
        """returns a list of (key, spell name, number of scrolls) tuples"""

        result = []
        for i, spell in enumerate(self.scrolls):
            result.append((ALPHABET[i], spell, self.scrolls[spell]))
        self.scroll_list = result

    def spell_from_key(self, key):
        for i, spell, number in self.scroll_list:
            if i == key and number > 0:
                return spell
        return None


class Game():
    dungeon = []  # list of list of list. 3D map representation, using text chars. z,y,x ! z=0: first level. z=1: second level etc
    fov_map = []  # field of vie map, only for current level!
    objects = {}  # container for all Object instances in this dungeon
    # legend = {} # fills itself because of class Object's __init__ method
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
    cursor_x = 0  # absolute coordinate, tile
    cursor_y = 0

    # friend_image = "arch-mage-idle"
    # foe_image = None

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
        Dragon(33, 6, 0)
        Dragon(30, 5, 0)
        Dragon(31, 4, 0)
        Shop(7, 1, 0)
        Gold(2, 1, 0)
        for _ in range(15):
            Scroll(4, 4, 0)
            Scroll(5, 4, 0)
            Scroll(4, 6, 0)
        # Scroll(4, 5, 0)
        self.log.append("Welcome to the first dungeon level (level 0)!")
        self.log.append("Use cursor keys to move around")
        self.load_level(0, "level001.txt", "data")
        # self.load_level(1, "level002.txt", "data")
        # self.load_level(2, "level003.txt", "data")
        # TODO join create_empty_dungeon_level mit create_rooms_tunnels
        self.create_empty_dungeon_level(tiles_x, tiles_y, filled=True, z=1)  # dungoen is full of walls,
        # carve out some rooms and tunnels in this new dungeon level
        self.create_rooms_and_tunnels(z=1)  # carve out some random rooms and tunnels
        # append empty dungeon level
        self.turn = 1

    def new_turn(self):
        self.turn += 1
        # for o in Game.objects.values():
        #    if o.z == self.player.z and o != self.player and o.hitpoints > 0 and isinstance(o, Monster):
        # problem: move_monster can lead to a fight, monster may die and removed from Game.objects, while iterating over Game.objects
        for m in [o for o in Game.objects.values() if
                  o.z == self.player.z and o != self.player and o.hitpoints > 0 and isinstance(o, Monster)]:
            self.move_monster(m)

    def player_has_new_position(self):
        """called after postion change of player,
        checks if the player can pick up something or stays
        on an interesting tile"""
        myfloor = []
        for o in Game.objects.values():
            if (o.z == self.player.z and o.hitpoints > 0 and
                    not isinstance(o, Monster) and
                    o.x == self.player.x and o.y == self.player.y):
                myfloor.append(o)
        if len(myfloor) > 0:
            for o in myfloor:
                if isinstance(o, Gold):
                    Game.log.append("You found {} gold!".format(o.value))
                    self.player.gold += o.value
                    # kill gold from dungeon
                    del Game.objects[o.number]

                elif isinstance(o, Scroll):
                    Game.log.append("you found a scroll of {}".format(o.spell))
                    if o.spell in self.player.scrolls:
                        self.player.scrolls[o.spell] += 1
                    else:
                        self.player.scrolls[o.spell] = 1
                    self.player.calculate_scroll_list()
                    # kill this scroll instance in the dungeon
                    del Game.objects[o.number]

    def other_arrow(self, shooterposition, targetposition):
        # returns start, end, victimposition(s)
        # damage calculation
        # check if line of tiles in arrow path
        flightpath = get_line(shooterposition, targetposition)

        # flightpath = flightpath[1:] # remove first tile, because it is blocked by shooter
        victim = None
        for i, (x, y) in enumerate(flightpath):
            if i == 0:
                continue  # don't look for objects at shooterposition
            # print(Game.dungeon[self.player.z][y][x]) # TODO: highlight flightpath with cursor movement ?
            if Game.dungeon[self.player.z][y][x].block_flying:
                targetposition = flightpath[i - 1]
                break  # some tile is blocking the path
            # is a monster blocking path ?
            for o in [o for o in Game.objects.values() if
                      o.z == self.player.z and o.y == y and o.x == x and isinstance(o, Monster)]:
                # TODO: arrow damage calculation, hit or miss calculation
                Game.log.append("an arrow hit the {} and makes 10 damage!".format(o.__class__.__name__))
                o.hitpoints -= 10
                vicitm = (o.x, o.y)
                self.remove_dead_monsters(o)  # only if really dead
                # non-penetration arrow. the flightpath stops here!
                # TODO: penetration arrow
                # return flightpath[:i]
                return shooterposition, flightpath[i], o  # o = victim
        return shooterposition, targetposition, None  # no victim
        # print("flightpath", flightpath)

    def player_arrow(self):
        """fires an arrow from player to Cursor.
           returns start, end, victim"""
        # TODO: check if player has enough arrows in his inventory
        if Game.cursor_y == self.player.y and Game.cursor_x == self.player.x:
            Game.log.append("you must move the cursor with mouse before shooting with f")
            return None, None, None  # start, end, victim
        return self.other_arrow((self.player.x, self.player.y),
                                (Game.cursor_x, Game.cursor_y))

    def checkfight(self, x, y, z):
        """wir gehen davon aus dass nur der player schaut (checkt) ob er in ein Monster läuft"""
        # Game.foe_image = None
        for o in Game.objects.values():
            if o == self.player:
                continue
            if o.hitpoints <= 0:
                continue
            if not isinstance(o, Monster):
                continue
            if o.z == z:
                if o.x > self.player.x:
                    o.look_direction = 0
                elif o.x < self.player.x:
                    o.look_direction = 1
                # if o.x == x and o.y == y and o.z == z:
                if o.x == x and o.y == y:
                    # monster should now look toward player
                    # if o.x > self.player.x:
                    #    o.look_direction = 0
                    # elif o.x < self.player.x:
                    #    o.look_direction = 1
                    self.fight(self.player, o)
                    return True
        return False

    def move_player(self, dx=0, dy=0):
        if not self.checkfight(self.player.x + dx, self.player.y + dy, self.player.z):
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
            if not isinstance(o, Monster):
                continue
            if o.x == m.x + dx and o.y == m.y + dy:
                dx, dy = 0, 0
                if o == self.player:
                    self.fight(m, self.player)
                break
        m.x += dx
        m.y += dy

    def fight(self, a, b):
        self.strike(a, b)  # first strike
        if b.hitpoints > 0:
            self.strike(b, a)  # counterstrike
        # remove dead monsters from game
        self.remove_dead_monsters(a, b)

    def remove_dead_monsters(self, *monster):
        for mo in monster:  # a monster is a Game.object.value, the key is it's number
            if mo != self.player and mo.hitpoints <= 0:
                name = mo.__class__.__name__
                if name not in self.player.victims:
                    self.player.victims[name] = 1
                else:
                    self.player.victims[name] += 1
                # del Game.objects[monster.number]
                mo.kill()

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

    def cast(self, spell):
        if spell not in self.player.scrolls or self.player.scrolls[spell] < 1:
            Game.log.append("You have currently no scroll of {}".format(spell))
            return False  # no casting
        # ----- spells that need no cursor position at all -----
        if spell == "magic map":
            # make all tiles in this dungeon level explored
            for y, line in enumerate(Game.dungeon[self.player.z]):
                for x, map_tile in enumerate(line):
                    map_tile.explored = True
            self.player.scrolls["magic map"] -= 1
            self.player.calculate_scroll_list()
            return True

        # ----- spells that need a cursor position different from player position ---
        if Game.cursor_y == 0 and Game.cursor_x == 0:
            Game.log.append("you must select another tile with cursor (w,a,s,d) before casting {}".format(spell))
            return False  # no casting

        if spell == "blink":
            # teleport to cursor position TODO: check for wall and illegal landing tiles
            target_tile = Game.dungeon[self.player.z][self.player.y + Game.cursor_y][self.player.x + Game.cursor_x]
            if not target_tile.explored:
                Game.log.append("You can not blink on a unexplored tile.")
                return False
            if target_tile.block_movement:
                Game.log.append("You can not blink to this tile.")
                return False
            if not Game.fov_map[self.player.y + Game.cursor_y][self.player.x + Game.cursor_x]:
                Game.log.append("You can not blink on a tile outside your field of view")
                return False
            for o in Game.objects.values():
                if (o.z == self.player.z and o.y == self.player.y + Game.cursor_y and
                        o.x == self.player.x + Game.cursor_x and o != self.player and
                        isinstance(o, Monster) and o.hitpoints > 0):
                    Game.log.append("You can not blink on top of a monster")
                    return False

            self.move_player(Game.cursor_x, Game.cursor_y)
            self.player.scrolls["blink"] -= 1
            self.player.calculate_scroll_list()
            return True

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
                    Shop(x, y, z, char)
                if char == "*":
                    row.append(Tile("."))
                    Gold(x, y, z, char)
                if char == "M":
                    row.append(Tile("."))
                    if random.random() < 0.5:
                        Wolf(x, y, z)
                    else:
                        Snake(x, y, z)
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
                         o.char == ">" and o.z == z - 1 and isinstance(o, Stair)]
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

    def use_stairs(self):
        """go up or done one dungeon level, depending on stair"""
        for o in Game.objects.values():
            if isinstance(o,
                          Stair) and o.char in "<>" and o.z == self.player.z and o.y == self.player.y and o.x == self.player.x:
                break  # all ok, found a stair
        else:
            Game.log.append("You must find a stair up to ascend or descend")
            return False
        if o.char == "<":
            self.ascend()
            return True
        elif o.char == ">":
            self.descend()
            return True

    def ascend(self):
        """go up one dungeon level (or leave the game if already at level 0)"""
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


class CursorSprite(VectorSprite):

    def create_image(self):
        self.image = pygame.surface.Surface((Viewer.grid_size[0],
                                             Viewer.grid_size[1]))
        c = random.randint(100, 250)
        pygame.draw.rect(self.image, (c, c, c), (0, 0, Viewer.grid_size[0],
                                                 Viewer.grid_size[1]), 3)
        self.image.set_colorkey((0, 0, 0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()

    def update(self, seconds):
        self.create_image() # always make new image every frame with different color
        super().update(seconds)



class Viewer():
    width = 0  # screen x resolution in pixel
    height = 0  # screen y resolution in pixel
    panel_width = 200
    log_height = 100
    grid_size = (32, 32)
    pcx = 0  # player x coordinate in pixel
    pcy = 0  # player y coordinate in pixel

    def __init__(self, game, width=640, height=400, grid_size=(32, 32), fps=60, ):
        """Initialize pygame, window, background, font,...
           default arguments """
        self.game = game
        self.fps = fps
        Viewer.grid_size = grid_size  # make global readable
        Viewer.width = width
        Viewer.height = height
        self.random1 = random.randint(1, 1000)  # necessary for Viewer.wall_and_floor_theme
        self.random2 = random.randint(1, 1000)
        pygame.init()
        # player center in pixel
        Viewer.pcx = (width - Viewer.panel_width) // 2  # set player in the middle of the screen
        Viewer.pcy = (height - Viewer.log_height) // 2
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
        # self.load_images()
        self.create_tiles()
        self.wall_and_floor_theme()

        self.prepare_spritegroups()
        self.cursor = CursorSprite(pos=pygame.math.Vector2(Viewer.pcx, Viewer.pcy))
        self.run()

    def prepare_spritegroups(self):
        self.allgroup = pygame.sprite.LayeredUpdates()  # for drawing
        self.flytextgroup = pygame.sprite.Group()
        #self.cursorgroup = pygame.sprite.Group()

        VectorSprite.groups = self.allgroup
        Flytext.groups = self.allgroup, self.flytextgroup
        ArrowSprite.groups = self.allgroup
        CursorSprite.groups = self.allgroup

    def pixel_to_tile(self, pixelcoordinate):
        """transform pixelcoordinate (x,y, from pygame mouse).
           returns  distance to player tile in tiles (relative coordinates)"""
        x,y = pixelcoordinate
        return (x - self.pcx) // Viewer.grid_size[0]  , (y-self.pcy) // Viewer.grid_size[1]


    def tile_to_pixel(self, pos):
        """get a tile coordinate and returns pixel coordinate"""
        x, y = pos
        x2 = self.pcx + (x - self.game.player.x) * Viewer.grid_size[0]
        y2 = self.pcy + (y - self.game.player.y) * Viewer.grid_size[1]
        return (x2, y2)

    def load_images(self):
        """single images. char looks to the right by default?"""
        # self.images["arch-mage-attack"] = pygame.image.load(
        #    os.path.join("data", "arch-mage-attack.png")).convert_alpha()
        # self.images["arch-mage-defend"] = pygame.image.load(
        #    os.path.join("data", "arch-mage-defend.png")).convert_alpha()
        # self.images["arch-mage-idle"] = pygame.image.load(os.path.join("data", "arch-mage-idle.png")).convert_alpha()
        # self.images["direwolf-attack"] = pygame.image.load(os.path.join("data", "direwolf-attack.png")).convert_alpha()
        # self.images["direwolf-defend"] = pygame.image.load(os.path.join("data", "direwolf-defend.png")).convert_alpha()
        # self.images["direwolf-idle"] = pygame.image.load(os.path.join("data", "direwolf-idle.png")).convert_alpha()
        # self.images["snake-attack"] = pygame.image.load(os.path.join("data", "snake-attack.png")).convert_alpha()
        # self.images["snake-defend"] = pygame.image.load(os.path.join("data", "snake-defend.png")).convert_alpha()
        # self.images["snake-idle"] = pygame.image.load(os.path.join("data", "snake-idle.png")).convert_alpha()
        # self.images["yeti-attack"] = pygame.image.load(os.path.join("data", "yeti-attack.png")).convert_alpha()
        # self.images["yeti-defend"] = pygame.image.load(os.path.join("data", "yeti-defend.png")).convert_alpha()
        # self.images["yeti-idle"] = pygame.image.load(os.path.join("data", "yeti-idle.png")).convert_alpha()
        # self.images["dragon-attack"] = pygame.image.load(os.path.join("data", "yeti-attack.png")).convert_alpha()
        # self.images["dragon-defend"] = pygame.image.load(os.path.join("data", "yeti-defend.png")).convert_alpha()
        # self.images["dragon-idle"] = pygame.image.load(os.path.join("data", "yeti-idle.png")).convert_alpha()

    def move_cursor_to(self, x, y):
        """moves the cursor to tiles xy, """
        target_x, target_y = self.game.player.x + x, self.game.player.y + y
        # check if the target tile is inside the current level dimensions
        level_width = len(Game.dungeon[self.game.player.z][0])
        level_height = len(Game.dungeon[self.game.player.z])
        #print("level dimension in tiles:", level_width, level_height, Game.cursor_x, Game.cursor_y, dx, dy)
        if target_x < 0 or target_y < 0 or target_x >= level_width or target_y >= level_height:
            print("mouse outside level tiles", x, y)
            return  # cursor can not move outside of the current level
        # check if the target tile is outside the current game window
        x = self.pcx + x * self.grid_size[0]
        y = self.pcy + y * self.grid_size[1]
        if x < 0 or y < 0 or x > (self.width - self.panel_width) or y > (self.height - self.log_height):
            print("mouse outside game panel", x, y)
            return  # cursor can not move outside of the game window
        #
        # ---- finally, move the cursor ---
        Game.cursor_x = target_x
        Game.cursor_y = target_y
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
        # those are sprite-sheets, taken from dungeon crawl
        player_img = pygame.image.load(os.path.join("data",
                                                    "player.png")).convert_alpha()  # spritesheed, mostly 32x32, figures looking to the left
        self.walls_img = pygame.image.load(os.path.join("data", "wall.png")).convert_alpha()  # spritesheet 32x32 pixel
        self.floors_img = pygame.image.load(
            os.path.join("data", "floor.png")).convert_alpha()  # spritesheet 32x32 pixel
        self.walls_dark_img = self.walls_img.copy()
        self.floors_dark_img = self.floors_img.copy()
        feats_img = pygame.image.load(os.path.join("data", "feat.png")).convert_alpha()
        feats_dark_img = feats_img.copy()
        main_img = pygame.image.load(os.path.join("data", "main.png")).convert_alpha()
        main_dark_img = main_img.copy()
        # blit a darker picture over the original to darken
        darken_percent = .50
        for (original, copy) in [(self.walls_img, self.walls_dark_img), (self.floors_img, self.floors_dark_img),
                                 (feats_img, feats_dark_img), (main_img, main_dark_img)]:
            dark = pygame.surface.Surface(original.get_size()).convert_alpha()
            dark.fill((0, 0, 0, darken_percent * 255))
            copy.blit(dark, (0, 0))  # blit dark surface over original
            copy.convert_alpha()

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
        # self.stair_up_tile = make_text("<", font_color=(128, 0, 128), grid_size=self.grid_size)[0]

        ##self.stair_up_tile = self.lightfeats[5*35+2]
        ### stair tiles: index 0 -> light tile, index 1 -> dark tile
        self.stair_up_tiles = (pygame.Surface.subsurface(feats_img, (32, 192, 32, 32)),
                               pygame.Surface.subsurface(feats_dark_img, (32, 192, 32, 32)))
        # self.stair_up_tile_dark = pygame.Surface.subsurface(feats_dark_img, (32,192,32,32))
        ##self.stair_down_tile = make_text(">", font_color=(128, 255, 128), grid_size=self.grid_size)[0]
        ### stair tiles: index 0 -> light tile, index 1 -> dark tile
        self.stair_down_tiles = (pygame.Surface.subsurface(feats_img, (0, 192, 32, 32)),
                                 pygame.Surface.subsurface(feats_dark_img, (0, 192, 32, 32)))
        # self.stair_down_tile_dark = pygame.Surface.subsurface(feats_dark_img, (0,192,32,32))

        self.shop_tiles = (pygame.Surface.subsurface(feats_img, (439, 192, 32, 32)),
                           pygame.Surface.subsurface(feats_dark_img, (439, 192, 32, 32)))
        self.gold_tiles = (pygame.Surface.subsurface(main_img, (207, 655, 26, 20)),
                           pygame.Surface.subsurface(main_dark_img, (207, 655, 26, 20)))
        self.scroll_tiles = (pygame.Surface.subsurface(main_img, (188, 412, 27, 28)),
                             pygame.Surface.subsurface(main_dark_img, (188, 412, 27, 28)))

        # ------ sprites -----
        # arrow looking right, only used for Sprite Animation (arrow on the ground has different picture)
        ArrowSprite.image = pygame.Surface.subsurface(main_img, (808, 224, 22, 7))
        # self.arrow_tiles = ( pygame.Surface.subsurface(main_img, (808,224,22,7)),
        #                     pygame.Surface.subsurface(main_dark_img, (808,224,22,7)))
        MagicSprite.image = pygame.Surface.subsurface(main_img, (404,840,19,20)) # magic missile, orange rectangle

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
                       "i": self.scroll_tiles,

                       }  # rest of legend in wall_and_floor_theme

    def wall_and_floor_theme(self):
        """select a set of floor/walltiles, depending on level number (z)"""
        # TODO: make one function out of this and call it twice
        ## manipulate random seed so that each dungeon level always generate the same random tiles
        ##random.seed(self.game.player.z)
        # ---------------------------- walls ----------------------
        # walls: all tiles 32x32, huge image is 1024x1280 x(topleft), y(topleft), how many elements to the right
        # create 2 very large integer numbers
        a = self.game.player.z * self.random1
        b = self.game.player.z * self.random2
        walls = [(0, 0, 8), (256, 0, 8), (512, 0, 8), (768, 0, 8),
                 (0, 32, 8), (256, 32, 8), (512, 32, 8), (768, 32, 8),
                 (0, 64, 8), (256, 64, 8), (512, 64, 8), (768, 64, 8),
                 (0, 96, 8), (256, 96, 8), (512, 96, 8), (768, 96, 8),
                 (0, 128, 8), (256, 128, 8), (512, 128, 8), (768, 128, 8),
                 (0, 160, 8), (256, 160, 8), (512, 160, 8), (768, 160, 8),
                 (0, 192, 8), (256, 192, 8), (512, 192, 8), (768, 192, 4),
                 ]
        walls = walls[a % len(walls)]  # like random.choice, but with consistent result
        # walls = (992,384,5)

        # ---- add single subimages to darkwalls and lightwalls---
        # x1,y1, x2,y2: 0,225, 32 , 256
        # see class floor, attribute decoration for probability. first img comes most often
        mywalls = []
        for i in range(walls[2]):
            x = walls[0] + i * 32
            y = walls[1]
            if x > 1024 - 32:
                x = x - 1024
                y += 32

            mywalls.append((x, y))
        self.darkwalls = []
        self.lightwalls = []
        for (x, y) in mywalls:
            self.lightwalls.append(pygame.Surface.subsurface(self.walls_img, (x, y, 32, 32)))
            self.darkwalls.append(pygame.Surface.subsurface(self.walls_dark_img, (x, y, 32, 32)))
        # ---------------------- floors ------------------
        # floor.png 1024x960, tiles are 32x32
        # floors: all32x32: x(topleft), y(topleft), how many elements

        floors = [(576, 0, 9), (128, 32, 9), (416, 32, 9), (704, 32, 9), (256, 64, 9), (544, 64, 9),
                  (96, 96, 9), (384, 96, 9), (672, 96, 9), (224, 128, 9), (512, 128, 9), (64, 160, 4),
                  (192, 160, 4), (320, 160, 4), (448, 160, 9),
                  ]
        floors = floors[b % len(floors)]  # like random.choice, but consistent
        ##floors = (928,512,10)
        myfloors = []
        for i in range(floors[2]):
            x = floors[0] + i * 32
            y = floors[1]
            if x > 1024 - 32:
                x = x - 1024
                y += 32
            myfloors.append((x, y))
        self.darkfloors = []
        self.lightfloors = []
        for (x, y) in myfloors:
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
                # print("dist, x, y", distance, x, y)
                if distance > Game.torch_radius or Game.fov_map[y][x] == False:
                    # -- only blit (dark) if tile is explored. only draw explored Items (stairs)
                    if map_tile.explored:
                        if map_tile.char == "#":
                            i = map_tile.decoration % len(self.darkwalls)
                            c = self.darkwalls[i]
                            # print(map_tile.i)
                            # c = self.darkwalls[map_tile.i]
                        elif map_tile.char == ".":
                            i = map_tile.decoration % len(self.darkfloors)
                            # c = self.darkfloors[map_tile.decoration]
                            c = self.darkfloors[i]
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
                        # print("blitting....", o.char)
                        # if o.char in "<>":
                        self.tile_blit(self.legend[o.char][1], x, y)
                        # else:
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
                if map_tile.char in "#.":  # light floor or light wall
                    i = map_tile.decoration % len(self.legend[map_tile.char])
                    c = self.legend[map_tile.char][i]
                else:
                    # ?????
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
                if not isinstance(o, Monster):
                    # if o.char in "<>$*": # TODO check if tuple instead surface
                    c = self.legend[o.char][0]  # light tile
                    # else:
                    #    print("ALAAAAAAAAAAAAAAARRRRRMMM")
                    #    c = self.legend[o.char]
                    # print("c = ", c, o.char)
                    o.explored = True  # redundant ?
                    # self.screen.blit(c, (m.x * self.grid_size[0], m.y * self.grid_size[1]))
                    self.tile_blit(c, o.x, o.y)

    def draw_monsters(self, x, y):
        z = self.game.player.z
        for o in Game.objects.values():
            if o.z == z and o.y == y and o.x == x:  # only care if in the correct dungeon level
                # -- only care for Monster class instances or instances that are a child of the Monster class --
                if isinstance(o, Monster) and o.hitpoints > 0:
                    c = self.legend[o.char][o.look_direction]  # looks left or right
                    # self.screen.blit(c, (o.x * self.grid_size[0], o.y * self.grid_size[1]))
                    # correction so that if monster surface != size of tile surface monster is centered on tile
                    corr_x, corr_y = 0, 0
                    if c.get_size() != self.grid_size:
                        corr_x = (self.grid_size[0] - c.get_size()[0]) // 2
                        corr_y = (self.grid_size[1] - c.get_size()[1]) // 2

                    # if o == self.game.player:
                    #    self.screen.blit(c, (self.pcx+corr_x, self.pcy+corr_y))  # blit the player always in middle of screen
                    # else:
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
                distance = ((x - self.game.player.x) ** 2 + (y - self.game.player.y) ** 2) ** 0.5
                try:
                    t = Game.dungeon[self.game.player.z][y][x]
                except:
                    continue
                color = (10, 10, 10)  # black
                dx = -(x - self.game.player.x) * self.radarblipsize
                dy = -(y - self.game.player.y) * self.radarblipsize
                if t.explored:
                    if t.block_movement:
                        color = (50, 50, 250)  # blue wall
                    else:
                        color = (150, 150, 150)  # light grey corridor
                    # pygame.draw.rect(self.radarscreen, color,
                    #                 (self.rcx - dx, self.rcy - dy, self.radarblipsize, self.radarblipsize))
                # ---if a stair is there, paint it (if explored) ---
                for o in Game.objects.values():
                    if o.z == self.game.player.z and o.y == y and o.x == x:
                        if isinstance(o, Stair) and o.explored:
                            if o.char == ">":
                                color = (128, 255, 128)
                            else:
                                color = (64, 255, 64)
                        elif isinstance(o, Shop) and o.explored:
                            color = (200, 200, 200)
                        elif isinstance(o, Item):
                            if Game.fov_map[y][x] or distance < self.game.player.sniffrange_items:
                                color = (0, 200, 0)
                        elif isinstance(o, Monster):
                            if Game.fov_map[y][x] or distance < self.game.player.sniffrange_monster:
                                color = (255, 0, 0)

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

        tilex, tiley = Game.cursor_x,  Game.cursor_y
        ##print("cursor is at ", tilex, tiley, "=", self.tile_to_pixel(tilex, tiley))
        print("tile:", tilex, tiley)
        t = Game.dungeon[self.game.player.z][tiley][tilex]

        write(self.panelscreen, text="x:{} y:{} turn:{}".format(tilex, tiley, self.game.turn), x=5, y=95,
              color=(255, 255, 255),
              font_size=16)
        # tile information
        # - y115
        write(self.panelscreen, text=Game.legend[t.char] if t.explored else "not yet explored", x=5, y=115,
              color=(255, 255, 255), font_size=16)
        # objects on top of that tile ?
        here = []
        hints = []
        if t.explored:
            for o in Game.objects.values():
                # print("object:",o)
                if o.z == self.game.player.z and o.x == tilex and o.y == tiley and o.hitpoints > 0:
                    if not isinstance(o, Monster):
                        here.append(o)
                        if o.hint is not None:
                            hints.append(o.hint)
                    else:
                        # monster only if inside fov
                        if Game.fov_map[o.y][o.x]:
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
            write(self.panelscreen, text=h, x=5, y=y, color=(0, 0, 0), font_size=10)
            y += 20

        # ---- magic scrolls -----
        if len(self.game.player.scrolls) > 0:
            write(self.panelscreen, text="Magic: use CTRL+", color=(80, 0, 80),
                  font_size=20, x=5, y=y)
            y += 20
        for key, spell, number in self.game.player.scroll_list:
            t = "{}: {} x {}".format(key, spell, number)
            write(self.panelscreen, text=t, x=5, y=y, color=(255, 255, 255), font_size=14)
            y += 15

        # blit panelscreen
        # ----- friend and foe ----
        # self.panelscreen.blit(self.images[Game.friend_image], (10, 400))
        # if Game.foe_image is not None:
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
        # all shooters (except player) shoot their arrows at the same time

        for monster in [o for o in Game.objects.values() if
                        o != self.game.player and o.z == self.game.player.z and isinstance(o,
                                                                                           Monster) and o.shoot_arrows]:
            # calculate distance to player
            distance = ((monster.x - self.game.player.x) ** 2 + (monster.y - self.game.player.y) ** 2) ** 0.5
            # monster shoots at you if it can, player is in shooting range and player sees monster
            # print(monster, monster.y, monster.x)
            if Game.fov_map[monster.y][monster.x] and distance < monster.arrow_range:
                ## FlyObject (start, end)
                start, end, victimpos = self.game.other_arrow((monster.x, monster.y),
                                                              (self.game.player.x, self.game.player.y))
                a = MagicSprite(startpos=self.tile_to_pixel(start), endpos=self.tile_to_pixel(end))
                if self.playtime + a.duration > self.animation:
                    self.animation = self.playtime + a.duration
                if victimpos is not None:
                    pass  # todo victim impact animation

        self.animate_sprites_only()

        self.game.new_turn()
        self.redraw = True
        # self.redraw = True

    def animate_sprites_only(self):
        """loop as long as necessary to finish all animations, before coninuing with main loop"""
        while self.animation > self.playtime:
            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000
            self.playtime += seconds

            self.allgroup.clear(self.screen, self.spriteless_background)
            self.allgroup.update(seconds)
            self.allgroup.draw(self.screen)
            pygame.display.update()

    def run(self):
        """The mainloop"""
        running = True
        pygame.mouse.set_visible(True)
        oldleft, oldmiddle, oldright = False, False, False
        self.game.make_fov_map()
        self.redraw = True
        # exittime = 0
        self.spriteless_background = pygame.Surface((Viewer.width, Viewer.height))
        show_range = False
        self.animation = 0  # how many seconds animation should be played until the game accept inputs, new turn etc again
        reset_cursor = True
        log_lines = len(Game.log)
        while running:

            self.game.check_player()  # if player has hitpoints left
            if Game.game_over:
                running = False
            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000
            # --- redraw whole screen if animation has ended ----
            # if animation > self.playtime and animation < (self.playtime + seconds):
            #    self.redraw = True

            self.playtime += seconds

            # ------ mouse handler ------
            # left, middle, right = pygame.mouse.get_pressed()
            # oldleft, oldmiddle, oldright = left, middle, right

            # ------ joystick handler -------
            # for number, j in enumerate(self.joysticks):
            #    if number == 0:
            #        x = j.get_axis(0)
            #        y = j.get_axis(1)
            #        buttons = j.get_numbuttons()
            #        for b in range(buttons):
            #            pushed = j.get_button(b)

            # ------------ pressed keys (in this moment pressed down)------
            pressed_keys = pygame.key.get_pressed()

            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # ---- move the game cursor with wasd ----
                    #if event.key == pygame.K_a:
                    #    self.move_cursor(-1, 0)
                    #    self.redraw = True
                    #    reset_cursor = False
                    #    # Game.cursor_x -= 1
                    #if event.key == pygame.K_d:
                    #    self.move_cursor(1, 0)
                    #    self.redraw = True
                    #    reset_cursor = False
                    #
                    #    # Game.cursor_x += 1
                    #if event.key == pygame.K_w:
                    #    self.move_cursor(0, -1)
                    #    self.redraw = True
                    #    reset_cursor = False#
                    #
                    #    # Game.cursor_y -= 1
                    #if event.key == pygame.K_s:
                    #    self.move_cursor(0, 1)
                    #    self.redraw = True
                    #    reset_cursor = False
                    #
                    #    # Game.cursor_y += 1
                    #
                    # ----------- magic with ctrl key and dynamic key -----
                    # if pressed_keys[pygame.K_RCTRL] or pressed_keys[pygame.K_LCTRL]:
                    if event.mod & pygame.KMOD_CTRL:  # any or both ctrl keys are pressed
                        key = pygame.key.name(event.key)  # name of event key: a, b, c etc.
                        spell = self.game.player.spell_from_key(key)  # get the spell that is currently bond to this key
                        if self.game.cast(spell):  # sucessfull casting -> new turn
                            self.new_turn()

                    # ---- -simple player movement with cursor keys -------
                    if event.key in (pygame.K_RIGHT, pygame.K_KP6):
                        self.new_turn()
                        self.game.move_player(1, 0)

                    if event.key in (pygame.K_LEFT, pygame.K_KP4):
                        self.new_turn()
                        self.game.move_player(-1, 0)

                    if event.key in (pygame.K_UP, pygame.K_KP8):
                        self.new_turn()
                        self.game.move_player(0, -1)

                    if event.key in (pygame.K_DOWN, pygame.K_KP2):
                        self.new_turn()
                        self.game.move_player(0, 1)

                    # --- diagonal movement ---
                    if event.key in (pygame.K_KP7, pygame.K_HOME):
                        self.new_turn()
                        self.game.move_player(-1, -1)

                    if event.key in (pygame.K_KP9, pygame.K_PAGEUP):
                        self.new_turn()
                        self.game.move_player(1, -1)

                    if event.key in (pygame.K_KP1, pygame.K_END):
                        self.new_turn()
                        self.game.move_player(-1, 1)

                    if event.key in (pygame.K_KP3, pygame.K_PAGEDOWN):
                        self.new_turn()
                        self.game.move_player(1, 1)

                    if event.key == pygame.K_SPACE:
                        # Game.turn += 1  # wait a turn
                        self.new_turn()
                        # on shop buy 10 hp for one gold
                        for o in Game.objects.values():
                            if (o.z == self.game.player.z and
                                    o.x == self.game.player.x and
                                    o.y == self.game.player.y and
                                    self.game.player.gold > 0 and
                                    isinstance(o, Shop)):
                                # and o.__class__.__name__=="Shop"):
                                self.game.player.gold -= 1
                                self.game.player.hitpoints += 10

                        self.redraw = True

                    if event.key == pygame.K_x:
                        Flytext(text="Hallo Horst", pos=pygame.math.Vector2(300, 300), move=pygame.math.Vector2(0, -10),
                                max_age=15)

                    if event.key == pygame.K_f:
                        # fire arrow to cursor
                        start, end, victimpos = self.game.player_arrow()  # None , None, None  when player can not shoot, otherwise startpos, endpos, victim
                        if start is not None:
                            a = ArrowSprite(startpos=self.tile_to_pixel(start), endpos=self.tile_to_pixel(end))
                            self.animation = self.playtime + a.duration
                            if victimpos is not None:
                                pass  # todo victim impact animation

                            self.animate_sprites_only()
                            self.new_turn()

                    if event.key in (pygame.K_LESS, pygame.K_GREATER):
                        self.new_turn()
                        # go up a level
                        if self.game.use_stairs():
                            self.redraw = True
                            self.wall_and_floor_theme()  # new walls and floor colors

                    if event.key == pygame.K_PLUS:
                        if event.mod & pygame.KMOD_CTRL:
                            # zoom out radar
                            self.radarblipsize *= 0.5
                            self.radarblipsize = int(max(1, self.radarblipsize))  # don't become zero
                            print("radarblip:", self.radarblipsize)
                            self.redraw = True
                        else:
                            # more torch radius
                            Game.torch_radius += 1
                            self.game.make_fov_map()
                            self.redraw = True


                    if event.key == pygame.K_MINUS:
                        if event.mod & pygame.KMOD_CTRL:
                            # zoom in radar
                            self.radarblipsize *= 2
                            self.radarblipsize = min(64, self.radarblipsize)  # don't become absurd large
                            self.redraw = True
                        else:
                            # --- decrease torch radius ----
                            Game.torch_radius -= 1
                            self.game.make_fov_map()
                            self.redraw = True

            # --- set cursor to mouse if inside play area -----
            x,y =  self.pixel_to_tile(pygame.mouse.get_pos())
            self.move_cursor_to(x,y) # only moves if on valid tile


            # ============== draw screen =================
            # screen_without_sprites = self.screen.copy()
            # self.allgroup.clear(bgd=self.screen)
            self.allgroup.clear(self.screen, self.spriteless_background)

            self.allgroup.update(seconds)

            # dirtyrects = []
            dirtyrects = self.allgroup.draw(self.screen)




            if self.redraw:
                #print(self.pixel_to_tile(pygame.mouse.get_pos()))
                #if self.pixel_to_tile(pygame.mouse.get_pos()) is not (None, None) and reset_cursor:

                    #if reset_cursor and
                #    Game.cursor_x, Game.cursor_y = 0, 0
                #reset_cursor = True
                # delete everything on screen
                self.screen.blit(self.background, (0, 0))
                # --- order of drawing (back to front) ---
                self.draw_dungeon()

                self.draw_radar()
                dirtyrects.append((0, 0, Viewer.width, Viewer.height))
                # self.draw_panel()
                self.draw_log()
                self.spriteless_background.blit(self.screen, (0, 0))

            elif len(Game.log) > log_lines:
                self.draw_log()  # always draw log
                log_lines = len(Game.log)
                dirtyrects.append((0, Viewer.height - self.log_height, Viewer.width, self.log_height))

            self.draw_panel()  # always draw panel
            dirtyrects.append((Viewer.width - self.panel_width, 0, Viewer.panel_width, Viewer.height))

            self.redraw = False



            # write text below sprites
            fps_text = "FPS: {:5.3}".format(self.clock.get_fps())
            pygame.draw.rect(self.screen, (64, 255, 64), (Viewer.width - 110, Viewer.height - 20, 110, 20))
            write(self.screen, text=fps_text, origin="bottomright", x=Viewer.width - 2, y=Viewer.height - 2,
                  font_size=16, bold=True, color=(0, 0, 0))

            # ------ Cursor -----
            self.cursor.pos = pygame.math.Vector2(self.tile_to_pixel((Game.cursor_x, Game.cursor_y)))
            self.cursor.pos += pygame.math.Vector2(Viewer.grid_size[0]//2, Viewer.grid_size[1]//2) # center on tile
            # -------- next frame -------------
            pygame.display.update(dirtyrects)
        # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()
        print("you killed:")
        for v in self.game.player.victims:
            print(v, self.game.player.victims[v])


if __name__ == '__main__':
    g = Game(tiles_x=80, tiles_y=40)
    Viewer(g, width=1200, height=800, grid_size=(32, 32))  # , (35,35))
