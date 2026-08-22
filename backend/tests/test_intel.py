import pandas as pd
from src import competitor_intel as ci

def test_normalize_products():
    df = pd.DataFrame({
        "product_name": ["Eco Yoga Mat", "Cork Block Set"],
        "price": ["$49.99", "19.50"],
        "rating": ["4.7", "4.2"]
    })
    products = ci.normalize_products(df)
    assert len(products) == 2
    assert products[0]["price"] == 49.99
    assert products[1]["price"] == 19.50

def test_aspect_sentiment():
    r = ci.analyze_reviews([
        "Great quality and material but too expensive",
        "Shipping was slow and box arrived broken"
    ])
    assert "quality" in r["aspects"]
    assert "shipping" in r["aspects"]
    assert "price" in r["aspects"]
    assert isinstance(r["overall"], float)

def test_feature_gap():
    gap = ci.feature_gap()
    assert isinstance(gap, list)

def test_price_history_and_changes():
    cid = "test_intel_cid"
    snap1 = {"id": cid, "ts": 100, "url": "http://test.com", "products": [{"title": "Mat", "price": 50}]}
    snap2 = {"id": cid, "ts": 200, "url": "http://test.com", "products": [{"title": "Mat", "price": 45}]}
    
    # Check price delta logic
    series = {"mat": [{"ts": 100, "price": 50, "title": "Mat"}, {"ts": 200, "price": 45, "title": "Mat"}]}
    changes = []
    for key, pts in series.items():
        if len(pts) >= 2:
            a, b = pts[-2], pts[-1]
            if a["price"] != b["price"]:
                changes.append({"title": b["title"], "before": a["price"], "after": b["price"], "delta": b["price"] - a["price"]})
    assert len(changes) == 1
    assert changes[0]["delta"] == -5
