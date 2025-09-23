-- Get server IP addresses
SELECT ip_address FROM servers WHERE status = 'active' AND ping_monitoring = true;