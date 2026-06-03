const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const Anthropic = require('@anthropic-ai/sdk');
const { Resend } = require('resend');

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
const resend = new Resend(process.env.RESEND_API_KEY);

const ADMIN_EMAIL   = process.env.ADMIN_EMAIL   || 'jouw@email.be';
const ADMIN_TOKEN   = process.env.ADMIN_TOKEN   || 'verander-dit-in-render';
const FROM_EMAIL    = process.env.FROM_EMAIL    || 'onboarding@resend.dev';
const BACKEND_HOST  = process.env.RENDER_EXTERNAL_URL || 'https://toqp-backend.onrender.com';

const REPORT_NAMES = {
  full:         { nl: 'Persoonlijk Zielsblauwdruk Rapport', prijs: '€39' },
  humandesign:  { nl: 'Human Design Rapport',               prijs: '€15' },
  bazi:         { nl: 'BaZi Vier Pilaren Rapport',          prijs: '€12' },
  saju:         { nl: 'Saju Rapport',                       prijs: '€12' },
  astrology:    { nl: 'Astrologie Rapport',                 prijs: '€15' },
  numerology:   { nl: 'Numerologie Rapport',                prijs: '€9'  },
};

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

// ─── Bestellingen ────────────────────────────────────────────────────────────

const orderLimiter = rateLimit({ windowMs: 60 * 60 * 1000, max: 10 });

// POST /api/order — klant dient bestelling in na betaling
app.post('/api/order', orderLimiter, async (req, res) => {
  const { birth, systems, reportType, customerEmail } = req.body;

  if (!birth || !customerEmail || !reportType) {
    return res.status(400).json({ error: 'Naam, e-mail en rapporttype zijn verplicht.' });
  }
  if (!REPORT_NAMES[reportType]) {
    return res.status(400).json({ error: 'Onbekend rapporttype.' });
  }

  // Encodeer alles in de magic link — geen database nodig
  const payload = Buffer.from(JSON.stringify({
    birth, systems: systems || {}, reportType, customerEmail, ts: Date.now(),
  })).toString('base64url');

  const magicLink = `${BACKEND_HOST}/admin/generate?d=${payload}&t=${ADMIN_TOKEN}`;
  const rapport   = REPORT_NAMES[reportType];

  try {
    // 1. Melding aan jou (admin)
    await resend.emails.send({
      from: FROM_EMAIL, to: ADMIN_EMAIL,
      subject: `🌙 Nieuwe bestelling: ${rapport.nl} — ${birth.name}`,
      html: buildAdminEmail(birth, rapport, customerEmail, magicLink),
    });

    // 2. Bevestiging aan klant
    await resend.emails.send({
      from: FROM_EMAIL, to: customerEmail,
      subject: `Bevestiging: jouw ${rapport.nl} — Het Stille Pad`,
      html: buildConfirmEmail(birth.name, rapport.nl),
    });

    res.json({ success: true });
  } catch (err) {
    console.error('Resend error:', err);
    res.status(500).json({ error: 'E-mail kon niet worden verstuurd. Probeer opnieuw.' });
  }
});

// GET /admin/generate — jij klikt op de magic link, ziet een bevestigingspagina
app.get('/admin/generate', (req, res) => {
  const { d, t } = req.query;
  if (!d || t !== ADMIN_TOKEN) return res.status(403).send('<h1>Toegang geweigerd</h1>');

  let order;
  try { order = JSON.parse(Buffer.from(d, 'base64url').toString()); }
  catch { return res.status(400).send('<h1>Ongeldige link</h1>'); }

  const rapport = REPORT_NAMES[order.reportType] || { nl: order.reportType };
  const date = new Date(order.ts).toLocaleString('nl-BE');

  res.send(`<!DOCTYPE html><html lang="nl"><head><meta charset="UTF-8">
  <title>Rapport genereren — Het Stille Pad</title>
  <style>
    body { font-family: Georgia, serif; max-width: 560px; margin: 60px auto; padding: 0 24px; color: #2a2a35; }
    h1 { font-size: 1.6rem; font-weight: 400; margin-bottom: 6px; }
    .meta { color: #888; font-size: 0.85rem; font-family: monospace; margin-bottom: 28px; }
    .card { border: 1px solid #e5dfd0; border-radius: 6px; padding: 20px 24px; background: #faf8f4; margin-bottom: 24px; }
    .row { display: flex; justify-content: space-between; font-size: 0.9rem; padding: 5px 0; border-bottom: 1px solid #ede8df; }
    .row:last-child { border: 0; }
    .label { color: #888; }
    form { margin-top: 0; }
    button { background: #b8884a; color: white; border: 0; padding: 16px 32px; font-size: 1rem;
             border-radius: 4px; cursor: pointer; width: 100%; font-family: Georgia, serif; }
    button:hover { background: #9a7040; }
    .warn { font-size: 0.8rem; color: #aaa; margin-top: 12px; text-align: center; }
  </style></head><body>
  <h1>Rapport genereren</h1>
  <div class="meta">Bestelling ontvangen: ${date}</div>
  <div class="card">
    <div class="row"><span class="label">Naam</span><span>${order.birth.name}</span></div>
    <div class="row"><span class="label">Geboren</span><span>${order.birth.day}.${order.birth.month}.${order.birth.year}${order.birth.hasExactTime ? ` om ${String(order.birth.hour).padStart(2,'0')}:${String(order.birth.minute||0).padStart(2,'0')}` : ''}</span></div>
    <div class="row"><span class="label">Plaats</span><span>${order.birth.place || '—'}</span></div>
    <div class="row"><span class="label">Rapport</span><span>${rapport.nl}</span></div>
    <div class="row"><span class="label">E-mail klant</span><span>${order.customerEmail}</span></div>
  </div>
  <form method="POST" action="/admin/generate">
    <input type="hidden" name="d" value="${d}">
    <input type="hidden" name="t" value="${t}">
    <button type="submit">✦ Genereer & verstuur rapport →</button>
  </form>
  <p class="warn">Het rapport wordt gegenereerd door Claude en direct verstuurd naar ${order.customerEmail}.<br>Dit duurt 30–60 seconden.</p>
  </body></html>`);
});

// POST /admin/generate — genereert het rapport en stuurt het op
app.post('/admin/generate', express.urlencoded({ extended: true }), async (req, res) => {
  const { d, t } = req.body;
  if (!d || t !== ADMIN_TOKEN) return res.status(403).send('<h1>Toegang geweigerd</h1>');

  let order;
  try { order = JSON.parse(Buffer.from(d, 'base64url').toString()); }
  catch { return res.status(400).send('<h1>Ongeldige data</h1>'); }

  const { birth, systems, reportType, customerEmail } = order;
  const rapport = REPORT_NAMES[reportType] || { nl: reportType };

  res.write(`<!DOCTYPE html><html lang="nl"><head><meta charset="UTF-8"><title>Genereren…</title>
  <style>body{font-family:Georgia,serif;max-width:480px;margin:80px auto;text-align:center;color:#2a2a35}
  h2{font-weight:400;font-size:1.4rem}p{color:#888;font-size:0.9rem}</style></head><body>
  <h2>⏳ Rapport wordt gegenereerd…</h2>
  <p>Claude schrijft het rapport voor ${birth.name}.<br>Dit duurt 30–60 seconden. Laat dit venster open.</p></body></html>`);

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
        fullReport += chunk.delta.text;
      }
    }

    await resend.emails.send({
      from: FROM_EMAIL, to: customerEmail,
      subject: `Jouw ${rapport.nl} — Het Stille Pad`,
      html: buildReportEmail(birth.name, rapport.nl, fullReport),
    });

    res.write(`<script>document.body.innerHTML='<h2>✓ Verstuurd!</h2><p>Rapport bezorgd aan ${customerEmail}.</p>'</script>`);
    res.end();

  } catch (err) {
    console.error('Generate error:', err.message);
    res.write(`<script>document.body.innerHTML='<h2>❌ Fout</h2><p>${err.message}</p>'</script>`);
    res.end();
  }
});

// ─── E-mail templates ─────────────────────────────────────────────────────────

function buildAdminEmail(birth, rapport, email, magicLink) {
  const time = birth.hasExactTime ? ` om ${String(birth.hour).padStart(2,'0')}:${String(birth.minute||0).padStart(2,'0')}` : '';
  return `<!DOCTYPE html><html><body style="font-family:Georgia,serif;max-width:560px;margin:0 auto;padding:24px;color:#2a2a35">
  <h2 style="font-weight:400;color:#b8884a">🌙 Nieuwe bestelling — Het Stille Pad</h2>
  <table style="width:100%;border-collapse:collapse;margin:20px 0">
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888;width:120px">Naam</td><td style="padding:8px 0;border-bottom:1px solid #ede8df"><strong>${birth.name}</strong></td></tr>
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888">Geboren</td><td style="padding:8px 0;border-bottom:1px solid #ede8df">${birth.day}.${birth.month}.${birth.year}${time}</td></tr>
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888">Plaats</td><td style="padding:8px 0;border-bottom:1px solid #ede8df">${birth.place || '—'}</td></tr>
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888">Rapport</td><td style="padding:8px 0;border-bottom:1px solid #ede8df">${rapport.nl} (${rapport.prijs})</td></tr>
    <tr><td style="padding:8px 0;color:#888">E-mail</td><td style="padding:8px 0">${email}</td></tr>
  </table>
  <a href="${magicLink}" style="display:inline-block;background:#b8884a;color:white;text-decoration:none;padding:16px 32px;border-radius:4px;font-size:1rem;margin-top:8px">
    ✦ Genereer & verstuur rapport →
  </a>
  <p style="color:#aaa;font-size:0.8rem;margin-top:20px">Klik alleen als je de betaling hebt geverifieerd in Gumroad.</p>
  </body></html>`;
}

function buildConfirmEmail(name, rapportNaam) {
  return `<!DOCTYPE html><html><body style="font-family:Georgia,serif;max-width:560px;margin:0 auto;padding:40px 24px;color:#2a2a35">
  <p style="font-family:monospace;font-size:0.7rem;letter-spacing:0.2em;text-transform:uppercase;color:#b8884a">— Het Stille Pad</p>
  <h1 style="font-weight:400;font-size:1.8rem;line-height:1.2">Bedankt, ${name}.</h1>
  <p style="font-size:1rem;color:#666;line-height:1.7">Je bestelling voor het <strong>${rapportNaam}</strong> is ontvangen en wordt persoonlijk voorbereid.</p>
  <p style="font-size:1rem;color:#666;line-height:1.7">Je ontvangt je rapport <strong>binnen 24 uur</strong> op dit e-mailadres. Neem gerust contact op als je vragen hebt.</p>
  <hr style="border:0;border-top:1px solid #ede8df;margin:32px 0">
  <p style="font-size:0.82rem;color:#aaa">Het Stille Pad · Kosmische zelfkennis</p>
  </body></html>`;
}

function buildReportEmail(name, rapportNaam, reportHTML) {
  return `<!DOCTYPE html><html><head><meta charset="UTF-8">
  <style>
    body { font-family: Georgia, serif; max-width: 720px; margin: 0 auto; padding: 40px 32px; color: #2a2a35; line-height: 1.75; }
    h1, h2, h3, h4 { font-weight: 400; line-height: 1.2; }
    .report-cover { text-align: center; padding: 48px 0; border-bottom: 1px solid #e5dfd0; margin-bottom: 48px; }
    .report-label { font-family: monospace; font-size: 0.65rem; letter-spacing: 0.22em; text-transform: uppercase; color: #b8884a; }
    .report-name { font-size: 2.4rem; margin: 16px 0 10px; }
    .report-date { font-family: monospace; font-size: 0.72rem; color: #aaa; text-transform: uppercase; letter-spacing: 0.1em; }
    .report-section { margin-bottom: 56px; padding-bottom: 40px; border-bottom: 1px solid #e5dfd0; }
    .section-number { font-family: monospace; font-size: 0.62rem; letter-spacing: 0.2em; color: #b8884a; text-transform: uppercase; margin-bottom: 10px; }
    .section-body h3 { font-size: 1.2rem; color: #2a2a35; border-bottom: 1px solid #e5dfd0; padding-bottom: 8px; margin: 32px 0 14px; }
    .section-body h4 { font-size: 1rem; margin: 0 0 8px; }
    .section-body p { color: #555; margin: 0 0 16px; }
    .insight { border-left: 3px solid #b8884a; background: #fdf8f0; padding: 14px 18px; margin: 20px 0; border-radius: 0 4px 4px 0; }
    .action-item { border: 1px solid #e5dfd0; border-radius: 4px; padding: 16px 18px; margin: 12px 0; background: #faf8f4; }
    .action-item h4 { color: #b8884a; font-size: 0.95rem; margin-bottom: 6px; }
    .week-block { border-left: 3px solid #5a6a8a; background: #f4f5f8; padding: 16px 18px; margin: 14px 0; border-radius: 0 4px 4px 0; }
    .week-block h4 { color: #5a6a8a; margin-bottom: 8px; }
    .report-closing { margin-top: 40px; padding-top: 28px; border-top: 1px solid #e5dfd0; font-style: italic; color: #888; }
    @media print { .no-print { display: none; } }
  </style></head><body>
  ${reportHTML}
  <div style="margin-top:48px;padding-top:24px;border-top:1px solid #e5dfd0;text-align:center">
    <p style="font-family:monospace;font-size:0.7rem;letter-spacing:0.15em;text-transform:uppercase;color:#aaa">
      Het Stille Pad · Persoonlijk Rapport voor ${name}
    </p>
    <p style="font-size:0.8rem;color:#ccc">Je kunt dit rapport afdrukken als PDF via Ctrl+P (Windows) of Cmd+P (Mac).</p>
  </div>
  </body></html>`;
}

// ─── Health ────────────────────────────────────────────────────────────────────

app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Stille Pad backend draait op poort ${PORT}`));
