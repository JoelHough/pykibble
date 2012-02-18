import numpy as np
import scipy.optimize as op
import re
import os

rdi = "dri_table" + os.sep

# def load_globals():
# 	global food_ids, food_group_ids, food_names, \
# 	  groups, \
# 	  nut_ids, nut_units, nut_names, \
# 	  data, \
# 	  rdi_nut_ids, rdi_nut_amounts

# 	food_ids, food_group_ids, food_names = load_food_des()
# 	groups = load_fd_group()
# 	nut_ids, nut_units, nut_names = load_nutr_def()
# 	data = load_nut_data()
# 	rdi_nut_names, rdi_nut_amounts = load_rdi_data()
# 	rdi_nut_ids = map(lambda (name): get_id(name, nut_names, nut_ids), rdi_nut_names)
	
# def no_cap(r):
# 	return r.replace('(', '').replace(')', '')

# def get_fields(filename, *fields):
# 	return map(list, zip(*get_field_lists(filename, *fields)))

# def get_id(name, names, ids):
# 	return ids[names.index(name)]

# def get_recipe(food_mat, rdi_amounts, food_ids, food_names):
# 	amounts, error = op.nnls(food_mat, rdi_amounts)
# 	results = []
# 	for i in range(len(amounts)):
# 		if amounts[i] > 0:
# 			results.append(food_names[i] + " * " + str(amounts[i] * 100) + "g")
# 	return (results, error)

# def filter_data(nut_ids, data):
# 	results = []
# 	for datum in data:
# 		if datum[1] in nut_ids:
# 			results.append(datum)
# 	return results

# def filter_foods(groups, food_ids, food_group_ids, food_names):
# 	new_ids = []
# 	new_group_ids = []
# 	new_names = []
# 	for i in range(len(food_ids)):
# 		if food_group_ids[i] in groups:
# 			new_ids.append(food_ids[i])
# 			new_group_ids.append(food_group_ids[i])
# 			new_names.append(food_names[i])
# 	return (new_ids, new_group_ids, new_names)
                
# def build_food_mat(food_ids, nut_ids, data):
# 	""" Builds a nut-by-food matrix containing nutrient values in foods """
# 	n, m = len(nut_ids), len(food_ids)
# 	mat = np.zeros([n, m])
# 	for datum in data:
# 		food_id, nut_id, amount = datum
# 		#nut_idx = index(nut_ids, nut_id)
# 		#food_idx = index(food_ids, food_id)
# 		#if not nut_idx is None and not food_idx is None:
# 		#	mat[nut_idx][food_idx] = amount
# 		try:
# 			mat[nut_ids.index(nut_id)][food_ids.index(food_id)] = amount
# 		except ValueError:
# 			pass
# 	return mat

# def index(a, v):
# 	""" Finds the index of v in a or returns None """
# 	if v in a:
# 		return a.index(v)
# 	#for i in range(len(a)):
# 	#	if a[i] == v:
# 	#		return i
# 	return None

# def all_indices(a, v):
# 	""" Returns a set of all indices of a that contain v """
# 	result = set()
# 	for i in range(len(a)):
# 		if a[i] == v:
# 			result.add(i)
# 	return result

