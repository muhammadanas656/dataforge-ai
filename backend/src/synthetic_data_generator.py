"""Generates realistic, intentionally messy unit economics data for the DataForge cleaning pipeline."""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
from typing import Optional, Dict
from src.utils import logger

CUSTOMER_SEGMENTS = {
    'DTC_New': {
        'weight': 0.35,
        'cogs_range': (25, 40),
        'margin_multiplier': (2.8, 4.0),
        'volume_range': (50, 200),
        'cac_multiplier': (0.25, 0.40)
    },
    'DTC_Returning': {
        'weight': 0.25,
        'cogs_range': (25, 40),
        'margin_multiplier': (3.0, 4.5),
        'volume_range': (80, 300),
        'cac_multiplier': (0.05, 0.15)
    },
    'Wholesale': {
        'weight': 0.20,
        'cogs_range': (15, 25),
        'margin_multiplier': (1.8, 2.2),
        'volume_range': (300, 800),
        'cac_multiplier': (0.08, 0.18)
    },
    'Amazon_FBA': {
        'weight': 0.15,
        'cogs_range': (20, 35),
        'margin_multiplier': (2.5, 3.5),
        'volume_range': (100, 400),
        'cac_multiplier': (0.0, 0.0)
    },
    'Subscription': {
        'weight': 0.05,
        'cogs_range': (10, 20),
        'margin_multiplier': (4.0, 6.0),
        'volume_range': (30, 150),
        'cac_multiplier': (0.30, 0.50)
    }
}

def generate_realistic_unit_economics(
    niche: str,
    n_months: int = 12,
    rows_per_month: int = 15,
    inject_quality_issues: bool = True,
    seasonality_strength: float = 1.5
) -> pd.DataFrame:
    """Generate realistic unit economics data with intentional data quality issues."""
    logger.info(f"[synthetic_data] Generating {n_months} months of data for '{niche}'")
    
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=n_months, freq='ME')
    
    data = []
    sku_counter = 1000
    
    for month_idx, month in enumerate(dates):
        if month.month in [10, 11, 12]:
            seasonality = seasonality_strength
        elif month.month in [6, 7, 8]:
            seasonality = 0.8
        else:
            seasonality = 1.0
        
        trend_multiplier = 1 + (month_idx * 0.02)
        
        for _ in range(rows_per_month):
            segment = np.random.choice(
                list(CUSTOMER_SEGMENTS.keys()),
                p=[s['weight'] for s in CUSTOMER_SEGMENTS.values()]
            )
            segment_config = CUSTOMER_SEGMENTS[segment]
            
            cogs_min, cogs_max = segment_config['cogs_range']
            cogs = np.random.triangular(cogs_min, (cogs_min + cogs_max) / 2, cogs_max)
            
            margin_min, margin_max = segment_config['margin_multiplier']
            margin = np.random.uniform(margin_min, margin_max)
            retail = cogs * margin
            
            vol_min, vol_max = segment_config['volume_range']
            base_volume = np.random.uniform(vol_min, vol_max)
            volume = max(1, int(base_volume * seasonality * trend_multiplier))
            
            cac_min, cac_max = segment_config['cac_multiplier']
            cac = retail * np.random.uniform(cac_min, cac_max)
            
            amazon_fee = 0.0
            if segment == 'Amazon_FBA':
                amazon_referral = retail * 0.15
                fulfillment_fee = np.random.uniform(3.5, 8.5)
                amazon_fee = amazon_referral + fulfillment_fee
            
            revenue = retail * volume
            total_cogs = cogs * volume
            total_cac = cac * volume
            gross_profit = revenue - total_cogs
            net_profit = gross_profit - total_cac - (amazon_fee * volume if segment == 'Amazon_FBA' else 0)
            
            sku = f"SKU-{sku_counter}"
            sku_counter += np.random.randint(1, 5)
            
            product_variant = np.random.choice(['Standard', 'Premium', 'Deluxe', 'Basic', 'Pro'])
            product_name = f"{niche} - {product_variant}"
            
            data.append({
                'month': month,
                'segment': segment,
                'product_name': product_name,
                'sku': sku,
                'cogs_usd': round(float(cogs), 2),
                'retail_price_usd': round(float(retail), 2),
                'units_sold': int(volume),
                'customer_acquisition_cost': round(float(cac), 2),
                'amazon_fee_usd': round(float(amazon_fee), 2) if segment == 'Amazon_FBA' else 0.0,
                'revenue_usd': round(float(revenue), 2),
                'gross_profit_usd': round(float(gross_profit), 2),
                'net_profit_usd': round(float(net_profit), 2)
            })
    
    df = pd.DataFrame(data)
    if inject_quality_issues:
        df = _inject_quality_issues(df)
    return df

def _inject_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n_rows = len(df)
    if n_rows < 10:
        return df
    
    # 1. Duplicates (~8%)
    n_dupes = max(1, int(n_rows * 0.08))
    dupe_indices = np.random.choice(df.index, size=n_dupes, replace=False)
    dupes = df.loc[dupe_indices].copy()
    df = pd.concat([df, dupes], ignore_index=True)
    
    # 2. Negative CAC (~3%)
    n_negative_cac = max(1, int(len(df) * 0.03))
    neg_cac_indices = np.random.choice(df.index, size=n_negative_cac, replace=False)
    df.loc[neg_cac_indices, 'customer_acquisition_cost'] *= -1
    
    # 3. Missing SKU (~5%)
    n_missing_sku = max(1, int(len(df) * 0.05))
    missing_sku_indices = np.random.choice(df.index, size=n_missing_sku, replace=False)
    df.loc[missing_sku_indices, 'sku'] = np.nan
    
    # 4. Outlier prices (~5%)
    n_outliers = max(1, int(len(df) * 0.05))
    outlier_indices = np.random.choice(df.index, size=n_outliers, replace=False)
    for idx in outlier_indices:
        df.loc[idx, 'retail_price_usd'] *= 10 if np.random.random() > 0.5 else 0.1
    
    # 5. Inconsistent product names
    n_inconsistent = max(1, int(len(df) * 0.07))
    inconsistent_indices = np.random.choice(df.index, size=n_inconsistent, replace=False)
    for idx in inconsistent_indices:
        current = str(df.loc[idx, 'product_name'])
        df.loc[idx, 'product_name'] = current.upper() if idx % 2 == 0 else current.lower()
    
    return df

def generate_comprehensive_unit_economics(
    niche: str,
    include_customer_data: bool = True,
    include_cohort_data: bool = True,
    n_rows: int = 200
) -> Dict[str, pd.DataFrame]:
    datasets = {}
    datasets['unit_economics'] = generate_realistic_unit_economics(
        niche=niche,
        n_months=12,
        rows_per_month=15,
        inject_quality_issues=True
    )
    if include_customer_data:
        datasets['customers'] = _generate_customer_data(n_customers=100)
    if include_cohort_data:
        datasets['cohorts'] = _generate_cohort_data(n_cohorts=12)
    return datasets

def _generate_customer_data(n_customers: int = 100) -> pd.DataFrame:
    data = []
    channels = {
        'Organic_Search': {'weight': 0.30, 'cac': (5, 20)},
        'Paid_Social': {'weight': 0.25, 'cac': (15, 45)},
        'Paid_Search': {'weight': 0.20, 'cac': (20, 50)},
        'Email_Marketing': {'weight': 0.15, 'cac': (2, 10)},
        'Referral': {'weight': 0.10, 'cac': (5, 15)}
    }
    for i in range(n_customers):
        channel = np.random.choice(list(channels.keys()), p=[c['weight'] for c in channels.values()])
        c_min, c_max = channels[channel]['cac']
        cac = round(float(np.random.uniform(c_min, c_max)), 2)
        ltv = round(float(cac * np.random.uniform(2.5, 7.5)), 2)
        n_orders = int(np.random.poisson(3) + 1)
        days_since = int(np.random.randint(5, 360))
        is_churned = int(np.random.random() < 0.25)
        
        data.append({
            'customer_id': f"CUST-{1000 + i}",
            'acquisition_channel': channel,
            'cac_usd': cac,
            'lifetime_value_usd': ltv,
            'ltv_cac_ratio': round(ltv / max(cac, 1), 2),
            'total_orders': n_orders,
            'days_since_acquisition': days_since,
            'is_churned': is_churned,
            'acquisition_date': (datetime.now() - timedelta(days=days_since)).strftime('%Y-%m-%d')
        })
    df = pd.DataFrame(data)
    return df

def _generate_cohort_data(n_cohorts: int = 12) -> pd.DataFrame:
    data = []
    for cohort_idx in range(n_cohorts):
        cohort_month = datetime.now() - timedelta(days=30 * (n_cohorts - cohort_idx))
        cohort_size = int(np.random.uniform(50, 200))
        retention_rates = {0: 1.0, 1: 0.52, 2: 0.41, 3: 0.33, 6: 0.24, 12: 0.15}
        for month_offset, base_rate in retention_rates.items():
            rate = max(0.0, min(1.0, base_rate + np.random.uniform(-0.04, 0.04)))
            data.append({
                'cohort_month': cohort_month.strftime('%Y-%m'),
                'cohort_size': cohort_size,
                'month_offset': month_offset,
                'retained_customers': int(cohort_size * rate),
                'retention_rate': round(float(rate), 3)
            })
    return pd.DataFrame(data)
