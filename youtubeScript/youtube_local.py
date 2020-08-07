import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (10, 8),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)


USER_RANK = 150
RANK_CELL = 1098 #community 2
# RANK_CELL = 535

TOP_10_COMMUNITY_SIZE = [2217, 1900, 1098, 824, 700, 678, 664, 639, 598, 535]

# top user bins size = [3,1,1,3,1,3]
community_number = 0

# TOP_USER_NUMBER = TOP_10_COMMUNITY_SIZE[community_number]


#read community from file
#obtain a list of user id in that community
community_file = "com-youtube.top5000.cmty.txt"
top_10_community_list = []
with open(community_file) as infile:
		for line in infile:
			line_strip = line.strip()
			elements = line_strip.split()
			community_size = len(elements)
			if community_size in TOP_10_COMMUNITY_SIZE:
				elements = list(map(lambda x:int(x), elements))
				top_10_community_list.append(elements)
			# if community_size >=100 and community_size <=120:
			# 	elements = list(map(lambda x:int(x), elements))
			# 	top_10_community_list.append(elements)

G_complete = nx.Graph()

community_1 = top_10_community_list[community_number]

TOP_USER_NUMBER = len(community_1)

#read edge list from the file
complete_graph_file = "com-youtube.ungraph.txt"
edge_list = []

#user id, follower count, following count, following_list
user_info = {}
with open(complete_graph_file) as infile:
		for line in infile:
			if '#' not in line:
				line_strip = line.strip()
				elements = line_strip.split()
				vertex1  = int(elements[0])
				vertex2  = int(elements[1])
				if vertex1 in community_1 and vertex2 in community_1:
					if vertex1 not in user_info.keys():
						user_info[vertex1] = [1,1,[vertex2]]
					else:
						user_info[vertex1][0] = user_info[vertex1][0] + 1 
						user_info[vertex1][1] = user_info[vertex1][1] + 1 
						user_info[vertex1][2].append(vertex2)


					if vertex2 not in user_info.keys():
						user_info[vertex2] = [1,1,[vertex1]]
					else:
						user_info[vertex2][0] = user_info[vertex2][0] + 1 
						user_info[vertex2][1] = user_info[vertex2][1] + 1 
						user_info[vertex2][2].append(vertex1)

#sort the user ID based on follower number
#obtian a list of ranked user id
follower_sorted_key = sorted(user_info,key=lambda x: user_info[x][0],reverse = True)

print(len(follower_sorted_key))
interested_rank_user_id = follower_sorted_key[USER_RANK]

print(interested_rank_user_id)

print(user_info[interested_rank_user_id][2])

follower_count_list  = []
following_count_list = []
interaction_spectral = [0] * RANK_CELL
# average_rank_list	 = []
for user in follower_sorted_key:
	follower_count_list.append(user_info[user][0])
	following_count_list.append(user_info[user][1])

	#spectral
	if user == interested_rank_user_id:
		follower_id_list = user_info[user][2]
		for follower_id in follower_id_list:
			follwer_index = follower_sorted_key.index(follower_id)
			if follwer_index <= RANK_CELL:
				interaction_spectral[follwer_index] = 1

	#average rank
	# average_rank = 0
	# follower_id_list = user_info[user][2]
	# number_of_follower = len(follower_id_list)
	# for follower_id in follower_id_list:
	# 	follwer_index = follower_sorted_key.index(follower_id)
	# 	if follwer_index <= RANK_CELL:
	# 		average_rank = average_rank + follwer_index
	# average_rank = average_rank/number_of_follower
	# average_rank_list.append(average_rank)

	



x = list(range(0,RANK_CELL))
ypos=[0,1,2]
ylabl = [' ','1',' ']

list.sort(following_count_list,reverse = True)

interaction_spectral_filtered = [float('nan') if z==0 else z for z in interaction_spectral]
Top_user_count = following_count_list[0:TOP_USER_NUMBER]

plt.figure(0)
axes = plt.axes()
axes.set_xlim([0,RANK_CELL])
plt.xticks(fontsize=30)
plt.yticks(fontsize=60)
# plt.ylabel('connection',fontsize=30)
plt.scatter(x,interaction_spectral_filtered,[300])
# Set the tick positions
axes.set_yticks(ypos)
# Set the tick labels
axes.set_yticklabels(ylabl)


# plt.figure(1)
# x1 = list(range(0,51))
# y  = [1]*51
# y[0] = 0
# print(y)
# axes = plt.axes()
# axes.set_xlim([1,50])
# axes.set_ylim([0,2])
# plt.xticks(fontsize=25)
# plt.yticks(fontsize=25, visible = False)
# plt.xlabel('consumption rank',fontsize=30)
# # plt.ylabel('connection',fontsize=30)
# plt.scatter(x1,y)

plt.show()