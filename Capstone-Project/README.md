# Capstone project

## Project scope
This project combines data from [Twitter](https://www.twitter.com), [AWS Comprehend](https://aws.amazon.com/comprehend) 
and static data sources, namely the [world happiness report](https://www.kaggle.com/unsdsn/world-happines) and 
[earth surface temperature data](https://www.kaggle.com/berkeleyearth/climate-change-earth-surface-temperature-data).
The idea is to work with batch- and/or streaming data from Twitter, e.g. tweets related to a  topic of interest 
such as [#PrayForAmazonas](https://twitter.com/hashtag/PrayforAmazonas), related to the enormous fires raging in the
tropical rain forest of Brazil, or [#FridaysForFuture](https://twitter.com/hashtag/FridaysForFuture), related to the 
protests of pupils and students against the way their governments are handling climate change, determine their 
sentiment, that is whether the text of a tweet has positive, neutral or negative tone, and combine that information with 
data related to the happiness score of a country and data related to climate (temperature) changes over several decades. 
Doing so allows analysts to answer interesting questions, e.g. are positive or negative tweets about the #FridaysForFuture 
movement correlated with the happiness of the country a user is residing in, or, is there a relationship between the 
sentiment of a tweet and the temperature change in a country a user is living in?

### Implementation details
In order to gather data from Twitter, we need to access its [API](https://developer.twitter.com/en/docs), which can be 
accomplished conveniently via [tweepy](http://www.tweepy.org/). For this project I decided to work with historical 
tweets (c.f. `search_tweets.py`), since streaming a sufficient amount of tweets (e.g. 1,000,000) 
would have taken a long time - nevertheless, the streaming code in `stream_tweets.py` is fully functional. In order to 
determine the sentiment of a tweet, its text attribute is sent to AWS Comprehend (c.f. `detect_sentiment()` method 
in `search_tweets.py`). While we can run both scripts from local machines, it may be more convenient to deploy them to a 
dedicated server/container in the cloud (c.f. AWS [EC2](https://aws.amazon.com/ec2) or 
[ECS](https://aws.amazon.com/ecs)). Since we need to store tweets for further processing and as 
they usually come in large quantities at fast speeds, we use AWS [Kinesis](https://aws.amazon.com/kinesis/data-firehose) 
to ingest tweet data into [S3](https://aws.amazon.com/s3) before we finally stage it into 
[Redshift](https://aws.amazon.com/redshift). Note that static datasets mentioned above are also transferred to S3 before 
they are loaded into Redshift. Using the aforementioned AWS toolstack to process data is convenient in 
our case, since it can scale to large amounts of data/users easily and is fully managed. Since we do not want to run 
individual scripts to manually populate our data source, we use [Airflow](https://airflow.apache.org/) to create tables
in Redshift, stage data and derive fact and dimension tables (c.f. `airflow/capstone_dag.py`).

Once this has been done we have access to the following star-schema based data model: 
 
| Table | Description |
--- | ---
| staging_tweets      | Staging table for tweets
| staging_happiness   | Staging table for world happiness data
| staging_temperature | Staging table for temperature data by country
| users               | Dimension table containing user related information derived from staging_tweets
| sources             | Dimension table containing sources (e.g. Twitter for Android/iPhone) derived from tweets
| happiness           | Dimension table containing happiness related data (e.g. country, rank, score, etc.) derived from staging_happiness
| temperature         | Dimension table containing temperature related data (e.g. country, average temperature over last 20/50/100 years) derived from staging_temperature
| tweets              | Fact table containing tweet related information, happiness score/rank and temperature derived from all staging tables

Note: The data dictionary (c.f. `DATADICT.md`) contains a description of every attribute for all tables listed above.

Using the data model above we can finally answer questions regarding relationships between tweets, their sentiment, 
users, their location, happiness scores by country and variations in temperature by country.

### A word on data quality
Before developing the data pipeline described above, I did a quick data quality assessment of the static datasets and a 
sample (roughly 1.200) of tweets (c.f. `notebooks/exploration.ipynb`). In short, while happiness data is fine (no duplicates or missing values), temperature data contains roughly 4% percent missing values for average temperature. Since this is negligible for our use case, missing values where dropped before uploading the temperature dataset to S3. Tweet data is fine too,the only issue here is the missing standardization of user locations (c.f. Limitation section), which may make it hard to join it with happiness and/or temperature data.

### Handling alternative scenarios
This section discusses strategies to deal with the following scenarios:
1. Data is increased 100x  
2. Data pipeline is run on daily basis by 7 am every day
3. Database needs to be accessed by 100+ users simultaneously

#### Data is increased 100x
Since we decided to use scalable, fully managed cloud services to store and process our data, we might only need to  increase the available resources (e.g. number/CPU/RAM of Redshift nodes) to handle an increase in data volume. While an increase in Redshift nodes would allow us to load larger static datasets faster, it would not help with an increase in tweets, since those need to pass through Kinesis before being saved to S3 and loaded into Redshift. In order to handle an increase in tweets we could switch from processing them individually to processing in batches (logic already implemented). Additionally we could deliver tweets to different Kinesis streams (each capable of processing 5,000 records/second) and/or increase the processing limit up to 10,000 records/second (c.f.[Kinesis limits](https://docs.aws.amazon.com/firehose/latest/dev/limits.html))

#### Data pipleline is run on a daily basis by 7 am every day
As the static datasets do not change on a daily basis, the major challenge here, is to process the amount of newly 
captured tweets in an acceptable time. Fortunately, Kinesis partitions the data into yearly/monthly/daily/hourly blocks, 
i.e. a collection of tweets may be stored in `2019/09/10/17/<some-random-id>.json`. This makes it easy for us to schedule 
data loads, for example via another dedicated Airflow dag. Given an appropriate increase in Redshift resources, this 
should be sufficient to process tweet data in time.

#### Database needs to be accessed by 100+ users simultaneously
Besides increasing Redshift resources as mentioned above, we could deal with an increase in users by precomputing the 
most complicated (in terms of required processing power) and/or most desired queries and store them in an additional 
table.

## Prerequisites
* Twitter developer account including registered app with consumer key/secret and access token/secret
* Kaggle account in order to access static datasets
* AWS account with dedicated user including access key ID and secret access key
* Access to AWS Kinesis Firehose including existing delivery stream
* Access to AWS Comprehend
* Access to a (running) AWS Redshift cluster, where access means:
    - Having created an attached a security group allowing access on port 5439
    - Having created an attached a role allowing Redshift to access buckets on AWS S3
    - Create/drop/insert/update rights for the Redshift instance
* Working installation of Airflow, where working means:
    - Airflow web server and scheduler are running
    - Connection to AWS is set up using `aws_default` ID
    - Connection to Redshift is set up using `redshift_default` ID
    - AWS IAM role is set up as Airflow variable using `aws_iam_role` as key
* Unix-like environment (Linux, macOS, WSL on Windows)
* Python 3.7+
* Python packages tweepy, boto3, airflow, etc. (c.f. `capstone_env.yml` and `requirements.txt`)

## Usage
1. Double check that you meet all prerequisites specified above
2. Create a dedicated Python environment using conda via `conda env create -f capstone_env.yml` 
and activate it via `conda actiate udacity-dend`
3. Edit `app.cfg` and enter your information in the corresponding sections (aws, twitter, etc.)  
4. Get the [world happiness](https://www.kaggle.com/unsdsn/world-happiness#2017.csv) and 
[earth temperature](https://www.kaggle.com/berkeleyearth climate-change-earth-surface-temperature-data#GlobalLandTemperaturesByCountry.csv) datasets from Kaggle and save them to the data directory in this repository
5. Search or stream some tweets by running either `python search_tweets.py` or `python stream_tweets.py`
6. Verify that the capstone_dag has been correctly parsed by Airflow via `airflow list_tasks capstone_dag --tree`
7. Trigger a DAG run via `airflow trigger_dag capstone_dag`. If just want to run a specific task do so via
`airflow run -i capstone_dag<task_id>`
8. Have fun analyzing the data

## Limitations
* Location of Twitter users are not standardized, may be NULL and may contain data which is not a location at all.  Further pre-processing, i.e. via [geopy](https://github.com/geopy/geopy) and its [Nomiatim geocoder](https://geopy.readthedocs.io/en/1.10.0/#geopy.geocoders.Nominatim), may be required to derive actual countries from users locations. 
* Error and exception handling in `search_tweets.py` and `stream_tweets.py` is very basic and does not guarantee data 
delivery to Kinesis.
* The setup process for all AWS tools is manual and not yet automated via [Ansible](https://docs.ansible.com/ansible/latest/index.html)

## Resources
* [Twitter API documentation](https://developer.twitter.com/en/docs)
* [Twitter search API documentation](https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html)
* [Twitter tweet data dictionary](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object)
* [Twitter basic stream API parameters documentation](https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters)
* [Tweepy documentation](https://tweepy.readthedocs.io/en/latest/index.html)
* [Tutorial on using tweepy to process Twitter streams with Python](https://www.dataquest.io/blog/streaming-data-python/)
* [Blog post on using Kinesis and Redshift to stream Twitter data](https://medium.com/@siprem/streaming-twitter-feed-using-kinesis-data-firehose-and-redshift-745c96d04f58)
* [Blog post on using Kinesis to batch insert streaming data](https://medium.com/retailmenot-engineering/building-a-high-throughput-data-pipeline-with-kinesis-lambda-and-dynamodb-7d78e992a02d)
* [AWS Boto 3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
* [AWS Kinesis documentation for PutRecords](https://docs.aws.amazon.com/kinesis/latest/APIReference/API_PutRecords.html)
* [AWS Comprehend documentation for DetectSentiment](https://docs.aws.amazon.com/comprehend/latest/dg/API_DetectSentiment.html)