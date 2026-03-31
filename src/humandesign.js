'use strict';
// ═══════════════════════════════════════════════
// HUMAN DESIGN — Full calculation engine
// Uses high-accuracy Meeus ephemeris
// HD wheel offset: 302° verified against known charts
// ═══════════════════════════════════════════════

const { julianDay, getAllPlanetPositions, getDesignJD, norm360 } = require('./ephemeris');

// ─── HD GATE WHEEL (302° offset from tropical 0°Aries) ───
const GATE_WHEEL = [
  41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,
  27,24,2,23,8,20,16,35,45,12,15,52,39,53,62,56,
  31,33,7,4,29,59,40,64,47,6,46,18,48,57,32,50,
  28,44,1,43,14,34,9,5,26,11,10,58,38,54,61,60
];
const HD_OFFSET = 302;

function lonToGate(lon) {
  const n = norm360(lon - HD_OFFSET);
  return GATE_WHEEL[Math.floor(n / (360 / 64))];
}

function lonToLine(lon) {
  const n = norm360(lon - HD_OFFSET);
  const gs = 360 / 64;
  return Math.floor((n % gs) / (gs / 6)) + 1;
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

// All 36 channels: [gate1, gate2]
const ALL_CHANNELS = [
  [1,8],[2,14],[3,60],[4,63],[5,15],[6,59],[7,31],[9,52],[10,20],[10,34],[10,57],
  [11,56],[12,22],[13,33],[14,2],[15,5],[16,48],[17,62],[18,58],[19,49],[20,10],[20,34],[20,57],
  [21,45],[22,12],[23,43],[24,61],[25,51],[26,44],[27,50],[28,38],[29,46],[30,41],[31,7],
  [32,54],[33,13],[34,10],[34,20],[34,57],[35,36],[37,40],[38,28],[39,55],[40,37],
  [41,30],[42,53],[43,23],[44,26],[45,21],[46,29],[47,64],[48,16],[49,19],[50,27],[51,25],
  [52,9],[53,42],[54,32],[55,39],[56,11],[57,10],[57,20],[57,34],[58,18],[59,6],[60,3],
  [61,24],[62,17],[63,4],[64,47]
];

// Deduplicate channels (some appear twice in list above)
const UNIQUE_CHANNELS = (() => {
  const seen = new Set();
  return ALL_CHANNELS.filter(([a, b]) => {
    const k = Math.min(a,b)+'-'+Math.max(a,b);
    if (seen.has(k)) return false;
    seen.add(k); return true;
  });
})();

// Center → gates mapping
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

// Which center does a gate belong to?
const GATE_CENTER = {};
for (const [center, gates] of Object.entries(CENTER_GATES)) {
  for (const gate of gates) GATE_CENTER[gate] = center;
}

// Motor centers
const MOTORS = new Set(['Will', 'Solar', 'Sacral', 'Root']);

const PROFILE_NAMES = {
  '1/3':'Onderzoeker / Martelaar','1/4':'Onderzoeker / Opportunist',
  '2/4':'Kluizenaar / Opportunist','2/5':'Kluizenaar / Ketter',
  '3/5':'Martelaar / Ketter','3/6':'Martelaar / Rolmodel',
  '4/6':'Opportunist / Rolmodel','4/1':'Opportunist / Onderzoeker',
  '5/1':'Ketter / Onderzoeker','5/2':'Ketter / Kluizenaar',
  '6/2':'Rolmodel / Kluizenaar','6/3':'Rolmodel / Martelaar'
};

const TYPE_DATA = {
  Generator:  { strategy:'Wacht om te reageren',          notself:'Frustratie',    signature:'Voldoening' },
  Manifestor: { strategy:'Informeer voor je handelt',     notself:'Woede',         signature:'Vrede' },
  Projector:  { strategy:'Wacht op de uitnodiging',       notself:'Bitterheid',    signature:'Succes' },
  Reflector:  { strategy:'Wacht een maanmaand (28 dagen)',notself:'Teleurstelling', signature:'Verrassing' }
};

const AUTHORITY_NAMES = {
  Emotional:     'Emotionele autoriteit',
  Sacral:        'Sacrale autoriteit',
  Splenic:       'Miltautoriteit (Spleen)',
  Ego:           'Ego-autoriteit (Will)',
  SelfProjected: 'Zelf-geprojecteerde autoriteit',
  Mental:        'Mentale autoriteit (No Inner)',
  Lunar:         'Lunaire autoriteit'
};

// ─── MAIN CALCULATION ───
function calcHumanDesign({ day, month, year, hour, minute, lat, lon, tz }) {
  // UTC conversion
  const utcHour = (hour || 0) - (tz || 1) + (minute || 0) / 60;
  const birthJD = julianDay(year, month, day, utcHour);
  const designJD = getDesignJD(birthJD);

  // All planet positions
  const pPos = getAllPlanetPositions(birthJD);  // Personality (birth)
  const dPos = getAllPlanetPositions(designJD); // Design (~88° before)

  const planetKeys = ['sun','earth','moon','mercury','venus','mars','jupiter','saturn','uranus','neptune','pluto','chiron','north_node'];
  const planetNames = {
    sun:'Zon', earth:'Aarde', moon:'Maan', mercury:'Mercurius', venus:'Venus',
    mars:'Mars', jupiter:'Jupiter', saturn:'Saturnus', uranus:'Uranus',
    neptune:'Neptunus', pluto:'Pluto', chiron:'Chiron', north_node:'Noordknoop'
  };
  const planetIcons = {
    sun:'☀', earth:'⊕', moon:'☽', mercury:'☿', venus:'♀', mars:'♂',
    jupiter:'♃', saturn:'♄', uranus:'♅', neptune:'♆', pluto:'♇', chiron:'⚷', north_node:'☊'
  };

  // Gates and lines for all planets
  const pGates = new Set();
  const dGates = new Set();
  const activations = [];

  for (const key of planetKeys) {
    const pLon = pPos[key];
    const dLon = dPos[key];
    const pg = lonToGate(pLon), pl = lonToLine(pLon);
    const dg = lonToGate(dLon), dl = lonToLine(dLon);
    pGates.add(pg);
    dGates.add(dg);
    activations.push({
      planet: planetNames[key] || key,
      key,
      icon: planetIcons[key] || '·',
      personality: { gate: pg, line: pl, longitude: Math.round(pLon * 1000) / 1000, gateName: GATE_NAMES[pg] },
      design:       { gate: dg, line: dl, longitude: Math.round(dLon * 1000) / 1000, gateName: GATE_NAMES[dg] }
    });
  }

  // ─── CHANNEL & CENTER ANALYSIS ───
  const centerDef = {};
  Object.keys(CENTER_GATES).forEach(c => { centerDef[c] = 'undefined'; });

  const activeChannels = [];

  for (const [g1, g2] of UNIQUE_CHANNELS) {
    const p1 = pGates.has(g1), d1 = dGates.has(g1);
    const p2 = pGates.has(g2), d2 = dGates.has(g2);
    const active1 = p1 || d1;
    const active2 = p2 || d2;

    if (active1 && active2) {
      const c1 = GATE_CENTER[g1];
      const c2 = GATE_CENTER[g2];
      const byP = (p1 || p2) && !(d1 || d2);
      const byD = (d1 || d2) && !(p1 || p2);
      const both = !byP && !byD;
      const type = byP ? 'personality' : byD ? 'design' : 'both';

      activeChannels.push({ gates: [g1, g2], c1, c2, type, byP, byD, both });

      // Define both centers
      for (const c of [c1, c2]) {
        if (!c) continue;
        if (centerDef[c] === 'undefined') centerDef[c] = type;
        else if (centerDef[c] !== type) centerDef[c] = 'both';
      }
    }
  }

  // ─── TYPE DETERMINATION ───
  const sacral  = centerDef.Sacral  !== 'undefined';
  const throat  = centerDef.Throat  !== 'undefined';
  const solar   = centerDef.Solar   !== 'undefined';
  const will    = centerDef.Will    !== 'undefined';
  const spleen  = centerDef.Spleen  !== 'undefined';
  const root    = centerDef.Root    !== 'undefined';
  const g       = centerDef.G       !== 'undefined';

  const definedCenters = Object.entries(centerDef).filter(([,v]) => v !== 'undefined').map(([k]) => k);
  const undefinedCenters = Object.entries(centerDef).filter(([,v]) => v === 'undefined').map(([k]) => k);

  // Check if a motor connects to Throat (directly or via defined centers path)
  function motorToThroat() {
    // Build adjacency from active channels
    const adj = {};
    for (const { c1, c2 } of activeChannels) {
      if (!adj[c1]) adj[c1] = new Set();
      if (!adj[c2]) adj[c2] = new Set();
      adj[c1].add(c2);
      adj[c2].add(c1);
    }
    // BFS from each motor to Throat
    for (const motor of ['Sacral', 'Will', 'Solar', 'Root']) {
      if (centerDef[motor] === 'undefined') continue;
      const visited = new Set([motor]);
      const queue = [motor];
      while (queue.length) {
        const curr = queue.shift();
        if (curr === 'Throat') return true;
        for (const next of (adj[curr] || [])) {
          if (!visited.has(next) && centerDef[next] !== 'undefined') {
            visited.add(next);
            queue.push(next);
          }
        }
      }
    }
    return false;
  }

  let type, subtype = null;

  if (definedCenters.length === 0) {
    type = 'Reflector';
  } else if (sacral) {
    type = 'Generator';
    subtype = motorToThroat() ? 'Manifesting Generator' : 'Pure Generator';
  } else if (motorToThroat()) {
    type = 'Manifestor';
  } else {
    type = 'Projector';
  }

  // ─── AUTHORITY ───
  let authority = 'Mental';
  if (type === 'Reflector') {
    authority = 'Lunar';
  } else if (solar) {
    authority = 'Emotional';
  } else if (sacral) {
    authority = 'Sacral';
  } else if (spleen) {
    authority = 'Splenic';
  } else if (will) {
    authority = 'Ego';
  } else if (g && throat) {
    // G center connected to Throat = Self-Projected
    const gToThroat = activeChannels.some(ch =>
      (ch.c1 === 'G' && ch.c2 === 'Throat') ||
      (ch.c2 === 'G' && ch.c1 === 'Throat')
    );
    authority = gToThroat ? 'SelfProjected' : 'Mental';
  } else {
    authority = 'Mental';
  }

  // ─── PROFILE ───
  const pSunLine = lonToLine(pPos.sun);
  const dSunLine = lonToLine(dPos.sun);
  const profileKey = `${pSunLine}/${dSunLine}`;

  // ─── DEFINITION ───
  // Count connected components among defined centers
  function countComponents() {
    if (definedCenters.length === 0) return 0;
    const adj = {};
    for (const { c1, c2 } of activeChannels) {
      if (!adj[c1]) adj[c1] = [];
      if (!adj[c2]) adj[c2] = [];
      adj[c1].push(c2); adj[c2].push(c1);
    }
    const visited = new Set();
    let comps = 0;
    for (const c of definedCenters) {
      if (!visited.has(c)) {
        comps++;
        const queue = [c];
        while (queue.length) {
          const curr = queue.shift();
          visited.add(curr);
          for (const next of (adj[curr] || [])) {
            if (!visited.has(next) && centerDef[next] !== 'undefined') queue.push(next);
          }
        }
      }
    }
    return comps;
  }

  const comps = countComponents();
  const defLabels = ['Enkelvoudige definitie','Split definitie','Triple split definitie','Quadruple split definitie'];
  const definition = defLabels[Math.min(comps - 1, 3)] || 'Enkelvoudige definitie';

  // ─── INCARNATION CROSS ───
  const pSunGate   = lonToGate(pPos.sun);
  const pEarthGate = lonToGate(pPos.earth);
  const dSunGate   = lonToGate(dPos.sun);
  const dEarthGate = lonToGate(dPos.earth);
  const incarnationCross = `Poort ${pSunGate}.${pSunLine} / ${pEarthGate} — Poort ${dSunGate}.${dSunLine} / ${dEarthGate}`;

  const td = TYPE_DATA[type] || TYPE_DATA.Generator;
  const displayType = subtype ? `${type} — ${subtype}` : type;
  const strategy = subtype === 'Manifesting Generator'
    ? 'Wacht om te reageren, informeer dan'
    : td.strategy;

  return {
    // Type & profile
    type,
    subtype,
    displayType,
    strategy,
    authority,
    authorityNl: AUTHORITY_NAMES[authority] || authority,
    profile: profileKey,
    profileName: PROFILE_NAMES[profileKey] || profileKey,
    definition,
    incarnationCross,
    notself: td.notself,
    signature: td.signature,

    // Centers
    centerDefinitions: centerDef,
    definedCenters,
    undefinedCenters,

    // Channels
    activeChannels: activeChannels.map(ch => ({
      gates: ch.gates,
      center1: ch.c1,
      center2: ch.c2,
      type: ch.type
    })),

    // Gates
    personalityGates: [...pGates].sort((a,b)=>a-b),
    designGates: [...dGates].sort((a,b)=>a-b),

    // All planet activations
    activations
  };
}

module.exports = { calcHumanDesign };
