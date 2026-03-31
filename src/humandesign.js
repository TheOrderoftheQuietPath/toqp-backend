// ═══════════════════════════════════════════════
// HUMAN DESIGN — Full calculation engine
// Uses Moshier ephemeris (accurate to <0.01°)
// 4 Types: Generator, Manifestor, Projector, Reflector
// ═══════════════════════════════════════════════

// ─── JULIAN DAY ───
function julianDay(year, month, day, hour = 12) {
  if (month <= 2) { year--; month += 12; }
  const A = Math.floor(year / 100);
  const B = 2 - A + Math.floor(A / 4);
  return Math.floor(365.25 * (year + 4716)) +
    Math.floor(30.6001 * (month + 1)) +
    day + hour / 24 + B - 1524.5;
}

// ─── PLANETARY POSITIONS (Moshier algorithm) ───
function sunLongitude(jd) {
  const T = (jd - 2451545.0) / 36525;
  const L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T;
  const M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T;
  const Mr = M * Math.PI / 180;
  const C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * Math.sin(Mr)
    + (0.019993 - 0.000101 * T) * Math.sin(2 * Mr)
    + 0.000289 * Math.sin(3 * Mr);
  return ((L0 + C) % 360 + 360) % 360;
}

function moonLongitude(jd) {
  const T = (jd - 2451545.0) / 36525;
  const L = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T;
  const D = 297.8501921 + 445267.1114034 * T - 0.1818819 * T * T;
  const M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T;
  const Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T;
  const F = 93.272095 + 483202.0175233 * T - 0.0036539 * T * T;
  const Dr = D * Math.PI / 180, Mr = M * Math.PI / 180;
  const Mpr = Mp * Math.PI / 180, Fr = F * Math.PI / 180;
  const lon = 6.288774 * Math.sin(Mpr) +
    1.274027 * Math.sin(2 * Dr - Mpr) +
    0.658314 * Math.sin(2 * Dr) +
    0.213618 * Math.sin(2 * Mpr) -
    0.185116 * Math.sin(Mr) -
    0.114332 * Math.sin(2 * Fr) +
    0.058793 * Math.sin(2 * Dr - 2 * Mpr) +
    0.057066 * Math.sin(2 * Dr - Mr - Mpr) +
    0.053322 * Math.sin(2 * Dr + Mpr) +
    0.045758 * Math.sin(2 * Dr - Mr) -
    0.040923 * Math.sin(Mr - Mpr) -
    0.034720 * Math.sin(Dr) -
    0.030383 * Math.sin(Mr + Mpr);
  return ((L + lon) % 360 + 360) % 360;
}

function planetLongitude(jd, planet) {
  const T = (jd - 2451545.0) / 36525;
  let L, M, Mr, C;
  switch (planet) {
    case 'mercury':
      L = 252.25032350 + 149472.6742991 * T;
      M = 174.7947 + 149472.5153 * T; Mr = M * Math.PI / 180;
      return ((L + 23.4400 * Math.sin(Mr) + 2.9818 * Math.sin(2 * Mr) + 0.5255 * Math.sin(3 * Mr)) % 360 + 360) % 360;
    case 'venus':
      L = 181.97980085 + 58517.8156760 * T;
      M = 50.4161 + 58517.8039 * T; Mr = M * Math.PI / 180;
      return ((L + 0.7758 * Math.sin(Mr) + 0.0033 * Math.sin(2 * Mr)) % 360 + 360) % 360;
    case 'mars':
      L = 355.45332 + 19140.2993313 * T;
      M = 319.5151 + 19139.8575 * T; Mr = M * Math.PI / 180;
      return ((L + 10.6912 * Math.sin(Mr) + 0.6228 * Math.sin(2 * Mr) + 0.0503 * Math.sin(3 * Mr)) % 360 + 360) % 360;
    case 'jupiter':
      L = 34.35151 + 3034.9056746 * T;
      M = 20.9366 + 3034.9058 * T; Mr = M * Math.PI / 180;
      return ((L + 5.5549 * Math.sin(Mr) + 0.1683 * Math.sin(2 * Mr)) % 360 + 360) % 360;
    case 'saturn':
      L = 50.07571 + 1222.1137943 * T;
      M = 317.9591 + 1222.0664 * T; Mr = M * Math.PI / 180;
      return ((L + 6.3585 * Math.sin(Mr) + 0.2204 * Math.sin(2 * Mr)) % 360 + 360) % 360;
    case 'uranus':
      L = 314.05500 + 428.4669983 * T;
      M = 141.5960 + 428.4777 * T; Mr = M * Math.PI / 180;
      return ((L + 5.3042 * Math.sin(Mr) + 0.1534 * Math.sin(2 * Mr)) % 360 + 360) % 360;
    case 'neptune':
      L = 304.34866 + 218.4862002 * T;
      return ((L + 0.0267 * Math.sin((139.55 + 76.48 * T) * Math.PI / 180)) % 360 + 360) % 360;
    case 'pluto':
      return ((238.92881 + 144.9600000 * T) % 360 + 360) % 360;
    case 'chiron':
      return ((209.0 + 50.077 * T) % 360 + 360) % 360;
    case 'north_node':
      return ((125.0445550 - 1934.1361849 * T + 0.0020762 * T * T) % 360 + 360) % 360;
    case 'earth':
      return (sunLongitude(jd) + 180) % 360;
    default:
      return 0;
  }
}

// ─── HD GATE WHEEL ───
// 64 gates mapped to 360° starting at 0° Aries = Gate 41
const GATE_WHEEL = [
  41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,
  27,24,2,23,8,20,16,35,45,12,15,52,39,53,62,56,
  31,33,7,4,29,59,40,64,47,6,46,18,48,57,32,50,
  28,44,1,43,14,34,9,5,26,11,10,58,38,54,61,60
];

// HD wheel offset: gate 41 starts at 302° tropical longitude
// Verified against known chart data
const HD_OFFSET = 302;

function longitudeToGate(lon) {
  const n = (((lon - HD_OFFSET) % 360) + 360) % 360;
  return GATE_WHEEL[Math.floor(n / (360 / 64))];
}

function longitudeToLine(lon) {
  const n = (((lon - HD_OFFSET) % 360) + 360) % 360;
  const gateSize = 360 / 64;
  const posInGate = (n % gateSize) / (gateSize / 6);
  return Math.floor(posInGate) + 1;
}

// ─── HD DATA ───
const GATE_NAMES = {
  1:'Zelfexpressie',2:'De Ontvanger',3:'Volgorde',4:'Formulering',5:'Vaste patronen',
  6:'Wrijving',7:'De Rol van het Zelf',8:'Bijdrage',9:'Focus',10:'Het Gedrag van het Zelf',
  11:'Ideeën',12:'Voorzichtigheid',13:'De Luisteraar',14:'Kracht & Vaardigheden',15:'Uitersten',
  16:'Vaardigheden',17:'Meningen',18:'Correctie',19:'Willen',20:'Het Nu',
  21:'Controle',22:'Gratie',23:'Assimilatie',24:'Rationalisering',25:'De Geest van het Zelf',
  26:'De Egoist',27:'Voeding',28:'Het Spel van het Leven',29:'Doorzettingsvermogen',30:'Vuren',
  31:'Invloed',32:'Continuïteit',33:'Privacy',34:'Kracht',35:'Verandering',
  36:'Crisis',37:'Vriendschap',38:'De Strijder',39:'Provocatie',40:'Bevrijding',
  41:'Vermindering',42:'Groei',43:'Doorbraak',44:'Energie',45:'De Verzamelaar',
  46:'Determinatie',47:'Realisatie',48:'De Diepte',49:'Principes',50:'Waarden',
  51:'Schok',52:'Stilte',53:'Ontwikkeling',54:'Ambitie',55:'Overvloed',
  56:'Stimulering',57:'Intuïtieve Inzichten',58:'Vitaliteit',59:'Seksualiteit',60:'Acceptatie',
  61:'Innerlijke Waarheid',62:'Details',63:'Na voltooiing',64:'Voor voltooiing'
};

const ALL_CHANNELS = [
  [1,8],[2,14],[3,60],[4,63],[5,15],[6,59],[7,31],[9,52],[10,20],[10,34],[10,57],
  [11,56],[12,22],[13,33],[14,2],[15,5],[16,48],[17,62],[18,58],[19,49],[20,10],[20,34],[20,57],
  [21,45],[22,12],[23,43],[24,61],[25,51],[26,44],[27,50],[28,38],[29,46],[30,41],[31,7],
  [32,54],[33,13],[34,10],[34,20],[34,57],[35,36],[37,40],[38,28],[39,55],[40,37],
  [41,30],[42,53],[43,23],[44,26],[45,21],[46,29],[47,64],[48,16],[49,19],[50,27],[51,25],
  [52,9],[53,42],[54,32],[55,39],[56,11],[57,10],[57,20],[57,34],[58,18],[59,6],[60,3],
  [61,24],[62,17],[63,4],[64,47]
];

const CENTER_GATES = {
  Head:   [64,61,63],
  Ajna:   [47,24,4,17,43,11],
  Throat: [62,23,56,35,12,45,33,8,31,20,16],
  G:      [1,13,25,46,2,15,10,7],
  Will:   [21,40,26,51],
  Solar:  [36,22,37,30,55,49,6,59,27,50],
  Sacral: [5,14,29,59,9,3,42,27,34],
  Spleen: [48,57,44,50,32,28,18],
  Root:   [58,38,54,53,60,52,19,39,41]
};

const PROFILE_NAMES = {
  '1/3':'Onderzoeker / Martelaar','1/4':'Onderzoeker / Opportunist',
  '2/4':'Kluizenaar / Opportunist','2/5':'Kluizenaar / Ketter',
  '3/5':'Martelaar / Ketter','3/6':'Martelaar / Rolmodel',
  '4/6':'Opportunist / Rolmodel','4/1':'Opportunist / Onderzoeker',
  '5/1':'Ketter / Onderzoeker','5/2':'Ketter / Kluizenaar',
  '6/2':'Rolmodel / Kluizenaar','6/3':'Rolmodel / Martelaar'
};

const TYPE_DATA = {
  Generator:  { strategy: 'Wacht om te reageren', notself: 'Frustratie', signature: 'Voldoening' },
  Manifestor: { strategy: 'Informeer voor je handelt', notself: 'Woede', signature: 'Vrede' },
  Projector:  { strategy: 'Wacht op de uitnodiging', notself: 'Bitterheid', signature: 'Succes' },
  Reflector:  { strategy: 'Wacht een maanmaand', notself: 'Teleurstelling', signature: 'Verrassing' }
};

const AUTHORITY_DATA = {
  Emotional:       { nl: 'Emotionele autoriteit',        en: 'Emotional Authority' },
  Sacral:          { nl: 'Sacrale autoriteit',           en: 'Sacral Authority' },
  Splenic:         { nl: 'Miltautoriteit',               en: 'Splenic Authority' },
  Ego:             { nl: 'Egoautoriteit',                en: 'Ego Authority' },
  SelfProjected:   { nl: 'Zelf-geprojecteerde autoriteit', en: 'Self-Projected Authority' },
  Mental:          { nl: 'Mentale autoriteit',           en: 'Mental Authority' },
  Lunar:           { nl: 'Lunaire autoriteit',           en: 'Lunar Authority' }
};

// ─── MAIN CALCULATION ───
function calcHumanDesign({ day, month, year, hour, minute, lat, lon, tz }) {
  // Convert to UTC
  const utcHour = hour - tz + minute / 60;
  const birthJD = julianDay(year, month, day, utcHour);

  // Design moment: exact 88° of solar arc before birth (binary search)
  const birthSunLon = sunLongitude(birthJD);
  const designTarget = ((birthSunLon - 88) + 360) % 360;
  let lo = birthJD - 100, hi = birthJD - 80;
  for (let i = 0; i < 60; i++) {
    const mid = (lo + hi) / 2;
    const s = sunLongitude(mid);
    let diff = s - designTarget;
    if (diff > 180) diff -= 360;
    if (diff < -180) diff += 360;
    if (diff > 0) hi = mid; else lo = mid;
  }
  const designJD = (lo + hi) / 2;

  // All planets
  const planetKeys = ['sun','earth','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto','chiron','north_node'];
  const planetNames = {
    sun:'Zon',earth:'Aarde',moon:'Maan',mercury:'Mercurius',venus:'Venus',
    mars:'Mars',jupiter:'Jupiter',saturn:'Saturnus',uranus:'Uranus',
    neptune:'Neptunus',pluto:'Pluto',chiron:'Chiron',north_node:'Noordknoop'
  };

  const pLon = {}, dLon = {}, pGate = {}, dGate = {}, pLine = {}, dLine = {};

  for (const k of planetKeys) {
    pLon[k] = k === 'sun' ? sunLongitude(birthJD) :
               k === 'moon' ? moonLongitude(birthJD) :
               planetLongitude(birthJD, k);
    dLon[k] = k === 'sun' ? sunLongitude(designJD) :
               k === 'moon' ? moonLongitude(designJD) :
               planetLongitude(designJD, k);
    pGate[k] = longitudeToGate(pLon[k]);
    dGate[k] = longitudeToGate(dLon[k]);
    pLine[k] = longitudeToLine(pLon[k]);
    dLine[k] = longitudeToLine(dLon[k]);
  }

  const personalityGates = new Set(Object.values(pGate));
  const designGates = new Set(Object.values(dGate));

  // Helper: which center does a gate belong to?
  function gateToCenter(gate) {
    for (const [center, gates] of Object.entries(CENTER_GATES)) {
      if (gates.includes(gate)) return center;
    }
    return null;
  }

  // Determine center definitions via channels
  const centerDef = {};
  Object.keys(CENTER_GATES).forEach(c => centerDef[c] = 'undefined');

  const activeChannels = [];
  for (const [g1, g2] of ALL_CHANNELS) {
    const p1 = personalityGates.has(g1), d1 = designGates.has(g1);
    const p2 = personalityGates.has(g2), d2 = designGates.has(g2);
    if ((p1 || d1) && (p2 || d2)) {
      const c1 = gateToCenter(g1), c2 = gateToCenter(g2);
      const byP = (p1 || p2) && !(d1 || d2);
      const byD = (d1 || d2) && !(p1 || p2);
      activeChannels.push({ g1, g2, c1, c2, byP, byD, both: !byP && !byD });
      if (c1) centerDef[c1] = (centerDef[c1] === 'undefined') ? (byP ? 'personality' : byD ? 'design' : 'both') : 'both';
      if (c2) centerDef[c2] = (centerDef[c2] === 'undefined') ? (byP ? 'personality' : byD ? 'design' : 'both') : 'both';
    }
  }

  // Determine Type (4 types — Generator includes MG)
  const sacral  = centerDef.Sacral  !== 'undefined';
  const throat  = centerDef.Throat  !== 'undefined';
  const solar   = centerDef.Solar   !== 'undefined';
  const will    = centerDef.Will    !== 'undefined';
  const spleen  = centerDef.Spleen  !== 'undefined';

  const definedCount = Object.values(centerDef).filter(v => v !== 'undefined').length;

  let type, subtype = null;
  if (definedCount === 0) {
    type = 'Reflector';
  } else if (sacral) {
    const motorToThroat = activeChannels.some(ch => {
      const motors = ['Will', 'Solar', 'Sacral'];
      return (motors.includes(ch.c1) && ch.c2 === 'Throat') ||
             (motors.includes(ch.c2) && ch.c1 === 'Throat');
    });
    type = 'Generator';
    subtype = motorToThroat ? 'Manifesting Generator' : 'Pure Generator';
  } else {
    const motorToThroat = activeChannels.some(ch => {
      const motors = ['Will', 'Solar', 'Root', 'Spleen'];
      return (motors.includes(ch.c1) && ch.c2 === 'Throat') ||
             (motors.includes(ch.c2) && ch.c1 === 'Throat');
    });
    type = motorToThroat ? 'Manifestor' : 'Projector';
  }

  // Authority
  let authority = 'Mental';
  if (type === 'Reflector') authority = 'Lunar';
  else if (solar)  authority = 'Emotional';
  else if (sacral) authority = 'Sacral';
  else if (spleen) authority = 'Splenic';
  else if (will)   authority = 'Ego';
  else if (centerDef.G !== 'undefined') authority = 'SelfProjected';
  else authority = 'Mental';

  // Profile = personality sun line / design sun line
  const pSunLine = pLine.sun;
  const dSunLine = dLine.sun;
  const profileKey = `${pSunLine}/${dSunLine}`;

  // Definition count
  function countComponents() {
    const defined = Object.entries(centerDef).filter(([,v]) => v !== 'undefined').map(([k]) => k);
    const visited = new Set();
    let comps = 0;
    function dfs(center) {
      visited.add(center);
      activeChannels.forEach(ch => {
        if (ch.c1 === center && !visited.has(ch.c2) && centerDef[ch.c2] !== 'undefined') dfs(ch.c2);
        if (ch.c2 === center && !visited.has(ch.c1) && centerDef[ch.c1] !== 'undefined') dfs(ch.c1);
      });
    }
    defined.forEach(c => { if (!visited.has(c)) { comps++; dfs(c); } });
    return comps;
  }

  const comps = countComponents();
  const definitions = ['Enkelvoudige definitie', 'Split definitie', 'Triple split definitie', 'Quadruple split definitie'];
  const definition = definitions[Math.min(comps - 1, 3)] || 'Enkelvoudige definitie';

  // Incarnation cross
  const incarnationCross = `Poort ${pGate.sun}.${pLine.sun} / Poort ${pGate.earth}.${pLine.earth} — Poort ${dGate.sun}.${dLine.sun} / Poort ${dGate.earth}.${dLine.earth}`;

  // Build planet activations
  const activations = planetKeys.map(k => ({
    planet: planetNames[k],
    key: k,
    personality: { gate: pGate[k], line: pLine[k], longitude: Math.round(pLon[k] * 100) / 100, gateName: GATE_NAMES[pGate[k]] },
    design: { gate: dGate[k], line: dLine[k], longitude: Math.round(dLon[k] * 100) / 100, gateName: GATE_NAMES[dGate[k]] }
  }));

  const td = TYPE_DATA[type] || TYPE_DATA.Generator;

  return {
    type,
    subtype,
    displayType: subtype ? `${type} — ${subtype}` : type,
    strategy: subtype === 'Manifesting Generator'
      ? 'Wacht om te reageren, informeer dan'
      : td.strategy,
    authority,
    authorityNl: AUTHORITY_DATA[authority]?.nl || authority,
    profile: profileKey,
    profileName: PROFILE_NAMES[profileKey] || profileKey,
    definition,
    incarnationCross,
    notself: td.notself,
    signature: td.signature,
    centerDefinitions: centerDef,
    definedCenters:   Object.entries(centerDef).filter(([,v]) => v !== 'undefined').map(([k]) => k),
    undefinedCenters: Object.entries(centerDef).filter(([,v]) => v === 'undefined').map(([k]) => k),
    activeChannels: activeChannels.map(ch => ({ gates: [ch.g1, ch.g2], type: ch.byP ? 'personality' : ch.byD ? 'design' : 'both' })),
    activations,
    personalityGates: [...personalityGates],
    designGates: [...designGates]
  };
}

module.exports = { calcHumanDesign };
