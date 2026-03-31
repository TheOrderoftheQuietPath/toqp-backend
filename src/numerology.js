// ═══════════════════════════════════════════════
// NUMEROLOGY CALCULATIONS
// Pythagoras system — Life Path, Soul Urge,
// Personality, Destiny
// ═══════════════════════════════════════════════

const MASTER_NUMBERS = [11, 22, 33];

const NUM_NAMES = {
  1:  { nl: 'De Leider',          en: 'The Leader' },
  2:  { nl: 'De Diplomaat',       en: 'The Diplomat' },
  3:  { nl: 'De Creatieveling',   en: 'The Creative' },
  4:  { nl: 'De Bouwer',          en: 'The Builder' },
  5:  { nl: 'De Avonturier',      en: 'The Adventurer' },
  6:  { nl: 'De Verzorger',       en: 'The Nurturer' },
  7:  { nl: 'De Zoeker',          en: 'The Seeker' },
  8:  { nl: 'De Strateeg',        en: 'The Strategist' },
  9:  { nl: 'De Wijze',           en: 'The Wise One' },
  11: { nl: 'De Ingewijde',       en: 'The Initiate' },
  22: { nl: 'De Meesterbouwer',   en: 'The Master Builder' },
  33: { nl: 'De Meesterleraar',   en: 'The Master Teacher' }
};

function reduceNumber(n) {
  if (MASTER_NUMBERS.includes(n)) return n;
  while (n > 9) {
    n = String(n).split('').reduce((a, b) => a + parseInt(b), 0);
    if (MASTER_NUMBERS.includes(n)) return n;
  }
  return n;
}

function digitSum(str) {
  return str.split('').reduce((a, b) => {
    const d = parseInt(b);
    return isNaN(d) ? a : a + d;
  }, 0);
}

// Letter values A=1, B=2 ... Z=8 (Pythagorean)
const LETTER_VALUES = {
  a:1, b:2, c:3, d:4, e:5, f:6, g:7, h:8, i:9,
  j:1, k:2, l:3, m:4, n:5, o:6, p:7, q:8, r:9,
  s:1, t:2, u:3, v:4, w:5, x:6, y:7, z:8
};

const VOWELS = new Set(['a','e','i','o','u']);

function letterValue(char) {
  return LETTER_VALUES[char.toLowerCase()] || 0;
}

function calcLifePath(day, month, year) {
  const sum = digitSum(String(day)) + digitSum(String(month)) + digitSum(String(year));
  return reduceNumber(sum);
}

function calcSoulUrge(name) {
  if (!name) return null;
  const sum = name.toLowerCase().split('').reduce((a, c) => {
    return VOWELS.has(c) ? a + letterValue(c) : a;
  }, 0);
  return sum > 0 ? reduceNumber(sum) : null;
}

function calcPersonality(name) {
  if (!name) return null;
  const sum = name.toLowerCase().split('').reduce((a, c) => {
    return c.match(/[a-z]/) && !VOWELS.has(c) ? a + letterValue(c) : a;
  }, 0);
  return sum > 0 ? reduceNumber(sum) : null;
}

function calcDestiny(name) {
  if (!name) return null;
  const sum = name.toLowerCase().split('').reduce((a, c) => {
    return c.match(/[a-z]/) ? a + letterValue(c) : a;
  }, 0);
  return sum > 0 ? reduceNumber(sum) : null;
}

function calcBirthDay(day) {
  return reduceNumber(day);
}

function calcNumerology({ day, month, year, name }) {
  const lifePath = calcLifePath(day, month, year);
  const soulUrge = calcSoulUrge(name);
  const personality = calcPersonality(name);
  const destiny = calcDestiny(name);
  const birthday = calcBirthDay(day);

  return {
    lifePath,
    lifePathName: NUM_NAMES[lifePath] || null,
    soulUrge,
    soulUrgeName: soulUrge ? (NUM_NAMES[soulUrge] || null) : null,
    personality,
    personalityName: personality ? (NUM_NAMES[personality] || null) : null,
    destiny,
    destinyName: destiny ? (NUM_NAMES[destiny] || null) : null,
    birthday,
    birthdayName: NUM_NAMES[birthday] || null,
    isMasterNumber: MASTER_NUMBERS.includes(lifePath)
  };
}

module.exports = { calcNumerology };
