"""
bazi_relations.py
Laag 2 van de BaZi engine voor The Order of the Quiet Path / Elias Reavan.

Voegt toe aan de bestaande bazi.py:
  - Dagmeester sterkte berekening (gewogen, seizoen-first)
  - Yong Shen (Gunstig Element) bepaling
  - Botsingen, Combinaties, Straffen, Schade, Destructies detectie
  - Pilaar-interactie analyse (timing engine)
  - Hoofd-interface: full_relations_analysis()

Gebruik:
    from bazi_relations import full_relations_analysis, analyse_luck_pillar_interaction

    chart = {
        'dm_stem': 'Xin',          # Dagmeester Hemelse Stam
        'month_branch': 'Mao',      # Maand Aardse Tak
        'stems':   ['Ren', 'Xin', 'Jia', 'Ji'],   # [uur, dag, mnd, jaar]
        'branches':['Xu',  'Mao',  'Mao', 'Si'],   # [uur, dag, mnd, jaar]
    }
    result = full_relations_analysis(chart)
    print(result['dm_strength']['strength_label'])   # bijv. 'Zwak'
    print(result['dm_strength']['yong_shen'])         # bijv. 'Earth'
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Constanten
# ─────────────────────────────────────────────────────────────────────────────

ELEMENT_OF_STEM: Dict[str, str] = {
    'Jia': 'Wood', 'Yi': 'Wood',
    'Bing': 'Fire', 'Ding': 'Fire',
    'Wu': 'Earth', 'Ji': 'Earth',
    'Geng': 'Metal', 'Xin': 'Metal',
    'Ren': 'Water', 'Gui': 'Water',
}

ELEMENT_OF_BRANCH: Dict[str, str] = {
    'Zi': 'Water', 'Chou': 'Earth', 'Yin': 'Wood',  'Mao': 'Wood',
    'Chen': 'Earth', 'Si': 'Fire',  'Wu': 'Fire',   'Wei': 'Earth',
    'Shen': 'Metal', 'You': 'Metal','Xu': 'Earth',  'Hai': 'Water',
}

SEASON_GROUP: Dict[str, int] = {
    'Yin': 0, 'Mao': 0, 'Chen': 0,   # 0 = Lente
    'Si': 1,  'Wu': 1,  'Wei': 1,    # 1 = Zomer
    'Shen': 2,'You': 2, 'Xu': 2,     # 2 = Herfst
    'Hai': 3, 'Zi': 3,  'Chou': 3,   # 3 = Winter
}

# (element, seizoen) → (score 0-20, label NL)
SEASON_STRENGTH_TABLE: Dict[Tuple[str, int], Tuple[int, str]] = {
    ('Wood',  0): (20, 'Welvarend'), ('Wood',  1): (5,  'Zwak'),
    ('Wood',  2): (0,  'Dood'),      ('Wood',  3): (15, 'Sterk'),
    ('Fire',  0): (15, 'Sterk'),     ('Fire',  1): (20, 'Welvarend'),
    ('Fire',  2): (3,  'Gevangen'),  ('Fire',  3): (0,  'Dood'),
    ('Earth', 0): (0,  'Dood'),      ('Earth', 1): (15, 'Sterk'),
    ('Earth', 2): (5,  'Zwak'),      ('Earth', 3): (3,  'Gevangen'),
    ('Metal', 0): (3,  'Gevangen'),  ('Metal', 1): (0,  'Dood'),
    ('Metal', 2): (20, 'Welvarend'), ('Metal', 3): (5,  'Zwak'),
    ('Water', 0): (5,  'Zwak'),      ('Water', 1): (3,  'Gevangen'),
    ('Water', 2): (15, 'Sterk'),     ('Water', 3): (20, 'Welvarend'),
}

# Vijf Element cycli
PRODUCES: Dict[str, str] = {
    'Wood': 'Fire', 'Fire': 'Earth', 'Earth': 'Metal',
    'Metal': 'Water', 'Water': 'Wood'
}
CONTROLS: Dict[str, str] = {
    'Wood': 'Earth', 'Earth': 'Water', 'Water': 'Fire',
    'Fire': 'Metal', 'Metal': 'Wood'
}
PRODUCED_BY: Dict[str, str] = {v: k for k, v in PRODUCES.items()}
CONTROLLED_BY: Dict[str, str] = {v: k for k, v in CONTROLS.items()}

# Verborgen Stammen (Cang Gan) met rol-gewicht
HIDDEN_STEMS: Dict[str, List[Tuple[str, str]]] = {
    'Zi':  [('Gui', 'main')],
    'Chou':[('Ji', 'main'),   ('Gui', 'mid'),  ('Xin', 'residual')],
    'Yin': [('Jia', 'main'),  ('Bing', 'mid'), ('Wu', 'residual')],
    'Mao': [('Yi', 'main')],
    'Chen':[('Wu', 'main'),   ('Yi', 'mid'),   ('Gui', 'residual')],
    'Si':  [('Bing', 'main'), ('Geng', 'mid'), ('Wu', 'residual')],
    'Wu':  [('Ding', 'main'), ('Ji', 'mid')],
    'Wei': [('Ji', 'main'),   ('Ding', 'mid'), ('Yi', 'residual')],
    'Shen':[('Geng', 'main'), ('Ren', 'mid'),  ('Wu', 'residual')],
    'You': [('Xin', 'main')],
    'Xu':  [('Wu', 'main'),   ('Xin', 'mid'),  ('Ding', 'residual')],
    'Hai': [('Ren', 'main'),  ('Jia', 'mid')],
}
HIDDEN_WEIGHT: Dict[str, float] = {'main': 1.0, 'mid': 0.5, 'residual': 0.3}

# Relatie-tabellen
CLASHES_BRANCHES: List[Tuple[str, str]] = [
    ('Zi', 'Wu'), ('Chou', 'Wei'), ('Yin', 'Shen'),
    ('Mao', 'You'), ('Chen', 'Xu'), ('Si', 'Hai'),
]
CLASHES_STEMS: List[Tuple[str, str]] = [
    ('Jia', 'Geng'), ('Yi', 'Xin'), ('Bing', 'Ren'),
    ('Ding', 'Gui'), ('Wu', 'Ji'),
]
THREE_HARMONY: List[Tuple[List[str], str]] = [
    (['Shen', 'Zi', 'Chen'], 'Water'),
    (['Hai', 'Mao', 'Wei'],  'Wood'),
    (['Yin', 'Wu', 'Xu'],    'Fire'),
    (['Si', 'You', 'Chou'],  'Metal'),
]
DIRECTIONAL: List[Tuple[List[str], str]] = [
    (['Yin', 'Mao', 'Chen'], 'Wood'),
    (['Si', 'Wu', 'Wei'],    'Fire'),
    (['Shen', 'You', 'Xu'],  'Metal'),
    (['Hai', 'Zi', 'Chou'],  'Water'),
]
SIX_HARMONY: List[Tuple[str, str, str]] = [
    ('Zi', 'Chou', 'Earth'), ('Yin', 'Hai', 'Wood'),
    ('Mao', 'Xu', 'Fire'),   ('Chen', 'You', 'Metal'),
    ('Si', 'Shen', 'Water'), ('Wu', 'Wei', 'Fire'),
]
STEM_COMBOS: List[Tuple[str, str, str]] = [
    ('Jia', 'Ji', 'Earth'), ('Yi', 'Geng', 'Metal'),
    ('Bing', 'Xin', 'Water'), ('Ding', 'Ren', 'Wood'),
    ('Wu', 'Gui', 'Fire'),
]
HARMS: List[Tuple[str, str]] = [
    ('Zi', 'Wei'), ('Chou', 'Wu'), ('Yin', 'Si'),
    ('Mao', 'Chen'), ('Shen', 'Hai'), ('You', 'Xu'),
]
DESTRUCTIONS: List[Tuple[str, str]] = [
    ('Zi', 'You'), ('Chou', 'Chen'), ('Yin', 'Hai'),
    ('Mao', 'Wu'), ('Si', 'Shen'), ('Xu', 'Wei'),
]
PUNISHMENTS_GROUP: List[List[str]] = [
    ['Yin', 'Si', 'Shen'],   # Onbarmhartige straf
    ['Chou', 'Xu', 'Wei'],   # Straf van onrechtvaardigheid
]
SELF_PUNISHMENTS: List[str] = ['Zi', 'Wu', 'You', 'Hai']

# Positie-labels voor leesbaarheid
POSITION_LABELS: Dict[int, str] = {0: 'Uur', 1: 'Dag', 2: 'Maand', 3: 'Jaar'}

# Tien Goden labels (NL) — afgeleid van DM-element en element-relatie
TEN_GODS_NL: Dict[Tuple[str, str, str], str] = {
    # (dm_element, other_element, polarity_match) → naam
    # polarity_match: 'same' of 'diff' (yin/yang zelfde als DM)
    # Wealth: DM controleert dit element
    # Output: DM produceert dit element
    # Influence: dit element controleert DM
    # Resource: dit element produceert DM
    # Companion: zelfde element als DM
}

# ─────────────────────────────────────────────────────────────────────────────
# Hulpfuncties
# ─────────────────────────────────────────────────────────────────────────────

def _is_yang(stem_or_branch: str) -> bool:
    """Bepaalt of een stam of tak Yang is."""
    yang_stems = ['Jia', 'Bing', 'Wu', 'Geng', 'Ren']
    yang_branches = ['Zi', 'Yin', 'Chen', 'Wu', 'Shen', 'Xu']
    return stem_or_branch in yang_stems or stem_or_branch in yang_branches


def _element_relation(dm_element: str, other_element: str) -> str:
    """Geeft de relatie van other_element t.o.v. dm_element."""
    if other_element == dm_element:
        return 'companion'
    elif PRODUCES.get(other_element) == dm_element:
        return 'resource'
    elif CONTROLS.get(other_element) == dm_element:
        return 'influence'
    elif PRODUCES.get(dm_element) == other_element:
        return 'output'
    elif CONTROLS.get(dm_element) == other_element:
        return 'wealth'
    return 'unknown'


def get_ten_god(dm_stem: str, other_stem: str) -> str:
    """Geeft de Tien God naam voor een stam t.o.v. de Dagmeester."""
    dm_el = ELEMENT_OF_STEM[dm_stem]
    other_el = ELEMENT_OF_STEM[other_stem]
    relation = _element_relation(dm_el, other_el)
    dm_yang = _is_yang(dm_stem)
    other_yang = _is_yang(other_stem)
    same_polarity = (dm_yang == other_yang)

    tg_map = {
        ('companion',  True):  'Vriend (Bi Jian)',
        ('companion',  False): 'Rob Rijkdom (Jie Cai)',
        ('output',     True):  'Etende God (Shi Shen)',
        ('output',     False): 'Kwetsende Beambte (Shang Guan)',
        ('wealth',     False): 'Directe Rijkdom (Zheng Cai)',
        ('wealth',     True):  'Indirecte Rijkdom (Pian Cai)',
        ('influence',  False): 'Directe Beambte (Zheng Guan)',
        ('influence',  True):  'Zeven Moorden (Qi Sha)',
        ('resource',   False): 'Directe Bron (Zheng Yin)',
        ('resource',   True):  'Indirecte Bron (Pian Yin)',
    }
    return tg_map.get((relation, same_polarity), relation)


# ─────────────────────────────────────────────────────────────────────────────
# Dagmeester Sterkte
# ─────────────────────────────────────────────────────────────────────────────

def calc_dm_strength(chart: dict) -> dict:
    """
    Berekent de gewogen sterkte van de Dagmeester.

    Parameters
    ----------
    chart : dict met sleutels:
        dm_stem      : str  — Hemelse Stam van de Dagpilaar (bijv. 'Xin')
        month_branch : str  — Aardse Tak van de Maandpilaar (bijv. 'Mao')
        stems        : list[str] — [uur, dag, maand, jaar] Hemelse Stammen
        branches     : list[str] — [uur, dag, maand, jaar] Aardse Takken

    Returns
    -------
    dict met:
        score              : float (0–100+)
        season_base        : str   (Welvarend/Sterk/Zwak/Gevangen/Dood)
        strength_label     : str   (Extreem Sterk / Sterk / Neutraal / Zwak / Extreem Zwak)
        is_strong          : bool
        yong_shen          : str   (Gunstig Element)
        ji_shen            : str   (Ongunstig Element)
        favourable_elements: list[str]
        unfavourable_elements: list[str]
        follow_chart       : bool  (True als speciale Follow-structuur)
        analysis_notes     : list[str]
    """
    dm_stem = chart['dm_stem']
    dm_el = ELEMENT_OF_STEM[dm_stem]
    month_branch = chart['month_branch']
    season = SEASON_GROUP[month_branch]

    notes = []

    # Stap 1: Yue Ling (seizoens-basis) — meest gewichtig
    base_score, season_label = SEASON_STRENGTH_TABLE[(dm_el, season)]
    total = base_score * 1.5  # Yue Ling krijgt 1.5x gewicht
    notes.append(f"Yue Ling ({month_branch}, {season_label}): basesscore {base_score} × 1.5 = {base_score * 1.5:.1f}")

    # Stap 2: Support van andere Hemelse Stammen
    for i, stem in enumerate(chart['stems']):
        if i == 1:  # Dag-stam = DM zelf, overslaan
            continue
        if stem not in ELEMENT_OF_STEM:
            continue
        el = ELEMENT_OF_STEM[stem]
        if el == dm_el:
            total += 8
            notes.append(f"Stam {stem} ({POSITION_LABELS[i]}): zelfde element +8")
        elif PRODUCES.get(el) == dm_el:
            total += 6
            notes.append(f"Stam {stem} ({POSITION_LABELS[i]}): voedt DM +6")
        elif CONTROLS.get(el) == dm_el:
            total -= 5
            notes.append(f"Stam {stem} ({POSITION_LABELS[i]}): controleert DM -5")
        elif PRODUCES.get(dm_el) == el:
            total -= 3
            notes.append(f"Stam {stem} ({POSITION_LABELS[i]}): DM produceert dit -3 (uitputting)")

    # Stap 3: Support via Aardse Takken (verborgen stammen)
    for i, branch in enumerate(chart['branches']):
        if i == 1:  # Dag-tak: minder gewicht (DM zelf is de referentie)
            weight_mult = 0.7
        else:
            weight_mult = 1.0
        for hidden_stem, role in HIDDEN_STEMS.get(branch, []):
            el = ELEMENT_OF_STEM[hidden_stem]
            w = HIDDEN_WEIGHT[role] * weight_mult
            if el == dm_el:
                add = 6 * w
                total += add
                notes.append(f"Verborgen {hidden_stem} in {branch} ({POSITION_LABELS[i]}, {role}): +{add:.1f}")
            elif PRODUCES.get(el) == dm_el:
                add = 4 * w
                total += add
                notes.append(f"Verborgen {hidden_stem} in {branch} ({POSITION_LABELS[i]}, {role}): voedt +{add:.1f}")
            elif CONTROLS.get(el) == dm_el:
                sub = 3 * w
                total -= sub
                notes.append(f"Verborgen {hidden_stem} in {branch} ({POSITION_LABELS[i]}, {role}): controleert -{sub:.1f}")

    total = round(total, 1)

    # Classificatie
    if total >= 60:
        strength_label = 'Extreem Sterk'
        is_strong = True
    elif total >= 38:
        strength_label = 'Sterk'
        is_strong = True
    elif total >= 22:
        strength_label = 'Neutraal'
        is_strong = True  # bij twijfel: behandel als sterk
    elif total >= 10:
        strength_label = 'Zwak'
        is_strong = False
    else:
        strength_label = 'Extreem Zwak'
        is_strong = False

    # Check voor Follow Chart (极弱从格)
    follow_chart = False
    if total < 10:
        # Tel dominant element in de rest van de grafiek
        element_counts: Dict[str, float] = {}
        for stem in chart['stems']:
            if stem in ELEMENT_OF_STEM:
                el = ELEMENT_OF_STEM[stem]
                element_counts[el] = element_counts.get(el, 0) + 1
        for branch in chart['branches']:
            main_hidden = HIDDEN_STEMS.get(branch, [('', '')])[0][0]
            if main_hidden in ELEMENT_OF_STEM:
                el = ELEMENT_OF_STEM[main_hidden]
                element_counts[el] = element_counts.get(el, 0) + 1
        dominant = max(element_counts, key=element_counts.get, default=None)
        if dominant and element_counts.get(dominant, 0) >= 5:
            follow_chart = True
            strength_label = f'Follow Chart → {dominant}'
            notes.append(f"SPECIALE STRUCTUUR: Follow Chart — DM volgt dominerend {dominant}")

    # Yong Shen (Gunstig Element) bepalen
    if follow_chart:
        dominant_el = strength_label.split('→')[-1].strip()
        yong_shen = dominant_el
        ji_shen = CONTROLS.get(dominant_el, dm_el)
        fav = [dominant_el, PRODUCES[dominant_el]]
        unfav = [CONTROLS[dominant_el]]
    elif is_strong:
        # Sterk: DM moet gecontroleerd, uitgeput of afgeleid worden
        yong_shen = CONTROLS[dm_el]   # element dat DM controleert = primair gunstig
        ji_shen_el = PRODUCED_BY.get(dm_el, '')  # element dat DM voedt = ongunstig
        fav = [CONTROLS[dm_el], PRODUCES[dm_el], CONTROLS.get(CONTROLS[dm_el], '')]
        fav = [e for e in fav if e]
        unfav = [dm_el, PRODUCED_BY.get(dm_el, '')]
        unfav = [e for e in unfav if e]
        ji_shen = unfav[0] if unfav else dm_el
    else:
        # Zwak: DM heeft steun nodig
        yong_shen = PRODUCED_BY.get(dm_el, dm_el)  # element dat DM voedt
        fav = [dm_el, PRODUCED_BY.get(dm_el, '')]
        fav = [e for e in fav if e]
        unfav = [CONTROLS[dm_el], PRODUCES[dm_el]]
        ji_shen = unfav[0] if unfav else CONTROLS[dm_el]

    return {
        'score': total,
        'season_base': season_label,
        'strength_label': strength_label,
        'is_strong': is_strong,
        'follow_chart': follow_chart,
        'yong_shen': yong_shen,
        'ji_shen': ji_shen,
        'favourable_elements': list(dict.fromkeys(fav)),    # uniek, volgorde bewaard
        'unfavourable_elements': list(dict.fromkeys(unfav)),
        'analysis_notes': notes,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Relatie Detectie
# ─────────────────────────────────────────────────────────────────────────────

def detect_branch_clashes(branches: List[str]) -> List[dict]:
    results = []
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            b1, b2 = branches[i], branches[j]
            if {b1, b2} in [{p[0], p[1]} for p in CLASHES_BRANCHES]:
                results.append({
                    'type': 'branch_clash',
                    'pair': [b1, b2],
                    'positions': [POSITION_LABELS[i], POSITION_LABELS[j]],
                    'severity': 'major',
                })
    return results


def detect_stem_clashes(stems: List[str]) -> List[dict]:
    results = []
    for i in range(len(stems)):
        for j in range(i + 1, len(stems)):
            s1, s2 = stems[i], stems[j]
            if {s1, s2} in [{p[0], p[1]} for p in CLASHES_STEMS]:
                results.append({
                    'type': 'stem_clash',
                    'pair': [s1, s2],
                    'positions': [POSITION_LABELS[i], POSITION_LABELS[j]],
                    'severity': 'minor',
                })
    return results


def detect_combinations(branches: List[str], stems: List[str]) -> List[dict]:
    results = []
    branch_set = set(branches)
    stem_set = set(stems)

    # Drie Harmonie
    for members, element in THREE_HARMONY:
        found = [b for b in members if b in branch_set]
        if len(found) == 3:
            results.append({
                'type': 'three_harmony',
                'members': found,
                'element': element,
                'complete': True,
                'strength': 'major',
            })
        elif len(found) == 2:
            missing = [b for b in members if b not in branch_set][0]
            results.append({
                'type': 'three_harmony_partial',
                'members': found,
                'element': element,
                'complete': False,
                'missing': missing,
                'note': f'Wordt geactiveerd wanneer {missing} arriveert in Gelukspilaar of Jaarlijkse Pilaar',
            })

    # Directionele Combinatie
    for members, element in DIRECTIONAL:
        if all(b in branch_set for b in members):
            results.append({
                'type': 'directional',
                'members': list(members),
                'element': element,
                'complete': True,
                'strength': 'very_major',
            })

    # Zes Harmonie
    for b1, b2, element in SIX_HARMONY:
        if b1 in branch_set and b2 in branch_set:
            results.append({
                'type': 'six_harmony',
                'pair': [b1, b2],
                'element': element,
                'strength': 'moderate',
            })

    # Hemelse Stam Combinaties
    for s1, s2, element in STEM_COMBOS:
        if s1 in stem_set and s2 in stem_set:
            results.append({
                'type': 'stem_combo',
                'pair': [s1, s2],
                'element': element,
                'strength': 'surface',
            })

    return results


def detect_harms(branches: List[str]) -> List[dict]:
    results = []
    branch_set = set(branches)
    for b1, b2 in HARMS:
        if b1 in branch_set and b2 in branch_set:
            results.append({'type': 'harm', 'pair': [b1, b2]})
    return results


def detect_destructions(branches: List[str]) -> List[dict]:
    results = []
    branch_set = set(branches)
    for b1, b2 in DESTRUCTIONS:
        if b1 in branch_set and b2 in branch_set:
            results.append({'type': 'destruction', 'pair': [b1, b2]})
    return results


def detect_punishments(branches: List[str]) -> List[dict]:
    results = []
    branch_set = set(branches)
    for group in PUNISHMENTS_GROUP:
        found = [b for b in group if b in branch_set]
        if len(found) >= 2:
            results.append({
                'type': 'punishment',
                'members': found,
                'complete': len(found) == 3,
                'group': group,
            })
    for b in SELF_PUNISHMENTS:
        if branches.count(b) >= 2:
            results.append({'type': 'self_punishment', 'branch': b})
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Timing Engine: Pilaar Interactie
# ─────────────────────────────────────────────────────────────────────────────

def analyse_luck_pillar_interaction(
    static_chart: dict,
    luck_stem: str,
    luck_branch: str,
    annual_stem: str,
    annual_branch: str,
    dm_strength: Optional[dict] = None,
) -> dict:
    """
    Analyseert de interactie tussen de statische BaZi grafiek
    en de lopende Gelukspilaar + Jaarlijkse Pilaar.

    Parameters
    ----------
    static_chart  : dict — zelfde formaat als voor full_relations_analysis()
    luck_stem     : str  — Hemelse Stam lopende Gelukspilaar
    luck_branch   : str  — Aardse Tak lopende Gelukspilaar
    annual_stem   : str  — Hemelse Stam huidig jaar
    annual_branch : str  — Aardse Tak huidig jaar
    dm_strength   : dict — resultaat van calc_dm_strength(), optioneel

    Returns
    -------
    dict met:
        luck_element, luck_quality, annual_element, annual_quality : str
        events                                                      : list[dict]
        activated_combinations                                      : list[dict]
        summary                                                     : str
    """
    if dm_strength is None:
        dm_strength = calc_dm_strength(static_chart)

    fav_els = dm_strength['favourable_elements']
    unfav_els = dm_strength['unfavourable_elements']
    yong = dm_strength['yong_shen']

    events = []

    # Botsingen tussen dynamische takken en statische takken
    dynamic_pairs = [
        (luck_branch, 'Gelukspilaar'),
        (annual_branch, 'Jaarlijkse Pilaar'),
    ]
    for db, source in dynamic_pairs:
        for i, sb in enumerate(static_chart['branches']):
            if {sb, db} in [{p[0], p[1]} for p in CLASHES_BRANCHES]:
                db_el = ELEMENT_OF_BRANCH.get(db, '')
                is_fav = db_el in fav_els
                events.append({
                    'type': 'dynamic_clash',
                    'static_branch': sb,
                    'static_position': POSITION_LABELS[i],
                    'dynamic_branch': db,
                    'source': source,
                    'favourable': is_fav,
                    'interpretation': (
                        f'Gunstige botsing — {db} verwijdert het negatieve {sb} element'
                        if is_fav else
                        f'Ongunstige botsing — verstoring in het {POSITION_LABELS[i]}-domein'
                    ),
                })

    # Botsingen stam-stam (dynamisch vs statisch)
    dynamic_stem_pairs = [(luck_stem, 'Gelukspilaar'), (annual_stem, 'Jaarlijkse Pilaar')]
    for ds, source in dynamic_stem_pairs:
        for i, ss in enumerate(static_chart['stems']):
            if {ss, ds} in [{p[0], p[1]} for p in CLASHES_STEMS]:
                events.append({
                    'type': 'dynamic_stem_clash',
                    'static_stem': ss,
                    'dynamic_stem': ds,
                    'source': source,
                })

    # Check of gedeeltelijke combinaties nu geactiveerd worden
    all_branches = static_chart['branches'] + [luck_branch, annual_branch]
    all_stems = static_chart['stems'] + [luck_stem, annual_stem]
    full_combos = detect_combinations(all_branches, all_stems)
    static_combos = detect_combinations(static_chart['branches'], static_chart['stems'])
    static_keys = {f"{c['type']}_{c.get('element', '')}" for c in static_combos if c.get('complete')}
    activated = []
    for combo in full_combos:
        if not combo.get('complete'):
            continue
        key = f"{combo['type']}_{combo.get('element', '')}"
        if key not in static_keys:
            activated.append({**combo, 'activated_by': 'Lopende Gelukspilaar/Jaarlijkse Pilaar'})

    # Kwaliteit van de lopende elementen
    luck_el = ELEMENT_OF_BRANCH.get(luck_branch, '')
    annual_el = ELEMENT_OF_BRANCH.get(annual_branch, '')

    def _quality(el: str) -> str:
        if el == yong:
            return 'gunstig'
        elif el in unfav_els:
            return 'ongunstig'
        elif el in fav_els:
            return 'gunstig'
        return 'neutraal'

    luck_q = _quality(luck_el)
    annual_q = _quality(annual_el)

    return {
        'luck_element': luck_el,
        'luck_quality': luck_q,
        'annual_element': annual_el,
        'annual_quality': annual_q,
        'events': events,
        'activated_combinations': activated,
        'summary': _build_timing_summary(luck_q, annual_q, events, activated),
    }


def _build_timing_summary(luck_q: str, annual_q: str,
                           events: list, activated: list) -> str:
    base_map = {
        ('gunstig', 'gunstig'): (
            "Uitstekende periode — zowel de 10-jarige cyclus als het lopende jaar "
            "zijn gunstig. Dit is het moment om grote stappen te zetten."
        ),
        ('gunstig', 'neutraal'): (
            "Goede 10-jarige cyclus. Het lopende jaar is neutraal — consolideer "
            "eerder dan te expanderen."
        ),
        ('gunstig', 'ongunstig'): (
            "Goede 10-jarige cyclus, maar het lopende jaar brengt weerstand. "
            "Bouw voort op de cyclus, maar reken op obstakels dit jaar."
        ),
        ('neutraal', 'gunstig'): (
            "Neutraal decennium, maar het lopende jaar biedt een venster van kansen. "
            "Benut het jaar goed."
        ),
        ('neutraal', 'ongunstig'): (
            "Rustige, neutrale periode met een uitdagend jaar. Conservatieve "
            "aanpak aanbevolen."
        ),
        ('ongunstig', 'gunstig'): (
            "Uitdagend decennium, maar het lopende jaar geeft verlichting. "
            "Gebruik dit jaar als springplank."
        ),
        ('ongunstig', 'ongunstig'): (
            "Uitdagende periode — zowel de cyclus als het jaar zijn ongunstig. "
            "Bescherm wat je hebt, vermijd grote risico's."
        ),
    }
    summary = base_map.get((luck_q, annual_q), "Gemengde periode — analyseer per levendomein.")

    unfav_clashes = [e for e in events if e.get('type') == 'dynamic_clash' and not e.get('favourable')]
    fav_clashes   = [e for e in events if e.get('type') == 'dynamic_clash' and e.get('favourable')]

    if unfav_clashes:
        summary += f" Let op: {len(unfav_clashes)} actieve ongunstige botsing(en)."
    if fav_clashes:
        summary += f" Positief: {len(fav_clashes)} botsing(en) ruimen negatieve energie op."
    if activated:
        els = ', '.join(set(c.get('element', '') for c in activated))
        summary += f" Bijzonder: {els}-combinatie geactiveerd door lopende pilaar."

    return summary


# ─────────────────────────────────────────────────────────────────────────────
# Hoofd-interface
# ─────────────────────────────────────────────────────────────────────────────

def full_relations_analysis(chart: dict) -> dict:
    """
    Voert een volledige relatie-analyse uit op de statische BaZi grafiek.

    Parameters
    ----------
    chart : dict met:
        dm_stem      : str        — bijv. 'Xin'
        month_branch : str        — bijv. 'Mao'
        stems        : list[str]  — [uur, dag, maand, jaar]
        branches     : list[str]  — [uur, dag, maand, jaar]

    Returns
    -------
    dict met alle analyse-resultaten, klaar voor JSON-serialisatie
    en voor Claude reading-engine.
    """
    dm_strength   = calc_dm_strength(chart)
    combinations  = detect_combinations(chart['branches'], chart['stems'])
    branch_clashes = detect_branch_clashes(chart['branches'])
    stem_clashes  = detect_stem_clashes(chart['stems'])
    harms         = detect_harms(chart['branches'])
    destructions  = detect_destructions(chart['branches'])
    punishments   = detect_punishments(chart['branches'])

    # Interpreteer elke relatie t.o.v. Yong Shen
    def _tag_relation(rel: dict) -> dict:
        el = rel.get('element', '')
        fav = dm_strength['favourable_elements']
        unfav = dm_strength['unfavourable_elements']
        if el:
            rel['element_quality'] = (
                'gunstig' if el in fav else
                'ongunstig' if el in unfav else 'neutraal'
            )
        return rel

    combinations = [_tag_relation(c) for c in combinations]

    return {
        'dm_strength':     dm_strength,
        'branch_clashes':  branch_clashes,
        'stem_clashes':    stem_clashes,
        'combinations':    combinations,
        'harms':           harms,
        'destructions':    destructions,
        'punishments':     punishments,
        'summary': {
            'has_clashes':       len(branch_clashes) > 0,
            'has_combinations':  any(c.get('complete') for c in combinations),
            'has_punishments':   len(punishments) > 0,
            'yong_shen':         dm_strength['yong_shen'],
            'strength_label':    dm_strength['strength_label'],
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# Quick Test
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import json

    # Timo's chart: Xin Mao dag, Mao maand (Lente), Ji Si jaar, Ren Xu uur
    test_chart = {
        'dm_stem': 'Xin',
        'month_branch': 'Mao',
        'stems':   ['Ren', 'Xin', 'Jia', 'Ji'],
        'branches':['Xu',  'Mao', 'Mao', 'Si'],
    }

    result = full_relations_analysis(test_chart)
    print("=== Dagmeester Sterkte ===")
    print(f"Score:   {result['dm_strength']['score']}")
    print(f"Label:   {result['dm_strength']['strength_label']}")
    print(f"Yong:    {result['dm_strength']['yong_shen']}")
    print(f"Ji Shen: {result['dm_strength']['ji_shen']}")
    print()
    print("=== Botsingen ===")
    for c in result['branch_clashes']:
        print(f"  {c['pair']} ({c['positions'][0]} ↔ {c['positions'][1]})")
    print()
    print("=== Combinaties ===")
    for c in result['combinations']:
        print(f"  {c['type']}: {c.get('members', c.get('pair'))} → {c.get('element','?')}"
              f" ({'compleet' if c.get('complete') else 'gedeeltelijk'})")
    print()
    print("=== Timing 2026 ===")
    timing = analyse_luck_pillar_interaction(
        static_chart=test_chart,
        luck_stem='Ren', luck_branch='Zi',       # bijv. huidige gelukspilaar
        annual_stem='Bing', annual_branch='Wu',   # 2026 = Bing Wu jaar
        dm_strength=result['dm_strength'],
    )
    print(f"Luck: {timing['luck_element']} ({timing['luck_quality']})")
    print(f"Jaar: {timing['annual_element']} ({timing['annual_quality']})")
    print(f"Samenvatting: {timing['summary']}")
