INSERT INTO tweets (tweet_id,
                    text,
                    favs,
                    retweets,
                    creation_date,
                    location,
                    user_id,
                    source,
                    happy_rank,
                    happy_score,
                    temp_last_20,
                    temp_last_50,
                    temp_last_100)
SELECT t.tweet_id,
       t.text,
       t.favs,
       t.retweets,
       t.creation_date,
       t.user_location,
       t.user_id,
       t.source,
       h.rank,
       h.score,
       temp.last_20,
       temp.last_50,
       temp.last_100
FROM staging_tweets t
    LEFT JOIN happiness h
        ON t.user_location = h.country
    LEFT JOIN temperature temp
        ON t.user_location = temp.country

