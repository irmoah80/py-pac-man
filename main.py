"""
A-Star Path-finding

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.astar_pathfinding
"""

from collections import deque
import math
import time
import arcade
import search
from arcade import Point
import random
from arcade.experimental.crt_filter import CRTFilter
from typing import List, NamedTuple, Optional, Sequence, Tuple, Union
from pyglet.math import Vec2

SPRITE_IMAGE_SIZE = 83
SPRITE_SCALING = 0.45
SPRITE_SIZE = int(SPRITE_IMAGE_SIZE * SPRITE_SCALING)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
HIT_SCALE = 1
SCREEN_TITLE = "PAC-FREE-MAN"

MOVEMENT_SPEED = 1

VIEWPORT_MARGIN = 0


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

        # Variables that will hold sprite lists
        self.player_list = None
        self.wall_list = None
        self.enemy_list = None
        self.mgoal_list = None
        self.map_radar = None
        self.map = []
        self.i = None
        self.dest_X = 0
        self.dest_y = 0
        self.cols = 30
        self.rows = 20
        self.queue = None
        self.visited = None
        self.color_mgoal = None
        

        # Set up the player info
        self.player = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.physics_engine = None
        self.Spressed = False
        self.pause = None

        # --- Related to paths
        # List of points that makes up a path between two points
        self.path = None
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
        self.pause = True
        

        # Set up the player
        resource = ":resources:/images/packman.png"
        self.player = arcade.Sprite(resource, SPRITE_SCALING , hit_box_detail= HIT_SCALE)
        self.player.center_x = SPRITE_SIZE *10
        self.player.center_y = SPRITE_SIZE *10
        self.map[10][10] = 0
        self.player_list.append(self.player)
        self.player.hit_box_detail = 1

        # Set enemies
        resource = ":resources:/images/enemy.png"
        self.enemy = arcade.Sprite(resource, SPRITE_SCALING*1 , hit_box_detail= HIT_SCALE)
        self.enemy.center_x = (SPRITE_SIZE) * 4
        self.enemy.center_y = (SPRITE_SIZE) * 7
        self.map[4][7] = -1
        self.enemy_list.append(self.enemy)
        self.enemy.hit_box_detail = 1

        self.queue = deque([self.player.position])
        self.visited = {self.player.position: None}

        spacing = SPRITE_SIZE
        su = 0
        sa = 0
        for column in range(self.cols):
            self.map_radar.append([])
            for row in range(self.rows):
                # if sprite i wall , actually we make it randomly
                if (random.randrange(100) > 70) or (column == 0) or (row == 0) or (column == self.cols -1) or (row == self.rows -1):
                    sprite = arcade.Sprite(":resources:/images/wall.png",0.39 ,
                                           image_width=SPRITE_IMAGE_SIZE , image_height=SPRITE_IMAGE_SIZE , hit_box_detail= HIT_SCALE)
                    sprite.hit_box_detail = 1
                    x = (column + 1) * spacing
                    y = (row + 1) * spacing
                    sprite.center_x = x
                    sprite.center_y = y
                    self.wall_list.append(sprite)
                    su +=1
                    self.map[row][column] = 2
                    self.map_radar[column].append([2 , su])

                # if not , it is mini goal
                else:
                    sprite = arcade.Sprite(":resources:/images/minigoal.png",
                                        SPRITE_SCALING, image_width=SPRITE_IMAGE_SIZE , image_height=SPRITE_IMAGE_SIZE , hit_box_detail= HIT_SCALE)
                    x = (column + 1) * spacing
                    y = (row + 1) * spacing
                    sprite.center_x = x
                    sprite.center_y = y
                    self.mgoal_list.append(sprite)
                    sa += 1
                    self.map[row][column] = 1
                    self.map_radar[column].append([1 , sa])

        self.graph = self.Graph_maker(self.map)
        print(self.graph)
                
                #self.wall_list.append(sprite)

                # x = (column + 1) * spacing
                # y = (row + 1) * (SPRITE_SIZE+1)

                # sprite.center_x = x
                # sprite.center_y = y
                # if random.randrange(100) > 30:
                #     self.wall_list.append(sprite)
                
        print("------")
        print(self.map)
        self.physics_engine = arcade.PhysicsEngineSimple2(self.player, self.enemy, self.wall_list)

        # --- Path related
        # This variable holds the travel-path. We keep it as an attribute so
        # we can calculate it in on_update, and draw it in on_draw.
        self.path = None
        # Grid size for calculations. The smaller the grid, the longer the time
        # for calculations. Make sure the grid aligns with the sprite wall grid,
        # or some openings might be missed.
        grid_size = SPRITE_SIZE

        # Calculate the playing field size. We can't generate paths outside of
        # this.
        self.playing_field_left_boundary = -SPRITE_SIZE * 2
        self.playing_field_right_boundary = SPRITE_SIZE * 50
        self.playing_field_top_boundary = SPRITE_SIZE * 20
        self.playing_field_bottom_boundary = -SPRITE_SIZE * 2

        # This calculates a list of barriers. By calculating it here in the
        # init, we are assuming this list does not change. In this example,
        # our walls don't move, so that is ok. If we want moving barriers (such as
        # moving platforms or enemies) we need to recalculate. This can be an
        # time-intensive process depending on the playing field size and grid
        # resolution.

        # Note: If the enemy sprites are the same size, we only need to calculate
        # one of these. We do NOT need a different one for each enemy. The sprite
        # is just used for a size calculation.

        #1
        self.barrier_list = arcade.AStarBarrierList(self.enemy,
                                                    self.wall_list,
                                                    grid_size,
                                                    self.playing_field_left_boundary,
                                                    self.playing_field_right_boundary,
                                                    self.playing_field_bottom_boundary,
                                                    self.playing_field_top_boundary)
        
        
    def Node_mode_changer(self , x , y , mode):
        pass

    def Node_ditector(self) -> bool:
        pass

    def Node_food_handler(self , x , y) -> bool:
        pass

    def check_next_node(self , x , y , grid):
        if 0 <= x < self.cols and 0 <= y < self.rows and grid[y][x] != 2:
            return True
        else:
            return False
    
    def get_next_nodes(self ,x, y , grid):
        
        # check_next_node = lambda x, y: True if 0 <= x < self.cols and 0 <= y < self.rows and not grid[y][x] else False
        ways = [-1, 0], [0, -1], [1, 0], [0, 1]
        final = []
        for dx , dy in ways:
            if self.check_next_node(x + dx, y + dy , grid):
                 final.append((x + dx, y + dy))
        return final
        # return [(x + dx, y + dy) for dx, dy in ways if check_next_node(x + dx, y + dy)]

    def Graph_maker(self , map: list) :
        print(map)
        graph = {}
        for y, row in enumerate(map):
            for x, col in enumerate(row):
                if col != 2:
                    next_nodes = self.get_next_nodes(x, y , map)
                    print("next nodes ----")
                    print(next_nodes)
                    graph[(x, y)] = graph.get((x, y), []) + next_nodes
                    # print(graph[(x ,y)])
        return graph

    def bfs(self, start, goal, graph):
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
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
    
    def bfs_calculate_path(self , start , goal):
        pass

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
        
        #2
        if self.path:
            arcade.draw_line_strip(self.path, arcade.color.BLUE, 2)

        # self.use()
        # self.clear()
        # self.crt_filter.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """
        #self.color_mgoal = 

        # Calculate speed based on the keys pressed
        self.player.change_x = 0
        self.player.change_y = 0
        self.enemy.change_x = 0
        self.enemy.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player.change_y = MOVEMENT_SPEED
            #self.enemy.change_y = -MOVEMENT_SPEED
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
        
        # Set to True if we can move diagonally. Note that diagonal movement
        # might cause the enemy to clip corners.
        
        self.path = arcade.astar_calculate_path(enemy.position,
                                                self.player.position,
                                                self.barrier_list,
                                                diagonal_movement=False)


        
        if self.path and self.pause:
            for x in self.mgoal_list :
                x.color = (255 , 255 , 255)
            #self.mgoal_list.color = 
            # Where are we
            start_x = self.enemy.center_x
            start_y = self.enemy.center_y

            # Where are we going
            
            self.dest_x = self.path[self.i][0]
            self.dest_y = self.path[self.i][1]
            

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
            
            start = (int(self.player.center_x//SPRITE_SIZE) , int(self.player.center_y//SPRITE_SIZE))
            enemy_pos = (int(self.enemy.center_x//SPRITE_SIZE) , int(self.enemy.center_y//SPRITE_SIZE))

            # run bfs , return 2 value
            self.queue, self.visited = self.bfs(enemy_pos , start , self.graph)
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
        elif key == arcade.key.P :
            self.pause = not self.pause

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
