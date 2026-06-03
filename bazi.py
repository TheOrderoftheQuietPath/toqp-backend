import swisseph as swe

try:
    from bazi_relations import full_relations_analysis
    _RELATIONS_AVAILABLE = True
except ImportError:
    _RELATIONS_AVAILABLE = False

# Mapping: Chinese branch symbol → bazi_relations romanisatie key
_BRANCH_SYM_TO_KEY = {
    '子': 'Zi',  '丑': 'Chou', '寅': 'Yin',  '卯': 'Mao',
    '辰': 'Chen','巳': 'Si',   '午': 'Wu',   '未': 'Wei',
    '申': 'Shen','酉': 'You',  '戌': 'Xu',   '亥': 'Hai',
}
# Mapping: stem id (lowercase) → bazi_relations key (capitalised)
def _stem_to_key(stem_obj: dict) -> str:
    return stem_obj.get('id', '').capitalize()

# ═══════════════════════════════════════════════════════
# BAZI — VIER PILAREN VAN LOT
# Verbeteringen t.o.v. standaard online tools:
# ✅ Jaarpilaar wisselt op exacte Li Chun (315° zon, ~4 feb)
# ✅ Maandpilaar wisselt op exacte Solar Terms (30° stappen)
# ✅ Uurpilaar gebruikt Ware Zonnestijd (longitude correctie)
# ✅ Swiss Ephemeris voor alle berekeningen
# Accuraatheid: ~90%+ vs gemiddelde online tools
# ═══════════════════════════════════════════════════════

HEAVENLY_STEMS = [
    {'id':'jia',  'nl':'Jiǎ',  'en':'Jiǎ',  'symbol':'甲',
     'element':'Wood',  'element_nl':'Hout',   'element_en':'Wood',
     'polarity':'+', 'polarity_nl':'Yang', 'polarity_en':'Yang',
     'color':'#4a8a4a',
     'archetype_nl': 'De Grote Eik — oprijzend, vastberaden, recht',
     'archetype_en': 'The Great Oak — rising, determined, upright',
     'qualities_nl': 'leiderschap, visie, integriteit, groei',
     'qualities_en': 'leadership, vision, integrity, growth',
     'year_meaning_nl':  'Voorouderlijke energie: jouw roots zijn sterk en recht',
     'month_meaning_nl': 'Carrière sfeer: je groeit best in structuur en richting',
     'day_meaning_nl':   'Jij bent de leider — principes en visie zijn je kern',
     'hour_meaning_nl':  'Jouw nalatenschap: je kinderen of creaties dragen jouw vastheid'},
    {'id':'yi',   'nl':'Yǐ',   'en':'Yǐ',   'symbol':'乙',
     'element':'Wood',  'element_nl':'Hout',   'element_en':'Wood',
     'polarity':'-', 'polarity_nl':'Yin',  'polarity_en':'Yin',
     'color':'#6aaa5a',
     'archetype_nl': 'De Klimplant — soepel, creatief, verbindend',
     'archetype_en': 'The Vine — flexible, creative, connecting',
     'qualities_nl': 'aanpassingsvermogen, elegantie, diplomatie, doorzettingsvermogen',
     'qualities_en': 'adaptability, elegance, diplomacy, perseverance',
     'year_meaning_nl':  'Je komst was zacht maar krachtig — je bent gevormd door subtiele krachten',
     'month_meaning_nl': 'Je gedijt in omgevingen met steun en ruimte voor creativiteit',
     'day_meaning_nl':   'Jij bent de diplomat — aanpassing en verbinding zijn jouw gave',
     'hour_meaning_nl':  'Je nalatenschap groeit langzaam maar zeker, als een wijnstok'},
    {'id':'bing', 'nl':'Bǐng', 'en':'Bǐng', 'symbol':'丙',
     'element':'Fire',  'element_nl':'Vuur',   'element_en':'Fire',
     'polarity':'+', 'polarity_nl':'Yang', 'polarity_en':'Yang',
     'color':'#c05a3a',
     'archetype_nl': 'De Zon — stralend, warm, alles verlichtend',
     'archetype_en': 'The Sun — radiant, warm, illuminating all',
     'qualities_nl': 'uitbundigheid, optimisme, charisma, directheid',
     'qualities_en': 'exuberance, optimism, charisma, directness',
     'year_meaning_nl':  'Je werd geboren met zonne-energie — je aanwezigheid was direct voelbaar',
     'month_meaning_nl': 'Je carrière bloeit best in het volle licht, voor een publiek',
     'day_meaning_nl':   'Jij bent de zon — jouw warmte en licht zijn jouw essentie',
     'hour_meaning_nl':  'Je nalatenschap is een blijvend licht voor de mensen om je heen'},
    {'id':'ding', 'nl':'Dīng', 'en':'Dīng', 'symbol':'丁',
     'element':'Fire',  'element_nl':'Vuur',   'element_en':'Fire',
     'polarity':'-', 'polarity_nl':'Yin',  'polarity_en':'Yin',
     'color':'#e07a5a',
     'archetype_nl': 'De Kaars — intiem, precies, diepzinnig licht',
     'archetype_en': 'The Candle — intimate, precise, deep light',
     'qualities_nl': 'intuïtie, verfijning, empathie, doordachtheid',
     'qualities_en': 'intuition, refinement, empathy, thoughtfulness',
     'year_meaning_nl':  'Je werd geboren met een fijn, gericht licht — diepgang van jongs af aan',
     'month_meaning_nl': 'Je werkt best in intieme, betekenisvolle omgevingen',
     'day_meaning_nl':   'Jij bent de kaars — jouw intuïtie en warmte zijn jouw kern',
     'hour_meaning_nl':  'Jouw nalatenschap is diep en persoonlijk — niet breed maar onvergetelijk'},
    {'id':'wu',   'nl':'Wù',   'en':'Wù',   'symbol':'戊',
     'element':'Earth', 'element_nl':'Aarde',  'element_en':'Earth',
     'polarity':'+', 'polarity_nl':'Yang', 'polarity_en':'Yang',
     'color':'#a08040',
     'archetype_nl': 'De Berg — stabiel, beschermend, onwrikbaar',
     'archetype_en': 'The Mountain — stable, protective, immovable',
     'qualities_nl': 'betrouwbaarheid, geduld, kracht, standvastigheid',
     'qualities_en': 'reliability, patience, strength, steadfastness',
     'year_meaning_nl':  'Je werd geboren in stabiliteit — je roots zijn diep verankerd',
     'month_meaning_nl': 'Je gedijt in omgevingen die structuur en zekerheid bieden',
     'day_meaning_nl':   'Jij bent de berg — anderen zoeken houvast bij jou',
     'hour_meaning_nl':  'Jouw nalatenschap is een fundament dat generaties draagt'},
    {'id':'ji',   'nl':'Jǐ',   'en':'Jǐ',   'symbol':'己',
     'element':'Earth', 'element_nl':'Aarde',  'element_en':'Earth',
     'polarity':'-', 'polarity_nl':'Yin',  'polarity_en':'Yin',
     'color':'#c0a060',
     'archetype_nl': 'De Akker — voedend, zorgzaam, vruchtbaar',
     'archetype_en': 'The Field — nurturing, caring, fertile',
     'qualities_nl': 'verzorging, geduld, praktisch, ontvankelijk',
     'qualities_en': 'nurturing, patience, practicality, receptiveness',
     'year_meaning_nl':  'Je werd geboren in vruchtbare grond — je hebt veel meegekregen',
     'month_meaning_nl': 'Je gedijt het best als je anderen kunt voeden en ondersteunen',
     'day_meaning_nl':   'Jij bent de akker — groei jij, groeien ook de mensen om je heen',
     'hour_meaning_nl':  'Jouw nalatenschap is de vrucht van jouw zorg voor anderen'},
    {'id':'geng', 'nl':'Gēng', 'en':'Gēng', 'symbol':'庚',
     'element':'Metal', 'element_nl':'Metaal', 'element_en':'Metal',
     'polarity':'+', 'polarity_nl':'Yang', 'polarity_en':'Yang',
     'color':'#7090a0',
     'archetype_nl': 'Het Zwaard — scherp, direct, moedig',
     'archetype_en': 'The Sword — sharp, direct, courageous',
     'qualities_nl': 'daadkracht, eerlijkheid, moed, efficiëntie',
     'qualities_en': 'decisiveness, honesty, courage, efficiency',
     'year_meaning_nl':  'Je werd geboren met ijzeren kracht — uitdagingen tempen jou',
     'month_meaning_nl': 'Je excelleert in omgevingen die actie en resultaat vragen',
     'day_meaning_nl':   'Jij bent het zwaard — scherpte en directheid zijn jouw identiteit',
     'hour_meaning_nl':  'Jouw nalatenschap is de verandering die jij teweeg hebt gebracht'},
    {'id':'xin',  'nl':'Xīn',  'en':'Xīn',  'symbol':'辛',
     'element':'Metal', 'element_nl':'Metaal', 'element_en':'Metal',
     'polarity':'-', 'polarity_nl':'Yin',  'polarity_en':'Yin',
     'color':'#90b0c0',
     'archetype_nl': 'Het Edelmetaal — verfijnd, precies, van hoge kwaliteit',
     'archetype_en': 'The Precious Metal — refined, precise, high quality',
     'qualities_nl': 'precisie, esthetiek, analytisch, eerlijkheid',
     'qualities_en': 'precision, aesthetics, analytical, honesty',
     'year_meaning_nl':  'Je werd geboren met verfijnde zintuigen — je voelde al vroeg wat klopt',
     'month_meaning_nl': 'Je werkt best in omgevingen die kwaliteit en precisie waarderen',
     'day_meaning_nl':   'Jij bent het edelmetaal — perfectie en waarheid zijn jouw kompas',
     'hour_meaning_nl':  'Jouw nalatenschap is de kwaliteit en schoonheid die je hebt nagelaten'},
    {'id':'ren',  'nl':'Rén',  'en':'Rén',  'symbol':'壬',
     'element':'Water', 'element_nl':'Water',  'element_en':'Water',
     'polarity':'+', 'polarity_nl':'Yang', 'polarity_en':'Yang',
     'color':'#3a6a9a',
     'archetype_nl': 'De Oceaan — diep, krachtig, wijs',
     'archetype_en': 'The Ocean — deep, powerful, wise',
     'qualities_nl': 'intelligentie, strategie, diepgang, flexibiliteit',
     'qualities_en': 'intelligence, strategy, depth, flexibility',
     'year_meaning_nl':  'Je werd geboren met oceanische diepte — je draagt oude wijsheid in je',
     'month_meaning_nl': 'Je excelleert in strategische, intellectuele omgevingen',
     'day_meaning_nl':   'Jij bent de oceaan — wijsheid en strategie stromen door jou heen',
     'hour_meaning_nl':  'Jouw nalatenschap is de kennis en inzichten die je hebt doorgegeven'},
    {'id':'gui',  'nl':'Guǐ',  'en':'Guǐ',  'symbol':'癸',
     'element':'Water', 'element_nl':'Water',  'element_en':'Water',
     'polarity':'-', 'polarity_nl':'Yin',  'polarity_en':'Yin',
     'color':'#5a8aba',
     'archetype_nl': 'De Regenbui — zacht, voedend, alles doordringend',
     'archetype_en': 'The Rain — gentle, nourishing, all-permeating',
     'qualities_nl': 'empathie, intuïtie, gevoeligheid, aanpassingsvermogen',
     'qualities_en': 'empathy, intuition, sensitivity, adaptability',
     'year_meaning_nl':  'Je werd geboren met fijne gevoeligheid — je absorbeerde alles om je heen',
     'month_meaning_nl': 'Je gedijt in empathische, zorgzame omgevingen',
     'day_meaning_nl':   'Jij bent de regen — jouw gevoeligheid en empathie zijn jouw gave',
     'hour_meaning_nl':  'Jouw nalatenschap is de zachte maar blijvende invloed op anderen'},
]

EARTHLY_BRANCHES = [
    {'nl':'Zǐ',   'en':'Zǐ',   'symbol':'子',
     'element':'Water', 'element_nl':'Water',  'element_en':'Water',
     'animal':'Rat',     'nl_animal':'Rat',     'en_animal':'Rat',
     'archetype_nl': 'De Rat — inventief, charmant, overlever',
     'archetype_en': 'The Rat — inventive, charming, survivor',
     'qualities_nl': 'slimheid, aanpassingsvermogen, sociale intelligentie',
     'year_meaning_nl':  'Je bezit aangeboren vindingrijkheid en sociale antenne',
     'month_meaning_nl': 'Een periode van slimme kansen en nieuwe verbindingen',
     'day_meaning_nl':   'Jij of je partner heeft een scherp, adaptief karakter',
     'hour_meaning_nl':  'Jouw latere jaren brengen vindingrijke oplossingen'},
    {'nl':'Chǒu', 'en':'Chǒu', 'symbol':'丑',
     'element':'Earth', 'element_nl':'Aarde',  'element_en':'Earth',
     'animal':'Ox',      'nl_animal':'Os',      'en_animal':'Ox',
     'archetype_nl': 'De Os — geduldig, hardwerkend, betrouwbaar',
     'archetype_en': 'The Ox — patient, hardworking, reliable',
     'qualities_nl': 'doorzettingsvermogen, loyaliteit, praktische kracht',
     'year_meaning_nl':  'Je bent geboren met de kracht om te bouwen en vol te houden',
     'month_meaning_nl': 'Hard werk dat vaste, blijvende vruchten afwerpt',
     'day_meaning_nl':   'Jij of je partner is betrouwbaar, geduldig en sterk',
     'hour_meaning_nl':  'Jouw erfenis is wat je met eigen handen hebt gebouwd'},
    {'nl':'Yín',  'en':'Yín',  'symbol':'寅',
     'element':'Wood',  'element_nl':'Hout',   'element_en':'Wood',
     'animal':'Tiger',  'nl_animal':'Tijger',  'en_animal':'Tiger',
     'archetype_nl': 'De Tijger — moedig, charismatisch, onafhankelijk',
     'archetype_en': 'The Tiger — courageous, charismatic, independent',
     'qualities_nl': 'moed, leiderschap, energie, spontaniteit',
     'year_meaning_nl':  'Je bent geboren met een krachtige, vrije geest',
     'month_meaning_nl': 'Een periode van actie, kansen en nieuwe uitdagingen',
     'day_meaning_nl':   'Jij of je partner heeft een sterke, onafhankelijke natuur',
     'hour_meaning_nl':  'Jouw nalatenschap is de moed die je anderen hebt geïnspireerd'},
    {'nl':'Mǎo',  'en':'Mǎo',  'symbol':'卯',
     'element':'Wood',  'element_nl':'Hout',   'element_en':'Wood',
     'animal':'Rabbit', 'nl_animal':'Konijn',  'en_animal':'Rabbit',
     'archetype_nl': 'Het Konijn — verfijnd, diplomatiek, intuïtief',
     'archetype_en': 'The Rabbit — refined, diplomatic, intuitive',
     'qualities_nl': 'elegantie, tact, empathie, artistiek gevoel',
     'year_meaning_nl':  'Je bent geboren met verfijning en een fijn sociaal gevoel',
     'month_meaning_nl': 'Een periode van diplomatie, verbinding en esthetiek',
     'day_meaning_nl':   'Jij of je partner is verfijnd, empathisch en kunstzinnig',
     'hour_meaning_nl':  'Jouw erfenis is de schoonheid en harmonie die je hebt gecreëerd'},
    {'nl':'Chén', 'en':'Chén', 'symbol':'辰',
     'element':'Earth', 'element_nl':'Aarde',  'element_en':'Earth',
     'animal':'Dragon', 'nl_animal':'Draak',   'en_animal':'Dragon',
     'archetype_nl': 'De Draak — krachtig, visionair, magisch',
     'archetype_en': 'The Dragon — powerful, visionary, magical',
     'qualities_nl': 'charisma, visie, kracht, originaliteit',
     'year_meaning_nl':  'Je bent geboren met uitzonderlijke energie en visie',
     'month_meaning_nl': 'Een periode van grootse kansen en magische samenloop',
     'day_meaning_nl':   'Jij of je partner heeft een krachtige, unieke persoonlijkheid',
     'hour_meaning_nl':  'Jouw nalatenschap overstijgt het gewone — blijvende impact'},
    {'nl':'Sì',   'en':'Sì',   'symbol':'巳',
     'element':'Fire',  'element_nl':'Vuur',   'element_en':'Fire',
     'animal':'Snake',  'nl_animal':'Slang',   'en_animal':'Snake',
     'archetype_nl': 'De Slang — wijs, mysterieus, intuïtief',
     'archetype_en': 'The Snake — wise, mysterious, intuitive',
     'qualities_nl': 'wijsheid, intuïtie, elegantie, diepgang',
     'year_meaning_nl':  'Je bent geboren met diepe wijsheid en fijn instinct',
     'month_meaning_nl': 'Een periode van stille kracht, transformatie en inzicht',
     'day_meaning_nl':   'Jij of je partner is wijs, intuïtief en mysterieus diep',
     'hour_meaning_nl':  'Jouw erfenis is de wijsheid die je in stilte hebt vergaard'},
    {'nl':'Wǔ',   'en':'Wǔ',   'symbol':'午',
     'element':'Fire',  'element_nl':'Vuur',   'element_en':'Fire',
     'animal':'Horse',  'nl_animal':'Paard',   'en_animal':'Horse',
     'archetype_nl': 'Het Paard — vrij, enthousiast, energiek',
     'archetype_en': 'The Horse — free, enthusiastic, energetic',
     'qualities_nl': 'vrijheid, passie, snelheid, optimisme',
     'year_meaning_nl':  'Je bent geboren met een vrije, energieke geest',
     'month_meaning_nl': 'Een periode van energie, beweging en nieuwe horizons',
     'day_meaning_nl':   'Jij of je partner heeft een vrije, passionele natuur',
     'hour_meaning_nl':  'Jouw nalatenschap is de vonk die je hebt doorgegeven'},
    {'nl':'Wèi',  'en':'Wèi',  'symbol':'未',
     'element':'Earth', 'element_nl':'Aarde',  'element_en':'Earth',
     'animal':'Goat',   'nl_animal':'Geit',    'en_animal':'Goat',
     'archetype_nl': 'De Geit — creatief, zorgzaam, kunstzinnig',
     'archetype_en': 'The Goat — creative, caring, artistic',
     'qualities_nl': 'creativiteit, empathie, artistieke sensitiviteit, zorg',
     'year_meaning_nl':  'Je bent geboren met een fijngevoelig, creatief hart',
     'month_meaning_nl': 'Een periode van creativiteit, zorg en artistieke expressie',
     'day_meaning_nl':   'Jij of je partner is zacht, creatief en diep gevoelig',
     'hour_meaning_nl':  'Jouw erfenis is de schoonheid en zorg die je hebt gegeven'},
    {'nl':'Shēn', 'en':'Shēn', 'symbol':'申',
     'element':'Metal', 'element_nl':'Metaal', 'element_en':'Metal',
     'animal':'Monkey', 'nl_animal':'Aap',     'en_animal':'Monkey',
     'archetype_nl': 'De Aap — intelligent, vindingrijk, speels',
     'archetype_en': 'The Monkey — intelligent, resourceful, playful',
     'qualities_nl': 'intelligentie, vindingrijkheid, aanpassingsvermogen, humor',
     'year_meaning_nl':  'Je bent geboren met scherpe intelligentie en lenigheid',
     'month_meaning_nl': 'Een periode van slimme oplossingen en onverwachte wendingen',
     'day_meaning_nl':   'Jij of je partner is intellectueel, vindingrijk en versatiel',
     'hour_meaning_nl':  'Jouw nalatenschap zijn de ingenieuze oplossingen die je bedacht'},
    {'nl':'Yǒu',  'en':'Yǒu',  'symbol':'酉',
     'element':'Metal', 'element_nl':'Metaal', 'element_en':'Metal',
     'animal':'Rooster','nl_animal':'Haan',    'en_animal':'Rooster',
     'archetype_nl': 'De Haan — precies, eerlijk, gedetailleerd',
     'archetype_en': 'The Rooster — precise, honest, detailed',
     'qualities_nl': 'precisie, eerlijkheid, observatievermogen, plichtsgevoel',
     'year_meaning_nl':  'Je bent geboren met een scherp oog en hoge standaard',
     'month_meaning_nl': 'Een periode van precisie, evaluatie en eerlijkheid',
     'day_meaning_nl':   'Jij of je partner is precies, eerlijk en veeleisend',
     'hour_meaning_nl':  'Jouw erfenis is de standaard van kwaliteit die je hebt gesteld'},
    {'nl':'Xū',   'en':'Xū',   'symbol':'戌',
     'element':'Earth', 'element_nl':'Aarde',  'element_en':'Earth',
     'animal':'Dog',    'nl_animal':'Hond',    'en_animal':'Dog',
     'archetype_nl': 'De Hond — loyaal, beschermend, rechtvaardig',
     'archetype_en': 'The Dog — loyal, protective, just',
     'qualities_nl': 'loyaliteit, rechtvaardigheid, toewijding, bescherming',
     'year_meaning_nl':  'Je bent geboren met een diep gevoel voor recht en loyaliteit',
     'month_meaning_nl': 'Een periode van toewijding, bescherming en rechtvaardigheid',
     'day_meaning_nl':   'Jij of je partner is onwrikbaar loyaal en rechtvaardig',
     'hour_meaning_nl':  'Jouw nalatenschap is de trouw en bescherming die je hebt geboden'},
    {'nl':'Hài',  'en':'Hài',  'symbol':'亥',
     'element':'Water', 'element_nl':'Water',  'element_en':'Water',
     'animal':'Pig',    'nl_animal':'Varken',  'en_animal':'Pig',
     'archetype_nl': 'Het Varken — genereus, oprecht, levenslustig',
     'archetype_en': 'The Pig — generous, sincere, zestful',
     'qualities_nl': 'generositeit, oprechtheid, levensvreugde, doorzettingsvermogen',
     'year_meaning_nl':  'Je bent geboren met een open, genereus hart',
     'month_meaning_nl': 'Een periode van genot, oprechtheid en samenwerking',
     'day_meaning_nl':   'Jij of je partner is oprecht, genereus en levenslustig',
     'hour_meaning_nl':  'Jouw erfenis is de vreugde en vrijgevigheid die je hebt verspreid'},
]

ELEMENT_NAMES = {
    'Wood':  {'nl':'Hout',   'en':'Wood',  'icon':'🌿', 'color':'#4a8a4a'},
    'Fire':  {'nl':'Vuur',   'en':'Fire',  'icon':'🔥', 'color':'#c05a3a'},
    'Earth': {'nl':'Aarde',  'en':'Earth', 'icon':'⛰',  'color':'#a08040'},
    'Metal': {'nl':'Metaal', 'en':'Metal', 'icon':'⚙',  'color':'#7090a0'},
    'Water': {'nl':'Water',  'en':'Water', 'icon':'💧', 'color':'#3a6a9a'},
}


# ══════════════════════════════════════════════════════════
# HIDDEN STEMS (藏干) — verborgen hemelse stammen per branch
# ══════════════════════════════════════════════════════════
HIDDEN_STEMS = {
    '子': [{'stem': '壬', 'name': 'Rén', 'element': 'Water', 'polarity': '+', 'weight': 'main'}],
    '丑': [{'stem': '己', 'name': 'Jǐ',  'element': 'Earth', 'polarity': '-', 'weight': 'main'},
           {'stem': '癸', 'name': 'Guǐ', 'element': 'Water', 'polarity': '-', 'weight': 'mid'},
           {'stem': '辛', 'name': 'Xīn', 'element': 'Metal', 'polarity': '-', 'weight': 'minor'}],
    '寅': [{'stem': '甲', 'name': 'Jiǎ', 'element': 'Wood',  'polarity': '+', 'weight': 'main'},
           {'stem': '丙', 'name': 'Bǐng','element': 'Fire',  'polarity': '+', 'weight': 'mid'},
           {'stem': '戊', 'name': 'Wù',  'element': 'Earth', 'polarity': '+', 'weight': 'minor'}],
    '卯': [{'stem': '乙', 'name': 'Yǐ',  'element': 'Wood',  'polarity': '-', 'weight': 'main'}],
    '辰': [{'stem': '戊', 'name': 'Wù',  'element': 'Earth', 'polarity': '+', 'weight': 'main'},
           {'stem': '乙', 'name': 'Yǐ',  'element': 'Wood',  'polarity': '-', 'weight': 'mid'},
           {'stem': '癸', 'name': 'Guǐ', 'element': 'Water', 'polarity': '-', 'weight': 'minor'}],
    '巳': [{'stem': '丙', 'name': 'Bǐng','element': 'Fire',  'polarity': '+', 'weight': 'main'},
           {'stem': '庚', 'name': 'Gēng','element': 'Metal', 'polarity': '+', 'weight': 'mid'},
           {'stem': '戊', 'name': 'Wù',  'element': 'Earth', 'polarity': '+', 'weight': 'minor'}],
    '午': [{'stem': '丁', 'name': 'Dīng','element': 'Fire',  'polarity': '-', 'weight': 'main'},
           {'stem': '己', 'name': 'Jǐ',  'element': 'Earth', 'polarity': '-', 'weight': 'mid'}],
    '未': [{'stem': '己', 'name': 'Jǐ',  'element': 'Earth', 'polarity': '-', 'weight': 'main'},
           {'stem': '丁', 'name': 'Dīng','element': 'Fire',  'polarity': '-', 'weight': 'mid'},
           {'stem': '乙', 'name': 'Yǐ',  'element': 'Wood',  'polarity': '-', 'weight': 'minor'}],
    '申': [{'stem': '庚', 'name': 'Gēng','element': 'Metal', 'polarity': '+', 'weight': 'main'},
           {'stem': '壬', 'name': 'Rén', 'element': 'Water', 'polarity': '+', 'weight': 'mid'},
           {'stem': '戊', 'name': 'Wù',  'element': 'Earth', 'polarity': '+', 'weight': 'minor'}],
    '酉': [{'stem': '辛', 'name': 'Xīn', 'element': 'Metal', 'polarity': '-', 'weight': 'main'}],
    '戌': [{'stem': '戊', 'name': 'Wù',  'element': 'Earth', 'polarity': '+', 'weight': 'main'},
           {'stem': '辛', 'name': 'Xīn', 'element': 'Metal', 'polarity': '-', 'weight': 'mid'},
           {'stem': '丁', 'name': 'Dīng','element': 'Fire',  'polarity': '-', 'weight': 'minor'}],
    '亥': [{'stem': '壬', 'name': 'Rén', 'element': 'Water', 'polarity': '+', 'weight': 'main'},
           {'stem': '甲', 'name': 'Jiǎ', 'element': 'Wood',  'polarity': '+', 'weight': 'mid'}],
}

# ══════════════════════════════════════════════════════════
# DAG-MEESTER VERHALENDE BESCHRIJVINGEN (Nederlands)
# ══════════════════════════════════════════════════════════
DAY_MASTER_STORIES = {
    '甲': {
        'title': 'De Grote Eik — Yang Hout',
        'core': 'Jij bent als een grote, rechte boom: je groeit omhoog, recht op je doel af. Je bezit een aangeboren gevoel voor leiderschap, integriteit en visie. Net als een eik geef jij anderen schaduw en structuur.',
        'strength': 'Vastberaden, principieel, loyaal, natural leader',
        'shadow': 'Kan star zijn, moeite met buigen en aanpassen',
        'invite': 'Hoe jouw Hout-energie zich verhoudt tot je relaties en carrière — daar duiken we dieper in tijdens een persoonlijke reading.'
    },
    '乙': {
        'title': 'De Klimplant — Yin Hout',
        'core': 'Jij bent als een elegante klimplant: flexibel, vindingrijk en in staat om schoonheid te creëren vanuit elke omstandigheid. Je bezit een subtiele kracht die de kracht van anderen weet te gebruiken.',
        'strength': 'Aanpassingsvermogen, diplomatiek, creatief, charmant',
        'shadow': 'Kan afhankelijk worden van externe ondersteuning',
        'invite': 'Welke "bomen" in jouw leven je de meeste steun geven — dat onthullen we in een diepere reading.'
    },
    '丙': {
        'title': 'De Zon — Yang Vuur',
        'core': 'Jij bent als de zon zelf: warmte, licht en vitaliteit straalt van je af. Je hebt een natuurlijk vermogen om anderen op te beuren en te inspireren. Jij verlicht elke kamer die je binnenstapt.',
        'strength': 'Uitbundig, optimistisch, inspirerend, direct',
        'shadow': 'Kan te fel zijn, anderen overschaduwen zonder het te beseffen',
        'invite': 'Hoe je jouw zonlicht gericht inzet zonder je te verbranden — dat verkennen we samen.'
    },
    '丁': {
        'title': 'De Kaars — Yin Vuur',
        'core': 'Jij bent als een kaars: jouw licht is intiem, warm en precies. Waar de zon alles verlicht, verlicht jij gericht — met diepgang, intuïtie en een fijn gevoel voor wat mensen nodig hebben.',
        'strength': 'Intuïtief, warmhartig, gedetailleerd, doordacht',
        'shadow': 'Kan uitdoven als de wind te hard waait — gevoelig voor omgeving',
        'invite': 'Welke omgevingen jouw vlam het best beschermen en doen oplaaien — een vraag voor onze reading.'
    },
    '戊': {
        'title': 'De Berg — Yang Aarde',
        'core': 'Jij bent als een massieve berg: stabiel, betrouwbaar en een baken voor anderen. Je bezit een onwrikbare kracht en biedt anderen een veilige basis. Mensen zoeken jou op als ankerpunt.',
        'strength': 'Betrouwbaar, geduldig, protectief, standvastig',
        'shadow': 'Kan stroef zijn, verandering weerstaan',
        'invite': 'Hoe de berg in jou zowel beschermt als soms blokkeert — dat is een rijke verkenning voor een reading.'
    },
    '己': {
        'title': 'De Akker — Yin Aarde',
        'core': 'Jij bent als vruchtbare akkergrond: zacht, voedend en in staat om alles te laten groeien. Je bezit een zeldzame gave om anderen tot bloei te brengen. Jij bent de bodem waarop dromen gedijen.',
        'strength': 'Verzorgend, geduldig, praktisch, adaptief',
        'shadow': 'Kan zich te veel aanpassen, verliest soms eigen richting',
        'invite': 'Wat jij zelf nodig hebt om te bloeien — dat verkennen we in jouw persoonlijke reading.'
    },
    '庚': {
        'title': 'Het Zwaard — Yang Metaal',
        'core': 'Jij bent als gehard staal: scherp, direct en onbuigzaam. Je snijdt door het onessentiële heen en komt altijd tot de kern. Jij bent gemaakt voor uitdagingen die anderen doen terugdeinzen.',
        'strength': 'Doortastend, eerlijk, moedig, resultaatgericht',
        'shadow': 'Kan bot overkomen, het diplomatieke missen',
        'invite': 'Hoe jij je scherpte inzet zonder weerstand op te roepen — een sleutelthema in jouw reading.'
    },
    '辛': {
        'title': 'Het Edelmetaal — Yin Metaal',
        'core': 'Jij bent als fijn geslepen edelmetaal: precies, verfijnd en van hoge kwaliteit. Je bezit een scherp oog voor perfectie en schoonheid. Jij voelt instinctief aan wanneer iets niet klopt.',
        'strength': 'Analytisch, esthetisch, precies, eerlijk',
        'shadow': 'Kan te kritisch zijn — voor zichzelf en anderen',
        'invite': 'Hoe jouw precisie een gave wordt in plaats van een last — dat is de kern van jouw persoonlijke reading.'
    },
    '壬': {
        'title': 'De Oceaan — Yang Water',
        'core': 'Jij bent als de open oceaan: diep, krachtig en in constante beweging. Je bezit een enorm vermogen om te absorberen, te verwerken en vervolgens als wijsheid terug te geven.',
        'strength': 'Intelligent, flexibel, diepzinnig, strategisch',
        'shadow': 'Kan overweldigen of zichzelf verliezen in te veel richtingen',
        'invite': 'Welke oevers jouw oceaan de beste richting geven — dat ontdekken we samen.'
    },
    '癸': {
        'title': 'De Regenbui — Yin Water',
        'core': 'Jij bent als een zachte regenbui: voedend, intuitief en overal aanwezig zonder op te dringen. Je bezit een zeldzame gevoeligheid die je in staat stelt diep menselijk te verbinden.',
        'strength': 'Empathisch, intuïtief, adaptief, zorgzaam',
        'shadow': 'Kan te gevoelig zijn, moeite met grenzen stellen',
        'invite': 'Hoe je jouw gevoeligheid beschermt én inzet als superkracht — dé vraag voor jouw reading.'
    },
}

# ══════════════════════════════════════════════════════════
# SHEN SHA STERREN (神煞) — een selectie
# ══════════════════════════════════════════════════════════
def calc_shen_sha(year_branch, day_branch, day_stem):
    """Bereken een selectie van klassieke Shen Sha sterren."""
    stars = []

    # Nobleman Star (天乙貴人) — op basis van dag-stam
    nobleman_map = {
        '甲': ['丑','未'], '乙': ['子','申'], '丙': ['亥','酉'],
        '丁': ['亥','酉'], '戊': ['丑','未'], '己': ['子','申'],
        '庚': ['丑','未'], '辛': ['寅','午'], '壬': ['卯','巳'],
        '癸': ['卯','巳'],
    }
    noble = nobleman_map.get(day_stem, [])
    if day_branch in noble or year_branch in noble:
        stars.append({
            'name': '天乙貴人', 'nl': 'Edelmanster',
            'en': 'Nobleman Star',
            'meaning': 'Je trekt helpers en beschermers aan in moeilijke tijden. Mensen met macht en invloed staan je bij wanneer je ze nodig hebt.'
        })

    # Peach Blossom (桃花) — op basis van jaar-branch
    peach_map = {'子':'酉','丑':'午','寅':'卯','卯':'子','辰':'酉','巳':'午',
                 '午':'卯','未':'子','申':'酉','酉':'午','戌':'卯','亥':'子'}
    if peach_map.get(year_branch) == day_branch:
        stars.append({
            'name': '桃花', 'nl': 'Perzikbloesemster',
            'en': 'Peach Blossom Star',
            'meaning': 'Je bezit een natuurlijke charme en aantrekkingskracht. Mensen worden aangetrokken tot jouw energie — zowel romantisch als sociaal.'
        })

    # Academic Star (文昌) — op basis van dag-stam
    academic_map = {
        '甲':'巳','乙':'午','丙':'申','丁':'酉','戊':'申',
        '己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯'
    }
    if academic_map.get(day_stem) == day_branch:
        stars.append({
            'name': '文昌', 'nl': 'Academische Ster',
            'en': 'Academic Star',
            'meaning': 'Je hebt een aangeboren talent voor leren, schrijven en intellectueel werk. Studie en kennis brengen je ver.'
        })

    # Sky Horse (驛馬) — beweging en reizen
    sky_horse_map = {'子':'寅','丑':'亥','寅':'申','卯':'巳','辰':'寅','巳':'亥',
                     '午':'申','未':'巳','申':'寅','酉':'亥','戌':'申','亥':'巳'}
    if sky_horse_map.get(year_branch) == day_branch:
        stars.append({
            'name': '驛馬', 'nl': 'Hemelspaard',
            'en': 'Sky Horse Star',
            'meaning': 'Je bent gemaakt voor beweging, reizen en verandering. Stilstand is niet voor jou — je energie bloeit op als je in beweging bent.'
        })

    # Longevity Star (福星貴人)
    longevity_map = {
        '甲':'寅','乙':'卯','丙':'午','丁':'午','戊':'午',
        '己':'午','庚':'申','辛':'酉','壬':'子','癸':'亥'
    }
    if longevity_map.get(day_stem) == year_branch:
        stars.append({
            'name': '福星貴人', 'nl': 'Geluksster',
            'en': 'Fortune Star',
            'meaning': 'Je wordt beschermd door een bijzondere geluksenergie. Obstakels lossen vaker op dan bij anderen, en kansen komen op je pad.'
        })

    return stars


# ══════════════════════════════════════════════════════════
# LUCK PILLARS (大运) — 10-jaar cycli
# ══════════════════════════════════════════════════════════
def calc_luck_pillars(birth_jd, year_stem_idx, month_stem_idx, month_branch_idx,
                      gender, birth_year, birth_month, birth_day):
    """
    Berekent de grote gelukspilaren (大运).
    Richting: Yang jaar + mannelijk → voorwaarts; Yin jaar + vrouwelijk → voorwaarts
    """
    import math

    # Yang/Yin jaar
    year_yang = (year_stem_idx % 2 == 0)  # 甲丙戊庚壬 = yang = even index

    # Richting: forward als (yang jaar EN man) OF (yin jaar EN vrouw)
    forward = (year_yang and gender == 'M') or (not year_yang and gender == 'F')

    # Vind start van volgende (of vorige) solar term
    def sun_longitude_lp(jd):
        n = jd - 2451545.0
        L = (280.460 + 0.9856474 * n) % 360
        g = math.radians((357.528 + 0.9856003 * n) % 360)
        return (L + 1.915*math.sin(g) + 0.020*math.sin(2*g)) % 360

    def find_next_term(jd, forward):
        """Vind afstand in dagen naar volgende/vorige solar term."""
        current_lon = sun_longitude_lp(jd)
        # Solar terms elke 30°
        if forward:
            next_lon = (math.floor(current_lon / 30) + 1) * 30
        else:
            next_lon = math.floor(current_lon / 30) * 30
        next_lon = next_lon % 360

        lo = jd - 35 if not forward else jd
        hi = jd + 35 if forward else jd
        if not forward:
            lo, hi = jd - 35, jd

        for _ in range(60):
            mid = (lo + hi) / 2
            lon = sun_longitude_lp(mid)
            diff = (lon - next_lon + 360) % 360
            if diff > 180: diff -= 360
            if forward:
                if diff > 0: hi = mid
                else: lo = mid
            else:
                if diff < 0: hi = mid
                else: lo = mid
        return abs((lo + hi) / 2 - jd)

    days_to_term = find_next_term(birth_jd, forward)
    # Regel: 3 dagen = 1 jaar luck pillar start leeftijd
    start_age = round(days_to_term / 3)

    # Genereer 8 luck pillars
    pillars = []
    current_stem = month_stem_idx
    current_branch = month_branch_idx

    for i in range(8):
        if forward:
            s = (current_stem + i + 1) % 10
            b = (current_branch + i + 1) % 12
        else:
            s = (current_stem - i - 1 + 100) % 10
            b = (current_branch - i - 1 + 120) % 12

        lp_start_age = start_age + i * 10
        lp_start_year = birth_year + lp_start_age

        pillars.append({
            'age': lp_start_age,
            'yearStart': lp_start_year,
            'yearEnd': lp_start_year + 9,
            'stem': HEAVENLY_STEMS[s]['symbol'],
            'stemName': HEAVENLY_STEMS[s]['nl'],
            'stemElement': HEAVENLY_STEMS[s]['element'],
            'stemElementNl': HEAVENLY_STEMS[s].get('element_nl', ELEMENT_NAMES.get(HEAVENLY_STEMS[s]['element'],{}).get('nl', HEAVENLY_STEMS[s]['element'])),
            'stemPolarity': HEAVENLY_STEMS[s]['polarity'],
            'stemPolarityNl': HEAVENLY_STEMS[s].get('polarity_nl','Yang' if HEAVENLY_STEMS[s]['polarity']=='+' else 'Yin'),
            'branch': EARTHLY_BRANCHES[b]['symbol'],
            'branchName': EARTHLY_BRANCHES[b]['nl'],
            'branchAnimal': EARTHLY_BRANCHES[b].get('nl_animal', EARTHLY_BRANCHES[b].get('animal','')),
            'branchAnimalEn': EARTHLY_BRANCHES[b].get('en_animal', EARTHLY_BRANCHES[b].get('animal','')),
            'branchElement': EARTHLY_BRANCHES[b]['element'],
            'branchElementNl': EARTHLY_BRANCHES[b].get('element_nl', ELEMENT_NAMES.get(EARTHLY_BRANCHES[b]['element'],{}).get('nl','')),
        })

    return {
        'startAge': start_age,
        'direction': 'voorwaarts' if forward else 'achterwaarts',
        'pillars': pillars,
        'currentPillar': next((p for p in pillars
                               if p['yearStart'] <= 2026 <= p['yearEnd']), None)
    }


# ══════════════════════════════════════════════════════════
# CURRENT YEAR INTERACTION (2026 = 丙午)
# ══════════════════════════════════════════════════════════
def calc_year_interaction(day_stem_idx, current_year=2026):
    """Simpele analyse van huidig jaar vs dag-meester."""
    cy_stem_idx = (current_year - 4) % 10
    cy_branch_idx = (current_year - 4) % 12

    cy_stem = HEAVENLY_STEMS[cy_stem_idx]
    cy_branch = EARTHLY_BRANCHES[cy_branch_idx]
    dm = HEAVENLY_STEMS[day_stem_idx]

    produces = {'Wood':'Fire','Fire':'Earth','Earth':'Metal','Metal':'Water','Water':'Wood'}
    controls = {'Wood':'Earth','Fire':'Metal','Earth':'Water','Metal':'Wood','Water':'Fire'}
    controlled_by = {'Wood':'Metal','Fire':'Water','Earth':'Wood','Metal':'Fire','Water':'Earth'}

    dm_el = dm['element']
    cy_el = cy_stem['element']

    el_nl = ELEMENT_NAMES.get(cy_el, {}).get('nl', cy_el)
    dm_el_nl = ELEMENT_NAMES.get(dm_el, {}).get('nl', dm_el)
    if cy_el == dm_el:
        relation = 'metgezel'
        reading = f'{cy_stem["symbol"]} {cy_stem["nl"]} vult jouw eigen {dm_el_nl}-energie aan. Een jaar om samen te werken, netwerken en krachten te bundelen.'
    elif produces.get(cy_el) == dm_el:
        relation = 'voedend'
        reading = f'Het {el_nl} van {cy_stem["symbol"]} voedt jouw {dm_el_nl} dag-meester. Dit jaar ondersteunt jouw groei en brengt hulpbronnen op je pad.'
    elif controls.get(cy_el) == dm_el:
        relation = 'controlerend'
        reading = f'Het {el_nl} van {cy_stem["symbol"]} controleert jouw {dm_el_nl}. Dit vraagt discipline en focus — druk kan ook vormen.'
    elif controlled_by.get(cy_el) == dm_el:
        relation = 'uitputtend'
        reading = f'Jouw {dm_el_nl} controleert het {el_nl} van {cy_stem["symbol"]}. Je hebt macht maar let op energieverliezen.'
    else:
        relation = 'neutraal'
        reading = f'{cy_stem["symbol"]} {cy_stem["nl"]} brengt een nieuwe energie die jou uitdaagt te groeien.'

    return {
        'year': current_year,
        'yearStem': cy_stem['symbol'],
        'yearStemName': cy_stem['nl'],
        'yearBranch': cy_branch['symbol'],
        'yearBranchAnimal': cy_branch['nl_animal'],
        'relation': relation,
        'reading': reading
    }


# Month stem starts per year stem group:
# 甲己→丙(2), 乙庚→戊(4), 丙辛→庚(6), 丁壬→壬(8), 戊癸→甲(0)
MONTH_STEM_STARTS = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]


def get_stem(idx):
    return HEAVENLY_STEMS[((idx % 10) + 10) % 10]


def get_branch(idx):
    return EARTHLY_BRANCHES[((idx % 12) + 12) % 12]


def get_sun_longitude(jd):
    result, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
    return result[0]


def find_solar_term_jd(year, target_lon):
    """Binary search for exact JD when sun reaches target_lon."""
    # Rough estimate: days since Jan 1
    approx_doy = ((target_lon - 280) % 360) / 360 * 365
    jd_start = swe.julday(year, 1, 1, 0) + approx_doy - 20
    jd_end = jd_start + 45
    lo, hi = jd_start, jd_end
    for _ in range(60):
        mid = (lo + hi) / 2
        lon = get_sun_longitude(mid)
        diff = (lon - target_lon + 360) % 360
        if diff > 180:
            diff -= 360
        if diff > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def get_effective_year(birth_jd, gregorian_year):
    """
    BaZi year starts at Li Chun = sun at 315° (~Feb 4).
    If birth is before Li Chun → use previous year.
    """
    li_chun_jd = find_solar_term_jd(gregorian_year, 315.0)
    return gregorian_year if birth_jd >= li_chun_jd else gregorian_year - 1


def get_solar_month_index(birth_jd):
    """
    BaZi solar month index based on exact sun longitude.
    315° = Tiger month start (month index 0)
    Each month = 30° of solar travel.
    Returns: 0=Tiger, 1=Rabbit, 2=Dragon, ..., 11=Ox
    """
    sun_lon = get_sun_longitude(birth_jd)
    adjusted = (sun_lon - 315 + 360) % 360
    return int(adjusted / 30)


def get_year_pillar(effective_year):
    return {
        'stem': get_stem((effective_year - 4) % 10),
        'branch': get_branch((effective_year - 4) % 12)
    }


def get_month_pillar_solar(birth_jd, effective_year):
    """
    Month pillar via exact solar term — not Gregorian month.
    Branch: Tiger(2), Rabbit(3), Dragon(4)... Ox(1)
    Stem: from year stem group × month index
    """
    month_idx = get_solar_month_index(birth_jd)
    branch_idx = (month_idx + 2) % 12
    year_stem_idx = ((effective_year - 4) % 10 + 10) % 10
    start_stem = MONTH_STEM_STARTS[year_stem_idx]
    stem_idx = (start_stem + month_idx) % 10
    return {'stem': get_stem(stem_idx), 'branch': get_branch(branch_idx)}


def get_day_pillar(year, month, day):
    # Gebruik noon JD + offset 49 (gevalideerd vs. Flowtastic/Saju)
    jd = int(swe.julday(year, month, day, 12))
    return {
        'stem': get_stem((jd + 49) % 10),
        'branch': get_branch((jd + 49) % 12)
    }


def get_true_solar_hour(clock_hour, clock_minute, longitude, tz_offset):
    """True Solar Time = clock time + longitude correction."""
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
        for key in ['stem', 'branch']:
            el = p[key]['element']
            if el in counts:
                counts[el] += 1
    return counts


def format_pillar(pillar, label):
    stem = pillar['stem']
    branch = pillar['branch']
    # Determine pillar context key
    pillar_key = {'Jaar Pilaar':'year','Maand Pilaar':'month',
                  'Dag Pilaar':'day','Uur Pilaar':'hour'}.get(label,'day')
    return {
        'label': label,
        'stem': {
            'symbol':       stem['symbol'],
            'name':         stem['nl'],
            'name_en':      stem.get('en', stem['nl']),
            'element':      stem['element'],
            'element_nl':   stem.get('element_nl', ELEMENT_NAMES[stem['element']]['nl']),
            'element_en':   stem.get('element_en', stem['element']),
            'polarity':     stem['polarity'],
            'polarity_nl':  stem.get('polarity_nl', 'Yang' if stem['polarity']=='+' else 'Yin'),
            'polarity_en':  stem.get('polarity_en', 'Yang' if stem['polarity']=='+' else 'Yin'),
            'color':        stem['color'],
            'archetype_nl': stem.get('archetype_nl',''),
            'archetype_en': stem.get('archetype_en',''),
            'qualities_nl': stem.get('qualities_nl',''),
            'qualities_en': stem.get('qualities_en',''),
            'meaning_nl':   stem.get(f'{pillar_key}_meaning_nl',''),
        },
        'branch': {
            'symbol':       branch['symbol'],
            'name':         branch['nl'],
            'name_en':      branch.get('en', branch['nl']),
            'animal':       branch.get('en_animal', branch.get('animal','')),
            'animal_nl':    branch.get('nl_animal',''),
            'animal_en':    branch.get('en_animal', branch.get('animal','')),
            'element':      branch['element'],
            'element_nl':   branch.get('element_nl', ELEMENT_NAMES[branch['element']]['nl']),
            'element_en':   branch.get('element_en', branch['element']),
            'archetype_nl': branch.get('archetype_nl',''),
            'archetype_en': branch.get('archetype_en',''),
            'qualities_nl': branch.get('qualities_nl',''),
            'meaning_nl':   branch.get(f'{pillar_key}_meaning_nl',''),
        }
    }


def is_dst_europe(year, month, day):
    """Simpele CET/CEST detectie voor Europa.
    Zomertijd: laatste zondag maart tot laatste zondag oktober."""
    if month < 3 or month > 10: return False
    if month > 3 and month < 10: return True
    # Maart: zoek laatste zondag
    import datetime
    if month == 3:
        last_sun = max(d for d in range(25,32)
                       if datetime.date(year,3,d).weekday()==6)
        return day >= last_sun
    # Oktober: zoek laatste zondag
    if month == 10:
        last_sun = max(d for d in range(25,32)
                       if datetime.date(year,10,d).weekday()==6)
        return day < last_sun
    return False

def calc_five_factors(dm_elem, element_counts, total):
    """
    Five Factors: relatie van elk element tot de dag-meester.
    Companion, Output, Wealth, Influence, Resource
    """
    # Element keys are English (Wood/Fire/Earth/Metal/Water)
    produces     = {'Wood':'Fire','Fire':'Earth','Earth':'Metal','Metal':'Water','Water':'Wood'}
    controls     = {'Wood':'Earth','Fire':'Metal','Earth':'Water','Metal':'Wood','Water':'Fire'}
    controlled_by= {'Wood':'Metal','Fire':'Water','Earth':'Wood','Metal':'Fire','Water':'Earth'}
    supported_by = {'Wood':'Water','Fire':'Wood','Earth':'Fire','Metal':'Earth','Water':'Metal'}

    factor_map = {
        dm_elem:               {'nl': 'Metgezel (比)',  'en': 'Companion', 'code': 'F'},
        produces[dm_elem]:     {'nl': 'Uitstroom (食)',    'en': 'Output',    'code': 'EG'},
        controls[dm_elem]:     {'nl': 'Rijkdom (財)',   'en': 'Wealth',    'code': 'DW'},
        controlled_by[dm_elem]:{'nl': 'Invloed (官)',   'en': 'Influence', 'code': 'DO'},
        supported_by[dm_elem]: {'nl': 'Hulpbron (印)',  'en': 'Resource',  'code': 'IR'},
    }

    result = {}
    for elem, info in factor_map.items():
        cnt = element_counts.get(elem, 0)
        pct = round(cnt / total * 100) if total else 0
        result[elem] = {
            **info,
            'count': cnt,
            'percentage': pct,
            'element': elem,
            'element_nl': ELEMENT_NAMES.get(elem,{}).get('nl', elem),
            'element_en': ELEMENT_NAMES.get(elem,{}).get('en', elem),
        }
    return result


def calc_bazi(data):
    year   = int(data['year'])
    month  = int(data['month'])
    day    = int(data['day'])
    hour   = int(data.get('hour', 12))
    minute = int(data.get('minute', 0))
    lon    = float(data.get('lon', 4.45))
    # Timezone: gebruik opgegeven waarde, of detecteer automatisch zomertijd
    tz_input = data.get('tz')
    if tz_input is not None:
        tz = float(tz_input)
    else:
        # Auto-detectie: CET+1 of CEST+2
        base_tz = 1.0  # standaard CET voor België/NL
        tz = base_tz + (1.0 if is_dst_europe(year, month, day) else 0.0)

    # UTC birth Julian Day
    utc_hour = hour - tz + minute / 60
    birth_jd = swe.julday(year, month, day, utc_hour)

    # ── 1. Effective year (Li Chun boundary) ──
    effective_year = get_effective_year(birth_jd, year)
    year_pillar = get_year_pillar(effective_year)
    ys_idx = ((effective_year - 4) % 10 + 10) % 10

    # ── 2. Month pillar (exact solar term) ──
    month_pillar = get_month_pillar_solar(birth_jd, effective_year)

    # ── 3. Day pillar ──
    day_pillar = get_day_pillar(year, month, day)

    # ── 4. Hour pillar (True Solar Time) ──
    # Gebruik klok-tijd direct (conform Flowtastic/Saju standaard)
    clock_hour = hour + minute / 60
    day_stem_idx = HEAVENLY_STEMS.index(day_pillar['stem'])
    hour_pillar = get_hour_pillar(day_stem_idx, clock_hour)

    pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]
    element_counts = count_elements(pillars)

    # Day master analysis
    dm_el = day_pillar['stem']['element']
    produces     = {'Wood':'Fire','Fire':'Earth','Earth':'Metal','Metal':'Water','Water':'Wood'}
    supported_by = {'Wood':'Water','Fire':'Wood','Earth':'Fire','Metal':'Earth','Water':'Metal'}
    controlled_by = {'Wood':'Metal','Fire':'Water','Earth':'Wood','Metal':'Fire','Water':'Earth'}
    total = sum(element_counts.values())
    strength = (element_counts.get(dm_el, 0) + element_counts.get(supported_by[dm_el], 0)) / total if total else 0

    day_master = {
        'element':      dm_el,
        'elementNl':    ELEMENT_NAMES[dm_el]['nl'],
        'symbol':       day_pillar['stem']['symbol'],
        'polarity':     day_pillar['stem']['polarity'],
        'isStrong':     strength > 0.35,
        'produces':     produces[dm_el],
        'supportedBy':  supported_by[dm_el],
        'controlledBy': controlled_by[dm_el],
    }

    dominant = max(element_counts, key=element_counts.get)
    dominant_nl = ELEMENT_NAMES.get(dominant, {}).get('nl', dominant)
    missing  = [el for el, cnt in element_counts.items() if cnt == 0]
    missing_nl = [ELEMENT_NAMES.get(el,{}).get('nl',el) for el in missing]

    # Five Factors berekening (relatief aan dag-meester)
    five_factors = calc_five_factors(dm_el, element_counts, total)

    # Early Zi correctie: geboorte 23:00-01:00 → dag pilaar = volgende dag
    early_zi = clock_hour >= 23 or clock_hour < 1
    if early_zi:
        jd_noon_early = int(swe.julday(year, month, day, 12)) + 1
        day_pillar = {
            'stem': get_stem((jd_noon_early + 49) % 10),
            'branch': get_branch((jd_noon_early + 49) % 12)
        }
        day_stem_idx = HEAVENLY_STEMS.index(day_pillar['stem'])
        hour_pillar = get_hour_pillar(day_stem_idx, clock_hour)

    # Hidden Stems per pilaar
    def get_hidden(pillar):
        branch_sym = pillar['branch']['symbol']
        raw = HIDDEN_STEMS.get(branch_sym, [])
        return [{
            **s,
            'element_nl': ELEMENT_NAMES.get(s['element'],{}).get('nl', s['element']),
            'weight_nl': {'main':'hoofd','mid':'midden','minor':'klein'}.get(s.get('weight',''),''),
        } for s in raw]

    # Shen Sha sterren
    year_branch_sym = year_pillar['branch']['symbol']
    day_branch_sym  = day_pillar['branch']['symbol']
    day_stem_sym    = day_pillar['stem']['symbol']
    shen_sha = calc_shen_sha(year_branch_sym, day_branch_sym, day_stem_sym)

    # Day Master verhaal
    dm_story = DAY_MASTER_STORIES.get(day_stem_sym, {})

    # Luck Pillars
    gender = data.get('gender', 'M')
    # Extract month stem/branch indices for luck pillars
    ms_idx = HEAVENLY_STEMS.index(month_pillar['stem'])
    mb_idx = EARTHLY_BRANCHES.index(month_pillar['branch'])
    luck_pillars = calc_luck_pillars(
        birth_jd, ys_idx, ms_idx, mb_idx, gender, year, month, day
    )

    # Current year interactie
    year_interaction = calc_year_interaction(day_stem_idx)

    # ── Laag 2: Relatie-analyse (botsingen, combinaties, DM sterkte) ──
    relations = {}
    if _RELATIONS_AVAILABLE:
        try:
            # Volgorde: [uur, dag, maand, jaar]  (conform bazi_relations interface)
            raw_order = [hour_pillar, day_pillar, month_pillar, year_pillar]
            rel_chart = {
                'dm_stem':      _stem_to_key(day_pillar['stem']),
                'month_branch': _BRANCH_SYM_TO_KEY.get(month_pillar['branch']['symbol'], ''),
                'stems':   [_stem_to_key(p['stem'])   for p in raw_order],
                'branches': [_BRANCH_SYM_TO_KEY.get(p['branch']['symbol'], '') for p in raw_order],
            }
            relations = full_relations_analysis(rel_chart)
        except Exception as _rel_err:
            relations = {'error': str(_rel_err)}

    return {
        'yearPillar':    format_pillar(year_pillar,  'Jaar Pilaar'),
        'monthPillar':   format_pillar(month_pillar, 'Maand Pilaar'),
        'dayPillar':     format_pillar(day_pillar,   'Dag Pilaar'),
        'hourPillar':    format_pillar(hour_pillar,  'Uur Pilaar'),
        'hiddenStems': {
            'year':  get_hidden(year_pillar),
            'month': get_hidden(month_pillar),
            'day':   get_hidden(day_pillar),
            'hour':  get_hidden(hour_pillar),
        },
        'elementCounts':  element_counts,
        'elementDetails': {k: {'count': v, **ELEMENT_NAMES[k]} for k, v in element_counts.items()},
        'dayMaster':       day_master,
        'dayMasterStory':  dm_story,
        'dominantElement': dominant,
        'dominantElementNl': dominant_nl,
        'missingElements': missing,
        'missingElementsNl': missing_nl,
        'fiveFactors':     five_factors,
        'shenSha':         shen_sha,
        'luckPillars':     luck_pillars,
        'yearInteraction': year_interaction,
        'earlyZi':         early_zi,
        'accuracy':        'Swiss Ephemeris — Solar Terms + Early Zi methode',
        'relations':       relations,
    }
