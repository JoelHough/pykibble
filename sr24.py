import os
import re
import pickle
from food_selector import select_foods

_sr = "sr24" + os.sep
_txt = r"~([^~]*)~"
_num = r"([^\^]*)"
_sep = r"\^"

def test():
    _load_fd_group()
    _load_food_des()
    global f, t, r
    f = Food.all()
    t = category_tree(f)
    r = reduced_tree('snacks', t['snacks'])
    
def find_first_branch(key, node):
    if len(node[1]) == 1:
        return find_first_branch(key + ', ' + node[1].keys()[0], node[1].values()[0])
    return (key, node)
    
def reduced_tree(key, node):
    new_tree = dict()
    reduced_key = ''
    reduced_node = []
    if len(node[1]) == 1 and node[0] == None:
        reduced_key, reduced_node = find_first_branch(key, node)
    else:
        reduced_key = key
        reduced_node = list(node)
    new_node = [reduced_node[0], dict()]
    for child in reduced_node[1]:
        child_tree = reduced_tree(child, reduced_node[1][child])
        new_node[1].update(child_tree)
    new_tree[reduced_key] = new_node
    return new_tree

def add_to_tree(tree, path, value):
    if len(path) == 1:
        if path[0] in tree:
           if not tree[path[0]][0] == None:
               print "Ack! Already have " + str(value)
               return
           else:
               tree[path[0]][0] = value
        tree[path[0]] = [value, dict()]
    else:
        if not path[0] in tree:
            tree[path[0]] = [None, dict()]
        add_to_tree(tree[path[0]][1], path[1:], value)

def add_to_tree2(tree, path, value):
    if len(path) == 1:
        if path[0] in tree:
            print "Ack!"
            return
        tree[path[0]] = value
    else:
        if not path[0] in tree:
            tree[path[0]] = dict()
        add_to_tree2(tree[path[0]], path[1:], value)
    
def category_tree(things):
    result = dict()
    for thing in things:
        category = [chunk.strip() for chunk in str(thing).split(",")]
        add_to_tree(result, category, thing)
    return result

#class FoodMatrix():
#
#    def __init__(self, foods, nuts):
#        n, m = 
class Recipe():
    def add_food(self, food, amount):
        if food in self.foods:
            self.foods[food] += amount
        else:
            self.foods[food] = amount

    def __init__(self, rdi):
        self.foods = dict()
        self.rdi = rdi
        
class Food():
    @staticmethod
    def by_id(id):
        return _foods[id]

    @staticmethod
    def all():
        return _foods.values()

    def add_nut(self, nut, amount):
        self.nuts[nut] = amount
        
    def __init__(self, food_id, group, name):
        self.id = food_id
        self.group = group
        self.name = name
        self.nuts = dict()

    def __repr__(self):
        group = self.group.name.lower()
        name = self.name.lower()
        if not name.startswith(group):
            name = group + ', ' + name
        return name
    
class Group():
    @staticmethod
    def by_id(id):
        return _groups[id]

    @staticmethod
    def all():
        return _groups.values()
    
    def __init__(self, group_id, name):
        self.id = group_id
        self.name = name

    def __repr__(self):
        return self.name
    
class Nutrient():
    @staticmethod
    def by_id(id):
        return _nuts[id]

    @staticmethod
    def all():
        return _nuts.values()
    
    def __init__(self, nut_id, units, name):
        self.id = nut_id
        self.units = units
        self.name = name

    def __repr__(self):
        return name + " " + units
    
class RDI():
    def __init__(self, nut, amount):
        self.nut = nut
        self.amount = amount

def _none(v):
    return None

def _not_none(v):
    return not v is None

def _get_field_lists(filename, *fields):
    def call(f, v):
        return f(v)
    field_types = zip(*fields)[0]
    to_types = zip(*fields)[1]
    with open(filename, 'r') as f:
        rs = []
        for line in f.readlines():
            groups = re.match(r"^" + _sep.join(field_types), line).groups()
            converted = map(call, to_types, groups)
            result = filter(_not_none, converted)
            rs.append(list(result))
        return rs

def _load_fd_group():
    """ Loads FD_GRP.txt """
    global _groups
    #if os.path.exists(_sr + 'groups.pkl'):
    #    with open(_sr + 'groups.pkl') as f:
    #        _groups = pickle.load(f)
    #else:
    _groups = dict([(group_id, Group(group_id, name)) for group_id, name in _get_field_lists(_sr + 'FD_GROUP.txt', (_txt, int), (_txt, str))])

def _load_nutr_def():
    """ Loads NUTR_DEF.txt """
    global _nuts
    #if os.path.exists(_sr + 'nuts.pkl'):
    #    with open(_sr + 'nuts.pkl') as f:
    #        _nuts = pickle.load(f)
    #else:
    _nuts = dict([(nut_id, Nutrient(nut_id, units, name)) for nut_id, units, name in _get_field_lists(_sr + 'NUTR_DEF.txt', (_txt, int), (_txt, str), (_txt, _none), (_txt, str))])

def _load_foods():
    """ Loads Food structures with data from FOOD_DES.txt and NUT_DATA.txt """
    if not _load_food_des():
        _load_nut_data()

def _load_food_des():
    """ Loads FOOD_DES.txt, returns whether or not the data was loaded from pickle file """
    global _foods
    #if os.path.exists(_sr + 'foods.pkl'):
    #    with open(_sr + 'foods.pkl') as f:
    #        _foods = pickle.load(f)
    #    return True
    #else:
    _foods = dict([(food_id, Food(food_id, Group.by_id(group_id), name)) for food_id, group_id, name in _get_field_lists(_sr + 'FOOD_DES.txt', (_txt, int), (_txt, int), (_txt, str))])
    return False

def _load_nut_data():
    """ Loads NUT_DATA.txt """
    for food_id, nut_id, amount in _get_field_lists(_sr + 'NUT_DATA.txt', (_txt, int), (_txt, int), (_num, float)):
        Food.by_id(food_id).add_nut(Nutrient.by_id(nut_id), amount)

def _pickle_globals():
    with open(_sr + 'nuts.pkl', 'w') as f:
        pickle.dump(_nuts, f)
    with open(_sr + 'groups.pkl', 'w') as f:
        pickle.dump(_groups, f)
    with open(_sr + 'foods.pkl', 'w') as f:
        pickle.dump(_foods, f)
    
def _load_globals():
    """ Loads the module lists in the proper order (group, nut, food, data) """
    _load_fd_group()
    _load_nutr_def()
    _load_foods()

# def load_rdi_data():
#   """ Loads rdi_target, returns (nut_names, nut_values) """
#   return get_fields(rdi + "rdi_target", (txt, str), (txt, float))

