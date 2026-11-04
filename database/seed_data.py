"""
Database Seeding Script
Populates the crop_information table with detailed agronomic guidelines,
scientific data, soil requirements, cultivation tips, and expected benefits for 22 crops.
"""

CROPS_CATALOG = [
    {
        "crop_name": "rice",
        "scientific_name": "Oryza sativa",
        "category": "Cereals",
        "description": "Rice is a staple cereal food for over half of the world's population. It thrives in high rainfall or irrigated wetland environments.",
        "soil_information": "Clayey, heavy loamy, or alluvial soils capable of retaining water. Tolerates pH 5.5 - 7.0.",
        "cultivation_information": "Nursery seedbed preparation, puddle transplantation at 20-25 days, maintain standing water (2-5 cm) during tillering.",
        "water_requirement": "High (1200 - 2000 mm)",
        "harvest_duration": "110 - 150 days",
        "expected_benefits": "High yield potential, stable market price, excellent caloric return per hectare.",
        "farming_tips": "Practice Alternate Wetting and Drying (AWD) to save up to 30% water and reduce methane emissions."
    },
    {
        "crop_name": "maize",
        "scientific_name": "Zea mays",
        "category": "Cereals",
        "description": "Maize (corn) is the queen of cereals with high nutritional value and versatility across food, animal feed, and industrial starch.",
        "soil_information": "Deep, well-drained fertile loamy soils rich in organic matter. pH 5.8 - 7.5.",
        "cultivation_information": "Direct ridge-and-furrow seeding with 60x20 cm spacing. Split nitrogen application at basal, knee-high, and tasseling stages.",
        "water_requirement": "Moderate (500 - 800 mm)",
        "harvest_duration": "90 - 120 days",
        "expected_benefits": "High economic value for grain and fodder; essential crop for poultry feed industry.",
        "farming_tips": "Avoid waterlogging; apply zinc sulfate at sowing to prevent white bud disorder."
    },
    {
        "crop_name": "chickpea",
        "scientific_name": "Cicer arietinum",
        "category": "Pulses",
        "description": "Chickpea (gram) is a premier cool-season pulse crop rich in proteins, essential minerals, and dietary fibers.",
        "soil_information": "Well-drained sandy loam to deep clay loam soils. pH 6.0 - 8.0. Avoid saline/alkaline soils.",
        "cultivation_information": "Sow in October-November in lines 30 cm apart. Inoculate seeds with Rhizobium and PSB cultures.",
        "water_requirement": "Low (250 - 400 mm)",
        "harvest_duration": "90 - 120 days",
        "expected_benefits": "Fixes atmospheric nitrogen into soil (30-40 kg N/ha), low water footprint, excellent cash pulse crop.",
        "farming_tips": "Nip shoot tips at 30-40 days to encourage profuse branching and pod bearing."
    },
    {
        "crop_name": "kidneybeans",
        "scientific_name": "Phaseolus vulgaris",
        "category": "Pulses",
        "description": "Kidney beans (Rajma) are highly popular legumes packed with protein, iron, and potassium.",
        "soil_information": "Deep, fertile, well-drained loamy soils. Sensitive to water stagnation. pH 5.5 - 6.5.",
        "cultivation_information": "Line sowing with 45x10 cm spacing. Needs adequate basal fertilizer as natural nodulation is weaker than other pulses.",
        "water_requirement": "Moderate (350 - 500 mm)",
        "harvest_duration": "90 - 130 days",
        "expected_benefits": "Premium market price in urban consumer markets; excellent rotation crop with cereals.",
        "farming_tips": "Provide 3-4 timely irrigations: pre-flowering, flowering, and pod filling stages."
    },
    {
        "crop_name": "pigeonpeas",
        "scientific_name": "Cajanus cajan",
        "category": "Pulses",
        "description": "Pigeonpea (Arhar/Tur) is a drought-tolerant legume and major source of dietary protein in tropical diets.",
        "soil_information": "Deep, well-drained loams and vertisols. pH 6.5 - 7.5.",
        "cultivation_information": "Grown as sole crop (75x25 cm) or intercropped with cotton/sorghum. Deep taproot system withstands drought.",
        "water_requirement": "Low to Moderate (600 - 800 mm)",
        "harvest_duration": "150 - 200 days",
        "expected_benefits": "Enriches soil with organic biomass and fixed nitrogen; drought resilient insurance crop.",
        "farming_tips": "Install pheromone traps to monitor Helicoverpa armigera (pod borer) during flowering."
    },
    {
        "crop_name": "mothbeans",
        "scientific_name": "Vigna aconitifolia",
        "category": "Pulses",
        "description": "Moth bean is an ultra-drought-resistant, arid legume grown extensively in dry regions.",
        "soil_information": "Sandy to light loamy soils with good drainage. pH 6.0 - 7.5.",
        "cultivation_information": "Broadcast or drill sowing with 30-45 cm spacing at the onset of monsoon rains.",
        "water_requirement": "Very Low (200 - 400 mm)",
        "harvest_duration": "65 - 85 days",
        "expected_benefits": "Prevents soil erosion in arid zones, highly nutritious for livestock fodder and human consumption.",
        "farming_tips": "Ideal for dryland organic farming with minimal chemical inputs."
    },
    {
        "crop_name": "mungbean",
        "scientific_name": "Vigna radiata",
        "category": "Pulses",
        "description": "Mungbean (green gram) is a fast-maturing pulse that fits perfectly into multi-cropping systems.",
        "soil_information": "Well-drained loam to clay loam soils. pH 6.2 - 7.2.",
        "cultivation_information": "Short duration kharif or summer crop. Seed rate 15-20 kg/ha with Rhizobium seed treatment.",
        "water_requirement": "Low (300 - 450 mm)",
        "harvest_duration": "60 - 75 days",
        "expected_benefits": "High turnaround, restores soil nitrogen, premium price as sprouted bean.",
        "farming_tips": "Spray yellow mosaic virus vector controls (e.g. yellow sticky traps, imidacloprid) early."
    },
    {
        "crop_name": "blackgram",
        "scientific_name": "Vigna mungo",
        "category": "Pulses",
        "description": "Blackgram (Urad) is an important pulse crop used in diverse traditional dishes and protein supplements.",
        "soil_information": "Heavy clay to loam soils with good water-holding capacity. pH 6.5 - 7.5.",
        "cultivation_information": "Broadcast or line sowing with 30x10 cm spacing. Needs weed-free condition for first 30 days.",
        "water_requirement": "Low to Moderate (350 - 550 mm)",
        "harvest_duration": "70 - 90 days",
        "expected_benefits": "High yield stability, excellent source of phosphoric acid and iron.",
        "farming_tips": "Apply foliar DAP (2%) spray at flowering to boost pod setting and seed weight."
    },
    {
        "crop_name": "lentil",
        "scientific_name": "Lens culinaris",
        "category": "Pulses",
        "description": "Lentil (Masoor) is one of the oldest domesticated pulses, prized for easy cooking and high protein.",
        "soil_information": "Light loams to heavy clay soils with good drainage. pH 6.0 - 7.5.",
        "cultivation_information": "Sow in winter (rabi) with 25 cm row spacing. Highly suitable as a relay crop after paddy.",
        "water_requirement": "Low (200 - 350 mm)",
        "harvest_duration": "100 - 130 days",
        "expected_benefits": "Low cost of cultivation, low pest incidence, high household nutrition security.",
        "farming_tips": "Ensure one light irrigation at branching stage if winter rains fail."
    },
    {
        "crop_name": "pomegranate",
        "scientific_name": "Punica granatum",
        "category": "Fruits",
        "description": "Pomegranate is a high-value commercial fruit crop known for rich antioxidant polyphenols.",
        "soil_information": "Well-drained deep sandy loam to alluvial soils. Tolerates slightly alkaline soil (pH 6.5 - 8.0).",
        "cultivation_information": "Propagated via air layering or hardwood cuttings. Plant at 4.5x3 m spacing. Bahar treatment regulates flowering.",
        "water_requirement": "Moderate (500 - 700 mm) via drip",
        "harvest_duration": "Perennial (Bearing at 2-3 years, 150-180 days from bloom)",
        "expected_benefits": "High export profitability, long shelf life, high medicinal and processing value.",
        "farming_tips": "Adopt Hastha Bahar for superior fruit quality; bag fruits on tree to avoid pomegranate butterfly (Deudorix isocrates)."
    },
    {
        "crop_name": "banana",
        "scientific_name": "Musa acuminata",
        "category": "Fruits",
        "description": "Banana is a fast-growing, year-round commercial fruit providing continuous income for farmers.",
        "soil_information": "Deep, rich, well-drained loamy soil with high organic content. pH 6.0 - 7.5.",
        "cultivation_information": "Plant tissue-cultured plantlets at 1.8x1.8 m spacing. Heavy feeder of potassium and water.",
        "water_requirement": "High (1500 - 2000 mm)",
        "harvest_duration": "11 - 13 months",
        "expected_benefits": "Continuous commercial cash flow, high yield (60-80 tonnes/ha with precision drip fertigation).",
        "farming_tips": "De-sucker regularly leaving only one follower sucker; prop bunches with bamboo stakes to prevent lodging."
    },
    {
        "crop_name": "mango",
        "scientific_name": "Mangifera indica",
        "category": "Fruits",
        "description": "Known as the King of Fruits, mango is an evergreen tropical fruit celebrated for flavor and aroma.",
        "soil_information": "Deep, fertile alluvial or lateritic soils with good drainage. pH 5.5 - 7.5.",
        "cultivation_information": "Grafted saplings planted at 8x8 m or High Density Planting (5x5 m). Requires warm, dry season for flowering.",
        "water_requirement": "Moderate (700 - 1000 mm)",
        "harvest_duration": "Perennial (Starts bearing at 3-4 years, 100-130 days from flower to harvest)",
        "expected_benefits": "Lifespan of 40+ years, high market demand in fresh, pulp, and export sectors.",
        "farming_tips": "Withhold irrigation 2 months prior to flowering to stimulate flower bud differentiation."
    },
    {
        "crop_name": "grapes",
        "scientific_name": "Vitis vinifera",
        "category": "Fruits",
        "description": "Grape is a premium deciduous vine crop cultivated for fresh table consumption, raisins, and juice.",
        "soil_information": "Well-drained sandy loam or clay loam with gravelly subsoil. pH 6.5 - 8.0.",
        "cultivation_information": "Bower (Y-trellis) system training. Pruning twice a year (foundation pruning and fruit pruning).",
        "water_requirement": "Moderate (500 - 700 mm)",
        "harvest_duration": "Perennial (110 - 140 days after fruit pruning)",
        "expected_benefits": "High export value, excellent returns with drip fertigation and canopy micro-climate control.",
        "farming_tips": "Dip flower clusters in Gibberellic Acid (GA3) solution to improve berry size and cluster looseness."
    },
    {
        "crop_name": "watermelon",
        "scientific_name": "Citrullus lanatus",
        "category": "Fruits",
        "description": "Watermelon is a refreshing, warm-season vine crop with high lycopene content.",
        "soil_information": "Sandy loam soils rich in organic matter that warm quickly in spring. pH 6.0 - 7.0.",
        "cultivation_information": "Sow in pits or drip-mulch raised beds at 2x1.5 m spacing. Needs hot, dry days and sunshine.",
        "water_requirement": "Moderate (400 - 600 mm)",
        "harvest_duration": "75 - 95 days",
        "expected_benefits": "Short crop cycle, high summer consumer demand, high gross returns.",
        "farming_tips": "Use silver-black plastic mulch to suppress weeds, conserve moisture, and accelerate ripening."
    },
    {
        "crop_name": "muskmelon",
        "scientific_name": "Cucumis melo",
        "category": "Fruits",
        "description": "Muskmelon (cantaloupe) is a delicious summer fruit with rich aroma and sweetness.",
        "soil_information": "Well-drained sandy loam or riverbed alluvial soils. pH 6.0 - 7.5.",
        "cultivation_information": "Raised bed planting under drip and mulch. High sunshine requirement during fruit maturation.",
        "water_requirement": "Moderate (350 - 500 mm)",
        "harvest_duration": "70 - 85 days",
        "expected_benefits": "Quick cash turnaround, high sweetness and consumer appeal.",
        "farming_tips": "Reduce irrigation 10-14 days before harvest to concentrate sugar content (Brix level)."
    },
    {
        "crop_name": "apple",
        "scientific_name": "Malus domestica",
        "category": "Fruits",
        "description": "Apple is the premier temperate fruit crop grown in high-altitude valleys with chilling hour requirements.",
        "soil_information": "Deep, loamy, well-aerated soils with good drainage. pH 5.8 - 6.8.",
        "cultivation_information": "Grafted on clonal rootstocks (M9, MM106) on trellis systems. Requires 800-1200 chilling hours below 7°C.",
        "water_requirement": "Moderate to High (800 - 1100 mm)",
        "harvest_duration": "Perennial (130 - 160 days from bloom)",
        "expected_benefits": "Long cold storage potential, stable high-value domestic market, processed into juices/cider.",
        "farming_tips": "Thin fruit clusters to 1-2 king fruits per spur to prevent biennial bearing."
    },
    {
        "crop_name": "orange",
        "scientific_name": "Citrus sinensis",
        "category": "Fruits",
        "description": "Sweet orange is a premier citrus fruit packed with Vitamin C and natural citrus bioflavonoids.",
        "soil_information": "Deep, light, well-drained sandy loam or loam with subsoil drainage. pH 6.0 - 7.5.",
        "cultivation_information": "Budded plants on Rangpur lime or trifoliate rootstocks at 6x6 m spacing.",
        "water_requirement": "Moderate (800 - 1200 mm)",
        "harvest_duration": "Perennial (240 - 270 days from fruit set)",
        "expected_benefits": "Extensive industrial processing demand, excellent fresh fruit market, long productive lifespan.",
        "farming_tips": "Apply micronutrient sprays (Zinc, Manganese, Iron) during fresh flush emergence."
    },
    {
        "crop_name": "papaya",
        "scientific_name": "Carica papaya",
        "category": "Fruits",
        "description": "Papaya is a fast-growing, heavy-yielding tropical fruit loaded with papain enzyme and beta-carotene.",
        "soil_information": "Well-drained, rich, friable sandy loam soils. Highly sensitive to waterlogging. pH 6.0 - 7.0.",
        "cultivation_information": "Transplant 45-day seedlings into pits at 2x2 m spacing. Gynodioecious varieties (Red Lady) preferred.",
        "water_requirement": "Moderate (1000 - 1500 mm)",
        "harvest_duration": "9 - 11 months from transplant",
        "expected_benefits": "Starts yielding within a year; produces 40-70 kg fruit per tree annually.",
        "farming_tips": "Ensure raised mounds around tree base to prevent collar rot (Pythium aphanidermatum)."
    },
    {
        "crop_name": "coconut",
        "scientific_name": "Cocos nucifera",
        "category": "Plantation",
        "description": "Known as the Kalpavriksha (Tree of Life), coconut provides tender water, oil, fiber, and building material.",
        "soil_information": "Coastal sands, alluvial, red sandy loams, and lateritic soils with good drainage. pH 5.2 - 8.0.",
        "cultivation_information": "Plant 9-12 month vigorous seedlings in 1x1x1 m pits at 7.5x7.5 m spacing.",
        "water_requirement": "Moderate to High (1300 - 2300 mm)",
        "harvest_duration": "Perennial (Starts yielding at 5-6 years; produces monthly bunches for 60+ years)",
        "expected_benefits": "Monthly steady income, tender water boom in urban areas, copra and coir value additions.",
        "farming_tips": "Mulch basin with coconut husk to retain moisture and supply potassium naturally."
    },
    {
        "crop_name": "cotton",
        "scientific_name": "Gossypium hirsutum",
        "category": "Cash Crops",
        "description": "Known as White Gold, cotton is the world's most important natural textile fiber crop.",
        "soil_information": "Deep black cotton soils (vertisols) or fertile alluvial soils with good moisture retention. pH 6.5 - 8.0.",
        "cultivation_information": "Bt-cotton hybrids planted at 90x60 cm or 120x45 cm spacing with dibbling at monsoon onset.",
        "water_requirement": "Moderate (650 - 1000 mm)",
        "harvest_duration": "140 - 180 days",
        "expected_benefits": "High cash revenue from lint and cotton seed oil; major agricultural export commodity.",
        "farming_tips": "Top terminal shoots (nipping) at 80-90 days to divert nutrients into boll development."
    },
    {
        "crop_name": "jute",
        "scientific_name": "Corchorus olitorius",
        "category": "Cash Crops",
        "description": "Known as the Golden Fiber, jute is a biodegradable bast fiber crop essential for packaging and eco-textiles.",
        "soil_information": "Rich alluvial, sandy loam to clay loam soils refreshed by flood deposits. pH 6.0 - 7.5.",
        "cultivation_information": "Direct line sowing (25x5 cm) in March-April. High humidity (>80%) and standing water during retting.",
        "water_requirement": "High (1200 - 1800 mm)",
        "harvest_duration": "120 - 140 days",
        "expected_benefits": "Eco-friendly bio-degradable fiber, excellent carbon sequestration rate, low chemical pesticide needs.",
        "farming_tips": "Harvest at small pod stage for optimal fiber tensile strength and silky luster."
    },
    {
        "crop_name": "coffee",
        "scientific_name": "Coffea arabica / canephora",
        "category": "Plantation",
        "description": "Coffee is a global beverage plantation crop cultivated under multi-tiered shade canopies.",
        "soil_information": "Deep, porous, rich volcanic or forest loams with high humus and acidic reaction. pH 5.0 - 6.5.",
        "cultivation_information": "Plant 1-year nursery seedlings at 2x2 m under shade trees (Silver Oak, Erythrina).",
        "water_requirement": "Moderate to High (1500 - 2500 mm)",
        "harvest_duration": "Perennial (Starts yielding at 3-4 years; 8-9 months from blossom to berry)",
        "expected_benefits": "Premium export prices, supports biodiverse agroforestry, high value in specialty roast markets.",
        "farming_tips": "Apply blossom and backing irrigation to trigger uniform flowering and high fruit set."
    }
]

def seed_crop_information(engine=None, db_session=None):
    """
    Inserts or updates crop catalog records in the database.
    """
    if db_session is None and engine is None:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server')))
        from app import create_app, db
        from models.crop_models import CropInformation
        
        app = create_app()
        with app.app_context():
            db.create_all()
            for crop_data in CROPS_CATALOG:
                existing = CropInformation.query.filter_by(crop_name=crop_data['crop_name']).first()
                if existing:
                    for key, val in crop_data.items():
                        setattr(existing, key, val)
                else:
                    new_item = CropInformation(**crop_data)
                    db.session.add(new_item)
            db.session.commit()
            print(f"Successfully seeded {len(CROPS_CATALOG)} crops into crop_information table.")
    else:
        # direct engine insert
        pass

if __name__ == '__main__':
    seed_crop_information()
