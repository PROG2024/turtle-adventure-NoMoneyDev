"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
import random
import time
from turtle import RawTurtle
from gamelib import Game, GameElement
import math

class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()


    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color
        self.__turtle: RawTurtle

    def set_spawn_point(self):
        self.x = random.randint(0, self.game.screen_width)
        self.y = random.randint(0, self.game.screen_height)

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )

    @property
    def turtle(self):
        return self.__turtle

    @property
    def x(self):
        return self.turtle.xcor()

    @x.setter
    def x(self, val):
        self.turtle.setx(val)

    @property
    def y(self):
        return self.turtle.ycor()

    @y.setter
    def y(self, val):
        self.turtle.sety(val)


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.
class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str = 'green'):
        super().__init__(game, size, color)
        self.__speed = 3.5 + 2*math.sin(self.game.level * 0.08)
        self.__randseed = random.randint(0,100)

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("circle")
        turtle.color(self.color)
        turtle.penup()
        self.__turtle = turtle

    def update(self) -> None:
        if self.detect():
            self.__turtle.setheading(self.__turtle.towards(self.game.player.x, self.game.player.y))
            self.turtle.color('red')
        else:
            self.__turtle.setheading(self.randheading)
            self.turtle.color('blue')
        self.__turtle.forward(self.movespeed)
        if self.hits_player():
            self.game.game_over_lose()

    @property
    def movespeed(self):
        if self.detect():
            return 0.9 * self.__speed
        return self.__speed

    def render(self) -> None:
        self.x, self.y = self.turtle.xcor(), self.turtle.ycor()
        self.__turtle.getscreen().update()

    def detect(self):
        return self.turtle.distance(self.game.player.x, self.game.player.y) < 100

    def delete(self) -> None:
        pass

    @property
    def turtle(self):
        return self.__turtle

    @property
    def randheading(self):
        random.seed((self.__randseed + datetime.now().second) // 3)
        width = self.game.screen_width
        height = self.game.screen_height
        rand_x = random.randint(width//10, width*9//10)
        rand_y = random.randint(height//10, height*9//10)
        return self.turtle.towards(rand_x, rand_y)

class RandomWalkEnemy(Enemy):
    """
    RandomWalk enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str = 'blue'):
        super().__init__(game, size, color)
        self.__speed = 10 + 3 * math.sin(self.game.level * 0.08)
        self.__randseed = random.randint(0, 100)

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("circle")
        turtle.color(self.color)
        turtle.penup()
        self.__turtle = turtle
        self.new_rand_point()
        self.set_spawn_point()
        self.turtle.setheading(self.turtle.towards(self.rand_point))
        self.draw_path()


    def update(self) -> None:
        if self.distance_to_rand_point < self.__speed:
            self.new_rand_point()
            self.turtle.setheading(self.turtle.towards(self.rand_point))
            self.turtle.clear()
            self.draw_path()
        self.turtle.forward(self.__speed)
        if self.hits_player():
            self.game.game_over_lose()

    def draw_path(self):
        self.turtle.pendown()
        self.turtle.pencolor('red')
        self.turtle.pensize(1)
        distance = self.distance_to_rand_point
        self.turtle.forward(distance)
        self.reset_pen()
        self.turtle.back(distance)

    def reset_pen(self):
        self.turtle.penup()
        self.turtle.pencolor(self.color)
        self.turtle.pensize(self.size)

    def render(self) -> None:
        self.__turtle.getscreen().update()

    def delete(self) -> None:
        pass

    def new_rand_point(self):
        x_margin = 300
        y_margin = 200
        width = self.game.screen_width
        height = self.game.screen_height
        x_range = (int(max(0,self.x - x_margin)), int(min(width, self.x + x_margin)))
        y_range = (int(max(0,self.y - y_margin)), int(min(height, self.y + y_margin)))
        rand_x = random.randint(*x_range)
        rand_y = random.randint(*y_range)
        self.rand_point = (rand_x, rand_y)

    @property
    def distance_to_rand_point(self):
        return self.turtle.distance(self.rand_point)

    @property
    def turtle(self):
        return self.__turtle


class ChaseEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str = 'red'):
        super().__init__(game, size, color)
        self.__speed = 3.5 + 2*math.sin(self.game.level * 0.08)

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("circle")
        turtle.color(self.color)
        turtle.penup()
        self.__turtle = turtle
        self.set_spawn_point()

    def update(self) -> None:
        self.__turtle.setheading(self.__turtle.towards(self.game.player.x, self.game.player.y))
        self.turtle.color('red')
        self.__turtle.forward(self.__speed)
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.x, self.y = self.turtle.xcor(), self.turtle.ycor()
        self.__turtle.getscreen().update()

    def delete(self) -> None:
        pass

    @property
    def turtle(self):
        return self.__turtle


class FencingEnemy(Enemy):
    """
    Fencing enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str = 'blue'):
        super().__init__(game, size, color)
        self.__speed = 7 + 3 * math.sin(self.game.level * 0.08)
        self.radius = 50

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("circle")
        turtle.color(self.color)
        turtle.penup()
        self.__turtle = turtle
        self.set_spawn_point()
        self.turtle.setheading(0)

    def set_spawn_point(self):
        self.x = self.game.home.x - self.radius
        self.y = self.game.home.y - self.radius

    def update(self) -> None:
        if (abs(self.game.home.x - self.x) > self.radius or
            abs(self.game.home.y - self.y) > self.radius) :
            self.turtle.back(self.__speed)
            self.turtle.left(90)
        self.turtle.forward(self.__speed)
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.__turtle.getscreen().update()

    def delete(self) -> None:
        pass

    @property
    def turtle(self):
        return self.__turtle


class SentryGun(Enemy):
    """
    SentryGun enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str = 'blue'):
        super().__init__(game, size, color)
        self.__speed = 7 + 3 * math.sin(self.game.level * 0.08)
        self.__interval =

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("triangle")
        turtle.color(self.color)
        turtle.penup()
        self.__turtle = turtle
        self.set_spawn_point()
        self.turtle.setheading(0)

    def set_spawn_point(self):
        self.x = self.game.screen_width/2
        self.y = self.game.screen_height/2

    def update(self) -> None:
        if (abs(self.game.home.x - self.x) > self.radius or
                abs(self.game.home.y - self.y) > self.radius):
            self.turtle.back(self.__speed)
            self.turtle.left(90)
        self.turtle.forward(self.__speed)
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.__turtle.getscreen().update()

    def delete(self) -> None:
        pass

    @property
    def turtle(self):
        return self.__turtle

# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """
    NUM_ENEMY_PER_LEVEL = [2,2,3,4,4,5,5,5,6,6] # R,R,C,F,C,CT
    ENEMY_TYPE = [FencingEnemy, ChaseEnemy]

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level

        for i in range(EnemyGenerator.NUM_ENEMY_PER_LEVEL[level]):
            self.__game.after(i*1000, lambda i=i: self.create_enemy(i))

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self, i) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        new_enemy = EnemyGenerator.ENEMY_TYPE[i](self.game, 20)
        self.__game.add_enemy(new_enemy)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Lose",
                                font=font,
                                fill="red")
