import json
import os
import re
import nltk
import collections

from nltk.corpus import stopwords
from wordcloud import WordCloud
from collections import Counter

import twitter_client as tc
import matplotlib.pyplot as plt
import networkx as nx


def read_user_following_list(file_name):
	"""read the following information of neighbor

	Parameters
	----------
	file_name : files that contain information 

	Returns
	-------
	dictionary that contain following information
	{user_id:following information}
	"""
	user_following_info = {}
	with open(file_name) as infile:
		for line in infile:
			line = line.strip()
			elements = line.split(",")
			user_index = int(elements[0])
			user_id    = int(elements[1])
			user_following_list = elements[2].split(" ")
			if len(user_following_list) >= 2:
				user_following_info[user_id] = list(map(int, user_following_list))
			
	return user_following_info


def edge_list_undirected(following_info,user_group):
	"""create edge list from following information for a given user group

	Parameters
	----------
	user_group : a set/list of user id
	following_info : a dictionary that contain following info of this user group

	Returns
	-------
	edge list for user_group:
		create an edge iff two user follow each other
	"""
	edge_list = []

	for user1 in user_group:
		for user2 in user_group:
			if user1 == user2:
				pass
			else:
				if user2 in following_info[user1] and user1 in following_info[user2]:
					edge12 = (user1, user2)
					edge21 = (user2, user1)
					if (not edge12 in edge_list) and (not edge21 in edge_list):
						edge_list.append(edge12)

	return edge_list

def edge_list_directed(following_info,user_group):
	"""create edge list from following information for a given user group

	Parameters
	----------
	user_group : a set/list of user id
	following_info : a dictionary that contain following info of this user group

	Returns
	-------
	edge list for user_group:
		create an edge(user1, user2) iff user1 follow user2
	"""
	edge_list = []

	for user1 in user_group:
		for user2 in user_group:
			if user1 == user2:
				pass
			else:
				if user2 in following_info[user1]:
					edge = (user1, user2)
					edge_list.append(edge)
		
	return edge_list

def cross_edge(neighbor_degress_dist,cluster_degress_dist):
	"""create edge list from following information for a given user group

	Parameters
	----------
	user_group : a set/list of user id
	following_info : a dictionary that contain following info of this user group

	Returns
	-------
	edge list for user_group:
		create an edge(user1, user2) iff user1 follow user2
	"""
	edge_list = []

	for user1 in user_group:
		for user2 in user_group:
			if user1 == user2:
				pass
			else:
				if user2 in following_info[user1]:
					edge = (user1, user2)
					edge_list.append(edge)
		
	return edge_list
