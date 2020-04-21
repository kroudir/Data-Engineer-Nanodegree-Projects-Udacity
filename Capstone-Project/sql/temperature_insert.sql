INSERT INTO temperature (country, temp_last_20, temp_last_50, temp_last_100)
    SELECT DISTINCT country,
            (
               SELECT avg(temperature)
               FROM staging_temperature
               WHERE year(date) >= 2019 - 20
               GROUP BY country
               ORDER BY country) AS temp_last_20,
            (
                SELECT avg(temperature)
                FROM staging_temperature
                WHERE year(date) >= 2019 - 50
                GROUP BY country
                ORDER BY country) AS temp_last_50,
            (
                SELECT avg(temperature)
                FROM staging_temperature
                WHERE year(date) >= 2019 - 100
                GROUP BY country
                ORDER BY country) AS temp_last_100
    ORDER BY country;
