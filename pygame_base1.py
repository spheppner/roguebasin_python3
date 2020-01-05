"""
author: Horst JENS
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download:

TODO: http://www.roguebasin.com/index.php?title=Roguelike_Tutorial,_using_python3%2Btdl,_part_2


"""
import pygame
import random


# import os


def make_text(msg="@", fontcolor=(255, 0, 255), fontsize=48, grid_size=None):
    """returns pygame surface with text. You still need to blit the surface.
    for size 48 dimensions are 29,49"""
    myfont = pygame.font.SysFont("mono", fontsize, bold=True)
    print("font size:", myfont.size(msg))
    mytext = myfont.render(msg, True, fontcolor)
    mytext = mytext.convert_alpha()
    if grid_size is not None:
        # TODO error handler
        mytext = pygame.transform.scale(mytext, (grid_size, grid_size))
    return mytext


def write(background, text, x=50, y=150, color=(0, 0, 0),
          fontsize=None, center=False):
    """write text on pygame surface. """
    if fontsize is None:
        fontsize = 24
    font = pygame.font.SysFont('mono', fontsize, bold=True)
    fw, fh = font.size(text)
    surface = font.render(text, True, color)
    if center:  # center text around x,y
        background.blit(surface, (x - fw // 2, y - fh // 2))
    else:  # topleft corner is x,y
        background.blit(surface, (x, y))

class Monster():
    number = 0

    def __init__(self, x, y, z=0, char="M"):
        self.number =Monster.number
        Monster.number += 1
        Game.zoo[self.number] = self
        self.x = x
        self.y = y
        self.z = z

    def move(self, dx, dy, dz=0):
        try:
            target = Game.dungeon[self.z+dz][self.y+dy][self.x+dx]
        except:
            raise SystemError("out of dungeon?", self.x,self.y,self.z)
        if target == "#":
            print("ouch!")
            return
        self.x += dx
        self.y += dy
        self.z += dz



class Game():

    dungeon = []
    zoo = {} # collects all Monster instances

    def __init__(self):
        self.player = Monster(5,3,char="@")
        self.create_dungeon_level(80, 40)
        #print(self.dungeon)

    def create_dungeon_level(self, max_x, max_y):
        """creates empty dungeon with tiles '.' and outer wall '#'"""
        floor = []
        for y in range(max_y):
            line = []
            for x in range(max_x):
                line.append("#" if y == 0 or y== max_y - 1 or x == 0 or x ==max_x-1 else ".")
            floor.append(line)
        Game.dungeon.append(floor)
        #print("Dungeon is ready:")
        #print(Game.dungeon)




class Viewer():
    width = 0
    height = 0

    def __init__(self, width=640, height=400, fps=30, grid_size = 15):
        """Initialize pygame, window, background, font,...
           default arguments """
        self.game = Game()
        self.grid_size = grid_size
        pygame.init()
        Viewer.width = width  # make global readable
        Viewer.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill((255, 255, 255))  # fill background white
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        # ------ background images ------
        self.backgroundfilenames = []  # every .jpg or .jpeg file in the folder 'data'
        self.load_background()
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

    def create_tiles(self):
        self.player_char = make_text("@", fontcolor=(0,200,0), grid_size = self.grid_size)
        self.floor_char =  make_text(".", fontcolor=(100,100,100), grid_size = self.grid_size)
        self.wall_char =   make_text("#", fontcolor=(128,128,128), grid_size = self.grid_size)

        self.legend = {"@": self.player_char,
                       ".": self.floor_char,
                       "#": self.wall_char}

    def load_background(self):
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

    def draw_dungeon(self):
        z  = self.game.player.z
        for y, line in enumerate(Game.dungeon[z]):
            for x, char in enumerate(line):
                #print("char is now:", char, x, y)
                if y == self.game.player.y and x == self.game.player.x:
                    #self.screen.blit(self.player_char, (x * self.grid_size, y * self.grid_size))
                    c = self.player_char
                else:
                    c = self.legend[char]
                self.screen.blit(c, (x * self.grid_size, y * self.grid_size))

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
            self.draw_dungeon()


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
            write(self.screen, text=fps_text, x=Viewer.width-200, y=Viewer.height-20, fontsize=18, color=(200,40,40))


            # -------- next frame -------------
            pygame.display.flip()
        # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()


if __name__ == '__main__':
    Viewer(1200, 800)
