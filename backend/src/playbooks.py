PLAYBOOKS = {
    "e-commerce": {
        "kpis": ["AOV", "discount_rate", "category_concentration"],
        "checks": ["price>0", "discount in [0,100]", "duplicate orders"],
        "charts": ["category bar", "discount distribution", "price histogram"]
    },
    "sports-retail": {
        "kpis": ["category_revenue", "discount_depth", "premium_tail_share"],
        "checks": ["price>0", "discount in [0,100]", "low-cardinality category col"],
        "charts": ["category bar", "price histogram", "price-vs-discount scatter"]
    },
    "finance": {
        "kpis": ["avg_balance", "delinquency_rate"],
        "checks": ["no negative balances", "amount outliers"],
        "charts": ["balance histogram", "segment bar"]
    },
    "healthcare": {
        "kpis": ["missing_rate_critical", "readmission_rate"],
        "checks": ["critical fields not null", "heavy PII"],
        "charts": ["missing heatmap", "outcome bar"]
    },
    "telecom": {
        "kpis": ["churn_rate", "tenure_distribution"],
        "checks": ["tenure>=0", "monthly_charges>0"],
        "charts": ["churn bar", "tenure histogram"]
    },
    "education": {
        "kpis": ["pass_rate", "attendance"],
        "checks": ["scores in range", "id columns"],
        "charts": ["score histogram", "group bar"]
    },
    "generic": {
        "kpis": ["completeness", "uniqueness", "spread"],
        "checks": ["nulls", "duplicates", "outliers"],
        "charts": ["distribution", "category bar", "correlation"]
    }
}

def get_playbook(domain):
    return PLAYBOOKS.get(domain, PLAYBOOKS["generic"])
