# Data dictionary

## About
This file contains an overview of the attributes (columns), types and descriptions for all tables used in the project.

### Tables

#### Staging Tweets

| Column         | Type      | Description |
| -------------- | --------- | ----------------------------------------------------
| user_id        | varchar   | ID of Twitter user
| name           | varchar   | "Real" name of Twitter user, e.g. Stefan Langenbach
| nickname       | varchar   | Screename of Twitter user, e.g. @stefan
| description    | varchar   | Bio of Twitter user
| user_location  | varchar   | Location of Twitter user, e.g. Milan, Italy
| followers_count| int       | Number of followers of Twitter user
| tweets_count   | int       | Number of tweets of Twitter user
| user_date      | timestamp | Date Twitter user was created
| verified       | bool      | Whether the user is verified (small blue check sign)
| tweet_id       | varchar   | ID of tweet
| text           | varchar   | Text of tweet
| favs           | int       | Number of times tweet is marked as favourite by other Twitter users
| retweets       | int       | Number of times tweet is retweeted by other Twitter users
| tweet_date     | timestamp | Date tweet was created
| tweet_location | varchar   | Location the tweet was send from (if available)
| source         | varchar   | Device/App used to create the tweet, e.g. Twitter for Android/iPhone, Twitter for Desktop etc.
| sentiment      | varchar   | Sentiment of the tweet's text as determined by AWS Comprehend (positive/neutral/negative)

#### Staging Happiness

| Column | Type | Description |
| --- | --- | --- 
| country | varchar | Country happiness data has been collected on
| rank | int | Position of country in happiness ranking
| score | decimal | Happiness score
| confidence_high | decimal | Upper bound of confidence interval for happiness score
| confidence_low | decimal | Lower bound of confidence interval for happiness score
| economy | decimal | Contribution of economic situation to happiness score
| family | decimal | Contribution of family situation to happiness score
| health | decimal | Contribution of life expectancy to happiness score
| freedom | decimal | Contribution of personal/collective freedom to happiness score
| trust | decimal | Contribution of corruption into situation to happiness score
| generosity | decimal | Contribution of perceived generosity to happiness score
| dystopia | decimal | Contribution of dystopia to happiness score

#### Staging Temperature

| Column | Type | Description |
| --- | --- | --- 
date | timestamp | Date temperature was recorded
temperature | decimal | Average temperature measured at recording date
uncertainty | decimal | 95% confidence interval around average temperature
country | varchar | Country where temperature was recorded

#### Users
| Column | Type | Description |
| --- | --- | --- 
| user_id | varchar | c.f. staging_tweets
| name | varchar | c.f. staging_tweets
| nickname | varchar | c.f. staging_tweets
| description | varchar | c.f. staging_tweets
| location | varchar | c.f. user_location in staging_tweets
| followers_count | int | c.f. staging_tweets
| tweets_count | int | c.f. staging_tweets
| creation_date | timestamp | c.f. user_date in staging_tweets
| is_verified | bool | c.f. verified in staging_tweets

#### Sources
| Column | Type | Description |
| --- | --- | --- 
source_id | bigint | auto-incrementing ID of sources
source | varchar | c.f. staging_tweets
is_mobile | bool | Whether the source is a mobile device
is_from_twitter | bool | Whether the source is made by Twitter or a third-party app, e.g. Tweetdeck

#### Happiness
| Column | Type | Description |
| --- | --- | ---
| country | varchar | c.f. staging_happiness
| rank | int | c.f. staging_happiness
| score | decimal | c.f. staging_happiness
| economy | decimal | c.f. staging_happiness
| family | decimal | c.f. staging_happiness
| health | decimal | c.f. staging_happiness
| freedom | decimal | c.f. staging_happiness
| trust | decimal | c.f. staging_happiness
| generosity | decimal | c.f. staging_happiness
| dystopia | decimal | c.f. staging_happiness

#### Temperature
| Column | Type | Description |
| --- | --- | ---
| country | varchar | c.f. staging_temperature
| temp_last_20 | decimal | average temperature over the last 20 years
| temp_last_50 | decimal | average temperature over the last 50 years
| temp_last_100 | decimal | average temperature over the last 100 years

#### Time
| Column | Type | Description |
| --- | --- | ---
| date | timestamp | Union of distinct timestamps from user_date and tweet_date found in staging_tweets
| second | int | Second derived from date
| minute | int | Minute derived from date
| hour | int | Hour derived from date
| week | int | Calendar week derived from date
| month | varchar | Month derived from date
| year | int | Year derived from date
| weekday | varchar | Weekday derived from date

#### Tweets
| Column | Type | Description |
| --- | --- | ---
| tweet_id | varchar | c.f. staging_tweets
| text | varchar | c.f. staging_tweets
| favs | int | c.f. staging_tweets
| retweets | int | c.f. staging_tweets
| creation_date | timestamp | c.f. tweet_date in staging_tweets
| location | varchar | c.f. user_location in staging_tweets
| user_id | varchar | c.f. staging_tweets
| source | varchar | c.f. staging_tweets
| happy_rank | int | Happiness rank of country from user who created the tweet
| happy_score | int | Happiness score of country from user who created the tweet
| temp_last_20 | decimal | Average temperature over last 20 years of country from user who created the tweet
| temp_last_50 | decimal | Average temperature over last 50 years of country from user who created the tweet
| temp_last_100 | decimal | Average temperature over last 100 years of country from user who created the tweet
