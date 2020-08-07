# from TwitterClient import TwitterClient
from networkx.algorithms import community

# import community
import networkx as nx
import matplotlib.pyplot as plt
import copy
import pickle
import itertools


CORE_RATIO_FOLLOWER  = 0.45
CORE_RATIO_FOLLOWING = 0.2

#object that represent a twitter user in our purpose of usage
class user():
	def __init__(self, id, follwowing_list):
		self.id 					= id
		self.follwowing_list 		= follwowing_list
		self.com_follower_number 	= []
		self.com_following_number	= []
		self.is_core 				= False

	# A function that detect if a user in one's list
	def is_following(self,user):
		if user.id in self.follwowing_list:
			return True
		else:
			return False

	#A function that update the number of follower in community
	def update_follower_following_number(self,user_list):
		com_follower  = 0
		com_following = 0

		for user in user_list:
			if user.is_following(self):
				com_follower = com_follower + 1

			if self.is_following(user):
				com_following = com_following + 1

		self.com_follower_number.append(com_follower)
		self.com_following_number.append(com_following)

		if com_follower >= len(user_list)*CORE_RATIO_FOLLOWER and com_following >= len(user_list)*CORE_RATIO_FOLLOWING:
			self.is_core = True



#A function take in a list of user and generate a unweighted directed graph
def unweighted_directed_graph_generator(user_list):
	DG = nx.DiGraph()
	edge_list = []
	for user1 in user_list:
		for user2 in user_list:
			if user1.is_following(user2):
				edge_list.append((user1,user2))
	DG.add_edges_from(edge_list)
	return DG

#A function take in a list of user and generate a unweighted undirected graph
def unweighted_undirected_graph_generator(user_list):
	G = nx.Graph()
	edge_list = set()
	for user1 in user_list:
		for user2 in user_list:
			if mutual_friend(user1,user2):
				edge_list.add((user1.id,user2.id))
	G.add_edges_from(edge_list)
	return G

#A function determine if two users are mutual friends
def mutual_friend(user1, user2):
	if user1.is_following(user2) and user2.is_following(user1):
		return True
	else:
		return False

# A function that read from a line and return a list of user
def read_user(file_name):
	user_list = []
	with open(file_name) as infile:
	    for line in infile:
	    	line = line.strip()
	    	elements = line.split(",")
	    	user_id    = int(elements[1])
	    	user_following_list = elements[2].split(" ")
	    	if len(user_following_list) >= 2:
	    		user_following_list = list(map(int, user_following_list))
	    	user_list.append(user(user_id,user_following_list))
	return user_list

# A function that take in a undirected graph and detect community 
# by using max modularity
def modularity_community_detection_and_write1(graph,outfile_name):
	out_file_name = 'output/'+outfile_name+'.txt'
	list_com   = []
	partition1 = community.best_partition(graph)
	partition2 = community.best_partition(graph)
	node 	  = 0
	with open(out_file_name, 'w') as outfile:
		for com in set(partition1.values()):
			list_nodes1 = [nodes for nodes in partition1.keys() if partition1[nodes] == com]
			list_nodes2 = [nodes for nodes in partition2.keys() if partition2[nodes] == com]
			list_nodes  = list(set(list_nodes1) & set(list_nodes2))
			list_com.append(list_nodes)
			for node in list_nodes:
				outfile.write(str(node)+" ")
			outfile.write("\n")
	return list_com[0],list_com[1],list_com[2],list_com[3],list_com[4]

# A function that take in a undirected graph and detect community 
# by using max modularity
def modularity_community_detection_and_write2(graph,outfile_name):
	out_file_name = 'output/'+outfile_name+'.txt'
	list_com   = []
	partition = community.best_partition(graph)
	node 	  = 0
	with open(out_file_name, 'w') as outfile:
		for com in set(partition.values()):
			list_nodes = [nodes for nodes in partition.keys() if partition[nodes] == com]
			list_com.append(list_nodes)
			for node in list_nodes:
				outfile.write(str(node)+" ")
			outfile.write("\n")
	return list_com


# A function that takes a community and classify the user into core user and leaf users
# def core_user_detect(com, threshold):
# 	out_file_name = 'output/community3_cores.txt'
# 	twitter_client = TwitterClient()
# 	api = twitter_client.get_twitter_client_api()

# 	core_users = []
# 	for u in com:
# 		user_info = api.get_user(user_id = u)
# 		follower_count = user_info.followers_count
# 		if follower_count >= threshold:
# 			core_users.append(u)
# 	with open(out_file_name, 'w') as outfile:
# 		for u in core_users:
# 			outfile.write("%i," %u)
# 		outfile.write("\n")

#A function that return a list of user object from the community 
def community_user(com,user_list):
	com_user 	= set()
	first_seen  = 1
	for user_id in com:
		for u in user_list:
			if u.id == user_id and first_seen:
				com_user.add(u)
				first_seen = 0
		first_seen = 1
	return com_user

#A function that return connectivity between two community 
def interaction_between_community(com1, com2, user_list, file_name):
	com1_interaction = []
	com2_interaction = []

	community1_user  = community_user(com1,user_list)
	community2_user  = community_user(com2,user_list)

	for user1 in community1_user:
		interactio_number = 0
		for user2 in community2_user:
			if user1.is_following(user2):
				interactio_number = interactio_number + 1
		com1_interaction.append(interactio_number)

	for user2 in community2_user:
		interactio_number = 0
		for user1 in community1_user:
			if user2.is_following(user1):
				interactio_number = interactio_number + 1
		com2_interaction.append(interactio_number)

	out_file_name = 'output/'+file_name+'.txt'

	with open(out_file_name, 'w') as outfile:
		outfile.write('AI:')
		for n in com1_interaction:
			outfile.write(str(n))
			outfile.write(',')
		outfile.write("\n")

		outfile.write('Tech:')
		for n in com2_interaction:
			outfile.write(str(n))
			outfile.write(',')
		outfile.write("\n")	
					

	return com1_interaction,com2_interaction


def community_follower_count(com_users):
	count_list = {}
	for user in com_users:
		user.update_follower_following_number(com_users)
		count_list[user.id] = user.com_follower_number[0]
	return count_list

def community_following_count(com_users):
	count_list = {}
	for user in com_users:
		user.update_follower_following_number(com_users)
		count_list[user] = user.com_following_number[0]
	return count_list

#this function detect the following and follower a user has on a community
def inter_community_follower(user, com_users):
	following = []
	follower  = []
	for u in com_users:
		if user.is_following(u):
			following.append(u)

		if u.is_following(user):
			follower.append(u)

	return follower,following

def write_com_with_core(user_list,outfile):
	for u in user_list:
			outfile.write(str(u.id)+":")
			if u.is_core == True:
				outfile.write("core"+" ")
			else:
				outfile.write("leaf"+" ")
	outfile.write("\n")

def read_user_id(user_list, user_id):
	for u in user_list:
		if u.id == user_id:
			return u
		else:
			return None

def write_coms(file_name,user_name):
	
	out_file_name = 'output/'+user_name+'_Com_stat.txt'

	user_list = read_user(file_name)

	graph     = unweighted_undirected_graph_generator(user_list)

	partition  = community.greedy_modularity_communities(graph)

	com_user_list = []
	
	for com in partition:
		com_user = community_user(com,user_list)
		com_user_list.append(com_user)

	for com in com_user_list:
		com_count = community_follower_count(com)


	with open(out_file_name, 'w') as outfile:
		for com in com_user_list:
			write_com_with_core(com,outfile)


if __name__ == '__main__':

	#AI com
	Hardmaru_file 	= "input/hardmaru_graph_0_620.txt"


	hardmaru_user_list	= read_user(Hardmaru_file)


	Hardmaru_graph 	= unweighted_undirected_graph_generator(hardmaru_user_list)



	#Cluter the neighbor
	# Hardmaru_partition	= community.greedy_modularity_communities(Hardmaru_graph)
	Hardmaru_partition	= community.label_propagation_communities(Hardmaru_graph)

	print(Hardmaru_partition)



	# Andrew_AIneighbor 	= Andrew_partition[0]
	# Ian_AIneighbor 		= Ian_partition[0]|Ian_partition[2]
	# Lecun_AIneighbor 	= Lecun_partition[0]|Lecun_partition[1]|Lecun_partition[2]|Lecun_partition[3]
	# Jeff_AIneighbor		= Jeff_partition[1]
	# Russ_AIneighbor		= Russ_partition[0]|Russ_partition[1]|Russ_partition[2]
	# Hardmaru_AIneighbor = Hardmaru_partition[0]|Hardmaru_partition[2]

	# AIcom 				= Andrew_AIneighbor|Ian_AIneighbor|Lecun_AIneighbor|Jeff_AIneighbor|Russ_AIneighbor|Hardmaru_AIneighbor

	# # AIcom_user	 = community_user(AIcom,user_set)
	# # AIcom_counts = community_follower_count(AIcom_user)

	# # out_file_name = 'output/AIcom_stat.txt'
	# # size = len(AIcom_user)

	# # with open(out_file_name, 'w') as outfile:
	# # 	outfile.write("%i," %size)
	# # 	write_com_with_core(AIcom_user,outfile)

	# TECHcom	= Jeff_partition[0] | Ian_partition[1] | Andrew_partition[1] | Tim_partition[0]

	# AIfollowing, TECHfollowing = interaction_between_community(AIcom,TECHcom,user_set,"AI_Tech_stat")

