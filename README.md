# AI Project : Pacman game
Made by [arcade library](https://api.arcade.academy/en/stable/index.html) with some changes in library. Before runing main.py, please edit library files as below :
## Changing some arcade's files
Add this function to handle moving two objects - arcade supports just one object :
### 1. Add PhysicsEngineSimple2
In your arcade library, go to `physics_engines.py` and add this function after `PhysicsEngineSimple` :

```python
class  PhysicsEngineSimple2:
	"""
	Simplistic physics engine for use in games without gravity, such as top-down
	games. It is easier to get
	started with this engine than more sophisticated engines like PyMunk.
	:param Sprite player_sprite: The moving sprite
	:param Union[SpriteList, Iterable[SpriteList] walls: The sprites it can't move through.
	This can be one or multiple spritelists.
	"""
	def  __init__(self,  enemy_sprite:  Sprite,  player_sprite:  Sprite,  walls:  Union[SpriteList,  Iterable[SpriteList]]):
		"""
		Create a simple physics engine.
		"""
		assert  isinstance(player_sprite,  Sprite)
		assert  isinstance(enemy_sprite,  Sprite)
		if  walls:
			if  isinstance(walls,  SpriteList):
				self.walls  =  [walls]
			else:
				self.walls  =  list(walls)
		else:
			self.walls  =  []
		    	self.player_sprite  =  player_sprite
			self.enemy_sprite  =  enemy_sprite
		    
	def  update(self):
		"""
		Move everything and resolve collisions.
		:Returns: SpriteList with all sprites contacted. Empty list if no sprites.
		"""
		return  _move_sprite(self.player_sprite,  self.walls,  ramp_up=False)+_move_sprite(self.enemy_sprite,  self.walls,  ramp_up=False)
```

### 2. Next ...
After that add `from  .physics_engines  import  PhysicsEngineSimple2`to file `__init__.py`in arcade library in line 301.

### 3. Finally!
Last , add `'PhysicsEngineSimple2'` in to file `__init__.py`in arcade library in line 382.
