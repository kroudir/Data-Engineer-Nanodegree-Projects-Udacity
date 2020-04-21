INSERT INTO users (user_id, name, nickname, descrption, location, followers_count, tweets_count, creation_date, is_verified)
    SELECT DISTINCT user_id,
                    name,
                    nickname,
                    descrpition,
                    user_location,
                    followers_count,
                    tweets_count,
                    user_date,
                    verified
    FROM staging_tweets;
