select
    plant_id,
    plant_name,
    plant_type,
    region,
    country_code,
    timezone
from (
    values
        ('PLT-US01', 'Chicago Manufacturing', 'MANUFACTURING', 'US', 'US', 'America/Chicago'),
        ('PLT-DE01', 'Stuttgart Manufacturing', 'MANUFACTURING', 'EMEA', 'DE', 'Europe/Berlin'),
        ('PLT-SG01', 'Singapore Manufacturing', 'MANUFACTURING', 'APAC', 'SG', 'Asia/Singapore'),
        ('DC-US01', 'Atlanta Distribution Center', 'DISTRIBUTION', 'US', 'US', 'America/New_York'),
        ('DC-DE01', 'Rotterdam Distribution Center', 'DISTRIBUTION', 'EMEA', 'NL', 'Europe/Amsterdam')
) as t(plant_id, plant_name, plant_type, region, country_code, timezone)
