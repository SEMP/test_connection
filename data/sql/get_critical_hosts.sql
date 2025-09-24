-- Get critical infrastructure hosts with module and criticality info
SELECT ip_address,
       CONCAT(module_name, '_Critical_L', criticality_level) as label
FROM infrastructure_hosts i
JOIN modules m ON i.module_id = m.id
WHERE criticality_level >= 3 AND monitor_ping = true
ORDER BY criticality_level DESC;