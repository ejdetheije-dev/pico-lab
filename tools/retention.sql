-- PICO-47: Data retentie via pg_cron
-- Voer uit in Supabase Dashboard > SQL Editor
-- Bewaart 365 dagen data; daarna dagelijks opschonen

-- Stap 1: voeg created_at toe aan events als die nog ontbreekt
ALTER TABLE public.events ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();

-- Stap 2: schakel pg_cron in
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Stap 3: dagelijkse cleanup om 03:00 UTC
SELECT cron.schedule(
  'nexus-sensor-retention',
  '0 3 * * *',
  $$DELETE FROM public.sensor_readings WHERE created_at < NOW() - INTERVAL '365 days'$$
);

SELECT cron.schedule(
  'nexus-events-retention',
  '5 3 * * *',
  $$DELETE FROM public.events WHERE created_at < NOW() - INTERVAL '365 days'$$
);

-- Verificatie: controleer geplande jobs
SELECT jobid, jobname, schedule, command FROM cron.job;
