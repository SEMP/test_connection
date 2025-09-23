-- Example SQL query to get IP addresses for ping monitoring
-- Query MUST return a single column with IP addresses
-- Column name doesn't matter, only the first column will be used

SELECT ip_address
FROM monitoring_targets
WHERE active = true AND type = 'ping'
ORDER BY priority DESC;

-- More examples:

-- Simple server query:
-- SELECT server_ip FROM servers WHERE monitor_ping = true;

-- Network devices:
-- SELECT management_ip FROM network_devices WHERE enabled = true;

-- Multiple sources with UNION:
-- SELECT ip_address FROM servers WHERE active = true
-- UNION
-- SELECT gateway_ip FROM networks WHERE monitor_gateway = true;

-- With filtering:
-- SELECT host_ip FROM infrastructure
-- WHERE environment = 'production' AND ping_check = true;
