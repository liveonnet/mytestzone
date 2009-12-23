#!/usr/bin/env python
#coding=utf-8
SCREEN_SIZE = (800, 600)
ANT_COUNT = 16
NEST_SIZE = 100.
import pygame
from pygame.locals import *
from random import randint, choice
from gameobjects.vector2 import Vector2
from threading import Timer
class State(object):
	def __init__(self, name):
		self.name = name
	def do_actions(self):
		pass
	def check_conditions(self):
		pass
	def entry_actions(self):
		pass
	def exit_actions(self):
		pass
class StateMachine(object):
	def __init__(self):
		self.states = {}
		self.active_state = None
	def add_state(self, state):
		self.states[state.name] = state
	def think(self):
		if self.active_state is None:
			return
		self.active_state.do_actions()
		new_state_name = self.active_state.check_conditions()
		if new_state_name is not None:
			self.set_state(new_state_name)
	def set_state(self, new_state_name):
		if self.active_state is not None:
			self.active_state.exit_actions()
		self.active_state = self.states.get(new_state_name,None)
		if self.active_state is not None:
			self.active_state.entry_actions()

class World(object):
	def __init__(self):
		self.entities = {}
		self.entity_id = 0
		self.to_del=[]
		self.background = pygame.surface.Surface(SCREEN_SIZE).convert()
		self.background.fill((255, 255, 255))
		self.time_delay=3000 # 毫秒
	def add_entity(self, entity):
		self.entities[self.entity_id] = entity
		entity.id = self.entity_id
		self.entity_id += 1
	def remove_entity(self, entity,delay=False):
		#if isinstance(entity,SoldierAnt):
			#print "del soldierant %d"%(entity.id,)
			#raise Exception("own")
		del self.entities[entity.id]
		if delay:
			self.to_del.append((self.time_delay,entity))
	def get(self, entity_id):
		if entity_id in self.entities:
			return self.entities[entity_id]
		else:
			return None
	def process(self, time_passed):
		time_passed_seconds = time_passed / 1000.0
		for entity in list(self.entities.values()):
			entity.process(time_passed_seconds)
		new_to_del=[]
		for i,j in self.to_del:
			i-=time_passed
			if i>0.0:
				new_to_del.append((i,j))
		self.to_del=new_to_del
	def render(self, surface):
		surface.blit(self.background, (0, 0))
		for dummy,entity in self.to_del:
			entity.render(surface)
		for entity in self.entities.values():
			entity.render(surface)

	def get_close_entity(self, name, location, range=100.):
		location = Vector2(*location)
		for entity in self.entities.values():
			if entity.name == name:
				distance = location.get_distance_to(entity.location)
				if distance < range:
					return entity
		return None
	def get_close_enemy(self,stance,location,range=100.):
		location = Vector2(*location)
		for entity in self.entities.values():
			if entity.stance()==None:
				continue
			if entity.stance()!=stance:
				distance = location.get_distance_to(entity.location)
				if distance < range:
					return entity
		return None

class GameEntity(object):
	def __init__(self, world, name, image,stanceflag=None):
		self.world = world
		self.name = name
		self.image = image
		self.location = Vector2(0, 0)
		self.destination = Vector2(0, 0)
		self.speed = 0.
		self.brain = StateMachine()
		self.id = 0
		self.health=0 # 总生命值
		self.cur_health=0 # 当前生命值
		self.stance_flag=stanceflag # 当前阵营标志
		self.font = pygame.font.SysFont("arial", 16);
		self.font_height = self.font.get_linesize()
	def render(self, surface,health_bar=False,stance_flag=False,state=False):
		x, y = self.location
		w, h = self.image.get_size()
		surface.blit(self.image, (x-w/2, y-h/2))
		# 显示health bar
		if health_bar:
			if self.health>0:
				bar_x = x - w/2
				bar_y = y + h/2
				surface.fill( (255, 0, 0), (bar_x, bar_y, w, 4))
				surface.fill( (0, 255, 0), (bar_x, bar_y, w*self.cur_health/self.health, 4))
		# 显示stance flag
		if stance_flag:
			if self.stance_flag!=None:
				bar_x=x-w/2
				bar_y=y-h/2-4
				surface.fill( self.stance_flag, (bar_x, bar_y, w/4, 4))
		# 显示当前状态
		if state:
			if self.brain.active_state!=None:
				text_surface = self.font.render("%s"%(self.brain.active_state.name,), True, (0,0,0))
				surface.blit(text_surface, (x-w/2+w/4, y-h/2-self.font_height))

	def process(self, time_passed):
		self.brain.think()
		if self.speed > 0. and self.location != self.destination:
			vec_to_destination = self.destination - self.location
			distance_to_destination = vec_to_destination.get_length()
			heading = vec_to_destination.get_normalized()
			travel_distance = min(distance_to_destination, time_passed * self.speed)
			self.location += travel_distance * heading
	def stance(self):
		"""立场"""
		return None

class Leaf(GameEntity):
	def __init__(self, world, image):
		GameEntity.__init__(self, world, "leaf", image)
class Spider(GameEntity):
	def __init__(self, world, image):
		GameEntity.__init__(self, world, "spider", image)
		# Make a 'dead' spider image by turning it upside down
		self.dead_image = pygame.transform.flip(image, 0, 1)
		self.health,self.cur_health = 25,25
		self.speed = 50. + randint(-20, 20)
	def bitten(self):
		# Spider as been bitten
		self.cur_health -= 1
		if self.cur_health <= 0:
			self.speed = 0.
			self.image = self.dead_image
		self.speed = 140.
	def process(self, time_passed):
		x, y = self.location
		if x > SCREEN_SIZE[0] + 2:
			self.world.remove_entity(self)
			return
		GameEntity.process(self, time_passed)
	def render(self,surface):
		GameEntity.render(self,surface,True,False,False)
class Ant(GameEntity):
	def __init__(self, world, nest, image):
		GameEntity.__init__(self, world, "ant", image)
		# State classes are defined below
		exploring_state = AntStateExploring(self)
		seeking_state = AntStateSeeking(self)
		delivering_state = AntStateDelivering(self)
		hunting_state = AntStateHunting(self)
		self.brain.add_state(exploring_state)
		self.brain.add_state(seeking_state)
		self.brain.add_state(delivering_state)
		self.brain.add_state(hunting_state)
		self.nest=nest
		self.goods = None
		self.health,self.cur_health=35,35
		self.stance_flag=self.nest.stance_flag
	def carry(self, goods):
		self.goods=goods
	def drop(self, surface):
		if self.goods:
			self.nest.addgoods(self.goods)
			self.goods = None
	def render(self, surface):
		GameEntity.render(self, surface,False,True,False)
		if self.goods:
			x, y = self.location
			w, h = self.goods.image.get_size()
			surface.blit(self.goods.image, (x-w, y-h/2))

class AntStateExploring(State):
	def __init__(self, ant):
		State.__init__(self, "exploring")
		self.ant = ant
	def random_destination(self):
		w, h = SCREEN_SIZE
		self.ant.destination = Vector2(randint(0, w), randint(0, h))
	def do_actions(self):
		if randint(1, 20) == 1:
			self.random_destination()
	def check_conditions(self):
		# If ant sees a leaf, go to the seeking state
		leaf = self.ant.world.get_close_entity("leaf", self.ant.location)
		if leaf is not None:
			self.ant.leaf_id = leaf.id
			return "seeking"
		# If the ant sees a spider attacking the base, go to hunting state
		spider = self.ant.world.get_close_entity("spider", self.ant.nest.location, self.ant.nest.image.get_width()*2)
		if spider is not None:
			if self.ant.location.get_distance_to(spider.location) < 100.:
				self.ant.spider_id = spider.id
				return "hunting"
		return None
	def entry_actions(self):
		self.ant.speed = 120. + randint(-30, 30)
		self.random_destination()
class AntStateSeeking(State):
	def __init__(self, ant):
		State.__init__(self, "seeking")
		self.ant = ant
		self.leaf_id = None
	def check_conditions(self):
		# If the leaf is gone, then go back to exploring
		leaf = self.ant.world.get(self.ant.leaf_id)
		if leaf is None:
			return "exploring"
		# If we are next to the leaf, pick it up and deliver it
		if self.ant.location.get_distance_to(leaf.location) < 5.0:
			self.ant.carry(leaf)
			self.ant.world.remove_entity(leaf)
			return "delivering"
		return None
	def entry_actions(self):
		# Set the destination to the location of the leaf
		leaf = self.ant.world.get(self.ant.leaf_id)
		if leaf is not None:
			self.ant.destination = leaf.location
			self.ant.speed = 160. + randint(-20, 20)
class AntStateDelivering(State):
	def __init__(self, ant):
		State.__init__(self, "delivering")
		self.ant = ant
	def check_conditions(self):
		# If inside the nest, randomly drop the object
		if Vector2(self.ant.nest.location).get_distance_to(self.ant.location) < self.ant.nest.image.get_width():
			if (randint(1, 10) == 1):
				self.ant.drop(self.ant.world.background)
				return "exploring"
		return None
	def entry_actions(self):
		# Move to a random point in the nest
		self.ant.speed = 60.
		random_offset = Vector2(randint(-20, 20), randint(-20, 20))
		self.ant.destination = Vector2(self.ant.nest.location) + random_offset
class AntStateHunting(State):
	def __init__(self, ant):
		State.__init__(self, "hunting")
		self.ant = ant
		self.got_kill = False
	def do_actions(self):
		spider = self.ant.world.get(self.ant.spider_id)
		if spider is None:
			return
		self.ant.destination = spider.location
		if self.ant.location.get_distance_to(spider.location) < 15.:
			# Give the spider a fighting chance to avoid being killed!
			if randint(1, 5) == 1:
				spider.bitten()
				# If the spider is dead, move it back to the nest
				if spider.health <= 0:
					self.ant.carry(spider)
					self.ant.world.remove_entity(spider)
					self.got_kill = True
	def check_conditions(self):
		if self.got_kill:
			return "delivering"
		spider = self.ant.world.get(self.ant.spider_id)
		# If the spider has been killed then return to exploring state
		if spider is None:
			return "exploring"
		# If the spider gets far enough away, return to exploring state
		if spider.location.get_distance_to(self.ant.nest.location) > self.ant.nest.image.get_width() * 4:
			return "exploring"
		return None
	def entry_actions(self):
		self.speed = 160. + randint(0, 50)
	def exit_actions(self):
		self.got_kill = False

class AntNest(GameEntity):
	def __init__(self,world,name,image,stanceflag):
		GameEntity.__init__(self,world,name,image,stanceflag)
		self.cntLeaf=0
		self.cntSpider=0
		self.font = pygame.font.SysFont("arial", 16);
		self.size=self.image.get_size()
		self.cntSoldierAnt=0
		self.health,self.cur_health=800,800
	def render(self,surface):
		GameEntity.render(self,surface,False,True,False)
		x,y=self.location
		text_surface = self.font.render("%d/%d"%(self.cntLeaf,self.cntSpider), True, (0,0,0))
		surface.blit(text_surface, (x+self.image.get_width()/2, y))

	def process(self,time_passed):
		if self.cntSoldierAnt<2 and self.cntLeaf>=20:
			self.cntLeaf-=20
			# 生出一只兵蚁
			ant=SoldierAnt(self.world,self,soldierant_image)
			ant.location = Vector2(self.location)
			ant.brain.set_state("patrolling")
			self.world.add_entity(ant)
			self.cntSoldierAnt+=1
		pass
	def addgoods(self,goods):
		if isinstance(goods,Leaf):
			self.cntLeaf+=1
		elif isinstance(goods,Spider):
			self.cntSpider+=1
	def getSize(self):
		return self.image.get_width()

class SoldierAnt(GameEntity):
	def __init__(self, world, nest, image):
		GameEntity.__init__(self, world, "soldierant", image)
		# State classes are defined below
		patrolling_state = AntStatePatrolling(self)
		attacking_state = AntStateAttacking(self)
		self.brain.add_state(patrolling_state)
		self.brain.add_state(attacking_state)
		self.nest=nest
		self.health,self.cur_health=50,50
		self.dead_image = pygame.transform.flip(image, 0, 1)
		self.underattack=False
		self.stance_flag=self.nest.stance_flag
	def render(self, surface):
		GameEntity.render(self, surface,True,True)

	def bitten(self):
		# been bitten
		self.cur_health-= 1
		if self.cur_health<= 0:
			self.speed = 0.
			self.image = self.dead_image
			self.brain.set_state(None)
			self.nest.cntSoldierAnt-=1
		else:
			if not self.underattack:
				self.underattack=True
	def stance(self):
		return self.nest

class AntStatePatrolling(State):
	def __init__(self, ant):
		State.__init__(self, "patrolling")
		self.ant = ant
	def random_destination(self):
		w, h = SCREEN_SIZE
		self.ant.destination = Vector2(randint(0, w), randint(0, h))
	def do_actions(self):
		if randint(1, 20) == 1:
			self.random_destination()
	def check_conditions(self):
		if self.ant.underattack:
			enemy = self.ant.world.get_close_enemy(self.ant.stance(),self.ant.location, 15)
			if enemy is not None:
				#if self.ant.location.get_distance_to(enemy.location) < 100.:
				self.ant.enemy_id = enemy.id
				return "attacking"

		enemy = self.ant.world.get_close_enemy(self.ant.stance(),self.ant.nest.location, self.ant.nest.image.get_width()*3)
		if enemy is not None:
			#if self.ant.location.get_distance_to(enemy.location) < 100.:
			self.ant.enemy_id = enemy.id
			return "attacking"
		return None
	def entry_actions(self):
		self.ant.speed = 120. + randint(-30, 30)
		self.random_destination()
class AntStateAttacking(State):
	def __init__(self, ant):
		State.__init__(self, "attacking")
		self.ant = ant
		self.got_kill = False
	def do_actions(self):
		enemy = self.ant.world.get(self.ant.enemy_id)
		if enemy is None:
			return
		self.ant.destination = enemy.location
		if self.ant.location.get_distance_to(enemy.location) < self.ant.image.get_width()+enemy.image.get_width():
			## Give the enemy a fighting chance to avoid being killed!
			if randint(1, 2) == 1:
				enemy.bitten()
				# If the enemy is dead, leave it alone
				if enemy.cur_health <= 0:
					self.ant.world.remove_entity(enemy,True)
					self.got_kill = True

	def check_conditions(self):
		if self.got_kill:
			self.ant.underattack=False
			return "patrolling"

		enemy = self.ant.world.get(self.ant.enemy_id)
		# If the enemy has been killed then return to patrolling state
		if enemy is None:
			return "patrolling"

		# If the enemy gets far enough away, return to patrolling state
		if enemy.location.get_distance_to(self.ant.nest.location) > self.ant.nest.image.get_width() * 4:
			return "patrolling"

		return None
	def entry_actions(self):
		self.speed = 160. + randint(0, 50)
	def exit_actions(self):
		self.got_kill = False

def run():
	pygame.init()
	screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
	world = World()
	w, h = SCREEN_SIZE
	clock = pygame.time.Clock()
	ant_image = pygame.image.load("ant.png").convert_alpha()
	leaf_image = pygame.image.load("leaf.png").convert_alpha()
	spider_image = pygame.image.load("spider.png").convert_alpha()
	nest_image = pygame.image.load("nest.png").convert_alpha()
	soldierant_image = pygame.image.load("soldierant.png").convert_alpha()
	nestA_flag=(128,128,0)
	nestB_flag=(0,128,128)
	globals()["soldierant_image"]=soldierant_image
	nestA=AntNest(world,'n1',nest_image,nestA_flag)
	nestA.location=Vector2(w/4,h/4)
	world.add_entity(nestA)

	nestB=AntNest(world,'n2',nest_image,nestB_flag)
	nestB.location=Vector2(w*3/4,h*3/4)
	world.add_entity(nestB)

	# Add all our ant entities
	for ant_no in range(ANT_COUNT):
		ant = Ant(world, choice([nestA,nestB]),ant_image)
		ant.location = Vector2(randint(0, w), randint(0, h))
		ant.brain.set_state("exploring")
		world.add_entity(ant)

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				return
		time_passed = clock.tick(30)
		# Add a leaf entity 1 in 20 frames
		if randint(1, 20) == 1:
			leaf = Leaf(world, leaf_image)
			leaf.location = Vector2(randint(0, w), randint(0, h))
			world.add_entity(leaf)
		# Add a spider entity 1 in 100 frames
		if randint(1, 100) == 1:
			spider = Spider(world, spider_image)
			spider.location = Vector2(-50, randint(0, h))
			spider.destination = Vector2(w+50, randint(0, h))
			world.add_entity(spider)
		world.process(time_passed)
		world.render(screen)
		pygame.display.update()
if __name__ == "__main__":
	run()
