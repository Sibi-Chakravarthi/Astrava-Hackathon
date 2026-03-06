# =============================================================================
# Disease-to-Treatment Recommendation Engine
# Maps detected diseases to actionable farmer advice
# Covers all 23 classes from the ALLINONE dataset
# =============================================================================

DISEASE_INFO = {
    # ===== COTTON DISEASES (6) =====
    "cotton_bacterial_blight": {
        "crop": "Cotton", "disease": "Bacterial Blight",
        "scientific_name": "Xanthomonas citri subsp. malvacearum",
        "description": "Angular, water-soaked spots on leaves that turn brown-black. Boll rot in severe cases.",
        "severity_levels": {
            "low": "Small angular spots on few leaves. Manageable with treatment.",
            "moderate": "Spreading leaf spots with premature defoliation starting.",
            "high": "Severe defoliation and boll infection. Major fiber quality loss."
        },
        "treatment": [
            "Spray Copper Hydroxide (2g/L) or Streptocycline (1g/10L)",
            "Remove and destroy severely infected plant parts",
            "Apply Bordeaux mixture (1%) as preventive spray"
        ],
        "fertilizer": "Apply balanced NPK. Potash (25 kg/acre) to strengthen cell walls.",
        "prevention": "Use acid-delinted and treated seeds. Avoid overhead irrigation."
    },
    "cotton_leaf_curl_virus": {
        "crop": "Cotton", "disease": "Leaf Curl Virus (CLCuV)",
        "scientific_name": "Begomovirus (transmitted by whitefly)",
        "description": "Upward/downward leaf curling, vein thickening, stunted growth, and enations on leaf undersides.",
        "severity_levels": {
            "low": "Mild curling on new leaves. Whitefly population building up.",
            "moderate": "Significant curling and stunting. Yield loss 30-50%.",
            "high": "Severe stunting, no boll formation. Near-total yield loss."
        },
        "treatment": [
            "Control whitefly vectors with Imidacloprid (0.5ml/L) or Thiamethoxam",
            "Apply neem oil (5ml/L) as organic alternative",
            "Install yellow sticky traps (25/acre) for whitefly monitoring"
        ],
        "fertilizer": "Micronutrient spray (Zinc + Boron) to support stressed plants.",
        "prevention": "Plant CLCuV-tolerant varieties (e.g., Bt cotton). Early sowing."
    },
    "cotton_grey_mildew": {
        "crop": "Cotton", "disease": "Grey Mildew (Areolate Mildew)",
        "scientific_name": "Ramularia areola",
        "description": "Pale angular spots on upper leaf surface with whitish-grey powdery growth on the underside.",
        "severity_levels": {
            "low": "Few pale spots on lower leaves. Early detection advantage.",
            "moderate": "Spots spreading to middle canopy. Premature defoliation beginning.",
            "high": "Severe defoliation, reduced boll size and fiber quality."
        },
        "treatment": [
            "Spray Carbendazim (1g/L) or Tridemorph (0.5ml/L)",
            "Apply Wettable Sulphur (3g/L) as contact fungicide",
            "Two sprays at 15-day intervals recommended"
        ],
        "fertilizer": "Balanced NPK with Potash emphasis. Avoid excess nitrogen.",
        "prevention": "Use tolerant varieties. Proper spacing for air circulation."
    },
    "cotton_healthy": {
        "crop": "Cotton", "disease": "Healthy", "scientific_name": "N/A",
        "description": "No disease detected. Cotton crop appears healthy.",
        "severity_levels": {"low": "Crop is in good health.", "moderate": "N/A", "high": "N/A"},
        "treatment": ["Continue regular monitoring", "Maintain current agricultural practices"],
        "fertilizer": "Follow standard fertilizer schedule for growth stage.",
        "prevention": "Monitor for pest vectors. Maintain soil health."
    },
    "cotton_alternaria_leaf_spot": {
        "crop": "Cotton", "disease": "Alternaria Leaf Spot",
        "scientific_name": "Alternaria macrospora",
        "description": "Circular to irregular brown spots with concentric rings on leaves. Causes premature defoliation.",
        "severity_levels": {
            "low": "Few circular spots on older leaves. Minor concern.",
            "moderate": "Spots spreading with defoliation starting. 15-25% yield impact.",
            "high": "Severe defoliation exposing bolls. Major yield and quality loss."
        },
        "treatment": [
            "Spray Mancozeb (2.5g/L) or Copper Oxychloride (3g/L)",
            "Apply Propiconazole (1ml/L) for severe infections",
            "Remove fallen infected leaves from field"
        ],
        "fertilizer": "Balanced NPK. Potash (20 kg/acre) for plant defense.",
        "prevention": "Crop rotation. Remove crop debris. Use healthy seeds."
    },
    "cotton_wilt": {
        "crop": "Cotton", "disease": "Fusarium Wilt",
        "scientific_name": "Fusarium oxysporum f.sp. vasinfectum",
        "description": "Yellowing and wilting of leaves starting from bottom. Brown discoloration in vascular tissue.",
        "severity_levels": {
            "low": "Lower leaf yellowing. Early wilt symptoms in few plants.",
            "moderate": "Half the plant showing wilt. Vascular browning visible.",
            "high": "Entire plant wilted and dying. Soil heavily contaminated."
        },
        "treatment": [
            "Soil drenching with Carbendazim (1g/L) around plant base",
            "Apply Trichoderma viride (2.5 kg/acre) to soil",
            "Remove and destroy completely wilted plants to prevent spread"
        ],
        "fertilizer": "Apply well-decomposed FYM (5 tons/acre). Use Trichoderma-enriched compost.",
        "prevention": "Crop rotation with non-host crops for 3 years. Soil solarization."
    },

    # ===== RICE DISEASES (4) =====
    "rice_grain_discoloration": {
        "crop": "Rice", "disease": "Grain Discoloration",
        "scientific_name": "Multiple fungi (Helminthosporium, Fusarium, Curvularia)",
        "description": "Discolored grains turning brown, black, or pinkish. Reduces grain quality and market value.",
        "severity_levels": {
            "low": "Few discolored grains. Quality mostly unaffected.",
            "moderate": "10-25% grain discoloration. Reduced market grade.",
            "high": "Over 25% discolored. Significant quality and price impact."
        },
        "treatment": [
            "Spray Propiconazole (1ml/L) at flowering stage",
            "Apply Carbendazim (1g/L) at grain filling stage",
            "Proper drying and storage of harvested grain"
        ],
        "fertilizer": "Balanced NPK. Avoid late nitrogen application.",
        "prevention": "Use disease-free seeds. Timely harvesting. Proper field drainage."
    },
    "rice_leaf_blight": {
        "crop": "Rice", "disease": "Bacterial Leaf Blight",
        "scientific_name": "Xanthomonas oryzae",
        "description": "Water-soaked lesions starting from leaf tips, turning yellow-white and drying up.",
        "severity_levels": {
            "low": "Blight on leaf tips only. Early stage, treatable.",
            "moderate": "Lesions extending to mid-leaf. 20-30% yield reduction risk.",
            "high": "Entire leaves wilting. Kresek phase in seedlings. Critical damage."
        },
        "treatment": [
            "Spray Streptomycin sulphate + Tetracycline mixture (300g/acre)",
            "Apply Copper Oxychloride (3g/L) as preventive spray",
            "Drain fields and avoid excess nitrogen fertilization"
        ],
        "fertilizer": "Reduce Urea application. Apply Potash (MOP) - 15 kg/acre.",
        "prevention": "Use BLB-resistant varieties. Avoid clipping leaves during transplanting."
    },
    "rice_pesticide_residue": {
        "crop": "Rice", "disease": "Pesticide Residue Damage",
        "scientific_name": "Phytotoxicity (chemical damage)",
        "description": "Leaf tip burn, browning, or unusual discoloration caused by pesticide overuse or improper application.",
        "severity_levels": {
            "low": "Minor leaf tip burn. Plants will likely recover.",
            "moderate": "Significant browning. Temporary growth reduction.",
            "high": "Widespread chlorosis and necrosis. Yield severely impacted."
        },
        "treatment": [
            "Immediately irrigate to dilute residual chemicals",
            "Apply Gibberellic acid (GA3) to stimulate recovery growth",
            "Spray micronutrient mixture (Zinc + Iron) to aid recovery"
        ],
        "fertilizer": "Foliar spray of 1% Urea + Micronutrients for stress recovery.",
        "prevention": "Follow recommended pesticide dosages. Calibrate sprayers. Avoid spraying in hot midday."
    },
    "rice_blast": {
        "crop": "Rice", "disease": "Rice Blast",
        "scientific_name": "Magnaporthe oryzae",
        "description": "Diamond-shaped lesions on leaves with grey centers and brown borders. Can affect necks and panicles.",
        "severity_levels": {
            "low": "Small isolated lesions on few leaves. Crop can recover with treatment.",
            "moderate": "Lesions spreading across multiple leaves. Yield reduction 15-30% if untreated.",
            "high": "Widespread infection with neck blast. Potential yield loss >50%."
        },
        "treatment": [
            "Apply Tricyclazole (0.6g/L) or Isoprothiolane as foliar spray",
            "Drain excess water from fields to reduce humidity",
            "Apply potassium-rich fertilizers to strengthen plant resistance"
        ],
        "fertilizer": "Potash (MOP) - 20 kg/acre. Avoid excess nitrogen.",
        "prevention": "Use blast-resistant varieties. Maintain proper spacing between plants."
    },

    # ===== TOMATO DISEASES (7) =====
    "tomato_early_blight": {
        "crop": "Tomato", "disease": "Early Blight",
        "scientific_name": "Alternaria solani",
        "description": "Concentric ring pattern ('target spot') lesions on lower leaves. Causes defoliation.",
        "severity_levels": {
            "low": "Few target spots on lower/older leaves. Common and manageable.",
            "moderate": "Lesions spreading upward. 20-30% defoliation.",
            "high": "Severe defoliation exposing fruits to sunscald. Major yield loss."
        },
        "treatment": [
            "Spray Mancozeb (2.5g/L) or Chlorothalonil (2g/L)",
            "Apply Azoxystrobin for resistant strains",
            "Remove and destroy infected lower leaves"
        ],
        "fertilizer": "Calcium Nitrate foliar spray to strengthen cell walls. Standard NPK.",
        "prevention": "Mulching to prevent soil splash. Stake plants for air circulation."
    },
    "tomato_septoria_leaf_spot": {
        "crop": "Tomato", "disease": "Septoria Leaf Spot",
        "scientific_name": "Septoria lycopersici",
        "description": "Small circular spots with dark borders and grey centers on lower leaves. Tiny black dots (pycnidia) visible in centers.",
        "severity_levels": {
            "low": "Spots on lower leaves only. Easily treatable.",
            "moderate": "Spreading to middle canopy. 20-30% defoliation.",
            "high": "Severe defoliation affecting fruit development. Major yield loss."
        },
        "treatment": [
            "Spray Chlorothalonil (2g/L) or Mancozeb (2.5g/L)",
            "Apply Azoxystrobin-based fungicides for resistant strains",
            "Remove and destroy severely infected lower leaves"
        ],
        "fertilizer": "Standard NPK. Calcium-based products to strengthen cell walls.",
        "prevention": "Avoid overhead irrigation. Mulch to reduce soil splash. Crop rotation."
    },
    "tomato_healthy": {
        "crop": "Tomato", "disease": "Healthy", "scientific_name": "N/A",
        "description": "No disease detected. Tomato crop appears healthy.",
        "severity_levels": {"low": "Crop is in good health.", "moderate": "N/A", "high": "N/A"},
        "treatment": ["Continue regular monitoring", "Maintain current agricultural practices"],
        "fertilizer": "Follow standard fertilizer schedule for growth stage.",
        "prevention": "Proper staking and pruning. Monitor soil moisture."
    },
    "tomato_bacterial_spot": {
        "crop": "Tomato", "disease": "Bacterial Spot",
        "scientific_name": "Xanthomonas vesicatoria",
        "description": "Small, dark, water-soaked spots on leaves, stems, and fruits. Spots turn brown and scabby.",
        "severity_levels": {
            "low": "Few spots on leaves. Early detection is key.",
            "moderate": "Spots on leaves and some fruits. Quality affected.",
            "high": "Widespread spotting with fruit lesions. Severe quality loss."
        },
        "treatment": [
            "Spray Copper Hydroxide (2g/L) + Mancozeb (2.5g/L) combination",
            "Apply Streptocycline (1g/10L) for bacterial control",
            "Remove severely infected plants to prevent spread"
        ],
        "fertilizer": "Balanced NPK. Avoid excess nitrogen which promotes soft growth.",
        "prevention": "Use certified disease-free seeds. Avoid working in wet fields."
    },
    "tomato_late_blight": {
        "crop": "Tomato", "disease": "Late Blight",
        "scientific_name": "Phytophthora infestans",
        "description": "Water-soaked dark lesions on leaves and stems. White mold on leaf undersides in humid conditions.",
        "severity_levels": {
            "low": "Small water-soaked spots appearing. Act immediately!",
            "moderate": "Rapidly spreading lesions. Can destroy crop in days if untreated.",
            "high": "Widespread infection with fruit rot. Entire field at risk."
        },
        "treatment": [
            "URGENT: Spray Metalaxyl + Mancozeb (2.5g/L) immediately",
            "Apply Cymoxanil-based fungicides for curative action",
            "Spray every 5-7 days during wet weather"
        ],
        "fertilizer": "Phosphorus-rich fertilizer. Avoid excess nitrogen.",
        "prevention": "Avoid overhead irrigation. Ensure good air circulation. Destroy crop debris."
    },
    "tomato_mosaic_virus": {
        "crop": "Tomato", "disease": "Mosaic Virus (ToMV)",
        "scientific_name": "Tobamovirus",
        "description": "Mottled light and dark green mosaic pattern on leaves. Leaf distortion, stunting, and reduced fruit set.",
        "severity_levels": {
            "low": "Mild mosaic pattern on few leaves. Yield impact minimal.",
            "moderate": "Widespread mosaic with leaf curling. 20-40% yield loss.",
            "high": "Severe stunting and fruit deformation. Major yield loss."
        },
        "treatment": [
            "No chemical cure - remove and destroy infected plants",
            "Disinfect tools with 10% bleach between plants",
            "Control aphid vectors with Imidacloprid (0.3ml/L)"
        ],
        "fertilizer": "Support healthy growth with balanced NPK + micronutrients.",
        "prevention": "Use resistant varieties. Wash hands before handling plants. Control insects."
    },
    "tomato_yellow_leaf_curl_virus": {
        "crop": "Tomato", "disease": "Yellow Leaf Curl Virus (TYLCV)",
        "scientific_name": "Begomovirus (transmitted by whitefly)",
        "description": "Severe upward curling, yellowing of leaf margins, stunted growth, and flower drop.",
        "severity_levels": {
            "low": "Mild curling on newest growth. Whitefly infestation beginning.",
            "moderate": "Pronounced curling and yellowing. Fruit set significantly reduced.",
            "high": "Severe stunting, no harvestable fruit. Remove plants to prevent spread."
        },
        "treatment": [
            "Control whiteflies with Imidacloprid (0.3ml/L) or Spiromesifen",
            "Use reflective silver mulch to repel whiteflies",
            "Remove and destroy severely infected plants"
        ],
        "fertilizer": "Micronutrient spray (Zinc + Iron + Boron) for stressed plants.",
        "prevention": "Use TYLCV-resistant varieties. Install insect-proof mesh. Yellow sticky traps."
    },
    "tomato_leaf_mold": {
        "crop": "Tomato", "disease": "Leaf Mold",
        "scientific_name": "Passalora fulva",
        "description": "Yellow patches on upper leaf surface with olive-green to brown velvety mold underneath.",
        "severity_levels": {
            "low": "Few yellow patches on lower leaves. Humidity likely too high.",
            "moderate": "Mold spreading to middle canopy. Reduce humidity immediately.",
            "high": "Severe mold covering most leaves. Significant yield reduction."
        },
        "treatment": [
            "Improve ventilation in greenhouse/field",
            "Spray Chlorothalonil (2g/L) or Mancozeb",
            "Remove severely infected leaves"
        ],
        "fertilizer": "Standard NPK. Avoid excessive watering.",
        "prevention": "Maintain <85% humidity. Use resistant varieties. Proper plant spacing."
    },
    "tomato_spider_mite": {
        "crop": "Tomato", "disease": "Spider Mite Infestation",
        "scientific_name": "Tetranychus urticae (Two-spotted spider mite)",
        "description": "Fine stippling and yellowing on leaves. Tiny mites and webbing visible on leaf undersides.",
        "severity_levels": {
            "low": "Light stippling on few leaves. Mite population building.",
            "moderate": "Widespread stippling, leaf bronzing. Visible webbing.",
            "high": "Severe bronzing, defoliation. Plant vigor severely affected."
        },
        "treatment": [
            "Spray Abamectin (0.5ml/L) or Spiromesifen (0.8ml/L)",
            "Apply Sulphur-based miticide (3g/L) for organic option",
            "Use strong water spray to dislodge mites from undersides"
        ],
        "fertilizer": "Avoid excess nitrogen which promotes mite-friendly soft growth.",
        "prevention": "Monitor regularly with hand lens. Encourage predatory mites. Avoid dusty conditions."
    },

    # ===== WHEAT DISEASES (4) =====
    "wheat_powdery_mildew": {
        "crop": "Wheat", "disease": "Powdery Mildew",
        "scientific_name": "Blumeria graminis f.sp. tritici",
        "description": "White to grey powdery fungal growth on leaves, stems, and ears. Reduces photosynthesis.",
        "severity_levels": {
            "low": "Small patches on lower leaves. Early stages.",
            "moderate": "Spreading to flag leaf. 15-30% yield reduction possible.",
            "high": "Severe coverage on flag leaf and ear. Significant yield loss."
        },
        "treatment": [
            "Spray Propiconazole (1ml/L) or Tebuconazole (1ml/L)",
            "Apply Sulphur-based fungicide (3g/L) as contact treatment",
            "Two sprays at 15-day intervals recommended"
        ],
        "fertilizer": "Balanced NPK. Avoid excess nitrogen. Apply Potash 20 kg/acre.",
        "prevention": "Use resistant varieties. Proper plant spacing. Avoid late sowing."
    },
    "wheat_septoria_leaf_blotch": {
        "crop": "Wheat", "disease": "Septoria Leaf Blotch",
        "scientific_name": "Zymoseptoria tritici",
        "description": "Irregular tan lesions with dark specks (pycnidia) on lower leaves, progressing upward.",
        "severity_levels": {
            "low": "Lesions confined to lower leaves. Minor impact.",
            "moderate": "Lesions reaching middle canopy. Yield loss 10-25%.",
            "high": "Flag leaf infected. Significant yield and grain quality loss."
        },
        "treatment": [
            "Apply Azoxystrobin + Cyproconazole combination spray",
            "Spray Chlorothalonil (2g/L) as preventive measure",
            "Time fungicide application at flag leaf emergence"
        ],
        "fertilizer": "Standard NPK schedule. Avoid late nitrogen application.",
        "prevention": "Crop rotation with non-cereal crops. Remove crop residues after harvest."
    },
    "wheat_stem_rust": {
        "crop": "Wheat", "disease": "Stem Rust (Black Rust)",
        "scientific_name": "Puccinia graminis f.sp. tritici",
        "description": "Dark reddish-brown pustules on stems and leaf sheaths. Turns black at maturity. Weakens stems.",
        "severity_levels": {
            "low": "Few pustules on lower stems. Early detection advantage.",
            "moderate": "Pustules on multiple stems. Lodging risk increasing.",
            "high": "Heavy infection causing stem weakening and lodging. Devastating yield loss."
        },
        "treatment": [
            "Spray Propiconazole 25% EC (1ml/L) immediately",
            "Apply Tebuconazole (1ml/L) for severe infections",
            "Two sprays at 15-day intervals for best results"
        ],
        "fertilizer": "Balanced NPK. Potash (20 kg/acre) for stem strength.",
        "prevention": "Plant rust-resistant varieties. Early sowing. Eradicate barberry host."
    },
    "wheat_yellow_rust": {
        "crop": "Wheat", "disease": "Yellow Rust (Stripe Rust)",
        "scientific_name": "Puccinia striiformis f.sp. tritici",
        "description": "Yellow-orange pustules arranged in stripes along leaf veins. Favored by cool, moist conditions.",
        "severity_levels": {
            "low": "Few yellow stripes on lower leaves. Act fast!",
            "moderate": "Stripes on flag leaves. 20-40% yield loss if untreated.",
            "high": "Heavy striping on all leaves and ears. Potential crop failure."
        },
        "treatment": [
            "Spray Propiconazole 25% EC (1ml/L) as soon as detected",
            "Apply Tebuconazole + Trifloxystrobin for best curative effect",
            "Repeat spray after 15 days if conditions persist"
        ],
        "fertilizer": "Balanced NPK. Avoid excess nitrogen which makes plants susceptible.",
        "prevention": "Plant stripe rust-resistant varieties. Avoid late sowing. Scout fields regularly."
    },
}


def get_recommendation(disease_key, severity):
    """
    Get full recommendation for a detected disease.
    Args:
        disease_key: The class label from the model
        severity: Severity percentage (0-100)
    Returns:
        Dict with all recommendation info
    """
    key = disease_key.lower().replace(" ", "_").replace("-", "_")
    
    info = DISEASE_INFO.get(key)
    if not info:
        for k, v in DISEASE_INFO.items():
            if key in k or k in key:
                info = v
                break

    if not info:
        return {
            "crop": "Unknown",
            "disease": disease_key,
            "description": "Disease information not available in database.",
            "severity_label": _get_severity_label(severity),
            "severity_percent": severity,
            "treatment": ["Consult local agricultural extension officer"],
            "fertilizer": "Follow standard practices.",
            "prevention": "Regular field monitoring recommended.",
            "is_healthy": False
        }

    severity_label = _get_severity_label(severity)

    return {
        "crop": info["crop"],
        "disease": info["disease"],
        "scientific_name": info.get("scientific_name", ""),
        "description": info["description"],
        "severity_label": severity_label,
        "severity_percent": round(float(severity), 1),
        "severity_description": info["severity_levels"].get(severity_label, ""),
        "treatment": info["treatment"],
        "fertilizer": info["fertilizer"],
        "prevention": info["prevention"],
        "is_healthy": "healthy" in key
    }


def _get_severity_label(severity):
    if severity < 25:
        return "low"
    elif severity < 55:
        return "moderate"
    else:
        return "high"


def get_all_diseases():
    """Get list of all supported diseases for the UI."""
    diseases = []
    for key, info in DISEASE_INFO.items():
        if "healthy" not in key:
            diseases.append({
                "key": key,
                "crop": info["crop"],
                "disease": info["disease"]
            })
    return diseases
