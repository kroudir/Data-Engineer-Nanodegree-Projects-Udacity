-- staging tables
CREATE TABLE IF NOT EXISTS public.staging_tweets (
    user_id varchar(256),
    name varchar(256),
    nickname varchar(256),
    description varchar(256),
    user_location varchar(256),
    followers_count int4,
    tweets_count int4,
    user_date timestamp,
    verified bool,
    tweet_id varchar(256),
    -- Twitters character limit is 280
    text varchar(280),
    favs int4,
    retweets int4,
    tweet_date timestamp,
    tweet_location varchar(256),
    source varchar(256),
    sentiment varchar(8)
);

CREATE TABLE IF NOT EXISTS public.staging_happiness (
    country varchar(256),
    rank int2,
    score numeric,
    confidence_high numeric,
    confidence_low numeric,
    economy numeric,
    family numeric,
    health numeric,
    freedom numeric,
    trust numeric,
    generosity numeric,
    dystopia numeric
);

CREATE TABLE IF NOT EXISTS public.staging_temperature (
    "date" timestamp,
    temperature decimal,
    uncertainty decimal,
    country varchar(256)
);

-- dimension tables
CREATE TABLE IF NOT EXISTS public.users (
    user_id varchar(256) NOT NULL,
    name varchar(256),
    nickname varchar(256),
    description varchar(256),
    location varchar(256),
    followers_count int4,
    tweets_count int4,
    creation_date timestamp,
    is_verified bool,
    CONSTRAINT users.pkey PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS public.sources (
    source_id bigint identity(0, 1),
    source varchar(256),
    is_mobile bool,
    is_from_twitter bool,
    CONSTRAINT sources.pkey PRIMARY KEY (device_id)
);

CREATE TABLE IF NOT EXISTS public.happiness (
    country varchar(256) NOT NULL,
    rank int2 NOT NULL,
    score decimal NOT NULL,
    economy decimal,
    family decimal,
    health decimal,
    freedom decimal,
    trust decimal,
    geneorsity decimal,
    dystopia decimal,
    CONSTRAINT happiness.pkey PRIMARY KEY (country)
);

CREATE TABLE IF NOT EXISTS public.temperature (
    country varchar(256),
    temp_last_20 decimal,
    temp_last_50 decimal,
    temp_last_100 decimal,
    CONSTRAINT temperature.pkey PRIMARY KEY (country)
);

CREATE TABLE IF NOT EXISTS public."time" (
    "date" timestamp NOT NULL,
    "second" int4,
    "minute" int4,
    "hour" int4,
    week int4,
    "month" varchar(256),
    "year" int4,
    weekday varchar(256),
    CONSTRAINT time_pkey PRIMARY KEY (date)
);

-- fact table
CREATE TABLE IF NOT EXISTS public.tweets (
    tweet_id varchar(256),
    text varchar(280),
    favs int4,
    retweets int4,
    creation_date timestamp,
    location varchar(256),
    user_id varchar(256),
    source varchar(256),
    happy_rank int2,
    happy_score decimal,
    temp_last_20 decimal,
    temp_last_50 decimal,
    temp_last_100 decimal,
    CONSTRAINT tweets.pkey PRIMARY KEY (tweet_id)
);