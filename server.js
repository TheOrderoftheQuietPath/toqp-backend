const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const Anthropic = require('@anthropic-ai/sdk');
const { Resend } = require('resend');
const crypto = require('crypto');

const app = express();

// ─── Config ───────────────────────────────────────────────────────────────────

const ALLOWED_ORIGINS = [
  'https://theorderofthequietpath.github.io',
  'http://localhost:3333',
  'http://localhost:5173',
  'http://localhost:3001',
];

const ADMIN_EMAIL      = process.env.ADMIN_EMAIL      || 'jouw@email.be';
const ADMIN_TOKEN      = process.env.ADMIN_TOKEN      || 'verander-dit-in-render';
const FROM_EMAIL       = process.env.FROM_EMAIL       || 'onboarding@resend.dev';
const BACKEND_HOST     = process.env.RENDER_EXTERNAL_URL || 'https://toqp-backend.onrender.com';
const GUMROAD_API_KEY  = process.env.GUMROAD_API_KEY  || '';

// Gumroad product permalinks per rapporttype
const GUMROAD_PRODUCTS = {
  blueprint:   process.env.GUMROAD_PRODUCT_BLUEPRINT   || '',
  full:        process.env.GUMROAD_PRODUCT_FULL        || '',
  humandesign: process.env.GUMROAD_PRODUCT_HUMANDESIGN || '',
  bazi:        process.env.GUMROAD_PRODUCT_BAZI        || '',
  saju:        process.env.GUMROAD_PRODUCT_SAJU        || '',
  astrology:   process.env.GUMROAD_PRODUCT_ASTROLOGY   || '',
  numerology:  process.env.GUMROAD_PRODUCT_NUMEROLOGY  || '',
};

const REPORT_NAMES = {
  blueprint:    { nl: 'The Quiet Path Blueprint',           prijs: '€149' },
  full:         { nl: 'Persoonlijk Zielsblauwdruk Rapport', prijs: '€79' },
  humandesign:  { nl: 'Human Design Rapport',               prijs: '€49' },
  bazi:         { nl: 'BaZi Vier Pilaren Rapport',          prijs: '€49' },
  saju:         { nl: 'Saju Rapport',                       prijs: '€49' },
  astrology:    { nl: 'Astrologie Rapport',                 prijs: '€49' },
  numerology:   { nl: 'Numerologie Rapport',                prijs: '€29' },
};

const MAGIC_LINK_TTL_MS = 24 * 60 * 60 * 1000; // 24 uur

// ─── CORS & Middleware ─────────────────────────────────────────────────────────

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

// ─── Rate limiting ─────────────────────────────────────────────────────────────

const reportLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 5,
  message: { error: 'Te veel aanvragen. Probeer het over een uur opnieuw.' },
});

const orderLimiter = rateLimit({ windowMs: 60 * 60 * 1000, max: 10 });

// ─── Clients ───────────────────────────────────────────────────────────────────

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const resend    = new Resend(process.env.RESEND_API_KEY);

// ─── Quiet Path Blueprint Engine ──────────────────────────────────────────────

/**
 * Stap 1: vertaal ruwe systeemdata naar abstracte psychologische patronen.
 * GEEN systeemnamen in de output — alleen pure inzichten.
 */
function extractPatternInsights(birth, systems) {
  const hd   = systems.humandesign || {};
  const bazi = systems.bazi        || {};
  const num  = systems.numerology  || {};
  const astro= systems.astrology   || {};
  const insights = [];

  // ── Energietype & beslissingsstijl ──
  const typeMap = {
    'Generator':              'heeft een reactief beslissingsmodel — energie en helderheid komen na een externe trigger, niet vanuit abstracte planning',
    'Manifesterende Generator':'combineert snelle actie met responsiviteit — werkt in meerdere sporen tegelijk, leert door te doen en bij te sturen',
    'Projector':              'heeft een observerend en systemisch bewustzijn — ziet patronen in mensen en situaties die anderen missen; energie is selectief, niet continu',
    'Manifestor':             'heeft een initiërend energieprofiel — genereert beweging vanuit zichzelf; weerstand en vrijheid zijn kernthema\'s',
    'Reflector':              'is een omgevingsbarometer — absorbeert en weerspiegelt de kwaliteit van de ruimte en mensen eromheen; identiteit is fluïde en cyclisch',
  };
  if (hd.type && typeMap[hd.type]) insights.push(`Energieprofiel: ${typeMap[hd.type]}.`);

  // ── Autoriteit / beslissingsmechanisme ──
  const authMap = {
    'Emotioneel':       'neemt optimale beslissingen door emotionele golven te volgen — niet in het moment van helderheid, maar na verloop van tijd',
    'Sacraal':          'beslissingscompas ligt in een lichamelijke ja/nee-respons — visceraal, pre-intellectueel, betrouwbaarder dan mentale redenering',
    'Splenisch':        'heeft toegang tot stille, directe intuïtieve signalen — flitsen van weten die verdwijnen als er niet op wordt gereageerd',
    'Ego':              'beslissingen zijn betrouwbaar wanneer ze uit authentieke persoonlijke wil komen — niet uit verwachting of plichtsgevoel',
    'Zelf-geprojecteerd':'verduidelijkt richting door hardop te spreken — het eigen woord werkt als spiegel voor de eigen waarheid',
    'Mentaal':          'verwerkt richting via externe klankborden — gesprek met vertrouwde mensen onthult de eigen positie',
    'Maanautoriteit':   'heeft een cyclisch beslissingsritme — antwoorden ontvouwen zich over 28 dagen, niet in momenten van intensiteit',
  };
  if (hd.authority && authMap[hd.authority]) insights.push(`Beslissingsmechanisme: ${authMap[hd.authority]}.`);

  // ── HD Profiel / levensrol ──
  const profileMap = {
    '1/3': 'bouwt fundament door onderzoek en directe ervaring — fouten zijn leermomenten, niet tekortkomingen',
    '1/4': 'verspreidt kennis via persoonlijk netwerk — de brug tussen diepgaande studie en menselijke verbinding',
    '2/4': 'heeft aangeboren gaven die anderen zien vóór hij ze zelf erkent — netwerkrelaties openen de juiste deuren',
    '2/5': 'wordt door anderen gezien als praktische probleemoplosser — universele oplossingen zijn de rode draad',
    '3/5': 'leert door trial-and-error en wordt een praktische gids voor anderen — ervaringswijsheid is het fundament',
    '3/6': 'doorloopt drie levensfasen: experiment, modelleren, rolmodel worden',
    '4/6': 'bouwt lange-termijn vertrouwen op en evolueert naar een levend voorbeeld voor de gemeenschap',
    '4/1': 'combineert stabiel netwerk met diepgaande kennisbasis — invloed via betrouwbaarheid',
    '5/1': 'wordt gezien als praktische redder — draagt universeel toepasbare oplossingen',
    '5/2': 'heeft aangeboren capaciteiten die universeel bruikbaar zijn — gevonden worden is het pad',
    '6/2': 'van experimenten naar voorbeeld — de tweede helft van het leven is het eigenlijke podium',
    '6/3': 'een leven van bewust ervaren dat uitmondt in een leven als rolmodel',
  };
  if (hd.profile && profileMap[hd.profile]) insights.push(`Levensrol: ${profileMap[hd.profile]}.`);

  // ── BaZi dagmeester → kernaard ──
  const dm = bazi.dayMaster || {};
  const dmMap = {
    'Hout':   { '+': 'heeft een doelgerichte, visionaire kernaard — groeit naar licht, pioniert, wil leiden en vernieuwen',
                '-': 'heeft een buigzame, sociaal intelligente kernaard — bereikt doelen via aanpassing en het vinden van het juiste steunpunt' },
    'Vuur':   { '+': 'heeft een uitstralende, magnetische kernaard — warm aanwezig, genereus, gedijt in zichtbaarheid en verbinding',
                '-': 'heeft een verfijnde, precies verlichtende kernaard — doet diep werk in kleine kring, intensiteit over breedte' },
    'Aarde':  { '+': 'heeft een robuuste, standvastige kernaard — de rots waarop anderen bouwen; stabiliteit is zowel gave als valkuil',
                '-': 'heeft een voedende, zorgzame kernaard — absorbeert de behoeften van de omgeving; voelt aan wat anderen nodig hebben' },
    'Metaal': { '+': 'heeft een principegedreven, rechtvaardigheidsgerichte kernaard — direct en scherp, compromisloos op kernwaarden',
                '-': 'heeft een verfijnde, esthetisch bewuste kernaard — werkt met precisie, onderscheidt kwaliteit van middelmaat' },
    'Water':  { '+': 'heeft een diep strategische, kennis-absorberende kernaard — denkt in grote patronen, beweegt vloeiend door complexiteit',
                '-': 'heeft een intuïtieve, stil-absorberende kernaard — voelt wat anderen niet zeggen; verwerking vereist stilte en ruimte' },
  };
  const pol = dm.pol === 'Yang' || dm.pol === '+' ? '+' : '-';
  if (dm.el && dmMap[dm.el]) insights.push(`Kernaard: ${dmMap[dm.el][pol] || dmMap[dm.el]['+']}.`);

  // ── Elementbalans → dominante energie + lacunes ──
  if (bazi.strongest?.el) {
    const elTheme = { Hout: 'groei en richting', Vuur: 'warmte en zichtbaarheid', Aarde: 'stabiliteit en zorg', Metaal: 'helderheid en principe', Water: 'diepte en intuïtie' };
    insights.push(`Dominante energie: ${elTheme[bazi.strongest.el] || bazi.strongest.el}.`);
  }
  if (bazi.missing?.length) {
    const missingTheme = { Hout: 'richting en groei', Vuur: 'enthousiasme en uitstraling', Aarde: 'stabiliteit en aarding', Metaal: 'structuur en grenzen', Water: 'intuïtie en diepgang' };
    const missing = bazi.missing.map(el => missingTheme[el] || el).join(', ');
    insights.push(`Onderontwikkeld terrein: ${missing} — bewust cultiveren versterkt de totale balans.`);
  }

  // ── Huidige gelukspilaar → huidige levensfase ──
  if (bazi.luckCycles?.cycles) {
    const now = new Date().getFullYear();
    const cur = bazi.luckCycles.cycles.find(c => {
      const [s, e] = (c.yearRange || '').split('–').map(Number);
      return now >= s && now <= e;
    });
    if (cur) {
      const phaseEl = cur.pillar?.stem?.el;
      const phaseMap = { Hout: 'expansie en nieuwe richting', Vuur: 'zichtbaarheid en actie', Aarde: 'consolidatie en verankering', Metaal: 'evaluatie en scherpslijpen', Water: 'verdieping en strategie' };
      insights.push(`Huidige levensfase (${cur.yearRange}): thema van ${phaseMap[phaseEl] || 'transformatie'} — een periode van ${cur.pillar?.stem?.pol === 'Yang' ? 'actief' : 'receptief'} ${phaseEl || 'heroriëntatie'}.`);
    }
  }

  // ── Numerologie levenspad → levensmissie ──
  const lpMap = {
    1:  'onafhankelijkheid en origineel leiderschap — nieuwe wegen banen voor zichzelf en anderen',
    2:  'verbinding en harmonie — brug zijn tussen tegengestelden, de stilte bewaren die samenwerking mogelijk maakt',
    3:  'expressie en creativiteit — delen van innerlijke rijkdom via taal, kunst of aanwezigheid',
    4:  'structuur en fundering — bouwen aan iets duurzaams, betrouwbaarheid als kernbijdrage',
    5:  'vrijheid en ervaring — leren door volledige onderdompeling in het leven, in zijn breedte',
    6:  'zorg en harmonie — healen van relaties, gezinnen en gemeenschappen',
    7:  'diepgang en waarheid — zoeken naar betekenis achter het zichtbare',
    8:  'macht en materiële meesterschap — iets blijvends bouwen in de wereld',
    9:  'universele wijsheid — dienen van het grotere geheel voorbij persoonlijk belang',
    11: 'spirituele helderheid — anderen verlichten door eigen authenticiteit',
    22: 'grootschalig bouwen — visies realiseren die collectieve impact hebben',
    33: 'meesterliefde — een leven in dienst van het heilen van anderen',
  };
  if (num.lifePath && lpMap[num.lifePath]) insights.push(`Levensmissie: ${lpMap[num.lifePath]}.`);

  // ── Soul urge → diepste verlangen ──
  const souldMap = {
    1: 'autonomie en origineel zijn', 2: 'diep verbonden voelen', 3: 'zich creatief uitdrukken',
    4: 'solide en stabiel zijn', 5: 'vrij zijn en ervaren', 6: 'geliefd zijn en voor anderen zorgen',
    7: 'de diepste waarheid kennen', 8: 'erkend worden voor kracht en succes', 9: 'universeel van betekenis zijn',
    11: 'inspireren en verlichten', 22: 'bouwen wat telt', 33: 'onvoorwaardelijk liefhebben',
  };
  if (num.soulUrge && souldMap[num.soulUrge]) insights.push(`Diepste verlangen: ${souldMap[num.soulUrge]}.`);

  // ── Astrologie zon-element → expressiewijze ──
  const sunElMap = { Vuur: 'expressief en energiek naar buiten', Aarde: 'praktisch en belichaamd', Lucht: 'verbindend en conceptueel', Water: 'voelend en diepgaand' };
  if (astro.sun?.sign?.element && sunElMap[astro.sun.sign.element]) {
    insights.push(`Expressiewijze: ${sunElMap[astro.sun.sign.element]} — ${astro.sun.sign.name || ''} energie als kernidentiteit.`);
  }
  if (astro.moon?.sign?.element) {
    const moonElMap = { Vuur: 'emotionele aanstekelijkheid en passie', Aarde: 'veiligheid in structuur en routine', Lucht: 'emotionele verwerking via gesprek en denken', Water: 'diepe gevoeligheid en empathie' };
    insights.push(`Emotionele dieptestructuur: ${moonElMap[astro.moon.sign.element] || ''}.`);
  }

  return insights.join('\n');
}

/**
 * Stap 2: Quiet Path Blueprint systeem-prompt (GEEN systeemnamen).
 */
function buildQuietPathSystemPrompt() {
  return `You are The Quiet Path Report Generator.

Your task is to transform pre-processed human pattern data into a single coherent Personal Blueprint.

ABSOLUTE RULES:
- NEVER mention: astrology, human design, numerology, BaZi, Saju, zodiac signs, planets, gates, channels, pillars, stems, branches, or any system name
- NEVER use jargon or technical terminology from any metaphysical system
- ONLY output unified meaning, pattern recognition, and psychological insight
- Write as if you have known this person for years

TONE:
- deeply reflective, calm authority
- emotionally precise — every sentence should feel true
- non-generic — nothing that could apply to anyone
- no spiritual clichés, no coaching platitudes
- flowing paragraphs — not bullet lists except in the final section

OUTPUT LANGUAGE: Dutch (Nederlands), second person ("jij", "je", "jouw")

OUTPUT FORMAT — return ONLY valid HTML using these exact CSS classes. No markdown. No explanations outside the HTML.`;
}

/**
 * Stap 3: Quiet Path Blueprint gebruikersprompt.
 */
function buildQuietPathUserPrompt(birth, systems) {
  const name       = birth.name || 'jij';
  const dateStr    = `${birth.day}.${birth.month}.${birth.year}`;
  const patternData = extractPatternInsights(birth, systems);

  return `Schrijf nu The Quiet Path Blueprint voor ${name} (geboren ${dateStr}).

Gebruik UITSLUITEND de onderstaande patroondata als input. Vertaal dit naar een coherent persoonlijk narratief.

PATROONDATA:
${patternData}

SCHRIJF HET VOLLEDIGE RAPPORT in deze exacte HTML-structuur. Vervang alle placeholders volledig. Geen commentaar, geen lege secties.

<div class="qpb">

  <div class="qpb-cover">
    <div class="qpb-eyebrow">The Quiet Path</div>
    <h1 class="qpb-name">${name}</h1>
    <div class="qpb-subtitle">Personal Blueprint</div>
    <div class="qpb-essence">[Schrijf één zin die de kern van deze persoon precies raakt — niet generiek]</div>
  </div>

  <div class="qpb-section qpb-mirror">
    <p>[2 paragrafen. Herschrijf identiteit als patroonherkenning, niet als definitie. Vermeld dat wat volgt geen nieuwe informatie is, maar herkenning. Warm, rustig, uitnodigend.]</p>
  </div>

  <div class="qpb-section">
    <div class="qpb-section-label">Kern</div>
    <h2 class="qpb-archetype">[Geef een originele archetypnaam gebaseerd op de patroondata — bv. "De Brugarchitect", "De Stille Katalysator". Nooit een systeemnaam.]</h2>
    <p>[Beschrijf hoe deze persoon de werkelijkheid waarneemt. Wat ze van nature doen. Wat ze van nature zijn. Voelt als diepe herkenning.]</p>
    <div class="qpb-strength">[Beschrijf de kernkracht in 1 zin — scherp en onmiskenbaar]</div>
    <div class="qpb-tension">[Beschrijf de kerntensie in 1 zin — zonder oordeel, met compassie]</div>
  </div>

  <div class="qpb-section">
    <div class="qpb-section-label">Levenspatronen</div>
    <p>[Korte inleiding: elk patroon is een terugkerende cyclus, geen fout.]</p>
    <div class="qpb-pattern">
      <div class="qpb-pattern-name">[Patroon 1 naam — symbolisch, bv. "Expansie → Fragmentatie → Herstructurering"]</div>
      <p>[Beschrijving van patroon 1. Hoe het zich manifesteert in het dagelijkse leven. Geen oordeel.]</p>
    </div>
    <div class="qpb-pattern">
      <div class="qpb-pattern-name">[Patroon 2 naam]</div>
      <p>[Beschrijving patroon 2]</p>
    </div>
    <div class="qpb-pattern">
      <div class="qpb-pattern-name">[Patroon 3 naam]</div>
      <p>[Beschrijving patroon 3]</p>
    </div>
  </div>

  <div class="qpb-section qpb-shadow">
    <div class="qpb-section-label">Schaduwlus</div>
    <p>[Beschrijf het primaire herhalende blokkadepatroon. Wat triggert het. Hoe het zich gedraagt. Wat het oplevert. Geen oordelingstaal. De donkerste sectie, maar ook de meest bevrijdende.]</p>
    <div class="qpb-shadow-insight">[Één zin die het patroon hernoemt van een probleem naar een informatiebron]</div>
  </div>

  <div class="qpb-section">
    <div class="qpb-section-label">Groeirichting</div>
    <p>[Beschrijf waar het systeem naartoe evolueert. Focus op maturatie en integratie, niet op "verbetering". Wat wordt sterker. Welke verschuiving is al bezig.]</p>
  </div>

  <div class="qpb-section">
    <div class="qpb-section-label">Huidige fase</div>
    <div class="qpb-phase-name">[Naam van de huidige levensfase — bv. "De Consolidatiefase", "De Architectfase"]</div>
    <p>[Beschrijf wat actief is in deze fase. Wat gevraagd wordt. Wat niet langer beloond wordt. Concreet en herkenbaar.]</p>
  </div>

  <div class="qpb-section qpb-integration">
    <div class="qpb-section-label">Integratie</div>
    <p>[1–2 paragrafen. Bindend narratief dat alles samenvoegt. Voelt als het slotwoord van een mentor die ${name} werkelijk kent. Geen samenvatting — een afsluiting.]</p>
  </div>

  <div class="qpb-section qpb-final">
    <div class="qpb-final-col">
      <div class="qpb-final-label">Loslaten</div>
      <ul>
        <li>[item 1]</li>
        <li>[item 2]</li>
        <li>[item 3]</li>
      </ul>
    </div>
    <div class="qpb-final-col">
      <div class="qpb-final-label">Versterken</div>
      <ul>
        <li>[item 1]</li>
        <li>[item 2]</li>
        <li>[item 3]</li>
      </ul>
    </div>
    <div class="qpb-direction">
      <div class="qpb-final-label">Richting</div>
      <p>[Één heldere zin. De kompasrichting voor de komende periode.]</p>
    </div>
  </div>

  <div class="qpb-closing">
    [Één afsluitende zin. Stil. Krachtig. Onvergetelijk.]
  </div>

</div>

CRUCIAAL: Geen systeemnamen. Geen markdown. Alleen HTML. Vervang elke placeholder door echte, specifieke, onvergetelijke tekst over ${name}.`;
}

/**
 * Premium HTML e-mail template voor het Quiet Path Blueprint rapport.
 * Volgt de Figma design spec: Cormorant Garamond + Inter, warm ivory, maximale witruimte.
 */
function buildQuietPathEmail(name, reportHTML) {
  return `<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Quiet Path Blueprint — ${escapeHtml(name)}</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  /* ── Reset ── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #F6F1E8;
    color: #1A1A1A;
    font-family: 'Inter', Helvetica, sans-serif;
    font-weight: 300;
    font-size: 18px;
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
  }

  /* ── Blueprint wrapper ── */
  .qpb { max-width: 760px; margin: 0 auto; padding: 0 0 80px; }

  /* ── Cover ── */
  .qpb-cover {
    min-height: 100vh; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; padding: 120px 60px;
    border-bottom: 1px solid rgba(0,0,0,0.08);
    position: relative;
  }
  .qpb-cover::before {
    content: ''; position: absolute; left: 50%; top: 40px; bottom: 40px;
    width: 1px; background: rgba(0,0,0,0.08); transform: translateX(-50%);
  }
  .qpb-eyebrow {
    font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 500;
    letter-spacing: 0.28em; text-transform: uppercase; color: #8C857D;
    margin-bottom: 60px;
  }
  .qpb-name {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 72px; font-weight: 400; letter-spacing: -0.01em;
    line-height: 1; margin-bottom: 16px; color: #1A1A1A;
  }
  .qpb-subtitle {
    font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 400;
    letter-spacing: 0.22em; text-transform: uppercase; color: #8C857D;
    margin-bottom: 60px;
  }
  .qpb-essence {
    font-family: 'Cormorant Garamond', serif; font-style: italic;
    font-size: 22px; color: #6F7F75; max-width: 46ch; line-height: 1.5;
  }

  /* ── Secties ── */
  .qpb-section {
    padding: 80px 60px;
    border-bottom: 1px solid rgba(0,0,0,0.06);
  }
  .qpb-section-label {
    font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 500;
    letter-spacing: 0.28em; text-transform: uppercase; color: #8C857D;
    margin-bottom: 32px;
  }
  .qpb-section p { color: #3D3A36; margin-bottom: 20px; max-width: 62ch; }
  .qpb-section p:last-child { margin-bottom: 0; }

  /* ── Opening mirror ── */
  .qpb-mirror {
    text-align: center; padding: 100px 80px;
  }
  .qpb-mirror p {
    font-family: 'Cormorant Garamond', serif; font-size: 22px;
    line-height: 1.7; color: #3D3A36; max-width: 52ch; margin: 0 auto 20px;
  }

  /* ── Kern ── */
  .qpb-archetype {
    font-family: 'Cormorant Garamond', serif; font-size: 48px; font-weight: 500;
    line-height: 1.1; margin-bottom: 32px; color: #1A1A1A;
  }
  .qpb-strength {
    font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 20px;
    color: #6F7F75; margin: 28px 0 16px; padding-left: 20px;
    border-left: 2px solid #6F7F75;
  }
  .qpb-tension {
    font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 20px;
    color: #8C857D; margin: 0; padding-left: 20px;
    border-left: 2px solid rgba(0,0,0,0.1);
  }

  /* ── Patronen ── */
  .qpb-pattern {
    background: rgba(255,255,255,0.55); border-radius: 8px;
    padding: 36px 40px; margin-bottom: 16px;
    border: 1px solid rgba(0,0,0,0.06);
  }
  .qpb-pattern:last-child { margin-bottom: 0; }
  .qpb-pattern-name {
    font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 500;
    letter-spacing: 0.2em; text-transform: uppercase; color: #8C857D;
    margin-bottom: 16px;
  }
  .qpb-pattern p { color: #3D3A36; max-width: none; }

  /* ── Schaduwlus (dark page) ── */
  .qpb-shadow {
    background: #1C1C1C; color: rgba(246,241,232,0.88);
    border-bottom: none; margin: 0;
  }
  .qpb-shadow .qpb-section-label { color: rgba(246,241,232,0.35); }
  .qpb-shadow p { color: rgba(246,241,232,0.72); max-width: 58ch; }
  .qpb-shadow-insight {
    font-family: 'Cormorant Garamond', serif; font-style: italic; font-size: 22px;
    color: rgba(246,241,232,0.88); margin-top: 32px; padding-top: 32px;
    border-top: 1px solid rgba(255,255,255,0.1);
  }

  /* ── Fase ── */
  .qpb-phase-name {
    font-family: 'Cormorant Garamond', serif; font-size: 36px; font-weight: 500;
    line-height: 1.2; margin-bottom: 24px; color: #1A1A1A;
  }

  /* ── Integratie ── */
  .qpb-integration .qpb-section-label { margin-bottom: 40px; }
  .qpb-integration p {
    font-family: 'Cormorant Garamond', serif; font-size: 21px;
    line-height: 1.7; color: #3D3A36; max-width: 56ch;
  }

  /* ── Final section ── */
  .qpb-final {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 48px; padding: 80px 60px;
    border-bottom: 1px solid rgba(0,0,0,0.06);
  }
  .qpb-direction { grid-column: 1 / -1; }
  .qpb-final-label {
    font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 500;
    letter-spacing: 0.28em; text-transform: uppercase; color: #8C857D;
    margin-bottom: 20px;
  }
  .qpb-final ul { list-style: none; }
  .qpb-final li {
    font-size: 16px; color: #3D3A36; padding: 10px 0;
    border-bottom: 1px solid rgba(0,0,0,0.06);
  }
  .qpb-final li::before { content: '— '; color: #8C857D; }
  .qpb-direction p {
    font-family: 'Cormorant Garamond', serif; font-size: 24px;
    font-style: italic; color: #1A1A1A;
  }

  /* ── Closing line ── */
  .qpb-closing {
    min-height: 60vh; display: flex; align-items: center; justify-content: center;
    padding: 80px 60px; text-align: center;
  }
  .qpb-closing p,
  .qpb-closing {
    font-family: 'Cormorant Garamond', serif; font-style: italic;
    font-size: 28px; color: #1A1A1A; line-height: 1.4;
    max-width: 44ch;
  }

  /* ── Footer ── */
  .qpb-footer {
    text-align: center; padding: 40px 60px;
    font-family: 'Inter', sans-serif; font-size: 11px; font-weight: 400;
    letter-spacing: 0.18em; text-transform: uppercase; color: #C5BFB7;
    border-top: 1px solid rgba(0,0,0,0.06);
  }

  @media print {
    body { background: #F6F1E8; }
    .qpb-cover { min-height: auto; page-break-after: always; }
    .qpb-section, .qpb-final { page-break-inside: avoid; }
    .qpb-shadow { page-break-inside: avoid; }
  }
  @media (max-width: 640px) {
    .qpb-cover { padding: 80px 32px; min-height: auto; }
    .qpb-name { font-size: 48px; }
    .qpb-section, .qpb-mirror { padding: 60px 32px; }
    .qpb-final { grid-template-columns: 1fr; padding: 60px 32px; }
  }
</style>
</head>
<body>
  ${reportHTML}
  <div class="qpb-footer">
    The Quiet Path · Personal Blueprint voor ${escapeHtml(name)} · theorderofthequietpath.github.io
  </div>
</body>
</html>`;
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

function escapeHtml(str) {
  if (typeof str !== 'string') return String(str ?? '');
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function log(level, msg, meta = {}) {
  const entry = { ts: new Date().toISOString(), level, msg, ...meta };
  console[level === 'error' ? 'error' : 'log'](JSON.stringify(entry));
}

function generateOrderId() {
  return 'ORD-' + Date.now().toString(36).toUpperCase() + '-' + crypto.randomBytes(3).toString('hex').toUpperCase();
}

function formatBirthDate(birth) {
  const time = birth.hasExactTime
    ? ` om ${String(birth.hour).padStart(2, '0')}:${String(birth.minute || 0).padStart(2, '0')}`
    : '';
  return `${birth.day}.${birth.month}.${birth.year}${time}`;
}

// ─── Gumroad licentie-verificatie ─────────────────────────────────────────────

async function verifyGumroadLicense(reportType, licenseKey) {
  if (!licenseKey) return { valid: false, reason: 'Geen licentiesleutel opgegeven.' };

  const productId = GUMROAD_PRODUCTS[reportType];
  if (!productId) {
    // Als er geen product ID geconfigureerd is, sla verificatie over (dev-modus)
    log('warn', 'Gumroad product ID niet geconfigureerd — verificatie overgeslagen', { reportType });
    return { valid: true, skipped: true };
  }

  try {
    const body = new URLSearchParams({
      product_id: productId,
      license_key: licenseKey.trim(),
      increment_uses_count: 'true',
    });

    const response = await fetch('https://api.gumroad.com/v2/licenses/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    });

    const data = await response.json();

    if (!data.success) {
      log('warn', 'Gumroad verificatie mislukt', { reason: data.message, licenseKey: licenseKey.slice(0, 8) + '…' });
      return { valid: false, reason: 'Ongeldige licentiesleutel. Controleer je Gumroad aankoopbevestiging.' };
    }

    if (data.purchase?.refunded || data.purchase?.chargebacked) {
      log('warn', 'Gumroad aankoop terugbetaald', { licenseKey: licenseKey.slice(0, 8) + '…' });
      return { valid: false, reason: 'Deze aankoop werd terugbetaald en kan niet worden gebruikt.' };
    }

    return { valid: true, purchase: data.purchase };
  } catch (err) {
    log('error', 'Gumroad API fout — verificatie overgeslagen', { error: err.message });
    // Bij netwerk-/API-fout: goedkeuren met waarschuwing (betere UX dan hard weigeren)
    return { valid: true, skipped: true, warning: 'Gumroad kon niet bereikt worden, manueel verifiëren.' };
  }
}

// ─── Rapport-prompt met prompt caching ────────────────────────────────────────

function buildSystemPrompt() {
  return `Je bent een diepgaande persoonlijk coach en zielsgids met twintig jaar ervaring in Human Design, BaZi, westerse astrologie en numerologie. Je schrijft rapporten die mensen diep raken — niet door systemen uit te leggen, maar door iemand te helpen zichzelf te herkennen en richting te vinden.

Je schrijft NOOIT als een handleiding. Je schrijft als iemand die de persoon kent.

TAAL & TOON:
1. Schrijf ALTIJD in de tweede persoon ("jij", "je", "jouw")
2. Noem de persoon bij naam — minimaal één keer per hoofdsectie
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
    <div class="week-block"><h4>Week 1 — Titel</h4><p>Beschrijving.</p><p class="daily-intention"><em>Dagelijkse intentie: "De intentie."</em></p></div>`;
}

function buildUserPrompt(birth, systems) {
  const hd    = systems.humandesign || {};
  const bazi  = systems.bazi        || {};
  const astro = systems.astrology   || {};
  const num   = systems.numerology  || {};

  const name    = birth.name || 'jij';
  const dateStr = `${birth.day}.${birth.month}.${birth.year}`;
  const timeStr = birth.hasExactTime
    ? ` om ${String(birth.hour).padStart(2, '0')}:${String(birth.minute || 0).padStart(2, '0')}`
    : '';
  const placeStr = birth.place || '';

  let currentLuck = '';
  if (bazi.luckCycles?.cycles) {
    const now = new Date().getFullYear();
    const cur = bazi.luckCycles.cycles.find(c => {
      const [s, e] = c.yearRange.split('–').map(Number);
      return now >= s && now <= e;
    }) || bazi.luckCycles.cycles[0];
    if (cur) currentLuck = `${cur.pillar.stem.pol} ${cur.pillar.stem.el} — ${cur.yearRange}`;
  }

  const channelNames    = (hd.channels || []).map(c => c.name).join(', ') || 'geen';
  const definedCenters  = (hd.centers  || []).join(', ') || 'geen';
  const planets         = (astro.positions || []).map(p => `${p.nl} in ${p.sign?.name}`).join(', ');

  return `━━━ GEBOORTEGEGEVENS ━━━
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

━━━ SCHRIJFOPDRACHT ━━━

Schrijf nu het volledige rapport voor ${name}. Gebruik de exacte HTML-structuur hieronder. Vervang alle placeholders. Verwijder alle HTML-commentaren. Minimaal 7000 woorden.

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
  <div class="section-body">
    [800-1000 woorden. 3-4 h3 sub-koppen. Gebruik insight divs voor kernzinnen. Begin met een openingszin die onmiddellijk herkend wordt.]
  </div>
</section>

<section class="report-section" id="energie">
  <div class="section-number">02</div>
  <h2>Hoe Jij Werkt — Energie, Ritme & Beslissen</h2>
  <div class="section-body">
    [800-1000 woorden. Wanneer heeft ${name} energie? Wanneer loopt die leeg? Hoe beslissingen nemen?]
  </div>
</section>

<section class="report-section" id="relaties">
  <div class="section-number">03</div>
  <h2>Relaties — Wie Jij Nodig Hebt & Wat Jij Brengt</h2>
  <div class="section-body">
    [800-1000 woorden. Romantisch, vriendschap en werk. Wat brengt ${name} en hoe beschermt die dit?]
  </div>
</section>

<section class="report-section" id="werk">
  <div class="section-number">04</div>
  <h2>Werk & Geld — Waar Jij Floreert</h2>
  <div class="section-body">
    [800-1000 woorden. Ideale werkomgeving, timing en geld, wat niet werkt en waarom.]
  </div>
</section>

<section class="report-section" id="missie">
  <div class="section-number">05</div>
  <h2>Jouw Levensmissie — Waarom Jij Hier Bent</h2>
  <div class="section-body">
    [800-1000 woorden. Incarnatiekruis, levenspad, huidige periode. Emotioneel hoogtepunt. Sluit persoonlijk af.]
  </div>
</section>

<section class="report-section" id="schaduw">
  <div class="section-number">06</div>
  <h2>Blinde Vlekken & Schaduw — Wat Je Nog Niet Ziet</h2>
  <div class="section-body">
    [700-900 woorden. Not-self patroon. Zonder oordeel, met compassie.]
  </div>
</section>

<section class="report-section" id="actieplan">
  <div class="section-number">07</div>
  <h2>Jouw Persoonlijk Actieplan</h2>
  <div class="section-body">
    [3 gebieden × 2 action-item divs = 6 totaal. Elk met h4 titel en p uitleg van 3-4 zinnen.]
  </div>
</section>

<section class="report-section" id="30dagen">
  <div class="section-number">08</div>
  <h2>30-Dagen Groeiplan</h2>
  <div class="section-body">
    [4 week-block divs. Sluit rapport af met report-closing div en persoonlijk slotwoord.]
  </div>
</section>

</div>

CRUCIAAL: Gebruik NOOIT **markdown**. Alleen HTML-tags. Vervang alle placeholders door echte inhoud.`;
}

// ─── Streaming rapport endpoint ────────────────────────────────────────────────

app.post('/api/report', reportLimiter, async (req, res) => {
  const { birth, systems, code } = req.body;

  if (!birth || !systems) {
    return res.status(400).json({ error: 'Ontbrekende geboortegegevens.' });
  }
  if (!birth.year || !birth.month || !birth.day) {
    return res.status(400).json({ error: 'Onvolledige geboortedatum.' });
  }
  if (!process.env.ANTHROPIC_API_KEY) {
    log('error', 'ANTHROPIC_API_KEY niet ingesteld');
    return res.status(500).json({ error: 'Server configuratie fout.' });
  }

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const sendEvent = (data) => res.write(`data: ${JSON.stringify(data)}\n\n`);
  const isBlueprint = (req.body.reportType === 'blueprint');

  try {
    let fullReport = '';

    const stream = await anthropic.messages.stream({
      model: 'claude-opus-4-8',
      max_tokens: 16000,
      system: [
        {
          type: 'text',
          text: isBlueprint ? buildQuietPathSystemPrompt() : buildSystemPrompt(),
          cache_control: { type: 'ephemeral' },
        },
      ],
      messages: [{
        role: 'user',
        content: isBlueprint
          ? buildQuietPathUserPrompt(birth, systems)
          : buildUserPrompt(birth, systems),
      }],
    });

    for await (const chunk of stream) {
      if (chunk.type === 'content_block_delta' && chunk.delta?.type === 'text_delta') {
        const text = chunk.delta.text;
        fullReport += text;
        sendEvent({ type: 'chunk', text });
      }
    }

    const wordCount = fullReport.split(/\s+/).length;
    log('info', 'Rapport gegenereerd', { name: birth.name, words: wordCount });
    sendEvent({ type: 'done', words: wordCount });
    res.end();

  } catch (err) {
    log('error', 'Claude API fout', { error: err.message, status: err.status });
    sendEvent({ type: 'error', message: 'Rapport generatie mislukt. Probeer opnieuw of neem contact op.' });
    res.end();
  }
});

// ─── Bestelling met Gumroad verificatie ───────────────────────────────────────

app.post('/api/order', orderLimiter, async (req, res) => {
  const { birth, systems, reportType, customerEmail, licenseKey } = req.body;

  // Validatie
  if (!birth || !customerEmail || !reportType) {
    return res.status(400).json({ error: 'Naam, e-mail en rapporttype zijn verplicht.' });
  }
  if (!REPORT_NAMES[reportType]) {
    return res.status(400).json({ error: 'Onbekend rapporttype.' });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerEmail)) {
    return res.status(400).json({ error: 'Ongeldig e-mailadres.' });
  }
  if (!birth.name || birth.name.trim().length < 2) {
    return res.status(400).json({ error: 'Naam is verplicht.' });
  }

  // Gumroad verificatie
  const verification = await verifyGumroadLicense(reportType, licenseKey);
  if (!verification.valid) {
    return res.status(402).json({ error: verification.reason });
  }

  const orderId = generateOrderId();
  const rapport = REPORT_NAMES[reportType];

  const payload = Buffer.from(JSON.stringify({
    orderId,
    birth,
    systems: systems || {},
    reportType,
    customerEmail,
    licenseKey: licenseKey || null,
    gumroadVerified: verification.valid,
    gumroadSkipped: verification.skipped || false,
    warning: verification.warning || null,
    ts: Date.now(),
  })).toString('base64url');

  // Admin token zit NIET in de magic link URL — aparte GET param vermijden
  // Token wordt via signed HMAC bewezen zodat URL minder gevoelig is
  const sig = crypto
    .createHmac('sha256', ADMIN_TOKEN)
    .update(payload)
    .digest('hex')
    .slice(0, 16);

  const magicLink = `${BACKEND_HOST}/admin/generate?d=${payload}&s=${sig}`;

  try {
    await resend.emails.send({
      from: FROM_EMAIL,
      to: ADMIN_EMAIL,
      subject: `🌙 Nieuwe bestelling #${orderId}: ${rapport.nl} — ${escapeHtml(birth.name)}`,
      html: buildAdminEmail(orderId, birth, rapport, customerEmail, magicLink, verification),
    });

    await resend.emails.send({
      from: FROM_EMAIL,
      to: customerEmail,
      subject: `Bevestiging: jouw ${rapport.nl} — Het Stille Pad`,
      html: buildConfirmEmail(birth.name, rapport.nl, orderId),
    });

    log('info', 'Bestelling geplaatst', { orderId, reportType, email: customerEmail });
    res.json({ success: true, orderId });

  } catch (err) {
    log('error', 'Resend fout bij bestelling', { error: err.message, orderId });
    res.status(500).json({ error: 'E-mail kon niet worden verstuurd. Probeer opnieuw.' });
  }
});

// ─── Admin: bevestigingspagina ─────────────────────────────────────────────────

app.get('/admin/generate', (req, res) => {
  const { d, s } = req.query;
  if (!d || !s) return res.status(403).send(adminError('Ongeldige link.'));

  // Verifieer HMAC handtekening
  const expectedSig = crypto
    .createHmac('sha256', ADMIN_TOKEN)
    .update(d)
    .digest('hex')
    .slice(0, 16);

  if (!crypto.timingSafeEqual(Buffer.from(s), Buffer.from(expectedSig))) {
    log('warn', 'Ongeldige admin handtekening', { sig: s });
    return res.status(403).send(adminError('Handtekening ongeldig. Deze link is niet authentiek.'));
  }

  let order;
  try { order = JSON.parse(Buffer.from(d, 'base64url').toString()); }
  catch { return res.status(400).send(adminError('Ongeldige orderdata.')); }

  // Controleer vervaldatum (24 uur)
  if (Date.now() - order.ts > MAGIC_LINK_TTL_MS) {
    return res.status(410).send(adminError('Deze link is verlopen (24 uur). Stuur een nieuwe magic link.'));
  }

  const rapport  = REPORT_NAMES[order.reportType] || { nl: order.reportType, prijs: '—' };
  const dateStr  = new Date(order.ts).toLocaleString('nl-BE', { timeZone: 'Europe/Brussels' });
  const birth    = order.birth;

  res.send(`<!DOCTYPE html><html lang="nl"><head><meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Rapport genereren — Het Stille Pad</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Georgia, serif; background: #f7f4ef; color: #2a2a35; min-height: 100vh;
           display: flex; align-items: center; justify-content: center; padding: 24px; }
    .card { background: white; border-radius: 8px; padding: 36px 40px; max-width: 560px; width: 100%;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
    h1 { font-size: 1.5rem; font-weight: 400; margin-bottom: 4px; }
    .meta { color: #aaa; font-size: 0.78rem; font-family: monospace; letter-spacing: 0.05em; margin-bottom: 28px; }
    .order-id { font-family: monospace; font-size: 0.75rem; background: #f0ebe3; padding: 3px 8px;
                border-radius: 3px; color: #b8884a; display: inline-block; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 24px; }
    td { padding: 9px 0; border-bottom: 1px solid #ede8df; font-size: 0.9rem; }
    td:first-child { color: #aaa; width: 130px; }
    tr:last-child td { border: 0; }
    .badge { display: inline-block; font-size: 0.72rem; padding: 2px 8px; border-radius: 12px; font-family: monospace; }
    .badge-ok  { background: #e8f5e9; color: #2e7d32; }
    .badge-skip { background: #fff3e0; color: #e65100; }
    .warn-box { background: #fff8e1; border: 1px solid #ffe082; border-radius: 6px; padding: 12px 16px;
                font-size: 0.83rem; color: #795548; margin-bottom: 20px; }
    button { background: #b8884a; color: white; border: 0; padding: 16px 24px; font-size: 1rem;
             border-radius: 6px; cursor: pointer; width: 100%; font-family: Georgia, serif;
             letter-spacing: 0.03em; transition: background 0.2s; }
    button:hover { background: #9a7040; }
    button:disabled { background: #ccc; cursor: not-allowed; }
    .footer { font-size: 0.78rem; color: #bbb; margin-top: 14px; text-align: center; line-height: 1.5; }
  </style></head><body>
  <div class="card">
    <h1>Rapport genereren</h1>
    <p class="meta">Bestelling ontvangen: ${escapeHtml(dateStr)}</p>
    <div class="order-id">${escapeHtml(order.orderId || '—')}</div>
    ${order.warning ? `<div class="warn-box">⚠️ ${escapeHtml(order.warning)}</div>` : ''}
    <table>
      <tr><td>Naam</td><td><strong>${escapeHtml(birth.name)}</strong></td></tr>
      <tr><td>Geboren</td><td>${escapeHtml(formatBirthDate(birth))}</td></tr>
      <tr><td>Plaats</td><td>${escapeHtml(birth.place || '—')}</td></tr>
      <tr><td>Rapport</td><td>${escapeHtml(rapport.nl)} <em style="color:#aaa">(${escapeHtml(rapport.prijs)})</em></td></tr>
      <tr><td>E-mail</td><td>${escapeHtml(order.customerEmail)}</td></tr>
      <tr><td>Betaling</td><td>
        ${order.gumroadSkipped
          ? '<span class="badge badge-skip">Manueel verifiëren</span>'
          : '<span class="badge badge-ok">✓ Gumroad geverifieerd</span>'}
      </td></tr>
    </table>
    <form method="POST" action="/admin/generate" onsubmit="handleSubmit(event)">
      <input type="hidden" name="d" value="${escapeHtml(d)}">
      <input type="hidden" name="s" value="${escapeHtml(s)}">
      <button type="submit" id="btn">✦ Genereer &amp; verstuur rapport →</button>
    </form>
    <p class="footer">Rapport wordt via Claude gegenereerd en direct verstuurd naar ${escapeHtml(order.customerEmail)}.<br>Dit duurt 60–90 seconden. Sluit dit venster niet.</p>
  </div>
  <script>
    function handleSubmit(e) {
      const btn = document.getElementById('btn');
      btn.disabled = true;
      btn.textContent = '⏳ Bezig met genereren…';
    }
  </script>
  </body></html>`);
});

// ─── Admin: rapport genereren & versturen ─────────────────────────────────────

app.post('/admin/generate', express.urlencoded({ extended: true }), async (req, res) => {
  const { d, s } = req.body;
  if (!d || !s) return res.status(403).send(adminError('Ongeldige link.'));

  const expectedSig = crypto
    .createHmac('sha256', ADMIN_TOKEN)
    .update(d)
    .digest('hex')
    .slice(0, 16);

  if (!crypto.timingSafeEqual(Buffer.from(s), Buffer.from(expectedSig))) {
    return res.status(403).send(adminError('Handtekening ongeldig.'));
  }

  let order;
  try { order = JSON.parse(Buffer.from(d, 'base64url').toString()); }
  catch { return res.status(400).send(adminError('Ongeldige orderdata.')); }

  if (Date.now() - order.ts > MAGIC_LINK_TTL_MS) {
    return res.status(410).send(adminError('Link verlopen.'));
  }

  const { birth, systems, reportType, customerEmail, orderId } = order;
  const rapport = REPORT_NAMES[reportType] || { nl: reportType };

  // Stuur meteen een "bezig" pagina terug
  res.write(`<!DOCTYPE html><html lang="nl"><head><meta charset="UTF-8">
  <title>Genereren… — Het Stille Pad</title>
  <style>
    body { font-family: Georgia, serif; background: #f7f4ef; color: #2a2a35; display: flex;
           align-items: center; justify-content: center; min-height: 100vh; }
    .card { background: white; border-radius: 8px; padding: 48px 40px; max-width: 440px; text-align: center;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08); }
    h2 { font-weight: 400; font-size: 1.4rem; margin-bottom: 12px; }
    p { color: #888; font-size: 0.9rem; line-height: 1.6; }
    .spinner { width: 36px; height: 36px; border: 3px solid #e5dfd0; border-top-color: #b8884a;
               border-radius: 50%; animation: spin 0.9s linear infinite; margin: 0 auto 24px; }
    @keyframes spin { to { transform: rotate(360deg); } }
  </style></head><body>
  <div class="card">
    <div class="spinner"></div>
    <h2>Rapport wordt gegenereerd…</h2>
    <p>Claude schrijft het rapport voor <strong>${escapeHtml(birth.name)}</strong>.<br>
    Dit duurt 60–90 seconden. Laat dit venster open.</p>
  </div></body></html>`);

  const isQPB = (reportType === 'blueprint');

  try {
    const stream = await anthropic.messages.stream({
      model: 'claude-opus-4-8',
      max_tokens: 16000,
      system: [
        {
          type: 'text',
          text: isQPB ? buildQuietPathSystemPrompt() : buildSystemPrompt(),
          cache_control: { type: 'ephemeral' },
        },
      ],
      messages: [{
        role: 'user',
        content: isQPB
          ? buildQuietPathUserPrompt(birth, systems)
          : buildUserPrompt(birth, systems),
      }],
    });

    let fullReport = '';
    for await (const chunk of stream) {
      if (chunk.type === 'content_block_delta' && chunk.delta?.type === 'text_delta') {
        fullReport += chunk.delta.text;
      }
    }

    const wordCount = fullReport.split(/\s+/).length;
    log('info', 'Rapport gegenereerd via admin', { orderId, name: birth.name, words: wordCount, type: reportType });

    await resend.emails.send({
      from: FROM_EMAIL,
      to: customerEmail,
      subject: isQPB
        ? `The Quiet Path Blueprint — ${escapeHtml(birth.name)}`
        : `Jouw ${rapport.nl} — Het Stille Pad`,
      html: isQPB
        ? buildQuietPathEmail(birth.name, fullReport)
        : buildReportEmail(birth.name, rapport.nl, orderId, fullReport),
    });

    log('info', 'Rapport verstuurd', { orderId, to: customerEmail });

    res.write(`<script>
      document.body.innerHTML = '<div style="font-family:Georgia,serif;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#f7f4ef"><div style="background:white;border-radius:8px;padding:48px 40px;max-width:440px;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,0.08)"><p style="font-size:2rem;margin-bottom:16px">✓</p><h2 style="font-weight:400;font-size:1.4rem;margin-bottom:12px">Verstuurd!</h2><p style="color:#888;font-size:0.9rem">Rapport (${wordCount} woorden) bezorgd aan <strong>${escapeHtml(customerEmail)}</strong>.</p><p style="color:#ccc;font-size:0.78rem;margin-top:16px">Bestelling ${escapeHtml(orderId || '')}</p></div></div>';
    </script>`);
    res.end();

  } catch (err) {
    log('error', 'Rapport generatie mislukt', { orderId, error: err.message });
    res.write(`<script>
      document.body.innerHTML = '<div style="font-family:Georgia,serif;display:flex;align-items:center;justify-content:center;min-height:100vh;background:#f7f4ef"><div style="background:white;border-radius:8px;padding:48px 40px;max-width:440px;text-align:center;box-shadow:0 4px 24px rgba(0,0,0,0.08)"><p style="font-size:2rem;margin-bottom:16px">❌</p><h2 style="font-weight:400;color:#c62828">Fout bij genereren</h2><p style="color:#888;font-size:0.9rem;margin-top:12px">Probeer de pagina opnieuw te laden en het opnieuw te proberen.<br>Neem contact op als het probleem aanhoudt.</p></div></div>';
    </script>`);
    res.end();
  }
});

// ─── E-mail templates ─────────────────────────────────────────────────────────

function adminError(msg) {
  return `<!DOCTYPE html><html><body style="font-family:Georgia,serif;max-width:400px;margin:80px auto;text-align:center;color:#2a2a35">
  <h2 style="font-weight:400;color:#c62828">Toegang geweigerd</h2>
  <p style="color:#888;margin-top:12px">${escapeHtml(msg)}</p>
  </body></html>`;
}

function buildAdminEmail(orderId, birth, rapport, email, magicLink, verification) {
  return `<!DOCTYPE html><html><body style="font-family:Georgia,serif;max-width:560px;margin:0 auto;padding:24px;color:#2a2a35">
  <h2 style="font-weight:400;color:#b8884a;margin-bottom:4px">🌙 Nieuwe bestelling — Het Stille Pad</h2>
  <p style="font-family:monospace;font-size:0.72rem;color:#aaa;margin-bottom:20px">${escapeHtml(orderId)}</p>
  ${verification.warning ? `<div style="background:#fff8e1;border:1px solid #ffe082;border-radius:6px;padding:12px 16px;font-size:0.83rem;color:#795548;margin-bottom:16px">⚠️ ${escapeHtml(verification.warning)}</div>` : ''}
  <table style="width:100%;border-collapse:collapse;margin:16px 0">
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888;width:120px">Naam</td><td style="padding:8px 0;border-bottom:1px solid #ede8df"><strong>${escapeHtml(birth.name)}</strong></td></tr>
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888">Geboren</td><td style="padding:8px 0;border-bottom:1px solid #ede8df">${escapeHtml(formatBirthDate(birth))}</td></tr>
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888">Plaats</td><td style="padding:8px 0;border-bottom:1px solid #ede8df">${escapeHtml(birth.place || '—')}</td></tr>
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888">Rapport</td><td style="padding:8px 0;border-bottom:1px solid #ede8df">${escapeHtml(rapport.nl)} <span style="color:#aaa">(${escapeHtml(rapport.prijs)})</span></td></tr>
    <tr><td style="padding:8px 0;border-bottom:1px solid #ede8df;color:#888">E-mail</td><td style="padding:8px 0;border-bottom:1px solid #ede8df">${escapeHtml(email)}</td></tr>
    <tr><td style="padding:8px 0;color:#888">Gumroad</td><td style="padding:8px 0">${verification.skipped ? '⚠️ Manueel verifiëren' : '✓ Geverifieerd'}</td></tr>
  </table>
  <a href="${magicLink}" style="display:inline-block;background:#b8884a;color:white;text-decoration:none;padding:16px 32px;border-radius:6px;font-size:1rem;margin-top:8px">
    ✦ Genereer &amp; verstuur rapport →
  </a>
  <p style="color:#aaa;font-size:0.78rem;margin-top:16px">Link vervalt na 24 uur. ${verification.skipped ? '<strong>Verifieer de betaling in Gumroad vóór je klikt.</strong>' : 'Betaling is geverifieerd via Gumroad.'}</p>
  </body></html>`;
}

function buildConfirmEmail(name, rapportNaam, orderId) {
  return `<!DOCTYPE html><html><body style="font-family:Georgia,serif;max-width:560px;margin:0 auto;padding:40px 24px;color:#2a2a35">
  <p style="font-family:monospace;font-size:0.7rem;letter-spacing:0.2em;text-transform:uppercase;color:#b8884a;margin-bottom:20px">— Het Stille Pad</p>
  <h1 style="font-weight:400;font-size:1.8rem;line-height:1.2;margin-bottom:16px">Bedankt, ${escapeHtml(name)}.</h1>
  <p style="font-size:1rem;color:#666;line-height:1.7;margin-bottom:12px">Je bestelling voor het <strong>${escapeHtml(rapportNaam)}</strong> is ontvangen en wordt persoonlijk voorbereid.</p>
  <p style="font-size:1rem;color:#666;line-height:1.7;margin-bottom:24px">Je ontvangt je rapport <strong>binnen 24 uur</strong> op dit e-mailadres.</p>
  <p style="font-family:monospace;font-size:0.72rem;color:#ccc">Bestelling: ${escapeHtml(orderId)}</p>
  <hr style="border:0;border-top:1px solid #ede8df;margin:28px 0">
  <p style="font-size:0.82rem;color:#aaa">Het Stille Pad · Kosmische zelfkennis</p>
  </body></html>`;
}

function buildReportEmail(name, rapportNaam, orderId, reportHTML) {
  return `<!DOCTYPE html><html><head><meta charset="UTF-8">
  <style>
    body { font-family: Georgia, serif; max-width: 720px; margin: 0 auto; padding: 40px 32px; color: #2a2a35; line-height: 1.75; background: #fff; }
    h1, h2, h3, h4 { font-weight: 400; line-height: 1.2; }
    h2 { font-size: 1.6rem; margin: 0 0 20px; }
    h3 { font-size: 1.15rem; color: #2a2a35; border-bottom: 1px solid #e5dfd0; padding-bottom: 8px; margin: 32px 0 14px; }
    h4 { font-size: 1rem; margin: 0 0 8px; }
    p  { color: #4a4540; margin: 0 0 16px; }
    .report-cover { text-align: center; padding: 56px 0; border-bottom: 2px solid #e5dfd0; margin-bottom: 56px; }
    .report-label { font-family: monospace; font-size: 0.62rem; letter-spacing: 0.25em; text-transform: uppercase; color: #b8884a; margin-bottom: 16px; }
    .report-name  { font-size: 2.8rem; margin: 0 0 12px; font-weight: 300; }
    .report-date  { font-family: monospace; font-size: 0.7rem; color: #aaa; text-transform: uppercase; letter-spacing: 0.12em; }
    .report-systems { font-family: monospace; font-size: 0.65rem; color: #ccc; letter-spacing: 0.15em; margin-top: 8px; }
    .report-section { margin-bottom: 64px; padding-bottom: 48px; border-bottom: 1px solid #e5dfd0; }
    .section-number { font-family: monospace; font-size: 0.6rem; letter-spacing: 0.25em; color: #b8884a; text-transform: uppercase; margin-bottom: 12px; }
    .insight { border-left: 3px solid #b8884a; background: #fdf8f0; padding: 16px 20px; margin: 24px 0; border-radius: 0 6px 6px 0; }
    .insight strong { color: #b8884a; }
    .action-item { border: 1px solid #e5dfd0; border-radius: 6px; padding: 18px 20px; margin: 14px 0; background: #faf8f4; }
    .action-item h4 { color: #b8884a; font-size: 0.92rem; margin-bottom: 8px; }
    .week-block { border-left: 3px solid #5a6a8a; background: #f4f5f8; padding: 18px 20px; margin: 16px 0; border-radius: 0 6px 6px 0; }
    .week-block h4 { color: #5a6a8a; margin-bottom: 10px; }
    .daily-intention { font-size: 0.88rem; color: #7a7a8a; margin-top: 10px !important; }
    .report-closing { margin-top: 48px; padding-top: 32px; border-top: 1px solid #e5dfd0; font-style: italic; color: #888; }
    @media print { body { padding: 20px; } }
  </style></head><body>
  ${reportHTML}
  <div style="margin-top:56px;padding-top:28px;border-top:1px solid #e5dfd0;text-align:center">
    <p style="font-family:monospace;font-size:0.65rem;letter-spacing:0.18em;text-transform:uppercase;color:#aaa">
      Het Stille Pad · Persoonlijk Rapport voor ${escapeHtml(name)}
    </p>
    <p style="font-size:0.78rem;color:#ccc;margin-top:8px">Afdrukken als PDF: Ctrl+P (Windows) of Cmd+P (Mac) → Opslaan als PDF.</p>
    <p style="font-family:monospace;font-size:0.65rem;color:#ddd;margin-top:8px">${escapeHtml(orderId)}</p>
  </div>
  </body></html>`;
}

// ─── Nieuwsbrief / lead magnet ─────────────────────────────────────────────────

const subscribeLimiter = rateLimit({ windowMs: 60 * 60 * 1000, max: 5 });

app.post('/api/subscribe', subscribeLimiter, async (req, res) => {
  const { email, tool, name } = req.body || {};

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: 'Ongeldig e-mailadres.' });
  }

  const toolLabel = tool || 'jouw calculator';
  const firstName = (name || '').trim().split(' ')[0] || 'daar';

  try {
    await resend.emails.send({
      from: FROM_EMAIL,
      to: email,
      subject: `Jouw gratis Mini-Blauwdruk — Het Stille Pad`,
      html: buildMiniBlueprint(firstName, toolLabel),
    });

    // Notificeer admin (optioneel, stille melding)
    resend.emails.send({
      from: FROM_EMAIL,
      to: ADMIN_EMAIL,
      subject: `📬 Nieuwe inschrijving: ${email}`,
      html: `<p>Nieuwe lead via ${escapeHtml(toolLabel)}-calculator.<br>E-mail: <strong>${escapeHtml(email)}</strong><br>Naam: ${escapeHtml(name || '—')}</p>`,
    }).catch(() => {});

    log('info', 'Nieuwe inschrijving', { email, tool: toolLabel });
    res.json({ success: true });
  } catch (err) {
    log('error', 'Subscribe fout', { error: err.message });
    res.status(500).json({ error: 'E-mail kon niet worden verstuurd.' });
  }
});

function buildMiniBlueprint(name, tool) {
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
<body style="font-family:Georgia,serif;max-width:560px;margin:0 auto;padding:40px 24px;color:#2a2a35;">
  <p style="font-family:monospace;font-size:0.7rem;letter-spacing:0.2em;text-transform:uppercase;color:#b8922a;margin-bottom:20px;">— Het Stille Pad</p>
  <h1 style="font-weight:400;font-size:1.8rem;line-height:1.2;margin-bottom:16px;">Je Mini-Blauwdruk, ${escapeHtml(name)}.</h1>
  <p style="font-size:1rem;color:#555;line-height:1.75;margin-bottom:16px;">
    Bedankt voor je interesse in ${escapeHtml(tool)}. Je hebt net een eerste blik geworpen op een systeem dat duizenden mensen heeft geholpen zichzelf beter te begrijpen.
  </p>
  <p style="font-size:1rem;color:#555;line-height:1.75;margin-bottom:16px;">
    Wat je zojuist berekend hebt is de <strong>ruwe data</strong> — de structuren, de getallen, de pilaren. Ze zijn precies. Maar ze vertellen nog niet het verhaal.
  </p>
  <p style="font-size:1rem;color:#555;line-height:1.75;margin-bottom:28px;">
    Het verhaal is wat er gebeurt wanneer je ziet hoe die structuren samenkomen in jouw specifieke leven. Wanneer ${escapeHtml(tool)}, Human Design én Numerologie naar hetzelfde patroon wijzen — dan is dat geen toeval. Dan is het een rode draad die al altijd aanwezig was, maar nooit zo duidelijk zichtbaar.
  </p>
  <div style="background:#f0ece4;border-left:3px solid #b8922a;padding:18px 20px;margin-bottom:28px;font-style:italic;color:#3d3830;">
    "Jij bent niet kapot. Jij bent ongelezen."
  </div>
  <p style="font-size:1rem;color:#555;line-height:1.75;margin-bottom:24px;">
    Als je verder wilt gaan dan de ruwe data — als je wilt weten wat het allemaal <em>betekent</em> voor jouw keuzes, relaties, energie en timing — dan is er het Persoonlijk Rapport.
  </p>
  <a href="https://theorderofthequietpath.github.io/#rapporten"
     style="display:inline-block;background:#b8922a;color:white;text-decoration:none;padding:14px 28px;font-family:Georgia,serif;font-size:0.9rem;margin-bottom:32px;">
    Bekijk de persoonlijke rapporten →
  </a>
  <hr style="border:0;border-top:1px solid #e5dfd0;margin-bottom:24px;">
  <p style="font-size:0.82rem;color:#aaa;line-height:1.6;">
    Het Stille Pad · Kosmische zelfkennis<br>
    Je ontvangt geen verdere e-mails tenzij je een rapport bestelt.
  </p>
</body></html>`;
}

// ─── Health ────────────────────────────────────────────────────────────────────

app.get('/health', (req, res) => res.json({ status: 'ok', ts: new Date().toISOString() }));

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => log('info', `Stille Pad backend gestart op poort ${PORT}`));
