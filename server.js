const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const Anthropic = require('@anthropic-ai/sdk');

const app = express();

// CORS: sta alleen jouw GitHub Pages domein toe (pas aan naar jouw domein)
const ALLOWED_ORIGINS = [
  'https://theorderofthequietpath.github.io',
  'http://localhost:3333',
  'http://localhost:5173',
  'http://localhost:3001',
];

app.use(cors({
  origin: (origin, cb) => {
    if (!origin || ALLOWED_ORIGINS.includes(origin)) return cb(null, true);
    cb(new Error('Not allowed by CORS'));
  },
}));

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

1. Schrijf ALTIJD in de tweede persoon ("jij", "je", "jouw")
2. Noem ${name} bij naam — minimaal één keer per hoofdsectie
3. Vermijd droge systeemuitleg. Gebruik systemen als bewijs, niet als onderwerp
4. Verbind systemen: "Niet alleen je HD bevestigt dit — je BaZi dagmeester en je levenspad doen dit ook"
5. Schrijf in warm, helder, coachend Nederlands. Geen spiritueel cliché-taal
6. Elke alinea moet het gevoel geven: "Dit gaat over mij"
7. Wees concreet: noem situaties, keuzes, patronen die herkend worden
8. Het rapport moet minimaal 7000 woorden bevatten
9. Gebruik de HTML-structuur hieronder exact zoals aangegeven

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
  <!-- 700-900 woorden. Syntheseer HD type + BaZi dagmeester + zon-teken.
       Begin met een zin die onmiddellijk herkend wordt.
       Beschrijf de essentie van wie ${name} is. Wat maakt hem/haar uniek?
       Welk patroon keert terug in alle systemen? -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

<section class="report-section" id="energie">
  <div class="section-number">02</div>
  <h2>Hoe Jij Werkt — Energie, Ritme & Beslissen</h2>
  <!-- 700-900 woorden. Autoriteit + strategie + BaZi element + levenspad.
       Wanneer heeft ${name} energie? Wanneer loopt die leeg?
       Hoe neemt hij/zij de beste beslissingen? Wat werkt NIET?
       Praktisch en concreet — herkenbare situaties benoemen. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

<section class="report-section" id="relaties">
  <div class="section-number">03</div>
  <h2>Relaties — Wie Jij Nodig Hebt & Wat Jij Brengt</h2>
  <!-- 700-900 woorden. HD profiel + maan-teken + open centra + missing elements.
       Communicatiestijl, wat ${name} nodig heeft in relaties.
       Waar loopt hij/zij vast? Wat trekt hij/zij aan (en waarom)?
       Zowel romantische relaties als vriendschappen en werk. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

<section class="report-section" id="werk">
  <div class="section-number">04</div>
  <h2>Werk & Geld — Waar Jij Floreert</h2>
  <!-- 700-900 woorden. HD type + kanalen + BaZi dagmeester + uitdrukkingsgetal.
       Ideale werkomgeving. Talenten die misschien onderschat worden.
       Valkuilen in werk en carrière. Timing (wanneer handelen, wanneer wachten).
       Concrete voorbeelden van hoe dit er uitziet. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

<section class="report-section" id="missie">
  <div class="section-number">05</div>
  <h2>Jouw Levensmissie — Waarom Jij Hier Bent</h2>
  <!-- 700-900 woorden. Incarnatiekruis + levenspad + gelukspilaar + ascendant.
       Dit is het emotionele hoogtepunt van het rapport.
       Wat is de diepere richting van ${name} zijn/haar leven?
       Wat worden ze geroepen om te doen, te zijn, te leren?
       Schrijf dit met zorg — dit raakt mensen diep. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

<section class="report-section" id="schaduw">
  <div class="section-number">06</div>
  <h2>Blinde Vlekken & Schaduw — Wat Je Nog Niet Ziet</h2>
  <!-- 600-800 woorden. Open centra + not-self thema + schaduwelementen.
       Zonder oordeel, met compassie en herkenning.
       Patronen die steeds terugkeren. Conditionering van buitenaf.
       Hoe ${name} soms tegen zichzelf in werkt — en waarom. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

<section class="report-section" id="actieplan">
  <div class="section-number">07</div>
  <h2>Jouw Persoonlijk Actieplan</h2>
  <!-- 500-700 woorden. 3 gebieden: werk/missie, relaties, innerlijke groei.
       Per gebied: 2-3 CONCRETE, specifieke actiepunten voor DEZE persoon.
       Niet generiek — elk punt moet logisch volgen uit de kaartdata.
       Formuleer als uitnodiging, niet als opdracht. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

<section class="report-section" id="30dagen">
  <div class="section-number">08</div>
  <h2>30-Dagen Groeiplan</h2>
  <!-- 500-600 woorden. Week 1 t/m 4.
       Elke week een specifieke focus die past bij de kaart.
       Dagelijkse oefening of intentie per week.
       Eindig met een persoonlijk slotwoord aan ${name}. -->
  <div class="section-body">
    [SCHRIJF HIER DE VOLLEDIGE TEKST]
  </div>
</section>

</div>

Schrijf nu het volledige rapport. Vervang elk [SCHRIJF HIER DE VOLLEDIGE TEKST] door de werkelijke inhoud. Verwijder de HTML-commentaren in het eindresultaat.`;
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
