
DROP MATERIALIZED VIEW IF EXISTS "student_melika_nobakhtian".mv_airbnb_neighbourhood_summary;

CREATE MATERIALIZED VIEW "student_melika_nobakhtian".mv_airbnb_neighbourhood_summary AS
WITH calendar_30 AS (
    SELECT
        listing_id,
        ROUND(AVG(CASE WHEN available THEN 1.0 ELSE 0.0 END)::numeric, 4) AS availability_30_rate
    FROM core.calendar_day
    WHERE date >= CURRENT_DATE
      AND date < CURRENT_DATE + INTERVAL '30 days'
    GROUP BY listing_id
),
review_counts AS (
    SELECT
        listing_id,
        COUNT(*) AS total_reviews
    FROM core.review
    GROUP BY listing_id
)
SELECT
    l.neighbourhood_id::text                                                               AS neighbourhood,
    COUNT(l.listing_id)                                                                    AS num_listings,
    ROUND(AVG(l.listing_price)::numeric, 2)                                                AS avg_price,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY l.listing_price)::numeric, 2)       AS median_price,
    ROUND(AVG(l.minimum_nights)::numeric, 2)                                               AS avg_minimum_nights,
    COALESCE(SUM(r.total_reviews), 0)                                                      AS total_reviews,
    ROUND(COALESCE(SUM(r.total_reviews)::numeric / NULLIF(COUNT(l.listing_id), 0), 0), 2) AS reviews_per_listing,
    ROUND(AVG(c30.availability_30_rate)::numeric, 4)                                       AS availability_30_rate
FROM core.listing l
LEFT JOIN calendar_30   c30 ON c30.listing_id = l.listing_id
LEFT JOIN review_counts r   ON r.listing_id   = l.listing_id
GROUP BY l.neighbourhood_id;

-- Index 1: fast lookup and filtering by neighbourhood
CREATE INDEX idx_mv_neighbourhood
    ON "student_melika_nobakhtian".mv_airbnb_neighbourhood_summary (neighbourhood);

-- Index 2: fast sorting by number of listings ]
CREATE INDEX idx_mv_num_listings
    ON "student_melika_nobakhtian".mv_airbnb_neighbourhood_summary (num_listings DESC);
