-- Top 10 CPI clubs in latest season
SELECT team_id, cpi, cpi_tier
FROM club_metrics
WHERE season = (SELECT MAX(season) FROM club_metrics)
ORDER BY cpi DESC
LIMIT 10;

-- Under-monetized clubs
SELECT team_id, attendance_pct, ticket_price_proxy, cpi
FROM club_metrics
WHERE season = (SELECT MAX(season) FROM club_metrics)
  AND attendance_pct >= 0.80
  AND ticket_price_proxy <= 32
ORDER BY attendance_pct DESC;
