import json

import boto3
import tweepy

consumer_key = ""
consumer_secret = ""
bearer_token = "%"

auth = tweepy.OAuth2AppHandler(consumer_key, consumer_secret)
api = tweepy.API(auth)
client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret, return_type=dict)

bucket__name = "collected-tweets"
s3 = boto3.resource('s3')
sqs_queue = "https://sqs.sa-east-1.amazonaws.com/689566614228/defend-queue"
sqs = boto3.client('sqs')

def get_tweet_data(tweet_id):
    tweet = api.get_status(id=tweet_id, tweet_mode='extended')._json
    return tweet

def get_retweets_data(tweet_id):
    retweets = api.get_retweets(id=tweet_id, count=10000, tweet_mode='extended')
    retweetsJson = {"retweets": [retweet._json for retweet in retweets]}
    return retweetsJson

def get_same_text_tweets_data(query, tweet_id):
    try:
        tweets = api.search_tweets(query, tweet_mode='extended')
        tweets = [tweet._json for tweet in tweets]
        sameTextTweets = list(filter(lambda tweet: query == tweet['full_text'] and tweet['id'] != tweet_id, tweets))
    except:
        sameTextTweets = []
    return {"same_text_tweets": sameTextTweets}

def write_to_s3(data, s3_path, file_name):
    s3_object = s3.Object(bucket__name, s3_path + file_name + '.json')
    s3_object.put(Body=bytes(json.dumps(data).encode('UTF-8')), ContentType='application/json')
    print("Wrote {}.json to {}".format(file_name, bucket__name))

def get_quote_tweets(tweet_id):
    tweets = client.get_quote_tweets(tweet_id, max_results=100)
    return {"quote_tweets": tweets['data']}

def get_replies(tweet_id, screen_name):
    replies=[]
    for tweet in tweepy.Cursor(api.search_tweets,q='to:'+screen_name, result_type='recent', tweet_mode='extended').items(1000):
        if hasattr(tweet, 'in_reply_to_status_id'):
            if (tweet.in_reply_to_status_id==tweet_id):
                replies.append(tweet)
    reply_json_list = [reply._json for reply in replies]
    return {"replies": reply_json_list}


def send_to_sqs_queue(message):
    response = sqs.send_message(
        QueueUrl=sqs_queue,
        DelaySeconds=10,
        MessageBody=message
    )

    print(response['MessageId'])
    print(message)
    print("------------------------------------")

def lambda_handler(event, context):
    tweet_info = json.loads(event['Records'][0]['body'])

    tweet_id = tweet_info['conversation_id']
    tag_id = tweet_info['tag_id']

    tweet_data = get_tweet_data(tweet_id)
    retweets_data = get_retweets_data(tweet_id)
    same_text_tweets_data = get_same_text_tweets_data(tweet_data['full_text'], tweet_data['id'])
    quote_tweets_data = get_quote_tweets(tweet_id)
    replies_data = get_replies(tweet_id, tweet_data['user']['screen_name'])

    s3_path = "{}/{}/".format(tweet_id, tag_id)
    write_to_s3(tweet_info, s3_path, 'collection_log')
    write_to_s3(tweet_data, s3_path, str(tweet_id))
    write_to_s3(retweets_data, s3_path, 'retweets')
    write_to_s3(same_text_tweets_data, s3_path, 'same_text_tweets')
    write_to_s3(quote_tweets_data, s3_path, 'quote_tweets')
    write_to_s3(replies_data, s3_path, 'replies')

    send_to_sqs_queue(json.dumps(tweet_info))

if __name__ == "__main__":
    tweet_data = get_tweet_data(1597022459957739520)
    json.dump(tweet_data, open("tweet.json", "w"))

    retweets_data = get_retweets_data(1597022459957739520)
    json.dump(retweets_data, open("retweets.json", "w"))

    same_text_tweets_data = get_same_text_tweets_data(tweet_data['full_text'], tweet_data['id'])
    json.dump(same_text_tweets_data, open("same_text_tweets.json", "w"))

    quote_tweets_data = get_quote_tweets(1597022459957739520)
    json.dump(quote_tweets_data, open("quote_tweets.json", "w"))

    replies_data = get_replies(1597022459957739520, tweet_data['user']['screen_name'])
    json.dump(replies_data, open("replies.json", "w"))
