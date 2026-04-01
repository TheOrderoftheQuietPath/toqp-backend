import swisseph as swe
import math
from datetime import datetime, timezone

# HD wheel: gate 41 starts at 302° tropical longitude (verified)
HD_OFFSET = 302.0
GATE_WHEEL = [
    41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,
    27,24,2,23,8,20,16,35,45,12,15,52,39,53,62,56,
    31,33,7,4,29,59,40,64,47,6,46,18,48,57,32,50,
    28,44,1,43,14,34,9,5,26,11,10,58,38,54,61,60
]

GATE_NAMES = {
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
}

PLANET_NAMES = {
    swe.SUN:'Zon', swe.MOON:'Maan', swe.MERCURY:'Mercurius', swe.VENUS:'Venus',
    swe.MARS:'Mars', swe.JUPITER:'Jupiter', swe.SATURN:'Saturnus',
    swe.URANUS:'Uranus', swe.NEPTUNE:'Neptunus', swe.PLUTO:'Pluto',
    swe.TRUE_NODE:'Noordknoop', swe.CHIRON:'Chiron'
}

PLANET_ICONS = {
    swe.SUN:'☀', swe.MOON:'☽', swe.MERCURY:'☿', swe.VENUS:'♀',
    swe.MARS:'♂', swe.JUPITER:'♃', swe.SATURN:'♄',
    swe.URANUS:'♅', swe.NEPTUNE:'♆', swe.PLUTO:'♇',
    swe.TRUE_NODE:'☊', swe.CHIRON:'⚷'
}

PLANET_KEYS = [swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
               swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO,
               swe.TRUE_NODE, swe.CHIRON]

# All HD channels (deduplicated)
ALL_CHANNELS = [
    (1,8),(2,14),(3,60),(4,63),(5,15),(6,59),(7,31),(9,52),(10,20),(10,34),(10,57),
    (11,56),(12,22),(13,33),(14,2),(15,5),(16,48),(17,62),(18,58),(19,49),(20,57),
    (21,45),(22,12),(23,43),(24,61),(25,51),(26,44),(27,50),(28,38),(29,46),(30,41),(31,7),
    (32,54),(33,13),(34,57),(35,36),(37,40),(38,28),(39,55),(40,37),
    (41,30),(42,53),(43,23),(44,26),(45,21),(46,29),(47,64),(48,16),(49,19),(50,27),(51,25),
    (52,9),(53,42),(54,32),(55,39),(56,11),(58,18),(59,6),(60,3),
    (61,24),(62,17),(63,4),(64,47)
]

# Deduplicate channels
seen = set()
UNIQUE_CHANNELS = []
for (a, b) in ALL_CHANNELS:
    key = (min(a,b), max(a,b))
    if key not in seen:
        seen.add(key)
        UNIQUE_CHANNELS.append((a, b))

CENTER_GATES = {
    'Head':   [64, 61, 63],
    'Ajna':   [47, 24, 4, 17, 43, 11],
    'Throat': [62, 23, 56, 35, 12, 45, 33, 8, 31, 20, 16],
    'G':      [1, 13, 25, 46, 2, 15, 10, 7],
    'Will':   [21, 40, 26, 51],
    'Solar':  [36, 22, 37, 30, 55, 49, 6, 59, 27, 50],
    'Sacral': [5, 14, 29, 59, 9, 3, 42, 27, 34],
    'Spleen': [48, 57, 44, 50, 32, 28, 18],
    'Root':   [58, 38, 54, 53, 60, 52, 19, 39, 41]
}

PROFILE_NAMES = {
    '1/3':'Onderzoeker / Martelaar','1/4':'Onderzoeker / Opportunist',
    '2/4':'Kluizenaar / Opportunist','2/5':'Kluizenaar / Ketter',
    '3/5':'Martelaar / Ketter','3/6':'Martelaar / Rolmodel',
    '4/6':'Opportunist / Rolmodel','4/1':'Opportunist / Onderzoeker',
    '5/1':'Ketter / Onderzoeker','5/2':'Ketter / Kluizenaar',
    '6/2':'Rolmodel / Kluizenaar','6/3':'Rolmodel / Martelaar'
}

TYPE_DATA = {
    'Generator':  {'strategy':'Wacht om te reageren','notself':'Frustratie','signature':'Voldoening'},
    'Manifestor': {'strategy':'Informeer voor je handelt','notself':'Woede','signature':'Vrede'},
    'Projector':  {'strategy':'Wacht op de uitnodiging','notself':'Bitterheid','signature':'Succes'},
    'Reflector':  {'strategy':'Wacht een maanmaand','notself':'Teleurstelling','signature':'Verrassing'}
}

AUTHORITY_NAMES = {
    'Emotional':     'Emotionele autoriteit',
    'Sacral':        'Sacrale autoriteit',
    'Splenic':       'Miltautoriteit',
    'Ego':           'Egoautoriteit',
    'SelfProjected': 'Zelf-geprojecteerde autoriteit',
    'Mental':        'Mentale autoriteit',
    'Lunar':         'Lunaire autoriteit'
}


def lon_to_gate(lon):
    n = ((lon - HD_OFFSET) % 360 + 360) % 360
    return GATE_WHEEL[int(n / (360 / 64))]


def lon_to_line(lon):
    n = ((lon - HD_OFFSET) % 360 + 360) % 360
    gate_size = 360 / 64
    return int((n % gate_size) / (gate_size / 6)) + 1


def get_julian_day(year, month, day, hour_utc):
    """Convert to Julian Day Number."""
    jd = swe.julday(year, month, day, hour_utc)
    return jd


def get_planet_longitude(jd, planet_id):
    """Get tropical longitude using Swiss Ephemeris."""
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result, ret_flags = swe.calc_ut(jd, planet_id, flags)
    return result[0]  # longitude in degrees


def get_all_longitudes(jd):
    """Get all planet longitudes for a given JD."""
    positions = {}
    for planet_id in PLANET_KEYS:
        try:
            lon = get_planet_longitude(jd, planet_id)
            positions[planet_id] = lon
        except Exception:
            positions[planet_id] = 0.0
    # Earth = Sun + 180°
    positions['earth'] = (positions[swe.SUN] + 180) % 360
    return positions


def find_design_jd(birth_jd):
    """Find JD when sun was exactly 88° before birth sun (binary search)."""
    birth_sun = get_planet_longitude(birth_jd, swe.SUN)
    target = (birth_sun - 88 + 360) % 360
    lo, hi = birth_jd - 100, birth_jd - 80
    for _ in range(60):
        mid = (lo + hi) / 2
        s = get_planet_longitude(mid, swe.SUN)
        diff = s - target
        if diff > 180: diff -= 360
        if diff < -180: diff += 360
        if diff > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def gate_to_center(gate):
    for center, gates in CENTER_GATES.items():
        if gate in gates:
            return center
    return None


def get_connected_components(center_def, active_channels):
    """Count connected components among defined centers."""
    defined = [c for c, v in center_def.items() if v != 'undefined']
    if not defined:
        return 0
    visited = set()
    components = 0

    def dfs(center):
        visited.add(center)
        for ch in active_channels:
            c1, c2 = ch['c1'], ch['c2']
            if c1 == center and c2 not in visited and center_def.get(c2, 'undefined') != 'undefined':
                dfs(c2)
            if c2 == center and c1 not in visited and center_def.get(c1, 'undefined') != 'undefined':
                dfs(c1)

    for c in defined:
        if c not in visited:
            components += 1
            dfs(c)
    return components


def calc_human_design(data):
    year = int(data['year'])
    month = int(data['month'])
    day = int(data['day'])
    hour = int(data.get('hour', 0))
    minute = int(data.get('minute', 0))
    tz = float(data.get('tz', 1))

    # Convert to UTC
    utc_hour = hour - tz + minute / 60
    birth_jd = get_julian_day(year, month, day, utc_hour)
    design_jd = find_design_jd(birth_jd)

    # Get all planet positions
    p_lons = get_all_longitudes(birth_jd)
    d_lons = get_all_longitudes(design_jd)

    # Convert to gates and lines
    p_gates = {}
    d_gates = {}
    p_lines = {}
    d_lines = {}

    all_planet_ids = PLANET_KEYS + ['earth']
    for pid in all_planet_ids:
        p_gates[pid] = lon_to_gate(p_lons[pid])
        d_gates[pid] = lon_to_gate(d_lons[pid])
        p_lines[pid] = lon_to_line(p_lons[pid])
        d_lines[pid] = lon_to_line(d_lons[pid])

    personality_gates = set(p_gates.values())
    design_gates = set(d_gates.values())
    all_gates = personality_gates | design_gates

    # Determine center definitions
    center_def = {c: 'undefined' for c in CENTER_GATES}
    active_channels = []

    for (g1, g2) in UNIQUE_CHANNELS:
        p1 = g1 in personality_gates
        d1 = g1 in design_gates
        p2 = g2 in personality_gates
        d2 = g2 in design_gates
        if (p1 or d1) and (p2 or d2):
            c1 = gate_to_center(g1)
            c2 = gate_to_center(g2)
            by_p = (p1 or p2) and not (d1 or d2)
            by_d = (d1 or d2) and not (p1 or p2)
            ch_type = 'personality' if by_p else ('design' if by_d else 'both')
            active_channels.append({'g1': g1, 'g2': g2, 'c1': c1, 'c2': c2, 'type': ch_type})
            color = ch_type
            if c1:
                center_def[c1] = color if center_def[c1] == 'undefined' else 'both'
            if c2:
                center_def[c2] = color if center_def[c2] == 'undefined' else 'both'

    # Determine Type
    sacral = center_def['Sacral'] != 'undefined'
    throat = center_def['Throat'] != 'undefined'
    solar = center_def['Solar'] != 'undefined'
    will = center_def['Will'] != 'undefined'
    spleen = center_def['Spleen'] != 'undefined'
    g = center_def['G'] != 'undefined'
    defined_count = sum(1 for v in center_def.values() if v != 'undefined')

    if defined_count == 0:
        hd_type = 'Reflector'
        subtype = None
    elif sacral:
        motors = ['Will', 'Solar', 'Sacral']
        motor_to_throat = any(
            (ch['c1'] in motors and ch['c2'] == 'Throat') or
            (ch['c2'] in motors and ch['c1'] == 'Throat')
            for ch in active_channels
        )
        hd_type = 'Generator'
        subtype = 'Manifesting Generator' if motor_to_throat else 'Pure Generator'
    else:
        motors = ['Will', 'Solar', 'Root']
        motor_to_throat = any(
            (ch['c1'] in motors and ch['c2'] == 'Throat') or
            (ch['c2'] in motors and ch['c1'] == 'Throat')
            for ch in active_channels
        )
        hd_type = 'Manifestor' if motor_to_throat else 'Projector'
        subtype = None

    # Determine Authority
    if hd_type == 'Reflector':
        authority = 'Lunar'
    elif solar:
        authority = 'Emotional'
    elif sacral:
        authority = 'Sacral'
    elif spleen:
        authority = 'Splenic'
    elif will:
        authority = 'Ego'
    elif g and throat:
        g_to_throat = any(
            (ch['c1'] == 'G' and ch['c2'] == 'Throat') or
            (ch['c2'] == 'G' and ch['c1'] == 'Throat')
            for ch in active_channels
        )
        authority = 'SelfProjected' if g_to_throat else 'Mental'
    else:
        authority = 'Mental'

    # Profile
    p_sun_line = p_lines[swe.SUN]
    d_sun_line = d_lines[swe.SUN]
    profile_key = f"{p_sun_line}/{d_sun_line}"

    # Definition
    comps = get_connected_components(center_def, active_channels)
    def_labels = ['', 'Enkelvoudige definitie', 'Split definitie',
                  'Triple split definitie', 'Quadruple split definitie']
    definition = def_labels[min(comps, 4)] if comps > 0 else 'Geen definitie'

    # Incarnation cross
    p_sun_gate = p_gates[swe.SUN]
    p_earth_gate = p_gates['earth']
    d_sun_gate = d_gates[swe.SUN]
    d_earth_gate = d_gates['earth']
    incarnation_cross = f"Poort {p_sun_gate}.{p_lines[swe.SUN]} — Poort {p_earth_gate}.{p_lines['earth']} / Poort {d_sun_gate}.{d_lines[swe.SUN]} — Poort {d_earth_gate}.{d_lines['earth']}"

    # Build activations list
    td = TYPE_DATA.get(hd_type, TYPE_DATA['Generator'])
    strategy = 'Wacht om te reageren, informeer dan' if subtype == 'Manifesting Generator' else td['strategy']

    activations = []
    # Sun first
    activations.append({
        'planet': 'Zon', 'icon': '☀', 'key': 'sun',
        'personality': {'gate': p_gates[swe.SUN], 'line': p_lines[swe.SUN],
                        'longitude': round(p_lons[swe.SUN], 3),
                        'gateName': GATE_NAMES.get(p_gates[swe.SUN], '')},
        'design': {'gate': d_gates[swe.SUN], 'line': d_lines[swe.SUN],
                   'longitude': round(d_lons[swe.SUN], 3),
                   'gateName': GATE_NAMES.get(d_gates[swe.SUN], '')}
    })
    # Earth
    activations.append({
        'planet': 'Aarde', 'icon': '⊕', 'key': 'earth',
        'personality': {'gate': p_gates['earth'], 'line': p_lines['earth'],
                        'longitude': round(p_lons['earth'], 3),
                        'gateName': GATE_NAMES.get(p_gates['earth'], '')},
        'design': {'gate': d_gates['earth'], 'line': d_lines['earth'],
                   'longitude': round(d_lons['earth'], 3),
                   'gateName': GATE_NAMES.get(d_gates['earth'], '')}
    })
    # Other planets
    for pid in PLANET_KEYS:
        if pid == swe.SUN:
            continue
        activations.append({
            'planet': PLANET_NAMES[pid], 'icon': PLANET_ICONS[pid], 'key': str(pid),
            'personality': {'gate': p_gates[pid], 'line': p_lines[pid],
                            'longitude': round(p_lons[pid], 3),
                            'gateName': GATE_NAMES.get(p_gates[pid], '')},
            'design': {'gate': d_gates[pid], 'line': d_lines[pid],
                       'longitude': round(d_lons[pid], 3),
                       'gateName': GATE_NAMES.get(d_gates[pid], '')}
        })

    display_type = f"{hd_type} ({subtype})" if subtype else hd_type

    return {
        'type': hd_type,
        'subtype': subtype,
        'displayType': display_type,
        'strategy': strategy,
        'authority': authority,
        'authorityNl': AUTHORITY_NAMES.get(authority, authority),
        'profile': profile_key,
        'profileName': PROFILE_NAMES.get(profile_key, profile_key),
        'definition': definition,
        'incarnationCross': incarnation_cross,
        'notself': td['notself'],
        'signature': td['signature'],
        'centerDefinitions': center_def,
        'definedCenters': [c for c, v in center_def.items() if v != 'undefined'],
        'undefinedCenters': [c for c, v in center_def.items() if v == 'undefined'],
        'activeChannels': [{'gates': [ch['g1'], ch['g2']], 'type': ch['type'], 'centers': [ch['c1'], ch['c2']]} for ch in active_channels],
        'personalityGates': sorted(list(personality_gates)),
        'designGates': sorted(list(design_gates)),
        'activations': activations,
        'accuracy': 'Swiss Ephemeris (pyswisseph)'
    }
