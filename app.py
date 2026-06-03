import logging
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from humandesign import calc_human_design
from bazi import calc_bazi
from numerology import calc_numerology

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
logger = logging.getLogger(__name__)

# ─── App ──────────────────────────────────────────────────────────────────────

app = Flask(__name__)

ALLOWED_ORIGINS = [
    'https://theorderofthequietpath.github.io',
    'http://localhost:3333',
    'http://localhost:5173',
    'http://localhost:3001',
]

CORS(app, origins=ALLOWED_ORIGINS)

# ─── Input validatie helpers ──────────────────────────────────────────────────

def require_fields(data, *fields):
    """Geeft een foutmelding terug als een vereist veld ontbreekt."""
    if not isinstance(data, dict):
        return 'Ongeldige JSON payload.'
    for field in fields:
        if field not in data or data[field] is None:
            return f"Veld '{field}' is verplicht."
    return None

def validate_birth_data(data):
    """Valideert geboortedata-velden."""
    err = require_fields(data, 'year', 'month', 'day')
    if err:
        return err
    try:
        year  = int(data['year'])
        month = int(data['month'])
        day   = int(data['day'])
        if not (1900 <= year <= 2100):
            return 'Ongeldig geboortejaar.'
        if not (1 <= month <= 12):
            return 'Ongeldige geboortemaand.'
        if not (1 <= day <= 31):
            return 'Ongeldige geboortedag.'
    except (ValueError, TypeError):
        return 'Geboortedata moeten nummers zijn.'
    return None

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def health():
    return jsonify({'status': 'ok', 'service': 'The Order of the Quiet Path API'})

@app.route('/api/human-design', methods=['POST'])
def human_design():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Ongeldige of ontbrekende JSON body.'}), 400

    err = validate_birth_data(data)
    if err:
        return jsonify({'error': err}), 400

    try:
        result = calc_human_design(data)
        logger.info('Human Design berekend', extra={'year': data.get('year')})
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception('Human Design fout')
        return jsonify({'error': 'Berekening mislukt. Controleer je invoer.'}), 500

@app.route('/api/bazi', methods=['POST'])
def bazi():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Ongeldige of ontbrekende JSON body.'}), 400

    err = validate_birth_data(data)
    if err:
        return jsonify({'error': err}), 400

    try:
        result = calc_bazi(data)
        logger.info('BaZi berekend', extra={'year': data.get('year')})
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception('BaZi fout')
        return jsonify({'error': 'Berekening mislukt. Controleer je invoer.'}), 500

@app.route('/api/numerology', methods=['POST'])
def numerology():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Ongeldige of ontbrekende JSON body.'}), 400

    err = require_fields(data, 'year', 'month', 'day')
    if err:
        return jsonify({'error': err}), 400

    try:
        result = calc_numerology(data)
        logger.info('Numerologie berekend')
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.exception('Numerologie fout')
        return jsonify({'error': 'Berekening mislukt. Controleer je invoer.'}), 500

@app.route('/api/reading', methods=['POST'])
def reading():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Ongeldige of ontbrekende JSON body.'}), 400

    hd_data        = data.get('hd', {})
    numerology_data = data.get('numerology', {})
    bazi_data      = data.get('bazi', {})
    name           = str(data.get('firstname', 'je'))[:64]  # begrensd

    try:
        text = generate_reading(hd_data, numerology_data, bazi_data, name)
        return jsonify({'text': text})
    except Exception as e:
        logger.exception('Reading generatie fout')
        return jsonify({'error': 'Reading generatie mislukt.'}), 500

# ─── Reading generator ─────────────────────────────────────────────────────────

def generate_reading(hd, num, bazi, name):
    lines = []

    # ── Human Design ──
    if hd.get('type'):
        type_texts = {
            'Generator': (
                f'Als Generator ben jij de levenskracht — {name} is hier om te reageren op het leven. '
                f'Je sacrale energie is je grootste kompas.'
            ),
            'Manifestor': (
                f'Als Manifestor draag jij een zeldzame kracht — {name} is hier om te initiëren. '
                f'Informeren voor je handelt opent deuren.'
            ),
            'Projector': (
                f'Als Projector zie jij wat anderen niet zien — {name} heeft het vermogen systemen en mensen '
                f'diep te begrijpen. Wacht op de uitnodiging.'
            ),
            'Reflector': (
                f'Als Reflector ben jij de spiegel van je omgeving — {name} weerspiegelt de gezondheid '
                f'van de gemeenschap.'
            ),
            'Manifesting Generator': (
                f'Als Manifesting Generator combineert {name} de kracht van de Generator met het initiatief '
                f'van de Manifestor — reageer én initieer, maar informeer.'
            ),
        }
        lines.append(type_texts.get(hd['type'], f"Jouw Human Design type is {hd['type']}."))

    if hd.get('profile'):
        lines.append(
            f"Je {hd['profile']} profiel geeft jouw leven een specifieke kleur — "
            f"dit is de rol die jij speelt in het grotere geheel."
        )

    # ── Numerologie ──
    if num.get('lifePath'):
        lp_texts = {
            1:  'Je levenspadgetal 1 wijst op leiderschap — jij baant nieuwe wegen.',
            2:  'Je levenspadgetal 2 wijst op diplomatie — jij brengt mensen samen.',
            3:  'Je levenspadgetal 3 wijst op creativiteit — jij bent hier om te delen.',
            4:  'Je levenspadgetal 4 wijst op structuur — jij legt de fundering.',
            5:  'Je levenspadgetal 5 wijst op vrijheid — jij bent hier om te ervaren.',
            6:  'Je levenspadgetal 6 wijst op zorg en harmonie — jij heelt en verbindt.',
            7:  'Je levenspadgetal 7 wijst op diepgang — jij zoekt de waarheid.',
            8:  'Je levenspadgetal 8 wijst op kracht — jij bouwt iets blijvends.',
            9:  'Je levenspadgetal 9 wijst op wijsheid — jij draagt een universele missie.',
            11: 'Je meestergetal 11 wijst op spiritueel inzicht — jij verlicht anderen.',
            22: 'Je meestergetal 22 is de meesterbouwer — jij realiseert visies op grote schaal.',
            33: 'Je meestergetal 33 is de meesterleraar — jij draagt liefde als gift.',
        }
        lines.append(lp_texts.get(num['lifePath'], f"Je levenspadgetal {num['lifePath']} draagt een unieke boodschap."))

    # ── BaZi dagmeester ──
    dm = bazi.get('dayMaster', {}) if bazi else {}
    if dm.get('element'):
        polarity  = dm.get('polarity', '')
        pol_label = 'Yang' if polarity == '+' else 'Yin' if polarity == '-' else ''
        lines.append(
            f"Je BaZi dagmeester is {pol_label} {dm['element']} — dit is de kern van jouw innerlijke aard, "
            f"het element dat bepaalt hoe jij de wereld ervaart en verwerkt."
        )

    # ── Relatie-analyse ──
    relations    = bazi.get('relations', {}) if bazi else {}
    dm_strength  = relations.get('dm_strength', {})

    if dm_strength.get('strength_label'):
        strength = dm_strength['strength_label']
        yong     = dm_strength.get('yong_shen', '')
        fav      = dm_strength.get('favourable_elements', [])
        lines.append(
            f"Jouw dagmeester is {strength.lower()} in kracht. "
            f"Het gunstige element voor jou is {yong} — omgevingen, kleuren en tijdperken "
            f"die {', '.join(fav)} energie belichamen werken mee in jouw voordeel."
        )

    branch_clashes = relations.get('branch_clashes', [])
    if branch_clashes:
        clash_desc = [
            f"{c['pair'][0]}–{c['pair'][1]} ({c['positions'][0]} ↔ {c['positions'][1]})"
            for c in branch_clashes
        ]
        lines.append(
            f"Er zijn {len(branch_clashes)} actieve botsing(en) in jouw grafiek: "
            f"{', '.join(clash_desc)}. Dit wijst op een ingebouwde spanning of dynamiek "
            f"die energie vrijzet — destruktief of transformatief, afhankelijk van bewustzijn."
        )

    complete_combos = [c for c in relations.get('combinations', []) if c.get('complete')]
    if complete_combos:
        combo_desc = [
            f"{c.get('type', '').replace('_', ' ')} ({c.get('element', '')})"
            for c in complete_combos
        ]
        lines.append(
            f"Jouw grafiek bevat {len(complete_combos)} volledige combinatie(s): "
            f"{', '.join(combo_desc)}. Combinaties versterken het betrokken element aanzienlijk."
        )

    if relations.get('punishments'):
        lines.append(
            "Er is een straf-configuratie aanwezig in jouw grafiek. Dit duidt op een "
            "terugkerend patroon dat om bewuste aandacht vraagt — niet als vloek, maar als leraar."
        )

    lines.append(
        "Dit is een automatische eerste laag van jouw kosmische blauwdruk. "
        "Voor een volledige, persoonlijke duiding met alle lagen — neem contact op met Shi Ming Dao."
    )

    return '\n\n'.join(lines)

# ─── Start ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
