"""Get tweet in real time."""
from slistener import SListener
from tweepy import OAuthHandler
import tweepy


# Twitter dev information
access_token = "3170234799-qOw35tM50S5W0MHG9O8VRlZh5j6f7m8GzEuEcQQ"
access_token_secret = "5FBYdB7jwR447aE2XMXeM6yJiSGh0fJMYb9WujBJT5Swm"
consumer_key = "IlPMH3fWCDvzLCn2OS3Qk1D1R"
consumer_secret = "DQKeuoyrl77HBXKkBrNlhJjqyMz3UICBbaoeMTy6QllxjoZi9k"

# Connection to the Twitter API
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def main():
    """Method to get Twitter status in real time."""
    track = ['@realDonaldTrump', '#Trump2016', '#TeamTrump', '#Trump',
             '@HillaryClinton', '#Hillary2016', '#Hillary', '#HillaryClinton',
             '#USAElection', '#usaelections', '#MakeAmericaGreatAgain']

    listen = SListener(api, 'myprefix')
    stream = tweepy.Stream(auth, listen)

    print "Streaming started..."
    while True:
        try:
            stream.filter(track=track)
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)
            print "error!"
            continue

if __name__ == '__main__':
    main()
