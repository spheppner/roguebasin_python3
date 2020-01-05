"""
author: Horst JENS
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download:

based on: http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod,_part_4

field of view and exploration
also see http://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds
"""
import pygame
import random
#import inspect

import os


def make_text(text="@", font_color=(255, 0, 255), font_size=48, font_name = "mono", bold=True, grid_size=None):
    """returns pygame surface with text and x, y dimensions in pixel
       grid_size must be None or a tuple with positive integers.
       Use grid_size to scale the text to your desired dimension or None to just render it
       You still need to blit the surface.
       Example: text with one char for font_size 48 returns the dimensions 29,49
    """
    myfont = pygame.font.SysFont(font_name, font_size, bold)
    size_x, size_y = myfont.size(text)
    mytext = myfont.render(text, True, font_color)
    mytext = mytext.convert_alpha() # pygame surface, use for blitting
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
        background.blit(surface, (x - width , y))
    elif origin == "centerleft":
        background.blit(surface, (x, y - height // 2))
    elif origin == "centerright":
        background.blit(surface, (x - width , y - height // 2))
    elif origin == "bottomleft":
        background.blit(surface, (x , y - height ))
    elif origin == "bottomcenter":
        background.blit(surface, (x - width // 2, y ))
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
    def __init__(self, char, block_movement=None, block_sight=None, explored=False):
        self.char = char
        self.block_movement = block_movement
        self.block_sight = block_sight
        self.explored = explored
        # --- some common tiles ---
        if char == "#":
            self.block_movement = True
            self.block_sight = True
        elif char == ".":
            self.block_movement = False
            self.block_sight = False


class Object():
    """this is a generic dungeon object: the player, a monster, an item, the stairs...
       it's always represented by a character (for text representation).
       NOTE: a dungeon tile (wall, floor, water..) is represented by the Tile class
    """

    number = 0

    def __init__(self, x, y, z=0, char="?", color=None):
        self.number = Object.number
        Object.number += 1
        Game.objects[self.number] = self
        self.x = x
        self.y = y
        self.z = z
        self.char = char
        self.color = color
        self.hitpoints = 1 # objects with 0 or less hitpoints will be deleted
        self._overwrite()  # child classes can do stuff here without needing their own __init__ method

    def _overwrite(self):
        pass

    def is_member(self, name):
        """returns True if the instance is a member of the 'name' class or a child of it"""
        if self.__class__.__name__ == name:
            return True
        for c in self.__class__.__bases__:
            if c.__name__ == name:
                return True
        # it's not a member of 'name'
        return False



class Monster(Object):
    """a (moving?) dungeon Monster, like the player, a boss, a NPC..."""

    def _overwrite(self):
        if self.color is None:
            # yello as default color
            self.color = (255,255,0)


    def move(self, dx, dy, dz=0):
        try:
            target = Game.dungeon[self.z+dz][self.y+dy][self.x+dx]
        except:
            raise SystemError("out of dungeon?", self.x,self.y,self.z)
        # --- check if monsters is trying to run into a wall ---
        if target.block_movement:
            print("ouch!") # movement is not possible
            return
        self.x += dx
        self.y += dy
        self.z += dz



class Game():

    dungeon = [] # list of list of list. 3D map representation, using text chars. z,y,x !
    fov_map = [] # for current level!
    objects = {} # container for all Object instances in this dungeon
    legend = {"@":"player",
              "#":"wall tile",
              ".":"floor tile"}
    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30
    TILES_X = 0
    TILES_Y = 0
    START_X = 0
    START_Y = 0
    torch_radius = 10

    def __init__(self, tiles_x=80, tiles_y=40):
        Game.TILES_X = tiles_x
        Game.TILES_Y = tiles_y
        #self.checked = set()  # like a list, but without duplicates. for fov calculation
        self.player = Monster(x=1,y=1,z=0,char="@", color=(0,0,255))
        self.create_empty_dungeon_level(tiles_x, tiles_y, filled=True) # dungoen is full of walls,
        self.create_rooms_and_tunnels() # carve out some random rooms and tunnels, set the player in first room

    def create_rooms_and_tunnels(self, z=0):
        """carve out some random rooms and connects them by tunnels"""
        rooms = []
        num_rooms = 0

        for r in range(Game.MAX_ROOMS):
            print("carving out room number {}...".format(r))
            # random width and height
            w = random.randint(Game.ROOM_MIN_SIZE, Game.ROOM_MAX_SIZE)
            h = random.randint(Game.ROOM_MIN_SIZE, Game.ROOM_MAX_SIZE)
            # random topleft position without going out of the boundaries of the map
            x = random.randint(0, Game.TILES_X - w - 1)
            y = random.randint(0, Game.TILES_Y - h - 1)
            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)
            # run through the other rooms and see if they intersect with this one
            #failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    #failed = True
                    break
            #if not failed:
            else: # for loop got through without a break
                # this means there are no intersections, so this room is valid
                # carve out this room!
                self.create_room(new_room, z)
                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    self.player.x = new_x
                    self.player.y = new_y
                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel
                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # draw a coin (random number that is either 0 or 1)
                    if random.choice([0,1]) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y, z)
                        self.create_v_tunnel(prev_y, new_y, new_x, z)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x, z)
                        self.create_h_tunnel(prev_x, new_x, new_y, z)

                    # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1


    def create_empty_dungeon_level(self, max_x, max_y, filled=True):
        """creates empty dungeon level.
           if "filled" is False with floor tiles ('.') and an outer wall ('#')
           otherwise all is filled with walls
        """
        floor = []
        for y in range(max_y):
            line = []
            for x in range(max_x):
                if filled:
                    line.append(Tile("#")) # fill the whole dungeon level with walls
                else:
                    # outer walls only
                    line.append(Tile("#") if y == 0 or y== max_y - 1 or x == 0 or x ==max_x-1 else Tile("."))
            floor.append(line)
        Game.dungeon.append(floor)

    def create_room(self, rect, z=0):
        """needs a rect object and carves a room out of this (z) dungeon level. Each room has a wall"""
        for x in range(rect.x1 + 1, rect.x2):
            for y in range(rect.y1 + 1, rect.y2):
                # replace the tile at this position with an floor tile
                Game.dungeon[z][y][x] = Tile(".") # replace whatever tile that was there before with a floor

    def create_h_tunnel(self, x1, x2, y, z=0):
        """create an horizontal tunnel in dungeon level z (filled with floor tiles)"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            Game.dungeon[z][y][x] = Tile(".")  # replace whatever tile that was there before with a floor

    def create_v_tunnel(self, y1, y2, x, z=0):
        """create an vertical tunnel in dungeon level z (filled with floor tiles)"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            Game.dungeon[z][y][x] = Tile(".")  # replace whatever tile that was there before with a floor

    def make_fov_map(self):
        Game.fov_map = []
        #self.checked = set() # clear the set of checked coordinates
        px,py,pz = self.player.x, self.player.y, self.player.z
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
            if y == 0 or y == py + Game.torch_radius:
                for x in range(px - Game.torch_radius, px + Game.torch_radius +1):
                    endpoints.add((x,y))
            else:
                endpoints.add((0,y))
                endpoints.add((px + Game.torch_radius, y))
        for coordinate in endpoints:
            # a line of points from the player position to the outer edge of the torchsquare
            points = get_line((px, py), (coordinate[0], coordinate[1]))
            self.calculate_fov_points(points)
        #print(Game.fov_map)

    def calculate_fov_points(self, points):
        """needs a points-list from Bresham's get_line method"""
        for point in points:
            x,y = point[0], point[1]
            # player tile always visible
            if x == self.player.x and y == self.player.y:
                Game.fov_map[y][x] = True  # make this tile visible and move to next point
                continue
            # outside of dungeon level ?
            try:
                tile = Game.dungeon[self.player.z][y][x]
            except:
                continue # outside of dungeon error
            # outside of torch radius ?
            distance = ((self.player.x - x)**2 + (self.player.y - y)**2)**0.5
            if distance > Game.torch_radius:
                continue

            Game.fov_map[y][x] = True # make this tile visible
            if tile.block_sight:
                break #  forget the rest





class Viewer():
    width = 0
    height = 0

    def __init__(self, game, width=640, height=400, grid_size = (15,15), fps=60, ):
        """Initialize pygame, window, background, font,...
           default arguments """
        self.game = game
        self.grid_size = grid_size
        pygame.init()
        Viewer.width = width  # make global readable
        Viewer.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        # ------ background images ------
        self.backgroundfilenames = []  # every .jpg or .jpeg file in the folder 'data'
        self.make_background()
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        # ------ create bitmaps for player and dungeon tiles ----
        #print("fontsize dim values")
        #test = make_text("@")

        self.create_tiles()
        self.run()

    def make_background(self):
        """scans the subfolder 'data' for .jpg files, randomly selects
        one of those as background image. If no files are found, makes a
        white screen"""
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:].lower() == ".jpg" or file[-5:].lower() == ".jpeg":
                        self.backgroundfilenames.append(os.path.join(root,file))
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
        self.player_tile = make_text("@", font_color=self.game.player.color, grid_size = self.grid_size)[0]
        self.floor_tile_dark =  make_text(".", font_color=(50,50,150), grid_size = self.grid_size)[0]
        self.floor_tile_light = make_text(".", font_color=(200, 180, 50), grid_size=self.grid_size)[0]
        self.wall_tile_dark =   make_text("#", font_color=(0,0,100), grid_size = self.grid_size)[0]
        self.wall_tile_light = make_text("#", font_color=(200, 180, 50), grid_size=self.grid_size)[0]
        self.unknown_tile = make_text("?", font_color=(14,14,14),  grid_size=self.grid_size)[0]
        self.legend = {"@": self.player_tile,
                       ".": self.floor_tile_light,
                       "#": self.wall_tile_light,
                       ":": self.floor_tile_dark,
                       "X": self.wall_tile_dark,
                       "?": self.unknown_tile}



    def draw_dungeon(self):
        z  = self.game.player.z
        px, py = self.game.player.x, self.game.player.y
        for y, line in enumerate(Game.dungeon[z]):
            for x, map_tile in enumerate(line):
                distance = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
                # ---- check if tiles is outside torch radius of player ----
                # ---- or otherwise invisible

                if distance > Game.torch_radius or Game.fov_map[y][x] == False:
                    # -- only blit (dark) if tile is explored. Do not test for Monster and items ---
                    # TODO: non-movable Items (stairs) should be remain explored and visible outside Fog of War
                    if map_tile.explored:
                        if map_tile.char == "#":
                            c = self.wall_tile_dark
                        elif map_tile.char == ".":
                            c = self.floor_tile_dark
                        else:
                            raise SystemError("strange tile in map:", c)
                    else:
                        c= self.unknown_tile
                    self.screen.blit(c, (x * self.grid_size[0], y * self.grid_size[1]))  # * self.grid_size[0], y * self.grid_size[1]))
                    continue # next tile, please
                # ==============================================
                # ---- we are inside the torch radius ---
                # ---- AND we are visible! ----
                # explore if this tile is not yet explored
                if not map_tile.explored:
                    map_tile.explored = True
                # --- blit dungeon tile ----
                # TODO: option to skip blitting dungeon tile if Monster or object is here
                c = self.legend[map_tile.char] # light tiles
                self.screen.blit(c, (x * self.grid_size[0], y * self.grid_size[1]))
                self.draw_non_monsters(x,y)
                self.draw_monsters(x,y)


    def draw_non_monsters(self, x, y):
        z = self.game.player.z
        for o in Game.objects.values():
            if o.z == z and o.x == x and o.z == z:  # only care if in the correct dungeon level
                # -- only care if NOT: Monster class instances or instances that are a child of the Monster class
                if not o.is_member("Monster"):
                    c = self.legend[m.char]
                    self.screen.blit(c, (m.x * self.grid_size[0], m.y * self.grid_size[1]))

    def draw_monsters(self, x, y):
        z = self.game.player.z
        for o in Game.objects.values():
            if o.z == z and o.x == x and o.y == y: # only care if in the correct dungeon level
                # -- only care for Monster class instances or instances that are a child of the Monster class --
                if o.is_member("Monster"):
                    c = self.legend[o.char]
                    self.screen.blit(c, (o.x * self.grid_size[0], o.y * self.grid_size[1]))
                    break # one monster per tile is enough

    def run(self):
        """The mainloop"""
        running = True
        pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright = False, False, False
        self.game.make_fov_map()

        #exittime = 0
        while running:
            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000
            self.playtime += seconds
            recalculate_fov = False
            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # ---- -simple movement with cursor keys -------
                    if event.key == pygame.K_RIGHT:
                        self.game.player.move(1, 0)
                        recalculate_fov = True
                    if event.key == pygame.K_LEFT:
                        self.game.player.move(-1, 0)
                        recalculate_fov = True
                    if event.key == pygame.K_UP:
                        self.game.player.move(0, -1)
                        recalculate_fov = True
                    if event.key == pygame.K_DOWN:
                        self.game.player.move(0, 1)
                        recalculate_fov = True



            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            if recalculate_fov:
                self.game.make_fov_map()
            # --- order of drawing (back to front) ---
            self.draw_dungeon()
            #self.draw_non_monsters()
            #self.draw_monsters()


            # ------------ pressed keys ------
            pressed_keys = pygame.key.get_pressed()
            #if pressed_keys[pygame.K_SPACE]:
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
            fps_text = "FPS: {:8.3}".format(self.clock.get_fps())
            write(self.screen, text=fps_text, origin="bottomright", x=Viewer.width-5, y=Viewer.height-5, font_size=18, color=(200,40,40))


            # -------- next frame -------------
            pygame.display.flip()
        # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()



if __name__ == '__main__':
    g = Game(tiles_x=80, tiles_y=40 )
    Viewer(g, 1200, 800)
