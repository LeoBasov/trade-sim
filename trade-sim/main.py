#!/usr/bin/env python3

station1 = "station 1"
station2 = "station 2"

merchant1 = "merchant 1"

good_a = "good_a"

class World:
    def __init__(self):
        self.stattions = dict()
        self.merchants = dict()
        
    def add_station(self, name):
        station = Station(name)
        self.stattions[name] = station
        print("added station:", name)
        
    def add_merchant(self, name, current_station):
        merchant = Merchant(name, current_station)
        self.merchants[name] = merchant
        print("added merchant:", name, "to station:", current_station)

class Station:
    def __init__(self, name):
        self.name = name
        self.stock = dict()
        self.sell_prizes = dict()
        self.buy_prizes = dict()
        
    def add_good(self, good, number, sell_prize, buy_prize):
        self.stock[good] = number
        self.sell_prizes[good] = sell_prize
        self.buy_prizes[good] = buy_prize
        
        print("added good to station", self.name)
        print("    name:", good, "number:", number, "sell_prize:", sell_prize, "buy_prize:", buy_prize)
        
class Merchant:
    def __init__(self, name, current_station):
        self.name = name
        self.current_station = current_station
        self.money = 0
        self.stock = dict()
        
def set_up_station(world):
    print("setting up stations")
    
    world.add_station(station1)
    world.add_station(station2)
    
    world.stattions[station1].add_good("good_a", 0, 9, 9)
    world.stattions[station2].add_good("good_a", 0, 11, 11)
    

def set_up_merchants(world):
    print("setting up merchants")
    
    world.add_merchant(merchant1, station1)
    
    world.merchants[merchant1].money = 10
    world.merchants[merchant1].stock[good_a] = 0

if __name__ == '__main__':
    world = World()
    
    set_up_station(world)
    set_up_merchants(world)
    
    print("done")
