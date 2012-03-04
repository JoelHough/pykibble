import os
import re
import pickle
import numpy as np
import scipy.optimize as op
#import matplotlib.pyplot as plt
import operator
import math
import food_selector

_sr = "sr24" + os.sep
_txt = r"~([^~]*)~"
_num = r"([^\^]*)"
_sep = r"\^"

_good_groups = [100, 200, 400, 900, 1100, 1200, 1600, 2000]

def _test():
    _load_fd_group()
    _load_food_des()
    global f, t, r
    f = Food.all()
    
def _find_first_branch(key, node):
    if len(node[1]) == 1:
        return _find_first_branch(key + ', ' + node[1].keys()[0], node[1].values()[0])
    return (key, node)
    
def _reduced_tree(tree):
    new_tree = dict()
    for key in tree:
        node = tree[key]
        reduced_key = ''
        reduced_node = []
        if len(node[1]) == 1 and node[0] == None:
            reduced_key, reduced_node = _find_first_branch(key, node)
        else:
            reduced_key = key
            reduced_node = list(node)
        new_node = [reduced_node[0], _reduced_tree(reduced_node[1])]
        new_tree[reduced_key] = new_node
    return new_tree

def _add_to_tree(tree, path, value):
    if len(path) == 1:
        if path[0] in tree:
            assert tree[path[0]][0] == None, "Ack! Already have " + str(value)
            tree[path[0]][0] = value
        tree[path[0]] = [value, dict()]
    else:
        if not path[0] in tree:
            tree[path[0]] = [None, dict()]
        _add_to_tree(tree[path[0]][1], path[1:], value)

def _food_tree(foods):
    result = dict()
    for food in foods:
        category = [chunk.strip() for chunk in str(food).split(",")]
        _add_to_tree(result, category, food)
    return _reduced_tree(result)

def display_foods(foods):
    food_selector.select_foods(_food_tree(foods))

        
class Recipe():
    def __repr__(self):
        if len(self.food_amounts) == 0:
            return "Empty recipe"
        food_amounts = sorted(self.food_amounts.items(), key=operator.itemgetter(1), reverse=True)
        width = max([len(str(fa[0])) for fa in food_amounts])
        result = ""
        for fa in food_amounts:
            result += ('{:>5}:{:<' + str(width) + "} | {}g\n").format(str(fa[0].id), str(fa[0]), str(fa[1] * 100.0))
        return result

    # def plot_di(self):
    #     di_vals = dict()
    #     foods = [f.name for f in self.food_amounts]
    #     last = (0,) * len(foods)
    #     ind = np.arange(len(foods))
    #     for rdi in self.target_di:            
    #         vals = [(f[0].nut_amounts.get(rdi.nut, 0.0) * f[1]) / (rdi.lower + (rdi.upper - rdi.lower) / 2) for f in self.food_amounts.items()]
    #         plt.bar(ind, vals, 0.5, bottom=last)
    #         last = list(vals)
    #     plt.show()

    def di_off_by(self):
        di = self.get_di()
        results = []
        for i in range(len(di)):
            percent = 0
            diff = max(min(0, di[i].amount - di[i].lower), di[i].amount - di[i].upper)
            if self.target_di[i].amount > 0:
                percent = diff / self.target_di[i].amount
            off_by = DI(di[i].nut, diff, di[i].lower, di[i].upper, di[i].retention)
            results.append((percent, off_by))
        return sorted(results, key=operator.itemgetter(0), reverse=True)

    def add_food_ids(self, foods):
        for food in foods:
            self.add_food(Food.by_id(food[0]), food[1])

    def get_food_ids(self):
        return [(fa[0].id, fa[1] * 100.0) for fa in self.food_amounts.items()]

    def add_food(self, food, amount):
        """ Food amount in g """
        # The data lists food in 100g units
        self.food_amounts[food] = amount / 100.0 + (self.food_amounts.get(food) or 0)

    def get_di(self):
        """ The nutrient totals with the current food amounts.  Lines up with di_target """
        dis = []
        for di in self.target_di:
            amount = 0
            for food in self.food_amounts:
                amount += (food.nut_amounts.get(di.nut) or 0) * self.food_amounts[food]
            dis.append(DI(di.nut, amount, di.lower, di.upper, di.retention))
        return dis
    
    def complete_with(self, foods):
        # This function does these things
        # Adjust rdi based on already added foods
        # Build food_mat from foods
        # Normalizes and weights using half of upper-lower
        # Linear regress
        # Remove zero foods from result
        n, m = len(self.target_di), len(foods)
        food_mat = np.zeros([n, m])
        di_amounts = np.zeros([n])
        di_so_far = self.get_di()
        norm_terms = np.ones([n])
        missing = dict()
        for i in range(n):
            di = self.target_di[i]
            norm_terms[i] = (di.upper - di.lower) / 2.0
            di_amounts[i] = (di.lower + norm_terms[i] - di_so_far[i].amount) / norm_terms[i]
                
            for j in range(m):
                food = foods[j]
                try:
                    food_mat[i][j] = food.nut_amounts[di.nut] / norm_terms[i]
                except KeyError:
                    pass
                    # print "Warning: No nutrient data for " + str(nut) + " in " + str(food)
                    # missing[nut] = (missing.get(nut) or 0) + 1
        amounts, error = op.nnls(food_mat, di_amounts)
        for j in range(m):
            if amounts[j] > 0:
                self.add_food(foods[j], amounts[j] * 100.0)
        return error
        
    def __init__(self, rdi):
        self.food_amounts = dict()
        self.target_di = rdi

class FoodList(list):
    def where(self, name_has=None, name_has_not=None, group=None, group_in=None, id=None, id_in=None, manufacturer=None):
        return FoodList([food for food in self if (
    (name_has == None or _contains_any(str(food), [name_has] if isinstance(name_has, str) else name_has)) and
    (name_has_not == None or not _contains_any(str(food), [name_has_not] if isinstance(name_has_not, str) else name_has_not)) and
    (group == None or food.group == group) and
    (group_in == None or food.group in group_in) and
    (id == None or food.id == id) and
    (id_in == None or foor.id in id_in) and
    (manufacturer == None or food.manufacturer == manufacturer)
    )])

    def id_dict(self):
        return dict(zip(self.ids(), self))
    
    def ids(self):
        return [f.id for f in self]
    
    def save(self, filename):
        _save_to_file(filename, self.ids())

    @staticmethod
    def load(filename):
        return FoodList(Food.by_id(_load_from_file(filename)))
        
class Food():
    @staticmethod
    def by_id(id):
        try:
            return FoodList(map(_foods.get, id))
        except TypeError:
            return _foods[id]

    @staticmethod
    def all():
        return FoodList(_foods.values())

    def add_nut(self, nut, amount):
        self.nut_amounts[nut] = amount
        
    def __init__(self, food_id, group, name, manufacturer):
        self.id = food_id
        self.group = group
        self.name = name
        self.manufacturer = manufacturer
        self.nut_amounts = dict()

    def __repr__(self):
        group = self.group.name.lower()
        name = self.name.lower()
        if not name.startswith(group):
            name = group + ', ' + name
        return name
    
class Group():
    @staticmethod
    def by_id(id):
        try:
            return map(_groups.get, id)
        except TypeError:
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
    def by_name(name):
        if isinstance(name, str):
            # Special case since there are two 'Energy' nutrients.  We prefer the kcal (rather than kj) entry.
            if name == "Energy":
                return Nutrient.by_id(208)
            for nut in _nuts.values():
                if nut.name == name:
                    return nut
        else:
            return map(Nutrient.by_name, name)
        raise KeyError(str(name) + " not found!")
        
    @staticmethod
    def by_id(id):
        try:
            return map(_nuts.get, id)
        except TypeError:
            return _nuts[id]

    @staticmethod
    def all():
        return _nuts.values()
    
    def __init__(self, nut_id, units, name):
        self.id = nut_id
        self.units = units
        self.name = name

    def __repr__(self):
        return self.units + " " + self.name
    
class DI():
    def __init__(self, nut, amount, lower, upper, retention):
        self.nut = nut
        self.amount = amount / retention
        self.lower = lower
        self.upper = upper
        self.retention = retention

    def __repr__(self):
        return str(self.amount) + str(self.nut)

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
            if line.strip().startswith('#'): continue
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
    """ Loads NUTR_DEF.txt, plus a fake "Weight" nutrient, id 0 """
    global _nuts
    #if os.path.exists(_sr + 'nuts.pkl'):
    #    with open(_sr + 'nuts.pkl') as f:
    #        _nuts = pickle.load(f)
    #else:
    _nuts = dict([(nut_id, Nutrient(nut_id, units, name)) for nut_id, units, name in _get_field_lists(_sr + 'NUTR_DEF.txt', (_txt, int), (_txt, str), (_txt, _none), (_txt, str))])
    _nuts[0] = Nutrient(0, 'g', 'Weight')

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
    _foods = dict([(food_id, Food(food_id, Group.by_id(group_id), name, manufacturer)) for food_id, group_id, name, manufacturer in _get_field_lists(_sr + 'FOOD_DES.txt', (_txt, int), (_txt, int), (_txt, str), (_txt, _none), (_txt, _none), (_txt, str))])
    return False

def _load_nut_data():
    """ Loads NUT_DATA.txt, plus adds 100g of weight to each food as nutrient """
    for food_id, nut_id, amount in _get_field_lists(_sr + 'NUT_DATA.txt', (_txt, int), (_txt, int), (_num, float)):
        Food.by_id(food_id).add_nut(Nutrient.by_id(nut_id), amount)
    for food in Food.all():
        food.add_nut(Nutrient.by_id(0), 100)

def _load_rdi():
    """ Loads rdi_target """
    global _rdi
    _rdi = [DI(Nutrient.by_name(name), amount, lower, upper, retention) for name, amount, lower, upper, retention in _get_field_lists("rdi_target", (_txt, str), (_txt, float), (_txt, float), (_txt, float), (_txt, float))]

def _pickle_globals():
    with open(_sr + 'nuts.pkl', 'w') as f:
        pickle.dump(_nuts, f)
    with open(_sr + 'groups.pkl', 'w') as f:
        pickle.dump(_groups, f)
    with open(_sr + 'foods.pkl', 'w') as f:
        pickle.dump(_foods, f)
    with open('rdi.pkl', 'w') as f:
        pickle.dump(_rdi, f)
    
def _load_globals():
    """ Loads the module lists in the proper order (group, nut, food, data, rdi) """
    _load_fd_group()
    _load_nutr_def()
    _load_foods()
    _load_rdi()

def _save_to_file(filename, obj):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)

def _load_from_file(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

def _load_blacklist():
    global blacklist
    blacklist = _load_from_file('blacklist.pkl')

def _contains_any(container, things):
    for t in things:
        if t in container:
           return True
    return False

def save_working():
    _save_to_file('current_blacklist.pkl', blacklist)
    f.save('current_foods.pkl')
    _save_to_file('current_base_ingredients.pkl', i)
    _save_to_file('current_recipe.pkl', r.get_food_ids())

def load_working():
    global blacklist, f, i, r
    blacklist = _load_from_file('current_blacklist.pkl')
    f = FoodList.load('current_foods.pkl')
    i = _load_from_file('current_base_ingredients.pkl')
    r = Recipe(_rdi)
    r.add_food_ids(_load_from_file('current_recipe.pkl'))
    
def ban(name):
    global blacklist, f
    blacklist.append(name)
    f = f.where(name_has_not=blacklist)

def remix():
    global r, i, f
    r = Recipe(_rdi)
    r.add_food_ids(i)
    r.complete_with(f)
    print r
    print r.di_off_by()
