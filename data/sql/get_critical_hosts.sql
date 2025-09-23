-- Get critical infrastructure hosts
SELECT ip_address FROM infrastructure_hosts
WHERE criticality_level >= 3 AND monitor_ping = true
ORDER BY criticality_level DESC;