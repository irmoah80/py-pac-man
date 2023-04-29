"""
Ai Project : PacMan game with BFS , DFS and A* algorithms
Apr 2023 , Sina Maleki , Shahed University
"""

from collections import deque
import math
import time
import arcade
import random
from arcade.experimental.crt_filter import CRTFilter
from typing import List, NamedTuple, Optional, Sequence, Tuple, Union
from pyglet.math import Vec2
import arcade.gui
import os


SPRITE_IMAGE_SIZE = 83
SPRITE_SCALING = 0.45
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING)

SCREEN_WIDTH = 1150
SCREEN_HEIGHT = 800
HIT_SCALE = 1
SCREEN_TITLE = "PAC-FREE-MAN"

MOVEMENT_SPEED = 1

VIEWPORT_MARGIN = 0

FILE_PATH = os.path.dirname(os.path.abspath(__file__))


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Initializer
        """

        # Call the parent class initializer
        super().__init__(width, height, title)

        # Variables
        self.player_list = None
        self.wall_list = None
        self.enemy_list = None
        self.mgoal_list = None

        #set up maps of game
        self.map_radar = None
        self.map = []
        self.i = None
        self.dest_X = 0
        self.dest_y = 0
        self.cols = 30
        self.rows = 20
        self.queue = None
        self.visited = None

        #for clear mode/btn
        self.wall_clear = False
        self.color_mgoal = None
        

        # Set up the player info
        self.player = None

        #delay time
        self.delta = "0"

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.physics_engine = None

        #True when S on key board pressed
        self.Spressed = False
        self.pause = False
        self.wall_set = False

        #use for algorithm changing
        self.alofsoul = 'b'

        # --- Related to paths
        # List of points that makes up a path between two points
        self.path = None
        self.bfs_path = None
        # List of points we checked to see if there is a barrier there
        self.barrier_list = None
        self.search_barrier_list = None

        # Used in scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Set the window background color
        self.background_color = arcade.color.BLACK
        # Create the crt filter
        self.crt_filter = CRTFilter(width, height,
                                    resolution_down_scale=1.8,
                                    hard_scan=-8,
                                    hard_pix=-3.0,
                                    display_warp = Vec2(1.0 / 80.0, 1.0 / 60.0),
                                    mask_dark=0.5,
                                    mask_light=1.5)
        
        
        #setting up button styles , multiple bacause of python call by reffrence
        style = {
			"font_size" : 12,
			"font_name" : "Kenney Mini Square"
        }

        style1 = {
			"font_size" : 12,
			"font_name" : "Kenney Mini Square"
        }

        style2 = {
			"font_size" : 12,
			"font_name" : "Kenney Mini Square"
        }

        style3 = {
			"font_size" : 12,
			"font_name" : "Kenney Mini Square"
        }

        style4 = {
			"font_size" : 12,
			"font_name" : "Kenney Mini Square"
        }

        style5 = {
			"font_size" : 12,
			"font_name" : "Kenney Mini Square"
        }

        style6 = {
			"font_size" : 12,
			"font_name" : "Kenney Mini Square"
        }

        style6 = {
			"font_size" : 12,
			"font_name" : "Kenney Mini Square",
            "color" : (200 , 200 , 200)
        }
        
        self.uimanager = arcade.gui.UIManager()
        self.uimanager.enable()

        self.delta_txt = arcade.gui.UILabel(text=self.delta ,
                                            width=60, height = 30, style= style6 , font_name="Kenney Mini Square")
        self.bfsbtn = arcade.gui.UIFlatButton(text="bfs",
											width=60, height = 30 , style=style)
        self.dfsbtn = arcade.gui.UIFlatButton(text="dfs",
											width=60, height = 30 , style=style1)
        self.astbtn = arcade.gui.UIFlatButton(text="A*",
											width=60, height = 30 , style=style2)
        self.pausebtn = arcade.gui.UIFlatButton(text="pause",
											width=100, height = 30 , style=style3)
        self.wallbtn = arcade.gui.UIFlatButton(text="wall",
											width=100, height = 30 , style=style4)
        self.clearbtn = arcade.gui.UIFlatButton(text="clear",
											width=100, height = 30 , style=style5)
        self.rawbtn = arcade.gui.UIFlatButton(text="random",
											width=100, height = 30 , style=style6)
        

        # setting up btn 's on click function
        self.bfsbtn.on_click = self.bfs_btn
        self.dfsbtn.on_click = self.dfs_btn
        self.astbtn.on_click = self.ast_btn
        self.pausebtn.on_click = self.pause_btn
        self.wallbtn.on_click = self.wall_btn
        self.clearbtn.on_click = self.clear_btn
        self.rawbtn.on_click = self.raw_btn

        
        # add btns to ui manager
        self.uimanager.add(
			arcade.gui.UIAnchorWidget(
                anchor_x="left",
				anchor_y="top",
				align_x=20,
				align_y=-7,
				child=self.bfsbtn)
		)

        self.uimanager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x="left",
				anchor_y="top",
				align_x=90,
				align_y=-7,
				child=self.dfsbtn)
		)

        self.uimanager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x="left",
				anchor_y="top",
				align_x=230,
				align_y=-7,
				child=self.pausebtn)
		)

        self.uimanager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x="left",
				anchor_y="top",
				align_x=160,
				align_y=-7,
				child=self.astbtn)
		)

        self.uimanager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x="left",
				anchor_y="top",
				align_x=1027,
				align_y=-7,
				child=self.wallbtn)
		)

        self.uimanager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x="left",
				anchor_y="top",
				align_x=917,
				align_y=-7,
				child=self.clearbtn)
		)

        self.uimanager.add(
			arcade.gui.UIAnchorWidget(
				anchor_x="left",
				anchor_y="top",
				align_x=807,
				align_y=-7,
				child=self.rawbtn)
		)

        self.uimanager.add(
			arcade.gui.UIAnchorWidget(
                anchor_x="left",
				anchor_y="top",
				align_x= 573,
				align_y=-14,
				child=self.delta_txt)
		)

        # our default algorithm is bfs , set it btn color green
        self.bfsbtn.bg_color = (21, 100, 21)

        


    def bfs_btn(self , event):
        self.alofsoul = 'b'
        self.bfsbtn.bg_color = (21, 100, 21)
        self.dfsbtn.bg_color = (21, 19, 21)
        self.astbtn.bg_color = (21, 19, 21)
        

    def dfs_btn(self , event):
        self.alofsoul = 'd'
        self.bfsbtn.bg_color = (21, 19, 21)
        self.dfsbtn.bg_color = (21, 100, 21)
        self.astbtn.bg_color = (21, 19, 21)


    
    def ast_btn(self , event):
        self.bfs_path.clear()
        self.alofsoul = 'a'
        self.bfsbtn.bg_color = (21, 19, 21)
        self.astbtn.bg_color = (21, 100, 21)
        self.dfsbtn.bg_color = (21, 19, 21)


    def pause_btn(self , event):
        #self.pause = not self.pause
        if not self.pause and not self.wall_set:
            self.pausebtn.bg_color = (120, 100, 21)
            self.pause = not self.pause
        elif self.pause:
            self.pause = not self.pause
            self.wall_set = False
            self.pausebtn.bg_color = (21, 19, 21)
            self.wallbtn.bg_color = (21, 19, 21)

    def wall_btn(self , event):
        if not self.wall_set and not self.pause:
            self.wall_set = not self.wall_set
            self.pause = not self.pause
            self.wallbtn.bg_color = (21, 19, 120)
            self.pausebtn.bg_color = (120, 100, 21)
        elif not self.wall_set and self.pause:
            self.wall_set = not self.wall_set
            self.wallbtn.bg_color = (21, 19, 120)
        elif self.wall_set:
            self.wall_set = not self.wall_set
            self.pause = False
            self.wallbtn.bg_color = (21, 19, 21)
            self.pausebtn.bg_color = (21, 19, 21)

    def clear_btn(self , event):
        self.wall_clear = True
        self.wall_set = True
        self.wall_adder()
        self.pause = True
        pass

    def raw_btn(self , event):
        self.wall_clear = False
        self.wall_set = False
        self.wall()
        self.pause = False
    
    def wall(self):
        """
        make our board game on normal mode
        """
        spacing = SPRITE_SIZE
        su = 0
        sa = 0
        map_radar = []
        map = []

        for y in range(20):
            map.append([])
            for x in range(30):
                map[y].append(None)
        
        wall_list = arcade.SpriteList()
        mgoal_list = arcade.SpriteList()

        for column in range(self.cols):
            map_radar.append([])
            for row in range(self.rows):
                # if sprite i wall , actually we make it randomly
                if (random.randrange(100) > 70) or (column == 0) or (row == 0) or (column == self.cols -1) or (row == self.rows -1):
                    sprite = arcade.Sprite(FILE_PATH+"\wall.png",0.39 ,
                                           image_width=SPRITE_IMAGE_SIZE , image_height=SPRITE_IMAGE_SIZE , hit_box_algorithm= "None")
                    sprite.hit_box_detail = 1
                    x = (column + 1) * spacing
                    y = (row + 1) * spacing
                    sprite.center_x = x
                    sprite.center_y = y
                    wall_list.append(sprite)
                    su +=1
                    map[row][column] = 2
                    map_radar[column].append([2 , su])

                # if not , it is mini goal
                else:
                    sprite = arcade.Sprite(FILE_PATH+"\minigoal.png",
                                        SPRITE_SCALING, image_width=SPRITE_IMAGE_SIZE , image_height=SPRITE_IMAGE_SIZE , hit_box_algorithm= "None")
                    x = (column + 1) * spacing
                    y = (row + 1) * spacing
                    sprite.center_x = x
                    sprite.center_y = y
                    mgoal_list.append(sprite)
                    sa += 1
                    map[row][column] = 1
                    map_radar[column].append([1 , sa])

        self.graph = self.Graph_maker(map)
        self.map_radar = map_radar
        self.map = map
        self.wall_list = wall_list
        self.mgoal_list = mgoal_list
        self.Astar_barrier_list()
        self.physics_engine = arcade.PhysicsEngineSimple2(self.player, self.enemy, self.wall_list)
        self.physics_engine.update()
        

    def wall_adder(self):
        """
        wall adding handler
        """
        self.w_clear_all()
        self.Astar_barrier_list()
        self.physics_engine = arcade.PhysicsEngineSimple2(self.player, self.enemy, self.wall_list)
        self.physics_engine.update()
        pass

    def w_clear_all(self):
        """
        make our board game on re building our bourd
        used when random button clicked
        """
        spacing = SPRITE_SIZE
        su = 0
        sa = 0
        map_radar = []
        map = []
        for y in range(20):
            map.append([])
            for x in range(30):
                map[y].append(None)
        
        wall_list = arcade.SpriteList()
        mgoal_list = arcade.SpriteList()

        for column in range(self.cols):
            map_radar.append([])
            for row in range(self.rows):
                # if sprite i wall , actually we make it randomly
                if (column == 0) or (row == 0) or (column == self.cols -1) or (row == self.rows -1):
                    sprite = arcade.Sprite(FILE_PATH+"\wall.png",0.39 ,
                                           image_width=SPRITE_IMAGE_SIZE , image_height=SPRITE_IMAGE_SIZE , hit_box_algorithm= "None")
                    sprite.hit_box_detail = 1
                    x = (column + 1) * spacing
                    y = (row + 1) * spacing
                    sprite.center_x = x
                    sprite.center_y = y
                    wall_list.append(sprite)
                    su +=1
                    map[row][column] = 2
                    map_radar[column].append([2 , su])

                # if not , it is mini goal
                else:
                    sprite = arcade.Sprite(FILE_PATH+"\minigoal.png",
                                        SPRITE_SCALING, image_width=SPRITE_IMAGE_SIZE , image_height=SPRITE_IMAGE_SIZE , hit_box_algorithm= "None")
                    x = (column + 1) * spacing
                    y = (row + 1) * spacing
                    sprite.center_x = x
                    sprite.center_y = y
                    mgoal_list.append(sprite)
                    sa += 1
                    map[row][column] = 1
                    map_radar[column].append([1 , sa])

        self.graph = self.Graph_maker(map)
        self.map_radar = map_radar
        self.map = map
        self.wall_list = wall_list
        self.mgoal_list = mgoal_list


    def setup(self):
        """ Set up the game and initialize the variables. """

        #implement map
        for y in range(20):
            self.map.append([])
            for x in range(30):
                self.map[y].append(None)

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True,
                                           spatial_hash_cell_size=128)
        sprite_list_sample = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.mgoal_list = arcade.SpriteList()
        self.map_radar = []
        self.i = 0
        part = arcade.Point
        self.lastsoulpo = False
        self.pause = False
        self.bfs_path = []
        

        # Set up the player
        resource = "D:\packman.png"
        self.player = arcade.Sprite(resource, SPRITE_SCALING , hit_box_detail= HIT_SCALE)
        self.player.center_x = SPRITE_SIZE *10
        self.player.center_y = SPRITE_SIZE *10
        self.map[10][10] = 0
        self.player_list.append(self.player)
        self.player.hit_box_detail = 1

        # Set enemies
        resource = "D:\enemy.png"
        self.enemy = arcade.Sprite(resource, SPRITE_SCALING*1 , hit_box_detail= HIT_SCALE)
        self.enemy.center_x = (SPRITE_SIZE) * 4
        self.enemy.center_y = (SPRITE_SIZE) * 7
        self.map[4][7] = -1
        self.enemy_list.append(self.enemy)
        self.enemy.hit_box_detail = 1

        self.queue = deque([self.player.position])
        self.visited = {self.player.position: None}

        self.playing_field_left_boundary = -SPRITE_SIZE * 2
        self.playing_field_right_boundary = SPRITE_SIZE * 50
        self.playing_field_top_boundary = SPRITE_SIZE * 20
        self.playing_field_bottom_boundary = -SPRITE_SIZE * 2

        # make game board , set value of walls , etc ...
        self.wall()

        self.physics_engine = arcade.PhysicsEngineSimple2(self.player, self.enemy, self.wall_list)



        #set Barrier list
        self.Astar_barrier_list()

    def Astar_barrier_list(self):
        """
        make barrier list
        """
        self.barrier_list = arcade.AStarBarrierList(self.enemy,
                                                    self.wall_list,
                                                    SPRITE_SIZE,
                                                    self.playing_field_left_boundary,
                                                    self.playing_field_right_boundary,
                                                    self.playing_field_bottom_boundary,
                                                    self.playing_field_top_boundary)


    def check_next_node(self , x , y , grid):
        if 0 <= x < self.cols and 0 <= y < self.rows and grid[y][x] != 2:
            return True
        else:
            return False
    
    
    def get_next_nodes(self ,x, y , grid):
        ways = [-1, 0], [0, -1], [1, 0], [0, 1]
        final = []
        for dx , dy in ways:
            if self.check_next_node(x + dx, y + dy , grid):
                 final.append((x + dx, y + dy))
        return final

    def Graph_maker(self , map: list) :
        """
        make graph for calculating path via bfs or dfs
        :param List map: map of game that shows kind of each sprite , via pos
        """
        print(map)
        graph = {}
        for y, row in enumerate(map):
            for x, col in enumerate(row):
                if col != 2:
                    next_nodes = self.get_next_nodes(x, y , map)
                    print("next nodes ----")
                    print(next_nodes)
                    graph[(x, y)] = graph.get((x, y), []) + next_nodes
        return graph
    
    #dfs and bfs function
    def xfs(self , x , start, goal, graph):
        """
        BFS or DFS
        :param x: 'd' for dfs , 'b' for bfs
         """
        assert x == 'b' or x == 'd' , "x should equal 'b' or 'd' to make this bfs or dfs"

        queue = deque([start])
        #use deque DS , easily to implement bfs and dfs
        visited = {start: None}

        while queue:
            if x == 'b':
                cur_node = queue.popleft()
            elif x == 'd':
                cur_node = queue.pop()
            else:
                return 

            if cur_node == goal:
                break
            try:
                next_nodes = graph[cur_node]
            except:
                continue
            for next_node in next_nodes:
                if next_node not in visited:
                    queue.append(next_node)
                    visited[next_node] = cur_node

        return queue, visited


    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        # self.crt_filter.clear()
        self.clear()

        # Draw all the sprites.
        self.wall_list.draw()
        self.mgoal_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        
        # draw path for A*
        if self.path and (self.alofsoul == 'a'):
            arcade.draw_line_strip(self.path, arcade.color.BLUE, 2)

        
        # draw path when dfs or bfs selected
        if self.bfs_path and (self.alofsoul == 'd' or 'b'):
            arcade.draw_line_strip(self.bfs_path, arcade.color.RED, 2)

        self.uimanager.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        self.player.change_x = 0
        self.player.change_y = 0
        self.enemy.change_x = 0
        self.enemy.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player.change_x = MOVEMENT_SPEED

        # Update the character
        self.physics_engine.update()

        # Calculate a path to the player
        enemy = self.enemy_list[0]


        start = (int(self.player.center_x//SPRITE_SIZE) , int(self.player.center_y//SPRITE_SIZE))
        enemy_pos = (int(self.enemy.center_x//SPRITE_SIZE) , int(self.enemy.center_y//SPRITE_SIZE))
        
        self.path = arcade.astar_calculate_path(enemy.position,
                                                    self.player.position,
                                                    self.barrier_list,
                                                    diagonal_movement=False)
        if self.alofsoul != 'a' :
            self.queue.clear()
            self.visited.clear()

            #calculate delay timr
            delta = time.time()
            self.queue, self.visited = self.xfs(self.alofsoul , enemy_pos , start , self.graph)
            delta = time.time() - delta
            self.delta_txt.text = str(delta)

            i = start
            bfs_cache = []

            while i in self.visited:
                try:
                    if self.map_radar[i[0]][i[1]][0] == 1:
                        i = self.visited[i]
                        pos1= self.map_radar[i[0]][i[1]][1]-1
                        pos = (self.mgoal_list[pos1])
                        if pos not in bfs_cache:
                            bfs_cache.append((pos.center_x , pos.center_y))
                except Exception as e:
                    print(e)

                
                if i == enemy_pos:
                    break

            bfs_cache.reverse()
            if len(bfs_cache) != 0:
                self.bfs_path = bfs_cache
            
        self.physics_engine.update()

        
        if self.path and not self.pause:
            for x in self.mgoal_list :
                x.color = (255 , 255 , 255)
            #self.mgoal_list.color = 
            # Where are we
            start_x = self.enemy.center_x
            start_y = self.enemy.center_y

            # use try 
            try:
                if self.alofsoul == 'b' or 'd':
                    self.dest_x = self.bfs_path[self.i][0]
                    self.dest_y = self.bfs_path[self.i][1]
                else:
                    self.dest_x = self.path[self.i][0]
                    self.dest_y = self.path[self.i][1]
            except Exception as e:
                self.dest_x = self.path[self.i][0]
                self.dest_y = self.path[self.i][1]
                print("error")
                print(e)

            # self.dest_x = self.path[self.i][0]
            # self.dest_y = self.path[self.i][1]
            # X and Y diff between the two
            x_diff = self.dest_x - start_x
            y_diff = self.dest_y - start_y

            distance_x = math.copysign(1 , x_diff)
            distance_y = math.copysign(1 , y_diff)


            # Calculate angle to get there
            angle = math.atan2(y_diff, x_diff)

            # How far are we?
            distance = math.sqrt((self.enemy.center_x - self.dest_x) ** 2 + (self.enemy.center_y - self.dest_y) ** 2)

            # How fast should we go? If we are close to our destination,
            # lower our speed so we don't overshoot.

            # Calculate vector to travel
            change_y = math.sin(angle) * MOVEMENT_SPEED
            change_x = math.cos(angle) * MOVEMENT_SPEED

            # Update our location
            self.enemy.center_x += change_x
            self.enemy.center_y += change_y

            # How far are we?
            distance = math.sqrt((self.enemy.center_x - self.dest_x) ** 2 + (self.enemy.center_y - self.dest_y) ** 2)

            # If we are there, head to the next point.
            if distance <= MOVEMENT_SPEED:
                self.i += 1
                self.isindest = 34

            # Reached the end of the list, start over.
            if self.i >= len(self.path):
                    self.i = 0

            # make color of visited node red , in bfs or dfs
            if self.alofsoul != 'a':
                for x, y in self.visited:
                    if self.map_radar[x][y][0] == 1:
                        self.mgoal_list[self.map_radar[x][y][1]-1].color = (200 , 20 , 50)
            
            self.physics_engine.update()



    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse press.
        """
        if not self.Spressed :
            self.player.center_x = x
            self.player.center_y = y
        else:
            self.enemy.center_x = x
            self.enemy.center_y = y


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.S:
            self.Spressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.S:
            self.Spressed = False


def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
