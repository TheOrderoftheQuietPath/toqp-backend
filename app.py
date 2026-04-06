from flask import Flask, request, jsonify
from flask_cors import CORS
from humandesign import calc_human_design
from bazi import calc_bazi
from numerology import calc_numerology

app = Flask(__name__)
CORS(app)

@app.route('/')
def health():
    return jsonify({'status': 'ok', 'service': 'The Order of the Quiet Path API (Python)'})

@app.route('/api/human-design', methods=['POST'])
def human_design():
    try:
        data = request.json
        result = calc_human_design(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bazi', methods=['POST'])
def bazi():
    try:
        data = request.json
        result = calc_bazi(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/numerology', methods=['POST'])
def numerology():
    try:
        data = request.json
        result = calc_numerology(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reading', methods=['POST'])
def reading():
    try:
        data = request.json
        hd = data.get('hd', {})
        numerology_data = data.get('numerology', {})
        bazi_data = data.get('bazi', {})
        name = data.get('firstname', 'je')
        text = generate_reading(hd, numerology_data, bazi_data, name)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_reading(hd, num, bazi, name):
    lines = []
    if hd.get('type'):
        type_texts = {
            'Generator': f'Als Generator ben jij de levenskracht — {name} is hier om te reageren op het leven. Je sacrale energie is je grootste kompas.',
            'Manifestor': f'Als Manifestor draag jij een zeldzame kracht — {name} is hier om te initiëren. Informeren voor je handelt opent deuren.',
            'Projector': f'Als Projector zie jij wat anderen niet zien — {name} heeft het vermogen systemen en mensen diep te begrijpen. Wacht op de uitnodiging.',
            'Reflector': f'Als Reflector ben jij de spiegel van je omgeving — {name} weerspiegelt de gezondheid van de gemeenschap.'
        }
        lines.append(type_texts.get(hd['type'], f"Jouw Human Design type is {hd['type']}."))
    if hd.get('profile'):
        lines.append(f"Je {hd['profile']} profiel geeft jouw leven een specifieke kleur — dit is de rol die jij speelt in het grotere geheel.")
    if num.get('lifePath'):
        lp_texts = {
            1:'Je levenspadgetal 1 wijst op leiderschap — jij baant nieuwe wegen.',
            2:'Je levenspadgetal 2 wijst op diplomatie — jij brengt mensen samen.',
            3:'Je levenspadgetal 3 wijst op creativiteit — jij bent hier om te delen.',
            4:'Je levenspadgetal 4 wijst op structuur — jij legt de fundering.',
            5:'Je levenspadgetal 5 wijst op vrijheid — jij bent hier om te ervaren.',
            6:'Je levenspadgetal 6 wijst op zorg en harmonie — jij heelt en verbindt.',
            7:'Je levenspadgetal 7 wijst op diepgang — jij zoekt de waarheid.',
            8:'Je levenspadgetal 8 wijst op kracht — jij bouwt iets blijvends.',
            9:'Je levenspadgetal 9 wijst op wijsheid — jij draagt een universele missie.',
            11:'Je meestergetal 11 wijst op spiritueel inzicht — jij verlicht anderen.',
            22:'Je meestergetal 22 is de meesterbouwer — jij realiseert visies op grote schaal.',
            33:'Je meestergetal 33 is de meesterleraar — jij draagt liefde als gift.'
        }
        lines.append(lp_texts.get(num['lifePath'], f"Je levenspadgetal {num['lifePath']} draagt een unieke boodschap."))
    if bazi and bazi.get('dayMaster', {}).get('element'):
        lines.append(f"Je BaZi dag-meester ({bazi['dayMaster']['element']}) onthult jouw ware innerlijke aard.")
    lines.append("Dit is een eerste blik op jouw kosmische blauwdruk. Voor een volledige persoonlijke duiding — neem contact op met Shi Ming Dao.")
    return '\n\n'.join(lines)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
