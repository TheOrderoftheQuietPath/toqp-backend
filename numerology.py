MASTER_NUMBERS = {11, 22, 33}

NUM_NAMES = {
    1:  {'nl':'De Leider',          'en':'The Leader'},
    2:  {'nl':'De Diplomaat',       'en':'The Diplomat'},
    3:  {'nl':'De Creatieveling',   'en':'The Creative'},
    4:  {'nl':'De Bouwer',          'en':'The Builder'},
    5:  {'nl':'De Avonturier',      'en':'The Adventurer'},
    6:  {'nl':'De Verzorger',       'en':'The Nurturer'},
    7:  {'nl':'De Zoeker',          'en':'The Seeker'},
    8:  {'nl':'De Strateeg',        'en':'The Strategist'},
    9:  {'nl':'De Wijze',           'en':'The Wise One'},
    11: {'nl':'De Ingewijde',       'en':'The Initiate'},
    22: {'nl':'De Meesterbouwer',   'en':'The Master Builder'},
    33: {'nl':'De Meesterleraar',   'en':'The Master Teacher'},
}

LETTER_VALUES = {
    'a':1,'b':2,'c':3,'d':4,'e':5,'f':6,'g':7,'h':8,'i':9,
    'j':1,'k':2,'l':3,'m':4,'n':5,'o':6,'p':7,'q':8,'r':9,
    's':1,'t':2,'u':3,'v':4,'w':5,'x':6,'y':7,'z':8
}
VOWELS = set('aeiou')

def reduce_num(n):
    if n in MASTER_NUMBERS:
        return n
    while n > 9:
        n = sum(int(d) for d in str(n))
        if n in MASTER_NUMBERS:
            return n
    return n

def digit_sum(s):
    return sum(int(c) for c in str(s) if c.isdigit())

def letter_value(c):
    return LETTER_VALUES.get(c.lower(), 0)

def calc_life_path(day, month, year):
    total = digit_sum(day) + digit_sum(month) + digit_sum(year)
    return reduce_num(total)

def calc_soul_urge(name):
    if not name:
        return None
    total = sum(letter_value(c) for c in name.lower() if c in VOWELS)
    return reduce_num(total) if total > 0 else None

def calc_personality(name):
    if not name:
        return None
    total = sum(letter_value(c) for c in name.lower() if c.isalpha() and c not in VOWELS)
    return reduce_num(total) if total > 0 else None

def calc_destiny(name):
    if not name:
        return None
    total = sum(letter_value(c) for c in name.lower() if c.isalpha())
    return reduce_num(total) if total > 0 else None

def calc_numerology(data):
    day = int(data['day'])
    month = int(data['month'])
    year = int(data['year'])
    firstname = data.get('firstname', '')
    lastname = data.get('lastname', '')
    name = f"{firstname} {lastname}".strip()

    lp = calc_life_path(day, month, year)
    su = calc_soul_urge(name)
    pers = calc_personality(name)
    dest = calc_destiny(name)
    bday = reduce_num(day)

    return {
        'lifePath': lp,
        'lifePathName': NUM_NAMES.get(lp),
        'soulUrge': su,
        'soulUrgeName': NUM_NAMES.get(su) if su else None,
        'personality': pers,
        'personalityName': NUM_NAMES.get(pers) if pers else None,
        'destiny': dest,
        'destinyName': NUM_NAMES.get(dest) if dest else None,
        'birthday': bday,
        'birthdayName': NUM_NAMES.get(bday),
        'isMasterNumber': lp in MASTER_NUMBERS
    }
