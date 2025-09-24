-- Get server IP addresses with labels
SELECT ip_address, server_name as label
FROM servers
WHERE status = 'active' AND ping_monitoring = true;

-- Single column example (backward compatible):
-- SELECT ip_address FROM servers WHERE status = 'active' AND ping_monitoring = true;