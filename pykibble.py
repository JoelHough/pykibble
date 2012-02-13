import numpy as np
import scipy.optimize as op
import re
import os

rdi = "dri_table" + os.sep
sr = "sr24" + os.sep
txt = r"~([^~]*)~"
num = r"([^\^]*)"
sep = r"\^"

class Food():
	def __init__(self, food_id, group_id, name):
		self.id = food_id
		self.group_id = group_id
		self.name = name
		
def load_globals():
	global food_ids, food_group_ids, food_names, \
	  groups, \
	  nut_ids, nut_units, nut_names, \
	  data, \
	  rdi_nut_ids, rdi_nut_amounts

	food_ids, food_group_ids, food_names = load_food_des()
	groups = load_fd_group()
	nut_ids, nut_units, nut_names = load_nutr_def()
	data = load_nut_data()
	rdi_nut_names, rdi_nut_amounts = load_rdi_data()
	rdi_nut_ids = map(lambda (name): get_id(name, nut_names, nut_ids), rdi_nut_names)
	
def no_cap(r):
	return r.replace('(', '').replace(')', '')

def none(v):
	return None

def not_none(v):
	return not v is None

def get_field_lists(filename, *fields):
	def call(f, v):
		return f(v)
	field_types = zip(*fields)[0]
	to_types = zip(*fields)[1]
	with open(filename, 'r') as f:
		rs = []
		for line in f.readlines():
			groups = re.match(r"^" + sep.join(field_types), line).groups()
			converted = map(call, to_types, groups)
			result = filter(not_none, converted)
			rs.append(list(result))
		return rs

def get_fields(filename, *fields):
	return map(list, zip(*get_field_lists(filename, *fields)))

def load_food_des():
	""" Loads FOOD_DES.txt, returns (food_ids, food_group_ids, food_names) """
	return get_fields(sr + 'FOOD_DES.txt', (txt, int), (txt, int), (txt, str))

def load_fd_group():
	""" Loads FD_GRP.txt, returns {group_id: group_name} """
	return dict(get_field_lists(sr + 'FD_GROUP.txt', (txt, int), (txt, str)))

def load_nutr_def():
	""" Loads NUTR_DEF.txt, returns (nut_ids, nut_units, nut_names) """
	return get_fields(sr + 'NUTR_DEF.txt', (txt, int), (txt, str), (txt, none), (txt, str))

def load_nut_data():
	""" Loads NUT_DATA.txt, returns [(data_food_id, data_nut_id, data_nut_amount)] """
	return get_field_lists(sr + 'NUT_DATA.txt', (txt, int), (txt, int), (num, float))

def load_rdi_data():
	""" Loads rdi_target, returns (nut_names, nut_values) """
	return get_fields(rdi + "rdi_target", (txt, str), (txt, float))

def get_id(name, names, ids):
	return ids[names.index(name)]

def get_recipe(food_mat, rdi_amounts, food_ids, food_names):
	amounts, error = op.nnls(food_mat, rdi_amounts)
	results = []
	for i in range(len(amounts)):
		if amounts[i] > 0:
			results.append(food_names[i] + " * " + str(amounts[i] * 100) + "g")
	return (results, error)

def filter_data(nut_ids, data):
	results = []
	for datum in data:
		if datum[1] in nut_ids:
			results.append(datum)
	return results

def filter_foods(groups, food_ids, food_group_ids, food_names):
	new_ids = []
	new_group_ids = []
	new_names = []
	for i in range(len(food_ids)):
		if food_group_ids[i] in groups:
			new_ids.append(food_ids[i])
			new_group_ids.append(food_group_ids[i])
			new_names.append(food_names[i])
	return (new_ids, new_group_ids, new_names)
                
def build_food_mat(food_ids, nut_ids, data):
	""" Builds a nut-by-food matrix containing nutrient values in foods """
	n, m = len(nut_ids), len(food_ids)
	mat = np.zeros([n, m])
	for datum in data:
		food_id, nut_id, amount = datum
		#nut_idx = index(nut_ids, nut_id)
		#food_idx = index(food_ids, food_id)
		#if not nut_idx is None and not food_idx is None:
		#	mat[nut_idx][food_idx] = amount
		try:
			mat[nut_ids.index(nut_id)][food_ids.index(food_id)] = amount
		except ValueError:
			pass
	return mat

def index(a, v):
	""" Finds the index of v in a or returns None """
	if v in a:
		return a.index(v)
	#for i in range(len(a)):
	#	if a[i] == v:
	#		return i
	return None

def all_indices(a, v):
	""" Returns a set of all indices of a that contain v """
	result = set()
	for i in range(len(a)):
		if a[i] == v:
			result.add(i)
	return result

