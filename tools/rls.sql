-- RLS op de meettabellen van Nexus
-- Voer uit in Supabase Dashboard > SQL Editor
--
-- Waarom: de publishable key staat in de browserbundle van nexus-web (geverifieerd
-- 2026-07-31 in /assets/index-*.js op nexus-ejdetheije.vercel.app). Zonder RLS kan
-- iedereen die hem daaruit haalt de 49.919 metingen en 3.122 events niet alleen lezen
-- maar ook wijzigen en wissen. Lezen blijft hierna publiek - dat is de bestaande
-- situatie, niet slechter - maar schrijven en verwijderen kan niet meer.
--
-- Dit raakt BEWUST alleen sensor_readings en events: die leest nexus-web alleen.
-- commands, settings, moods en mood_users worden vanuit de browser geschreven; RLS
-- daarop aanzetten breekt Commands, Settings en Mood. Dat vraagt een eigen ontwerpstap
-- (inloggen, of een serverroute ertussen) en hoort niet in dit bestand.
--
-- De Pico is niet geraakt: die schrijft met dezelfde anon-rol maar valt onder de
-- insert-policy hieronder.

ALTER TABLE public.sensor_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.events ENABLE ROW LEVEL SECURITY;

-- Idempotent: drop-dan-create, zodat herhaald draaien geen "policy already exists" geeft.
DROP POLICY IF EXISTS "publiek leesbaar" ON public.sensor_readings;
DROP POLICY IF EXISTS "publiek leesbaar" ON public.events;
DROP POLICY IF EXISTS "pico schrijft" ON public.sensor_readings;
DROP POLICY IF EXISTS "pico schrijft" ON public.events;

CREATE POLICY "publiek leesbaar" ON public.sensor_readings FOR SELECT USING (true);
CREATE POLICY "publiek leesbaar" ON public.events FOR SELECT USING (true);

-- Zonder deze twee stopt de Pico met loggen: hij schrijft met de publishable key en
-- valt dus onder RLS. Alleen INSERT - update en delete blijven voor iedereen dicht,
-- ook voor de Pico, die ze niet nodig heeft.
CREATE POLICY "pico schrijft" ON public.sensor_readings FOR INSERT WITH CHECK (true);
CREATE POLICY "pico schrijft" ON public.events FOR INSERT WITH CHECK (true);

-- Verificatie: vier policies, en rowsecurity = true op beide tabellen.
SELECT tablename, policyname, cmd FROM pg_policies
WHERE schemaname = 'public' AND tablename IN ('sensor_readings', 'events')
ORDER BY tablename, cmd;
