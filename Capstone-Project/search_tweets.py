import logging
import time
import json
import boto3
import tweepy
from configparser import ConfigParser
from botocore.exceptions import ClientError


class TweetHandler:
    """
    Process and filter individual or batches of tweets and push them to AWS Kinesis.
    """

    def __init__(self, config):
        self.config = config
        self.aws_access_key_id = self.config.get("aws", "access_key_id")
        self.aws_secret_access_key = self.config.get("aws", "secret_access_key")
        self.delivery_stream = self.config.get("kinesis", "delivery_stream")
        self.limit = self.config.getint("tweepy", "limit")
        self.logging_interval = self.config.getint("logging", "interval")
        self.counter = 0
        self._batch = []
        self.batch_size = self.config.getint("kinesis", "batch_size")
        self.comprehend_client = boto3.client("comprehend",
                                              aws_access_key_id=self.aws_access_key_id,
                                              aws_secret_access_key=self.aws_secret_access_key)
        self.firehose_client = boto3.client("firehose",
                                            aws_access_key_id=self.aws_access_key_id,
                                            aws_secret_access_key=self.aws_secret_access_key)

    def filter(self, tweet: dict) -> dict:
        """
        Select a subset of all tweet data and return it as dict
        :param tweet: Tweet data as dict
        :return: Filtered tweet data
        """
        filtered_tweet = {"user_id": tweet.user.id_str,
                          "name": tweet.user.name,
                          "nickname": tweet.user.screen_name,
                          "description": tweet.user.description,
                          "user_location": tweet.user.location,
                          "followers_count": tweet.user.followers_count,
                          "tweets_count": tweet.user.statuses_count,
                          "user_date": tweet.user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                          "verified": tweet.user.verified,
                          "tweet_id": tweet.id_str,
                          "text": tweet.full_text,
                          "favs": tweet.favorite_count,
                          "retweets": tweet.retweet_count,
                          "tweet_date": tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                          "tweet_location": tweet.place.full_name if tweet.place else None,
                          "source": tweet.source,
                          "sentiment": self.detect_sentiment(tweet.full_text, tweet.lang)}

        return filtered_tweet

    def detect_sentiment(self, text: str, lang: str, full_result: bool = False):
        """
        Detect the sentiment of a Tweet's text using AWS' Comprehend API.
        :param text: Text of Tweet
        :param lang: Language of string, i.e. en
        :param full_result: Bool indicating whether to return all data provided by AWS Comprehend or just the sentiment
        :return: Sentiment as str or dict (determined by full_result flag)
        """
        sentiment = self.comprehend_client.detect_sentiment(Text=text, LanguageCode=lang)

        if full_result:
            return sentiment
        else:
            return sentiment["Sentiment"]

    @staticmethod
    def handle_rate_limit(cursor: tweepy.Cursor):
        """
        If tweepy hits Twitter' API limit (180 calls in 15 minutes), wait for 15 minutes before continuing search.
        http://docs.tweepy.org/en/latest/code_snippet.html#handling-the-rate-limit-using-cursors
        :param cursor: Tweepy cursor iterator
        :return: Next iteration of cursor
        """
        while True:
            try:
                yield cursor.next()
            except tweepy.RateLimitError:
                # sleep for 15 minutes
                logging.warning("Hit Twitter APIs rate limit, sleeping for 15 minutes")
                time.sleep(15 * 60)

    def process(self, cursor: tweepy.Cursor):
        """
        Process single tweet and push it to Kinesis stream.
        :param cursor: Tweepy Cursor
        """
        logging.info("Processing tweets")

        for tweet in self.handle_rate_limit(cursor.items(self.limit)):
            filtered_tweet = self.filter(tweet)

            try:
                logging.debug("Pushing tweet data to Kinesis")
                response = self.firehose_client.put_record(DeliveryStreamName=self.delivery_stream,
                                                           Record={
                                                               # kinesis only accepts byte-like data
                                                               "Data": json.dumps(filtered_tweet)
                                                           })
                logging.debug(response)

            except ClientError as ex:
                logging.exception(f"Could not push tweet data to Kinesis: {ex}")

            finally:
                self.counter += 1
                if self.counter % self.logging_interval == 0:
                    logging.info(f"Processed {self.counter} tweets")

    def process_batch(self, cursor: tweepy.Cursor):
        """
        Process batch of tweets and push it to Kinesis stream.
        :param cursor: Tweepy Cursor iterator
        """
        logging.info("Processing tweets")

        for tweet in self.handle_rate_limit(cursor.items(self.limit)):
            if len(self._batch) < self.batch_size:
                self._batch.append(self.filter(tweet))
            else:
                self.submit_batch(self._batch)

        # make sure remaining tweets are submitted
        if self._batch:
            self.submit_batch(self._batch)

    def submit_batch(self, batch: list):
        """
        Push a batch of tweets to Kinesis.
        :param batch: List of tweets
        """
        try:
            logging.info(f"Pushing tweet data of size {len(batch)} to Kinesis")
            response = self.firehose_client.put_record_batch(DeliveryStreamName=self.delivery_stream,
                                                             Records=[{
                                                                 "Data": json.dumps(batch)
                                                             }])
            logging.debug(response)

        except ClientError as ex:
            logging.exception(f"Could not push tweet batch to Kinesis: {ex}")

        finally:
            self.counter += len(batch)
            self._batch = []


if __name__ == "__main__":
    # load config
    config = ConfigParser()
    config.read("app.cfg")

    # start logging
    logging.basicConfig(level=config.get("logging", "level"), format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Started")

    # start timer
    start_time = time.perf_counter()

    # authenticate to twitter API
    logging.info("Authenticating to Twitter")
    auth = tweepy.OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
    auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))
    api = tweepy.API(auth)

    # search and process tweets
    logging.info(f"Searching Twitter for: {config.get('tweepy', 'query')}")
    tweet_handler = TweetHandler(config)
    tweet_handler.process_batch(tweepy.Cursor(api.search,
                                              q=config.get("tweepy", "query"),
                                              lang=config.get("tweepy", "lang"),
                                              result_type=config.get("tweepy", "result_type"),
                                              tweet_mode=config.get("tweepy", "tweet_mode"),
                                              count=config.getint("tweepy", "count"),
                                              until=config.get("tweepy", "cutoff_date")))
    # stop timer
    stop_time = time.perf_counter()
    logging.info(f"Processed {tweet_handler.counter} tweets in {(stop_time - start_time):.2f} seconds")
    logging.info("Finished")
