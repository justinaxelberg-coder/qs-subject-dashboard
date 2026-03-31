"""Shared constants for the QS Subject Rankings dashboard."""

# Target universities — canonical names as they appear in QS data
TARGET_UNIVERSITIES = [
    "Universidade de São Paulo",
    "Universidade Estadual de Campinas (Unicamp)",
    "Universidade Estadual Paulista 'Júlio de Mesquita Filho'",
    "Universidade Federal de São Paulo",
    "Universidade Federal de São Carlos (UFSCar)",
    "Universidade Federal do ABC",
]

# Short display names
UNIVERSITY_SHORT_NAMES = {
    "Universidade de São Paulo": "USP",
    "Universidade Estadual de Campinas (Unicamp)": "UNICAMP",
    "Universidade Estadual Paulista 'Júlio de Mesquita Filho'": "UNESP",
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

# Indicator codes and display names
INDICATOR_NAMES = {
    "AR": "Academic Reputation",
    "ER": "Employer Reputation",
    "CpP": "Citations per Paper",
    "HI": "H-Index",
    "IRN": "International Research Network",
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

# Faculty areas
FACULTY_AREAS = [
    "Arts & Humanities",
    "Engineering & Technology",
    "Life Sciences & Medicine",
    "Natural Sciences",
    "Social Sciences & Management",
]
