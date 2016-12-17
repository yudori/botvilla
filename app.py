import os
import re
import random
import requests
import shutil
from collections import Counter

import tweepy


consumer_key = os.environ['CONSUMER_KEY']
consumer_secret = os.environ['CONSUMER_SECRET']
access_token = os.environ['ACCESS_TOKEN']
access_token_secret = os.environ['ACCESS_TOKEN_SECRET']

gifs = [
    {
        'caption': "You lit up my year",
        'url': "http://i.giphy.com/QMkPpxPDYY0fu.gif"
    },
    {
        'caption': "You were the sauce to my age #2016",
        'url':"http://i.giphy.com/brJ48z2MI16tG.gif" 
    },
    {
        'caption': "Ma gees fo life!",
        'url': "http://i.giphy.com/l0ErD3jZchiD7yMQE.gif"
    },
    {
        'caption': "I ain't Lion 'bout what you mean to me",
        'url': "http://i.giphy.com/Dc9AyUMrBKvkI.gif"
    },
    {
        'caption': "You've been absolutely SOUPer!",
        'url': "http://i.giphy.com/d6mz7A2HJI69G.gif"
    },
    {
        'caption': "You're the Shit!",
        'url': "http://i.giphy.com/awKjbkkb4PWs8.gif"
    },
    {
        'caption': "MOO-cho Gracias! #2016",
        'url': "http://i.giphy.com/ZITn05KW13znG.gif"
    },
]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def get_best_friends(user_id, count=1):
    all_tweets = []
    try:
        tweets = api.user_timeline(user_id, count=200)
    except tweepy.error.TweepError:
        return []
    all_tweets.extend(tweets)
    last = all_tweets[-1].id - 1
    page_counter = 1

    while page_counter < 5 and len(tweets) > 0:
        tweets = api.user_timeline(user_id, count=200, max_id=last)
        all_tweets.extend(tweets)
        last = all_tweets[-1].id - 1
        page_counter += 1

    tweets_str = str([tweet.text for tweet in all_tweets])
    mentions = re.findall(r"\B@[a-zA-Z0-9_-]+", tweets_str)
    return Counter(mentions).most_common()[:count]


class MyStreamListener(tweepy.StreamListener):    
    def on_status(self, status): 
        tweet = status.text
        if status.retweeted == False and tweet[:2] != 'RT':    
            sender = '@'+status.user.screen_name
            top_friends = set([val[0] for val in get_best_friends(sender, 6)])
            try:
                friends = " ".join(random.sample(top_friends, 3))
            except ValueError:
                friends = " ".join(top_friends)
            gif = random.choice(gifs)
            reply = "{} {} [from {}]".format(friends, gif['caption'], sender)
            response = requests.get(gif['url'], stream=True)
            with open('tmp.gif', 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
                api.update_with_media("tmp.gif", status=reply, in_reply_to_status_id=status.id)
            del response
    def on_error(self, status_code):
            print("Error {}!".format(str(status_code)))
            return False

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=['@ekelebot #DoYourDance'], async=True)
