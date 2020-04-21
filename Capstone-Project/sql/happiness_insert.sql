INSERT INTO happiness (country, rank, score, economy, family, health, freedom, trust, generosity, dystopia)
SELECT DISTINCT country,
                rank,
                score,
                economy,
                family,
                health,
                freedom,
                trust,
                generosity,
                dystopia
FROM staging_happiness;