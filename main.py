import pygame
from sys import exit 
import zmq
import pickle
import subprocess
from pygame.math import Vector2
from random import randint
import random

# manage microservices
def open_services():
    services = ['country_attributes.py']
    processes = []
    for service in services:
        p = subprocess.Popen(['python', service])
        processes.append(p)
    return processes

def close_services(processes):
    for p in processes: 
        p.terminate()

# import board attributes from microservice
def import_data(request):
    processes = open_services()
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://localhost:5555')

    socket.send_string(request)
    message = socket.recv()
    data_dict = pickle.loads(message)
    close_services(processes)

    return data_dict

# define game and board attributes
continents = import_data('continents')
country_coords = import_data('country_coords')
country_neighbors = import_data('country_neighbors')
deck = import_data('deck')

class Player:
    def __init__(self, color, turn_order, troops_available=0):
        self._color = color
        self._troops_available = troops_available
        self.countries_conquered = []
        self._cards = []
        self.continents_conquered = [] # list of Countries objects
        self._turn = False
        self.turn_order = turn_order
        self._dice = []
        self._countries_selected = []
    
    def start_turn(self):
        self.turn = True

    def end_turn(self):
        self.turn = False

    def roll_dice(self, number_of_dice):
        result = [0 for dice in range(number_of_dice)]
        for dice in result:
            result[dice] = randint(1,7)
        return result
    
    def deploy(self, country):  # must pass in Countries object
        country.add_troops()

    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = color
    
    @property
    def turn(self):
        return self._turn
    
    @turn.setter
    def turn(self, turn):
        self._turn = turn
    
    def end_turn(self):
        self.turn = False

    def get_turn_order(self):
        return self.turn_order
    
    def add_troops(self):
        self._troops_available += 1

    def remove_troops(self):
        self._troops_available -= 1

    @property
    def troops_available(self):
        return self._troops_available
    
    @troops_available.setter
    def troops_available(self, troops):
        self._troops_available = troops
    
    @property 
    def cards(self):
        return self._cards
    
    @cards.setter
    def cards(self, cards):
        self._cards = cards
    
    @property 
    def dice(self):
        return self._dice
    
    @dice.setter
    def dice(self, dice):
        self._dice = dice

    @property
    def countries_selected(self):
        return self._countries_selected
    
    @countries_selected.setter
    def countries_selected(self, country):
        if not self._countries_selected:
            self._countries_selected.append(country)
            return True
        if len(self._countries_selected) < 3 and country not in self._countries_selected:
            if country in self._countries_selected[0].get_neighbors():
                self._countries_selected.append(country)
                return True
            
    def select_country(self, country):
        if not self._countries_selected:
            self._countries_selected.append(country)
            return True
        if len(self._countries_selected) < 3 and country not in self._countries_selected:
            if country.name in self._countries_selected[0].get_neighbors():
                self._countries_selected.append(country)
                return True
            
    def deselect_country(self, country):
        if country in self._countries_selected:
            self._countries_selected.remove(country)
            return True


    


class Card:
    def __init__(self, country, type):
        self.country = country 
        self.type = type
        self.in_deck = True
        self.in_hand = False
        self.played = False

    @property
    def type(self):
        return self.type
    
    @property
    def country(self):
        return self.country
    
    @property
    def in_deck(self):
        return self.in_deck
    
    @property
    def in_hand(self):
        return self.in_hand
    
    @property 
    def played(self):
        return self.played
    
    def set_in_deck(self, state):
        self.in_deck = state

    def set_in_hand(self, state):
        self.in_hand = state
    
    def set_played(self, state):
        self.played = state

class GameState:
    def __init__(self, turn):
        self._turn = turn
        self._active = True
        self._phases = ['Deploy', 'Attack', 'Reinforce']
        self._phase = 0

    @property
    def turn(self):
        return self._turn
    
    @turn.setter
    def turn(self, turn):
        self._turn = turn
    
    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, state):
        self._active = state
    
    @property 
    def phase(self):
        return self._phases[self._phase]
    
    @phase.setter
    def phase(self, phase):
        self._phase = phase


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1360,906))
pygame.display.set_caption('Risk')
test_font = pygame.font.Font('fonts/courier_new.ttf', 16)
roboto = pygame.font.Font('fonts/Roboto_Bold.ttf', 20)
roboto_regular = pygame.font.Font('fonts/Roboto-Regular.ttf', 16)

class Countries(pygame.sprite.Sprite):
    def __init__(self, center, name, neighbors, player_color, troop_number=0):
        super().__init__()
        self.name = name
        self._color = player_color
        self._center = center 
        self.neighbors = neighbors
        self.troop_number = troop_number
        self._owner = None

        self.image = pygame.Surface((20,20))
        self.image.fill(('Black'))
        self.rect = self.image.get_rect(center=self._center)
        self.render_text()
        

    def render_text(self, color='White'):
        self.image.fill(f'{self._color}')
        text_surface = roboto.render(f'{self.troop_number}', True, color)
        text_rect = text_surface.get_rect(center=(self.rect.width /2, self.rect.height / 2))
        self.image.blit(text_surface, text_rect)
        
    def add_troops(self, player):
        if player.troops_available > 0:
            self.troop_number += 1
            player.remove_troops()
            self.render_text()

    def remove_troops(self, player):
        if self.troop_number > 1:
            player.add_troops()
            self.troop_number -= 1
            self.render_text()

    def conquer(self, color, troops_moved, owner):
        self._color = color
        self._owner = owner
        self.troop_number = troops_moved
        self.render_text()
    
    def select_country(self, player):
        if player.turn and len(player.countries_selected) < 3:
            if player.select_country(self):
                self._color = 'Yellow'
                self.render_text('Black')

    def deselect_country(self, player):
        if player.turn:
            if player.deselect_country(self):
                self._color = f'{self._owner.color}'
                self.render_text('White')


    def get_name(self):
        return self.name
    
    def get_neighbors(self):
        return self.neighbors
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = color
    
    @property 
    def center(self):
        return self._center
    
    @center.setter
    def center(self, value):
        self._center = value

    @property 
    def owner(self):
        return self._owner
    
    @owner.setter
    def owner(self, owner):
        self._owner = owner

    @property 
    def get_troop_number(self):
        return self.troop_number
    
    @get_troop_number.setter
    def set_troop_number(self, troop_number):
        self.troop_number = troop_number

class TextBox(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


        self.image = pygame.Surface((250,280))
        self.image.fill('Light Grey')
        self.rect = self.image.get_rect(bottomleft = (0,906))


# game info functions
def display_turn(player):
    text = f"{player.color} player's turn"
    coords = (5, 650)
    return GameInfo(text, coords, 'roboto')

def display_troop_count(player):
    text = f'{player.color} troops available: {player.troops_available}'
    coords = (5,675)
    return GameInfo(text, coords, 'roboto_regular')

def display_cards_in_hand(player):
    text = f"{player.color} player's cards: {player.cards}"
    coords = (5, 700)
    return GameInfo(text, coords, 'roboto_regular')

def display_phase_button():
    text = 'End Phase'
    coords = (0, 906)
    background = 'Red'
    return Buttons(text, coords, background)
  
def display_game_state():
    text = game_state.phase
    coords = (680,0)
    return Buttons(text, coords, 'White')

class GameInfo(pygame.sprite.Sprite):
    def __init__(self, text, coords, font):
        super().__init__()
        if font == 'roboto_regular':
            self.image = roboto_regular.render(f'{text}', True, 'Black')
        else:
            self.image = roboto.render(f'{text}', True, 'Black')
        self.rect = self.image.get_rect(midleft = coords)

class Buttons(pygame.sprite.Sprite):
    def __init__(self, text, coords, background):
        super().__init__()
        if text == 'Deploy' or text == 'Attack' or text == 'Reinforce':
            self.image = roboto.render(f'{text}', True, 'Black')
            self.rect = self.image.get_rect(midtop = coords) 
        else:
            self.image = roboto.render(f'{text}', True, 'Black', f'{background}')
            self.rect = self.image.get_rect(bottomleft = coords)   


    def render_text_wrapped(self):
            pass
    
   

    

    

    def display_dice(self, attacking_player, defending_player):
        self.image.fill('Light Grey')
        text_surface = roboto.render(f"{attacking_player.color}: {attacking_player.dice} | {defending_player.color}: {defending_player.dice}", True, (255,255,255))
        text_rect = text_surface.get_rect(midleft=(5,800))
        # render text wrapped
        text_rect.height = 25
        self.image.blit(text_surface, text_rect)

    

    def display_end_turn_button(self):
        self.image.fill('Light Grey')
        text_surface = roboto.render('End Turn', True, ('Black'), ('Red'))
        text_rect = text_surface.get_rect(bottomleft=(0,906))
        text_rect.width, text_rect.height = 100,25
        self.image.blit(text_surface, text_rect)

# initialization functions 
def create_countries():
    countries_group = pygame.sprite.Group()
    for country in country_coords: 
        countries_group.add(Countries(country_coords[country], country, country_neighbors[country], 'White'))

    sprites = list(countries_group)
    random.shuffle(sprites)
    countries_group.empty()
    countries_group.add(sprites)
    return countries_group

def create_players():
    number_of_players = 2    # come up with input mechanism
    troops = 21    # come up with calculation according to risk rules 
    colors = ['Dark Red', 'Blue', 'Green']
    players = [Player(f'{colors[player]}', player + 1, troops) for player in range(number_of_players)]
    return players

def initialize_game(countries_group, players):
    player_index = 0
    for country in countries_group:
        if player_index > len(players) - 1:
            player_index = 0
        country.conquer(players[player_index].color, 1, players[player_index])
        player_index += 1
    players[0].start_turn()
    game_state = GameState(players[0].turn)
    return game_state

def update_turn(players):
    for player in players:
        if player.get_turn():
            player.end_turn()
            index = player.get_turn_order()
            if player.get_turn_order() == len(players):
                players[0].start_turn()
            else:
                players[index].start_turn()
                break
        
def check_turn(players):
    for player in players:
        if player.turn:
            return player


# game play functions
def attack(attacker, defender):
    if attacker.get_troop_number < 2:
        print('Too low to attack')
    if attacker.get_troop_number == 2:
        attack = attacker.owner.roll_dice(1)
    if attacker.get_troop_number == 3:
        attack = attacker.owner.roll_dice(2)
    if attacker.get_troop_number > 3:
        attack = attacker.owner.roll_dice(3)
    if defender.get_troop_number == 1:
        defense = defender.owner.roll_dice(1)
    if defender.get_troop_number > 2:
        defense = defender.owner.roll_dice(2)
    
    determine_winner(attack, defense, attacker, defender)


def determine_winner(attack, defense, attacker, defender):
    sorted_attack = sorted(attack, reverse=True)
    sorted_defense = sorted(defense, reverse=True)

    while sorted_defense:
        highest_attack = sorted_attack[0]
        highest_defense = sorted_attack[0]
        if highest_attack > highest_defense:
            defender.remove_troops(defender.owner)
        else:
            attacker.remove_troops(attacker.owner)
        sorted_attack[1:]
        sorted_defense[1:]






#board setup and player initialization
board_image = pygame.transform.scale(pygame.image.load('graphics/board1.png'), (1360,906)).convert()
countries_group = create_countries()
players = create_players()
text_box_group = pygame.sprite.GroupSingle()
text_box_group.add(TextBox())
game_info_group = pygame.sprite.Group()
buttons_group = pygame.sprite.Group()


text_box_sprite = text_box_group.sprite
game_state = initialize_game(countries_group, players)

# game loop
while True:
    # get current player
    current_player = check_turn(players)

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        

        # deploy
        collided_countries = [country for country in countries_group if country.rect.collidepoint(pygame.mouse.get_pos())]
        if collided_countries and game_state.phase == 'Deploy':
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_player = check_turn(players)
                current_country = collided_countries[0]
                if current_country.color == current_player.color:
                    if event.button == 1:
                        current_country.add_troops(current_player)
                        collided_countries.clear()
                    if event.button == 3: # to check make sure player can't remove troops from countries
                        current_country.remove_troops(current_player)
                        collided_countries.clear()
       
        # attack
        if collided_countries and game_state.phase == 'Attack':
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_player = check_turn(players)
                current_country = collided_countries[0]
                if current_country.color == current_player.color and not current_player.countries_selected and event.button == 1:
                    current_country.select_country(current_player)
                    collided_countries.clear()
                if current_country.color != current_player.color and current_player.countries_selected and event.button == 1:
                    current_country.select_country(current_player)
                    collided_countries.clear()
                if current_country in current_player.countries_selected and event.button == 3:
                    current_country.deselect_country(current_player)
                    collided_countries.clear()
        
    # game loop
    if game_state.active:
        screen.blit(board_image, (0, 0))
        countries_group.draw(screen)
        text_box_group.draw(screen)
        countries_group.update()
        text_box_group.update()

        # Deploy
        if game_state.phase == 'Deploy': 
            game_state_banner = display_game_state()
            player_turn = display_turn(current_player)
            troop_count = display_troop_count(current_player)
            hand = display_cards_in_hand(current_player)
            phase_button = display_phase_button()
            game_info_group.add(troop_count, player_turn, hand, game_state_banner)
            buttons_group.add(phase_button)
            game_info_group.draw(screen)
            buttons_group.draw(screen)

            # end phase
            end_phase = [phase for phase in buttons_group if phase.rect.collidepoint(pygame.mouse.get_pos())]
            if end_phase:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: game_state.phase = 1

            game_info_group.remove(troop_count, player_turn, hand, game_state_banner)
            buttons_group.remove(phase_button)
        
        # Attack
        if game_state.phase == 'Attack': 
            game_state_banner = display_game_state()
            player_turn = display_turn(current_player)
            phase_button = display_phase_button()
            game_info_group.add(player_turn, game_state_banner)
            buttons_group.add(phase_button)
            game_info_group.draw(screen)
            buttons_group.draw(screen)
            # if collided_countries and game_state.phase == 'Attack':
            #     if event.type == pygame.MOUSEBUTTONDOWN:
            #         current_player = check_turn(players)
            #         if collided_countries[0].get_player_color() == current_player.color and event.button == 1:
            #             pass
            game_info_group.remove(player_turn, game_state_banner)
            buttons_group.remove(phase_button)

    pygame.display.update()