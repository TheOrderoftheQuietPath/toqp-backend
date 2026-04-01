import swisseph as swe
import math

HEAVENLY_STEMS = [
    {'id':'jia',  'nl':'Jiǎ',  'symbol':'甲', 'element':'Wood',  'polarity':'+', 'color':'#4a8a4a'},
    {'id':'yi',   'nl':'Yǐ',   'symbol':'乙', 'element':'Wood',  'polarity':'-', 'color':'#6aaa5a'},
    {'id':'bing', 'nl':'Bǐng', 'symbol':'丙', 'element':'Fire',  'polarity':'+', 'color':'#c05a3a'},
    {'id':'ding', 'nl':'Dīng', 'symbol':'丁', 'element':'Fire',  'polarity':'-', 'color':'#e07a5a'},
    {'id':'wu',   'nl':'Wù',   'symbol':'戊', 'element':'Earth', 'polarity':'+', 'color':'#a08040'},
    {'id':'ji',   'nl':'Jǐ',   'symbol':'己', 'element':'Earth', 'polarity':'-', 'color':'#c0a060'},
    {'id':'geng', 'nl':'Gēng', 'symbol':'庚', 'element':'Metal', 'polarity':'+', 'color':'#7090a0'},
    {'id':'xin',  'nl':'Xīn',  'symbol':'辛', 'element':'Metal', 'polarity':'-', 'color':'#90b0c0'},
    {'id':'ren',  'nl':'Rén',  'symbol':'壬', 'element':'Water', 'polarity':'+', 'color':'#3a6a9a'},
    {'id':'gui',  'nl':'Guǐ',  'symbol':'癸', 'element':'Water', 'polarity':'-', 'color':'#5a8aba'},
]

EARTHLY_BRANCHES = [
    {'nl':'Zǐ',   'symbol':'子', 'element':'Water', 'animal':'Rat',     'nl_animal':'Rat'},
    {'nl':'Chǒu', 'symbol':'丑', 'element':'Earth', 'animal':'Ox',      'nl_animal':'Os'},
    {'nl':'Yín',  'symbol':'寅', 'element':'Wood',  'animal':'Tiger',   'nl_animal':'Tijger'},
    {'nl':'Mǎo',  'symbol':'卯', 'element':'Wood',  'animal':'Rabbit',  'nl_animal':'Konijn'},
    {'nl':'Chén', 'symbol':'辰', 'element':'Earth', 'animal':'Dragon',  'nl_animal':'Draak'},
    {'nl':'Sì',   'symbol':'巳', 'element':'Fire',  'animal':'Snake',   'nl_animal':'Slang'},
    {'nl':'Wǔ',   'symbol':'午', 'element':'Fire',  'animal':'Horse',   'nl_animal':'Paard'},
    {'nl':'Wèi',  'symbol':'未', 'element':'Earth', 'animal':'Goat',    'nl_animal':'Geit'},
    {'nl':'Shēn', 'symbol':'申', 'element':'Metal', 'animal':'Monkey',  'nl_animal':'Aap'},
    {'nl':'Yǒu',  'symbol':'酉', 'element':'Metal', 'animal':'Rooster', 'nl_animal':'Haan'},
    {'nl':'Xū',   'symbol':'戌', 'element':'Earth', 'animal':'Dog',     'nl_animal':'Hond'},
    {'nl':'Hài',  'symbol':'亥', 'element':'Water', 'animal':'Pig',     'nl_animal':'Varken'},
]

ELEMENT_NAMES = {
    'Wood':  {'nl':'Hout',   'en':'Wood',  'icon':'🌿', 'color':'#4a8a4a'},
    'Fire':  {'nl':'Vuur',   'en':'Fire',  'icon':'🔥', 'color':'#c05a3a'},
    'Earth': {'nl':'Aarde',  'en':'Earth', 'icon':'⛰',  'color':'#a08040'},
    'Metal': {'nl':'Metaal', 'en':'Metal', 'icon':'⚙',  'color':'#7090a0'},
    'Water': {'nl':'Water',  'en':'Water', 'icon':'💧', 'color':'#3a6a9a'},
}

# Month stem starts per year stem group
# 甲己→丙(2), 乙庚→戊(4), 丙辛→庚(6), 丁壬→壬(8), 戊癸→甲(0)
MONTH_STEM_STARTS = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]

def get_stem(idx):
    return HEAVENLY_STEMS[((idx % 10) + 10) % 10]

def get_branch(idx):
    return EARTHLY_BRANCHES[((idx % 12) + 12) % 12]

def get_year_pillar(year):
    return {'stem': get_stem((year - 4) % 10), 'branch': get_branch((year - 4) % 12)}

def get_month_pillar(year, month):
    year_stem_idx = ((year - 4) % 10 + 10) % 10
    start_stem = MONTH_STEM_STARTS[year_stem_idx]
    stem_idx = (start_stem + month - 1) % 10
    branch_idx = (month + 1) % 12
    return {'stem': get_stem(stem_idx), 'branch': get_branch(branch_idx)}

def get_day_pillar(year, month, day):
    # Use Swiss Ephemeris Julian Day for accuracy
    jd = int(swe.julday(year, month, day, 0))
    stem_idx = (jd + 6) % 10
    branch_idx = (jd + 6) % 12
    return {'stem': get_stem(stem_idx), 'branch': get_branch(branch_idx)}

def get_true_solar_hour(clock_hour, clock_minute, longitude, tz_offset):
    """True Solar Time based on birth longitude."""
    std_meridian = tz_offset * 15
    correction_minutes = (longitude - std_meridian) * 4
    total_minutes = clock_hour * 60 + clock_minute + correction_minutes
    return (total_minutes / 60) % 24

def get_hour_pillar(day_stem_idx, solar_hour):
    hour_branch_idx = int(((solar_hour + 1) % 24) / 2)
    hour_stem_idx = (day_stem_idx % 5 * 2 + hour_branch_idx) % 10
    return {'stem': get_stem(hour_stem_idx), 'branch': get_branch(hour_branch_idx)}

def count_elements(pillars):
    counts = {'Wood': 0, 'Fire': 0, 'Earth': 0, 'Metal': 0, 'Water': 0}
    for p in pillars:
        se = p['stem']['element']
        be = p['branch']['element']
        if se in counts: counts[se] += 1
        if be in counts: counts[be] += 1
    return counts

def format_pillar(pillar, label):
    stem = pillar['stem']
    branch = pillar['branch']
    return {
        'label': label,
        'stem': {
            'symbol': stem['symbol'],
            'name': stem['nl'],
            'element': stem['element'],
            'elementNl': ELEMENT_NAMES[stem['element']]['nl'],
            'polarity': stem['polarity'],
            'color': stem['color']
        },
        'branch': {
            'symbol': branch['symbol'],
            'name': branch['nl'],
            'animal': branch['nl_animal'],
            'element': branch['element'],
            'elementNl': ELEMENT_NAMES[branch['element']]['nl']
        }
    }

def calc_bazi(data):
    year = int(data['year'])
    month = int(data['month'])
    day = int(data['day'])
    hour = int(data.get('hour', 12))
    minute = int(data.get('minute', 0))
    lon = float(data.get('lon', 4.45))
    tz = float(data.get('tz', 1))

    year_pillar  = get_year_pillar(year)
    month_pillar = get_month_pillar(year, month)
    day_pillar   = get_day_pillar(year, month, day)

    solar_hour = get_true_solar_hour(hour, minute, lon, tz)
    day_stem_idx = HEAVENLY_STEMS.index(day_pillar['stem'])
    hour_pillar  = get_hour_pillar(day_stem_idx, solar_hour)

    pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]
    element_counts = count_elements(pillars)

    # Day master analysis
    dm_el = day_pillar['stem']['element']
    produces = {'Wood':'Fire','Fire':'Earth','Earth':'Metal','Metal':'Water','Water':'Wood'}
    supported_by = {'Wood':'Water','Fire':'Wood','Earth':'Fire','Metal':'Earth','Water':'Metal'}
    total = sum(element_counts.values())
    strength = (element_counts.get(dm_el, 0) + element_counts.get(supported_by[dm_el], 0)) / total if total else 0

    day_master = {
        'element': dm_el,
        'elementNl': ELEMENT_NAMES[dm_el]['nl'],
        'polarity': day_pillar['stem']['polarity'],
        'isStrong': strength > 0.35,
        'produces': produces[dm_el],
        'supportedBy': supported_by[dm_el]
    }

    dominant = max(element_counts, key=element_counts.get)

    return {
        'yearPillar':  format_pillar(year_pillar,  'Jaar Pilaar'),
        'monthPillar': format_pillar(month_pillar, 'Maand Pilaar'),
        'dayPillar':   format_pillar(day_pillar,   'Dag Pilaar'),
        'hourPillar':  format_pillar(hour_pillar,  'Uur Pilaar'),
        'elementCounts': element_counts,
        'elementDetails': {k: {'count': v, **ELEMENT_NAMES[k]} for k, v in element_counts.items()},
        'dayMaster': day_master,
        'dominantElement': dominant
    }
