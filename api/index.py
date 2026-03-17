from flask import Flask, render_template, request, jsonify
import numpy as np

app.run(...)

# --- ១. ទិន្នន័យបទដ្ឋាន (Reference Metadata) ---
# អ្នកអាចបន្ថែមជួរទិន្នន័យក្នុងនេះឱ្យកាន់តែច្រើនដើម្បីឱ្យ AI កាន់តែឆ្លាត
METALS_DATABASE = [
    {"type": "Gold", "purity": "24K (99.9%)", "rgb": [255, 215, 0], "desc": "មាសសុទ្ធទឹកដប់"},
    {"type": "Gold", "purity": "22K (91.6%)", "rgb": [255, 200, 46], "desc": "មាសគីឡូ"},
    {"type": "Gold", "purity": "18K (75.0%)", "rgb": [212, 175, 55], "desc": "មាសសម្រាប់គ្រឿងអលង្ការ"},
    {"type": "Platinum", "purity": "Pt950", "rgb": [229, 228, 226], "desc": "ផ្លាកទីនទឹកខ្ពស់"},
    {"type": "Platinum", "purity": "Pt900", "rgb": [192, 192, 192], "desc": "ផ្លាកទីនទឹកមធ្យម"},
    {"type": "Silver/Fake", "purity": "Low Purity", "rgb": [160, 160, 160], "desc": "ប្រាក់ ឬលោហៈធាតុលាយច្រើន"}
]

# --- ២. អនុគមន៍ AI សម្រាប់គណនា (Core Logic) ---
def analyze_color(user_rgb):
    """
    ប្រើរូបមន្ត r-mean Euclidean Distance ដើម្បីរកពណ៌ដែលនៅជិតបំផុត
    """
    r1, g1, b1 = user_rgb
    best_match = None
    min_dist = float('inf')

    for metal in METALS_DATABASE:
        r2, g2, b2 = metal['rgb']
        
        # រូបមន្តគណនាចម្ងាយពណ៌ដែលភ្នែកមនុស្សមើលឃើញ (Perceptual Color Distance)
        rmean = (r1 + r2) / 2
        dR = r1 - r2
        dG = g1 - g2
        dB = b1 - b2
        
        # គណនា Distance (កាន់តែតូច កាន់តែដូច)
        dist = np.sqrt(
            (2 + rmean/256) * (dR**2) + 
            4 * (dG**2) + 
            (2 + (255 - rmean)/256) * (dB**2)
        )

        if dist < min_dist:
            min_dist = dist
            best_match = metal

    # គណនាភាគរយនៃទំនុកចិត្ត (Confidence)
    # យើងសន្មត់ថាបើចម្ងាយពណ៌ > 150 គឺមិនមែនជាលោហៈក្នុងបញ្ជីឡើយ
    confidence = max(0, 100 - (min_dist / 1.5))
    
    return {
        "metal_type": best_match['type'],
        "purity": best_match['purity'],
        "description": best_match['desc'],
        "confidence": f"{confidence:.2f}%",
        "dist_score": round(min_dist, 2),
        "status": "Success" if confidence > 70 else "Low Accuracy"
    }

# --- ៣. កំណត់ Route សម្រាប់ Web App ---

@app.route('/')
def home():
    """បង្ហាញទំព័រ HTML ក្បាលម៉ាស៊ីន"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """API ច្រកចេញចូលសម្រាប់ទទួលទិន្នន័យពី HTML"""
    try:
        # ទទួលទិន្នន័យ JSON ផ្ញើមកពី JavaScript (fetch)
        data = request.get_json()
        if not data or 'rgb' not in data:
            return jsonify({"error": "មិនមានទិន្នន័យ RGB"}), 400

        user_rgb = [
            int(data['rgb']['r']),
            int(data['rgb']['g']),
            int(data['rgb']['b'])
        ]

        # បញ្ជូនទៅកាន់ AI Logic
        result = analyze_color(user_rgb)
        
        # បន្ថែមព័ត៌មាន RGB ដែលរកឃើញត្រឡប់ទៅវិញ
        result['detected_rgb'] = f"RGB({user_rgb[0]}, {user_rgb[1]}, {user_rgb[2]})"
        
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # ដំណើរការ Server លើ Port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)