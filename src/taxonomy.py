"""
Simplified IPTC Media Topics taxonomy for NewsTagger .
- Categories in English (IPTC-like).
- Keywords in Spanish, English, Portuguese (accent-free where possible).
- STRONG_KEYWORDS: if any appears in title/description, allow 1-hit classification.
"""

from typing import Dict, List

DEFAULT_CATEGORY = "General"

# -------- Strong signals per category (single hit can be enough) --------
STRONG_KEYWORDS: Dict[str, List[str]] = {
    "Politics": [
        # ES
        "balotaje", "segunda vuelta", "encuesta electoral", "decreto ley",
        "boleta unica", "candidato presidencial", "gira presidencial",
        # EN
        "runoff", "ballot", "election runoff", "presidential candidate",
        "executive order",
        # PT
        "segundo turno", "urna", "candidato presidencial", "medida provisoria"
    ],
    "Economy": [
        # ES
        "inflacion", "recesion", "estanflacion", "devaluacion",
        "banco central", "tasas de interes", "riesgo pais", "salario minimo",
        "indice de precios", "suba de precios", "canasta basica",
        # EN
        "inflation", "recession", "stagflation", "devaluation",
        "central bank", "interest rate", "cpi", "ppi", "minimum wage",
        # PT
        "inflacao", "recessao", "desvalorizacao", "banco central",
        "taxa de juros", "salario minimo", "ipca"
    ],
    "Business": [
        # ES
        "adquisicion", "fusion", "oferta publica", "opa", "salida a bolsa",
        "resultados trimestrales", "facturacion", "ingresos record",
        "ronda de financiacion", "capital de riesgo", "despidos masivos",
        # EN
        "acquisition", "merger", "ipo", "earnings", "quarterly results",
        "revenue record", "venture capital", "layoffs",
        # PT
        "fusao", "aquisicao", "ipo", "resultados trimestrais",
        "receita recorde", "demissoes"
    ],
    "Technology": [
        # ES
        "inteligencia artificial", "ia", "machine learning", "ciberataque",
        "filtracion de datos", "chip", "semiconductor", "app",
        "redes sociales",
        # EN
        "artificial intelligence", "ai", "machine learning", "cyberattack",
        "data breach", "chip", "semiconductor", "app", "social media",
        # PT
        "inteligencia artificial", "ia", "aprendizado de maquina",
        "ataque cibernetico", "vazamento de dados", "semicondutor", "aplicativo"
    ],
    "Health": [
        # ES
        "brote", "dengue", "covid", "gripe", "vacunacion", "alerta sanitaria",
        # EN
        "outbreak", "covid", "flu", "vaccination", "health alert",
        # PT
        "surto", "dengue", "covid", "gripe", "vacinacao", "alerta sanitario"
    ],
    "Sports": [
        # ES
        "partido", "victoria", "derrota", "marcador", "final", "semifinal",
        "copa america", "mundial", "libertadores",
        # EN
        "match", "win", "loss", "score", "final", "semifinal",
        "world cup",
        # PT
        "partida", "vitoria", "derrota", "placar", "final", "semifinal"
    ],
    "Environment": [
        # ES
        "ola de calor", "incendio forestal", "sequía", "inundacion",
        "contaminacion", "emisiones", "deforestacion",
        # EN
        "heat wave", "wildfire", "drought", "flood", "pollution",
        "emissions", "deforestation",
        # PT
        "onda de calor", "incendio florestal", "seca", "enchente",
        "poluicao", "emissoes", "desmatamento"
    ],
    "Culture/Entertainment": [
        # ES
        "estreno", "taquilla", "concierto", "festival", "gira",
        # EN
        "premiere", "box office", "concert", "festival", "tour",
        # PT
        "estreia", "bilheteria", "show", "festival", "turne"
    ],
    "Crime/Law": [
        # ES
        "detencion", "allanamiento", "condena", "juicio oral",
        "investigacion fiscal", "lavado de dinero",
        # EN
        "arrest", "raid", "conviction", "indictment", "money laundering",
        # PT
        "prisao", "busca e apreensao", "condenacao", "acusacao",
        "lavagem de dinheiro"
    ],
}

# -------- Broad keyword lists (2 hits recommended) --------
TAXONOMY: Dict[str, List[str]] = {
    "Politics": [
        # ES
        "presidente", "gobierno", "ministro", "asamblea", "congreso",
        "parlamento", "elecciones", "votacion", "reforma", "decreto",
        "partido", "candidato", "campana", "encuesta", "senado",
        # EN
        "president", "government", "minister", "congress", "parliament",
        "election", "policy", "reform", "decree", "party",
        "candidate", "campaign", "senate", "poll",
        # PT
        "presidente", "governo", "ministro", "eleicao", "parlamento",
        "reforma", "partido", "candidato", "campanha", "senado"
    ],
    "Economy": [
        # ES
        "inflacion", "pib", "tasa de interes", "mercado", "deficit",
        "exportaciones", "importaciones", "dolar", "tipo de cambio",
        "desempleo", "impuestos", "tarifas", "deuda",
        # EN
        "inflation", "gdp", "interest rate", "market", "deficit",
        "exports", "imports", "dollar", "unemployment",
        "taxes", "tariffs", "debt", "trade balance",
        # PT
        "economia", "inflacao", "juros", "mercado", "pib",
        "desemprego", "impostos", "tarifas", "divida"
    ],
    "Business": [
        # ES
        "empresa", "negocio", "ingresos", "utilidades", "ganancias",
        "adquisicion", "fusion", "acuerdo", "contrato", "inversion",
        "ventas", "facturacion", "proveedores",
        # EN
        "company", "business", "earnings", "profits", "merger",
        "acquisition", "deal", "contract", "investment", "startup",
        "sales", "revenue", "supplier",
        # PT
        "empresa", "negocios", "lucros", "fusao", "aquisicao",
        "investimento", "vendas", "receita", "fornecedor"
    ],
    "Technology": [
        # ES
        "tecnologia", "software", "ciberseguridad", "plataforma",
        "algoritmo", "nube", "datos", "chip", "semiconductores",
        "inteligencia artificial", "ia", "aplicacion", "redes sociales",
        # EN
        "technology", "software", "cybersecurity", "platform",
        "algorithm", "cloud", "data", "chip", "semiconductor",
        "artificial intelligence", "ai", "app", "social media",
        # PT
        "tecnologia", "dados", "seguranca cibernetica", "plataforma",
        "inteligencia artificial", "aplicativo", "rede social"
    ],
    "Health": [
        # ES
        "salud", "hospital", "vacuna", "virus", "pandemia", "brote",
        "salud publica", "epidemia", "dengue", "covid", "gripe",
        # EN
        "health", "hospital", "vaccine", "virus", "pandemic", "outbreak",
        "public health", "epidemic", "covid", "flu",
        # PT
        "saude", "hospital", "vacina", "virus", "pandemia",
        "surto", "covid", "gripe"
    ],
    "Sports": [
        # ES
        "deporte", "futbol", "baloncesto", "tenis", "copa",
        "liga", "equipo", "campeonato", "mundial", "goles",
        "partido", "marcador", "victoria", "derrota",
        # EN
        "sports", "football", "soccer", "basketball", "tennis",
        "cup", "league", "team", "championship", "world cup",
        "match", "score", "win", "loss",
        # PT
        "futebol", "time", "campeonato", "gol", "partida",
        "placar", "vitoria", "derrota"
    ],
    "Environment": [
        # ES
        "medioambiente", "clima", "cambio climatico", "emisiones",
        "co2", "deforestacion", "contaminacion", "biodiversidad",
        "huracan", "sequía", "inundacion", "incendio",
        # EN
        "environment", "climate", "climate change", "emissions",
        "co2", "deforestation", "pollution", "biodiversity",
        "hurricane", "drought", "flood", "wildfire",
        # PT
        "meio ambiente", "clima", "emissoes", "desmatamento",
        "poluicao", "biodiversidade", "seca", "enchente", "incendio"
    ],
    "Culture/Entertainment": [
        # ES
        "cultura", "cine", "pelicula", "musica", "arte", "teatro",
        "festival", "celebridad", "entretenimiento", "serie",
        "estreno", "taquilla", "concierto", "gira",
        # EN
        "culture", "cinema", "movie", "music", "art", "theater",
        "festival", "celebrity", "entertainment", "series",
        "premiere", "box office", "concert", "tour",
        # PT
        "cultura", "cinema", "filme", "musica", "arte", "festival",
        "estreia", "bilheteria", "show", "turne"
    ],
    "Crime/Law": [
        # ES
        "crimen", "delito", "arresto", "homicidio", "narcotrafico",
        "tribunal", "juzgado", "sentencia", "juicio",
        "corrupcion", "fiscalia", "policia", "allanamiento",
        # EN
        "crime", "arrest", "homicide", "court", "trial", "sentence",
        "corruption", "prosecutor", "police", "raid",
        # PT
        "crime", "prisao", "homicidio", "tribunal", "corrupcao",
        "policia", "busca e apreensao"
    ],
}
 