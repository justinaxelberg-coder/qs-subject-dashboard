"""Shared constants for the QS Subject Rankings dashboard."""

# Target universities — canonical names as they appear in QS data
TARGET_UNIVERSITIES = [
    "Universidade de São Paulo",
    "Universidade Estadual de Campinas (Unicamp)",
    "UNESP",
    "Universidade Federal de São Paulo",
    "Universidade Federal de São Carlos (UFSCar)",
    "Universidade Federal do ABC",
]

# Short display names
UNIVERSITY_SHORT_NAMES = {
    "Universidade de São Paulo": "USP",
    "Universidade Estadual de Campinas (Unicamp)": "UNICAMP",
    "UNESP": "UNESP",
    "Universidade Federal de São Paulo": "UNIFESP",
    "Universidade Federal de São Carlos (UFSCar)": "UFSCar",
    "Universidade Federal do ABC": "UFABC",
}

# University colors (consistent across all tabs)
UNIVERSITY_COLORS = {
    "USP": "#1f77b4",       # blue
    "UNICAMP": "#2ca02c",   # green
    "UNESP": "#d62728",     # red
    "UNIFESP": "#ff7f0e",   # orange
    "UFSCar": "#9467bd",    # purple
    "UFABC": "#17becf",     # teal
}

# Indicator codes and display names (Brazilian Portuguese)
INDICATOR_NAMES = {
    "AR": "Reputação Acadêmica",
    "ER": "Reputação com Empregadores",
    "CpP": "Citações por Artigo",
    "HI": "Índice H",
    "IRN": "Rede Internacional de Pesquisa",
}

# Indicator colors (matching QS SVG palette)
INDICATOR_COLORS = {
    "AR": "#DE472C",   # red
    "ER": "#FECC01",   # yellow
    "CpP": "#739ED9",  # blue
    "HI": "#F7A70D",   # orange
    "IRN": "#F76000",  # dark orange
}

# Mapping from QS xlsx column headers to indicator codes
QS_COLUMN_TO_INDICATOR = {
    "Academic": "AR",
    "Employer": "ER",
    "Citations": "CpP",
    "H": "HI",
    "International": "IRN",
}

# ── Peer groups for Tab 5 benchmarking ────────────────────────────────────────
# All names are exact matches to QS 2026 xlsx institution column values.

# Chinese C9 League (C9 联盟 — top Chinese research universities)
PEER_GROUP_CHINESE_C9 = [
    "Tsinghua University",
    "Peking University",
    "Fudan University",
    "Shanghai Jiao Tong University",
    "Zhejiang University",
    "Nanjing University",
    "University of Science and Technology of China",
    "Xi\u2019an Jiaotong University",   # U+2019 RIGHT SINGLE QUOTATION MARK as in QS data
    "Harbin Institute of Technology",
]

# Latin American leading institutions
PEER_GROUP_LATIN_AMERICA = [
    "Universidad de Buenos Aires (UBA)",
    "Universidad Nacional Aut\u00f3noma de M\u00e9xico  (UNAM)",  # note double space in QS data
    "Pontificia Universidad Cat\u00f3lica de Chile (UC)",
    "Universidad de Chile",
    "Universidad de los Andes",
    "Universidad Nacional de Colombia",
    "Tecnol\u00f3gico de Monterrey",
]

# Dominant Brazilian institutions outside São Paulo
PEER_GROUP_BRAZIL_LEADERS = [
    "Universidade Federal do Rio de Janeiro",
    "Federal University of Minas Gerais (UFMG)",
    "Universidade Federal do Rio Grande Do Sul",
    "Pontif\u00edcia Universidade Cat\u00f3lica do Rio de Janeiro",
    "Universidade Federal de Santa Catarina",
    "Universidade Federal da Bahia",
    "Universidade de Bras\u00edlia",
    "Universidade Federal Fluminense",
]

# Russell Group (UK research-intensive universities)
PEER_GROUP_RUSSELL = [
    "University of Oxford",
    "University of Cambridge",
    "Imperial College London",
    "UCL",
    "The University of Edinburgh",
    "The University of Manchester",
    "King's College London",
    "The University of Warwick",
    "University of Bristol",
    "University of Leeds",
    "The University of Sheffield",
    "University of Nottingham",
    "University of Birmingham",
    "Durham University",
    "University of Southampton",
    "University of Glasgow",
    "Queen Mary University of London",
    "University of Liverpool",
    "Newcastle University",
    "Cardiff University",
    "Queen's University Belfast",
    "University of Exeter",
]

# Ibero-American (Spain + Portugal)
PEER_GROUP_IBERO = [
    "Complutense University of Madrid",
    "Universidad Aut\u00f3noma de Madrid",
    "Universitat de Barcelona",
    "Universitat Pompeu Fabra (Barcelona)",
    "Universidad Polit\u00e9cnica de Madrid (UPM)",
    "Universitat de Valencia",
    "Universidad de Sevilla",
    "University of Porto",
    "Universidade Nova de Lisboa",
]

# BRICS peers (India, Russia, South Africa — China already in C9)
PEER_GROUP_BRICS = [
    "Indian Institute of Science (IISc) Bangalore",
    "Lomonosov Moscow State University",
    "HSE University",
    "University of Cape Town",
    "Stellenbosch University",
    "University of Witwatersrand",
    "University of Pretoria",
]

# Rising East Asian (Singapore, South Korea, Hong Kong — outside C9)
PEER_GROUP_EAST_ASIAN = [
    "National University of Singapore (NUS)",
    "Nanyang Technological University, Singapore (NTU Singapore)",
    "Seoul National University",
    "Sungkyunkwan University (SKKU)",
    "Pohang University of Science And Technology (POSTECH)",
    "Korea University",
    "Yonsei University",
    "The Hong Kong University of Science and Technology",
    "The Chinese University of Hong Kong (CUHK)",
    "City University of Hong Kong (CityUHK)",
]

PEER_GROUPS = {
    "C9 Chinesas": PEER_GROUP_CHINESE_C9,
    "Líderes Latino-Americanas": PEER_GROUP_LATIN_AMERICA,
    "Líderes Brasileiras (excl. SP)": PEER_GROUP_BRAZIL_LEADERS,
    "Russell Group": PEER_GROUP_RUSSELL,
    "Ibero-Americanas": PEER_GROUP_IBERO,
    "Pares BRICS": PEER_GROUP_BRICS,
    "Leste Asiático em Ascensão": PEER_GROUP_EAST_ASIAN,
}

# Faculty areas
FACULTY_AREAS = [
    "Arts & Humanities",
    "Engineering & Technology",
    "Life Sciences & Medicine",
    "Natural Sciences",
    "Social Sciences & Management",
]
