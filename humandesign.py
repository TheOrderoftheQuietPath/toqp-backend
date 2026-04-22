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

GATE_DATA = {
    1:{'nl':'Zelfexpressie','en':'Self-Expression','keynote_nl':'Creatief zijn is jouw levensdoel','shadow_nl':'Je creativiteit inslikken uit angst voor oordeel','gift_nl':'Authentieke creatie die anderen inspireert'},
    2:{'nl':'De Ontvanger','en':'The Receptive','keynote_nl':'Jij weet intuïtief de richting — het Hogere Zelf stuurt je','shadow_nl':'Gebrek aan zelfvertrouwen in jouw intuïtieve richting','gift_nl':'Natuurlijk leiderschap door overgave aan de stroom'},
    3:{'nl':'Volgorde','en':'Ordering','keynote_nl':'Mutatie vraagt geduld — jij brengt orde uit chaos','shadow_nl':'Frustratie bij het wachten op de juiste timing','gift_nl':'Transformeren terwijl je stabiel blijft'},
    4:{'nl':'Formulering','en':'Formulization','keynote_nl':'Jij formuleert antwoorden op fundamentele vragen','shadow_nl':'Angstig zijn dat je antwoorden niet correct zijn','gift_nl':'Helder uitdrukken van oplossingen die anderen helpen'},
    5:{'nl':'Vaste patronen','en':'Fixed Patterns','keynote_nl':'Universele ritmes en patronen — jij belichaamt de natuur','shadow_nl':'Rigiditeit in routines of gebrek aan structuur','gift_nl':'Consistentie die anderen houvast biedt'},
    6:{'nl':'Wrijving','en':'Friction','keynote_nl':'Door wrijving ontstaat warmte — jij schept diepgaand contact','shadow_nl':'Conflictvermijding of onnodige confrontatie','gift_nl':'Diplomatie die echte verbinding creëert'},
    7:{'nl':'De Rol van het Zelf','en':'The Role of the Self','keynote_nl':'Leiderschap via democraat zijn — jij dient het collectief','shadow_nl':'Autoritair gedrag of passief afwachten','gift_nl':'Inspireren van anderen via jouw integriteit'},
    8:{'nl':'Bijdrage','en':'Contribution','keynote_nl':'Jouw unieke bijdrage maakt een verschil — wees moedig','shadow_nl':'Je bijdrage inslikken uit angst voor afwijzing','gift_nl':'Stijlvolle expressie die anderen wakker maakt'},
    9:{'nl':'Focus','en':'Focus','keynote_nl':'Toewijding aan het detail — jij verdiept alles wat je aanpakt','shadow_nl':'Obsessie met details of gebrek aan focus','gift_nl':'Concentratie die tot meesterschap leidt'},
    10:{'nl':'Het Gedrag van het Zelf','en':'Behavior of the Self','keynote_nl':'Zelfliefde is de sleutel — hoe jij met jezelf omgaat inspireert','shadow_nl':'Zelfkritiek of aanpassen ten koste van jezelf','gift_nl':'Authenticiteit die anderen toestemming geeft zichzelf te zijn'},
    11:{'nl':'Ideeën','en':'Ideas','keynote_nl':'Jij bruist van ideeën en inspiratie voor de wereld','shadow_nl':'Overweldigd door te veel ideeën zonder uitvoering','gift_nl':'Het zaaien van ideeën die de wereld verrijken'},
    12:{'nl':'Voorzichtigheid','en':'Caution','keynote_nl':'Jij deelt je diepste zelf wanneer de timing klopt','shadow_nl':'Jezelf verstoppen of te vroeg delen','gift_nl':'Krachtige expressie die muteert wanneer de timing juist is'},
    13:{'nl':'De Luisteraar','en':'The Listener','keynote_nl':'Mensen openen zich voor jou — jij draagt hun verhalen','shadow_nl':'Te veel andermans verhalen dragen zonder eigen verhaal','gift_nl':'Bewaren van wijsheid voor het perfecte moment van delen'},
    14:{'nl':'Kracht & Vaardigheden','en':'Power Skills','keynote_nl':'Jij bezit de energie en middelen om richting te geven','shadow_nl':'Energie verspillen aan wat niet bij jou hoort','gift_nl':'Competentie gekoppeld aan eigenwaarde'},
    15:{'nl':'Uitersten','en':'Extremes','keynote_nl':'Jij belichaamt de extremen en omarmt ze allemaal','shadow_nl':'Duwen naar extremen of klem zitten in de middenweg','gift_nl':'Aanvaarding van de volledige menselijke natuur'},
    16:{'nl':'Vaardigheden','en':'Skills','keynote_nl':'Enthousiasme en talent — jij experimenteert tot perfectie','shadow_nl':'Oppervlakkige kennis of verdieping vermijden','gift_nl':'Meesterschap via toewijding en herhaalde oefening'},
    17:{'nl':'Meningen','en':'Opinions','keynote_nl':'Jij biedt logische organisatie en meningen die samenhang brengen','shadow_nl':'Vastklampen aan meningen of gebrek aan standpunt','gift_nl':'Helder denken dat anderen richting geeft'},
    18:{'nl':'Correctie','en':'Correction','keynote_nl':'Jij ziet direct wat kan verbeteren — perfectionisme als gave','shadow_nl':'Kritiek die pijn doet of alles als imperfect zien','gift_nl':'Corrigerende kracht die dient vanuit liefde'},
    19:{'nl':'Willen','en':'Wanting','keynote_nl':'Jij voelt wat anderen nodig hebben — een fijngevoelige antenne','shadow_nl':'Afhankelijkheid of niet weten wat jij zelf nodig hebt','gift_nl':'Gevoeligheid voor behoeften die gemeenschap bouwt'},
    20:{'nl':'Het Nu','en':'The Now','keynote_nl':'Aanwezig zijn is jouw kracht — jij leeft en spreekt in het Nu','shadow_nl':'Verstrikt raken in verleden of toekomst','gift_nl':'Aanwezigheid die anderen in het moment brengt'},
    21:{'nl':'Controle','en':'Control','keynote_nl':'Jij weet hoe materiële middelen worden gecontroleerd','shadow_nl':'Controledrang of loslaten van wat nodig is','gift_nl':'Verantwoordelijk beheer voor het grotere geheel'},
    22:{'nl':'Gratie','en':'Openness','keynote_nl':'Emotionele gratie en wachten op de perfecte timing','shadow_nl':'Emotionele reacties op het verkeerde moment','gift_nl':'Schoonheid en gratie in emotionele expressie'},
    23:{'nl':'Assimilatie','en':'Assimilation','keynote_nl':'Jij vertaalt individuele inzichten naar taal die de wereld begrijpt','shadow_nl':'Begrepen willen worden door iedereen','gift_nl':'Simplificatie van complexe inzichten'},
    24:{'nl':'Rationalisering','en':'Rationalization','keynote_nl':'Jij denkt in cirkels totdat het antwoord zich openbaart','shadow_nl':'Obsessief herkauwen of het antwoord forçeren','gift_nl':'Diepe contemplatie die tot originele inzichten leidt'},
    25:{'nl':'De Geest van het Zelf','en':'Spirit of the Self','keynote_nl':'Universele liefde — jij liefhebt zonder conditie','shadow_nl':'Naïviteit of gebrek aan persoonlijke grenzen','gift_nl':'Onvoorwaardelijke liefde als kosmische kracht'},
    26:{'nl':'De Egoïst','en':'The Egoist','keynote_nl':'Het ego in dienst van het geheel — jij overtuigt via verhalen','shadow_nl':'Manipulatie of overdreven zelfpromotie','gift_nl':'Overtuigend brengen van de juiste boodschap'},
    27:{'nl':'Voeding','en':'Caring','keynote_nl':'Jij voedt en verzorgt — de essentie van zorg en overleven','shadow_nl':'Voor anderen zorgen ten koste van jezelf','gift_nl':'Liefdevolle zorg die gemeenschappen in stand houdt'},
    28:{'nl':'Het Spel van het Leven','en':'Game of Life','keynote_nl':'Jij zoekt de zin van het leven in de strijd — moed en betekenis','shadow_nl':'Zinloze strijd of opgeven wanneer het zwaar wordt','gift_nl':'Moed om te leven met volle toewijding'},
    29:{'nl':'Doorzettingsvermogen','en':'Perseverance','keynote_nl':'Ja zeggen is jouw kracht — doorzetten maakt het verschil','shadow_nl':'Ja zeggen zonder te weten waaraan je je committeert','gift_nl':'Overgave aan het leven als weg naar ontdekking'},
    30:{'nl':'Vuren','en':'Feelings','keynote_nl':'Emotionele vurigheid — de brandstof voor nieuwe ervaringen','shadow_nl':'Vastlopen in onvervulde verlangens','gift_nl':'De vlam van verlangen als motor voor het leven'},
    31:{'nl':'Invloed','en':'Influence','keynote_nl':'Jij leidt wanneer anderen jou kiezen — democratisch leiderschap','shadow_nl':'Leiderschap opdringen of verborgen houden','gift_nl':'Invloed via authenticiteit en zichtbaarheid'},
    32:{'nl':'Continuïteit','en':'Continuity','keynote_nl':'Jij voelt instinctief wat de tand des tijds doorstaat','shadow_nl':'Angst voor verandering of vastklampen aan het verleden','gift_nl':'Wijsheid in het bewaren van wat waardevol is'},
    33:{'nl':'Privacy','en':'Privacy','keynote_nl':'Terugtrekken en reflecteren — jij deelt wanneer de cyclus voltooid is','shadow_nl':'Te lang verborgen blijven of te vroeg delen','gift_nl':'Rijpe wijsheid gedeeld op het perfecte moment'},
    34:{'nl':'Kracht','en':'Power','keynote_nl':'Rauwe kracht die handelt — jij bent een krachtpatser','shadow_nl':'Kracht die niemand toekomt of kracht verspild','gift_nl':'Kracht in dienst van overtuiging en integriteit'},
    35:{'nl':'Verandering','en':'Change','keynote_nl':'Ervaringen verzamelen is jouw passie — altijd vooruit','shadow_nl':'Constant veranderen zonder diepgang','gift_nl':'Rijkdom aan ervaring die anderen inspireert'},
    36:{'nl':'Crisis','en':'Crisis','keynote_nl':'Crisis als doorgang — jij leert en groeit via intense ervaring','shadow_nl':'Chaos zoeken of vluchten van emotionele diepte','gift_nl':'Emotionele maturiteit geboren uit crisis'},
    37:{'nl':'Vriendschap','en':'Friendship','keynote_nl':'Jij bouwt gemeenschap via vriendschap en deal-making','shadow_nl':'Onevenwichtige relaties of gebrek aan verbinding','gift_nl':'Warmte en verbinding die families en gemeenschappen smeden'},
    38:{'nl':'De Strijder','en':'The Fighter','keynote_nl':'Jij vecht voor wat betekenisvol is — doelgericht en puur','shadow_nl':'Zinloos vechten of opgeven wanneer het zwaar wordt','gift_nl':'Onverzettelijke spirit die anderen inspiratie geeft'},
    39:{'nl':'Provocatie','en':'Provocation','keynote_nl':'Jij provoceert om spirit te wekken — een heilige rebel','shadow_nl':'Provocatie die kwetst in plaats van wakker maakt','gift_nl':'De gave om anderen te bevrijden via heilige provocatie'},
    40:{'nl':'Bevrijding','en':'Aloneness','keynote_nl':'Alleenzijn als kracht — jij herstelt via rust en terugkeer','shadow_nl':'Isolatie of het verloochenen van je behoeften','gift_nl':'Zelfverzorging die anderen toont hoe grenzen werken'},
    41:{'nl':'Vermindering','en':'Contraction','keynote_nl':'Nieuwe cycli beginnen met beperking — jij voelt wat er komen gaat','shadow_nl':'Vastklampen aan het oude of angst voor nieuwe beginnen','gift_nl':'De drempel van nieuwe ervaringen met moed oversteken'},
    42:{'nl':'Groei','en':'Growth','keynote_nl':'Afmaken wat begonnen is — jij brengt cycli tot voltooiing','shadow_nl':'Half afmaken of eindeloos bezig blijven','gift_nl':'De voldoening van volledige cycli afronden'},
    43:{'nl':'Doorbraak','en':'Insight','keynote_nl':'Individuele doorbraken die de wereld veranderen — jij denkt anders','shadow_nl':'Begrepen willen worden voor jouw unieke inzichten','gift_nl':'Doorbraken die het collectief bewustzijn vooruithelpen'},
    44:{'nl':'Energie','en':'Alertness','keynote_nl':'Jij herinnert je patronen — instinct als bescherming','shadow_nl':'Herhaalde patronen die niet meer dienen','gift_nl':'Institutioneel geheugen dat de gemeenschap beschermt'},
    45:{'nl':'De Verzamelaar','en':'The Gatherer','keynote_nl':'Jij beheert middelen en onderwijs voor de gemeenschap','shadow_nl':'Materialisme of onmacht over middelen','gift_nl':'Leiderschap dat zorgt dat iedereen genoeg heeft'},
    46:{'nl':'Determinatie','en':'Determination','keynote_nl':'Succes via het lichaam — jij treft geluk via lichamelijke aanwezigheid','shadow_nl':'Het lichaam negeren of pushen voorbij zijn grenzen','gift_nl':'Levensliefde die het lichaam als tempel viert'},
    47:{'nl':'Realisatie','en':'Realization','keynote_nl':'Betekenis vinden in het verleden — jij verwerkt ervaringen tot wijsheid','shadow_nl':'Zinloosheid of het niet kunnen losgeven van het verleden','gift_nl':'Retroactieve wijsheid die anderen bevrijdt'},
    48:{'nl':'De Diepte','en':'Depth','keynote_nl':'Jij duikt diep — kennis en vaardigheidsontwikkeling is jouw weg','shadow_nl':'Onzekerheid over jouw diepte of kennis','gift_nl':'Rijke expertise die anderen ten diepste helpt'},
    49:{'nl':'Principes','en':'Principles','keynote_nl':'Revolutie vanuit principes — jij hervormt wat niet meer werkt','shadow_nl':'Extremisme of vasthouden aan verouderde principes','gift_nl':'Vernieuwing die de gemeenschap bevrijdt'},
    50:{'nl':'Waarden','en':'Values','keynote_nl':'Jij bewaakt de wetten en waarden van de gemeenschap','shadow_nl':'Rigide wetgeving of het overschrijden van grenzen','gift_nl':'Verantwoordelijkheid voor de gezondheid van de gemeenschap'},
    51:{'nl':'Schok','en':'Shock','keynote_nl':'Schok als initiatie — jij daagt anderen uit te ontwaken','shadow_nl':'Angst voor schok of anderen onnodig schokken','gift_nl':'Initiatiekracht die anderen door drempels heen leidt'},
    52:{'nl':'Stilte','en':'Stillness','keynote_nl':'Stille aanwezigheid als kracht — jij weet wanneer niet te bewegen','shadow_nl':'Verstarring of onnodige beweging','gift_nl':'Geconcentreerde rust die de basis legt voor actie'},
    53:{'nl':'Ontwikkeling','en':'Development','keynote_nl':'Nieuwe beginnen met energie — jij initieert cycli','shadow_nl':'Te veel beginnen zonder af te maken','gift_nl':'De kracht om nieuwe cycli te starten voor anderen'},
    54:{'nl':'Ambitie','en':'Ambition','keynote_nl':'Ambitieus klimmen — jij weet hoe je hiërarchieën navigeert','shadow_nl':'Blinde ambitie of gebrek aan erkenning','gift_nl':'Gerichte ambitie in dienst van collectief succes'},
    55:{'nl':'Overvloed','en':'Abundance','keynote_nl':'Emotionele overvloed via geest en vrijheid — jij muteert de mensheid','shadow_nl':'Emotionele leegte of overgave aan wat niet dient','gift_nl':'Spirituele overvloed die de mensheid transformeert'},
    56:{'nl':'Stimulering','en':'Stimulation','keynote_nl':'Verhalen vertellen die stimuleren — jij houdt de vlam brandend','shadow_nl':'Oppervlakkige stimulering zonder diepte','gift_nl':'Verhalen die ideeën levend houden'},
    57:{'nl':'Intuïtieve Inzichten','en':'Intuitive Insight','keynote_nl':'Intuïtie als overlevingsintelligentie — jij voelt wat gezond is','shadow_nl':'Intuïtieve signalen negeren of angst voor het lichaam','gift_nl':'Verfijnde intuïtie die in het moment de juiste keuze maakt'},
    58:{'nl':'Vitaliteit','en':'Vitality','keynote_nl':'Vreugde in het leven — jij straalt levensenergie uit','shadow_nl':'Energie verspillen of het leven als verplichting zien','gift_nl':'Aanstekelijke vitaliteit die anderen vreugde brengt'},
    59:{'nl':'Seksualiteit','en':'Sexuality','keynote_nl':'Intimiteit en genetische verbinding — jij doorbreekt muren','shadow_nl':'Emotionele muren of grensoverschrijdingen','gift_nl':'Diepgaand contact dat genetische verbinding schept'},
    60:{'nl':'Acceptatie','en':'Acceptance','keynote_nl':'Grenzen accepteren als de weg naar vrijheid','shadow_nl':'Verzet tegen beperkingen of capituleren','gift_nl':'Transformeren binnen grenzen'},
    61:{'nl':'Innerlijke Waarheid','en':'Inner Truth','keynote_nl':'Het mysterie van de geest — jij zoekt de innerlijke waarheid','shadow_nl':'Obsessief denken of de druk om alles te begrijpen','gift_nl':'Mystieke inzichten die anderen inspireren'},
    62:{'nl':'Details','en':'Detail','keynote_nl':'Jij verwoordt het onverwoordbare via feitelijke nauwkeurigheid','shadow_nl':'Verdwalen in details of oppervlakkig blijven','gift_nl':'Helder communiceren van complexe concepten'},
    63:{'nl':'Na voltooiing','en':'After Completion','keynote_nl':'Twijfel als motor — jij stelt vragen die leiden tot zekerheid','shadow_nl':'Eindeloze twijfel of angst voor het onbekende','gift_nl':'Kritisch denken dat echte antwoorden vindt'},
    64:{'nl':'Voor voltooiing','en':'Before Completion','keynote_nl':'Verwarring voor helderheid — jij verwerkt het verleden naar wijsheid','shadow_nl':'Vastlopen in het verleden of chaos als eindstation','gift_nl':'Patronen van verwarring omzetten in licht'},
}
GATE_NAMES = {g: {'nl': d['nl'], 'en': d['en']} for g, d in GATE_DATA.items()}
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
# Frontend-compatible string keys for activations
PLANET_STR_KEYS = {
    swe.SUN: 'sun', swe.MOON: 'moon', swe.MERCURY: 'mercury', swe.VENUS: 'venus',
    swe.MARS: 'mars', swe.JUPITER: 'jupiter', swe.SATURN: 'saturn',
    swe.URANUS: 'uranus', swe.NEPTUNE: 'neptune', swe.PLUTO: 'pluto',
    swe.TRUE_NODE: 'north_node', swe.CHIRON: 'chiron',
}

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


PROFILE_DESCRIPTIONS = {
    '1/3': {
        'name_nl': 'Onderzoeker / Martelaar',
        'theme_nl': 'Jij moet eerst grondig onderzoeken voordat je in actie komt. Door te experimenteren en van fouten te leren bouw je een levenswijsheid die uniek is.',
        'line1_nl': 'De Onderzoeker: jij bouwt een solide fundament van kennis voor je handelt',
        'line2_nl': 'De Martelaar: je leert door uit te proberen — fouten zijn jouw leerschool',
        'not_self_nl': 'Onzekerheid zonder genoeg kennis, of te lang wachten voor je begint'
    },
    '1/4': {
        'name_nl': 'Onderzoeker / Opportunist',
        'theme_nl': 'Jij hebt een stevige kennisbasis nodig én een netwerk van mensen die jou kennen. Jouw impact komt via bestaande relaties.',
        'line1_nl': 'De Onderzoeker: kennis en veiligheid zijn jouw fundering',
        'line2_nl': 'De Opportunist: jij benut jouw netwerk en relaties',
        'not_self_nl': 'Onveiligheid of het niet benutten van je netwerk'
    },
    '2/4': {
        'name_nl': 'Kluizenaar / Opportunist',
        'theme_nl': 'Jij trekt je terug om te verdiepen, maar jouw gave wordt ontdekt via mensen die jou goed kennen. Rust is essentieel voor jouw helderheid.',
        'line1_nl': 'De Kluizenaar: jij heeft tijd alleen nodig om je talenten te verdiepen',
        'line2_nl': 'De Opportunist: impact via je netwerk en vriendschappen',
        'not_self_nl': 'Te weinig alleen-tijd of jezelf opdringen in relaties'
    },
    '2/5': {
        'name_nl': 'Kluizenaar / Ketter',
        'theme_nl': 'Jij bent een naturel wiens gaven anderen verlossen. Je trekt je terug, maar de wereld vindt jou. Selectiviteit in je invitaties is cruciaal.',
        'line1_nl': 'De Kluizenaar: jij heeft solitude nodig om jouw gaven te verfijnen',
        'line2_nl': 'De Ketter: anderen projecteren op jou praktische oplossingen te bieden',
        'not_self_nl': 'Overweldigd door de projecties van anderen'
    },
    '3/5': {
        'name_nl': 'Martelaar / Ketter',
        'theme_nl': 'Jij hebt een leven vol experimenten geleefd en bent daardoor wijs. Anderen zoeken jou als universele redder — wees eerlijk over wat je wel en niet kunt.',
        'line1_nl': 'De Martelaar: jij leert door doen — fouten zijn jouw data',
        'line2_nl': 'De Ketter: anderen zien jou als de praktische probleemoplosser',
        'not_self_nl': 'Schuldgevoel over fouten of niet voldoen aan verwachtingen'
    },
    '3/6': {
        'name_nl': 'Martelaar / Rolmodel',
        'theme_nl': 'Jij doorloopt drie fasen: experimenteren (0-30), terugtrekken (30-50), en authentiek rolmodel zijn (50+). Jouw gebrokenheid wordt jouw grootste gave.',
        'line1_nl': 'De Martelaar: jij leert door te experimenteren',
        'line2_nl': 'Het Rolmodel: in drie levensfasen groei je naar echt rolmodel zijn',
        'not_self_nl': 'Te vroeg rolmodel willen zijn of schuldgevoel over fouten'
    },
    '4/6': {
        'name_nl': 'Opportunist / Rolmodel',
        'theme_nl': 'Vriendschappen zijn jouw fundament. Via jouw netwerk en jouw manier van zijn word jij een inspirerend rolmodel voor anderen.',
        'line1_nl': 'De Opportunist: jij bouwt via netwerken en vriendschappen',
        'line2_nl': 'Het Rolmodel: jij groeit naar authentiek leiderschap',
        'not_self_nl': 'Relaties onderhouden die jou niet werkelijk steunen'
    },
    '4/1': {
        'name_nl': 'Opportunist / Onderzoeker',
        'theme_nl': 'Jij brengt kennis en verbinding samen. Via jouw netwerk deel je wat jij grondig onderzocht hebt.',
        'line1_nl': 'De Opportunist: impact via vertrouwde relaties',
        'line2_nl': 'De Onderzoeker: kennisbasis als fundament',
        'not_self_nl': 'Onveiligheid zonder voldoende kennisbasis'
    },
    '5/1': {
        'name_nl': 'Ketter / Onderzoeker',
        'theme_nl': 'Jij wordt gezien als de universele probleemoplosser. Jouw kennis is jouw bescherming tegen de projecties. Wacht op de uitnodiging voor jij je kennis deelt.',
        'line1_nl': 'De Ketter: anderen projecteren praktische redding op jou',
        'line2_nl': 'De Onderzoeker: jouw solide kennisbasis maakt je betrouwbaar',
        'not_self_nl': 'Opgaan in andermans verwachtingen'
    },
    '5/2': {
        'name_nl': 'Ketter / Kluizenaar',
        'theme_nl': 'Jij wordt gevonden — maar je trekt je graag terug. Jouw gave is praktisch en universeel, maar selectiviteit over wanneer je het deelt is essentieel.',
        'line1_nl': 'De Ketter: anderen zien jou als redder',
        'line2_nl': 'De Kluizenaar: jij heeft solitude nodig om jouw ware gave te kennen',
        'not_self_nl': 'Te veel beschikbaar zijn of jezelf verbergen'
    },
    '6/2': {
        'name_nl': 'Rolmodel / Kluizenaar',
        'theme_nl': 'Jij groeit via drie fasen naar wie je werkelijk bent. Alleen-tijd is essentieel. In jouw latere jaren word je een echte inspiratie voor anderen.',
        'line1_nl': 'Het Rolmodel: in drie fasen groei je naar jouw ware leven',
        'line2_nl': 'De Kluizenaar: rust en solitude zijn jouw brandstof',
        'not_self_nl': 'Te vroeg een rolmodel willen zijn'
    },
    '6/3': {
        'name_nl': 'Rolmodel / Martelaar',
        'theme_nl': 'Jij ervaart meer dan de meesten — via fouten, experimenten en zelfontdekking. Dit maakt jou tot een diepzinnig rolmodel later in het leven.',
        'line1_nl': 'Het Rolmodel: authenticiteit via levenservaring',
        'line2_nl': 'De Martelaar: leren door te experimenteren en te falen',
        'not_self_nl': 'Schuldgevoel over mislukkingen of het leven als te zwaar ervaren'
    }
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
    'Mental':        'Mentale autoriteit (geen innerlijke autoriteit)',
    'Lunar':         'Lunaire autoriteit'
}


# ══════════════════════════════════════════════════════════════
# KANALEN — alle 36 met naam, circuit en beschrijving
# ══════════════════════════════════════════════════════════════

CENTER_DESCRIPTIONS = {
    'Head': {
        'nl': 'Hoofd', 'en': 'Head',
        'function_nl': 'Inspiratie en mentale druk — de bron van vragen en twijfels',
        'defined_nl': 'Jij ervaart consistente mentale druk en inspiratie. Je genereert constant ideeën en vragen.',
        'undefined_nl': 'Jij bent open voor inspiratie van anderen. Je pikt de mentale druk van anderen op — let op welke gedachten van jou zijn.',
        'not_self_nl': 'Jezelf verplichten aan ideeën die niet van jou zijn'
    },
    'Ajna': {
        'nl': 'Ajna (Geest)', 'en': 'Ajna',
        'function_nl': 'Verwerking en conceptualisering — het denken en analyseren',
        'defined_nl': 'Jij denkt op een vaste, consistente manier. Je perspectief is betrouwbaar en standvastig.',
        'undefined_nl': 'Jij bent flexibel in je denken en absorbeert ideeën van anderen. Pas op voor mentale zekerheid die je dwingend voelt.',
        'not_self_nl': 'Proberen zeker te zijn of anderen te overtuigen'
    },
    'Throat': {
        'nl': 'Keel', 'en': 'Throat',
        'function_nl': 'Manifestatie en communicatie — het in de wereld brengen',
        'defined_nl': 'Jij communiceert op een consistente manier. Je stem en aanwezigheid zijn krachtig en herkenbaar.',
        'undefined_nl': 'Jouw communicatie is situationeel en aanpasbaar. Je spreekt het beste wanneer je een reactie geeft.',
        'not_self_nl': 'Te veel spreken om aandacht te trekken'
    },
    'G': {
        'nl': 'G-Centrum (Zelf & Liefde)', 'en': 'G Center',
        'function_nl': 'Identiteit, richting en liefde — wie jij bent en waarheen jij gaat',
        'defined_nl': 'Jij heeft een vaste, consistente identiteit en richting. Je kent jezelf goed.',
        'undefined_nl': 'Jouw identiteit is fluïde en situationeel. Ruimtes en mensen beïnvloeden jouw gevoel van zelf.',
        'not_self_nl': "Vragen 'Wie ben ik?' en 'Waar ga ik heen?' met angst"
    },
    'Will': {
        'nl': 'Wilskracht (Ego / Hart)', 'en': 'Will / Ego',
        'function_nl': 'Wilskracht, zelfwaarde en materiële zaken — het ego',
        'defined_nl': 'Jij heeft consistente wilskracht en zelfwaarde. Je kunt beloften maken en nakomen.',
        'undefined_nl': 'Jouw wilskracht fluctueert. Pas op voor overschatting van je energie.',
        'not_self_nl': 'Jezelf bewijzen of beloften maken die je niet kunt waarmaken'
    },
    'Solar': {
        'nl': 'Zonnevlecht (Emoties)', 'en': 'Solar Plexus',
        'function_nl': 'Emotionele golven — gevoel, passie en geest',
        'defined_nl': 'Jij ervaart emotionele golven. Wacht op helderheid voor je beslist — jouw autoriteit werkt over tijd.',
        'undefined_nl': 'Jij absorbeert de emoties van anderen. Pas op voor meegaan in hun emotionele golf.',
        'not_self_nl': 'Emotionele druk vermijden of er onbewust in meegaan'
    },
    'Sacral': {
        'nl': 'Sacraal (Levensbron)', 'en': 'Sacral',
        'function_nl': 'Levensenergie, seksualiteit en vitaliteit — de motor van het leven',
        'defined_nl': 'Jij heeft een consistente bron van levensenergie. Je weet in je lijf wat ja of nee is.',
        'undefined_nl': 'Jij amplificieert de sacrale energie van anderen — pas op voor uitputting.',
        'not_self_nl': 'Doorgaan voorbij de echte energiegrenzen'
    },
    'Spleen': {
        'nl': 'Milt (Overleven & Intuïtie)', 'en': 'Spleen',
        'function_nl': 'Overlevingsinstinct, intuïtie en spontane wijsheid — het lichaam weet',
        'defined_nl': 'Jij heeft een consistent, betrouwbaar intuïtief systeem. Je weet in het moment wat gezond en veilig is.',
        'undefined_nl': 'Jouw intuïtie is situationeel. Je kunt mensen aanhangen die jou goed voelen maar je niet dienen.',
        'not_self_nl': 'Vasthouden aan wat niet goed voelt uit angst'
    },
    'Root': {
        'nl': 'Wortel (Adrenaline & Stress)', 'en': 'Root',
        'function_nl': 'Adrenaline, druk en drang naar voltooiing — de motor onder alles',
        'defined_nl': 'Jij heeft een consistente motor van adrenaline en druk. Je werkt goed onder druk.',
        'undefined_nl': 'Jij amplificieert de worteldruk van anderen. Pas op voor onnodige haast of stress.',
        'not_self_nl': 'Handelen vanuit druk en stress in plaats van timing'
    }
}

CHANNEL_DATA = {
    (1,8):   {'nl':'Inspiratie','en':'Inspiration',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Het kanaal van creatieve zelfexpressie — jij inspireert door simpelweg jezelf te zijn.'},
    (2,14):  {'nl':'De Geldheer','en':'The Money Line',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Richting en materiële kracht — jij weet intuïtief waarheen de energie moet stromen.'},
    (3,60):  {'nl':'Mutatie','en':'Mutation',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Het vermogen om vast te houden terwijl mutatie zich ontvouwt — rustig in de storm.'},
    (4,63):  {'nl':'Logica','en':'Logic',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Twijfel en antwoorden — jij heeft het talent om patronen te herkennen en concepten te formuleren.'},
    (5,15):  {'nl':'Ritme','en':'Rhythm',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Het universele ritme van de natuur — jij belichaamt de stroom en het ritme van het leven.'},
    (6,59):  {'nl':'Seksualiteit','en':'Mating',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'De kracht van intimiteit en genetische verbinding — diep contact als levenskracht.'},
    (7,31):  {'nl':'De Alpha','en':'The Alpha',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Leiderschap via democratisch proces — jij leidt wanneer anderen jou roepen.'},
    (9,52):  {'nl':'Concentratie','en':'Concentration',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Het vermogen om te focussen en vastberaden te zijn — rust in het zitten met het proces.'},
    (10,20): {'nl':'Wakker worden','en':'Awakening',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Zelfliefde die anderen wakker maakt — jouw integriteit inspireert vanzelf.'},
    (10,34): {'nl':'Verkenning','en':'Exploration',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Het volgen van overtuigingen met kracht — jij handelt vanuit diepe innerlijke zekerheid.'},
    (10,57): {'nl':'Perfecte Vorm','en':'Perfected Form',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Intuïtie in dienst van overleven — jij voelt instinctief wat goed en gezond is.'},
    (11,56): {'nl':'Nieuwsgierigheid','en':'Curiosity',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Ideeën omzetten in verhalen — jij stimuleert anderen via je rijk beeldend denken.'},
    (12,22): {'nl':'Openheid','en':'Openness',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Emotionele expressie die muteert — wanneer de timing klopt, raakt jouw communicatie diep.'},
    (13,33): {'nl':'De Getuige','en':'The Prodigal',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Verhalen bewaren en op het juiste moment delen — jij bent de bewaarder van wijsheid.'},
    (16,48): {'nl':'Golflengte','en':'Wavelength',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Vaardigheden verdiepen via herhaling — jij streeft naar perfectie via toewijding.'},
    (17,62): {'nl':'Acceptatie','en':'Acceptance',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Details in dienst van de logica — jij heeft de gave om complexe ideeën te verwoorden.'},
    (18,58): {'nl':'Oordeel','en':'Judgment',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'De drang tot perfectie en correctie — jij ziet direct wat beter kan en werkt er naartoe.'},
    (19,49): {'nl':'Synthese','en':'Synthesis',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'De verbinding tussen behoeften en principes — jij weet diep wat gemeenschappen draaiende houdt.'},
    (20,34): {'nl':'Charisma','en':'Charisma',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Kracht die direct tot expressie komt — jij handelt vanuit kracht en integriteit.'},
    (20,57): {'nl':'De Golven','en':'The Brain Waves',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Intuïtie die direct tot expressie komt — jij verwoordt wat anderen niet kunnen benoemen.'},
    (21,45): {'nl':'Het Geld kanaal','en':'Money Line',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Controle en leiderschap in materiële zaken — jij weet hoe je middelen beheert.'},
    (22,12): {'nl':'Openheid','en':'Openness',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Emotionele expressie en timing — jij deelt wanneer het moment er rijp voor is.'},
    (23,43): {'nl':'Structurering','en':'Structuring',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Van inzicht naar uitdrukking — jij vertaalt doorbraken in begrijpelijke taal.'},
    (24,61): {'nl':'Bewustwording','en':'Awareness',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Het mysterie van de geest — jij denkt in cirkels totdat het inzicht er plots doorheen breekt.'},
    (25,51): {'nl':'Initiatie','en':'Initiation',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'De kracht van shock en initiatief — jij durft het eerste te springen.'},
    (26,44): {'nl':'Overgave','en':'Surrender',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Geheugen en de kracht van het ego — jij weet hoe je mensen en patronen verbindt.'},
    (27,50): {'nl':'Bewaring','en':'Preservation',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Voeding en waarden doorgeven — jij zorgt diepgaand voor wie aan jou is toevertrouwd.'},
    (28,38): {'nl':'Strijd','en':'Struggle',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'De waarde van de strijd — jij zoekt betekenis in tegenslagen en geeft anderen hoop.'},
    (29,46): {'nl':'Ontdekking','en':'Discovery',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Overgave aan het leven — jij zegt ja en ontdekt wat er mogelijk is.'},
    (30,41): {'nl':'Herkenning','en':'Recognition',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Dromen die brandstof zijn — jij voelt de emotionele lading van nieuwe ervaringen.'},
    (32,54): {'nl':'Transformatie','en':'Transformation',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Ambitie in dienst van continuïteit — jij weet hoe je dingen opbouwt om te duren.'},
    (33,13): {'nl':'De Verloren Zoon','en':'The Prodigal',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Privacy en reflectie — jij deelt verhalen op het moment dat de cyclus is voltooid.'},
    (35,36): {'nl':'Transitorisch','en':'Transitoriness',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Ervaringen zoeken — jij gedijt in verandering en brengt nieuwe ervaringen in.'},
    (37,40): {'nl':'Gemeenschap','en':'Community',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Werk in ruil voor behoeftebevrediging — jij brengt samenhang in groepen.'},
    (38,28): {'nl':'Worsteling','en':'Struggle',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'De zoektocht naar levensbetekenis — jij vecht voor wat ertoe doet.'},
    (39,55): {'nl':'Emotie','en':'Emoting',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'De kracht van het emotionele geest — jij provoceert om geest te wekken.'},
    (41,30): {'nl':'Erkenning','en':'Recognition',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Dromen en verwachtingen — jij voelt welke nieuwe cycli op het punt staan te beginnen.'},
    (42,53): {'nl':'Maturatie','en':'Maturation',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Begin en einde van cycli — jij voltooit wat anderen niet kunnen afmaken.'},
    (43,23): {'nl':'Structurering','en':'Structuring',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Individuele inzichten die de wereld veranderen — jij denkt anders dan de massa.'},
    (44,26): {'nl':'Overgave','en':'Surrender',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Geheugen en instinct — jij herinnert je patronen uit het verleden.'},
    (45,21): {'nl':'Het Geld kanaal','en':'Money Line',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'De leider die zijn gemeenschap voedt — jij beheert materiële middelen voor het collectief.'},
    (46,29): {'nl':'Ontdekking','en':'Discovery',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Het lichaam als tempel — jij kent de kracht van overgave aan het leven.'},
    (47,64): {'nl':'Abstractie','en':'Abstraction',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Het verwerken van het verleden — jij vindt betekenis in ervaringen achteraf.'},
    (48,16): {'nl':'Golflengte','en':'Wavelength',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Diepte en talent — jij ontwikkelt vaardigheden tot meesterschap.'},
    (49,19): {'nl':'Synthese','en':'Synthesis',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Principes en behoeften — jij bepaalt wie toegang heeft tot de gemeenschap.'},
    (50,27): {'nl':'Bewaring','en':'Preservation',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Waarden bewaken — jij draagt de verantwoordelijkheid voor wat doorgegeven wordt.'},
    (51,25): {'nl':'Initiatie','en':'Initiation',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Shock als initiatie — jij durft te springen waar anderen aarzelen.'},
    (52,9):  {'nl':'Concentratie','en':'Concentration',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Stille kracht — jij heeft het vermogen om volledig aanwezig te zijn in het proces.'},
    (53,42): {'nl':'Maturatie','en':'Maturation',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Cycli beginnen en afronden — jij brengt projecten tot voltooiing.'},
    (54,32): {'nl':'Transformatie','en':'Transformation',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Ambitie en overleven — jij weet hoe je opklimt in hiërarchieën.'},
    (55,39): {'nl':'Emotionele Kracht','en':'Emoting',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Overvloed en geest — jij bezit een emotionele diepte die spirit oproept.'},
    (56,11): {'nl':'Nieuwsgierigheid','en':'Curiosity',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Ideeën in verhalen — jij stimuleert en inspireert via je verbeelding.'},
    (57,10): {'nl':'Perfecte Vorm','en':'Perfected Form',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Intuïtief overleven — jij voelt wat gezond en veilig is voor jezelf en anderen.'},
    (57,20): {'nl':'De Golven','en':'The Brain Waves',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Intuïtie en aanwezigheid — jij spreekt wat de ziel weet op het perfecte moment.'},
    (57,34): {'nl':'Kracht','en':'Power',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Intuïtieve kracht — jij handelt vanuit een diepe, onbewuste zekerheid.'},
    (58,18): {'nl':'Oordeel','en':'Judgment',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Vreugde door perfectie — jij ziet direct hoe dingen beter kunnen.'},
    (59,6):  {'nl':'Doordringen','en':'Mating',
               'circuit':'Stammes','circuit_en':'Tribal',
               'desc_nl':'Intimiteit en genetische verbinding — jij doorbreekt muren voor echte nabijheid.'},
    (60,3):  {'nl':'Mutatie','en':'Mutation',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Acceptatie en mutatie — jij houdt stand terwijl de transformatie zich voltrekt.'},
    (61,24): {'nl':'Bewustwording','en':'Awareness',
               'circuit':'Individueel','circuit_en':'Individual',
               'desc_nl':'Innerlijke waarheid — jij denkt diep en heeft plotselinge doorbraken.'},
    (62,17): {'nl':'Acceptatie','en':'Acceptance',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Feiten en details — jij heeft talent voor nauwkeurige analyse en verwoording.'},
    (63,4):  {'nl':'Logica','en':'Logic',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Twijfel en antwoorden zoeken — jij bedenkt formules voor complexe problemen.'},
    (64,47): {'nl':'Abstractie','en':'Abstraction',
               'circuit':'Collectief','circuit_en':'Collective',
               'desc_nl':'Het verleden verwerken — jij vindt rust door betekenis te geven aan ervaringen.'},
}

# ══════════════════════════════════════════════════════════════
# INCARNATIEKRUISEN — de 192 kruisen (Right Angle, Left Angle, Juxtaposition)
# Gebaseerd op zon personality gate
# ══════════════════════════════════════════════════════════════
INCARNATION_CROSSES = {
    # Right Angle Crosses (lijn 1-4)
    1:  {'name':'Sfinx','angle':'Rechte Hoek','gates':[1,2,7,13]},
    2:  {'name':'Penetratie','angle':'Rechte Hoek','gates':[2,1,49,4]},
    3:  {'name':'Marteling','angle':'Rechte Hoek','gates':[3,50,60,56]},
    4:  {'name':'Persoonlijkheid','angle':'Rechte Hoek','gates':[4,49,8,14]},
    5:  {'name':'Bewustzijn','angle':'Rechte Hoek','gates':[5,35,47,22]},
    6:  {'name':'Eden','angle':'Rechte Hoek','gates':[6,36,11,12]},
    7:  {'name':'Interactie','angle':'Rechte Hoek','gates':[7,13,1,2]},
    8:  {'name':'Dualisme','angle':'Rechte Hoek','gates':[8,14,55,59]},
    9:  {'name':'Planning','angle':'Rechte Hoek','gates':[9,16,40,37]},
    10: {'name':'Vluchtigheid','angle':'Rechte Hoek','gates':[10,15,18,17]},
    11: {'name':'Geluk','angle':'Rechte Hoek','gates':[11,12,46,25]},
    12: {'name':'Ervaring','angle':'Rechte Hoek','gates':[12,11,25,46]},
    13: {'name':'Verkenner','angle':'Rechte Hoek','gates':[13,7,30,29]},
    14: {'name':'Draagkracht','angle':'Rechte Hoek','gates':[14,8,59,55]},
    15: {'name':'Uitersten','angle':'Rechte Hoek','gates':[15,10,17,18]},
    16: {'name':'Experimenten','angle':'Rechte Hoek','gates':[16,9,37,40]},
    17: {'name':'Organisatie','angle':'Rechte Hoek','gates':[17,18,10,15]},
    18: {'name':'Ambiguïteit','angle':'Rechte Hoek','gates':[18,17,15,10]},
    19: {'name':'Noodzaak','angle':'Rechte Hoek','gates':[19,33,44,24]},
    20: {'name':'Tao','angle':'Rechte Hoek','gates':[20,34,37,40]},
    21: {'name':'Conflict','angle':'Rechte Hoek','gates':[21,48,54,38]},
    22: {'name':'Gratie','angle':'Rechte Hoek','gates':[22,47,26,45]},
    23: {'name':'Schepping','angle':'Rechte Hoek','gates':[23,43,30,29]},
    24: {'name':'Maya','angle':'Rechte Hoek','gates':[24,44,13,7]},
    25: {'name':'Incarnatie','angle':'Rechte Hoek','gates':[25,46,58,52]},
    26: {'name':'Transmissie','angle':'Rechte Hoek','gates':[26,45,22,47]},
    27: {'name':'Evenwicht','angle':'Rechte Hoek','gates':[27,28,19,33]},
    28: {'name':'Uitdaging','angle':'Rechte Hoek','gates':[28,27,33,19]},
    29: {'name':'Ommekeer','angle':'Rechte Hoek','gates':[29,30,20,34]},
    30: {'name':'Illusies','angle':'Rechte Hoek','gates':[30,29,34,20]},
    31: {'name':'Invloed','angle':'Rechte Hoek','gates':[31,41,24,44]},
    32: {'name':'Verval','angle':'Rechte Hoek','gates':[32,42,56,60]},
    33: {'name':'Geheugen','angle':'Rechte Hoek','gates':[33,19,7,13]},
    34: {'name':'Kracht','angle':'Rechte Hoek','gates':[34,20,40,37]},
    35: {'name':'Verleden','angle':'Rechte Hoek','gates':[35,5,22,47]},
    36: {'name':'Verandering','angle':'Rechte Hoek','gates':[36,6,12,11]},
    37: {'name':'Familie','angle':'Rechte Hoek','gates':[37,40,16,9]},
    38: {'name':'Tegenstelling','angle':'Rechte Hoek','gates':[38,39,28,27]},
    39: {'name':'Provokatie','angle':'Rechte Hoek','gates':[39,38,27,28]},
    40: {'name':'Eenzaamheid','angle':'Rechte Hoek','gates':[40,37,9,16]},
    41: {'name':'Beginnelingen','angle':'Rechte Hoek','gates':[41,31,44,24]},
    42: {'name':'Voltooiing','angle':'Rechte Hoek','gates':[42,32,60,56]},
    43: {'name':'Inzicht','angle':'Rechte Hoek','gates':[43,23,29,30]},
    44: {'name':'Terugkeer','angle':'Rechte Hoek','gates':[44,24,7,13]},
    45: {'name':'Dominantie','angle':'Rechte Hoek','gates':[45,26,47,22]},
    46: {'name':'Identificatie','angle':'Rechte Hoek','gates':[46,25,52,58]},
    47: {'name':'Onderdrukking','angle':'Rechte Hoek','gates':[47,22,45,26]},
    48: {'name':'Uitputting','angle':'Rechte Hoek','gates':[48,21,38,54]},
    49: {'name':'Revolutie','angle':'Rechte Hoek','gates':[49,4,14,8]},
    50: {'name':'Wetten','angle':'Rechte Hoek','gates':[50,3,56,60]},
    51: {'name':'Bliksem','angle':'Rechte Hoek','gates':[51,57,54,53]},  # Juxtaposition
    52: {'name':'Stilte','angle':'Rechte Hoek','gates':[52,58,25,46]},
    53: {'name':'Cycli','angle':'Rechte Hoek','gates':[53,54,42,32]},
    54: {'name':'Huwelijk','angle':'Rechte Hoek','gates':[54,53,32,42]},
    55: {'name':'Overvloed','angle':'Rechte Hoek','gates':[55,59,9,16]},
    56: {'name':'Afleiding','angle':'Rechte Hoek','gates':[56,60,3,50]},
    57: {'name':'Intuïtie','angle':'Rechte Hoek','gates':[57,51,53,54]},
    58: {'name':'Vitaliteit','angle':'Rechte Hoek','gates':[58,52,46,25]},
    59: {'name':'Strategie','angle':'Rechte Hoek','gates':[59,55,16,9]},
    60: {'name':'Beperking','angle':'Rechte Hoek','gates':[60,56,42,32]},
    61: {'name':'Mysterie','angle':'Rechte Hoek','gates':[61,62,53,54]},  # Left Angle
    62: {'name':'Civilisatie','angle':'Linker Hoek','gates':[62,61,17,18]},
    63: {'name':'Na de Val','angle':'Linker Hoek','gates':[63,64,26,45]},
    64: {'name':'Voor de Val','angle':'Linker Hoek','gates':[64,63,45,26]},
}

# Cross-name lookup by (p_sun_gate, d_sun_gate) pair.
# Built from the primary table, then overridden with edge-case entries where
# personality-sun lines 5/6 push the design-sun into a different gate.
INCARNATION_CROSSES_BY_PAIR = {
    (gate, data['gates'][2]): data
    for gate, data in INCARNATION_CROSSES.items()
}
# Edge-case overrides: gates whose line 5/6 produce a different d_sun_gate
# (16, 63): user-confirmed "Left Angle Cross of Identification I (16/9 | 63/64)"
INCARNATION_CROSSES_BY_PAIR.update({
    (16, 63): {'name': 'Identificatie I',  'angle': 'Linker Hoek', 'gates': [16, 9, 63, 64]},
    (16, 64): {'name': 'Identificatie II', 'angle': 'Linker Hoek', 'gates': [16, 9, 64, 63]},
})


# ══════════════════════════════════════════════════════════════
# VARIABELEN / 4 PIJLEN
# Links = actief/yang, Rechts = passief/yin
# Pijl 1 = Determinatie (Design Zon lijn)
# Pijl 2 = Omgeving (Design Zon kleur)
# Pijl 3 = Motivatie (Personality Zon kleur)
# Pijl 4 = Perspectief (Personality Zon lijn)
# ══════════════════════════════════════════════════════════════
DETERMINATIE = {
    1: {'nl':'Smaken (links)', 'en':'Taste (left)',  'type':'actief',
        'desc_nl':'Je voeding en zintuiglijke ervaringen zijn het meest persoonlijk voor jou. Eet wat jij lekker vindt, niet wat anderen aanraden.'},
    2: {'nl':'Smaken (rechts)','en':'Taste (right)', 'type':'passief',
        'desc_nl':'Je lichaam weet intuïtief wat het nodig heeft. Vertrouw op de aanwijzingen die het je geeft.'},
    3: {'nl':'Zien (links)',   'en':'Sight (left)',  'type':'actief',
        'desc_nl':'Je hebt een scherp, gefocust gezichtsveld nodig. Kies een omgeving die esthetisch aanspreekt.'},
    4: {'nl':'Zien (rechts)',  'en':'Sight (right)', 'type':'passief',
        'desc_nl':'Je absorbeert de hele omgeving. Kies een visueeel rijke, gevarieerde omgeving.'},
    5: {'nl':'Geluid (links)', 'en':'Sound (left)',  'type':'actief',
        'desc_nl':'Je hebt behoefte aan stilte of specifiek geluid. Kies bewust jouw akoestische omgeving.'},
    6: {'nl':'Geluid (rechts)','en':'Sound (right)', 'type':'passief',
        'desc_nl':'Je gedijt bij gevarieerde geluiden. Open, levende omgevingen geven je energie.'},
}

OMGEVING = {
    1: {'nl':'Grotten (ingetogen)',   'en':'Caves',       'type':'selectief',
        'desc_nl':'Je hebt een kleine, intieme, persoonlijke ruimte nodig om te floreren.'},
    2: {'nl':'Markten (sociaal)',     'en':'Markets',     'type':'open',
        'desc_nl':'Je gedijt in drukke, sociale omgevingen vol met mensen en activiteit.'},
    3: {'nl':'Keukens (warmte)',      'en':'Kitchens',    'type':'warm',
        'desc_nl':'Je hebt een hartelijke, verwelkomende omgeving nodig — een plek die als thuis voelt.'},
    4: {'nl':'Bergen (hoogte/rust)',  'en':'Mountains',   'type':'verheven',
        'desc_nl':'Je gedijt in open, hoge of rustige omgevingen met een ruim perspectief.'},
    5: {'nl':'Valleien (beschermd)', 'en':'Valleys',     'type':'beschermd',
        'desc_nl':'Je hebt een beschermde, rustige omgeving nodig die je afschermt van prikkels.'},
    6: {'nl':'Kusten (grens)',        'en':'Shores',      'type':'grens',
        'desc_nl':'Je gedijt op de grens van twee werelden — waar tegenstelElingen samenkomen.'},
}

MOTIVATIE = {
    1: {'nl':'Behoeftigheid',  'en':'Need',        'type':'behoeftigheid',
        'desc_nl':'Je wordt gemotiveerd door wat ontbreekt — je vult gaten op. Jouw motivatie is om behoeften te bevredigen.'},
    2: {'nl':'Schuld',         'en':'Guilt',       'type':'schuld',
        'desc_nl':'Je bent diep bewust van de impact van acties. Je motivatie is verantwoordelijkheid nemen.'},
    3: {'nl':'Onschuld',       'en':'Innocence',   'type':'onschuld',
        'desc_nl':'Je handelt vanuit een puur hart zonder bijgedachten. Jouw motivatie is eerlijkheid.'},
    4: {'nl':'Hoop',           'en':'Hope',        'type':'hoop',
        'desc_nl':'Je wordt geleid door potentie en mogelijkheid. Jouw motivatie is geloof in de toekomst.'},
    5: {'nl':'Angst',          'en':'Fear',        'type':'angst',
        'desc_nl':'Je wordt gemotiveerd door het anticiperen op gevaar. Dit kan beschermend of verlammend zijn.'},
    6: {'nl':'Verlangen',      'en':'Desire',      'type':'verlangen',
        'desc_nl':'Je wordt geleid door diep verlangen. Jouw motivatie is de passie voor wat je aantrekt.'},
}

PERSPECTIEF = {
    1: {'nl':'Persoonlijk (survivalist)',   'en':'Personal (Survivalist)',  'type':'persoonlijk',
        'desc_nl':'Je verwerkt alles door jouw persoonlijk perspectief. Overleving en eigenbelang zijn de lens.'},
    2: {'nl':'Moreel (opportunist)',        'en':'Moralistic (Opportunist)','type':'moreel',
        'desc_nl':'Je ziet de wereld door morele en ethische lenzen. Recht en verkeerd zijn jouw kompas.'},
    3: {'nl':'Wensen (martyr)',             'en':'Phasic (Martyr)',         'type':'cycli',
        'desc_nl':'Je verwerkt informatie in fasen en cycli. Je perspectief verschuift met de tijd.'},
    4: {'nl':'Uitzicht (opportunist)',      'en':'Probability (Opportunist)','type':'kansen',
        'desc_nl':'Je ziet kansen en waarschijnlijkheden. Je perspectief is strategisch gericht.'},
    5: {'nl':'Nihilisme (heretic)',         'en':'Nihilistic (Heretic)',    'type':'nihilisme',
        'desc_nl':'Je daagt aannames uit en bevraagt het systeem. Je perspectief is onconventioneel.'},
    6: {'nl':'Empathie (rolmodel)',         'en':'Empathic (Role model)',   'type':'empathie',
        'desc_nl':'Je ziet de wereld via empathie en diepe verbinding. Je perspectief is menselijk.'},
}


def calc_variables(p_sun_line, p_sun_color, d_sun_line, d_sun_color):
    """
    Bereken de 4 pijlen (variabelen).
    Lijn 1-3 = links (actief/yang), lijn 4-6 = rechts (passief/yin)
    Kleur 1-3 = links, 4-6 = rechts
    """
    arrow1 = 'links' if d_sun_line <= 3 else 'rechts'
    arrow2 = 'links' if d_sun_color <= 3 else 'rechts'
    arrow3 = 'links' if p_sun_color <= 3 else 'rechts'
    arrow4 = 'links' if p_sun_line <= 3 else 'rechts'

    det = DETERMINATIE.get(d_sun_line, {})
    omg = OMGEVING.get(d_sun_color, {})
    mot = MOTIVATIE.get(p_sun_color, {})
    per = PERSPECTIEF.get(p_sun_line, {})

    return {
        'pijl1': {'naam': 'Determinatie', 'richting': arrow1, **det},
        'pijl2': {'naam': 'Omgeving',     'richting': arrow2, **omg},
        'pijl3': {'naam': 'Motivatie',    'richting': arrow3, **mot},
        'pijl4': {'naam': 'Perspectief',  'richting': arrow4, **per},
        'samenvatting': f"{'↓' if arrow1=='links' else '↑'} {'↓' if arrow2=='links' else '↑'} {'↓' if arrow4=='links' else '↑'} {'↓' if arrow3=='links' else '↑'}"
    }


# Beschrijvingen voor de meest voorkomende incarnatiekruisen
INCARNATION_CROSS_DESCRIPTIONS = {
    'Sfinx':        'Het Kruis van de Sfinx draait om evenwicht: tussen zelfexpressie en ontvankelijkheid, tussen leiding en dienst. Jij bent hier om een nieuw tijdperk te belichamen.',
    'Penetratie':   'Het Kruis van Penetratie draagt de kracht om door schijnbaar ondoordringbare muren heen te breken — in ideeën, relaties en transformaties.',
    'Incarnatie':   'Het Kruis van de Incarnatie is het meest fundamentele kruis — de essentie van het volledig menselijk leven omhelzen.',
    'Maya':         'Het Kruis van Maya draagt de gave om te leven voorbij de illusie. Jij ziet doorheen patronen en helpt anderen het spel te doorzien.',
    'Tao':          'Het Kruis van het Tao belichaamt de perfecte stroom van actie en expressie in het moment. Aanwezigheid is jouw gave.',
    'Ervaring':     'Het Kruis van Ervaring is ontworpen om te leren via het leven zelf. Elke ervaring is een leraar.',
    'Planning':     'Het Kruis van Planning draagt het vermogen om gemeenschappen te organiseren en duurzame structuren te bouwen.',
    'Familie':      'Het Kruis van de Familie draagt de gave van verbinding, zorg en het hechten van banden die generaties overstijgen.',
    'Invloed':      'Het Kruis van Invloed geeft de kracht om anderen te beïnvloeden via jouw aanwezigheid, visie en woorden.',
    'Overvloed':    'Het Kruis van Overvloed draagt de sleutel tot ware rijkdom — spiritueel, emotioneel en materieel.',
    'Mysterie':     'Het Kruis van het Mysterie is geboren om het onkenbare te verkennen — jij brengt het mysterie tot leven.',
    'Stilte':       'Het Kruis van Stilte is een leven in meesterlijke kalmte — jouw rust geeft anderen ruimte om tot zichzelf te komen.',
    'Revolutie':    'Het Kruis van de Revolutie draagt de kracht om te hervormen wat niet meer werkt. Jij bent geboren voor transformatie.',
    'Vitaliteit':   'Het Kruis van Vitaliteit straalt pure levensenergie uit — jouw vreugde en enthousiasme zijn aanstekelijk.',
    'Herkenning':   'Het Kruis van Herkenning helpt anderen zichzelf te zien. Jij bent een spiegel voor het potentiel van anderen.',
    'Inzicht':      'Het Kruis van Inzicht draagt de gave om doorbraken te bewerkstelligen — in denken, wetenschap en bewustzijn.',
}


# I Ching hexagram namen (traditioneel Chinees) gekoppeld aan HD gates
ICHING_NAMES = {
    1:'Het Scheppende',      2:'Het Ontvankelijke',   3:'Moeilijkheid bij het Begin',
    4:'Jeugdige Dwaasheid',  5:'Wachten',             6:'Conflict',
    7:'Het Leger',           8:'Samenhoud',            9:'De Kleine Temende Kracht',
    10:'Gedraging',          11:'Vrede',              12:'Stilstand',
    13:'Gelijkgezinden',     14:'Het Bezit in Overvloed',15:'Bescheidenheid',
    16:'Enthousiasme',       17:'Volgen',             18:'Werk aan het Bedorvene',
    19:'Nadering',           20:'Aanschouwen',        21:'Bijten door',
    22:'Sierlijkheid',       23:'Aftakeling',         24:'Terugkeer',
    25:'Onschuld',           26:'De Temende Kracht van het Grote',27:'Mondhoeken',
    28:'Overmaat van het Grote',29:'Het Gevaarlijke Diepe', 30:'Het Aanhangende Vuur',
    31:'Inwerking',          32:'Duur',               33:'Terugtrekking',
    34:'Groot Vermogen',     35:'Vooruitgang',        36:'Verduistering van het Licht',
    37:'De Familieleden',    38:'Tegenstelling',      39:'Belemmering',
    40:'Verlossing',         41:'Vermindering',       42:'Vermeerdering',
    43:'Doorbraak',          44:'Tegenkomen',         45:'Verzamelen',
    46:'Opgang',             47:'Uitputting',         48:'De Put',
    49:'Revolutie',          50:'De Oven',            51:'Het Opwindende',
    52:'Het Stilhouden',     53:'Geleidelijke Ontwikkeling',54:'De Huwende Meisje',
    55:'Overvloed',          56:'De Zwervende',       57:'Het Zachtmakende',
    58:'De Vreugde',         59:'Verstrooiing',       60:'Beperking',
    61:'Innerlijke Waarheid',62:'Overheersing van het Kleine',63:'Na de Voltooiing',
    64:'Voor de Voltooiing',
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
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED
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



def _enrich_channel(g1, g2):
    """Add name, circuit and description to a channel."""
    key = (min(g1,g2), max(g1,g2))
    data = CHANNEL_DATA.get(key, CHANNEL_DATA.get((g1,g2), {}))
    g1_name = GATE_NAMES.get(g1, {})
    g2_name = GATE_NAMES.get(g2, {})
    return {
        'name_nl': data.get('nl', f'{g1}-{g2}'),
        'name_en': data.get('en', f'{g1}-{g2}'),
        'circuit': data.get('circuit', ''),
        'circuit_en': data.get('circuit_en', ''),
        'desc_nl': data.get('desc_nl', ''),
        'gate1_name_nl': g1_name.get('nl', '') if isinstance(g1_name, dict) else '',
        'gate2_name_nl': g2_name.get('nl', '') if isinstance(g2_name, dict) else '',
    }

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

    p_colors = {}
    d_colors = {}

    all_planet_ids = PLANET_KEYS + ['earth']
    for pid in all_planet_ids:
        p_gates[pid] = lon_to_gate(p_lons[pid])
        d_gates[pid] = lon_to_gate(d_lons[pid])
        p_lines[pid] = lon_to_line(p_lons[pid])
        d_lines[pid] = lon_to_line(d_lons[pid])
        # Kleur = positie binnen de lijn (1-6)
        n_p = ((p_lons[pid] - HD_OFFSET) % 360 + 360) % 360
        n_d = ((d_lons[pid] - HD_OFFSET) % 360 + 360) % 360
        gate_size = 360/64
        line_size = gate_size/6
        color_size = line_size/6
        p_colors[pid] = int((n_p % line_size) / color_size) + 1
        d_colors[pid] = int((n_d % line_size) / color_size) + 1

    personality_gates = set(p_gates.values())
    design_gates = set(d_gates.values())
    all_gates = personality_gates | design_gates

    # Determine center definitions
    # ── CHANNEL CALCULATION (OFFICIAL METHOD) ──
    active_channels = []   # full channels (both gates active)
    half_channels = []     # half channels (one gate active)

    for (g1, g2) in UNIQUE_CHANNELS:
        p1 = g1 in personality_gates
        d1 = g1 in design_gates
        p2 = g2 in personality_gates
        d2 = g2 in design_gates

        has1 = p1 or d1
        has2 = p2 or d2

        if not (has1 or has2):
            continue

        # Determine color type
        p_active = p1 or p2
        d_active = d1 or d2

        if p_active and d_active:
            ch_type = 'both'
        elif p_active:
            ch_type = 'personality'
        elif d_active:
            ch_type = 'design'
        else:
            continue

        state = 'full' if (has1 and has2) else 'half'
        c1 = gate_to_center(g1)
        c2 = gate_to_center(g2)

        ch = {'g1': g1, 'g2': g2, 'c1': c1, 'c2': c2, 'type': ch_type, 'state': state}

        if state == 'full':
            active_channels.append(ch)
        else:
            half_channels.append(ch)

    # ── CENTER DEFINITIONS — only full channels define centers ──
    center_def = {c: 'undefined' for c in CENTER_GATES}
    for ch in active_channels:
        c1, c2 = ch['c1'], ch['c2']
        color = ch['type']
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

    # Determine Authority (priority order per Ra Uru Hu)
    # Ego authority: Will→Throat (21-45) OR G→Will (25-51)
    will_to_throat = any(
        (ch['c1'] == 'Will' and ch['c2'] == 'Throat') or
        (ch['c2'] == 'Will' and ch['c1'] == 'Throat')
        for ch in active_channels
    )
    g_to_will = any(
        (ch['c1'] == 'G' and ch['c2'] == 'Will') or
        (ch['c2'] == 'G' and ch['c1'] == 'Will')
        for ch in active_channels
    )
    g_to_throat = any(
        (ch['c1'] == 'G' and ch['c2'] == 'Throat') or
        (ch['c2'] == 'G' and ch['c1'] == 'Throat')
        for ch in active_channels
    )
    head_to_ajna = any(
        (ch['c1'] == 'Head' and ch['c2'] == 'Ajna') or
        (ch['c2'] == 'Head' and ch['c1'] == 'Ajna')
        for ch in active_channels
    )
    ajna_to_throat = any(
        (ch['c1'] == 'Ajna' and ch['c2'] == 'Throat') or
        (ch['c2'] == 'Ajna' and ch['c1'] == 'Throat')
        for ch in active_channels
    )

    if hd_type == 'Reflector':
        authority = 'Lunar'
    elif solar:
        authority = 'Emotional'
    elif sacral:
        authority = 'Sacral'
    elif spleen:
        authority = 'Splenic'
    elif will and (will_to_throat or g_to_will):
        # Ego authority: Will connected to Throat OR G connected to Will
        authority = 'Ego'
    elif g_to_throat:
        # Self-Projected: G directly connected to Throat (no motor)
        authority = 'SelfProjected'
    elif head_to_ajna or ajna_to_throat:
        # Mental/Outer Authority: only Head/Ajna defined
        authority = 'Mental'
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
    # Variables / 4 pijlen
    p_sun_color = p_colors.get(swe.SUN, 1)
    d_sun_color = d_colors.get(swe.SUN, 1)
    variables = calc_variables(p_sun_line, p_sun_color, d_sun_line, d_sun_color)

    # Angle is always derived from the personality-sun LINE, not from the static table:
    #   lines 5/6 → Left Angle Cross  |  line 3 → Juxtaposition  |  1/2/4 → Right Angle Cross
    if p_sun_line in (5, 6):
        cross_angle = 'Linker Hoek'
    elif p_sun_line == 3:
        cross_angle = 'Juxtapositie'
    else:
        cross_angle = 'Rechte Hoek'

    # Cross name: try (p_sun_gate, d_sun_gate) pair first (handles edge-line gate shifts),
    # then fall back to the gate-only table.
    cross_data = (INCARNATION_CROSSES_BY_PAIR.get((p_sun_gate, d_sun_gate))
                  or INCARNATION_CROSSES.get(p_sun_gate, {}))
    cross_name = cross_data.get('name', '') if cross_data else ''
    incarnation_cross = f"{cross_angle} Kruis van {cross_name}" if cross_name else f"Poort {p_sun_gate}/{p_earth_gate} — {d_sun_gate}/{d_earth_gate}"
    incarnation_cross_detail = {
        'name': cross_name,
        'angle': cross_angle,
        'gates': [p_sun_gate, p_earth_gate, d_sun_gate, d_earth_gate],
        'gateLines': [p_lines[swe.SUN], p_lines['earth'], d_lines[swe.SUN], d_lines['earth']],
        'label': incarnation_cross,
    }

    # Build activations list
    td = TYPE_DATA.get(hd_type, TYPE_DATA['Generator'])
    strategy = 'Wacht om te reageren, informeer dan' if subtype == 'Manifesting Generator' else td['strategy']

    activations = []
    # Sun first
    activations.append({
        'planet': 'Zon', 'icon': '☀', 'key': 'sun',
        'personality': {'gate': p_gates[swe.SUN], 'line': p_lines[swe.SUN],
                        'longitude': round(p_lons[swe.SUN], 3),
                        'gateName': GATE_NAMES.get(p_gates[swe.SUN], {}).get('nl', '') if isinstance(GATE_NAMES.get(p_gates[swe.SUN]), dict) else GATE_NAMES.get(p_gates[swe.SUN], '')},
        'design': {'gate': d_gates[swe.SUN], 'line': d_lines[swe.SUN],
                   'longitude': round(d_lons[swe.SUN], 3),
                   'gateName': GATE_NAMES.get(d_gates[swe.SUN], {}).get('nl', '') if isinstance(GATE_NAMES.get(d_gates[swe.SUN]), dict) else GATE_NAMES.get(d_gates[swe.SUN], '')}
    })
    # Earth
    activations.append({
        'planet': 'Aarde', 'icon': '⊕', 'key': 'earth',
        'personality': {'gate': p_gates['earth'], 'line': p_lines['earth'],
                        'longitude': round(p_lons['earth'], 3),
                        'gateName': GATE_NAMES.get(p_gates['earth'], {}).get('nl', '') if isinstance(GATE_NAMES.get(p_gates['earth']), dict) else GATE_NAMES.get(p_gates['earth'], '')},
        'design': {'gate': d_gates['earth'], 'line': d_lines['earth'],
                   'longitude': round(d_lons['earth'], 3),
                   'gateName': GATE_NAMES.get(d_gates['earth'], {}).get('nl', '') if isinstance(GATE_NAMES.get(d_gates['earth']), dict) else GATE_NAMES.get(d_gates['earth'], '')}
    })
    # Other planets
    for pid in PLANET_KEYS:
        if pid == swe.SUN:
            continue
        activations.append({
            'planet': PLANET_NAMES[pid], 'icon': PLANET_ICONS[pid], 'key': PLANET_STR_KEYS.get(pid, str(pid)),
            'personality': {'gate': p_gates[pid], 'line': p_lines[pid],
                            'longitude': round(p_lons[pid], 3),
                            'gateName': GATE_NAMES.get(p_gates[pid], {}).get('nl', '') if isinstance(GATE_NAMES.get(p_gates[pid]), dict) else GATE_NAMES.get(p_gates[pid], '')},
            'design': {'gate': d_gates[pid], 'line': d_lines[pid],
                       'longitude': round(d_lons[pid], 3),
                       'gateName': GATE_NAMES.get(d_gates[pid], {}).get('nl', '') if isinstance(GATE_NAMES.get(d_gates[pid]), dict) else GATE_NAMES.get(d_gates[pid], '')}
        })

    display_type = f"{hd_type} ({subtype})" if subtype else hd_type

    # Enrich activations with gate descriptions
    def enrich_gate(gate_num):
        d = GATE_DATA.get(gate_num, {})
        return {
            'number': gate_num,
            'name_nl': d.get('nl', ''),
            'name_en': d.get('en', ''),
            'keynote_nl': d.get('keynote_nl', ''),
            'shadow_nl': d.get('shadow_nl', ''),
            'gift_nl': d.get('gift_nl', ''),
            'iching_nl': ICHING_NAMES.get(gate_num, ''),
        }

    # Enrich center definitions
    enriched_centers = {}
    for center, state in center_def.items():
        desc = CENTER_DESCRIPTIONS.get(center, {})
        enriched_centers[center] = {
            'state': state,
            'name_nl': desc.get('nl', center),
            'name_en': desc.get('en', center),
            'function_nl': desc.get('function_nl', ''),
            'reading_nl': desc.get('defined_nl', '') if state != 'undefined' else desc.get('undefined_nl', ''),
            'not_self_nl': desc.get('not_self_nl', '') if state == 'undefined' else '',
        }

    # Profile description
    profile_desc = PROFILE_DESCRIPTIONS.get(profile_key, {})

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
        'incarnationCrossDetail': incarnation_cross_detail,
        'notself': td['notself'],
        'signature': td['signature'],
        'centerDefinitions': center_def,
        'definedCenters': [c for c, v in center_def.items() if v != 'undefined'],
        'undefinedCenters': [c for c, v in center_def.items() if v == 'undefined'],
        'activeChannels': [
            {
                'gates': [ch['g1'], ch['g2']],
                'type': ch['type'], 'state': ch['state'],
                'centers': [ch['c1'], ch['c2']],
                **_enrich_channel(ch['g1'], ch['g2'])
            }
            for ch in active_channels
        ],
        'halfChannels': [
            {
                'gates': [ch['g1'], ch['g2']],
                'type': ch['type'], 'state': ch['state'],
                'centers': [ch['c1'], ch['c2']],
                **_enrich_channel(ch['g1'], ch['g2'])
            }
            for ch in half_channels
        ],
        'personalityGates': sorted(list(personality_gates)),
        'designGates': sorted(list(design_gates)),
        'personalityGateDetails': [enrich_gate(g) for g in sorted(personality_gates)],
        'designGateDetails': [enrich_gate(g) for g in sorted(design_gates)],
        'activations': activations,
        'centerDetails': enriched_centers,
        'profileDescription': profile_desc,
        'circuits': {
            'individueel': [ch for ch in active_channels if CHANNEL_DATA.get((min(ch['g1'],ch['g2']),max(ch['g1'],ch['g2'])),{}).get('circuit') == 'Individueel'],
            'collectief':  [ch for ch in active_channels if CHANNEL_DATA.get((min(ch['g1'],ch['g2']),max(ch['g1'],ch['g2'])),{}).get('circuit') == 'Collectief'],
            'stammes':     [ch for ch in active_channels if CHANNEL_DATA.get((min(ch['g1'],ch['g2']),max(ch['g1'],ch['g2'])),{}).get('circuit') == 'Stammes'],
        },
        'variables': variables,
        'incarnationCrossDescription': INCARNATION_CROSS_DESCRIPTIONS.get(cross_name, ''),
        'accuracy': 'Swiss Ephemeris (pyswisseph)'
    }
