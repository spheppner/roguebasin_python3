"""
author: Horst JENS
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download:

based on: http://www.roguebasin.com/index.php?title=Complete_Roguelike_Tutorial,_using_python%2Blibtcod


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
    Example: text with one char for font_size 48 returns the dimensions 29,49"""
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
     the origin is the alignement of the text surface"""
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


class Tile:
    """# a tile of the map and its properties
       block_movement means blocking the movement of Monster/Player, like a wall
       block_sight means blocking the field of view
    """
    def __init__(self, char, block_movement=None, block_sight=None):
        self.char = char
        self.block_movement = block_movement
        self.block_sight = block_sight
        # --- some common tiles ---
        if char == "#":
            self.block_movement = True
            self.block_sight = True
        elif char == ".":
            self.block_movement = False
            self.block_sight = False


class Object():

    number = 0
    # this is a generic dungeon object: the player, a monster, an item, the stairs...
    # it's always represented by a character (for text representation).
    # NOTE: a dungeon tile (wall, floor, water..) is represented by the Tile class
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
        self._overwrite()

    def _overwrite(self):
        pass

    def is_member(self, name):
        """returns True if the instance is a member of the 'name' class or a child of it"""
        # -- only care for Monster class instances or instances that are a child of the Monster class --
        if self.__class__.__name__ == name:
            return True
        for c in self.__class__.__bases__:
            if c.__name__ == name:
                return True
        # it's not a member of 'name'
        return False



class Monster(Object):

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
            print("ouch!")
            return
        self.x += dx
        self.y += dy
        self.z += dz



class Game():

    dungeon = [] # list of list of list. 3D map representation, using text chars. z,y,x !
    objects = {} # container for all Object instances in this dungeon
    legend = {"@":"player",
              "#":"wall tile",
              ".":"floor tile"}

    def __init__(self, tiles_x=80, tiles_y=40, start_x=5, start_y=3):
        self.player = Monster(start_x,start_y,char="@", color=(0,0,255))
        self.create_empty_dungeon_level(tiles_x, tiles_y)
        #print(self.dungeon)


    def create_empty_dungeon_level(self, max_x, max_y):
        """creates empty dungeon with floor tiles ('.') and an outer wall ('#')"""
        floor = []
        for y in range(max_y):
            line = []
            for x in range(max_x):
                #line.append("#" if y == 0 or y== max_y - 1 or x == 0 or x ==max_x-1 else ".")
                line.append(Tile("#") if y == 0 or y== max_y - 1 or x == 0 or x ==max_x-1 else Tile("."))
            floor.append(line)
        Game.dungeon.append(floor)



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
        self.floor_tile =  make_text(".", font_color=(100,100,100), grid_size = self.grid_size)[0]
        self.wall_tile =   make_text("#", font_color=(128,128,128), grid_size = self.grid_size)[0]
        self.legend = {"@": self.player_tile,
                       ".": self.floor_tile,
                       "#": self.wall_tile}



    def draw_dungeon(self):
        z  = self.game.player.z
        for y, line in enumerate(Game.dungeon[z]):
            for x, map_tile in enumerate(line):
                # --- skip blitting dungeon tile if a object/monster sits there ---
                for o in Game.objects.values():
                    # --- do not paint background if there is an object --
                    if o.z == z and o.x == x and o.y == y:
                        break # blit nothing, if one object is found, do not search for others
                else: # --- else in a for block means: the for loop was not exited by a break (no object was found at this place)
                    # ---- blit dungeon tile -----
                    c = self.legend[map_tile.char]
                    self.screen.blit(c, (x * self.grid_size[0],y * self.grid_size[1])) #* self.grid_size[0], y * self.grid_size[1]))

    def draw_non_monsters(self):
        z = self.game.player.z
        for o in Game.objects.values():
            if o.z == z:  # only care if in the correct dungeon level
                # -- only care if NOT: Monster class instances or instances that are a child of the Monster class
                if not o.is_member("Monster"):
                    c = self.legend[m.char]
                    self.screen.blit(c, (m.x * self.grid_size[0], m.y * self.grid_size[1]))

    def draw_monsters(self):
        z = self.game.player.z
        for o in Game.objects.values():
            if o.z == z: # only care if in the correct dungeon level
                # -- only care for Monster class instances or instances that are a child of the Monster class --
                if o.is_member("Monster"):
                    c = self.legend[o.char]
                    self.screen.blit(c, (o.x * self.grid_size[0], o.y * self.grid_size[1]))

    def run(self):
        """The mainloop"""
        running = True
        pygame.mouse.set_visible(False)
        oldleft, oldmiddle, oldright = False, False, False

        #exittime = 0
        while running:
            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000
            self.playtime += seconds
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
                    if event.key == pygame.K_LEFT:
                        self.game.player.move(-1, 0)
                    if event.key == pygame.K_UP:
                        self.game.player.move(0, -1)
                    if event.key == pygame.K_DOWN:
                        self.game.player.move(0, 1)



            # delete everything on screen
            self.screen.blit(self.background, (0, 0))
            # --- order of drawing (back to front) ---
            self.draw_dungeon()
            self.draw_non_monsters()
            self.draw_monsters()


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
    g = Game(tiles_x=60, tiles_y=40, start_x=1, start_y=1)
    Viewer(g, 1200, 800)
