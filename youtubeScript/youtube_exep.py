import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (12, 10),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)


TOP_10_COMMUNITY_SIZE = [2217, 1900, 1098, 824, 700, 678, 664, 639, 598, 535]

TOP_USER_NUMBER = 100

# top user bins size = [3,1,1,3,1,3]
community_number = 4

#read community from file
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


community_1 = top_10_community_list[community_number]

#read edge list from the file
complete_graph_file = "com-youtube.ungraph.txt"
edge_list = []

#user id, follower count, following count
user_info = {}
user_connection = {}

with open(complete_graph_file) as infile:
		for line in infile:
			if '#' not in line:
				line_strip = line.strip()
				elements = line_strip.split()
				vertex1  = int(elements[0]) 
				vertex2  = int(elements[1])
				#check if both vertex/users are in the community
				if vertex1 in community_1 and vertex2 in community_1:
					#if vertex 1 not in the array now
					if vertex1 not in user_info.keys():
						user_info[vertex1] = [1,1]
						user_connection[vertex1] = [vertex2]
					else:
						user_info[vertex1][0] = user_info[vertex1][0] + 1 
						user_info[vertex1][1] = user_info[vertex1][1] + 1 
						user_connection[vertex1].append(vertex2)

					if vertex2 not in user_info.keys():
						user_info[vertex2] = [1,1]
						user_connection[vertex2] = [vertex1]
					else:
						user_info[vertex2][0] = user_info[vertex2][0] + 1 
						user_info[vertex2][1] = user_info[vertex2][1] + 1 
						user_connection[vertex2].append(vertex1)

follower_sorted_key = sorted(user_info, reverse = True, key=lambda x: user_info[x][0])

follower_count_list = []
following_count_list = []
for user in follower_sorted_key:
	follower_count_list.append(user_info[user][0])
	following_count_list.append(user_info[user][1])


x = list(range(0,TOP_USER_NUMBER))

list.sort(following_count_list,reverse = True)

print(len(following_count_list))
	
Top_user_count = following_count_list[0:TOP_USER_NUMBER]

TOP5 = set(user_connection[follower_sorted_key[0]] + user_connection[follower_sorted_key[1]] + user_connection[follower_sorted_key[2]] + user_connection[follower_sorted_key[3]] + user_connection[follower_sorted_key[4]])
print(len(TOP5))
print(len(user_connection[follower_sorted_key[0]]))
print(len(user_connection[follower_sorted_key[1]]))
print(len(user_connection[follower_sorted_key[2]]))



plt.figure(0)
plt.xticks(fontsize=50)
plt.yticks(fontsize=50)
# plt.xlabel('rank',fontsize=50)
plt.ylabel('#following in community',fontsize=50)
plt.scatter(x,Top_user_count,[90])
plt.tight_layout()

# counts, bins = np.histogram(follower_count_list,bins=4)

# print(counts)
# print(bins)

# plt.bar(range(len(counts)), counts)

# plt.hist(follower_count_list,bins =4)
# plt.title("Histogram of Follower")
# plt.xlabel("number of followers",fontsize=30)
# plt.ylabel("number of users",fontsize=30)

plt.show()