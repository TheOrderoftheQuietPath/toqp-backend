// ═══════════════════════════════════════════════
// BAZI — FOUR PILLARS OF DESTINY
// Chinese Astrology calculation
// ═══════════════════════════════════════════════

const HEAVENLY_STEMS = [
  { id: 'jia',  nl: 'Jiǎ',  en: 'Jiǎ',  element: 'Wood',  polarity: '+', symbol: '甲', color: '#4a8a4a' },
  { id: 'yi',   nl: 'Yǐ',   en: 'Yǐ',   element: 'Wood',  polarity: '-', symbol: '乙', color: '#6aaa5a' },
  { id: 'bing', nl: 'Bǐng', en: 'Bǐng', element: 'Fire',  polarity: '+', symbol: '丙', color: '#c05a3a' },
  { id: 'ding', nl: 'Dīng', en: 'Dīng', element: 'Fire',  polarity: '-', symbol: '丁', color: '#e07a5a' },
  { id: 'wu',   nl: 'Wù',   en: 'Wù',   element: 'Earth', polarity: '+', symbol: '戊', color: '#a08040' },
  { id: 'ji',   nl: 'Jǐ',   en: 'Jǐ',   element: 'Earth', polarity: '-', symbol: '己', color: '#c0a060' },
  { id: 'geng', nl: 'Gēng', en: 'Gēng', element: 'Metal', polarity: '+', symbol: '庚', color: '#7090a0' },
  { id: 'xin',  nl: 'Xīn',  en: 'Xīn',  element: 'Metal', polarity: '-', symbol: '辛', color: '#90b0c0' },
  { id: 'ren',  nl: 'Rén',  en: 'Rén',  element: 'Water', polarity: '+', symbol: '壬', color: '#3a6a9a' },
  { id: 'gui',  nl: 'Guǐ', en: 'Guǐ',  element: 'Water', polarity: '-', symbol: '癸', color: '#5a8aba' }
];

const EARTHLY_BRANCHES = [
  { id: 'zi',   nl: 'Zǐ',   en: 'Zǐ',   animal: 'Rat',      nl_animal: 'Rat',      symbol: '子', element: 'Water', hours: [23,1]  },
  { id: 'chou', nl: 'Chǒu', en: 'Chǒu', animal: 'Ox',       nl_animal: 'Os',       symbol: '丑', element: 'Earth', hours: [1,3]   },
  { id: 'yin',  nl: 'Yín',  en: 'Yín',  animal: 'Tiger',    nl_animal: 'Tijger',   symbol: '寅', element: 'Wood',  hours: [3,5]   },
  { id: 'mao',  nl: 'Mǎo',  en: 'Mǎo',  animal: 'Rabbit',   nl_animal: 'Konijn',   symbol: '卯', element: 'Wood',  hours: [5,7]   },
  { id: 'chen', nl: 'Chén', en: 'Chén', animal: 'Dragon',   nl_animal: 'Draak',    symbol: '辰', element: 'Earth', hours: [7,9]   },
  { id: 'si',   nl: 'Sì',   en: 'Sì',   animal: 'Snake',    nl_animal: 'Slang',    symbol: '巳', element: 'Fire',  hours: [9,11]  },
  { id: 'wu2',  nl: 'Wǔ',   en: 'Wǔ',   animal: 'Horse',    nl_animal: 'Paard',    symbol: '午', element: 'Fire',  hours: [11,13] },
  { id: 'wei',  nl: 'Wèi',  en: 'Wèi',  animal: 'Goat',     nl_animal: 'Geit',     symbol: '未', element: 'Earth', hours: [13,15] },
  { id: 'shen', nl: 'Shēn', en: 'Shēn', animal: 'Monkey',   nl_animal: 'Aap',      symbol: '申', element: 'Metal', hours: [15,17] },
  { id: 'you',  nl: 'Yǒu',  en: 'Yǒu',  animal: 'Rooster',  nl_animal: 'Haan',     symbol: '酉', element: 'Metal', hours: [17,19] },
  { id: 'xu',   nl: 'Xū',   en: 'Xū',   animal: 'Dog',      nl_animal: 'Hond',     symbol: '戌', element: 'Earth', hours: [19,21] },
  { id: 'hai',  nl: 'Hài',  en: 'Hài',  animal: 'Pig',      nl_animal: 'Varken',   symbol: '亥', element: 'Water', hours: [21,23] }
];

const ELEMENT_NAMES = {
  Wood:  { nl: 'Hout',   en: 'Wood',  icon: '🌿', color: '#4a8a4a' },
  Fire:  { nl: 'Vuur',   en: 'Fire',  icon: '🔥', color: '#c05a3a' },
  Earth: { nl: 'Aarde',  en: 'Earth', icon: '⛰',  color: '#a08040' },
  Metal: { nl: 'Metaal', en: 'Metal', icon: '⚙',  color: '#7090a0' },
  Water: { nl: 'Water',  en: 'Water', icon: '💧', color: '#3a6a9a' }
};

function getStem(index) {
  return HEAVENLY_STEMS[((index % 10) + 10) % 10];
}

function getBranch(index) {
  return EARTHLY_BRANCHES[((index % 12) + 12) % 12];
}

// Year pillar
function getYearPillar(year) {
  const stemIdx = (year - 4) % 10;
  const branchIdx = (year - 4) % 12;
  return { stem: getStem(stemIdx), branch: getBranch(branchIdx) };
}

// Month pillar (approximate — based on solar month)
function getMonthPillar(year, month) {
  const stemBase = ((year - 4) % 5) * 2;
  const stemIdx = (stemBase + month - 1) % 10;
  const branchIdx = (month + 1) % 12;
  return { stem: getStem(stemIdx), branch: getBranch(branchIdx) };
}

// Day pillar — accurate calculation using Julian Day Number
function getJulianDay(year, month, day) {
  if (month <= 2) { year--; month += 12; }
  const A = Math.floor(year / 100);
  const B = 2 - A + Math.floor(A / 4);
  return Math.floor(365.25 * (year + 4716)) + Math.floor(30.6001 * (month + 1)) + day + B - 1524;
}

function getDayPillar(year, month, day) {
  const jd = getJulianDay(year, month, day);
  const stemIdx = (jd + 6) % 10;
  const branchIdx = (jd + 6) % 12;
  return { stem: getStem(stemIdx), branch: getBranch(branchIdx) };
}

// Hour pillar
function getHourPillar(dayStемIdx, hour) {
  const hourBranchIdx = Math.floor(((hour + 1) % 24) / 2);
  const hourStemIdx = (dayStемIdx % 5 * 2 + hourBranchIdx) % 10;
  return { stem: getStem(hourStemIdx), branch: getBranch(hourBranchIdx) };
}

// Count elements across all pillars
function countElements(pillars) {
  const counts = { Wood: 0, Fire: 0, Earth: 0, Metal: 0, Water: 0 };
  pillars.forEach(p => {
    if (p.stem?.element) counts[p.stem.element]++;
    if (p.branch?.element) counts[p.branch.element]++;
  });
  return counts;
}

// Day master analysis
function analyzeDayMaster(dayPillar, elementCounts) {
  const dm = dayPillar.stem;
  const el = dm.element;

  // Producing cycle: Wood→Fire→Earth→Metal→Water→Wood
  const produces = { Wood: 'Fire', Fire: 'Earth', Earth: 'Metal', Metal: 'Water', Water: 'Wood' };
  // Controlling cycle: Wood→Earth→Water→Fire→Metal→Wood
  const controls = { Wood: 'Earth', Earth: 'Water', Water: 'Fire', Fire: 'Metal', Metal: 'Wood' };
  // What supports day master
  const supportedBy = { Wood: 'Water', Fire: 'Wood', Earth: 'Fire', Metal: 'Earth', Water: 'Metal' };

  const totalElements = Object.values(elementCounts).reduce((a, b) => a + b, 0);
  const dmCount = elementCounts[el] || 0;
  const supportCount = elementCounts[supportedBy[el]] || 0;
  const strength = (dmCount + supportCount) / totalElements;

  return {
    element: el,
    elementNl: ELEMENT_NAMES[el]?.nl,
    polarity: dm.polarity,
    isStrong: strength > 0.35,
    produces: produces[el],
    controls: controls[el],
    supportedBy: supportedBy[el]
  };
}

function calcBazi({ day, month, year, hour, minute }) {
  const yearPillar  = getYearPillar(year);
  const monthPillar = getMonthPillar(year, month);
  const dayPillar   = getDayPillar(year, month, day);
  const hourPillar  = getHourPillar(HEAVENLY_STEMS.indexOf(dayPillar.stem), hour);

  const pillars = [yearPillar, monthPillar, dayPillar, hourPillar];
  const elementCounts = countElements(pillars);
  const dayMaster = analyzeDayMaster(dayPillar, elementCounts);

  // Format for response
  const format = (pillar, label) => ({
    label,
    stem: {
      symbol: pillar.stem.symbol,
      name: pillar.stem.nl,
      element: pillar.stem.element,
      elementNl: ELEMENT_NAMES[pillar.stem.element]?.nl,
      polarity: pillar.stem.polarity,
      color: pillar.stem.color
    },
    branch: {
      symbol: pillar.branch.symbol,
      name: pillar.branch.nl,
      animal: pillar.branch.nl_animal,
      element: pillar.branch.element,
      elementNl: ELEMENT_NAMES[pillar.branch.element]?.nl
    }
  });

  return {
    yearPillar:  format(yearPillar,  'Jaar Pilaar'),
    monthPillar: format(monthPillar, 'Maand Pilaar'),
    dayPillar:   format(dayPillar,   'Dag Pilaar'),
    hourPillar:  format(hourPillar,  'Uur Pilaar'),
    elementCounts,
    elementDetails: Object.fromEntries(
      Object.entries(elementCounts).map(([k, v]) => [k, { count: v, ...ELEMENT_NAMES[k] }])
    ),
    dayMaster,
    dominantElement: Object.entries(elementCounts).sort((a, b) => b[1] - a[1])[0][0]
  };
}

module.exports = { calcBazi };
