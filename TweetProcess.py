import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import GraphScript as gs

import json
import os
import re

class TweetAnalyzer():

    def __init__(self):
        self.RETWEET_FORMAT = r"^RT @.*[:]"
        self.RETWEET_USER = r"@([a-zA-Z0-9_]{1,15})"

    #given a list of tweets, text only, count the number of retweet among the user 
    #return a list of user and their retweet count from this community
    def count_retweet(self, tweets_list):

        retweet_count = {}

        for tweets in tweets_list:
            if self.is_retweet(tweets):             
                search  = re.findall(self.RETWEET_USER, tweets)
                if search:
                    source = search[0] #last element
                    if source in retweet_count.keys():
                        retweet_count[source] = retweet_count[source] + 1
                    else:   
                        retweet_count[source] = 1

        return retweet_count


    #tweet list is a list of tweet object
    def production_count(self):

        tweets_list = self.collect_production_related_tweets()

        os.chdir('D:/github/TwitterExperiment/TwitterScript')

        interested_user = []
        with open("result/verified_AIuser.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                user_screen_name     = line.split(',')[0]
                interested_user.append(user_screen_name)

        production_count = {}
        for tweet_obj in tweets_list:
            if self.is_retweet(tweet_obj['full_text']):             
                search  = re.findall(self.RETWEET_USER, tweet_obj['full_text'])
                if search:
                    source = search[0] #last element
                    if source in production_count.keys():
                        production_count[source] = production_count[source] + 1
                    else:   
                        production_count[source] = 1
            elif tweet_obj["is_quote_status"]:
                try:
                    quote_info = tweet_obj['quoted_status']
                except:
                    quote_info = False

                if quote_info:
                    source  = quote_info['user']['screen_name']
                    if source in production_count.keys():
                        production_count[source] = production_count[source] + 1
                    else:   
                        production_count[source] = 1
            # elif tweet_obj["in_reply_to_screen_name"] != None:
            #     source  = tweet_obj["in_reply_to_screen_name"]
            #     if source in production_count.keys():
            #         production_count[source] = production_count[source] + 1
            #     else:   
            #         production_count[source] = 1

        interested_user_count = {} 
        for user in interested_user:
            if user in production_count.keys():
                interested_user_count[user] = production_count[user]

        sorted_interested_user_count = sorted(interested_user_count, reverse=True, key=lambda x: interested_user_count[x])

        with open('result/AIuser_production.txt','w', encoding = 'utf-8') as outfile:
            for user in sorted_interested_user_count:
                    outfile.write(user)
                    outfile.write(',')
                    outfile.write(str(interested_user_count[user]))
                    outfile.write('\n')

        return production_count

    def load_tweet(self,tweet_json):
        if tweet_json:
            try:
                obj          = json.loads(tweet_json)
                return obj
            except:
                print('bad json: ', tweet_json)
                return False

    def clean_tweets(self, tweets_obj):
            if "full_text" in tweets_obj.keys():
                tweet_text   = str(tweets_obj["full_text"])
                tweet_text   = tweet_text.strip()
                tweet_text   = re.sub(r'https://t.co/(\S)*', '', tweet_text)
                tweet_text   = re.sub(r'\n*', '', tweet_text)
                return tweet_text
            else:
                return False

    # Given a tweet text, determine if it is a retweet from other user
    def is_retweet(self,tweets):
        match = re.search(self.RETWEET_FORMAT,tweets)
        if match:
            return True
        else:
            return False


    def monthToNum(self,shortMonth):
        return{
                'Jan' : 1,
                'Feb' : 2,
                'Mar' : 3,
                'Apr' : 4,
                'May' : 5,
                'Jun' : 6,
                'Jul' : 7,
                'Aug' : 8,
                'Sep' : 9, 
                'Oct' : 10,
                'Nov' : 11,
                'Dec' : 12
        }[shortMonth]


    def is_within_time(self,created_at, year, month, month_period):
        tweet_month      = int(created_at.month)
        tweet_year       = int(created_at.year)

        if tweet_year != year:
            return False
        elif tweet_month < month or tweet_month > month + month_period:
            return False
        else:
            return True

    def collect_retweets(self,path):

        os.chdir(path)

        files_arr   = os.listdir()
        Tweets_list = []
        for file in files_arr:
            with open(file,"r") as infile:
                for line in infile:
                    tweet = self.clean_tweets(line)
                    if tweet:
                        if self.is_retweet(tweet):
                            Tweets_list.append(tweet)

        return Tweets_list

    #collect all production related tweets from a dir with quote
    def collect_production_related_tweets(self):

        interested_user = []
        with open("result/verified_AIuser.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                user_screen_name     = line.split(',')[0]
                interested_user.append(user_screen_name)

        AI_user_id_name_map = {}
        AIcom_id = set()
        #get list of user screen name and id mapping
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                user_id = int(eles[1])
                user_creen_name = eles[0]
                AI_user_id_name_map[user_creen_name] = user_id
                if user_creen_name in interested_user:
                    AIcom_id.add(user_id)


        os.chdir('tweets/AI_tweets')

        files_arr   = os.listdir()
        Tweets_list = []
        for file in files_arr:
            user_id = int(file.split('_')[0])
            if user_id in AIcom_id:
                with open(file,"r") as infile:
                    for line in infile:
                        tweet_obj = self.load_tweet(line)
                        if tweet_obj != False:
                            #count quote
                            if tweet_obj["is_quote_status"]:
                                Tweets_list.append(tweet_obj)

                            #count retweet
                            tweet = self.clean_tweets(tweet_obj)
                            if tweet:
                                if self.is_retweet(tweet):
                                    Tweets_list.append(tweet_obj)
        return Tweets_list

    #Given a list of retweet and remove the oens from the give user_list
    def remove_community_tweet(self, user_list, tweet_list):
        new_tweet_list = []
        for tweet in tweet_list:
            search  = re.findall(self.RETWEET_USER, tweet)
            if search:
                source = search[0]
                if source not in user_list:
                    new_tweet_list.append(tweet)
        return new_tweet_list

    #Given a list of retweet and find the one that has been retweet the most
    def tweet_retweet_count(self, tweet_list):

        retweet_count       = {}
        tweet_set           = set(tweet_list)
        tweet_num           = len(tweet_set)
        retweet_sum         = 0

        for tweet in tweet_set:
            count = tweet_list.count(tweet)
            retweet_count[tweet] = count
            retweet_sum = retweet_sum + count
        return retweet_count, retweet_sum/tweet_num

    #remove the AI and TECH user from the retweet user set
    def remove_ranked_user(self):

        user_list = set()
        user_dict = {}

        #get list of user
        with open('result/AI_retweet_rank.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                line = line.split(',')
                user_name = line[0]
                user_list.add(user_name)
                user_dict[user_name] = int(line[1])

        AI_user_list = set()

        #get list of user
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                user_creen_name = line.strip()
                AI_user_list.add(user_creen_name)

        TECH_user_list = set()

        #get list of user
        with open('input/TECHuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                user_creen_name = line.strip()
                TECH_user_list.add(user_creen_name)

        remain_user_key = user_list - AI_user_list - TECH_user_list
        remain_user_dict = {}

        for user in remain_user_key:
            remain_user_dict[user] = int(user_dict[user])

        sorted_user = sorted(remain_user_dict, reverse=True, key=lambda x: remain_user_dict[x])

        with open('result/remain_user.txt','w', encoding = 'utf-8') as outfile:
            for u in sorted_user:
                outfile.write(u)
                outfile.write(',')
                outfile.write(str(remain_user_dict[u]))
                outfile.write('\n')

    def remove_retweet(self):

        Tweets_list = []

        #get list of tweet
        with open('result/AIretweet.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                Tweets = line.strip()
                Tweets_list.append(Tweets)

        AI_user_list = set()
        #get list of user
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                user_creen_name = line.strip()
                AI_user_list.add(user_creen_name)

        TECH_user_list = set()

        #get list of user
        with open('input/TECHuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                user_creen_name = line.strip()
                TECH_user_list.add(user_creen_name)

        remove_AI = self.remove_community_tweet(AI_user_list, Tweets_list)
        remove_TE = self.remove_community_tweet(TECH_user_list, remove_AI)

        retweet_rank = self.tweet_retweet_count(remove_TE)

        sorted_count = sorted(retweet_rank, reverse=True,key=lambda x: retweet_rank[x])

        with open('result/OTHER_retweet_TweetRank.txt','w',encoding = 'utf-8') as outfile:
            for tweet in sorted_count:
                if tweet in retweet_rank.keys():
                    outfile.write(str(tweet))
                    outfile.write(',')
                    outfile.write(str(retweet_rank[tweet]))
                    outfile.write('\n')

    def production_rank(self):

        AI_user_name = []
        #get list of user screen name and id mapping
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                user_id = int(eles[1])
                user_creen_name = eles[0]
                AI_user_name.append(user_creen_name)

        user_dict = {}
        #get list of user
        with open('result/AI_retweet_count.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                line = line.split(',')
                user_name = line[0]
                user_dict[user_name] = int(line[1])

        AI_user_dict = {}
        for u in AI_user_name:
            if u in user_dict.keys():
                AI_user_dict[u] = user_dict[u]

        sorted_count = sorted(AI_user_dict, reverse=True,key=lambda x: AI_user_dict[x])

        with open("result/AIuser_production.txt","w",encoding = 'utf-8') as outfile:
            for user in sorted_count:
                if user in AI_user_dict.keys():
                    outfile.write(str(user))
                    outfile.write(',')
                    outfile.write(str(AI_user_dict[user]))
                    outfile.write('\n')

    def consumption_rank(self):

        interested_user = []
        with open("result/verified_AIuser.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                user_screen_name     = line.split(',')[0]
                interested_user.append(user_screen_name)

        AI_user_id_name_map = {}
        AIcom_id = set()
        #get list of user screen name and id mapping
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                user_id = int(eles[1])
                user_creen_name = eles[0]
                AI_user_id_name_map[user_id] = user_creen_name
                if user_creen_name in interested_user:
                    AIcom_id.add(user_id)

        print(AIcom_id)

        os.chdir('tweets/AI_tweets/')
        files_arr   = os.listdir()
        AI_user_consumption = {}
        for file in files_arr:
            user_id = int(file.split('_')[0])
            if user_id in AIcom_id:
                retweet_count = 0
                reply_count   = 0
                quote_count   = 0
                with open(file,"r") as infile:
                    for line in infile:
                        tweet_obj = self.load_tweet(line)
                        if tweet_obj != False:
                            #count quote
                            if tweet_obj["is_quote_status"]:
                                quote_count = quote_count + 1

                            #count reply
                            reply_user_id = tweet_obj["in_reply_to_user_id"]
                            if reply_user_id != None and reply_user_id in AIcom_id:
                                reply_count = reply_count + 1

                            #count retweet
                            tweet = self.clean_tweets(tweet_obj)
                            if tweet:
                                if self.is_retweet(tweet):
                                    retweet_count = retweet_count + 1


                    if user_id in AI_user_id_name_map.keys():
                        AI_user_consumption[AI_user_id_name_map[user_id]] = (retweet_count,reply_count,quote_count)

        sorted_count = sorted(AI_user_consumption, reverse=True,key=lambda x: AI_user_consumption[x][1])

            
        os.chdir('D:/github/TwitterExperiment/TwitterScript')
        with open('result/AIuser_consumption.txt','w', encoding = 'utf-8') as outfile:
            outfile.write("###user name, retweet number, reply number, quote number\n")
            for user in sorted_count:
                if user in AI_user_consumption.keys():
                        outfile.write(str(user))
                        outfile.write(',')
                        outfile.write(str(AI_user_consumption[user][0]))
                        outfile.write(',')
                        outfile.write(str(AI_user_consumption[user][1]))
                        outfile.write(',')
                        outfile.write(str(AI_user_consumption[user][2]))
                        outfile.write('\n')
                            


    def following_rank(self):

        interested_user = []
        with open("result/verified_AIuser.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                user_screen_name     = line.split(',')[0]
                interested_user.append(user_screen_name)

        AIcom_id_list = set()
        AI_user_id_screen_name_map = {}
        #get list of user with name and id
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                line = line.split(',')
                user_creen_name = line[0]
                user_id         = line[1]
                AI_user_id_screen_name_map[user_id] = user_creen_name
                if user_creen_name in interested_user:
                    AIcom_id_list.add(int(user_id))


        #AI com
        Feifei_file     = "D:/github/TwitterExperiment/GraphScript/input/drfeifei_graph_0_253.txt"
        Andrew_file     = "D:/github/TwitterExperiment/GraphScript/input/andrew_graph_0_423.txt"
        Lecun_file      = "D:/github/TwitterExperiment/GraphScript/input/ylecun_graph_0_225.txt"
        Ian_file        = "D:/github/TwitterExperiment/GraphScript/input/goodfellow_ian_graph_0_1041.txt"
        Jeff_file       = "D:/github/TwitterExperiment/GraphScript/input/JeffDean_graph_0_2049.txt"
        Russ_file       = "D:/github/TwitterExperiment/GraphScript/input/rsalakhu_graph_0_100.txt"
        Hardmaru_file   = "D:/github/TwitterExperiment/GraphScript/input/hardmaru_graph_0_620.txt"
        Mile_File       = "D:/github/TwitterExperiment/GraphScript/input/Miles_Brundage_graph_0_3170.txt"
        Nando_File      = "D:/github/TwitterExperiment/GraphScript/input/NandoDF_graph_0_305.txt"
        Hugo_File       = "D:/github/TwitterExperiment/GraphScript/input/hugo_larochelle_graph_0_490.txt"
        Danilo_File     = "D:/github/TwitterExperiment/GraphScript/input/DeepSpiker_graph_0_849.txt"


        andrew_user_list    = gs.read_user(Andrew_file)
        ian_user_list       = gs.read_user(Ian_file)
        lecun_user_list     = gs.read_user(Lecun_file)
        jeff_user_list      = gs.read_user(Jeff_file)
        russ_user_list      = gs.read_user(Russ_file)
        hardmaru_user_list  = gs.read_user(Hardmaru_file)

        user_set  = set(andrew_user_list+ian_user_list+lecun_user_list+jeff_user_list+russ_user_list+hardmaru_user_list)

        AIcom_user  = gs.community_user(list(AIcom_id_list),user_set)

        ID_count   = gs.community_following_count(AIcom_user)
        sorted_count = sorted(ID_count, reverse=True,key=lambda x: ID_count[x])
        
        with open('result/AIuser_following_rank.txt','w', encoding = 'utf-8') as outfile:
            for user in sorted_count:
                print(str(user))
                if str(user.id) in AI_user_id_screen_name_map.keys():
                    print("i am here")
                    outfile.write(str(AI_user_id_screen_name_map[str(user.id)]))
                    outfile.write(',')
                    outfile.write(str(ID_count[user]))
                    outfile.write('\n')

    def follower_rank(self):

        interested_user = []
        with open("result/verified_AIuser.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                user_screen_name     = line.split(',')[0]
                interested_user.append(user_screen_name)

        AIcom_id_list = set()
        AI_user_id_screen_name_map = {}
        #get list of user with name and id
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                line = line.split(',')
                user_creen_name = line[0]
                user_id         = line[1]
                AI_user_id_screen_name_map[user_id] = user_creen_name
                if user_creen_name in interested_user:
                    AIcom_id_list.add(int(user_id))

        #AI com
        Feifei_file     = "D:/github/TwitterExperiment/GraphScript/input/drfeifei_graph_0_253.txt"
        Andrew_file     = "D:/github/TwitterExperiment/GraphScript/input/andrew_graph_0_423.txt"
        Lecun_file      = "D:/github/TwitterExperiment/GraphScript/input/ylecun_graph_0_225.txt"
        Ian_file        = "D:/github/TwitterExperiment/GraphScript/input/goodfellow_ian_graph_0_1041.txt"
        Jeff_file       = "D:/github/TwitterExperiment/GraphScript/input/JeffDean_graph_0_2049.txt"
        Russ_file       = "D:/github/TwitterExperiment/GraphScript/input/rsalakhu_graph_0_100.txt"
        Hardmaru_file   = "D:/github/TwitterExperiment/GraphScript/input/hardmaru_graph_0_620.txt"
        Mile_File       = "D:/github/TwitterExperiment/GraphScript/input/Miles_Brundage_graph_0_3170.txt"
        Nando_File      = "D:/github/TwitterExperiment/GraphScript/input/NandoDF_graph_0_305.txt"
        Hugo_File       = "D:/github/TwitterExperiment/GraphScript/input/hugo_larochelle_graph_0_490.txt"
        Danilo_File     = "D:/github/TwitterExperiment/GraphScript/input/DeepSpiker_graph_0_849.txt"


        andrew_user_list    = gs.read_user(Andrew_file)
        ian_user_list       = gs.read_user(Ian_file)
        lecun_user_list     = gs.read_user(Lecun_file)
        jeff_user_list      = gs.read_user(Jeff_file)
        russ_user_list      = gs.read_user(Russ_file)
        hardmaru_user_list  = gs.read_user(Hardmaru_file)

        user_set  = set(andrew_user_list+ian_user_list+lecun_user_list+jeff_user_list+russ_user_list+hardmaru_user_list)

        AIcom_user  = gs.community_user(list(AIcom_id_list),user_set)

        ID_count   = gs.community_follower_count(AIcom_user)
        sorted_count = sorted(ID_count, reverse=True,key=lambda x: ID_count[x])
        
        with open('result/AIuser_follower_rank.txt','w', encoding = 'utf-8') as outfile:
            for user in sorted_count:
                if str(user) in AI_user_id_screen_name_map.keys():
                    outfile.write(str(AI_user_id_screen_name_map[str(user)]))
                    outfile.write(',')
                    outfile.write(str(ID_count[user]))
                    outfile.write('\n')

    def mutual_connection_rank(self):

        interested_user = []
        with open("result/verified_AIuser.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                user_screen_name     = line.split(',')[0]
                interested_user.append(user_screen_name)

        AIcom_id_list = set()
        AI_user_id_screen_name_map = {}
        #get list of user with name and id
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                line = line.split(',')
                user_creen_name = line[0]
                user_id         = line[1]
                AI_user_id_screen_name_map[user_id] = user_creen_name
                if user_creen_name in interested_user:
                    AIcom_id_list.add(int(user_id))

        #AI com
        Feifei_file     = "D:/github/TwitterExperiment/GraphScript/input/drfeifei_graph_0_253.txt"
        Andrew_file     = "D:/github/TwitterExperiment/GraphScript/input/andrew_graph_0_423.txt"
        Lecun_file      = "D:/github/TwitterExperiment/GraphScript/input/ylecun_graph_0_225.txt"
        Ian_file        = "D:/github/TwitterExperiment/GraphScript/input/goodfellow_ian_graph_0_1041.txt"
        Jeff_file       = "D:/github/TwitterExperiment/GraphScript/input/JeffDean_graph_0_2049.txt"
        Russ_file       = "D:/github/TwitterExperiment/GraphScript/input/rsalakhu_graph_0_100.txt"
        Hardmaru_file   = "D:/github/TwitterExperiment/GraphScript/input/hardmaru_graph_0_620.txt"
        Mile_File       = "D:/github/TwitterExperiment/GraphScript/input/Miles_Brundage_graph_0_3170.txt"
        Nando_File      = "D:/github/TwitterExperiment/GraphScript/input/NandoDF_graph_0_305.txt"
        Hugo_File       = "D:/github/TwitterExperiment/GraphScript/input/hugo_larochelle_graph_0_490.txt"
        Danilo_File     = "D:/github/TwitterExperiment/GraphScript/input/DeepSpiker_graph_0_849.txt"


        andrew_user_list    = gs.read_user(Andrew_file)
        ian_user_list       = gs.read_user(Ian_file)
        lecun_user_list     = gs.read_user(Lecun_file)
        jeff_user_list      = gs.read_user(Jeff_file)
        russ_user_list      = gs.read_user(Russ_file)
        hardmaru_user_list  = gs.read_user(Hardmaru_file)

        user_set  = set(andrew_user_list+ian_user_list+lecun_user_list+jeff_user_list+russ_user_list+hardmaru_user_list)

        AIcom_user  = gs.community_user(list(AIcom_id_list),user_set)

        connection_count = {}
        for user1 in AIcom_user:
            connection_count[user1.id] = 0
            for user2 in AIcom_user:
                if gs.mutual_friend(user1,user2):
                    connection_count[user1.id] = connection_count[user1.id] + 1

        sorted_count = sorted(connection_count, reverse=True,key=lambda x: connection_count[x])
        with open('result/AIuser_mutual_connection_rank.txt','w', encoding = 'utf-8') as outfile:
            for user in sorted_count:
                if str(user) in AI_user_id_screen_name_map.keys():
                    outfile.write(str(AI_user_id_screen_name_map[str(user)]))
                    outfile.write(',')
                    outfile.write(str(int(connection_count[user]/2)))
                    outfile.write('\n')


    def rank_comparison(self):

        TOP = 1400

        following_rank = {}
        with open('handpickedAIresult/AIuser_following_rank.txt','r', encoding = 'utf-8') as infile:
            following_ranking = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if following_ranking <= TOP:
                    following_rank[eles[0]] = following_ranking
                    following_ranking = following_ranking + 1

        following_keys = set(following_rank.keys())

        follower_rank = {}
        with open('handpickedAIresult/AIuser_follower_rank.txt','r', encoding = 'utf-8') as infile:
            follower_ranking = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if follower_ranking <= TOP:
                    follower_rank[eles[0]] = follower_ranking
                    follower_ranking = follower_ranking + 1

        follower_keys = set(follower_rank.keys())

        production_rank = {}

        with open('handpickedAIresult/AI_production_utility.txt','r', encoding = 'utf-8') as infile:
            production_ranking = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if production_ranking <= TOP:
                    production_rank[eles[0]] = production_ranking
                    production_ranking = production_ranking + 1

        production_keys = set(production_rank.keys())

        consumption_rank = {}

        with open('handpickedAIresult/AIuser_consumption(withReplyAndQuote)_rank.txt','r', encoding = 'utf-8') as infile:
        # with open('result/AIuser_consumption_rank.txt','r', encoding = 'utf-8') as infile:
            consumption_ranking = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if consumption_ranking <= TOP:
                    consumption_rank[eles[0]] = consumption_ranking
                    consumption_ranking = consumption_ranking + 1

        consumption_keys = set(consumption_rank.keys())

        acitvity_count = {}
        with open('handpickedAIresult/AIuser_activity_measure.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                eles = line.split(',')
                acitvity_count[eles[0]] = int(eles[1])

        common_keys = set.intersection(following_keys,follower_keys,production_keys,consumption_keys,acitvity_count)

        following       = []
        follower        = []
        consumption     = []
        production      = []
        activity        = []

        with open("handpickedAIresult/users_in_different_ranks.txt","w") as outfile:
            outfile.write("user name, following rank, follower rank, production rank, consumption rank \n")
            for user in common_keys:
                outfile.write(user)
                outfile.write(',')
                outfile.write(str(following_rank[user]))
                outfile.write(',')
                outfile.write(str(follower_rank[user]))
                outfile.write(',')
                outfile.write(str(production_rank[user]))
                outfile.write(',')
                outfile.write(str(consumption_rank[user]))
                outfile.write(',')
                outfile.write(str(acitvity_count[user]))
                outfile.write('\n')

                following.append(following_rank[user])
                follower.append(follower_rank[user])
                consumption.append(production_rank[user])
                production.append(consumption_rank[user])
                activity.append(acitvity_count[user])

        sorted_user = sorted(follower_rank, key=lambda x: follower_rank[x])

        with open("handpickedAIresult/outliner_spot.txt","w") as outfile:
            for u in sorted_user:
                outfile.write(u)
                outfile.write(',')
                outfile.write(str(follower_rank[u]))
                outfile.write(',')
                outfile.write(str(following_rank[u]))
                outfile.write('\n')

        plt.figure(0)
        plt.title('x = follower, y = following')
        plt.scatter(follower,following)

        plt.figure(1)
        plt.title('x = follower, y = production')
        plt.scatter(follower,production)

        plt.figure(2)
        plt.title('x = following, y = consumption')
        plt.scatter(following,consumption)

        plt.figure(3)
        plt.title('x = production, y = consumption')
        plt.scatter(production,consumption)

        plt.figure(4)
        plt.title('x = follower, y = activity')
        plt.scatter(production,consumption)

        plt.figure(5)
        plt.title('x = following, y = activity')
        plt.scatter(production,consumption)

        plt.show()

    def rank_comparison_activity_filtered_rank(self):

        TOP = 1400

        # filtered_user  = {}
        # with open("handpickedAIresult/outliner_spot.txt","r") as infile:
        #     for line in infile:
        #         eles = line.split(',')
        #         filtered_user[eles[0]] = 0


        acitvity_count = {}
        with open('handpickedAIresult/AIuser_activity_measure.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                eles = line.split(',')
                acitvity_count[eles[0]] = int(eles[1])

        following_rank = {}
        with open('handpickedAIresult/AIuser_following_rank.txt','r', encoding = 'utf-8') as infile:
            following_ranking = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if following_ranking <= TOP:
                    if eles[0] in acitvity_count.keys():
                        following_rank[eles[0]] = following_ranking
                        following_ranking = following_ranking + 1

        following_keys = set(following_rank.keys())

        follower_rank = {}
        with open('handpickedAIresult/AIuser_follower_rank.txt','r', encoding = 'utf-8') as infile:
            follower_ranking = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if follower_ranking <= TOP:
                    if eles[0] in acitvity_count.keys():
                        follower_rank[eles[0]] = follower_ranking
                        follower_ranking = follower_ranking + 1

        follower_keys = set(follower_rank.keys())

        production_rank = {}

        with open('handpickedAIresult/AIuser_production_utility.txt','r', encoding = 'utf-8') as infile:
            production_ranking = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if production_ranking <= TOP:
                    if eles[0] in acitvity_count.keys():
                        production_rank[eles[0]] = production_ranking
                        production_ranking = production_ranking + 1

        production_keys = set(production_rank.keys())

        consumption_rank = {}

        with open('handpickedAIresult/AIuser_consumption(withReplyAndQuote)_rank.txt','r', encoding = 'utf-8') as infile:
            consumption_ranking = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if consumption_ranking <= TOP:
                    if eles[0] in acitvity_count.keys():
                        consumption_rank[eles[0]] = consumption_ranking
                        consumption_ranking = consumption_ranking + 1

        consumption_keys = set(consumption_rank.keys())

        common_keys = set.intersection(following_keys,follower_keys,production_keys,consumption_keys,acitvity_count,acitvity_count)

        following       = []
        follower        = []
        consumption     = []
        production      = []
        activity        = []

        with open("handpickedAIresult/users_in_different_ranks_filtered.txt","w") as outfile:
            outfile.write("user name, following rank, follower rank, production rank, consumption rank \n")
            for user in common_keys:
                outfile.write(user)
                outfile.write(',')
                outfile.write(str(following_rank[user]))
                outfile.write(',')
                outfile.write(str(follower_rank[user]))
                outfile.write(',')
                outfile.write(str(production_rank[user]))
                outfile.write(',')
                outfile.write(str(consumption_rank[user]))
                outfile.write(',')
                outfile.write(str(acitvity_count[user]))
                outfile.write('\n')

                following.append(following_rank[user])
                follower.append(follower_rank[user])
                consumption.append(production_rank[user])
                production.append(consumption_rank[user])
                activity.append(acitvity_count[user])

        sorted_user = sorted(follower_rank, key=lambda x: follower_rank[x])


        plt.figure(0)
        plt.title('x = follower, y = following')
        plt.scatter(follower,following)

        plt.figure(1)
        plt.title('x = follower, y = production')
        plt.scatter(follower,production)

        plt.figure(2)
        plt.title('x = following, y = consumption')
        plt.scatter(following,consumption)

        plt.figure(3)
        plt.title('x = production, y = consumption')
        plt.scatter(production,consumption)

        plt.figure(4)
        plt.title('x = consumption, y = activity')
        plt.scatter(consumption,activity)

        plt.figure(5)
        plt.title('x = production, y = activity')
        plt.scatter(production,activity)

        plt.figure(6)
        plt.title('x = follower, y = activity')
        plt.scatter(follower,activity)

        plt.figure(7)
        plt.title('x = following, y = activity')
        plt.scatter(following,activity)

        plt.show()

    def metric_comparison_activity_filtered(self):
        
        TOP = 15

        #filtered users
        filtered_user  = {}
        with open("result/verified_AIuser.txt","r") as infile:
            for line in infile:
                eles = line.split(',')
                filtered_user[eles[0]] = 0

        filtered_user_keys = filtered_user.keys()
        print(len(filtered_user_keys))

        #active user
        activity_count = {}
        with open('result/AIuser_activity_measure.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                eles = line.split(',')
                activity_count[eles[0]] = int(eles[1])

        activity_keys = activity_count.keys()

        #get a list of count of popular tweet that user are responsible for
        popular_tweet_count = {}
        with open("result/propogation_count.txt","r") as infile:
            for line in infile:
                line = line.strip()
                eles  = line.split(',')
                popular_tweet_count[eles[0]] = int(eles[1])

        popular_tweet_key = popular_tweet_count.keys()

        #number users follow
        following_rank = {}
        with open('result/AIuser_following_rank.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if eles[0] in filtered_user_keys:
                    following_rank[eles[0]] = int(eles[1])

        following_keys = set(following_rank.keys())

        #number of mutual connection
        mutual_connection_rank = {}
        with open('result/AIuser_mutual_connection_rank.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if eles[0] in filtered_user_keys:
                    mutual_connection_rank[eles[0]] = int(eles[1])

        mutual_connection_keys = set(mutual_connection_rank.keys())

        print(len(following_keys))

        #number of follower
        follower_rank = {}
        with open('result/AIuser_follower_rank.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if eles[0] in filtered_user_keys:
                    follower_rank[eles[0]] = int(eles[1])

        follower_keys = set(follower_rank.keys())

        print(len(follower_keys))

        #production utility
        production_rank = {}
        core_detect    ={}
        index  = 1
        with open('result/AIuser_production.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if eles[0] in filtered_user_keys:
                    production_rank[eles[0]] = int(eles[1])
                    if index <= TOP:
                        core_detect[eles[0]] = 'core'
                    else:
                        core_detect[eles[0]] = 'leaf'
                    index = index + 1

        production_keys = set(production_rank.keys())

        print(len(production_keys))

        #consumption utility
        consumption_rank = {}
        with open('result/AIuser_consumption.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if eles[0] in filtered_user_keys:
                    consumption_rank[eles[0]] = (int(eles[1]),int(eles[2]),int(eles[3]))

        consumption_keys = set(consumption_rank.keys())

        common_keys = set.intersection(following_keys,follower_keys,production_keys,consumption_keys,filtered_user_keys,popular_tweet_key)

        print(len(common_keys))

        with open("result/remain_user.txt","w") as outfile:
            for u in common_keys:
                outfile.write(u)
                outfile.write('\n')

        following               = []
        follower                = []
        consumption_retweet     = []
        consumption_reply       = []
        consumption_quote       = []
        consumption_reply_quote = []
        consumption_reply_retweet = []
        production              = []
        activity                = []
        popular_tweet           = []
        mutual_connection       = []

        sorted_user = sorted(production_rank, reverse = True, key=lambda x: production_rank[x])

        with open("result/users_in_different_ranks_filtered.txt","w") as outfile:
            outfile.write("user name, following rank, follower rank, production rank, consumption rank, activity, popular retweet, mutual connection \n")
            for user in sorted_user:
                if user in common_keys:
                    outfile.write(user)
                    outfile.write(',')
                    outfile.write(str(following_rank[user]))
                    outfile.write(',')
                    outfile.write(str(follower_rank[user]))
                    outfile.write(',')
                    outfile.write(str(production_rank[user]))
                    outfile.write(',')
                    outfile.write(str(consumption_rank[user]))
                    outfile.write(',')
                    outfile.write(str(activity_count[user]))
                    outfile.write(',')
                    outfile.write(str(popular_tweet_count[user]))
                    outfile.write(',')
                    outfile.write(str(mutual_connection_rank[user]))
                    outfile.write('\n')

                    following.append(following_rank[user])
                    follower.append(follower_rank[user])
                    consumption_retweet.append(consumption_rank[user][0])
                    consumption_reply.append(consumption_rank[user][1])
                    consumption_quote.append(consumption_rank[user][2])
                    consumption_reply_quote.append(consumption_rank[user][1]+consumption_rank[user][2])
                    consumption_reply_retweet.append(consumption_rank[user][0]+consumption_rank[user][1])
                    production.append(production_rank[user])
                    activity.append(activity_count[user])
                    popular_tweet.append(popular_tweet_count[user])
                    mutual_connection.append(mutual_connection_rank[user])

        with open("result/AI_cores.txt","w") as outfile:
            for user in core_detect.keys():
                outfile.write(user)
                outfile.write(':')
                outfile.write(core_detect[user])
                outfile.write('\n')


        # plt.figure(0)
        # plt.title('x = following, y = follower')
        # plt.scatter(following,follower)

        # plt.figure(1)
        # plt.title('x = follower, y = production')
        # plt.scatter(follower,production)

        # plt.figure(2)
        # plt.title('x = reply, y = production')
        # plt.scatter(consumption_reply,production)

        # plt.figure(3)
        # plt.title('x = activity, y = reply')
        # plt.scatter(activity,consumption_reply)

        # plt.figure(4)
        # plt.title('x = activity, y = production')
        # plt.scatter(activity,production)

        # plt.figure(5)
        # plt.title('x = activity, y = number of popular retweet bring in')
        # plt.scatter(activity,popular_tweet)

        # plt.figure(6)
        # plt.title('x = reply, y = number of popular retweet bring in')
        # plt.scatter(consumption_reply,popular_tweet)

        # plt.figure(7)
        # plt.title('x = following, y = number of popular retweet bring in')
        # plt.scatter(following,popular_tweet)

        # plt.figure(8)
        # plt.title('x = follower, y = number of popular retweet bring in')
        # plt.scatter(follower,popular_tweet)

        # plt.figure(9)
        # plt.title('x = mutual connection, y = number of popular retweet bring in')
        # plt.scatter(mutual_connection,popular_tweet)

        # plt.show()

    def top_ranked_user_comparison(self):

        TOP = 100

        top_following = set()
        with open('result/AIuser_following_rank.txt','r', encoding = 'utf-8') as infile:
            rank = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if rank <= TOP:
                    top_following.add(eles[0])
                rank = rank + 1

        top_follower = set()
        with open('result/AIuser_follower_rank.txt','r', encoding = 'utf-8') as infile:
            rank = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if rank <= TOP:
                    top_follower.add(eles[0])
                rank = rank + 1

        top_production = set()
        with open('result/AIuser_production(withQuoteAndReply)_rank.txt','r', encoding = 'utf-8') as infile:
            rank = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if rank <= TOP:
                    top_production.add(eles[0])
                rank = rank + 1

        top_consumption = set()
        # with open('result/AIuser_consumption_rank.txt','r', encoding = 'utf-8') as infile:
        with open('result/AIuser_consumption(withReplyAndQuote)_rank.txt','r', encoding = 'utf-8') as infile:
            rank = 0
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                if rank <= TOP:
                    top_consumption.add(eles[0])
                rank = rank + 1

        following_follower_intersect         = set.intersection(top_following,top_follower)
        follower_production_intersect        = set.intersection(top_follower,top_production)
        following_consumption_intersect      = set.intersection(top_following,top_consumption)
        production_consumption_intersect     = set.intersection(top_production,top_consumption)

        print("among the top %i ranked user from each categories" %TOP)
        print("number of intersection between following and follower")
        print(len(following_follower_intersect))

        print("number of intersection between following and production")
        print(len(follower_production_intersect))

        print("number of intersection between follower and consumption")
        print(len(following_consumption_intersect))

        print("number of intersection between production and consumption")
        print(len(production_consumption_intersect))

    def production_with_quote_rank(self):

        Tweets_list = self.collect_production_related_tweets()
        count       = self.production_count(Tweets_list)

        sorted_user = sorted(count, reverse=True, key=lambda x: count[x])

        os.chdir("D:/github/TwitterExperiment/TwitterScript")

        with open('result/AIuser_production(withQuote)_rank.txt','w', encoding = 'utf-8') as outfile:
            for u in sorted_user:
                outfile.write(u)
                outfile.write(',')
                outfile.write(str(count[u]))
                outfile.write('\n')

    def activity_measure(self):

        interested_user = []
        #get list of user with name and id
        with open('result/verified_AIuser.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                interested_user.append(eles[0])

        AIcom_id_list = set()
        AI_user_id_screen_name_map = {}
        #get list of user with name and id
        with open('input/AIuser_screen_name.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                line = line.split(',')
                user_creen_name = line[0]
                user_id         = int(line[1])
                AI_user_id_screen_name_map[user_id] = user_creen_name
                if user_creen_name in interested_user:
                    AIcom_id_list.add(int(user_id))

        print(len(AIcom_id_list))

        os.chdir('tweets/AI_tweets')

        files_arr       = os.listdir()
        activity_list  = {}
        for file in files_arr:
            eles = file.split('_')
            user_id   = int(eles[0])
            if user_id in AIcom_id_list:
                if user_id in AI_user_id_screen_name_map.keys():
                    print("I am here")
                    activity_list[AI_user_id_screen_name_map[user_id]] = 0
                    with open(file,"r") as infile:
                        for line in infile:
                            tweet_obj = self.load_tweet(line)
                            reply_user_id = tweet_obj["in_reply_to_user_id"]
                            if tweet_obj != False:
                                if reply_user_id != None:
                                    # if reply_user_id in AIcom_id_list:
                                    activity_list[AI_user_id_screen_name_map[user_id]] = activity_list[AI_user_id_screen_name_map[user_id]] + 1
                                # else:
                                #     activity_list[AI_user_id_screen_name_map[user_id]] = activity_list[AI_user_id_screen_name_map[user_id]] + 1

        print(len(activity_list))

        os.chdir('D:/github/TwitterExperiment/TwitterScript')
        with open('result/AIuser_activity_measure.txt','w', encoding = 'utf-8') as outfile:
            for user in activity_list.keys():
                outfile.write(str(user))
                outfile.write(',')
                outfile.write(str(activity_list[user]))
                outfile.write('\n')

    def compute_activity_analyze(self):

        acitvity_count = {}
        sum = 0 
        with open('result/AIuser_activity_measure(withoutReply).txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                eles = line.split(',')
                acitvity_count[eles[0]] = int(eles[1])
                sum = sum + int(eles[1])

        Threshold = sum/len(acitvity_count)

        print("average activity among AI research community:")
        print(int(Threshold))

        filtered_users = {}
        for user in acitvity_count.keys():
            if acitvity_count[user] >= Threshold:
                filtered_users[user] = acitvity_count[user]

        os.chdir('D:/github/TwitterExperiment/TwitterScript')
        with open('result/AIuser_activity_filtered(withoutReply).txt','w', encoding = 'utf-8') as outfile:
            for user in filtered_users.keys():
                outfile.write(str(user))
                outfile.write(',')
                outfile.write(str(filtered_users[user]))
                outfile.write('\n')

    def filtered_result(self):

        follower = []
        following = []
        activity = []

        follower_rank = {}
        following_rank = {}

        activity_list = {}

        with open('result/AIuser_activity_filtered(withoutReply).txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                eles = line.split(',')
                user_name = eles[0]
                activity_count = int(eles[1])
                activity_list[user_name] = activity_count

        with open('result/outliner_spot_1.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                eles = line.split(',')
                if eles[0] in activity_list.keys(): 
                    activity.append(activity_list[eles[0]])
                    follower.append(int(eles[2]))
                    following.append(int(eles[1]))

                follower_rank[eles[0]] = int(eles[1])
                following_rank[eles[0]] = int(eles[2])


        plt.figure(0)
        plt.title('x = follower, y = following')
        plt.scatter(follower,following)

        plt.figure(1)
        plt.title('x = follower, y = activity')
        plt.scatter(follower,activity)

        plt.figure(2)
        plt.title('x = following, y = activity')
        plt.scatter(following,activity)


        plt.show()

    #find a list of source for the popular tweet
    def find_popular_tweet(self):

        POPULARITY = 4

        interested_user_name = []
        with open("result/verified_AIuser.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                user_screen_name     = line.split(',')[0]
                interested_user_name.append(user_screen_name)

        Tweets_list = self.collect_production_related_tweets()
        
        os.chdir("D:/github/TwitterExperiment/TwitterScript")

        Tweet_text_list = list([x['full_text'] for x in Tweets_list])

        Tweet_count, average = self.tweet_retweet_count(Tweet_text_list)

        popular_tweet_list = []
        popular_tweet_count = {}
        for tweet in Tweet_count.keys():
            if Tweet_count[tweet] >= POPULARITY:
                popular_tweet_list.append(tweet)
                popular_tweet_count[tweet] = Tweet_count[tweet]

        sorted_tweet = sorted(popular_tweet_count, reverse = True, key=lambda x: popular_tweet_count[x])
        

        with open("result/popular_tweet.txt","w",encoding = "utf-8") as outfile:
            for tweet in sorted_tweet:
                outfile.write(tweet)
                outfile.write(',')
                outfile.write(str(Tweet_count[tweet]))
                outfile.write('\n')

        seen_source = set()
        with open("result/popular_tweet_source.txt","w") as outfile:
            for tweet in popular_tweet_list:
                search  = re.findall(self.RETWEET_USER, tweet)
                if search:
                    source = search[0]
                    if source not in interested_user_name:
                        if source not in seen_source:
                            seen_source.add(source)
                            outfile.write(source)
                            outfile.write(',')
                            outfile.write(str(Tweet_count[tweet]))
                            outfile.write('\n')


    #get the channel how popular tweet flow in the AI community
    def propogate_path(self):

        #read all the user of AI com
        Feifei_file     = "D:/github/TwitterExperiment/GraphScript/input/drfeifei_graph_0_253.txt"
        Andrew_file     = "D:/github/TwitterExperiment/GraphScript/input/andrew_graph_0_423.txt"
        Lecun_file      = "D:/github/TwitterExperiment/GraphScript/input/ylecun_graph_0_225.txt"
        Ian_file        = "D:/github/TwitterExperiment/GraphScript/input/goodfellow_ian_graph_0_1041.txt"
        Jeff_file       = "D:/github/TwitterExperiment/GraphScript/input/JeffDean_graph_0_2049.txt"
        Russ_file       = "D:/github/TwitterExperiment/GraphScript/input/rsalakhu_graph_0_100.txt"
        Hardmaru_file   = "D:/github/TwitterExperiment/GraphScript/input/hardmaru_graph_0_620.txt"
        Mile_File       = "D:/github/TwitterExperiment/GraphScript/input/Miles_Brundage_graph_0_3170.txt"
        Nando_File      = "D:/github/TwitterExperiment/GraphScript/input/NandoDF_graph_0_305.txt"
        Hugo_File       = "D:/github/TwitterExperiment/GraphScript/input/hugo_larochelle_graph_0_490.txt"
        Danilo_File     = "D:/github/TwitterExperiment/GraphScript/input/DeepSpiker_graph_0_849.txt"


        andrew_user_list    = gs.read_user(Andrew_file)
        ian_user_list       = gs.read_user(Ian_file)
        lecun_user_list     = gs.read_user(Lecun_file)
        jeff_user_list      = gs.read_user(Jeff_file)
        russ_user_list      = gs.read_user(Russ_file)
        hardmaru_user_list  = gs.read_user(Hardmaru_file)

        user_set  = set(andrew_user_list+ian_user_list+lecun_user_list+jeff_user_list+russ_user_list+hardmaru_user_list)

        #read the list of interested user
        interested_user = []
        #get list of user with name and id
        with open('result/verified_AIuser.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                interested_user.append(eles[0])

        #get the interested user id and screen name mapping
        interested_user_id_name_map = {}
        interested_user_id = []
        with open("input/AIuser_screen_name.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                eles                 = line.split(',')
                user_screen_name     = eles[0]
                user_id              = int(eles[1])
                if user_screen_name in interested_user:
                    interested_user_id.append(user_id)
                    interested_user_id_name_map[user_screen_name] = user_id

        #get the interested user obj
        interested_user_obj = []
        id_seen = []
        for user in user_set:
            if user.id in interested_user_id and user.id not in id_seen:
                id_seen.append(user.id)
                interested_user_obj.append(user)


        propogation_channel = {}
        with open("result/popular_source_user_id.txt","r") as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                user_id  = int(eles[1])
                propogation_channel[user_id] = set()
                for user in interested_user_obj:
                    if user_id in user.follwowing_list:
                        propogation_channel[user_id].add(user.id)

        with open("result/propogation_channel.txt","w") as outfile:
            for propogation in propogation_channel.keys():
                outfile.write(str(propogation))
                outfile.write(':')
                for channel in propogation_channel[propogation]:
                    outfile.write(str(channel))
                    outfile.write(',')
                outfile.write("\n")

    def count_propogation(self):

         #read the list of interested user
        interested_user = []
        #get list of user with name and id
        with open('result/verified_AIuser.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                interested_user.append(eles[0])

        #get the interested user id and screen name mapping
        interested_user_id_name_map = {}
        interested_user_id = []
        with open("input/AIuser_screen_name.txt","r") as infile:
            for line in infile:
                line                 = line.strip()
                eles                 = line.split(',')
                user_screen_name     = eles[0]
                user_id              = int(eles[1])
                if user_screen_name in interested_user:
                    interested_user_id.append(user_id)
                    interested_user_id_name_map[user_id] = user_screen_name

        propogation_count = {}

        with open("result/propogation_channel.txt","r") as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(':')
                propogator_list = eles[1].split(',')
                propogator_list.pop(-1)
                propogator = propogator_list
                if len(propogator) >= 1:
                    for people in propogator:
                        if people in propogation_count.keys():
                            propogation_count[people] = propogation_count[people] + 1
                        else:
                            propogation_count[people] = 1

        sorted_count = sorted(propogation_count, reverse = True, key=lambda x: propogation_count[x])
        
        with open("result/propogation_count.txt","w") as outfile:
            for u in sorted_count:
                outfile.write(str(interested_user_id_name_map[int(u)]))
                outfile.write(',')
                outfile.write(str(propogation_count[u]))
                outfile.write('\n')

    def popular_tweet_percentage(self):

        #get a list of count that user are responsible for
        count_value = {}
        with open("result/propogation_count.txt","r") as infile:
            for line in infile:
                line = line.strip()
                eles  = line.split(',')
                count_value[eles[0]] = int(eles[1])

        #production utility
        production_utility = {}
        prudction_rank     = []
        with open('result/AIuser_production.txt','r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                eles = line.split(',')
                prudction_rank.append(eles[0])
                production_utility[eles[0]] = int(eles[1])

        TOP = 50
        Top_sum = 0
        Total   = 0

        x = []
        y = []
        index = 1
        for user in prudction_rank:
            if user in count_value.keys():
                x.append(production_utility[user])
                y.append(count_value[user])
                if index <= TOP:
                    Top_sum = Top_sum + count_value[user]
                    Total   = Total + count_value[user]
                else:
                    Total   = Total + count_value[user]
                index = index + 1

        print(Top_sum/Total)

        plt.figure(0)
        plt.title('x = production , y = number of popular tweet responsible')
        plt.scatter(x,y)

        plt.show()


if __name__ == '__main__':

    TA = TweetAnalyzer()
    TA.metric_comparison_activity_filtered()
    # TA.metric_comparison_activity_filtered()
