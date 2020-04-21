import logging
import boto3
from configparser import ConfigParser
from botocore.exceptions import ClientError
from tweepy import StreamListener, Stream, OAuthHandler



class TweetListener(StreamListener):

    def __init__(self, config):
        super(StreamListener, self).__init__()
        self.config = config
        self.aws_access_key_id = self.config.get("aws", "access_key_id")
        self.aws_secret_access_key = self.config.get("aws", "secret_access_key")
        self.delivery_stream = self.config.get("kinesis", "delivery_stream")
        self.firehose_client = boto3.client("firehose",
                                            aws_access_key_id=self.aws_access_key_id,
                                            aws_secret_access_key=self.aws_secret_access_key)

    def on_data(self, tweet):
        """
        Push matching tweets to Kinesis.
        :param tweet: Tweet data as dict
        :return:
        """

        try:
            logging.info("Pushing tweet data to Kinesis")
            response = self.firehose_client.put_record(DeliveryStreamName=self.delivery_stream,
                                                       Record={
                                                           "Data": tweet
                                                       })
            logging.debug(response)
            return True

        except ClientError as ex:
            logging.exception(f"Could not push tweet data to Kinesis: {ex}")

    def on_error(self, status_code):
        """
        Handle errors.
        :param status_code: HTTP status code
        :return:
        """
        logging.error(status_code)
        # https://tweepy.readthedocs.io/en/latest/streaming_how_to.html#handling-errors
        if status_code == 420:
            return False


if __name__ == "__main__":
    # load config
    config = ConfigParser(converters={"list": lambda x: [e.strip() for e in x.split(",")]})
    config.read("app.cfg")

    # start logging
    logging.basicConfig(level=config.get("logging", "level"), format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Started")

    # authenticate to twitter API
    logging.info("Authenticating to Twitter")
    auth = OAuthHandler(config.get("twitter", "consumer_key"), config.get("twitter", "consumer_secret"))
    auth.set_access_token(config.get("twitter", "access_token"), config.get("twitter", "access_token_secret"))

    # start streaming
    logging.info(f"Start streaming tweets matching: {config.getlist('tweepy', 'track_topics')}")
    twitter_stream = Stream(auth, TweetListener(config))
    twitter_stream.filter(track=config.getlist("tweepy", "track_topics"),
                          languages=config.getlist("tweepy", "track_langs"))
