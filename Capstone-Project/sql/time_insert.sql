INSERT INTO time ("date", "second", "minute", "hour", week, "month", "year", weekday)
SELECT DISTINCT tweet_date,
       extract(second from tweet_date),
       extract(minute from tweet_date),
       extract(hour from tweet_date),
       extract(week from tweet_date),
       extract(month from tweet_date),
       extract(year from tweet_date),
       extract(dayofweek from tweet_date)
FROM staging_tweets
UNION
SELECT DISTINCT user_date,
        extract(second from user_date),
        extract(minute from user_date),
        extract(hour from user_date),
        extract(week from user_date),
        extract(month from user_date),
        extract(year from user_date),
        extract(dayofweek from user_date)
FROM staging_tweets;

