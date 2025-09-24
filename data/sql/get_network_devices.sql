-- Get network device IP addresses with module labels
SELECT management_ip,
       CONCAT(device_type, '_', module_name) as label
FROM network_devices n
JOIN modules m ON n.module_id = m.id
WHERE n.enabled = true;