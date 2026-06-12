# Nexus Web

React-dashboard voor het Nexus-project (Pico Lab experiment 06).
Toont live sensordata en stuurt commands naar de Raspberry Pi Pico 2W via Supabase.

**Stack:** Vite + React + TypeScript + Tailwind CSS + Supabase JS

## Pagina's

| Pagina     | Functie                                                    |
|------------|------------------------------------------------------------|
| Dashboard  | Live sensorkaarten: temp, vocht, licht, luchtdruk (5s poll)|
| Commands   | LCD-bericht, buzzer, ventilator aan/uit                    |
| Settings   | `poll_interval_s` en `temp_alert_threshold` instellen      |
| Events     | Event log (bewegingsdetectie)                              |

## Lokaal draaien

```bash
cd nexus-web
npm install
npm run dev
```

Maak een `.env.local` aan met de Supabase-credentials:

```
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

## Deployment

Vercel (ejdetheijes-projects). Verbind de GitHub-repo, stel de twee
environment variables in via het Vercel-dashboard, en deploy.
