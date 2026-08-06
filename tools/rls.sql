-- RLS op de meettabellen van Nexus
-- Voer uit in Supabase Dashboard > SQL Editor
--
-- Waarom: de publishable key staat in de browserbundle van nexus-web (geverifieerd
-- 2026-07-31 in /assets/index-*.js op nexus-ejdetheije.vercel.app). Zonder RLS kan
-- iedereen die hem daaruit haalt de 49.919 metingen en 3.122 events niet alleen lezen
-- maar ook wijzigen en wissen. Lezen blijft hierna publiek - dat is de bestaande
-- situatie, niet slechter - maar schrijven en verwijderen kan niet meer.
--
-- Deel 1 raakt alleen sensor_readings en events: die leest nexus-web alleen.
-- commands, settings, moods en mood_users worden vanuit de browser geschreven en
-- staan in deel 2, toegevoegd 2026-08-06 na een critical advisor-melding
-- (rls_disabled_in_public) van Supabase.
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


-- ===========================================================================
-- Deel 2 (2026-08-06): commands, settings, moods, mood_users
-- ===========================================================================
-- Waarom nu: Supabase meldde deze vier als CRITICAL rls_disabled_in_public.
-- Vastgesteld met de publishable key: alle vier geven rijen terug, terwijl de
-- energy_*-tabellen leeg teruggeven - die hebben RLS al aan zonder select-policy.
--
-- Wat dit WEL doet: anon DELETE gaat op alle vier dicht, en anon UPDATE op moods
-- en mood_users. Dat is de schade die vandaag mogelijk is en niemand nodig heeft:
-- 222 commands, 11 moods en 3 mood_users zijn nu wisbaar door iedereen met de
-- publishable key uit de browserbundle.
--
-- Wat dit NIET doet: lezen en de verbs die de apps echt gebruiken blijven publiek.
-- Wie de key heeft kan nog steeds een rij in commands zetten, en het bord voert die
-- uit (reset, set_setting). Dat dichtzetten vraagt inloggen of een serverroute
-- ertussen - een eigen ontwerpstap, geen policy.
--
-- De verbs per tabel zijn afgeleid uit de code, niet gegokt:
--   commands   select (Pico get_pending_commands), insert (Commands.tsx, Mood.tsx,
--              Settings.tsx), update (Pico mark_executed)
--   settings   select (Pico get_settings, Dashboard, Settings), insert + update
--              (Settings.tsx doet upsert - PostgREST vraagt daarvoor beide)
--   moods      select + insert (Mood.tsx)
--   mood_users select + insert (Mood.tsx)
-- Geen enkel pad doet DELETE. Zou er later een bijkomen, dan is dat zichtbaar als
-- een fout en niet als stille dataverlies.

ALTER TABLE public.commands   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.settings   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.moods      ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mood_users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "publiek leesbaar" ON public.commands;
DROP POLICY IF EXISTS "publiek leesbaar" ON public.settings;
DROP POLICY IF EXISTS "publiek leesbaar" ON public.moods;
DROP POLICY IF EXISTS "publiek leesbaar" ON public.mood_users;
DROP POLICY IF EXISTS "web voegt toe" ON public.commands;
DROP POLICY IF EXISTS "web voegt toe" ON public.settings;
DROP POLICY IF EXISTS "web voegt toe" ON public.moods;
DROP POLICY IF EXISTS "web voegt toe" ON public.mood_users;
DROP POLICY IF EXISTS "pico vinkt af" ON public.commands;
DROP POLICY IF EXISTS "web wijzigt" ON public.settings;

CREATE POLICY "publiek leesbaar" ON public.commands   FOR SELECT USING (true);
CREATE POLICY "publiek leesbaar" ON public.settings   FOR SELECT USING (true);
CREATE POLICY "publiek leesbaar" ON public.moods      FOR SELECT USING (true);
CREATE POLICY "publiek leesbaar" ON public.mood_users FOR SELECT USING (true);

CREATE POLICY "web voegt toe" ON public.commands   FOR INSERT WITH CHECK (true);
CREATE POLICY "web voegt toe" ON public.settings   FOR INSERT WITH CHECK (true);
CREATE POLICY "web voegt toe" ON public.moods      FOR INSERT WITH CHECK (true);
CREATE POLICY "web voegt toe" ON public.mood_users FOR INSERT WITH CHECK (true);

-- Zonder deze twee UPDATE-policies blijft elk commando eeuwig openstaan (de Pico
-- kan executed_at niet zetten en pikt het elke ronde opnieuw op) en weigert de
-- upsert op de Settings-pagina zodra de key al bestaat.
CREATE POLICY "pico vinkt af" ON public.commands FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "web wijzigt"   ON public.settings FOR UPDATE USING (true) WITH CHECK (true);

-- Verificatie deel 2: tien policies over vier tabellen, en rowsecurity = true.
SELECT tablename, string_agg(cmd, ',' ORDER BY cmd) AS verbs, count(*) AS aantal
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN ('commands', 'settings', 'moods', 'mood_users')
GROUP BY tablename ORDER BY tablename;

SELECT relname, relrowsecurity FROM pg_class
WHERE relnamespace = 'public'::regnamespace
  AND relname IN ('commands', 'settings', 'moods', 'mood_users')
ORDER BY relname;
