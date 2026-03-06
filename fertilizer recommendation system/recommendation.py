RECOMMENDATIONS = {
    # ── RICE (4 classes) ──────────────────────────────────────────────────────
    "rice_blast":               "Apply Tricyclazole 75WP. Boost potassium and silica.",
    "rice_leaf_blight":         "Apply Copper Oxychloride. Reduce nitrogen.",
    "rice_grain_discoloration": "Apply Propiconazole. Ensure proper drainage.",
    "rice_pesticide_residue":   "Stop pesticide application. Flush field with water.",

    # ── COTTON (5 classes) ────────────────────────────────────────────────────
    "cotton_bacterial_blight":     "Apply Copper-based bactericide. Remove infected leaves.",
    "cotton_leaf_curl_virus":      "No cure — remove infected plants. Apply imidacloprid for whitefly control.",
    "cotton_grey_mildew":          "Apply Carbendazim. Improve air circulation.",
    "cotton_alternaria_leaf_spot": "Apply Mancozeb. Avoid overhead irrigation.",
    "cotton_wilt":                 "Drench soil with Carbendazim. Improve drainage.",

    # ── TOMATO (8 classes) ────────────────────────────────────────────────────
    "tomato_early_blight":          "Apply Chlorothalonil. Mulch around base of plant.",
    "tomato_late_blight":           "Apply Metalaxyl + Mancozeb immediately. Remove infected tissue.",
    "tomato_bacterial_spot":        "Apply Copper Hydroxide. Avoid working in wet conditions.",
    "tomato_septoria_leaf_spot":    "Apply Chlorothalonil or Mancozeb. Remove lower leaves.",
    "tomato_mosaic_virus":          "No cure — remove and destroy infected plants. Control aphids.",
    "tomato_yellow_leaf_curl_virus":"No cure — remove infected plants. Apply thiamethoxam for whitefly.",
    "tomato_leaf_mold":             "Apply Copper Oxychloride. Reduce humidity.",
    "tomato_spider_mite":           "Apply Abamectin or neem oil. Increase humidity.",

    # ── WHEAT (4 classes) ─────────────────────────────────────────────────────
    "wheat_powdery_mildew":      "Apply Tebuconazole. Avoid excess nitrogen.",
    "wheat_septoria_leaf_blotch":"Apply Propiconazole. Remove crop debris after harvest.",
    "wheat_stem_rust":           "Apply Tebuconazole or Propiconazole immediately.",
    "wheat_yellow_rust":         "Apply Tebuconazole. Monitor weekly for spread.",
}

SOURCES = {
    "rice_blast":               "https://katyayanikrishidirect.com/blogs/news/how-azozole-is-the-best-fungicide-for-the-management-of-rice-blast",
    "rice_leaf_blight":         "http://www.pjp.pakps.com/index.php/PJP/article/view/282",
    "rice_grain_discoloration": "https://sataka.com.vn/en/propiconazole-for-treating-rice-seed-deficiency/",
    "rice_pesticide_residue":   "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4053915/",

    "cotton_bacterial_blight":     "https://archive.saulibrary.edu.bd/xmlui/handle/123456789/72",
    "cotton_leaf_curl_virus":      "https://krishibazaar.in/blog/understanding-leaf-curl-virus-key-symptoms-prevention-tips-and-effective-control-methods",
    "cotton_grey_mildew":          "https://ojs.pphouse.org/index.php/IJEP/article/view/4504",
    "cotton_alternaria_leaf_spot": "https://plantix.net/en/library/plant-diseases/100104/alternaria-leaf-spot-of-cotton/",
    "cotton_wilt":                 "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7503036/",

    "tomato_early_blight":          "https://content.ces.ncsu.edu/early-blight-of-tomato",
    "tomato_late_blight":           "https://bioinfopublication.org/include/download.php?id=BIA0006113",
    "tomato_bacterial_spot":        "https://www.sciencedirect.com/science/article/abs/pii/S0261219415300119",
    "tomato_septoria_leaf_spot":    "https://plantpathologyquarantine.org/pdf/PPQ_11_1_19.pdf",
    "tomato_mosaic_virus":          "https://www.missouribotanicalgarden.org/gardens-gardening/your-garden/help-for-the-home-gardener/advice-tips-resources/insects-pests-and-diseases/tobacco-mosaic-virus",
    "tomato_yellow_leaf_curl_virus":"https://content.ces.ncsu.edu/tomato-yellow-leaf-curl-virus",
    "tomato_leaf_mold":             "https://plant-pest-advisory.rutgers.edu/leaf-mold-in-tomato-2-2-2-2-2-2/",
    "tomato_spider_mite":           "https://www.hortidaily.com/article/9462908/efficacy-of-abamectin-against-adult-spider-mite-on-tomato-in-botswana/",

    "wheat_powdery_mildew":      "https://www.magiran.com/paper/2417194/investigation-on-the-efficacy-of-tebuconazole-pyraclostrobin-sc-30-in-controlling-of-powdery-mildew-of-wheat",
    "wheat_septoria_leaf_blotch":"https://ipm.ucanr.edu/agriculture/small-grains/septoria-tritici-blotch-of-wheat/",
    "wheat_stem_rust":           "https://pnwhandbooks.org/plantdisease/host-disease/wheat-triticum-aestivum-stem-rust-black-rust",
    "wheat_yellow_rust":         "https://www.bighaat.com/kisan-vedika/blogs/effective-strategies-for-managing-yellow-rust-disease-in-wheat-crops",
}


def recommend(cls_name: str) -> dict:
    if "healthy" in cls_name:
        return {
            "recommendation": "No treatment needed. Crop looks healthy.",
            "source": None
        }

    return {
        "recommendation": RECOMMENDATIONS.get(cls_name, "Disease identified — consult local agronomist."),
        "source":         SOURCES.get(cls_name, None)
    }