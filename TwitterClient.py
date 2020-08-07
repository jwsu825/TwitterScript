from tweepy import API 
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
 
import numpy as np
import pandas as pd

import TwitterCredential
import re
import tweepy
import time
import json
import TweetProcess as TP


# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_screen_name(self, user_id):
        try:
            user = self.twitter_client.get_user(user_id)
            return user.screen_name
        except tweepy.RateLimitError:
                print("sleeping for rate limit")
                time.sleep(15*60)
        except tweepy.TweepError:
                print("error")
                return None
                self.auth = TwitterAuthenticator().authenticate_twitter_app()

    def get_user_id(self, user_screen_name):
        try:
            user = self.twitter_client.get_user(user_screen_name)
            return user.id
        except tweepy.RateLimitError:
                print("sleeping for rate limit")
                time.sleep(15*60)
        except tweepy.TweepError:
                print(user_screen_name)
                return None
                self.auth = TwitterAuthenticator().authenticate_twitter_app()



    def get_friend_list_id(self, screen_name):
        friend_list = []
        try:
            for friend in Cursor(self.twitter_client.friends_ids, id=screen_name).items():
                friend_list.append(friend)
        except tweepy.RateLimitError:
                print("sleeping for rate limit")
                time.sleep(15*60)
        except tweepy.TweepError:
                print("skipping this user")
                return [-1]
        return friend_list


    def get_friend_list_and_write(self, screen_name):
        friend_list = self.get_friend_list_id(screen_name)
        file_name = 'output/'+ screen_name + '.txt'
        node_index = 0
        with open(file_name, 'w') as file:
            for friend in friend_list:
                file.write("%i," % node_index)
                file.write("%s\n" % friend)
                node_index = node_index + 1

    def get_neighbor_friend_list_and_write(self, friend_list_id):
        node_index = 0
        file_name = 'output/andrew_graph.txt'
        with open(file_name, 'w') as file:
            for neighbor in friend_list_id:
                neighbor_friend_list = self.get_friend_list_id(neighbor)
                file.write("%i," % node_index)
                file.write("%s," % neighbor)
                print 
                for neighbor_id in neighbor_friend_list:
                    file.write("%i " % neighbor_id)
                file.write("\n")
                node_index = node_index + 1

    def get_neighbor_friend_list_and_write_from_file(self, screen_name):
        node_index = 0
        in_file_name = 'output/'+screen_name+'.txt'
        out_file_name = 'output/'+screen_name+'_graph.txt'
        with open(in_file_name) as infile:
            with open(out_file_name, 'w') as outfile:
                for line in infile:
                    line = line.strip()
                    elements = line.split(",")
                    user_index = int(elements[0])
                    user_id    = int(elements[1])  
                    if user_index >= 0:
                        neighbor_friend_list = self.get_friend_list_id(user_id)
                        outfile.write("%i," % user_index)
                        outfile.write("%s," % user_id)
                        print("I am at index"+str(node_index)+"\n")
                        for neighbor_id in neighbor_friend_list:
                            outfile.write("%i " % neighbor_id)
                        outfile.write("\n")
                    node_index = node_index + 1
        return

    def get_tweets(self,user_id, year, month, month_period):
        TA    = TP.TweetAnalyzer()
        out_file_name = 'tweets/AIcom(handpick)Tweets/'+str(user_id)+'_tweets.txt'
        with open(out_file_name,'w') as outfile:
            try:
                for tweet in tweepy.Cursor(self.twitter_client.user_timeline, user_id = int(user_id), tweet_mode = "extended").items():             
                    #test if the tweet is within time period
                    if TA.is_within_time(tweet.created_at,year,month,month_period):
                        tweet_json = tweet._json
                        json_str = json.dumps(tweet_json)
                        outfile.write(json_str)
                        outfile.write('\n')
                    else:
                        break
            except tweepy.RateLimitError:
                print("sleeping for rate limit")
                time.sleep(15*60)
            except tweepy.TweepError as e:
                print("sleeping for rate limit and authen again")
                time.sleep(15*60)
                self.auth = TwitterAuthenticator().authenticate_twitter_app()

    def get_tweets_screen_name(self,name, year, month, month_period):
        TA    = TP.TweetAnalyzer()
        out_file_name = 'tweets/AIcom(handpick)Tweets/'+name+'_tweets.txt'
        with open(out_file_name,'w') as outfile:
            try:
                for tweet in tweepy.Cursor(self.twitter_client.user_timeline, screen_name = name, tweet_mode = "extended").items():             
                    #test if the tweet is within time period
                    if TA.is_within_time(tweet.created_at,year,month,month_period):
                        tweet_json = tweet._json
                        json_str = json.dumps(tweet_json)
                        outfile.write(json_str)
                        outfile.write('\n')
                    else:
                        break
            except tweepy.RateLimitError:
                print("sleeping for rate limit")
                time.sleep(15*60)
            except tweepy.TweepError as e:
                print("sleeping for rate limit and authen again")
                time.sleep(15*60)
                self.auth = TwitterAuthenticator().authenticate_twitter_app()
    
    def get_tweet_from_neighbor(self):

        with open("neighbor/JeffDean.txt","r") as infile:
            for line in infile:
                line            = line.strip()
                elements        = line.split(",")
                user_id         = elements[1]
                print("I am at %s",user_id)
                self.get_tweets(user_id=user_id, year=2019, month=5, month_period=3)

    def get_screen_name(self):

        AIuser_screen_name = {}

        number = 0
        with open("input/AIuser_screen_name.txt","w") as outfile:
            with open("input/AIcom_stat.txt","r") as infile:
                line        = infile.readline()
                line        = line.strip()
                line        = line.split(',')
                entry_line  = line[1]
                entries     = entry_line.split(' ')
                for entry in entries:
                    if number >= 0:
                        ele     = entry.split(':')
                        user_id = ele[0]
                        print("I am at %s",user_id)
                        screen_name = twitter_client.get_user_screen_name(user_id=user_id)
                        if screen_name:
                            outfile.write(screen_name)
                            outfile.write(",")
                            outfile.write(str(user_id))
                            outfile.write("\n")
                    number = number + 1

    def get_tweet_from_file(self):

        with open("input/AIcom(handpicked).txt","r") as infile:
            for line in infile:
                line            = line.strip()
                user_screen_name     = line
                print("I am at "+user_screen_name)
                self.get_tweets_screen_name(name=user_screen_name, year=2019, month=5, month_period=6)

    def get_popular_source_id(self):
        with open("result/popular_source_user_id.txt","w") as outfile:
            with open("result/popular_tweet_source.txt","r") as infile:
                for line in infile:
                    line            = line.strip()
                    user_screen_name     = line.split(',')[0]
                    id = twitter_client.get_user_id(user_screen_name)
                    outfile.write(user_screen_name)
                    outfile.write(",")
                    outfile.write(str(id))
                    outfile.write("\n")



# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(TwitterCredential.CONSUMER_KEY, TwitterCredential.CONSUMER_SECRET)
        auth.set_access_token(TwitterCredential.ACCESS_TOKEN, TwitterCredential.ACCESS_TOKEN_SECRET)
        return auth


 
if __name__ == '__main__':

    twitter_client = TwitterClient()

    with open("result/TechnologyComFollowing.txt","w") as outfile:
        with open("result/TechnologyCom.txt","r") as infile:
            for line in infile:
                user_screen_name = line.strip()
                user_id = twitter_client.get_user_id(user_screen_name)
                following_list_id = twitter_client.get_friend_list_id(user_screen_name)
                outfile.write(str(user_id))
                for u_id in following_list_id:
                    outfile.write(',')
                    outfile.write(str(u_id))
                outfile.write('\n')









