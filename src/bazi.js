'use strict';
const { julianDay: jdFromEph } = require('./ephemeris');

// ═══════════════════════════════════════════════
// BAZI — FOUR PILLARS OF DESTINY
// Corrections:
// 1. Month stem uses correct formula per year stem group
// 2. Hour pillar uses True Solar Time (not clock time)
// ═══════════════════════════════════════════════

const HEAVENLY_STEMS = [
  { id:'jia',  nl:'Jiǎ',  symbol:'甲', element:'Wood',  polarity:'+', color:'#4a8a4a' },
  { id:'yi',   nl:'Yǐ',   symbol:'乙', element:'Wood',  polarity:'-', color:'#6aaa5a' },
  { id:'bing', nl:'Bǐng', symbol:'丙', element:'Fire',  polarity:'+', color:'#c05a3a' },
  { id:'ding', nl:'Dīng', symbol:'丁', element:'Fire',  polarity:'-', color:'#e07a5a' },
  { id:'wu',   nl:'Wù',   symbol:'戊', element:'Earth', polarity:'+', color:'#a08040' },
  { id:'ji',   nl:'Jǐ',   symbol:'己', element:'Earth', polarity:'-', color:'#c0a060' },
  { id:'geng', nl:'Gēng', symbol:'庚', element:'Metal', polarity:'+', color:'#7090a0' },
  { id:'xin',  nl:'Xīn',  symbol:'辛', element:'Metal', polarity:'-', color:'#90b0c0' },
  { id:'ren',  nl:'Rén',  symbol:'壬', element:'Water', polarity:'+', color:'#3a6a9a' },
  { id:'gui',  nl:'Guǐ',  symbol:'癸', element:'Water', polarity:'-', color:'#5a8aba' }
];

const EARTHLY_BRANCHES = [
  { id:'zi',   nl:'Zǐ',   symbol:'子', element:'Water', animal:'Rat',     nl_animal:'Rat',     hours:[23,1]  },
  { id:'chou', nl:'Chǒu', symbol:'丑', element:'Earth', animal:'Ox',      nl_animal:'Os',      hours:[1,3]   },
  { id:'yin',  nl:'Yín',  symbol:'寅', element:'Wood',  animal:'Tiger',   nl_animal:'Tijger',  hours:[3,5]   },
  { id:'mao',  nl:'Mǎo',  symbol:'卯', element:'Wood',  animal:'Rabbit',  nl_animal:'Konijn',  hours:[5,7]   },
  { id:'chen', nl:'Chén', symbol:'辰', element:'Earth', animal:'Dragon',  nl_animal:'Draak',   hours:[7,9]   },
  { id:'si',   nl:'Sì',   symbol:'巳', element:'Fire',  animal:'Snake',   nl_animal:'Slang',   hours:[9,11]  },
  { id:'wu2',  nl:'Wǔ',   symbol:'午', element:'Fire',  animal:'Horse',   nl_animal:'Paard',   hours:[11,13] },
  { id:'wei',  nl:'Wèi',  symbol:'未', element:'Earth', animal:'Goat',    nl_animal:'Geit',    hours:[13,15] },
  { id:'shen', nl:'Shēn', symbol:'申', element:'Metal', animal:'Monkey',  nl_animal:'Aap',     hours:[15,17] },
  { id:'you',  nl:'Yǒu',  symbol:'酉', element:'Metal', animal:'Rooster', nl_animal:'Haan',    hours:[17,19] },
  { id:'xu',   nl:'Xū',   symbol:'戌', element:'Earth', animal:'Dog',     nl_animal:'Hond',    hours:[19,21] },
  { id:'hai',  nl:'Hài',  symbol:'亥', element:'Water', animal:'Pig',     nl_animal:'Varken',  hours:[21,23] }
];

const ELEMENT_NAMES = {
  Wood:  { nl:'Hout',   en:'Wood',  icon:'🌿', color:'#4a8a4a' },
  Fire:  { nl:'Vuur',   en:'Fire',  icon:'🔥', color:'#c05a3a' },
  Earth: { nl:'Aarde',  en:'Earth', icon:'⛰',  color:'#a08040' },
  Metal: { nl:'Metaal', en:'Metal', icon:'⚙',  color:'#7090a0' },
  Water: { nl:'Water',  en:'Water', icon:'💧', color:'#3a6a9a' }
};

function getStem(index) {
  return HEAVENLY_STEMS[((index % 10) + 10) % 10];
}

function getBranch(index) {
  return EARTHLY_BRANCHES[((index % 12) + 12) % 12];
}

// ─── YEAR PILLAR ───
function getYearPillar(year) {
  return {
    stem: getStem((year - 4) % 10),
    branch: getBranch((year - 4) % 12)
  };
}

// ─── MONTH PILLAR ───
// Correct formula: month stem depends on year stem group
// 甲己: starts 丙(2) | 乙庚: starts 戊(4) | 丙辛: starts 庚(6)
// 丁壬: starts 壬(8) | 戊癸: starts 甲(0)
const MONTH_STEM_STARTS = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0];

function getMonthPillar(year, month) {
  const yearStemIdx = ((year - 4) % 10 + 10) % 10;
  const startStem = MONTH_STEM_STARTS[yearStemIdx];
  const stemIdx = (startStem + month - 1) % 10;
  const branchIdx = (month + 1) % 12;
  return { stem: getStem(stemIdx), branch: getBranch(branchIdx) };
}

// ─── DAY PILLAR ───
function getJulianDay(year, month, day) {
  return Math.floor(jdFromEph(year, month, day, 12));
}

function getDayPillar(year, month, day) {
  const jd = getJulianDay(year, month, day);
  return { stem: getStem((jd + 6) % 10), branch: getBranch((jd + 6) % 12) };
}

// ─── HOUR PILLAR — True Solar Time ───
// True Solar Time = clock time - (timezone meridian - birth longitude) × 4 min/°
// This is essential for accurate hour pillar in BaZi
function getTrueSolarHour(clockHour, clockMinute, longitude, tzOffset) {
  const stdMeridian = tzOffset * 15;
  const correctionMinutes = (longitude - stdMeridian) * 4;
  const totalMinutes = clockHour * 60 + (clockMinute || 0) + correctionMinutes;
  return ((totalMinutes / 60) % 24 + 24) % 24;
}

function getHourPillar(dayStemIdx, clockHour, clockMinute, longitude, tzOffset) {
  const solarHour = getTrueSolarHour(clockHour, clockMinute || 0, longitude || 4.45, tzOffset || 1);
  const hourBranchIdx = Math.floor(((solarHour + 1) % 24) / 2);
  const hourStemIdx = (dayStemIdx % 5 * 2 + hourBranchIdx) % 10;
  return { stem: getStem(hourStemIdx), branch: getBranch(hourBranchIdx) };
}

// ─── ELEMENT ANALYSIS ───
function countElements(pillars) {
  const counts = { Wood: 0, Fire: 0, Earth: 0, Metal: 0, Water: 0 };
  pillars.forEach(p => {
    if (p.stem?.element) counts[p.stem.element]++;
    if (p.branch?.element) counts[p.branch.element]++;
  });
  return counts;
}

function analyzeDayMaster(dayPillar, elementCounts) {
  const el = dayPillar.stem.element;
  const produces = { Wood:'Fire', Fire:'Earth', Earth:'Metal', Metal:'Water', Water:'Wood' };
  const supportedBy = { Wood:'Water', Fire:'Wood', Earth:'Fire', Metal:'Earth', Water:'Metal' };
  const totalElements = Object.values(elementCounts).reduce((a, b) => a + b, 0);
  const dmCount = elementCounts[el] || 0;
  const supportCount = elementCounts[supportedBy[el]] || 0;
  const strength = totalElements > 0 ? (dmCount + supportCount) / totalElements : 0;
  return {
    element: el,
    elementNl: ELEMENT_NAMES[el]?.nl,
    polarity: dayPillar.stem.polarity,
    isStrong: strength > 0.35,
    produces: produces[el],
    supportedBy: supportedBy[el]
  };
}

// ─── MAIN EXPORT ───
function calcBazi({ day, month, year, hour, minute, lon, tz }) {
  const yearPillar  = getYearPillar(year);
  const monthPillar = getMonthPillar(year, month);
  const dayPillar   = getDayPillar(year, month, day);
  const dayStemIdx  = HEAVENLY_STEMS.indexOf(dayPillar.stem);
  const hourPillar  = getHourPillar(dayStemIdx, hour || 12, minute || 0, lon || 4.45, tz || 1);

  const pillars = [yearPillar, monthPillar, dayPillar, hourPillar];
  const elementCounts = countElements(pillars);
  const dayMaster = analyzeDayMaster(dayPillar, elementCounts);

  const format = (pillar, label) => ({
    label,
    stem: {
      symbol:    pillar.stem.symbol,
      name:      pillar.stem.nl,
      element:   pillar.stem.element,
      elementNl: ELEMENT_NAMES[pillar.stem.element]?.nl,
      polarity:  pillar.stem.polarity,
      color:     pillar.stem.color
    },
    branch: {
      symbol:    pillar.branch.symbol,
      name:      pillar.branch.nl,
      animal:    pillar.branch.nl_animal,
      element:   pillar.branch.element,
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
