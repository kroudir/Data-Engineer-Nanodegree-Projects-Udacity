INSERT into sources (source, is_mobile, is_from_twitter)
SELECT DISTINCT source,
                CASE
                    WHEN source LIKE "%Android" OR device LIKE "%iPhone" THEN TRUE
                    ELSE FALSE
                END,
                CASE WHEN source LIKE "%Twitter%" THEN TRUE
                     ELSE FALSE
                END
FROM staging_tweets;