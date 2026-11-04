"""
Script to update database/disease_info.json with:
1. Expected Recovery / Management Period (disease-specific, realistic range)
2. Recommendation 1 (Primary management / chemical / curative option)
3. Recommendation 2 (Alternative management / biological / cultural option)
4. Full profiles for the 3 new crops:
   - Green Gram (Vigna radiata): Cercospora leaf spot, Yellow mosaic, Powdery mildew, healthy
   - Cotton (Gossypium spp.): Bacterial blight, Leaf curl virus, Alternaria leaf spot, healthy
   - Pigeon Pea (Cajanus cajan): Sterility mosaic, Phytophthora blight, Cercospora leaf spot, healthy
5. Localized entries for English, Hindi (hi), and Marathi (mr).
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "database", "disease_info.json")

# Metadata mapping for existing 41 classes
EXISTING_UPDATES = {
    "Apple___Apple_scab": {
        "recovery_period": "10–14 days of intensive management to arrest sporulation and protect emerging foliage",
        "recommendation_1": "Apply protective fungicide (Captan 50 WP at 2 g/L or Mancozeb 75 WP at 2.5 g/L) from green tip through petal fall according to label directions.",
        "recommendation_2": "Apply bio-fungicide Bacillus subtilis or liquid copper octanoate at 7-day intervals to suppress secondary conidial germination.",
        "hi": {
            "recovery_period": "उचित प्रबंधन के साथ 10-14 दिन में बीजाणु प्रसार रुकता है",
            "recommendation_1": "कैप्टन 50 WP (2 ग्रा/ली) या मैंकोजेब 75 WP (2.5 ग्रा/ली) सुरक्षात्मक कवकनाशी का छिड़काव करें।",
            "recommendation_2": "बैसिलस सबटिलिस या तरल कॉपर फॉर्मूलेशन जैसे जैव-कवकनाशी का 7 दिन के अंतराल पर छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "योग्य व्यवस्थापनासह १० ते १४ दिवसांत बुरशीचा प्रादुर्भाव रोखता येतो",
            "recommendation_1": "कॅप्टन ५० डब्ल्यूपी (२ ग्रॅम/लि) किंवा मॅन्कोझेब ७५ डब्ल्यूपी (२.५ ग्रॅम/लि) बुरशीनाशकाची फवारणी करा.",
            "recommendation_2": "बॅसिलस सबटिलिस किंवा कॉपरयुक्त जैविक बुरशीनाशकाची ७ दिवसांच्या अंतराने फवारणी करा."
        }
    },
    "Apple___Black_rot": {
        "recovery_period": "14–21 days of active management with limb canker sanitation and protective spray cycles",
        "recommendation_1": "Prune out dead wood, mummified fruits, and cankered branches 15 cm below visibly diseased tissue during dry weather.",
        "recommendation_2": "Apply preventative sprays of Thiophanate-methyl 70 WP or Captan starting at tight cluster through mid-summer.",
        "hi": {
            "recovery_period": "संक्रमित टहनियों की छंटाई और छिड़काव के साथ 14-21 दिन का प्रबंधन आवश्यक है",
            "recommendation_1": "सूखी लकड़ियों, सड़े फलों और कैंकर वाली शाखाओं को रोगग्रस्त भाग से 15 सेमी नीचे से काटकर नष्ट करें।",
            "recommendation_2": "थायोफॅनेट-मिथाइल 70 WP या कैप्टन का निवारक छिड़काव कली निकलने से लेकर मध्य-गर्मी तक करें।"
        },
        "mr": {
            "recovery_period": "रोगट फांद्यांची छाटणी आणि फवारणी चक्रासह १४ ते २१ दिवसांचे व्यवस्थापन आवश्यक",
            "recommendation_1": "वाळलेल्या फांद्या, सडलेली फळे आणि बुरशीग्रस्त भाग १५ सेंमी खालून छाटून नष्ट करा.",
            "recommendation_2": "थायोफॅनेट-मिथाईल ७० डब्ल्यूपी किंवा कॅप्टन बुरशीनाशकाची नियमित अंतराने फवारणी करा."
        }
    },
    "Apple___Cedar_apple_rust": {
        "recovery_period": "10–14 days of protective fungicide cover during warm spring rain periods",
        "recommendation_1": "Apply systemic triazole fungicides like Myclobutanil or Propiconazole starting at pink bud stage until 2–3 weeks post petal-fall.",
        "recommendation_2": "Prune cedar apple galls on nearby juniper/cedar windbreaks and maintain an open tree canopy for rapid leaf drying.",
        "hi": {
            "recovery_period": "वसंत ऋतु की बारिश के दौरान 10-14 दिन का सुरक्षात्मक कवकनाशी प्रबंधन",
            "recommendation_1": "माइक्लोबुटानिल या प्रोपिकोनाजोल जैसे सिस्टेमिक कवकनाशी का छिड़काव गुलाबी कली अवस्था से शुरू करें।",
            "recommendation_2": "आसपास के जूनिपर वृक्षों से रतुआ की गांठों की छंटाई करें और हवा के संचार के लिए पेड़ की छतरी खुली रखें।"
        },
        "mr": {
            "recovery_period": "वसंत ऋतूतील पावसाच्या काळात १० ते १४ दिवसांचे संरक्षणात्मक व्यवस्थापन",
            "recommendation_1": "मायक्लोब्युटानिल किंवा प्रोपिकोनाझोल या आंतरप्रवाही बुरशीनाशकांची कळी अवस्थेपासून फवारणी करा.",
            "recommendation_2": "परिसरातील जुनिपर झाडांवरील गाठी छाटून नष्ट करा आणि बागेत सूर्यप्रकाश खेळता ठेवा."
        }
    },
    "Apple___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain regular preventive monitoring",
        "recommendation_1": "Maintain routine scouting every 7–10 days and ensure balanced nitrogen and potassium orchard fertilization.",
        "recommendation_2": "Apply organic compost and dormant horticultural oil during winter to suppress overwintering pest populations.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। नियमित निगरानी बनाए रखें",
            "recommendation_1": "प्रत्येक 7-10 दिनों में नियमित निरीक्षण करें और संतुलित उर्वरक प्रबंधन बनाए रखें।",
            "recommendation_2": "जैविक कम्पोस्ट और शीतकालीन बागवानी तेल का उपयोग करके कीटों का पूर्व-नियंत्रण करें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — पाने निरोगी आहेत. नियमित निरीक्षण चालू ठेवा",
            "recommendation_1": "दर ७ ते १० दिवसांनी नियमित पाहणी करा आणि संतुलित खतांचा वापर करा.",
            "recommendation_2": "सेंद्रिय खतांचा वापर करा आणि हिवाळ्यात फळबागेचे योग्य व्यवस्थापन ठेवा."
        }
    },
    "Blueberry___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain soil acidity (pH 4.5–5.2) and drip irrigation",
        "recommendation_1": "Maintain soil pH in the optimal acidic range (4.5–5.2) using elemental sulfur or organic pine mulch.",
        "recommendation_2": "Use drip irrigation to keep root zone evenly moist while avoiding wetting canopy foliage.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। मिट्टी की अम्लीयता (pH 4.5–5.2) बनाए रखें",
            "recommendation_1": "सल्फर या जैविक मल्च की सहायता से मिट्टी का pH 4.5-5.2 के बीच बनाए रखें।",
            "recommendation_2": "ड्रिप सिंचाई का उपयोग करें जिससे जड़ें नम रहें और पत्तियों पर पानी न पड़े।"
        },
        "mr": {
            "recovery_period": "लागू नाही — पाने निरोगी आहेत. जमिनीचा सामू ४.५ ते ५.२ दरम्यान ठेवा",
            "recommendation_1": "सल्फर किंवा पालापाचोळ्याच्या आच्छादनाने जमिनीचा सामू ४.५ ते ५.२ दरम्यान संतुलित ठेवा.",
            "recommendation_2": "ठिबक सिंचनाचा वापर करून झाडांच्या मुळाशी योग्य ओलावा राखा."
        }
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "recovery_period": "7–14 days of fungicide spray cycles to suppress active powdery mycelium",
        "recommendation_1": "Apply wettable sulfur (2–3 g/L) or potassium bicarbonate early in the morning when temperatures are below 30°C.",
        "recommendation_2": "Apply systemic sterol-inhibitor fungicides such as Myclobutanil or Tebuconazole if mildew pressure is high.",
        "hi": {
            "recovery_period": "सक्रिय फफूंद रोकने के लिए 7-14 दिन का कवकनाशी छिड़काव चक्र आवश्यक है",
            "recommendation_1": "तापमान 30°C से कम होने पर सुबह वेटेबल सल्फर (2-3 ग्रा/ली) का छिड़काव करें।",
            "recommendation_2": "रोग का प्रकोप अधिक होने पर माइक्लोबुटानिल या टेबुकोनाजोल जैसे सिस्टेमिक कवकनाशी का छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "भुरी रोगाचा प्रादुर्भाव नियंत्रणात आणण्यासाठी ७ ते १४ दिवस लागतात",
            "recommendation_1": "सकाळी लवकर पाण्यात विरघळणारे गंधक (२-३ ग्रॅम/लि) तापमान ३०°C पेक्षा कमी असताना फवारावे.",
            "recommendation_2": "प्रादुर्भाव जास्त असल्यास मायक्लोब्युटानिल किंवा टेब्युकोनाझोल आंतरप्रवाही बुरशीनाशकाची फवारणी करा."
        }
    },
    "Cherry_(including_sour)___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain regular canopy pruning and irrigation",
        "recommendation_1": "Prune interior branches in late winter to promote airflow and maximize sunlight penetration.",
        "recommendation_2": "Apply balanced micronutrient foliar spray and monitor for leaf spot pathogens post-harvest.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। नियमित छंटाई और सिंचाई बनाए रखें",
            "recommendation_1": "सर्दियों के अंत में आंतरिक शाखाओं की छंटाई करें ताकि धूप और हवा का संचार बना रहे।",
            "recommendation_2": "संतुलित सूक्ष्म पोषक तत्वों का छिड़काव करें और तुड़ाई के बाद पत्ती रोगों की जांच करें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — पाने निरोगी आहेत. झाडांची योग्य छाटणी व पाणी व्यवस्थापन राखा",
            "recommendation_1": "झाडांमध्ये हवा आणि सूर्यप्रकाश खेळता राहण्यासाठी योग्य छाटणी करा.",
            "recommendation_2": "सूक्ष्म अन्नद्रव्यांची फवारणी करा आणि काढणीनंतर नियमित पाहणी करा."
        }
    },
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot": {
        "recovery_period": "10–14 days of foliar fungicide management under humid conditions",
        "recommendation_1": "Apply a combination fungicide containing azoxystrobin + propiconazole at VT-R1 (tasseling/silking) stages.",
        "recommendation_2": "Practice crop rotation with non-grass crops and till residue to accelerate fungal decomposition.",
        "hi": {
            "recovery_period": "नमी वाले मौसम में 10-14 दिन का कवकनाशी प्रबंधन आवश्यक है",
            "recommendation_1": "मक्के में मंजर/सिल्क आने की अवस्था (VT-R1) पर एजोक्सीस्ट्रोबिन + प्रोपिकोनाजोल का छिड़काव करें।",
            "recommendation_2": "गैर-घास फसलों के साथ फसल चक्र अपनाएं और फसल अवशेषों को मिट्टी में मिलाएं।"
        },
        "mr": {
            "recovery_period": "दमट हवामानात १० ते १४ दिवसांचे बुरशीनाशक व्यवस्थापन आवश्यक",
            "recommendation_1": "तुरा येण्याच्या अवस्थेत अझॉक्सीस्ट्रॉबिन + प्रोपिकोनाझोल युक्त बुरशीनाशकाची फवारणी करा.",
            "recommendation_2": "पीक फेरपालट करा आणि काढणीनंतर शेतातील धसकटे जमिनीत गाडून टाका."
        }
    },
    "Corn_(maize)___Common_rust_": {
        "recovery_period": "7–12 days of monitoring and canopy management under favorable weather conditions",
        "recommendation_1": "Apply triazole or strobilurin-based foliar fungicide (e.g., Azoxystrobin + Difenoconazole) if pustules appear before tasseling.",
        "recommendation_2": "Ensure good field drainage and avoid excessive nitrogen top-dressing which stimulates succulent susceptible foliage.",
        "hi": {
            "recovery_period": "अनुकूल मौसम में 7-12 दिन की सघन निगरानी और प्रबंधन आवश्यक है",
            "recommendation_1": "मंजर निकलने से पहले रतुआ के फफोले दिखने पर एजोक्सीस्ट्रोबिन + डिफेनोकोनाजोल का छिड़काव करें।",
            "recommendation_2": "खेत में जल निकासी सुनिश्चित करें और अत्यधिक नाइट्रोजन के उपयोग से बचें।"
        },
        "mr": {
            "recovery_period": "योग्य हवामानात ७ ते १२ दिवसांचे निरीक्षण आणि व्यवस्थापन आवश्यक",
            "recommendation_1": "कणीस धरण्यापूर्वी तांबेऱ्याचे ठिपके दिसल्यास अझॉक्सीस्ट्रॉबिन + डायफेनोकोनॅझोलची फवारणी करा.",
            "recommendation_2": "शेतात पाण्याचा निचरा चांगला ठेवा आणि नत्र खतांचा अतिरेक टाळा."
        }
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "recovery_period": "10–14 days of protective fungicide coverage to protect ear leaves",
        "recommendation_1": "Apply Pyraclostrobin or Mancozeb sprays at first sign of cigar-shaped lesions prior to tasseling.",
        "recommendation_2": "Rotate out of corn for at least 1 year and plant resistant corn hybrids (containing Ht genes).",
        "hi": {
            "recovery_period": "भुट्टे की पत्तियों की सुरक्षा के लिए 10-14 दिन का कवकनाशी प्रबंधन",
            "recommendation_1": "मंजर आने से पहले सिगार के आकार के धब्बे दिखने पर पायराक्लोस्ट्रोबिन या मैंकोजेब का छिड़काव करें।",
            "recommendation_2": "कम से कम 1 वर्ष के लिए मक्के की जगह अन्य फसल लगाएं और रोग-प्रतिरोधी संकर किस्में चुनें।"
        },
        "mr": {
            "recovery_period": "कंसाच्या पानांचे रक्षण करण्यासाठी १० ते १४ दिवसांचे व्यवस्थापन आवश्यक",
            "recommendation_1": "पानांवर लांबट डाग दिसू लागताच पायराक्लोस्ट्रॉबिन किंवा मॅन्कोझेबची फवारणी करा.",
            "recommendation_2": "किमान एक वर्ष मक्याऐवजी दुसरे पीक घ्या आणि रोगप्रतिकारक वाणांची निवड करा."
        }
    },
    "Corn_(maize)___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain optimal nitrogen, phosphorus, and moisture balance",
        "recommendation_1": "Apply split nitrogen applications aligned with vegetative growth stages (V4 and V8) and monitor for stem borers.",
        "recommendation_2": "Maintain adequate soil moisture during tasseling and grain filling stages for maximum yield potential.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। नाइट्रोजन, फास्फोरस और नमी का संतुलन बनाए रखें",
            "recommendation_1": "वानस्पतिक वृद्धि अवस्था (V4 और V8) पर विभाजित नाइट्रोजन दें और तना छेदक की निगरानी करें।",
            "recommendation_2": "मंजर आने और दाना भरने के समय पर्याप्त सिंचाई सुनिश्चित करें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — मक्याची पाने निरोगी आहेत. योग्य खत व पाणी व्यवस्थापन ठेवा",
            "recommendation_1": "वाढीच्या टप्प्यात योग्य प्रमाणात खतांचा हप्ता द्या आणि खोडकिडीवर लक्ष ठेवा.",
            "recommendation_2": "तुरा येण्याच्या आणि दाणे भरण्याच्या नाजूक टप्प्यात पाण्याचा ताण पडू देऊ नका."
        }
    },
    "Grape___Black_rot": {
        "recovery_period": "14–21 days of rigorous canopy and chemical management during fruit set",
        "recommendation_1": "Apply protective systemic fungicides such as Myclobutanil (0.05%) or Tebuconazole starting from early shoot development.",
        "recommendation_2": "Prune lower leaf canopy to maximize sun exposure and spray bio-fungicide Bacillus amyloliquefaciens.",
        "hi": {
            "recovery_period": "फल लगने के दौरान 14-21 दिन का सघन कवकनाशी और छतरी प्रबंधन आवश्यक है",
            "recommendation_1": "शाखाओं के विकास से ही माइक्लोबुटानिल (0.05%) या टेबुकोनाजोल का सुरक्षात्मक छिड़काव करें।",
            "recommendation_2": "धूप और हवा के लिए निचली पत्तियों की छंटाई करें और बैसिलस जैव-कवकनाशी का छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "घड तयार होताना १४ ते २१ दिवसांचे काटेकोर बुरशीनाशक व कॅनोपी व्यवस्थापन आवश्यक",
            "recommendation_1": "पालवी फुटण्याच्या वेळेपासून मायक्लोब्युटानिल (०.०५%) किंवा टेब्युकोनाझोलची प्रतिबंधात्मक फवारणी करा.",
            "recommendation_2": "घडांवर सूर्यप्रकाश पडण्यासाठी पानांची विरळणी करा आणि बॅसिलस जैविक बुरशीनाशक वापरा."
        }
    },
    "Grape___Esca_(Black_Measles)": {
        "recovery_period": "Long-term trunk disease: Requires 3–4 weeks for wound protection and vine stabilization",
        "recommendation_1": "Protect all major pruning wounds immediately with fungicidal wound sealant or acrylic paint containing thiophanate-methyl.",
        "recommendation_2": "Apply Trichoderma-based pruning wound bio-protectants (e.g., Trichoderma atroviride) during dormant pruning.",
        "hi": {
            "recovery_period": "दीर्घकालिक तना रोग: घाव भरने और स्थिरीकरण के लिए 3-4 सप्ताह का प्रबंधन आवश्यक है",
            "recommendation_1": "छंटाई के घावों पर तुरंत थायोफॅनेट-मिथाइल युक्त फफूंदनाशक पेस्ट या सीलेंट लगाएं।",
            "recommendation_2": "सुप्त छंटाई के दौरान ट्राइकोडर्मा आधारित जैविक सुरक्षा एजेंट का उपयोग करें।"
        },
        "mr": {
            "recovery_period": "दीर्घकालीन खोड रोग: छाटणीच्या जखमा भरून येण्यासाठी ३ ते ४ आठवड्यांचे व्यवस्थापन आवश्यक",
            "recommendation_1": "छाटणीनंतरच्या जखमांवर लगेच थायोफॅनेट-मिथाईल किंवा बोर्डो पेस्ट लावा.",
            "recommendation_2": "विश्रांती काळातील छाटणीच्या वेळी ट्रायकोडर्मा जैविक संरक्षक वापरा."
        }
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "recovery_period": "10–14 days of protective fungicide spraying post-monsoon",
        "recommendation_1": "Apply Mancozeb 75 WP (2.5 g/L) or Copper oxychloride (3 g/L) thoroughly covering leaf undersides.",
        "recommendation_2": "Ensure canopy aeration through regular shoot positioning and avoid microclimate moisture retention.",
        "hi": {
            "recovery_period": "मानसून के बाद 10-14 दिन का सुरक्षात्मक कवकनाशी छिड़काव आवश्यक है",
            "recommendation_1": "पत्तियों की निचली सतह को ढकते हुए मैंकोजेब 75 WP (2.5 ग्रा/ली) या कॉपर ऑक्सीक्लोराइड का छिड़काव करें।",
            "recommendation_2": "शाखाओं को सही दिशा देकर छतरी में हवा का प्रवाह बनाए रखें।"
        },
        "mr": {
            "recovery_period": "पावसाळ्यानंतर १० ते १४ दिवसांचे संरक्षणात्मक बुरशीनाशक व्यवस्थापन",
            "recommendation_1": "पानांच्या खालच्या बाजूस मॅन्कोझेब ७५ डब्ल्यूपी (२.५ ग्रॅम/लि) किंवा कॉपर ऑक्सिक्लोराईडची फवारणी करा.",
            "recommendation_2": "फांद्यांची योग्य बांधणी करून बागेत दमटपणा साचू देऊ नका."
        }
    },
    "Grape___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain shoot positioning, balanced nutrition, and canopy aeration",
        "recommendation_1": "Maintain regular shoot thinning, shoot tipping, and cluster zone leaf removal for optimal sun exposure.",
        "recommendation_2": "Apply balanced potassium and calcium foliar sprays during berry development to strengthen berry skins.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। शाखाओं की छंटाई और संतुलित पोषण बनाए रखें",
            "recommendation_1": "धूप के लिए नियमित शाखा छंटाई और गुच्छों के आसपास की पत्तियों को हटाएं।",
            "recommendation_2": "फलों के विकास के समय पोटाश और कैल्शियम का छिड़काव करें जिससे फलों की त्वचा मजबूत हो।"
        },
        "mr": {
            "recovery_period": "लागू नाही — द्राक्षाची पाने निरोगी आहेत. कॅनोपी व पोषण व्यवस्थापन योग्य ठेवा",
            "recommendation_1": "घडांना चांगला सूर्यप्रकाश मिळण्यासाठी वेळेवर शेंडे मारणे व पानांची विरळणी करा.",
            "recommendation_2": "मणी वाढीच्या काळात पोटॅशियम व कॅल्शियमची फवारणी करून मण्यांची गुणवत्ता सुधारा."
        }
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "recovery_period": "Systemic bacterial infection: Vector psyllid control requires 10–14 days; infected trees require rehabilitation or removal",
        "recommendation_1": "Control Asian citrus psyllid vectors immediately with systemic insecticides such as Imidacloprid or Thiamethoxam.",
        "recommendation_2": "Apply enhanced foliar nutritional sprays (zinc, manganese, iron, potassium) to sustain productivity of symptomatic trees.",
        "hi": {
            "recovery_period": "सिस्टेमिक जीवाणु रोग: वेक्टर कीट नियंत्रण में 10-14 दिन लगते हैं; अत्यधिक संक्रमित पौधों को हटाना पड़ सकता है",
            "recommendation_1": "इमिडाक्लोप्रिड या थायामेथोक्सम जैसे कीटनाशकों से सिट्रस साइला कीट को तुरंत नियंत्रित करें।",
            "recommendation_2": "जिंक, मैंगनीज, लोहा और पोटाश का फोलियर स्प्रे देकर पौधों का पोषण सुधारें।"
        },
        "mr": {
            "recovery_period": "आंतरप्रवाही जिवाणू रोग: सायला किडीचे नियंत्रण १० ते १४ दिवसांत करणे आवश्यक; झाडांचे योग्य पुनर्वसन करा",
            "recommendation_1": "इमिडाक्लोप्रिड किंवा थायामेथोक्सामची फवारणी करून सिट्रस सायला किडीचा तात्काळ नायनाट करा.",
            "recommendation_2": "झिंक, मॅंगनीज, फेरस आणि पोटॅशियमयुक्त सूक्ष्म अन्नद्रव्यांची फवारणी करून झाडांना ताकद द्या."
        }
    },
    "Peach___Bacterial_spot": {
        "recovery_period": "10–14 days of bactericide management during warm, wet spring weather",
        "recommendation_1": "Apply low rates of copper bactericide (copper hydroxide) mixed with oxytetracycline from shuck split onward.",
        "recommendation_2": "Avoid excessive nitrogen fertilizers that stimulate succulent susceptible growth and establish windbreaks.",
        "hi": {
            "recovery_period": "वसंत ऋतु के नम मौसम में 10-14 दिन का जीवाणुनाशक प्रबंधन आवश्यक है",
            "recommendation_1": "ऑक्सीटेट्रासाइक्लिन के साथ कॉपर हाइड्रॉक्साइड की कम मात्रा का छिड़काव करें।",
            "recommendation_2": "अत्यधिक नाइट्रोजन उर्वरक से बचें और बगीचे के चारों ओर वायु-अवरोधक लगाएं।"
        },
        "mr": {
            "recovery_period": "उबदार व दमट हवामानात १० ते १४ दिवसांचे जिवाणूनाशक व्यवस्थापन आवश्यक",
            "recommendation_1": "ऑक्सिटेट्रासायक्लिनसोबत कॉपर हायड्रॉक्साईडची हलकी फवारणी करा.",
            "recommendation_2": "अवाजवी नत्र खतांचा वापर टाळा आणि बागेभोवती वारा प्रतिबंधक झाडे लावा."
        }
    },
    "Peach___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain regular canopy pruning and fruit thinning",
        "recommendation_1": "Thin fruit early to 6 inches apart to promote large, high-quality peaches and avoid branch breakage.",
        "recommendation_2": "Apply dormant copper spray in autumn after 90% leaf drop to prevent peach leaf curl.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। नियमित छंटाई और फलों की विरलता बनाए रखें",
            "recommendation_1": "फलों को 6 इंच की दूरी पर विरल करें ताकि उच्च गुणवत्ता वाले फल प्राप्त हों।",
            "recommendation_2": "शरद ऋतु में पत्ती झड़ने के बाद सुप्त कॉपर स्प्रे का उपयोग करें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — पाने निरोगी आहेत. झाडांची छाटणी व फळांची विरळणी वेळेवर करा",
            "recommendation_1": "उत्कृष्ट दर्जाच्या फळांसाठी फळांची योग्य विरळणी करा.",
            "recommendation_2": "पानगळीनंतर सुप्तावस्थेत कॉपरची फवारणी करा जेणेकरून पानांचा पीळ रोग रोखता येईल."
        }
    },
    "Pepper__bell___Bacterial_spot": {
        "recovery_period": "10–14 days of bactericide management with strict avoidance of overhead irrigation",
        "recommendation_1": "Apply copper hydroxide tank-mixed with Mancozeb to increase bactericidal efficacy against copper-tolerant Xanthomonas.",
        "recommendation_2": "Apply plant defense activator Acibenzolar-S-methyl (Actigard) or bio-bactericide Bacillus subtilis strain QST 713.",
        "hi": {
            "recovery_period": "फव्वारा सिंचाई से बचते हुए 10-14 दिन का जीवाणुनाशक प्रबंधन आवश्यक है",
            "recommendation_1": "कॉपर हाइड्रॉक्साइड को मैंकोजेब के साथ मिलाकर छिड़कें जिससे जीवाणुओं पर असर तेज हो।",
            "recommendation_2": "पौधे की रोग प्रतिरोधक क्षमता बढ़ाने वाले एक्टिवेटर या बैसिलस सबटिलिस जैव-कीटनाशक का छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "तुषार सिंचन टाळून १० ते १४ दिवसांचे जिवाणूनाशक व्यवस्थापन आवश्यक",
            "recommendation_1": "कॉपर हायड्रॉक्साईड सोबत मॅन्कोझेब एकत्र करून फवारणी करा ज्यामुळे जिवाणू नियंत्रण अधिक प्रभावी होते.",
            "recommendation_2": "झाडांची प्रतिकारशक्ती वाढवणारे ॲक्टिगार्ड किंवा बॅसिलस सबटिलिस जैविक जिवाणूनाशक वापरा."
        }
    },
    "Pepper__bell___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain drip irrigation, staking, and balanced calcium-magnesium feeding",
        "recommendation_1": "Ensure adequate soil calcium and steady soil moisture to prevent blossom end rot.",
        "recommendation_2": "Stake plants early to support heavy fruit loads and protect branches from wind damage.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। ड्रिप सिंचाई और कैल्शियम-मैग्नीशियम पोषण बनाए रखें",
            "recommendation_1": "ब्लॉसम एंड रॉट (फल का पिछला हिस्सा सड़ना) से बचने के लिए मिट्टी में कैल्शियम और नमी बनाए रखें।",
            "recommendation_2": "फलों के भार से पौधों को बचाने के लिए शुरुआती सहारा (स्टेकिंग) दें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — मिरचीची पाने निरोगी आहेत. ठिबक सिंचन व कॅल्शियम-मॅग्नेशियमचे योग्य पोषण ठेवा",
            "recommendation_1": "फळे सडणे टाळण्यासाठी जमिनीत कॅल्शियम व ओलाव्याचे संतुलन राखा.",
            "recommendation_2": "झाडांना वेळेवर आधार (स्टेकिंग) द्या जेणेकरून फळांच्या वजनाने फांद्या मोडणार नाहीत."
        }
    },
    "Potato___Early_blight": {
        "recovery_period": "7–14 days with proper fungicide scheduling and irrigation management",
        "recommendation_1": "Apply protectant fungicides like Chlorothalonil (2 g/L) or Mancozeb (2.5 g/L) alternately with systemic Difenoconazole.",
        "recommendation_2": "Apply bio-rational copper octanoate or Trichoderma harzianum soil-foliar applications and avoid overhead sprinkler watering.",
        "hi": {
            "recovery_period": "उचित कवकनाशी और सिंचाई प्रबंधन के साथ 7-14 दिन में सुधार देखा जाता है",
            "recommendation_1": "क्लोरोथैलोनिल (2 ग्रा/ली) या मैंकोजेब (2.5 ग्रा/ली) को डिफेनोकोनाजोल के साथ बारी-बारी से छिड़कें।",
            "recommendation_2": "ट्राइकोडर्मा या तरल कॉपर का उपयोग करें और ऊपर से फव्वारा सिंचाई से बचें।"
        },
        "mr": {
            "recovery_period": "योग्य बुरशीनाशक व पाणी व्यवस्थापनाने ७ ते १४ दिवसांत रोग नियंत्रणात येतो",
            "recommendation_1": "क्लोरोथॅलोनिल (२ ग्रॅम/लि) किंवा मॅन्कोझेब आणि डायफेनोकोनॅझोलची आलटून-पालटून फवारणी करा.",
            "recommendation_2": "ट्रायकोडर्मा हरझियानम किंवा कॉपर अष्टकाचा वापर करा आणि वरून पाणी देणे टाळा."
        }
    },
    "Potato___Late_blight": {
        "recovery_period": "5–10 days of rapid intervention; late blight requires immediate suppression to prevent total haulm destruction",
        "recommendation_1": "Apply systemic anti-oomycete fungicides such as Cymoxanil + Mancozeb (2.5 g/L) or Dimethomorph + Mancozeb upon first detection.",
        "recommendation_2": "Rogue out and bury severely infected focal plants immediately, and follow with protective Metalaxyl + Mancozeb sprays.",
        "hi": {
            "recovery_period": "त्वरित हस्तक्षेप के साथ 5-10 दिन; लेट ब्लाइट को फसल नष्ट होने से बचाने के लिए तुरंत दबाना आवश्यक है",
            "recommendation_1": "पहला लक्षण दिखते ही साइमोक्सानिल + मैंकोजेब (2.5 ग्रा/ली) या डाइमेथोमोर्फ + मैंकोजेब का छिड़काव करें।",
            "recommendation_2": "संक्रमित पौधों को तुरंत उखाड़कर जमीन में दबा दें और मेटालेक्सिल + मैंकोजेब का सुरक्षात्मक छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "तात्काळ उपाययोजना करून ५ ते १० दिवस; करपा वेगाने पसरत असल्याने त्वरित नियंत्रण आवश्यक",
            "recommendation_1": "लक्षणे दिसताच सायमोक्सॅनिल + मॅन्कोझेब (२.५ ग्रॅम/लि) किंवा डायमेथोमॉर्फची तातडीने फवारणी करा.",
            "recommendation_2": "बाधित झाडे तात्काळ उपटून जमिनीत गाडून टाका आणि मेटॅलॅक्सिल + मॅन्कोझेबची संरक्षक फवारणी करा."
        }
    },
    "Potato___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain proper hilling, uniform watering, and balanced potash",
        "recommendation_1": "Perform earthing-up (hilling) around plant bases to protect developing tubers from sun greening and blight spores.",
        "recommendation_2": "Ensure adequate potassium fertilizer and maintain uniform soil moisture to maximize tuber size.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। मिट्टी चढ़ाना (हिलिंग) और पोटाश का उचित प्रयोग बनाए रखें",
            "recommendation_1": "कंदों को धूप और बीजाणुओं से बचाने के लिए पौधों की जड़ों पर मिट्टी चढ़ाएं (हिलिंग करें)।",
            "recommendation_2": "कंदों के अच्छे विकास के लिए पर्याप्त पोटाश और समान सिंचाई बनाए रखें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — बटाट्याची पाने निरोगी आहेत. झाडांना भर लावणे व पोटॅश खतांचा वापर योग्य ठेवा",
            "recommendation_1": "बटाटे उघडे पडून हिरवे होऊ नयेत म्हणून झाडांच्या बुंध्याशी नियमित मातीची भर लावा.",
            "recommendation_2": "कंदांचा आकार वाढवण्यासाठी योग्य प्रमाणात पोटॅशियम खते आणि नियमित पाणी द्या."
        }
    },
    "Raspberry___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain trellis support, post-harvest cane thinning, and drip watering",
        "recommendation_1": "Prune out spent floricanes after harvest and tie primocanes to the trellis wire.",
        "recommendation_2": "Use organic wood chip mulch around roots and avoid overhead sprinkler watering.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। ट्रेलिस सहारा और पुरानी शाखाओं की छंटाई करें",
            "recommendation_1": "तुड़ाई के बाद पुरानी शाखाओं की छंटाई करें और नई शाखाओं को तारों से सहारा दें।",
            "recommendation_2": "जड़ों के पास लकड़ी के बुरादे का मल्च लगाएं और ऊपर से पानी देने से बचें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — पाने निरोगी आहेत. झाडांना तारांचा आधार द्या व जुन्या फांद्या छाटा",
            "recommendation_1": "काढणीनंतर जुन्या फांद्या कापून नवीन फांद्यांना तारेचा आधार द्या.",
            "recommendation_2": "मुळाशी आच्छादन करा आणि पानांवर पाणी तुषारू देऊ नका."
        }
    },
    "Soybean___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain regular field scouting, proper spacing, and weed management",
        "recommendation_1": "Scout lower canopy weekly for early signs of rust, bacterial lesions, or defoliating caterpillars.",
        "recommendation_2": "Inoculate seeds with Bradyrhizobium japonicum and maintain balanced phosphorus-potassium soil fertility.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। नियमित निरीक्षण, उचित अंतर और खरपतवार नियंत्रण बनाए रखें",
            "recommendation_1": "निचली पत्तियों की साप्ताहिक जांच करें ताकि रतुआ या जीवाणु रोगों का समय पर पता चल सके।",
            "recommendation_2": "बीजों को राइजोबियम से उपचारित करें और फास्फोरस-पोटाश का संतुलित प्रयोग करें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — सोयाबीनची पाने निरोगी आहेत. नियमित पाहणी, योग्य अंतर व तण नियंत्रण ठेवा",
            "recommendation_1": "तांबेरा किंवा करप्याच्या सुरुवातीच्या लक्षणांसाठी खालच्या पानांची आठवड्यातून एकदा पाहणी करा.",
            "recommendation_2": "पेरणीवेळी रायझोबियम जीवाणू संवर्धकाची बीजप्रक्रिया करा आणि संतुलित खते द्या."
        }
    },
    "Squash___Powdery_mildew": {
        "recovery_period": "7–10 days of bio-fungicide or sulfur spray to arrest white mycelial expansion",
        "recommendation_1": "Apply potassium bicarbonate or horticultural mineral oil (1–2%) at the first sign of powdery talc-like spots.",
        "recommendation_2": "Apply biological fungicide containing Bacillus amyloliquefaciens or wettable sulfur (avoid sulfur above 32°C).",
        "hi": {
            "recovery_period": "सफेद फफूंद रोकने के लिए 7-10 दिन का कवकनाशी या सल्फर छिड़काव आवश्यक है",
            "recommendation_1": "पाउडर जैसे सफेद धब्बे दिखते ही पोटैशियम बाइकार्बोनेट या बागवानी तेल (1-2%) का छिड़काव करें।",
            "recommendation_2": "बैसिलस आधारित जैव-कवकनाशी या वेटेबल सल्फर का छिड़काव करें (32°C से अधिक तापमान पर सल्फर न डालें)।"
        },
        "mr": {
            "recovery_period": "पांढऱ्या भुरी रोगाचा प्रसार रोखण्यासाठी ७ ते १० दिवसांचे व्यवस्थापन आवश्यक",
            "recommendation_1": "पानांवर पांढरे ठिपके दिसताच पोटॅशियम बायकार्बोनेट किंवा बागायती तेलाची (१-२%) फवारणी करा.",
            "recommendation_2": "बॅसिलसयुक्त जैविक बुरशीनाशक किंवा विरघळणाऱ्या गंधकाची फवारणी करा."
        }
    },
    "Strawberry___Leaf_scorch": {
        "recovery_period": "10–14 days of protective fungicide cover and runner thinning",
        "recommendation_1": "Apply Captan 50 WP (2 g/L) or Copper hydroxide sprays starting at new spring leaf emergence.",
        "recommendation_2": "Remove and destroy severely purplish-spotted older leaves and avoid high-density runner overcrowding.",
        "hi": {
            "recovery_period": "कवकनाशी छिड़काव और पुरानी पत्तियों की सफाई के साथ 10-14 दिन का प्रबंधन",
            "recommendation_1": "वसंत में नई पत्तियां निकलने पर कैप्टन 50 WP (2 ग्रा/ली) या कॉपर हाइड्रॉक्साइड का छिड़काव करें।",
            "recommendation_2": "गहरे बैंगनी धब्बों वाली पुरानी पत्तियों को काटकर नष्ट करें और अत्यधिक घने पौधों को विरल करें।"
        },
        "mr": {
            "recovery_period": "बुरशीनाशक फवारणी आणि जुनी पाने छाटून १० ते १४ दिवसांचे व्यवस्थापन",
            "recommendation_1": "नवीन पालवी फुटताना कॅप्टन ५० डब्ल्यूपी (२ ग्रॅम/लि) किंवा कॉपर हायड्रॉक्साईडची फवारणी करा.",
            "recommendation_2": "जांभळट ठिपके पडलेली जुनी पाने काढून नष्ट करा आणि झाडांची गर्दी कमी करा."
        }
    },
    "Strawberry___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain clean straw mulch, drip watering, and balanced feeding",
        "recommendation_1": "Maintain clean wheat straw or plastic mulch under plants to keep berries off damp soil and prevent fruit rots.",
        "recommendation_2": "Apply balanced water-soluble fertilizer through drip lines and scout for two-spotted spider mites.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। पुआल की मल्चिंग और ड्रिप सिंचाई बनाए रखें",
            "recommendation_1": "फलों को गीली मिट्टी से बचाने और सड़न रोकने के लिए साफ पुआल या प्लास्टिक मल्च का उपयोग करें।",
            "recommendation_2": "ड्रिप से संतुलित उर्वरक दें और लाल मकड़ी (माइट) की नियमित जांच करें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — स्ट्रॉबेरीची पाने निरोगी आहेत. गवताचे आच्छादन व ठिबक सिंचन राखा",
            "recommendation_1": "फळे जमिनीत खराब होऊ नयेत म्हणून पेंढ्याचे किंवा मल्चिंग पेपरचे आच्छादन करा.",
            "recommendation_2": "ठिबकमधून संतुलित विद्राव्य खते द्या आणि लाल कोळी किडीवर लक्ष ठेवा."
        }
    },
    "Tomato___Bacterial_spot": {
        "recovery_period": "10–14 days of bactericide management with copper-mancozeb combination",
        "recommendation_1": "Spray Copper hydroxide combined with Mancozeb (2 g/L each) at weekly intervals during rainy periods.",
        "recommendation_2": "Apply biological control Bacillus subtilis (Serenade ASO) and ensure plants are staked with bottom leaves pruned.",
        "hi": {
            "recovery_period": "कॉपर-मैंकोजेब संयोजन के साथ 10-14 दिन का जीवाणुनाशक प्रबंधन आवश्यक है",
            "recommendation_1": "बारिश के मौसम में साप्ताहिक अंतराल पर कॉपर हाइड्रॉक्साइड और मैंकोजेब (2 ग्रा/ली प्रत्येक) का छिड़काव करें।",
            "recommendation_2": "बैसिलस सबटिलिस जैव-कीटनाशक का प्रयोग करें और निचली पत्तियों की छंटाई करके पौधों को सहारा दें।"
        },
        "mr": {
            "recovery_period": "कॉपर व मॅन्कोझेबच्या एकत्रित फवारणीसह १० ते १४ दिवसांचे व्यवस्थापन",
            "recommendation_1": "पावसाळी वातावरणात कॉपर हायड्रॉक्साईड आणि मॅन्कोझेबची (प्रत्येकी २ ग्रॅम/लि) आठवड्यातून एकदा फवारणी करा.",
            "recommendation_2": "बॅसिलस सबटिलिस जैविक कीटकनाशक वापरा आणि झाडांच्या खालच्या पानांची छाटणी करा."
        }
    },
    "Tomato___Early_blight": {
        "recovery_period": "7–14 days of fungicide application and lower canopy sanitation",
        "recommendation_1": "Apply Chlorothalonil 75 WP (2 g/L) or Mancozeb 75 WP (2.5 g/L) alternately with Difenoconazole 25 EC on a 7–10 day cycle.",
        "recommendation_2": "Prune the bottom 12 inches of infected leaves to eliminate rain splash from soil, and apply Bacillus subtilis bio-fungicide.",
        "hi": {
            "recovery_period": "कवकनाशी छिड़काव और निचली पत्तियों की सफाई के साथ 7-14 दिन का प्रबंधन",
            "recommendation_1": "क्लोरोथैलोनिल (2 ग्रा/ली) या मैंकोजेब को डिफेनोकोनाजोल के साथ 7-10 दिन के चक्र में बारी-बारी से छिड़कें।",
            "recommendation_2": "मिट्टी के छींटों से बचाने के लिए नीचे की 12 इंच की पत्तियों को काटें और बैसिलस जैव-कवकनाशी का प्रयोग करें।"
        },
        "mr": {
            "recovery_period": "बुरशीनाशक फवारणी व खालची पाने छाटून ७ ते १४ दिवसांचे व्यवस्थापन",
            "recommendation_1": "क्लोरोथॅलोनिल (२ ग्रॅम/लि) किंवा मॅन्कोझेब आणि डायफेनोकोनॅझोलची ७ ते १० दिवसांच्या अंतराने आलटून-पालटून फवारणी करा.",
            "recommendation_2": "जमिनीतील मातीचे उडणारे थेंब रोखण्यासाठी खालची पाने छाटा आणि बॅसिलस जैविक बुरशीनाशक वापरा."
        }
    },
    "Tomato___Late_blight": {
        "recovery_period": "5–10 days of urgent intervention under cool, humid weather conditions",
        "recommendation_1": "Apply targeted oomycete fungicides such as Mandipropamid, Dimethomorph, or Cymoxanil combined with protectant Mancozeb.",
        "recommendation_2": "Prune and dispose of severely blighted leaves immediately during dry midday hours, and spray copper sulfate pentahydrate.",
        "hi": {
            "recovery_period": "ठंडे और नम मौसम में 5-10 दिन का त्वरित प्रबंधन आवश्यक है",
            "recommendation_1": "साइमोक्सानिल या डाइमेथोमोर्फ को मैंकोजेब के साथ मिलाकर तुरंत छिड़कें।",
            "recommendation_2": "अत्यधिक झुलसी हुई पत्तियों को दोपहर के समय काटकर नष्ट करें और कॉपर सल्फेट का छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "थंड व दमट हवामानात ५ ते १० दिवसांचे तात्काळ व आक्रमक व्यवस्थापन आवश्यक",
            "recommendation_1": "सायमोक्सॅनिल किंवा डायमेथोमॉर्फ सोबत मॅन्कोझेब एकत्र करून त्वरित फवारणी करा.",
            "recommendation_2": "रोगग्रस्त पाने दुपारी तोडून नष्ट करा आणि कॉपर सल्फेट पेंटाहायड्रेटची फवारणी करा."
        }
    },
    "Tomato___Leaf_Mold": {
        "recovery_period": "7–12 days of humidity reduction and protective fungicide application",
        "recommendation_1": "Apply Copper hydroxide (2 g/L) or Chlorothalonil (2 g/L) covering both upper and lower leaf surfaces.",
        "recommendation_2": "Increase greenhouse/field ventilation and space plants adequately to keep relative humidity below 85%.",
        "hi": {
            "recovery_period": "नमी कम करने और कवकनाशी छिड़काव के साथ 7-12 दिन का प्रबंधन",
            "recommendation_1": "पत्तियों के दोनों तरफ कॉपर हाइड्रॉक्साइड (2 ग्रा/ली) या क्लोरोथैलोनिल (2 ग्रा/ली) का छिड़काव करें।",
            "recommendation_2": "हवा का संचार बढ़ाएं ताकि सापेक्ष आर्द्रता 85% से कम बनी रहे।"
        },
        "mr": {
            "recovery_period": "हवेतील आर्द्रता कमी करून व बुरशीनाशक फवारणीने ७ ते १२ दिवसांचे व्यवस्थापन",
            "recommendation_1": "पानांच्या वरच्या व खालच्या बाजूवर कॉपर हायड्रॉक्साईड किंवा क्लोरोथॅलोनिलची फवारणी करा.",
            "recommendation_2": "हवा खेळती राहील अशी व्यवस्था करा जेणेकरून आर्द्रता ८५ टक्क्यांपेक्षा कमी राहील."
        }
    },
    "Tomato___Septoria_leaf_spot": {
        "recovery_period": "10–14 days of protective fungicide cycles and drip irrigation management",
        "recommendation_1": "Apply Chlorothalonil 75 WP or Mancozeb 75 WP on a 7-day schedule at the earliest sign of circular dark-bordered spots.",
        "recommendation_2": "Apply organic mulch around plants and strictly avoid overhead sprinkler irrigation to stop spore splash.",
        "hi": {
            "recovery_period": "कवकनाशी चक्र और ड्रिप सिंचाई के साथ 10-14 दिन का प्रबंधन",
            "recommendation_1": "छोटे गोल धब्बे दिखते ही क्लोरोथैलोनिल या मैंकोजेब का 7 दिन के अंतराल पर छिड़काव करें।",
            "recommendation_2": "पौधों के चारों ओर जैविक मल्च लगाएं और ऊपर से पानी छिड़कने से पूरी तरह बचें।"
        },
        "mr": {
            "recovery_period": "बुरशीनाशक फवारणी व योग्य सिंचनासह १० ते १४ दिवसांचे व्यवस्थापन",
            "recommendation_1": "बारीक गोल ठिपके दिसताच क्लोरोथॅलोनिल किंवा मॅन्कोझेबची दर आठवड्याला फवारणी करा.",
            "recommendation_2": "झाडांभोवती सेंद्रिय आच्छादन करा आणि पाण्याचा मारा पानांवर करणे टाळा."
        }
    },
    "Tomato___Spider_mites_Two-spotted_spider_mite": {
        "recovery_period": "5–10 days of miticide or predatory mite intervention under hot, dry conditions",
        "recommendation_1": "Apply selective acaricides such as Spiromesifen 22.9 SC (1 mL/L) or Abamectin 1.9 EC (0.5 mL/L) ensuring thorough leaf underside coverage.",
        "recommendation_2": "Release biological predatory mites (Phytoseiulus persimilis) and spray cold water misting during hot dry periods.",
        "hi": {
            "recovery_period": "गर्म और शुष्क मौसम में 5-10 दिन का माइट-नाशी या परभक्षी कीट प्रबंधन",
            "recommendation_1": "स्पाइरोमेसिफेन (1 मि.ली/ली) या एबामेक्टिन (0.5 मि.ली/ली) का पत्तियों की निचली सतह पर छिड़काव करें।",
            "recommendation_2": "मित्र परभक्षी माइट्स (Phytoseiulus) छोड़ें और अत्यधिक गर्मी में ठंडे पानी का छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "उष्ण व कोरड्या हवामानात ५ ते १० दिवसांचे कोळीनाशक व्यवस्थापन",
            "recommendation_1": "स्पायरोमेसिफेन (१ मिली/लि) किंवा अबामेक्टिन (०.५ मिली/लि) पानांच्या खालच्या बाजूवर चांगल्या प्रकारे फवारा.",
            "recommendation_2": "फायटोसेलस परभक्षी कोळी बागेत सोडा आणि कोरड्या वातावरणात झाडांवर थंड पाणी फवारा."
        }
    },
    "Tomato___Target_Spot": {
        "recovery_period": "10–14 days of protective fungicide cover and air circulation enhancement",
        "recommendation_1": "Apply systemic fungicides such as Azoxystrobin + Difenoconazole or Boscalid upon appearance of target-ring lesions.",
        "recommendation_2": "Prune crowded suckers to promote air drying and apply preventative copper hydroxide sprays.",
        "hi": {
            "recovery_period": "सुरक्षात्मक कवकनाशी और हवा के संचार के साथ 10-14 दिन का प्रबंधन",
            "recommendation_1": "एजोक्सीस्ट्रोबिन + डिफेनोकोनाजोल या बोस्केलिड का छिड़काव रिंग जैसे धब्बे दिखने पर करें।",
            "recommendation_2": "अवांछित शाखाओं (सकर्स) को हटाएं और कॉपर हाइड्रॉक्साइड का सुरक्षात्मक छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "संरक्षक बुरशीनाशक व हवा खेळती ठेवून १० ते १४ दिवसांचे व्यवस्थापन",
            "recommendation_1": "वर्तुळाकार डाग दिसताच अझॉक्सीस्ट्रॉबिन + डायफेनोकोनॅझोलची फवारणी करा.",
            "recommendation_2": "झाडांची गर्दी कमी करण्यासाठी फुटवे काढा आणि कॉपर हायड्रॉक्साईडची फवारणी करा."
        }
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "recovery_period": "Viral infection: 7–14 days of intensive whitefly vector suppression; infected plants cannot be cured but secondary spread is checked",
        "recommendation_1": "Suppress whitefly vectors using systemic insecticides such as Imidacloprid 17.8 SL (0.3 mL/L) or Spiromesifen.",
        "recommendation_2": "Deploy yellow sticky cards (20–25 per acre), spray neem seed kernel extract (NSKE 5%), and rogue out severely stunted plants.",
        "hi": {
            "recovery_period": "वायरल संक्रमण: सफेद मक्खी नियंत्रण में 7-14 दिन लगते हैं; रोगग्रस्त पौधे ठीक नहीं होते पर प्रसार रुकता है",
            "recommendation_1": "इमिडाक्लोप्रिड 17.8 SL (0.3 मि.ली/ली) का छिड़काव करके सफेद मक्खी को तुरंत नियंत्रित करें।",
            "recommendation_2": "पीले चिपचिपे कार्ड (20-25 प्रति एकड़) लगाएं, नीम का अर्क (NSKE 5%) छिड़कें और अत्यधिक बीमार पौधों को उखाड़ें।"
        },
        "mr": {
            "recovery_period": "विषाणूजन्य रोग: पांढऱ्या माशीचे नियंत्रण ७ ते १४ दिवसांत करणे आवश्यक; पुढील प्रादुर्भाव रोखता येतो",
            "recommendation_1": "इमिडाक्लोप्रिड १७.८ एसएल (०.३ मिली/लि) ची फवारणी करून पांढऱ्या माशीचा बंदोबस्त करा.",
            "recommendation_2": "पिवळे चिकट सापळे लावा, निंबोळी अर्क (५%) फवारा आणि अतिबाधित झाडे उपटून नष्ट करा."
        }
    },
    "Tomato___Tomato_mosaic_virus": {
        "recovery_period": "Mechanical viral pathogen: Requires 7–10 days of strict sanitation and removal of symptomatic plants to protect healthy crop",
        "recommendation_1": "Rogue out and destroy mosaic-infected plants immediately; disinfest pruning shears with 10% trisodium phosphate (TSP) or skim milk.",
        "recommendation_2": "Wash hands with soap before touching plants, eliminate solanaceous weeds, and avoid tobacco handling around the field.",
        "hi": {
            "recovery_period": "यांत्रिक वायरस: स्वस्थ पौधों की सुरक्षा के लिए 7-10 दिन की सख्त स्वच्छता और रोगग्रस्त पौधों को हटाना आवश्यक है",
            "recommendation_1": "संक्रमित पौधों को तुरंत उखाड़कर नष्ट करें; औजारों को 10% ट्राइसोडियम फॉस्फेट या साबुन के घोल से धोएं।",
            "recommendation_2": "पौधों को छूने से पहले हाथ साबुन से धोएं और खेत के आसपास तंबाकू का सेवन पूरी तरह वर्जित रखें।"
        },
        "mr": {
            "recovery_period": "विषाणूजन्य रोग: निरोगी झाडांच्या संरक्षणासाठी ७ ते १० दिवसांचे स्वच्छता व्यवस्थापन व रोगट झाडे नष्ट करणे आवश्यक",
            "recommendation_1": "मोझॅक झालेली झाडे उपटून जाळून टाका; छाटणीची अवजारे ट्रायसोडियम फॉस्फेट किंवा साबणाच्या पाण्याने निर्जंतुक करा.",
            "recommendation_2": "झाडांना हात लावण्यापूर्वी हात साबणाने धुवा आणि शेतात तंबाखूचा वापर टाळा."
        }
    },
    "Tomato___healthy": {
        "recovery_period": "N/A — Foliage is healthy. Maintain drip irrigation, suckering, staking, and calcium nutrition",
        "recommendation_1": "Prune side suckers regularly and secure main stems to vertical stakes or trellises for optimal airflow.",
        "recommendation_2": "Apply balanced calcium nitrate and potassium foliar feed to support continuous flowering and firm fruit development.",
        "hi": {
            "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। ड्रिप सिंचाई, स्टेकिंग और कैल्शियम पोषण बनाए रखें",
            "recommendation_1": "अनावश्यक शाखाएं (सकर्स) हटाएं और पौधों को लकड़ी या धागों से सहारा दें ताकि हवा का संचार बना रहे।",
            "recommendation_2": "लगातार फूल आने और ठोस फल बनने के लिए कैल्शियम नाइट्रेट और पोटाश का संतुलित प्रयोग करें।"
        },
        "mr": {
            "recovery_period": "लागू नाही — टोमॅटोची पाने निरोगी आहेत. योग्य सिंचन, स्टेकिंग व अन्नद्रव्य व्यवस्थापन ठेवा",
            "recommendation_1": "अनावश्यक फुटवे तोडा आणि झाडांना बांबू किंवा तारेचा आधार देऊन वर बांधा.",
            "recommendation_2": "भरपूर फुलोरा व टणक फळांसाठी कॅल्शियम नायट्रेट आणि पोटॅशची फवारणी करा."
        }
    },
    "Soybean___Bacterial_blight": {
        "recovery_period": "10–14 days of management under dry weather conditions; symptoms stabilize as dry warm weather returns",
        "recommendation_1": "Apply fixed copper bactericides (copper oxychloride at 2.5 g/L or copper hydroxide) during early vegetative stages if pressure is high.",
        "recommendation_2": "Avoid equipment movement in wet fields to eliminate physical spore spread, and use Bacillus amyloliquefaciens biological spray.",
        "hi": {
            "recovery_period": "सूखे मौसम में 10-14 दिन का प्रबंधन; गर्म और शुष्क मौसम लौटने पर लक्षण स्थिर हो जाते हैं",
            "recommendation_1": "रोग का प्रकोप अधिक होने पर कॉपर ऑक्सीक्लोराइड (2.5 ग्रा/ली) का प्रारंभिक वानस्पतिक अवस्था में छिड़काव करें।",
            "recommendation_2": "गीले खेत में कृषि यंत्र न चलाएं जिससे जीवाणु न फैलें, और बैसिलस जैविक स्प्रे का प्रयोग करें।"
        },
        "mr": {
            "recovery_period": "कोरड्या हवामानात १० ते १४ दिवसांचे व्यवस्थापन; हवामान कोरडे झाल्यास रोगाचा फैलाव मंदावतो",
            "recommendation_1": "सुरुवातीच्या टप्प्यात कॉपर ऑक्सिक्लोराईड (२.५ ग्रॅम/लि) किंवा कॉपर हायड्रॉक्साईडची फवारणी करा.",
            "recommendation_2": "ओल्या शेतातून ट्रॅक्टर किंवा अवजारे फिरवणे टाळा आणि बॅसिलस जैविक जिवाणूनाशक वापरा."
        }
    },
    "Soybean___Frogeye_leaf_spot": {
        "recovery_period": "12–18 days of management from R1 to R3 reproductive stages",
        "recommendation_1": "Apply a premix fungicide combining a triazole (e.g., Prothioconazole or Tebuconazole) and a SDHI to prevent strobilurin resistance.",
        "recommendation_2": "Practice deep tillage of crop debris post-harvest and apply potassium foliar nutrition to improve leaf tissue resistance.",
        "hi": {
            "recovery_period": "फूल और फली बनने (R1 से R3) की अवस्था में 12-18 दिन का प्रबंधन आवश्यक है",
            "recommendation_1": "प्रोपिकोनाजोल या टेबुकोनाजोल जैसे ट्रायजोल युक्त कवकनाशी का छिड़काव फफूंद प्रतिरोध से बचने के लिए करें।",
            "recommendation_2": "फसल कटाई के बाद गहरी जुताई करें और पत्तियों की मजबूती के लिए पोटाश का छिड़काव करें।"
        },
        "mr": {
            "recovery_period": "फुलोरा ते शेंगा भरण्याच्या अवस्थेत १२ ते १८ दिवसांचे बुरशीनाशक व्यवस्थापन आवश्यक",
            "recommendation_1": "टेब्युकोनाझोल किंवा प्रोपिकोनाझोल या ट्रायझोलयुक्त आंतरप्रवाही बुरशीनाशकाची योग्य प्रमाणात फवारणी करा.",
            "recommendation_2": "काढणीनंतर खोल नांगरट करा आणि पानांची प्रतिकारशक्ती वाढवण्यासाठी पोटॅशियमची फवारणी करा."
        }
    },
    "Soybean___Soybean_rust": {
        "recovery_period": "7–14 days of intensive protective spraying; rust requires rapid management before 10% canopy severity",
        "recommendation_1": "Apply dual-action systemic fungicides (Azoxystrobin + Cyproconazole or Pyraclostrobin + Epoxiconazole) at first local advisory.",
        "recommendation_2": "Apply preventative protective chlorothalonil or mancozeb sprays at flowering (R1/R2) stage and scout lower canopy regularly.",
        "hi": {
            "recovery_period": "7-14 दिन का सघन सुरक्षात्मक छिड़काव; रतुआ को 10% संक्रमण से पहले ही नियंत्रित करना आवश्यक है",
            "recommendation_1": "स्थानीय चेतावनी मिलते ही एजोक्सीस्ट्रोबिन + साइप्रिकोनाजोल जैसे दोहरे प्रभाव वाले कवकनाशी का छिड़काव करें।",
            "recommendation_2": "फूल आने (R1/R2) के समय क्लोरोथैलोनिल या मैंकोजेब का छिड़काव करें और निचली पत्तियों की जांच करते रहें।"
        },
        "mr": {
            "recovery_period": "७ ते १४ दिवसांचे काटेकोर बुरशीनाशक व्यवस्थापन; तांबेरा १०% पेक्षा जास्त पसरण्यापूर्वी रोखणे गरजेचे",
            "recommendation_1": "प्रादुर्भावाची पहिली सूचना मिळताच अझॉक्सीस्ट्रॉबिन + सायप्रिकोनाझोल बुरशीनाशकाची फवारणी करा.",
            "recommendation_2": "फुलोरा अवस्थेत क्लोरोथॅलोनिल किंवा मॅन्कोझेबची प्रतिबंधात्मक फवारणी करा व खालच्या पानांवर लक्ष ठेवा."
        }
    }
}

# 12 New profiles for the 3 new crops
NEW_PROFILES = {
    # ----------------------------------------------------
    # 1. GREEN GRAM (Vigna radiata)
    # ----------------------------------------------------
    "Green_Gram___Cercospora_leaf_spot": {
        "class_name": "Green_Gram___Cercospora_leaf_spot",
        "crop_name": "Green Gram (Vigna radiata)",
        "disease_name": "Cercospora Leaf Spot (Cercospora canescens)",
        "description": "Cercospora leaf spot causes circular to irregular spots with grey centers and reddish-brown margins on green gram foliage, resulting in premature leaf fall and reduced pod filling.",
        "symptoms": [
            "Small circular spots with greyish-white centers and dark brown to reddish borders on leaves.",
            "Lesions coalesce causing large necrotic blighted areas.",
            "Severely affected leaves turn yellow and shed prematurely during pod development."
        ],
        "prevention": [
            "Use certified disease-free seeds and treat seeds with Carbendazim (2 g/kg seed).",
            "Practice crop rotation with non-leguminous crops (maize, sorghum) for at least 1 season.",
            "Avoid excessive plant density to ensure good canopy aeration and light penetration."
        ],
        "treatment_or_cure": [
            "Spray systemic fungicides at initial leaf spotting to prevent canopy-wide defoliation.",
            "Apply bio-control agents such as Pseudomonas fluorescens to reduce sporulation."
        ],
        "recovery_period": "10–15 days of foliar management and canopy aeration",
        "recommendation_1": "Spray Carbendazim 50 WP (0.1% / 1 g/L) or Mancozeb 75 WP (0.2% / 2 g/L) at the onset of initial leaf spot symptoms.",
        "recommendation_2": "Apply neem oil formulation (3%) or Pseudomonas fluorescens (0.2%) foliar spray as an eco-friendly biological alternative.",
        "chemical_information": "Carbendazim 50 WP, Mancozeb 75 WP, or Thiophanate-methyl 70 WP provide effective control when applied at first symptom onset. Observe 14-day pre-harvest intervals.",
        "disclaimer": "Always observe local agricultural extension guidelines and chemical label dosage recommendations.",
        "translations": {
            "en": {
                "crop_name": "Green Gram (Vigna radiata)",
                "disease_name": "Cercospora Leaf Spot (Cercospora canescens)",
                "description": "Cercospora leaf spot causes circular to irregular spots with grey centers and reddish-brown margins on green gram foliage, resulting in premature leaf fall.",
                "symptoms": [
                    "Small circular spots with greyish-white centers and dark brown to reddish borders on leaves.",
                    "Lesions coalesce causing large necrotic blighted areas.",
                    "Severely affected leaves turn yellow and shed prematurely."
                ],
                "prevention": [
                    "Use certified disease-free seeds and treat seeds with Carbendazim (2 g/kg seed).",
                    "Practice crop rotation with non-leguminous crops.",
                    "Avoid excessive plant density to ensure good canopy aeration."
                ],
                "treatment_or_cure": [
                    "Spray systemic fungicides at initial leaf spotting.",
                    "Apply bio-control agents such as Pseudomonas fluorescens."
                ],
                "recovery_period": "10–15 days of foliar management and canopy aeration",
                "recommendation_1": "Spray Carbendazim 50 WP (1 g/L) or Mancozeb 75 WP (2 g/L) at the onset of initial leaf spot symptoms.",
                "recommendation_2": "Apply neem oil formulation (3%) or Pseudomonas fluorescens (0.2%) foliar spray as a biological alternative.",
                "chemical_information": "Carbendazim 50 WP or Mancozeb 75 WP provide effective control. Follow manufacturer label instructions.",
                "disclaimer": "Always observe local agricultural extension guidelines and pesticide safety labels."
            },
            "hi": {
                "crop_name": "मूंग (Green Gram)",
                "disease_name": "सर्कोस्पोरा पत्ती धब्बा रोग (Cercospora Leaf Spot)",
                "description": "सर्कोस्पोरा पत्ती धब्बा मूंग की पत्तियों पर भूरे और लाल किनारों वाले गोल धब्बे बनाता है, जिससे पत्तियां समय से पहले गिर जाती हैं।",
                "symptoms": [
                    "पत्तियों पर भूरे-सफेद केंद्र और लाल-भूरे किनारों वाले छोटे गोल धब्बे।",
                    "धब्बे आपस में मिलकर बड़े झुलसे हुए क्षेत्र बना देते हैं।",
                    "संक्रमित पत्तियां पीली पड़कर फलियां बनने से पहले ही झड़ जाती हैं।"
                ],
                "prevention": [
                    "प्रमाणित रोगमुक्त बीजों का उपयोग करें और कार्बेन्डाजिम (2 ग्रा/किग्रा) से बीज उपचार करें।",
                    "मक्का या ज्वार जैसी गैर-दलहनी फसलों के साथ फसल चक्र अपनाएं।",
                    "हवा के संचार के लिए पौधों के बीच उचित दूरी बनाए रखें।"
                ],
                "treatment_or_cure": [
                    "शुरुआती लक्षण दिखते ही कवकनाशी का छिड़काव करें।",
                    "स्यूडोमोनास फ्लोरोसेंस जैसे जैविक नियंत्रण एजेंट का उपयोग करें।"
                ],
                "recovery_period": "पर्ण प्रबंधन और छतरी में हवा के संचार के साथ 10-15 दिन",
                "recommendation_1": "शुरुआती लक्षण दिखने पर कार्बेन्डाजिम 50 WP (1 ग्रा/ली) या मैंकोजेब 75 WP (2 ग्रा/ली) का छिड़काव करें।",
                "recommendation_2": "नीम का तेल (3%) या स्यूडोमोनास फ्लोरोसेंस (0.2%) का छिड़काव जैविक विकल्प के रूप में करें।",
                "chemical_information": "कार्बेन्डाजिम 50 WP या मैंकोजेब 75 WP प्रभावी नियंत्रण प्रदान करते हैं।",
                "disclaimer": "हमेशा स्थानीय कृषि प्रसार केंद्र की सिफारिशों और लेबल निर्देशों का पालन करें।"
            },
            "mr": {
                "crop_name": "मूग (Green Gram)",
                "disease_name": "सार्कोस्पोरा पानांवरील ठिपके (Cercospora Leaf Spot)",
                "description": "सार्कोस्पोरा बुरशीमुळे मुगाच्या पानांवर करडे व तांबूस कडांचे ठिपके पडतात आणि पाने अकाली गळून उत्पादनात घट होते.",
                "symptoms": [
                    "पानांवर करड्या रंगाचे केंद्र आणि लालसर-तपकिरी कडा असलेले लहान गोल ठिपके.",
                    "ठिपके एकत्र येऊन पानांचा मोठा भाग करपतो.",
                    "शेंगा भरण्याच्या काळात पाने पिवळी पडून गळतात."
                ],
                "prevention": [
                    "प्रमाणित बियाणे वापरा आणि कार्बेन्डाझिमने (२ ग्रॅम/किलो) बीजप्रक्रिया करा.",
                    "ज्वारी किंवा मका यांसारख्या पिकांसोबत पीक फेरपालट करा.",
                    "बागेत हवा खेळती राहण्यासाठी योग्य अंतर ठेवा."
                ],
                "treatment_or_cure": [
                    "लक्षणे दिसताच आंतरप्रवाही बुरशीनाशकांची फवारणी करा.",
                    "स्यूडोमोनास फ्लोरोसन्स या जैविक घटकाचा वापर करा."
                ],
                "recovery_period": "योग्य बुरशीनाशक व हवा खेळती ठेवून १० ते १५ दिवसांचे व्यवस्थापन",
                "recommendation_1": "लक्षणे दिसू लागताच कार्बेन्डाझिम ५० डब्ल्यूपी (१ ग्रॅम/लि) किंवा मॅन्कोझेब ७५ डब्ल्यूपी (२ ग्रॅम/लि) फवारा.",
                "recommendation_2": "जैविक पर्याय म्हणून निंबोळी तेल (३%) किंवा स्यूडोमोनास फ्लोरोसन्स (०.२%) ची फवारणी करा.",
                "chemical_information": "कार्बेन्डाझिम ५० डब्ल्यूपी किंवा मॅन्कोझेब ७५ डब्ल्यूपी बुरशीनाशकांचा वेळेवर वापर करा.",
                "disclaimer": "नेहमी स्थानिक कृषी अधिकाऱ्यांचा सल्ला व औषध लेबलवरील सूचनांचे पालन करा."
            }
        }
    },
    "Green_Gram___Yellow_mosaic": {
        "class_name": "Green_Gram___Yellow_mosaic",
        "crop_name": "Green Gram (Vigna radiata)",
        "disease_name": "Yellow Mosaic Virus (MYMV)",
        "description": "Mungbean Yellow Mosaic Virus (MYMV) is transmitted by whiteflies (Bemisia tabaci), creating distinct bright yellow patches on leaves that reduce photosynthesis and stunt plant growth.",
        "symptoms": [
            "Bright yellow patches interspersed with green areas on young leaves (mosaic pattern).",
            "Complete yellowing and puckering of leaves as disease progresses.",
            "Stunted plant growth with few, poorly filled, deformed pods."
        ],
        "prevention": [
            "Sow yellow mosaic tolerant/resistant cultivars (e.g., IPM-02-3, Pant Mung 5, SML 668).",
            "Treat seeds with Imidacloprid 70 WS (5 g/kg seed) to protect seedlings for initial 25–30 days.",
            "Rogue out and destroy infected plants early to limit whitefly transmission sources."
        ],
        "treatment_or_cure": [
            "Control whitefly vector populations immediately upon initial observation.",
            "Install yellow sticky traps to continuously monitor and trap adult whiteflies."
        ],
        "recovery_period": "Vector management requires 7–12 days to halt whitefly proliferation and viral transmission",
        "recommendation_1": "Control the whitefly vector by spraying Imidacloprid 17.8 SL (0.3 mL/L) or Thiamethoxam 25 WG (0.25 g/L).",
        "recommendation_2": "Install yellow sticky traps (15–20 per acre) and spray botanical neem seed kernel extract (NSKE 5%) as a vector deterrent.",
        "chemical_information": "Systemic insecticides targeting whitefly vectors include Imidacloprid 17.8 SL, Thiamethoxam 25 WG, or Acetamiprid 20 SP. Rotate modes of action to prevent resistance.",
        "disclaimer": "Viral diseases cannot be cured once inside plant cells; management focuses entirely on vector control and tolerant varieties.",
        "translations": {
            "en": {
                "crop_name": "Green Gram (Vigna radiata)",
                "disease_name": "Yellow Mosaic Virus (MYMV)",
                "description": "Mungbean Yellow Mosaic Virus is transmitted by whiteflies, creating distinct yellow patches on foliage.",
                "symptoms": [
                    "Bright yellow patches interspersed with green areas on young leaves.",
                    "Complete yellowing and leaf puckering as disease progresses.",
                    "Stunted plant growth with few, poorly filled pods."
                ],
                "prevention": [
                    "Sow yellow mosaic tolerant cultivars.",
                    "Treat seeds with Imidacloprid to protect young seedlings.",
                    "Rogue out and destroy infected plants early."
                ],
                "treatment_or_cure": [
                    "Control whitefly vector populations immediately.",
                    "Install yellow sticky traps to trap adult whiteflies."
                ],
                "recovery_period": "Vector management requires 7–12 days to halt whitefly proliferation",
                "recommendation_1": "Control the whitefly vector by spraying Imidacloprid 17.8 SL (0.3 mL/L) or Thiamethoxam 25 WG (0.25 g/L).",
                "recommendation_2": "Install yellow sticky traps (15–20 per acre) and spray neem seed kernel extract (NSKE 5%).",
                "chemical_information": "Imidacloprid 17.8 SL or Thiamethoxam 25 WG manage vector whiteflies. Follow safety label instructions.",
                "disclaimer": "Viral diseases cannot be cured once established; management strictly targets whitefly vectors."
            },
            "hi": {
                "crop_name": "मूंग (Green Gram)",
                "disease_name": "पीला मोज़ेक वायरस (Yellow Mosaic Virus)",
                "description": "मूंग का पीला मोज़ेक वायरस सफेद मक्खी द्वारा फैलता है, जिससे पत्तियों पर चमकीले पीले धब्बे बन जाते हैं और पौधे बौने रह जाते हैं।",
                "symptoms": [
                    "छोटी पत्तियों पर हरे और चमकीले पीले रंग के मोज़ेक धब्बे।",
                    "संक्रमण बढ़ने पर पूरी पत्तियां पीली पड़कर मुड़ जाती हैं।",
                    "पौधों का विकास रुक जाता है और फलियां बहुत कम व छोटी बनती हैं।"
                ],
                "prevention": [
                    "रोग प्रतिरोधी किस्में लगाएं।",
                    "इमिडाक्लोप्रिड से बीजोपचार करें ताकि शुरुआती 30 दिन तक सुरक्षा मिले।",
                    "रोगग्रस्त पौधों को शुरुआत में ही उखाड़कर नष्ट करें।"
                ],
                "treatment_or_cure": [
                    "सफेद मक्खी को तुरंत नियंत्रित करें।",
                    "खेत में पीले चिपचिपे जाल लगाएं।"
                ],
                "recovery_period": "सफेद मक्खी के नियंत्रण और प्रसार रोकने के लिए 7-12 दिन आवश्यक हैं",
                "recommendation_1": "सफेद मक्खी के नियंत्रण हेतु इमिडाक्लोप्रिड 17.8 SL (0.3 मि.ली/ली) या थायामेथोक्सम 25 WG (0.25 ग्रा/ली) का छिड़काव करें।",
                "recommendation_2": "खेत में पीले चिपचिपे ट्रैप (15-20 प्रति एकड़) लगाएं और 5% निंबोली अर्क (NSKE) का छिड़काव करें।",
                "chemical_information": "इमिडाक्लोप्रिड या थायामेथोक्सम सफेद मक्खी का प्रभावी नियंत्रण करते हैं।",
                "disclaimer": "वायरल रोगों को दवा से ठीक नहीं किया जा सकता, इनका नियंत्रण केवल वाहक कीट रोककर ही संभव है।"
            },
            "mr": {
                "crop_name": "मूग (Green Gram)",
                "disease_name": "पिवळा मोझॅक विषाणू (Yellow Mosaic Virus)",
                "description": "मुगावरील पिवळा मोझॅक हा पांढऱ्या माशीद्वारे पसरणारा विषाणूजन्य रोग असून पानांवर पिवळे पट्टे पडून झाडांची वाढ खुंटते.",
                "symptoms": [
                    "पानांवर हिरव्या रंगात चमकदार पिवळे चट्टे दिसणे (मोझॅक लक्षण).",
                    "रोग वाढल्यावर संपूर्ण पान पिवळे पडून गोळा होते.",
                    "झाडांची वाढ खुंटते व शेंगा बारीक आणि कमी भरतात."
                ],
                "prevention": [
                    "रोगप्रतिकारक वाणांची लागवड करा.",
                    "पेरणीपूर्वी इमिडाक्लोप्रिडने बीजप्रक्रिया करा.",
                    "सुरुवातीलाच रोगट झाडे उपटून नष्ट करा."
                ],
                "treatment_or_cure": [
                    "पांढऱ्या माशीचा प्रादुर्भाव रोखण्यासाठी वेळेवर उपाय करा.",
                    "पांढऱ्या माशीच्या सर्वेक्षणासाठी पिवळे चिकट सापळे लावा."
                ],
                "recovery_period": "पांढऱ्या माशीच्या नियंत्रणासाठी व प्रसार रोखण्यासाठी ७ ते १२ दिवसांचे व्यवस्थापन",
                "recommendation_1": "पांढऱ्या माशीच्या नियंत्रणासाठी इमिडाक्लोप्रिड १७.८ एसएल (०.३ मिली/लि) किंवा थायामेथोक्साम २५ डब्ल्यूजी (०.२५ ग्रॅम/लि) फवारा.",
                "recommendation_2": "एकरी १५-२० पिवळे चिकट सापळे लावा आणि निंबोळी अर्क (५%) ची प्रतिबंधात्मक फवारणी करा.",
                "chemical_information": "इमिडाक्लोप्रिड किंवा थायामेथोक्साम पांढऱ्या माशीचे उत्तम नियंत्रण करतात.",
                "disclaimer": "विषाणूजन्य रोग एकदा झाडात शिरल्यावर बरा होत नाही; पांढऱ्या माशीचे नियंत्रण हाच एकमेव मार्ग आहे."
            }
        }
    },
    "Green_Gram___Powdery_mildew": {
        "class_name": "Green_Gram___Powdery_mildew",
        "crop_name": "Green Gram (Vigna radiata)",
        "disease_name": "Powdery Mildew (Erysiphe polygoni)",
        "description": "Powdery mildew appears as white talcum powder-like growth on leaves, stems, and pods of green gram, leading to reduced photosynthetic area and shriveled seeds.",
        "symptoms": [
            "White floury or talcum powder-like circular patches on upper leaf surfaces.",
            "Powdery growth covers entire leaves, petiole, and pods under dry, warm conditions.",
            "Heavily infected leaves turn chlorotic, dry up, and drop prematurely."
        ],
        "prevention": [
            "Sow early in the season to escape peak powdery mildew incidence.",
            "Avoid excessive nitrogen fertilization which causes lush susceptible foliage.",
            "Ensure proper crop spacing to reduce canopy humidity."
        ],
        "treatment_or_cure": [
            "Apply wettable sulfur or systemic triazole fungicides at first sign of white spots.",
            "Ensure thorough coverage of both upper and lower canopy foliage."
        ],
        "recovery_period": "8–12 days of sulfur or systemic fungicide application",
        "recommendation_1": "Apply wettable sulfur 80 WP (0.25% / 2.5 g/L) or Dinocap (0.1%) at early sign of white powdery patches.",
        "recommendation_2": "Spray Hexaconazole 5 EC (0.1% / 1 mL/L) or bio-control Ampelomyces quisqualis to suppress fungal mycelium.",
        "chemical_information": "Wettable sulfur 80 WP, Hexaconazole 5 EC, or Propiconazole 25 EC control powdery mildew effectively. Avoid sulfur above 32°C to prevent phytotoxicity.",
        "disclaimer": "Observe pre-harvest intervals and avoid spraying during high afternoon temperatures.",
        "translations": {
            "en": {
                "crop_name": "Green Gram (Vigna radiata)",
                "disease_name": "Powdery Mildew (Erysiphe polygoni)",
                "description": "Powdery mildew appears as white talc-like patches on foliage and pods of green gram.",
                "symptoms": [
                    "White floury patches on upper leaf surfaces.",
                    "Powdery growth spreads over leaves, stems, and pods.",
                    "Infected leaves dry up and shed prematurely."
                ],
                "prevention": [
                    "Sow early in the season to escape peak incidence.",
                    "Avoid excessive nitrogen fertilization.",
                    "Ensure proper spacing to reduce canopy humidity."
                ],
                "treatment_or_cure": [
                    "Apply wettable sulfur at first sign of white patches.",
                    "Ensure thorough spray coverage of all plant surfaces."
                ],
                "recovery_period": "8–12 days of sulfur or systemic fungicide application",
                "recommendation_1": "Apply wettable sulfur 80 WP (2.5 g/L) or Dinocap (0.1%) at early sign of powdery patches.",
                "recommendation_2": "Spray Hexaconazole 5 EC (1 mL/L) or bio-fungicide Ampelomyces quisqualis.",
                "chemical_information": "Wettable sulfur or Hexaconazole 5 EC control powdery mildew. Avoid sulfur during extreme heat.",
                "disclaimer": "Follow product safety directions and pre-harvest intervals."
            },
            "hi": {
                "crop_name": "मूंग (Green Gram)",
                "disease_name": "चूर्णिल आसिता / पाउडरी मिल्ड्यू (Powdery Mildew)",
                "description": "मूंग की पत्तियों पर सफेद पाउडर जैसी फफूंद जम जाती है जिससे प्रकाश संश्लेषण रुक जाता है और दाने सिकुड़ जाते हैं।",
                "symptoms": [
                    "पत्तियों की ऊपरी सतह पर सफेद आटे जैसी फफूंद के धब्बे।",
                    "सूखे और गर्म मौसम में फफूंद पत्तियों, तने और फलियों पर फैल जाती है।",
                    "प्रभावित पत्तियां सूखकर समय से पहले गिर जाती हैं।"
                ],
                "prevention": [
                    "मौसम में जल्दी बुआई करें ताकि रोग से बचा जा सके।",
                    "अत्यधिक नाइट्रोजन खाद डालने से बचें।",
                    "पौधों के बीच उचित दूरी रखें।"
                ],
                "treatment_or_cure": [
                    "सफेद धब्बे दिखते ही गंधक (सल्फर) या कवकनाशी का छिड़काव करें।",
                    "पत्तियों के दोनों तरफ अच्छी तरह छिड़काव सुनिश्चित करें।"
                ],
                "recovery_period": "सल्फर या कवकनाशी के साथ 8-12 दिन में फफूंद सूख जाती है",
                "recommendation_1": "वेटेबल सल्फर 80 WP (2.5 ग्रा/ली) या डाइनोकैप (0.1%) का शुरुआती सफेद धब्बे दिखने पर छिड़काव करें।",
                "recommendation_2": "हेक्साकोनाजोल 5 EC (1 मि.ली/ली) या जैविक कवकनाशी का छिड़काव करें।",
                "chemical_information": "वेटेबल सल्फर 80 WP या हेक्साकोनाजोल 5 EC पाउडरी मिल्ड्यू का प्रभावी नियंत्रण करते हैं। 32°C से अधिक तापमान में सल्फर न छिड़कें।",
                "disclaimer": "हमेशा तुड़ाई पूर्व अंतराल और लेबल निर्देशों का पालन करें।"
            },
            "mr": {
                "crop_name": "मूग (Green Gram)",
                "disease_name": "भुरी रोग (Powdery Mildew)",
                "description": "पानांवर आणि शेंगांवर पांढऱ्या पिठासारखी बुरशी वाढते, ज्यामुळे दाणे बारीक राहतात व उत्पादनात घट येते.",
                "symptoms": [
                    "पानांच्या वरच्या बाजूवर पांढऱ्या भुकटीसारखे चट्टे दिसणे.",
                    "कोरड्या हवामानात बुरशी संपूर्ण झाडावर पसरते.",
                    "बाधित पाने वाळून मुदतीपूर्वीच गळतात."
                ],
                "prevention": [
                    "हंगाम सुरू होताच वेळेवर पेरणी करा.",
                    "अतिरिक्त नत्र खतांचा वापर टाळा.",
                    "योग्य अंतर ठेवून हवा खेळती राहील याची काळजी घ्या."
                ],
                "treatment_or_cure": [
                    "पांढरे ठिपके दिसताच गंधकयुक्त बुरशीनाशकाची फवारणी करा.",
                    "संपूर्ण झाड व्यवस्थित भिजेल अशी फवारणी करा."
                ],
                "recovery_period": "गंधक किंवा बुरशीनाशक फवारणीने ८ ते १२ दिवसांत भुरीचे नियंत्रण होते",
                "recommendation_1": "पाण्यात विरघळणारे गंधक ८० डब्ल्यूपी (२.५ ग्रॅम/लि) ची सुरुवातीलाच फवारणी करा.",
                "recommendation_2": "हेक्झाकोनाझोल ५ ईसी (१ मिली/लि) आंतरप्रवाही बुरशीनाशकाची फवारणी करा.",
                "chemical_information": "विरघळणारे गंधक किंवा हेक्झाकोनाझोल ५ ईसी भुरी रोगावर अत्यंत प्रभावी ठरतात.",
                "disclaimer": "औषधाचे प्रमाण योग्य ठेवा आणि कडक उन्हात गंधकाची फवारणी टाळा."
            }
        }
    },
    "Green_Gram___healthy": {
        "class_name": "Green_Gram___healthy",
        "crop_name": "Green Gram (Vigna radiata)",
        "disease_name": "Healthy Foliage",
        "description": "Green gram foliage displays healthy trifoliate leaves with vibrant green coloration and no visible foliar lesions, mosaic mottling, or powdery fungal growth.",
        "symptoms": [
            "Uniform vibrant green trifoliate leaves with intact margins.",
            "Absence of yellow mosaic patches, necrotic spots, or white fungal mycelium.",
            "Vigorous branching with normal flowering and pod formation."
        ],
        "prevention": [
            "Maintain regular weekly field inspection for early vector activity.",
            "Apply balanced phosphorus fertilizer (SSP) and Rhizobium seed inoculation.",
            "Ensure proper drainage to prevent waterlogging during monsoon showers."
        ],
        "treatment_or_cure": [
            "Maintain routine agronomic care and timely irrigation during pod filling.",
            "Spray 2% DAP or pulse wonder nutrient mix at flowering to enhance pod setting."
        ],
        "recovery_period": "N/A — Foliage is healthy. Maintain regular scouting",
        "recommendation_1": "Monitor weekly for early vector presence (aphids/whiteflies) and maintain adequate soil moisture during flowering.",
        "recommendation_2": "Incorporate Rhizobium bio-fertilizer and maintain balanced phosphorus nutrition to boost natural plant immunity.",
        "chemical_information": "No chemical fungicides or bactericides required for healthy green gram plants.",
        "disclaimer": "Routine preventive scouting is recommended throughout the crop cycle.",
        "translations": {
            "en": {
                "crop_name": "Green Gram (Vigna radiata)",
                "disease_name": "Healthy Foliage",
                "description": "Green gram foliage displays healthy vibrant green coloration with no foliar lesions.",
                "symptoms": [
                    "Uniform vibrant green trifoliate leaves.",
                    "No yellow mosaic or necrotic spots.",
                    "Healthy vigorous flowering and pod development."
                ],
                "prevention": [
                    "Maintain weekly field scouting.",
                    "Apply Rhizobium seed inoculation.",
                    "Ensure adequate field drainage."
                ],
                "treatment_or_cure": [
                    "Maintain routine agronomic management.",
                    "Provide irrigation during flowering and pod development."
                ],
                "recovery_period": "N/A — Foliage is healthy. Maintain regular scouting",
                "recommendation_1": "Monitor weekly for early vector presence and maintain soil moisture during flowering.",
                "recommendation_2": "Incorporate Rhizobium bio-fertilizer and balanced phosphorus nutrition.",
                "chemical_information": "No chemicals needed for healthy foliage.",
                "disclaimer": "Routine preventive scouting is recommended."
            },
            "hi": {
                "crop_name": "मूंग (Green Gram)",
                "disease_name": "स्वस्थ पत्तियां (Healthy Foliage)",
                "description": "मूंग की पत्तियां पूरी तरह स्वस्थ हैं, जिनमें कोई धब्बा, पीलापन या फफूंद नहीं है।",
                "symptoms": [
                    "एकसमान हरी और चमकदार पत्तियां।",
                    "कोई मोज़ेक पीलापन या धब्बे उपस्थित नहीं हैं।",
                    "फूल और फलियों का सामान्य स्वस्थ विकास।"
                ],
                "prevention": [
                    "कीटों की जांच के लिए साप्ताहिक निरीक्षण करें।",
                    "राइजोबियम और फास्फोरस का उचित प्रयोग करें।",
                    "खेत में पानी भरने से रोकें।"
                ],
                "treatment_or_cure": [
                    "नियमित देखभाल और फूल आने पर हल्की सिंचाई जारी रखें।",
                    "फलियां बनते समय पोषक तत्वों का छिड़काव करें।"
                ],
                "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। नियमित निरीक्षण जारी रखें",
                "recommendation_1": "सफेद मक्खी की नियमित जांच करें और फूल आते समय खेत में उचित नमी बनाए रखें।",
                "recommendation_2": "राइजोबियम जैव-उर्वरक और संतुलित फास्फोरस देकर पौधों की प्राकृतिक प्रतिरोधक क्षमता बढ़ाएं।",
                "chemical_information": "स्वस्थ फसल पर किसी कवकनाशी या कीटनाशक की आवश्यकता नहीं है।",
                "disclaimer": "नियमित निगरानी बनाए रखें।"
            },
            "mr": {
                "crop_name": "मूग (Green Gram)",
                "disease_name": "निरोगी पाने (Healthy Foliage)",
                "description": "मुगाची पाने पूर्णपणे निरोगी असून पानांवर कोणतेही डाग, पिवळेपणा किंवा बुरशीची लक्षणे नाहीत.",
                "symptoms": [
                    "टवटवीत हिरवीगार पाने.",
                    "कोणतेही चट्टे किंवा करपा नसणे.",
                    "फुलोरा व शेंगांची जोमदार वाढ."
                ],
                "prevention": [
                    "आठवड्यातून एकदा शेताची पाहणी करा.",
                    "पेरणीवेळी रायझोबियमचा वापर करा.",
                    "शेतात पाणी साचणार नाही याची काळजी घ्या."
                ],
                "treatment_or_cure": [
                    "योग्य पाणी व्यवस्थापन चालू ठेवा.",
                    "फुलोरा अवस्थेत २% डीएपी किंवा सूक्ष्म अन्नद्रव्यांची फवारणी करा."
                ],
                "recovery_period": "लागू नाही — पाने निरोगी आहेत. नियमित पाहणी ठेवा",
                "recommendation_1": "पांढऱ्या माशीवर लक्ष ठेवा आणि फुलोऱ्याच्या काळात जमिनीत योग्य ओलावा राखा.",
                "recommendation_2": "रायझोबियम आणि स्फुरद खतांचा योग्य वापर करून झाडांची प्रतिकारशक्ती टिकवून ठेवा.",
                "chemical_information": "निरोगी पिकावर रासायनिक बुरशीनाशकांची गरज नसते.",
                "disclaimer": "पिकाचे नियमित निरीक्षण चालू ठेवा."
            }
        }
    },

    # ----------------------------------------------------
    # 2. COTTON (Gossypium spp.)
    # ----------------------------------------------------
    "Cotton___Bacterial_blight": {
        "class_name": "Cotton___Bacterial_blight",
        "crop_name": "Cotton (Gossypium spp.)",
        "disease_name": "Bacterial Blight / Angular Leaf Spot (Xanthomonas citri pv. malvacearum)",
        "description": "Bacterial blight is a major foliar disease of cotton causing angular water-soaked leaf lesions delimited by veins, black arm stem cankers, and boll rot.",
        "symptoms": [
            "Small water-soaked angular leaf spots bound by veins that turn purplish-brown to black.",
            "Veinal necrosis leading to systemic 'black arm' cankers on petioles and stems.",
            "Water-soaked circular greasy spots on developing green bolls causing premature drop."
        ],
        "prevention": [
            "Delint seed acid treatment (H2SO4 @ 100 mL/kg seed) to kill seed-borne bacteria.",
            "Plant bacterial blight-resistant cotton hybrids and destroy crop residue after harvest.",
            "Avoid excessive sprinkler irrigation and high nitrogen applications."
        ],
        "treatment_or_cure": [
            "Apply copper-based bactericide tank-mixed with an antibiotic at the first sign of angular spots.",
            "Avoid field operations while canopy foliage is wet to prevent mechanical spreading."
        ],
        "recovery_period": "10–14 days with copper bactericide application and moisture control",
        "recommendation_1": "Spray Copper oxychloride 50 WP (0.3% / 3 g/L) tank-mixed with Streptocycline (100 ppm / 1 g in 10 L water) at initial angular spot appearance.",
        "recommendation_2": "Apply Bacillus subtilis biological formulations and avoid excess nitrogen fertilization which stimulates succulent foliage.",
        "chemical_information": "Copper oxychloride 50 WP combined with Streptocycline or Kasugamycin provides effective bacterial suppression. Follow state agricultural university spray schedules.",
        "disclaimer": "Use antibiotics responsibly according to registered agricultural regulations and observe safety intervals.",
        "translations": {
            "en": {
                "crop_name": "Cotton (Gossypium spp.)",
                "disease_name": "Bacterial Blight / Angular Leaf Spot",
                "description": "Bacterial blight causes angular water-soaked lesions delimited by leaf veins, black arm cankers, and boll rot.",
                "symptoms": [
                    "Small water-soaked angular leaf spots bounded by leaf veins.",
                    "Vein necrosis and black arm lesions on stems.",
                    "Water-soaked greasy spots on green cotton bolls."
                ],
                "prevention": [
                    "Delint and treat seeds prior to sowing.",
                    "Plant resistant cotton hybrids.",
                    "Avoid excessive sprinkler irrigation."
                ],
                "treatment_or_cure": [
                    "Apply copper bactericide mixed with Streptocycline early.",
                    "Avoid moving through wet fields to prevent spread."
                ],
                "recovery_period": "10–14 days with copper bactericide application and moisture control",
                "recommendation_1": "Spray Copper oxychloride 50 WP (3 g/L) tank-mixed with Streptocycline (100 ppm / 1 g per 10 L).",
                "recommendation_2": "Apply Bacillus subtilis formulations and avoid excess nitrogen fertilization.",
                "chemical_information": "Copper oxychloride with Streptocycline suppresses bacterial blight effectively. Follow label instructions.",
                "disclaimer": "Follow agricultural regulations and safety intervals."
            },
            "hi": {
                "crop_name": "कपास (Cotton)",
                "disease_name": "जीवाणु झुलसा / कोणीय पत्ती धब्बा (Bacterial Blight)",
                "description": "कपास का जीवाणु झुलसा पत्तियों पर नसों से घिरे कोणीय पानीदार धब्बे, तने पर काली धारियां (ब्लैक आर्म) और गूलर सड़न पैदा करता है।",
                "symptoms": [
                    "पत्तियों की नसों से घिरे कोणीय पानीदार धब्बे जो बाद में काले-भूरे हो जाते हैं।",
                    "तने और टहनियों पर काले कैंकर (ब्लैक आर्म) बन जाते हैं।",
                    "हरे गूलरों (टिंडों) पर पानीदार गोल चिकने धब्बे।"
                ],
                "prevention": [
                    "एसिड द्वारा बीजोपचार करें ताकि बीज जनित जीवाणु नष्ट हो जाएं।",
                    "रोग प्रतिरोधी बीटी कपास की किस्में लगाएं।",
                    "अत्यधिक नाइट्रोजन खाद और फव्वारा सिंचाई से बचें।"
                ],
                "treatment_or_cure": [
                    "शुरुआती लक्षण दिखते ही कॉपर ऑक्सीक्लोराइड और एंटीबायोटिक का छिड़काव करें।",
                    "गीली फसल में निराई-गुड़ाई न करें जिससे संक्रमण न फैले।"
                ],
                "recovery_period": "कॉपर जीवाणुनाशक के साथ 10-14 दिन का प्रबंधन आवश्यक है",
                "recommendation_1": "कॉपर ऑक्सीक्लोराइड 50 WP (3 ग्रा/ली) के साथ स्ट्रेप्टोसाइक्लिन (1 ग्रा प्रति 10 लीटर पानी) मिलाकर छिड़कें।",
                "recommendation_2": "बैसिलस सबटिलिस जैव-कीटनाशक का प्रयोग करें और अतिरिक्त नाइट्रोजन न दें।",
                "chemical_information": "कॉपर ऑक्सीक्लोराइड और स्ट्रेप्टोसाइक्लिन का मिश्रण जीवाणु झुलसा पर सर्वोत्तम नियंत्रण देता है।",
                "disclaimer": "कृषि विभाग के निर्देशों और लेबल पर दी गई सुरक्षा सावधानियों का पालन करें।"
            },
            "mr": {
                "crop_name": "कापूस (Cotton)",
                "disease_name": "जिवाणूजन्य करपा / कोनीय ठिपके (Bacterial Blight)",
                "description": "कापसावरील जिवाणूजन्य करप्यामुळे पानांच्या शिरांमध्ये कोनीय पाणीदार ठिपके पडतात, फांद्यांवर काळे चट्टे (ब्लॅक आर्म) येतात आणि बोंडे सडतात.",
                "symptoms": [
                    "पानांवर शिरांनी मर्यादित असलेले कोनीय पाणीदार ठिपके जे नंतर काळपट-तांबूस होतात.",
                    "फांद्यांवर काळे चट्टे (ब्लॅक आर्म) पडून फांद्या मोडतात.",
                    "हिरव्या बोंडांवर तेलकट, खोलगट गोल चट्टे दिसतात."
                ],
                "prevention": [
                    "ॲसिड डिलिंटिंग करून बियाण्यावरील जिवाणू नष्ट करा.",
                    "करपा प्रतिबंधक वाणांची लागवड करा.",
                    "नत्र खतांचा अतिवापर टाळा."
                ],
                "treatment_or_cure": [
                    "लक्षणे दिसताच कॉपर व स्ट्रेप्टोसायक्लिनची फवारणी करा.",
                    "ओलसर पिकात काम करणे टाळा जेणेकरून रोग पसरणार नाही."
                ],
                "recovery_period": "कॉपर जिवाणूनाशक व ओलावा नियंत्रणासह १० ते १४ दिवसांचे व्यवस्थापन",
                "recommendation_1": "कॉपर ऑक्सिक्लोराईड ५० डब्ल्यूपी (३ ग्रॅम/लि) अधिक स्ट्रेप्टोसायक्लिन (१ ग्रॅम प्रति १० लिटर पाणी) एकत्र फवारा.",
                "recommendation_2": "बॅसिलस सबटिलिस जैविक जिवाणूनाशकाचा वापर करा आणि जास्त नत्र देणे टाळा.",
                "chemical_information": "कॉपर ऑक्सिक्लोराईड व स्ट्रेप्टोसायक्लिनचे मिश्रण जिवाणूजन्य करप्यावर गुणकारी आहे.",
                "disclaimer": "कीटकनाशके वापरताना संरक्षक साधनांचा वापर करा व लेबलवरील सूचना पाळा."
            }
        }
    },
    "Cotton___Leaf_curl_virus": {
        "class_name": "Cotton___Leaf_curl_virus",
        "crop_name": "Cotton (Gossypium spp.)",
        "disease_name": "Cotton Leaf Curl Virus (CLCuD)",
        "description": "Cotton leaf curl begomovirus is transmitted by whiteflies (Bemisia tabaci), producing upward or downward leaf curling, vein thickening, and leaf-like enations on leaf undersides.",
        "symptoms": [
            "Upward or downward rolling and curling of leaves.",
            "Thickening of primary and secondary leaf veins on undersides.",
            "Leaf-like outgrowths (enations) forming on veins beneath the leaf lamina.",
            "Severe stunting and near total reduction of boll formation."
        ],
        "prevention": [
            "Sow leaf curl virus-resistant/tolerant cotton hybrids.",
            "Eradicate alternate weed hosts (e.g., Abutilon, Parthenium, Sida) around field borders.",
            "Treat seed with Imidacloprid 70 WS to control early whitefly infestation."
        ],
        "treatment_or_cure": [
            "Manage whitefly vectors immediately using selective insecticides.",
            "Rogue out severely affected plants during early vegetative growth."
        ],
        "recovery_period": "Vector control requires 7–10 days; infected plants should be managed to limit field-wide secondary spread",
        "recommendation_1": "Manage the whitefly vector using systemic insecticides such as Diafenthiuron 50 WP (1.2 g/L) or Spiromesifen 22.9 SC (1 mL/L).",
        "recommendation_2": "Eradicate alternate weed hosts around field borders and deploy yellow sticky traps (25 traps/ha) as an IPM tactic.",
        "chemical_information": "Systemic insecticides against whiteflies include Diafenthiuron 50 WP, Pyriproxyfen 10 EC, or Spiromesifen. Rotate chemistry to prevent whitefly resistance.",
        "disclaimer": "Viral diseases cannot be cured once the plant is systemically infected; management focuses on vector suppression.",
        "translations": {
            "en": {
                "crop_name": "Cotton (Gossypium spp.)",
                "disease_name": "Cotton Leaf Curl Virus (CLCuD)",
                "description": "Cotton leaf curl virus is transmitted by whiteflies, causing severe leaf curling and vein thickening.",
                "symptoms": [
                    "Upward or downward rolling and curling of leaves.",
                    "Thickening of leaf veins on undersides.",
                    "Leaf-like enations on lower leaf surfaces.",
                    "Severe stunting and reduced boll formation."
                ],
                "prevention": [
                    "Sow leaf curl virus tolerant hybrids.",
                    "Eradicate weed hosts around field borders.",
                    "Treat seeds with Imidacloprid."
                ],
                "treatment_or_cure": [
                    "Manage whitefly vectors immediately.",
                    "Rogue out severely affected plants early."
                ],
                "recovery_period": "Vector control requires 7–10 days to check secondary spread",
                "recommendation_1": "Manage whiteflies using Diafenthiuron 50 WP (1.2 g/L) or Spiromesifen 22.9 SC (1 mL/L).",
                "recommendation_2": "Eradicate alternate weed hosts and deploy yellow sticky traps (25/ha).",
                "chemical_information": "Diafenthiuron 50 WP or Spiromesifen suppress whitefly vectors. Follow pesticide safety directions.",
                "disclaimer": "Viral infections cannot be cured; focus on rigorous vector suppression."
            },
            "hi": {
                "crop_name": "कपास (Cotton)",
                "disease_name": "कपास पत्ता मरोड़ वायरस (Leaf Curl Virus)",
                "description": "सफेद मक्खी द्वारा फैलने वाला यह वायरस पत्तियों को ऊपर या नीचे की ओर मोड़ देता है और नसों को मोटा कर देता है।",
                "symptoms": [
                    "पत्तियों का ऊपर या नीचे की ओर मुड़ना और ऐंठना।",
                    "पत्तियों की निचली सतह पर नसों का मोटा होना।",
                    "पत्तियों के नीचे छोटी पत्ती जैसी गांठें (इनेशन) बनना।",
                    "पौधों का बौना रह जाना और टिंडों का न बनना।"
                ],
                "prevention": [
                    "पत्ता मरोड़ प्रतिरोधी किस्मों की बुआई करें।",
                    "खेत की मेड़ों से खरपतवार (कंघी, गाजर घास) नष्ट करें।",
                    "इमिडाक्लोप्रिड से बीजोपचार करें।"
                ],
                "treatment_or_cure": [
                    "सफेद मक्खी का तुरंत रासायनिक नियंत्रण करें।",
                    "शुरुआती संक्रमित पौधों को उखाड़कर नष्ट करें।"
                ],
                "recovery_period": "सफेद मक्खी नियंत्रण में 7-10 दिन लगते हैं; द्वितीयक प्रसार रोकना मुख्य उद्देश्य है",
                "recommendation_1": "सफेद मक्खी नियंत्रण के लिए डायफेंथियूरॉन 50 WP (1.2 ग्रा/ली) या स्पाइरोमेसिफेन 22.9 SC (1 मि.ली/ली) का छिड़काव करें।",
                "recommendation_2": "मेड़ों से खरपतवार नष्ट करें और पीले चिपचिपे ट्रैप (25 प्रति हेक्टेयर) लगाएं।",
                "chemical_information": "डायफेंथियूरॉन 50 WP या स्पाइरोमेसिफेन सफेद मक्खी का प्रभावी नियंत्रण करते हैं।",
                "disclaimer": "वायरस का कोई सीधा इलाज नहीं है, सफेद मक्खी को मारकर ही इसे रोका जा सकता है।"
            },
            "mr": {
                "crop_name": "कापूस (Cotton)",
                "disease_name": "कापसावरील चुरडा-मुरडा / लीफ कर्ल (Leaf Curl Virus)",
                "description": "पांढऱ्या माशीद्वारे पसरणाऱ्या या विषाणूमुळे कापसाची पाने वर किंवा खाली मुरडतात, शिरा जाड होतात आणि बोंडे लागत नाहीत.",
                "symptoms": [
                    "पाने वरच्या किंवा खालच्या बाजूला वाटीसारखी गोळा होणे व मुरडणे.",
                    "पानांच्या खालच्या बाजूच्या शिरा जाड व फुगीर होणे.",
                    "शिरांवर पानासारखी छोटी वाढ तयार होणे.",
                    "झाडांची वाढ पूर्णपणे खुंटणे."
                ],
                "prevention": [
                    "रोगप्रतिकारक वाणांची निवड करा.",
                    "शेताच्या बांधावरील तण (काटेमाट, पेटारी) नष्ट करा.",
                    "इमिडाक्लोप्रिडने बीजप्रक्रिया करा."
                ],
                "treatment_or_cure": [
                    "पांढऱ्या माशीचे तात्काळ रासायनिक नियंत्रण करा.",
                    "सुरुवातीलाच बाधित झाडे काढून टाका."
                ],
                "recovery_period": "पांढऱ्या माशीच्या नियंत्रणासाठी ७ ते १० दिवस लागतात; रोगाचा फैलाव रोखणे आवश्यक",
                "recommendation_1": "पांढऱ्या माशीसाठी डायाफेन्थियुरॉन ५० डब्ल्यूपी (१.२ ग्रॅम/लि) किंवा स्पायरोमेसिफेन २२.९ एससी (१ मिली/लि) फवारा.",
                "recommendation_2": "बांधावरील तण नष्ट करा आणि हेक्टरी २५ पिवळे चिकट सापळे लावा.",
                "chemical_information": "डायाफेन्थियुरॉन किंवा स्पायरोमेसिफेन पांढऱ्या माशीवर अतिशय प्रभावी आहेत.",
                "disclaimer": "विषाणूवर थेट औषध नसते; पांढरी माशी रोखणे हाच एकमेव उपाय आहे."
            }
        }
    },
    "Cotton___Alternaria_leaf_spot": {
        "class_name": "Cotton___Alternaria_leaf_spot",
        "crop_name": "Cotton (Gossypium spp.)",
        "disease_name": "Alternaria Leaf Spot (Alternaria macrospora)",
        "description": "Alternaria leaf spot causes circular brown necrotic spots with concentric target-board rings on cotton leaves, favored by intermittent rains and potassium deficiency.",
        "symptoms": [
            "Brown to dark brown circular spots with distinct concentric rings (target board pattern).",
            "Centers of older spots crack and fall out, giving a shot-hole appearance.",
            "Severe foliar spotting leads to premature shedding of leaves and immature bolls."
        ],
        "prevention": [
            "Ensure adequate and balanced soil potassium (K) nutrition to enhance cell wall strength.",
            "Destroy cotton stalks and debris after harvest to reduce overwintering inocula.",
            "Avoid high plant density and waterlogged conditions."
        ],
        "treatment_or_cure": [
            "Apply protective foliar fungicides at first appearance of concentric lesions.",
            "Supplement with potassium nitrate foliar sprays."
        ],
        "recovery_period": "10–15 days of foliar fungicide management and potassium nutrition",
        "recommendation_1": "Apply Mancozeb 75 WP (0.25% / 2.5 g/L) or Propiconazole 25 EC (0.1% / 1 mL/L) upon observation of concentric necrotic leaf spots.",
        "recommendation_2": "Apply foliar potassium nitrate (KNO3 1%) to strengthen leaf cell walls and apply Trichoderma viride bio-fungicide.",
        "chemical_information": "Mancozeb 75 WP, Propiconazole 25 EC, or Pyraclostrobin 20 WG provide excellent control against Alternaria leaf spot. Follow manufacturer label intervals.",
        "disclaimer": "Always observe safety equipment requirements during pesticide spraying.",
        "translations": {
            "en": {
                "crop_name": "Cotton (Gossypium spp.)",
                "disease_name": "Alternaria Leaf Spot (Alternaria macrospora)",
                "description": "Alternaria leaf spot causes concentric circular brown spots on cotton foliage, aggravated by potassium deficiency.",
                "symptoms": [
                    "Brown circular spots with concentric target-board rings.",
                    "Shot-hole appearance as spot centers dry and drop out.",
                    "Premature leaf and square shedding."
                ],
                "prevention": [
                    "Ensure adequate soil potassium nutrition.",
                    "Destroy cotton crop debris after harvest.",
                    "Avoid waterlogging."
                ],
                "treatment_or_cure": [
                    "Apply foliar fungicides upon seeing lesions.",
                    "Spray potassium nitrate foliar feed."
                ],
                "recovery_period": "10–15 days of foliar fungicide management and potassium nutrition",
                "recommendation_1": "Apply Mancozeb 75 WP (2.5 g/L) or Propiconazole 25 EC (1 mL/L) upon observing concentric spots.",
                "recommendation_2": "Apply foliar potassium nitrate (KNO3 1%) and Trichoderma viride bio-fungicide.",
                "chemical_information": "Mancozeb 75 WP or Propiconazole 25 EC control Alternaria leaf spot effectively.",
                "disclaimer": "Follow pesticide label instructions and safety directions."
            },
            "hi": {
                "crop_name": "कपास (Cotton)",
                "disease_name": "अल्टरनेरिया पत्ती धब्बा (Alternaria Leaf Spot)",
                "description": "कपास की पत्तियों पर भूरे रंग के गोल धब्बे बनते हैं जिनमें संकेंद्री छल्ले (टारगेट बोर्ड) दिखते हैं, पोटाश की कमी से यह रोग बढ़ता है।",
                "symptoms": [
                    "पत्तियों पर संकेंद्री छल्लों वाले भूरे गोल धब्बे।",
                    "धब्बों के बीच का भाग सूखकर गिर जाता है जिससे पत्तियों में छेद हो जाते हैं।",
                    "पत्तियां और छोटे गूलर समय से पहले गिर जाते हैं।"
                ],
                "prevention": [
                    "मिट्टी में पोटाश की पर्याप्त मात्रा सुनिश्चित करें।",
                    "कटाई के बाद पुरानी डंठलें नष्ट करें।",
                    "खेत में पानी भरने से रोकें।"
                ],
                "treatment_or_cure": [
                    "धब्बे दिखने पर तुरंत कवकनाशी का छिड़काव करें।",
                    "पोटैशियम नाइट्रेट का फोलियर स्प्रे दें।"
                ],
                "recovery_period": "कवकनाशी और पोटाश पोषण के साथ 10-15 दिन का प्रबंधन आवश्यक है",
                "recommendation_1": "संकेंद्री धब्बे दिखने पर मैंकोजेब 75 WP (2.5 ग्रा/ली) या प्रोपिकोनाजोल 25 EC (1 मि.ली/ली) का छिड़काव करें।",
                "recommendation_2": "पत्तियों की मजबूती के लिए पोटैशियम नाइट्रेट (KNO3 1%) और ट्राइकोडर्मा विरिडी जैव-कवकनाशी का छिड़काव करें।",
                "chemical_information": "मैंकोजेब 75 WP या प्रोपिकोनाजोल 25 EC अल्टरनेरिया पर बहुत अच्छा असर करते हैं।",
                "disclaimer": "कीटनाशक छिड़कते समय सुरक्षात्मक मास्क और दस्ताने पहनें।"
            },
            "mr": {
                "crop_name": "कापूस (Cotton)",
                "disease_name": "अल्टरनेरिया पानांवरील ठिपके (Alternaria Leaf Spot)",
                "description": "पानांवर वर्तुळाकार तपकिरी ठिपके पडतात ज्यामध्ये चकत्यांसारखी वलये दिसतात; पोटॅशच्या कमतरतेमुळे हा रोग जास्त वाढतो.",
                "symptoms": [
                    "पानांवर गोलाकार वलयांकित तपकिरी ठिपके (टार्गेट बोर्ड पॅटर्न).",
                    "ठिपक्यांचा मधला भाग वाळून गळतो आणि पानांना चाळणीसारखी छिद्रे पडतात.",
                    "पाने आणि पाते अकाली गळून पडतात."
                ],
                "prevention": [
                    "जमिनीत पोटॅश खतांची योग्य मात्रा द्या.",
                    "काढणीनंतर पराट्या शेतातून काढून नष्ट करा.",
                    "पाण्याचा उत्तम निचरा ठेवा."
                ],
                "treatment_or_cure": [
                    "ठिपके दिसताच बुरशीनाशकाची फवारणी करा.",
                    "पोटॅशियम नायट्रेटची फवारणी करा."
                ],
                "recovery_period": "बुरशीनाशक व पोटॅशच्या पोषणासह १० ते १५ दिवसांचे व्यवस्थापन",
                "recommendation_1": "वलयांकित ठिपके दिसताच मॅन्कोझेब ७५ डब्ल्यूपी (२.५ ग्रॅम/लि) किंवा प्रोपिकोनाझोल २५ ईसी (१ मिली/लि) फवारा.",
                "recommendation_2": "पानांच्या ताकदीसाठी पोटॅशियम नायट्रेट (१३:००:४५ - १%) आणि ट्रायकोडर्मा व्हिरिडीची फवारणी करा.",
                "chemical_information": "मॅन्कोझेब किंवा प्रोपिकोनाझोल या बुरशीनाशकांचा वेळेवर वापर करा.",
                "disclaimer": "औषध लेबलवरील सुरक्षित फवारणीच्या नियमांचे पालन करा."
            }
        }
    },
    "Cotton___healthy": {
        "class_name": "Cotton___healthy",
        "crop_name": "Cotton (Gossypium spp.)",
        "disease_name": "Healthy Foliage",
        "description": "Cotton plant exhibits broad, vigorous palmately lobed green leaves without angular water-soaked lesions, leaf curling, or concentric fungal spots.",
        "symptoms": [
            "Dark green lobed leaves with clean margins and no curling.",
            "Intact leaf lamina free from angular spots or mosaic mottling.",
            "Healthy squares and boll development with vigorous stem growth."
        ],
        "prevention": [
            "Deploy pheromone traps (5 traps/ha) for pink bollworm monitoring.",
            "Maintain balanced NPK fertilization and avoid late excess nitrogen.",
            "Preserve beneficial predators (chrysoperla, ladybirds, spiders) by avoiding indiscriminate insecticide sprays."
        ],
        "treatment_or_cure": [
            "Apply foliar micronutrient sprays (Boron 0.1% + Magnesium sulfate 1%) during square and boll development.",
            "Ensure regular irrigation scheduling during peak flowering and boll formation."
        ],
        "recovery_period": "N/A — Foliage is healthy. Maintain regular scouting",
        "recommendation_1": "Practice integrated pest management (IPM) with pheromone traps and maintain balanced NPK nutrition.",
        "recommendation_2": "Preserve natural beneficial predators by avoiding broad-spectrum synthetic pyrethroids and apply boron at flowering.",
        "chemical_information": "No chemical fungicides or bactericides required for healthy cotton foliage.",
        "disclaimer": "Regular field scouting is recommended for bollworm and sucking pest monitoring.",
        "translations": {
            "en": {
                "crop_name": "Cotton (Gossypium spp.)",
                "disease_name": "Healthy Foliage",
                "description": "Cotton plant exhibits vigorous palmately lobed green leaves free from lesions or curling.",
                "symptoms": [
                    "Dark green lobed leaves with clean margins.",
                    "No leaf curling or angular spots.",
                    "Vigorous branching and normal boll setting."
                ],
                "prevention": [
                    "Deploy pheromone traps for pest monitoring.",
                    "Maintain balanced NPK nutrition.",
                    "Preserve beneficial insect predators."
                ],
                "treatment_or_cure": [
                    "Apply micronutrients (Boron + Magnesium) at boll development.",
                    "Provide timely irrigation during flowering."
                ],
                "recovery_period": "N/A — Foliage is healthy. Maintain regular scouting",
                "recommendation_1": "Practice IPM with pheromone traps and maintain balanced NPK nutrition.",
                "recommendation_2": "Preserve beneficial predators and spray boron at flowering stage.",
                "chemical_information": "No chemicals needed for healthy foliage.",
                "disclaimer": "Regular scouting is recommended."
            },
            "hi": {
                "crop_name": "कपास (Cotton)",
                "disease_name": "स्वस्थ पत्तियां (Healthy Foliage)",
                "description": "कपास की पत्तियां पूरी तरह स्वस्थ हैं, जिनमें कोई मरोड़, जीवाणु धब्बा या फफूंद नहीं है।",
                "symptoms": [
                    "गहरे हरे रंग की चौड़ी और स्वस्थ पत्तियां।",
                    "पत्तियों में कोई ऐंठन या कोणीय धब्बे नहीं हैं।",
                    "फूल और गूलर का सामान्य स्वस्थ विकास।"
                ],
                "prevention": [
                    "गुलाबी सुंडी की निगरानी के लिए फेरोमोन ट्रैप लगाएं।",
                    "संतुलित एनपीके खाद का प्रयोग करें।",
                    "मित्र कीटों की रक्षा करें।"
                ],
                "treatment_or_cure": [
                    "गूलर बनते समय बोरॉन और मैग्नीशियम सल्फेट का छिड़काव करें।",
                    "फूल आने के समय उचित सिंचाई बनाए रखें।"
                ],
                "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। नियमित निरीक्षण जारी रखें",
                "recommendation_1": "फेरोमोन ट्रैप के साथ एकीकृत कीट प्रबंधन अपनाएं और संतुलित खाद दें।",
                "recommendation_2": "मित्र कीटों को बचाएं और फूल खिलते समय 0.1% बोरॉन का छिड़काव करें।",
                "chemical_information": "स्वस्थ फसल पर किसी कवकनाशी की आवश्यकता नहीं है।",
                "disclaimer": "नियमित निगरानी बनाए रखें।"
            },
            "mr": {
                "crop_name": "कापूस (Cotton)",
                "disease_name": "निरोगी पाने (Healthy Foliage)",
                "description": "कापसाची पाने पूर्णपणे निरोगी असून पानांवर कोणताही चुरडा-मुरडा किंवा करप्याचे डाग नाहीत.",
                "symptoms": [
                    "गडद हिरवीगार, निरोगी व पसरट पाने.",
                    "पानांवर कोणतेही कोणीय किंवा वलयांकित ठिपके नसणे.",
                    "पात्या व बोंडांची जोमदार निरोगी वाढ."
                ],
                "prevention": [
                    "गुलाबी बोंडअळीच्या सर्वेक्षणासाठी कामगंध सापळे लावा.",
                    "संतुलित खतांचा वापर करा.",
                    "मित्रकिडींचे संवर्धन करा."
                ],
                "treatment_or_cure": [
                    "बोंड वाढीच्या काळात बोरोन आणि मॅग्नेशियम सल्फेटची फवारणी करा.",
                    "फुलोऱ्यात असताना पाण्याचा ताण पडू देऊ नका."
                ],
                "recovery_period": "लागू नाही — पाने निरोगी आहेत. नियमित पाहणी चालू ठेवा",
                "recommendation_1": "कामगंध सापळ्यांचा वापर करून एकात्मिक कीड व्यवस्थापन व संतुलित खत व्यवस्थापन राखा.",
                "recommendation_2": "मित्रकिडींचे रक्षण करा आणि पाते लागताना ०.१% बोरॉनची फवारणी करा.",
                "chemical_information": "निरोगी पिकावर बुरशीनाशकांची गरज नसते.",
                "disclaimer": "पिकाची नियमित पाहणी करत राहा."
            }
        }
    },

    # ----------------------------------------------------
    # 3. PIGEON PEA / RED GRAM (Cajanus cajan)
    # ----------------------------------------------------
    "Pigeon_Pea___Sterility_mosaic": {
        "class_name": "Pigeon_Pea___Sterility_mosaic",
        "crop_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
        "disease_name": "Sterility Mosaic Disease (PPSMV)",
        "description": "Pigeonpea Sterility Mosaic Disease (the 'green plague') is transmitted by the eriophyid mite (Aceria cajani), causing mosaic mottling, excessive vegetative bushiness, and complete floral sterility.",
        "symptoms": [
            "Severe mosaic mottling with chlorotic rings on leaves.",
            "Excessive clustering of small leaves giving plants a bushy, broom-like appearance.",
            "Partial or complete cessation of flowering, leading to total pod sterility."
        ],
        "prevention": [
            "Plant sterility mosaic-resistant cultivars (e.g., Asha / ICPL 87119, BSMR 736, Maruthi).",
            "Rogue out and bury infected plants early before mite populations multiply.",
            "Avoid ratoon cropping of pigeonpea which harbors overwintering mites."
        ],
        "treatment_or_cure": [
            "Control the eriophyid mite vector early in the season.",
            "Spray acaricides upon seeing first mosaic symptoms on border plants."
        ],
        "recovery_period": "Eriophyid mite vector suppression requires 7–12 days to prevent secondary bushiness spread",
        "recommendation_1": "Spray acaricides such as Fenazaquin 10 EC (0.1% / 1 mL/L) or Propargite 57 EC (0.2% / 2 mL/L) to suppress the vector Aceria cajani.",
        "recommendation_2": "Rogue out severely stunted sterility mosaic-infected plants early and apply wettable sulfur (0.2% / 2 g/L) to suppress mite populations.",
        "chemical_information": "Selective acaricides like Fenazaquin 10 EC, Spiromesifen 22.9 SC, or wettable sulfur control vector eriophyid mites. Follow label safety instructions.",
        "disclaimer": "Sterility mosaic is incurable in affected plants; management focuses strictly on mite control and resistant cultivars.",
        "translations": {
            "en": {
                "crop_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
                "disease_name": "Sterility Mosaic Disease (PPSMV)",
                "description": "Sterility mosaic disease is transmitted by eriophyid mites, causing excessive bushiness and complete floral sterility.",
                "symptoms": [
                    "Mosaic mottling with light and dark green patches.",
                    "Excessive leaf clustering creating a bushy appearance.",
                    "Complete absence of flowers and pods."
                ],
                "prevention": [
                    "Plant sterility mosaic resistant cultivars (Asha, BSMR 736).",
                    "Rogue out infected plants early.",
                    "Avoid ratoon cropping."
                ],
                "treatment_or_cure": [
                    "Control the eriophyid mite vector early.",
                    "Apply miticides on border plants."
                ],
                "recovery_period": "Mite vector suppression requires 7–12 days to stop secondary spread",
                "recommendation_1": "Spray acaricides such as Fenazaquin 10 EC (1 mL/L) or Propargite 57 EC (2 mL/L) against vector mites.",
                "recommendation_2": "Rogue out infected plants and apply wettable sulfur (2 g/L) as a bio-rational mite suppressant.",
                "chemical_information": "Fenazaquin 10 EC or wettable sulfur control the vector mite. Follow manufacturer label instructions.",
                "disclaimer": "Incurable once systemically infected; focus strictly on vector mite management."
            },
            "hi": {
                "crop_name": "अरहर / तुअर (Pigeon Pea)",
                "disease_name": "बांझपन मोज़ेक रोग (Sterility Mosaic Disease)",
                "description": "अरहर का बांझपन मोज़ेक माइट कीट द्वारा फैलता है, जिससे पत्तियां झाड़ीनुमा हो जाती हैं और फूल व फलियां नहीं बनती हैं।",
                "symptoms": [
                    "पत्तियों पर हल्के और गहरे हरे रंग के मोज़ेक धब्बे।",
                    "पत्तियां बहुत छोटी होकर गुच्छों में बदल जाती हैं और पौधा झाड़ी जैसा दिखता है।",
                    "पौधों में फूल नहीं आते और फलियां पूरी तरह बांझ रह जाती हैं।"
                ],
                "prevention": [
                    "रोग प्रतिरोधी किस्में (जैसे आशा / ICPL 87119, BSMR 736) लगाएं।",
                    "संक्रमित पौधों को शुरुआत में ही उखाड़कर नष्ट करें।",
                    "अरहर की रटून (पेड़ी) फसल लेने से बचें।"
                ],
                "treatment_or_cure": [
                    "वाहक माइट कीट का तुरंत रासायनिक नियंत्रण करें।",
                    "खेत की सीमा पर लगे पौधों पर कीटनाशक का छिड़काव करें।"
                ],
                "recovery_period": "माइट कीट के नियंत्रण में 7-12 दिन लगते हैं जिससे स्वस्थ पौधों में प्रसार रुकता है",
                "recommendation_1": "माइट कीट नियंत्रण के लिए फेनाजाक्विन 10 EC (1 मि.ली/ली) या प्रोपारगाइट 57 EC (2 मि.ली/ली) का छिड़काव करें।",
                "recommendation_2": "संक्रमित पौधों को उखाड़कर नष्ट करें और वेटेबल सल्फर (2 ग्रा/ली) का सुरक्षात्मक छिड़काव करें।",
                "chemical_information": "फेनाजाक्विन 10 EC या वेटेबल सल्फर माइट कीट को प्रभावी रूप से नियंत्रित करते हैं।",
                "disclaimer": "यह रोग एक बार लगने पर ठीक नहीं होता, केवल कीट नियंत्रण और प्रतिरोधी किस्मों से बचा जा सकता है।"
            },
            "mr": {
                "crop_name": "तूर (Pigeon Pea)",
                "disease_name": "वांझ रोग / स्टेरिलिटी मोझॅक (Sterility Mosaic)",
                "description": "तुरीवरील वांझ रोग हा कोळी किडीद्वारे (माइट्स) पसरतो; झाडाला भरपूर झाडासारख्या बारीक फांद्या फुटतात पण फुले व शेंगा अजिबात लागत नाहीत.",
                "symptoms": [
                    "पानांवर फिकट व गडद हिरवे चट्टे दिसणे.",
                    "झाडाला पानांचे बारीक गुच्छ येऊन झाड झाडूसारखे किंवा झुडपासारखे दिसणे.",
                    "झाडाला फुले न लागणे व संपूर्ण वांझपणा येणे."
                ],
                "prevention": [
                    "रोगप्रतिकारक वाणांची (उदा. आशा, बीएसएमआर ७३६) लागवड करा.",
                    "सुरुवातीलाच दिसलेली रोगट झाडे उपटून नष्ट करा.",
                    "तुरीचे खोडवे (रटून) घेणे टाळा."
                ],
                "treatment_or_cure": [
                    "कोळी किडीचा वेळेवर बंदोबस्त करा.",
                    "बांधावरील झाडांवर कोळीनाशकाची फवारणी करा."
                ],
                "recovery_period": "कोळी किडीच्या नियंत्रणासाठी ७ ते १२ दिवस लागतात; निरोगी पिकाचे रक्षण करणे हाच उद्देश",
                "recommendation_1": "कोळी किडीच्या नियंत्रणासाठी फेनाझाक्विन १० ईसी (१ मिली/लि) किंवा प्रोपारगाइट ५७ ईसी (२ मिली/लि) फवारा.",
                "recommendation_2": "बाधित झाडे उपटून टाका आणि पाण्यात विरघळणारे गंधक (२ ग्रॅम/लि) कोळी प्रतिबंधक म्हणून वापरा.",
                "chemical_information": "फेनाझाक्विन किंवा विरघळणारे गंधक वांझ रोगाचा प्रसार करणाऱ्या कोळी किडीवर नियंत्रण ठेवतात.",
                "disclaimer": "हा रोग औषधाने बरा होत नाही; केवळ कोळी नियंत्रण व प्रतिकारक वाण हाच उपाय आहे."
            }
        }
    },
    "Pigeon_Pea___Phytophthora_blight": {
        "class_name": "Pigeon_Pea___Phytophthora_blight",
        "crop_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
        "disease_name": "Phytophthora Blight (Phytophthora cajani)",
        "description": "Phytophthora blight attacks young pigeonpea seedlings and plants during heavy monsoons, causing water-soaked stem cankers, rapid wilting, and stem breakage.",
        "symptoms": [
            "Water-soaked circular lesions on leaves that rapidly dry and wither.",
            "Dark brown to black necrotic girdling cankers on the main stem and branches.",
            "Rapid wilting and drying of the upper canopy while leaves remain attached."
        ],
        "prevention": [
            "Plant pigeonpea on raised beds or broad bed furrow (BBF) to prevent standing water.",
            "Ensure swift field drainage during continuous torrential rainfall.",
            "Treat seed with Metalaxyl-M (2 g/kg seed) prior to sowing."
        ],
        "treatment_or_cure": [
            "Apply systemic anti-oomycete fungicides immediately upon water-soaked stem lesion detection.",
            "Drench collar region of adjacent healthy plants with protective fungicide."
        ],
        "recovery_period": "5–10 days of rapid drainage and anti-oomycete fungicide application",
        "recommendation_1": "Spray Metalaxyl-M + Mancozeb (0.2% / 2 g/L) or Fosetyl-Al (0.2% / 2 g/L) immediately upon noticing water-soaked stem lesions.",
        "recommendation_2": "Ensure rapid drainage of standing field water to eliminate zoospore movement and apply Trichoderma asperellum soil amendment.",
        "chemical_information": "Metalaxyl-M + Mancozeb, Fosetyl-Al, or Dimethomorph provide effective control against Phytophthora blight. Ensure application at soil-stem collar zone.",
        "disclaimer": "Avoid waterlogging; chemical treatment must be coupled with rapid field surface drainage.",
        "translations": {
            "en": {
                "crop_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
                "disease_name": "Phytophthora Blight (Phytophthora cajani)",
                "description": "Phytophthora blight causes water-soaked stem cankers and rapid wilting during heavy rains.",
                "symptoms": [
                    "Water-soaked lesions on foliage that wither rapidly.",
                    "Dark girdling cankers on stems causing breakage.",
                    "Sudden wilting with dry leaves remaining attached."
                ],
                "prevention": [
                    "Plant on raised beds to ensure rapid drainage.",
                    "Avoid standing water in the field.",
                    "Treat seeds with Metalaxyl-M."
                ],
                "treatment_or_cure": [
                    "Apply anti-oomycete fungicides immediately.",
                    "Drench collar region of surrounding plants."
                ],
                "recovery_period": "5–10 days of rapid drainage and anti-oomycete fungicide application",
                "recommendation_1": "Spray Metalaxyl-M + Mancozeb (2 g/L) or Fosetyl-Al (2 g/L) immediately.",
                "recommendation_2": "Drain standing water immediately and apply Trichoderma asperellum soil amendment.",
                "chemical_information": "Metalaxyl-M + Mancozeb or Fosetyl-Al control Phytophthora blight effectively.",
                "disclaimer": "Field drainage is essential alongside fungicide sprays."
            },
            "hi": {
                "crop_name": "अरहर / तुअर (Pigeon Pea)",
                "disease_name": "फाइटोफ्थोरा झुलसा (Phytophthora Blight)",
                "description": "भारी बारिश और जलभराव के दौरान तने पर काले कैंकर बनते हैं जिससे पौधा अचानक सूखकर टूट जाता है।",
                "symptoms": [
                    "पत्तियों पर पानीदार धब्बे जो तेजी से झुलस जाते हैं।",
                    "मुख्य तने पर गहरे भूरे या काले रंग के घेरेदार कैंकर।",
                    "पौधा अचानक सूख जाता है लेकिन सूखी पत्तियां तने से जुड़ी रहती हैं।"
                ],
                "prevention": [
                    "उठी हुई क्यारियों (रेज्ड बेड) पर बुआई करें ताकि पानी न ठहरे।",
                    "खेत से जल निकासी की त्वरित व्यवस्था करें।",
                    "मेटालेक्सिल-एम से बीजोपचार करें।"
                ],
                "treatment_or_cure": [
                    "तने पर पानीदार धब्बा दिखते ही कवकनाशी का छिड़काव करें।",
                    "आसपास के स्वस्थ पौधों की जड़ों के पास दवा डालें (ड्रेंचिंग)।"
                ],
                "recovery_period": "जल निकासी और कवकनाशी के साथ 5-10 दिन का त्वरित प्रबंधन आवश्यक है",
                "recommendation_1": "तने पर लक्षण दिखते ही मेटालेक्सिल-एम + मैंकोजेब (2 ग्रा/ली) या फोसेटाइल-एल (2 ग्रा/ली) का छिड़काव करें।",
                "recommendation_2": "खेत में जमा पानी को तुरंत बाहर निकालें और ट्राइकोडर्मा को गोबर की खाद में मिलाकर जमीन में दें।",
                "chemical_information": "मेटालेक्सिल-एम + मैंकोजेब फाइटोफ्थोरा झुलसा पर तुरंत असर दिखाते हैं।",
                "disclaimer": "दवा के साथ-साथ खेत से पानी निकालना अत्यंत आवश्यक है।"
            },
            "mr": {
                "crop_name": "तूर (Pigeon Pea)",
                "disease_name": "फायटोप्थोरा करपा (Phytophthora Blight)",
                "description": "अतिवृष्टी आणि शेतात पाणी साचल्यास खोडावर काळे पाणीदार चट्टे पडून झाडे अचानक वाळतात व खोडातून मोडतात.",
                "symptoms": [
                    "पानांवर पाणीदार डाग पडून पाने वेगाने करपणे.",
                    "खोडावर काळपट तपकिरी रंगाचे कडे तयार होणे.",
                    "झाड अचानक वाळणे पण वाळलेली पाने झाडालाच लटकून राहणे."
                ],
                "prevention": [
                    "गादीवाफ्यावर किंवा बीबीएफ (BBF) पद्धतीने पेरणी करा.",
                    "शेतात पाणी साचणार नाही असा उत्तम निचरा ठेवा.",
                    "मेटॅलॅक्सिल-एम ने बीजप्रक्रिया करा."
                ],
                "treatment_or_cure": [
                    "लक्षणे दिसताच आंतरप्रवाही बुरशीनाशकाची फवारणी व आळवणी करा.",
                    "शेतातील साचलेले पाणी त्वरित बाहेर काढा."
                ],
                "recovery_period": "पाण्याचा निचरा व बुरशीनाशक फवारणीने ५ ते १० दिवसांचे आक्रमक व्यवस्थापन आवश्यक",
                "recommendation_1": "मेटॅलॅक्सिल-एम + मॅन्कोझेब (२ ग्रॅम/लि) किंवा फॉसेटिल-अल (२ ग्रॅम/लि) ची त्वरित फवारणी व खोडाजवळ आळवणी करा.",
                "recommendation_2": "शेतातून पाणी तात्काळ बाहेर काढा आणि जमिनीतून ट्रायकोडर्मा ॲस्परेलम शेणखतातून द्या.",
                "chemical_information": "मेटॅलॅक्सिल-एम + मॅन्कोझेब फायटोप्थोरा करप्यावर अत्यंत प्रभावी ठरते.",
                "disclaimer": "फवारणीसोबत पाण्याचा निचरा करणे अनिवार्य आहे."
            }
        }
    },
    "Pigeon_Pea___Cercospora_leaf_spot": {
        "class_name": "Pigeon_Pea___Cercospora_leaf_spot",
        "crop_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
        "disease_name": "Cercospora Leaf Spot (Cercospora indica)",
        "description": "Cercospora leaf spot creates circular to angular brown lesions with concentric zones on pigeonpea leaves, leading to severe defoliation during humid reproductive stages.",
        "symptoms": [
            "Brown to dark grey necrotic spots on lower and middle leaves.",
            "Concentric rings visible on spots as they enlarge.",
            "Yellowing and premature shedding of infected foliage, impacting pod set."
        ],
        "prevention": [
            "Maintain optimum plant spacing to avoid dense, humid canopies.",
            "Rotate crops with non-hosts like sorghum or pearl millet.",
            "Treat seed with Carbendazim + Mancozeb (2 g/kg seed)."
        ],
        "treatment_or_cure": [
            "Apply foliar protectant fungicides at first sign of leaf spotting.",
            "Ensure lower canopy leaves receive adequate spray penetration."
        ],
        "recovery_period": "10–14 days of canopy management and protective foliar sprays",
        "recommendation_1": "Apply Chlorothalonil 75 WP (0.2% / 2 g/L) or Mancozeb 75 WP (0.2% / 2 g/L) when brown spots appear on lower leaves.",
        "recommendation_2": "Spray Carbendazim 50 WP (0.1% / 1 g/L) or apply botanical neem leaf extract (5%) to slow down spore dispersal.",
        "chemical_information": "Chlorothalonil 75 WP, Mancozeb 75 WP, or Carbendazim 50 WP provide effective control. Ensure 14-day pre-harvest interval.",
        "disclaimer": "Always observe pesticide label directions and wear protective equipment.",
        "translations": {
            "en": {
                "crop_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
                "disease_name": "Cercospora Leaf Spot (Cercospora indica)",
                "description": "Cercospora leaf spot creates circular to angular brown spots on pigeonpea leaves, causing leaf drop.",
                "symptoms": [
                    "Brown to dark grey necrotic spots on lower foliage.",
                    "Concentric rings on enlarging lesions.",
                    "Yellowing and premature defoliation."
                ],
                "prevention": [
                    "Maintain optimum plant spacing.",
                    "Rotate crops with sorghum or pearl millet.",
                    "Treat seeds with Carbendazim + Mancozeb."
                ],
                "treatment_or_cure": [
                    "Apply protectant fungicides upon first spotting.",
                    "Ensure thorough spray penetration into lower canopy."
                ],
                "recovery_period": "10–14 days of canopy management and protective foliar sprays",
                "recommendation_1": "Apply Chlorothalonil 75 WP (2 g/L) or Mancozeb 75 WP (2 g/L) when spots appear.",
                "recommendation_2": "Spray Carbendazim 50 WP (1 g/L) or apply neem leaf extract (5%).",
                "chemical_information": "Chlorothalonil 75 WP or Mancozeb 75 WP provide effective control.",
                "disclaimer": "Follow pesticide label directions and safety guidelines."
            },
            "hi": {
                "crop_name": "अरहर / तुअर (Pigeon Pea)",
                "disease_name": "सर्कोस्पोरा पत्ती धब्बा (Cercospora Leaf Spot)",
                "description": "अरहर की पत्तियों पर भूरे-काले गोल धब्बे बनते हैं जिससे पत्तियां पीली पड़कर गिर जाती हैं और फलियां कम बनती हैं।",
                "symptoms": [
                    "निचली और मध्य पत्तियों पर भूरे से गहरे स्लेटी धब्बे।",
                    "धब्बों के बड़े होने पर संकेंद्री छल्ले दिखते हैं।",
                    "संक्रमित पत्तियां पीली पड़कर समय से पहले गिर जाती हैं।"
                ],
                "prevention": [
                    "पौधों के बीच उचित दूरी रखें ताकि धूप और हवा मिलती रहे।",
                    "ज्वार या बाजरे के साथ फसल चक्र अपनाएं।",
                    "कार्बेन्डाजिम + मैंकोजेब से बीजोपचार करें।"
                ],
                "treatment_or_cure": [
                    "धब्बे दिखने पर सुरक्षात्मक कवकनाशी का छिड़काव करें।",
                    "निचली पत्तियों पर भी दवा का पूरा छिड़काव करें।"
                ],
                "recovery_period": "कवकनाशी छिड़काव और छतरी प्रबंधन के साथ 10-14 दिन का समय लगता है",
                "recommendation_1": "निचली पत्तियों पर धब्बे दिखने पर क्लोरोथैलोनिल 75 WP (2 ग्रा/ली) या मैंकोजेब 75 WP (2 ग्रा/ली) का छिड़काव करें।",
                "recommendation_2": "कार्बेन्डाजिम 50 WP (1 ग्रा/ली) या 5% नीम पत्ती अर्क का छिड़काव करें।",
                "chemical_information": "क्लोरोथैलोनिल 75 WP या मैंकोजेब 75 WP सर्कोस्पोरा धब्बा रोग पर प्रभावी नियंत्रण देते हैं।",
                "disclaimer": "कीटनाशक सुरक्षा निर्देशों का पालन करें।"
            },
            "mr": {
                "crop_name": "तूर (Pigeon Pea)",
                "disease_name": "सार्कोस्पोरा पानांवरील ठिपके (Cercospora Leaf Spot)",
                "description": "तुरीच्या पानांवर तपकिरी-करडे ठिपके पडतात ज्यामुळे पाने पिवळी पडून गळतात आणि शेंगांची संख्या घटते.",
                "symptoms": [
                    "खालच्या व मधल्या पानांवर तपकिरी ते करडे मृत ठिपके.",
                    "ठिपक्यांमध्ये वलयांकित गोल दिसणे.",
                    "पाने पिवळी पडून मुदतीपूर्वीच गळणे."
                ],
                "prevention": [
                    "हवा खेळती राहण्यासाठी झाडांमध्ये योग्य अंतर ठेवा.",
                    "ज्वारी किंवा बाजरी पिकांसोबत फेरपालट करा.",
                    "कार्बेन्डाझिम + मॅन्कोझेबने बीजप्रक्रिया करा."
                ],
                "treatment_or_cure": [
                    "ठिपके दिसताच बुरशीनाशकाची फवारणी करा.",
                    "खालच्या पानांपर्यंत फवारणी पोहोचेल याची काळजी घ्या."
                ],
                "recovery_period": "योग्य बुरशीनाशक फवारणीने १० ते १४ दिवसांचे व्यवस्थापन",
                "recommendation_1": "ठिपके दिसू लागताच क्लोरोथॅलोनिल ७५ डब्ल्यूपी (२ ग्रॅम/लि) किंवा मॅन्कोझेब ७५ डब्ल्यूपी (२ ग्रॅम/लि) फवारा.",
                "recommendation_2": "कार्बेन्डाझिम ५० डब्ल्यूपी (१ ग्रॅम/लि) किंवा कडुलिंबाच्या पानांचा अर्क (५%) फवारा.",
                "chemical_information": "क्लोरोथॅलोनिल किंवा मॅन्कोझेब बुरशीनाशके सार्कोस्पोरा ठिपक्यांवर उपयुक्त आहेत.",
                "disclaimer": "औषध फवारताना योग्य ती काळजी घ्या."
            }
        }
    },
    "Pigeon_Pea___healthy": {
        "class_name": "Pigeon_Pea___healthy",
        "crop_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
        "disease_name": "Healthy Foliage",
        "description": "Pigeonpea plant exhibits healthy, dark green pinnately trifoliate leaves with erect branching and no sterility bushiness, water-soaked stem lesions, or fungal spotting.",
        "symptoms": [
            "Uniform vibrant green trifoliate foliage with clean margins.",
            "Normal upright branching without witch's broom clustering.",
            "Healthy floral racemes and normal pod set."
        ],
        "prevention": [
            "Maintain wide row spacing (90–120 cm) for maximum canopy aeration and light.",
            "Inoculate seeds with Rhizobium and Phosphobacteria (PSB) bio-fertilizers.",
            "Install pheromone traps for Helicoverpa pod borer monitoring."
        ],
        "treatment_or_cure": [
            "Apply foliar nutrient spray (19:19:19 @ 1% or Pulse Wonder @ 2 kg/acre) at peak flowering.",
            "Provide one critical protective irrigation during pod development if dry spell occurs."
        ],
        "recovery_period": "N/A — Foliage is healthy. Maintain regular scouting",
        "recommendation_1": "Maintain proper plant spacing (90x30 cm) for canopy aeration and scout regularly for pod borer and mite vectors.",
        "recommendation_2": "Apply mycorrhizal bio-inoculants to stimulate deep root nodulation and spray 1% water-soluble fertilizer at flowering.",
        "chemical_information": "No chemical fungicides or bactericides required for healthy pigeon pea foliage.",
        "disclaimer": "Regular crop monitoring during flowering and pod development is recommended.",
        "translations": {
            "en": {
                "crop_name": "Pigeon Pea / Red Gram (Cajanus cajan)",
                "disease_name": "Healthy Foliage",
                "description": "Pigeonpea plant exhibits healthy dark green trifoliate foliage without lesions or clustering.",
                "symptoms": [
                    "Vibrant green trifoliate leaves.",
                    "Normal upright branching.",
                    "Healthy flowering and pod setting."
                ],
                "prevention": [
                    "Maintain proper row spacing.",
                    "Inoculate seeds with Rhizobium.",
                    "Deploy pheromone traps for pod borer."
                ],
                "treatment_or_cure": [
                    "Apply foliar nutrient spray at flowering.",
                    "Provide irrigation during pod formation."
                ],
                "recovery_period": "N/A — Foliage is healthy. Maintain regular scouting",
                "recommendation_1": "Maintain proper plant spacing for canopy aeration and scout regularly for vectors.",
                "recommendation_2": "Apply mycorrhizal bio-inoculants and 1% soluble fertilizer at flowering.",
                "chemical_information": "No chemicals needed for healthy foliage.",
                "disclaimer": "Regular crop scouting is recommended."
            },
            "hi": {
                "crop_name": "अरहर / तुअर (Pigeon Pea)",
                "disease_name": "स्वस्थ पत्तियां (Healthy Foliage)",
                "description": "अरहर की पत्तियां पूरी तरह स्वस्थ हैं, जिनमें कोई झाड़ीपन, झुलसा या धब्बे नहीं हैं।",
                "symptoms": [
                    "एकसमान गहरी हरी स्वस्थ पत्तियां।",
                    "शाखाओं का सामान्य सीधा और मजबूत विकास।",
                    "स्वस्थ फूल और फलियों का निर्माण।"
                ],
                "prevention": [
                    "हवा और धूप के लिए कतारों के बीच 90-120 सेमी की दूरी रखें।",
                    "राइजोबियम और पीएसबी से बीजोपचार करें।",
                    "फली छेदक कीट के लिए फेरोमोन ट्रैप लगाएं।"
                ],
                "treatment_or_cure": [
                    "फूल आते समय 1% विद्राव्य उर्वरक (19:19:19) का छिड़काव करें।",
                    "फलियां बनते समय सूखा पड़ने पर एक सुरक्षात्मक सिंचाई दें।"
                ],
                "recovery_period": "लागू नहीं — पत्तियां स्वस्थ हैं। नियमित निरीक्षण जारी रखें",
                "recommendation_1": "हवा के संचार के लिए उचित दूरी बनाए रखें और फली छेदक व माइट कीटों की जांच करते रहें।",
                "recommendation_2": "राइजोबियम जैव-उर्वरक का उपयोग करें और फूल आते समय 1% पानी में घुलनशील खाद का छिड़काव करें।",
                "chemical_information": "स्वस्थ फसल पर किसी कवकनाशी की आवश्यकता नहीं है।",
                "disclaimer": "नियमित निगरानी बनाए रखें।"
            },
            "mr": {
                "crop_name": "तूर (Pigeon Pea)",
                "disease_name": "निरोगी पाने (Healthy Foliage)",
                "description": "तुरीची पाने पूर्णपणे निरोगी असून पानांवर कोणताही वांझपणा, करपा किंवा ठिपक्यांचे डाग नाहीत.",
                "symptoms": [
                    "टवटवीत हिरवीगार तिहेरी पाने.",
                    "फांद्यांची जोमदार सरळ वाढ.",
                    "फुलोरा व शेंगांची उत्तम निरोगी मांडणी."
                ],
                "prevention": [
                    "चांगल्या सूर्यप्रकाशासाठी ओळीत ९० ते १२० सेंमी अंतर ठेवा.",
                    "रायझोबियम आणि पीएसबीची बीजप्रक्रिया करा.",
                    "घाटेअळीच्या नियंत्रणासाठी कामगंध सापळे लावा."
                ],
                "treatment_or_cure": [
                    "फुलोरा अवस्थेत १९:१९:१९ (१%) खताची फवारणी करा.",
                    "शेंगा भरण्याच्या काळात पावसाचा खंड पडल्यास संरक्षक पाणी द्या."
                ],
                "recovery_period": "लागू नाही — पाने निरोगी आहेत. नियमित पाहणी चालू ठेवा",
                "recommendation_1": "बागेत हवा खेळती राहण्यासाठी योग्य अंतर ठेवा आणि घाटेअळी व कोळी किडीवर लक्ष ठेवा.",
                "recommendation_2": "रायझोबियम जैविक खताचा वापर करा आणि फुलोऱ्यात विद्राव्य खतांची फवारणी करा.",
                "chemical_information": "निरोगी पिकावर रासायनिक बुरशीनाशकांची गरज नसते.",
                "disclaimer": "पिकाची नियमित पाहणी करत राहा."
            }
        }
    }
}

def update_disease_info():
    print(f"Reading existing disease info from: {JSON_PATH}")
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Update existing entries
    for cls_name, meta in EXISTING_UPDATES.items():
        if cls_name in data:
            entry = data[cls_name]
            entry["recovery_period"] = meta["recovery_period"]
            entry["recommendation_1"] = meta["recommendation_1"]
            entry["recommendation_2"] = meta["recommendation_2"]

            # Update translations
            trans = entry.setdefault("translations", {})
            for lang in ["en", "hi", "mr"]:
                if lang in trans:
                    if lang == "en":
                        trans[lang]["recovery_period"] = meta["recovery_period"]
                        trans[lang]["recommendation_1"] = meta["recommendation_1"]
                        trans[lang]["recommendation_2"] = meta["recommendation_2"]
                    elif lang in meta:
                        trans[lang]["recovery_period"] = meta[lang]["recovery_period"]
                        trans[lang]["recommendation_1"] = meta[lang]["recommendation_1"]
                        trans[lang]["recommendation_2"] = meta[lang]["recommendation_2"]
            print(f"Updated existing: {cls_name}")

    # Fallback for any other remaining classes in data that weren't in EXISTING_UPDATES
    for cls_name, entry in data.items():
        if "recovery_period" not in entry:
            is_healthy = "healthy" in cls_name.lower()
            if is_healthy:
                rec_period = "N/A — Foliage is healthy. Maintain regular monitoring"
                r1 = "Maintain standard balanced agronomic practices and monitor weekly."
                r2 = "Apply organic compost or bio-fertilizers to sustain vigor and reinforce immunity."
            else:
                rec_period = "7–14 days with proper fungicide/bactericide management"
                r1 = "Apply protective foliar fungicides or bactericides according to product label recommendations."
                r2 = "Prune infected tissue, improve canopy airflow, and apply appropriate biological controls."
            entry["recovery_period"] = rec_period
            entry["recommendation_1"] = r1
            entry["recommendation_2"] = r2
            print(f"Applied default recovery & recommendations to: {cls_name}")

    # 2. Add new 12 classes for Green Gram, Cotton, and Pigeon Pea
    for cls_name, new_entry in NEW_PROFILES.items():
        data[cls_name] = new_entry
        print(f"Added new profile: {cls_name} ({new_entry['crop_name']} - {new_entry['disease_name']})")

    # Save back to JSON
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Successfully updated {JSON_PATH} with {len(data)} total entries!")

if __name__ == "__main__":
    update_disease_info()
