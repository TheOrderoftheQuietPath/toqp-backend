const express = require('express');
const cors = require('cors');
const { calcNumerology } = require('./numerology');
const { calcBazi } = require('./bazi');
const { calcHumanDesign } = require('./humandesign');

const app = express();
const PORT = process.env.PORT || 3000;

// ─── MIDDLEWARE ───
app.use(cors());
app.use(express.json());

// ─── HEALTH CHECK ───
app.get('/', (req, res) => {
  res.json({ status: 'ok', service: 'The Order of the Quiet Path API' });
});

// ─── NUMEROLOGY ───
app.post('/api/numerology', (req, res) => {
  try {
    const { day, month, year, firstname, lastname } = req.body;
    if (!day || !month || !year) return res.status(400).json({ error: 'Missing birth date' });
    const name = `${firstname || ''} ${lastname || ''}`.trim();
    const result = calcNumerology({ day, month, year, name });
    res.json(result);
  } catch (err) {
    console.error('Numerology error:', err);
    res.status(500).json({ error: err.message });
  }
});

// ─── BAZI ───
app.post('/api/bazi', (req, res) => {
  try {
    const { day, month, year, hour, minute } = req.body;
    if (!day || !month || !year) return res.status(400).json({ error: 'Missing birth date' });
    const result = calcBazi({ day, month, year, hour: hour || 12, minute: minute || 0 });
    res.json(result);
  } catch (err) {
    console.error('BaZi error:', err);
    res.status(500).json({ error: err.message });
  }
});

// ─── HUMAN DESIGN ───
app.post('/api/human-design', (req, res) => {
  try {
    const { day, month, year, hour, minute, lat, lon, tz } = req.body;
    if (!day || !month || !year) return res.status(400).json({ error: 'Missing birth date' });
    const result = calcHumanDesign({
      day, month, year,
      hour: hour || 0,
      minute: minute || 0,
      lat: lat || 51.05,
      lon: lon || 3.72,
      tz: tz || 1
    });
    res.json(result);
  } catch (err) {
    console.error('Human Design error:', err);
    res.status(500).json({ error: err.message });
  }
});

// ─── COMBINED READING ───
app.post('/api/reading', (req, res) => {
  try {
    const { hd, numerology, bazi, firstname } = req.body;
    const name = firstname || 'je';

    const reading = generateReading({ hd, numerology, bazi, name });
    res.json({ text: reading });
  } catch (err) {
    console.error('Reading error:', err);
    res.status(500).json({ error: err.message });
  }
});

function generateReading({ hd, numerology, bazi, name }) {
  const lines = [];

  if (hd && hd.type) {
    const typeTexts = {
      Generator: `Als Generator ben jij de levenskracht van dit systeem — ${name} is hier om te reageren op het leven, niet om het te initiëren. Je sacrale energie is je grootste kompas.`,
      Manifestor: `Als Manifestor draag jij een zeldzame kracht in je — ${name} is hier om te initiëren en in beweging te zetten. Informeren voor je handelt opent deuren die anders gesloten blijven.`,
      Projector: `Als Projector zie jij wat anderen niet zien — ${name} heeft het vermogen om systemen en mensen diep te begrijpen. Wacht op de uitnodiging: zo wordt jouw wijsheid echt gehoord.`,
      Reflector: `Als Reflector ben jij de spiegel van je omgeving — ${name} weerspiegelt de gezondheid van de gemeenschap. Jouw seldzaamheid is een gave. Neem de tijd van een maancyclus voor grote beslissingen.`
    };
    lines.push(typeTexts[hd.type] || `Jouw Human Design type is ${hd.type}.`);
  }

  if (hd && hd.profile) {
    lines.push(`Je ${hd.profile} profiel geeft jouw leven een specifieke kleur en thema — dit is de rol die jij speelt in het grotere geheel.`);
  }

  if (numerology && numerology.lifePath) {
    const lpTexts = {
      1: 'Je levenspadgetal 1 wijst op leiderschap en pionieren — jij baant nieuwe wegen.',
      2: 'Je levenspadgetal 2 wijst op diplomatie en samenwerking — jij brengt mensen samen.',
      3: 'Je levenspadgetal 3 wijst op creativiteit en expressie — jij bent hier om te delen.',
      4: 'Je levenspadgetal 4 wijst op bouwen en structuur — jij legt de fundering.',
      5: 'Je levenspadgetal 5 wijst op vrijheid en avontuur — jij bent hier om te ervaren.',
      6: 'Je levenspadgetal 6 wijst op zorg en harmonie — jij heelt en verbindt.',
      7: 'Je levenspadgetal 7 wijst op diepgang en innerlijke wijsheid — jij zoekt de waarheid.',
      8: 'Je levenspadgetal 8 wijst op kracht en manifestatie — jij bouwt iets blijvends.',
      9: 'Je levenspadgetal 9 wijst op wijsheid en voltooiing — jij draagt een universele missie.',
      11: 'Je meestergetal 11 wijst op spiritueel inzicht en inspiratie — jij verlicht anderen.',
      22: 'Je meestergetal 22 wijst op de meesterbouwer — jij realiseert visies op grote schaal.',
      33: 'Je meestergetal 33 wijst op de meesterleraar — jij draagt liefde en wijsheid als gift.'
    };
    lines.push(lpTexts[numerology.lifePath] || `Je levenspadgetal ${numerology.lifePath} draagt een unieke boodschap.`);
  }

  if (bazi && bazi.dayPillar) {
    lines.push(`Je BaZi dag-meester (${bazi.dayPillar.stem}) onthult jouw ware innerlijke aard en hoe jij je verhoudt tot de wereld om je heen.`);
  }

  lines.push(`Dit is een eerste blik op jouw kosmische blauwdruk. Voor een volledige, persoonlijke duiding — neem contact op met Shi Ming Dao.`);

  return lines.join('\n\n');
}

app.listen(PORT, () => {
  console.log(`TOQP API running on port ${PORT}`);
});
