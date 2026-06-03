const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();

const ALLOWED_ORIGINS = [
  'https://theorderofthequietpath.github.io',
  'http://localhost:3333',
  'http://localhost:5173',
  'http://localhost:3001',
];

// Expliciete CORS inclusief preflight voor SSE/POST
app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (!origin || ALLOWED_ORIGINS.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin || '*');
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

app.use(express.json({ limit: '50kb' }));

// Rate limiting: max 5 rapporten per uur per IP
const reportLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 5,
  message: { error: 'Te veel aanvragen. Probeer het over een uur opnieuw.' },
});

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// ─── Rapport-prompt ──────────────────────────────────────────────────────────

function buildPrompt(birth, systems) {
  const hd   = systems.humandesign || {};
  const bazi = systems.bazi        || {};
  const astro= systems.astrology   || {};
  const num  = systems.numerology  || {};

  const name = birth.name || 'jij';
  const dateStr = `${birth.day}.${birth.month}.${birth.year}`;
  const timeStr = birth.hasExactTime
    ? ` om ${String(birth.hour).padStart(2,'0')}:${String(birth.minute||0).padStart(2,'0')}`
    : '';
  const placeStr = birth.place || '';

  // Huidige gelukspilaar
  let currentLuck = '';
  if (bazi.luckCycles && bazi.luckCycles.cycles) {
    const now = new Date().getFullYear();
    const cur = bazi.luckCycles.cycles.find(c => {
      const [s, e] = c.yearRange.split('–').map(Number);
      return now >= s && now <= e;
    }) || bazi.luckCycles.cycles[0];
    if (cur) currentLuck = `${cur.pillar.stem.pol} ${cur.pillar.stem.el} — ${cur.yearRange}`;
  }

  const channelNames = (hd.channels || []).map(c => c.name).join(', ') || 'geen';
  const definedCenters = (hd.centers || []).join(', ') || 'geen';
  const planets = (astro.positions || []).map(p => `${p.nl} in ${p.sign?.name}`).join(', ');

  return `Je bent een diepgaande persoonlijk coach en zielsgids met twintig jaar ervaring in Human Design, BaZi, westerse astrologie en numerologie. Je schrijft rapporten die mensen diep raken — niet door systemen uit te leggen, maar door iemand te helpen zichzelf te herkennen en richting te vinden.

Je schrijft NOOIT als een handleiding. Je schrijft als iemand die de persoon kent.

━━━ GEBOORTEGEGEVENS ━━━
Naam: ${name}
Geboren: ${dateStr}${timeStr}${placeStr ? ` in ${placeStr}` : ''}
Geslacht: ${birth.gender === 'v' ? 'vrouw' : 'man'}

━━━ BEREKENDE KAARTDATA ━━━

HUMAN DESIGN
Type: ${hd.type || '—'}
Strategie: ${hd.strategy || '—'}
Autoriteit: ${hd.authority || '—'}
Profiel: ${hd.profile || '—'}
Definitie: ${hd.definition || '—'}
Gedefinieerde centra: ${definedCenters}
Actieve kanalen: ${channelNames}
Incarnatiekruis poorten: ${hd.cross ? `${hd.cross.pSun}/${hd.cross.pEarth} & ${hd.cross.dSun}/${hd.cross.dEarth}` : '—'}
Not-self thema: ${hd.notSelf || '—'}
Handtekening: ${hd.signature || '—'}

BAZI (VIER PILAREN)
Dagmeester: ${bazi.dayMaster ? `${bazi.dayMaster.pol} ${bazi.dayMaster.el} (${bazi.dayMaster.cn})` : '—'}
Sterkste element: ${bazi.strongest?.el || '—'}
Ontbrekende elementen: ${bazi.missing?.join(', ') || 'geen'}
Huidige gelukspilaar: ${currentLuck || '—'}

WESTERSE ASTROLOGIE
Zon: ${astro.sun?.sign?.name || '—'}
Maan: ${astro.moon?.sign?.name || '—'}
Ascendant: ${astro.ascendant?.sign?.name || 'niet berekend'}
Planeten: ${planets || '—'}

NUMEROLOGIE
Levenspad: ${num.lifePath || '—'}
Uitdrukking: ${num.expression || '—'}
Zielsdrang: ${num.soulUrge || '—'}
Persoonlijkheid: ${num.personality || '—'}

━━━ SCHRIJFINSTRUCTIES ━━━

TAAL & TOON:
1. Schrijf ALTIJD in de tweede persoon ("jij", "je", "jouw")
2. Noem ${name} bij naam — minimaal één keer per hoofdsectie
3. Vermijd droge systeemuitleg. Gebruik systemen als bewijs, niet als onderwerp
4. Verbind systemen: "Niet alleen je HD bevestigt dit — je BaZi dagmeester en je levenspad doen dit ook"
5. Schrijf in warm, helder, coachend Nederlands. Geen spiritueel cliché-taal
6. Elke alinea moet het gevoel geven: "Dit gaat over mij"
7. Wees concreet: noem situaties, keuzes, patronen die herkend worden
8. Het rapport moet minimaal 7000 woorden bevatten

HTML-OPMAAK (VERPLICHT — gebruik NOOIT markdown):
9. Gebruik UITSLUITEND HTML-tags. NOOIT **bold**, *italic*, ## headers of andere markdown.
10. Vetgedrukt: gebruik <strong>tekst</strong>
11. Cursief: gebruik <em>tekst</em>
12. Sub-koppen binnen secties: gebruik <h3>titel</h3>
13. Alinea's: gebruik <p>tekst</p>
14. Elke sectie heeft 3-4 sub-koppen die de inhoud structureren
15. Gebruik dit patroon voor kerninzichten:
    <div class="insight"><strong>Kernpunt:</strong> de kernzin die blijft hangen.</div>
16. Voor actieplan-punten gebruik:
    <div class="action-item"><h4>Actie: De titel</h4><p>Uitleg van de actie.</p></div>
17. Voor het 30-dagenplan per week:
    <div class="week-block"><h4>Week 1 — Titel</h4><p>Beschrijving.</p><p class="daily-intention"><em>Dagelijkse intentie: "De intentie."</em></p></div>

━━━ STRUCTUUR (schrijf het rapport nu volledig uit) ━━━

<div class="report">

<div class="report-cover">
  <div class="report-label">Persoonlijk Zielsblauwdruk Rapport</div>
  <h1 class="report-name">${name}</h1>
  <div class="report-date">${dateStr}${timeStr}${placeStr ? ` · ${placeStr}` : ''}</div>
  <div class="report-systems">Human Design · BaZi · Astrologie · Numerologie</div>
</div>

<section class="report-section" id="kern">
  <div class="section-number">01</div>
  <h2>Wie Jij Bent — De Kern van Jouw Ontwerp</h2>
  <!-- 800-1000 woorden. Gebruik 3-4 <h3> sub-koppen zoals:
       "De gave die je niet altijd herkent", "Wat drie systemen gemeenschappelijk zeggen", "De keerzijde van je kracht"
       Begin met een openingszin die onmiddellijk herkend wordt.
       Gebruik <div class="insight"> voor de 1-2 sterkste kernzinnen. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST MET H3 SUB-KOPPEN EN INSIGHT DIVS]
  </div>
</section>

<section class="report-section" id="energie">
  <div class="section-number">02</div>
  <h2>Hoe Jij Werkt — Energie, Ritme & Beslissen</h2>
  <!-- 800-1000 woorden. Gebruik 3-4 <h3> sub-koppen zoals:
       "Jouw energietype en wat dat betekent in de praktijk", "Het ontbrekende element", "Hoe jij beslissingen neemt"
       Wanneer heeft ${name} energie? Wanneer loopt die leeg?
       Gebruik <div class="insight"> voor de kernzin over beslissen. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST MET H3 SUB-KOPPEN EN INSIGHT DIVS]
  </div>
</section>

<section class="report-section" id="relaties">
  <div class="section-number">03</div>
  <h2>Relaties — Wie Jij Nodig Hebt & Wat Jij Brengt</h2>
  <!-- 800-1000 woorden. Gebruik 3-4 <h3> sub-koppen zoals:
       "Wat jij emotioneel nodig hebt", "Jouw profiel in relaties", "Wat jij brengt — en hoe je dat beschermt"
       Zowel romantisch als vriendschap en werk. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST MET H3 SUB-KOPPEN EN INSIGHT DIVS]
  </div>
</section>

<section class="report-section" id="werk">
  <div class="section-number">04</div>
  <h2>Werk & Geld — Waar Jij Floreert</h2>
  <!-- 800-1000 woorden. Gebruik 3-4 <h3> sub-koppen zoals:
       "Jouw bijdrage is niet in volume maar in richting", "De ideale werkomgeving", "Timing en geld", "Wat niet werkt — en waarom"
       Gebruik <div class="insight"> voor de sterkste werkinzicht. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST MET H3 SUB-KOPPEN EN INSIGHT DIVS]
  </div>
</section>

<section class="report-section" id="missie">
  <div class="section-number">05</div>
  <h2>Jouw Levensmissie — Waarom Jij Hier Bent</h2>
  <!-- 800-1000 woorden. Gebruik 3-4 <h3> sub-koppen zoals:
       "Het incarnatiekruis: vier poorten, één verhaal", "Het levenspad als kompas", "De periode die nu speelt", "Wat jij hier komt brengen"
       Dit is het emotionele hoogtepunt. Gebruik <div class="insight"> voor de centrale missieverklaring.
       Sluit af met een persoonlijk, krachtig paragraaf aan ${name}. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST MET H3 SUB-KOPPEN EN INSIGHT DIVS]
  </div>
</section>

<section class="report-section" id="schaduw">
  <div class="section-number">06</div>
  <h2>Blinde Vlekken & Schaduw — Wat Je Nog Niet Ziet</h2>
  <!-- 700-900 woorden. Gebruik 3 <h3> sub-koppen zoals:
       "Het not-self patroon", "Wat je absorbeert van anderen", "De schaduw van jouw grootste kracht"
       Zonder oordeel, met compassie. Gebruik <div class="insight"> voor de centrale herkenningszin. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST MET H3 SUB-KOPPEN EN INSIGHT DIVS]
  </div>
</section>

<section class="report-section" id="actieplan">
  <div class="section-number">07</div>
  <h2>Jouw Persoonlijk Actieplan</h2>
  <!-- Gebruik VERPLICHT de <div class="action-item"> structuur voor elk actiepunt.
       3 gebieden met elk 2 actiepunten. Totaal 6 action-item divs.
       Elk actiepunt heeft een <h4> titel en een <p> uitleg van 3-4 zinnen.
       Begin met een korte inleidende paragraaf <p>. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

<section class="report-section" id="30dagen">
  <div class="section-number">08</div>
  <h2>30-Dagen Groeiplan</h2>
  <!-- Gebruik VERPLICHT <div class="week-block"> voor elke week (4 stuks).
       Elk week-blok: <h4>Week X — Titel</h4> + <p>beschrijving</p> + <p class="daily-intention"><em>Dagelijkse intentie: "..."</em></p>
       Sluit het hele rapport af met <div class="report-closing"><p>persoonlijk slotwoord aan ${name}</p></div> -->
  <div class="section-body">
    [SCHRIJF HIER MET WEEK-BLOCK DIVS]
  </div>
</section>

</div>

CRUCIAAL: Gebruik NOOIT **markdown** of *markdown* of ## markdown. Alleen HTML-tags.
Vervang alle placeholders door echte inhoud. Verwijder alle HTML-commentaren.`;
}

// ─── Endpoint ────────────────────────────────────────────────────────────────

// Streaming endpoint — stuurt het rapport stuk voor stuk terug (SSE)
app.post('/api/report', reportLimiter, async (req, res) => {
  const { birth, systems, code } = req.body;

  if (!birth || !systems) {
    return res.status(400).json({ error: 'Ontbrekende geboortegegevens.' });
  }
  if (!birth.year || !birth.month || !birth.day) {
    return res.status(400).json({ error: 'Onvolledige geboortedatum.' });
  }
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('ANTHROPIC_API_KEY not set');
    return res.status(500).json({ error: 'Server configuratie fout.' });
  }

  // SSE headers — houdt verbinding open tijdens generatie
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const sendEvent = (data) => {
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  try {
    const prompt = buildPrompt(birth, systems);
    let fullReport = '';

    const stream = await client.messages.stream({
      model: 'claude-sonnet-4-6',
      max_tokens: 12000,
      messages: [{ role: 'user', content: prompt }],
    });

    for await (const chunk of stream) {
      if (chunk.type === 'content_block_delta' && chunk.delta?.type === 'text_delta') {
        const text = chunk.delta.text;
        fullReport += text;
        sendEvent({ type: 'chunk', text });
      }
    }

    sendEvent({ type: 'done', words: fullReport.split(/\s+/).length });
    res.end();

  } catch (err) {
    console.error('Claude API error:', err.message, err.status);
    sendEvent({ type: 'error', message: 'Rapport generatie mislukt: ' + err.message });
    res.end();
  }
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Stille Pad backend draait op poort ${PORT}`));
