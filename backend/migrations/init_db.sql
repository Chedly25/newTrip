-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create initial sample data
INSERT INTO cities (name, region, department, country, population, tourist_season) VALUES 
('Paris', 'Île-de-France', 'Paris', 'France', 2161000, 'all_year'),
('Lyon', 'Auvergne-Rhône-Alpes', 'Rhône', 'France', 516092, 'spring_summer'),
('Marseille', 'Provence-Alpes-Côte d''Azur', 'Bouches-du-Rhône', 'France', 868277, 'summer'),
('Toulouse', 'Occitanie', 'Haute-Garonne', 'France', 479553, 'spring_summer'),
('Nice', 'Provence-Alpes-Côte d''Azur', 'Alpes-Maritimes', 'France', 342637, 'summer')
ON CONFLICT DO NOTHING;