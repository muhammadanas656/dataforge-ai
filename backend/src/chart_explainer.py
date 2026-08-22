CHART_EXPLAINERS = {
    "histogram": {
        "plain_name": "Histogram",
        "simple_definition": "A histogram shows how numeric values are spread across ranges.",
        "why_used": "It is used when we want to understand the distribution of a numeric column.",
        "helps_with": [
            "seeing common value ranges",
            "finding skewed data",
            "spotting unusual values or outliers",
            "understanding whether values are mostly low, medium, or high"
        ],
        "how_to_read": "Each bar represents a range of values. Taller bars mean more rows fall into that range.",
        "best_for": "numeric columns such as price, discount, age, revenue, or quantity",
        "not_best_for": "text columns or columns with categories"
    },

    "bar": {
        "plain_name": "Bar Chart",
        "simple_definition": "A bar chart compares values across categories.",
        "why_used": "It is used when we want to compare groups, categories, or ranked values.",
        "helps_with": [
            "finding the biggest or smallest category",
            "comparing product groups",
            "seeing imbalance between categories",
            "understanding which groups dominate the dataset"
        ],
        "how_to_read": "Each bar represents a category. Taller bars mean a higher count or value.",
        "best_for": "categorical columns such as product category, region, brand, or status",
        "not_best_for": "continuous numeric distributions where a histogram is better"
    },

    "scatter": {
        "plain_name": "Scatter Plot",
        "simple_definition": "A scatter plot shows the relationship between two numeric columns.",
        "why_used": "It is used when we want to see whether two numeric values move together.",
        "helps_with": [
            "finding relationships between two measures",
            "seeing whether one value increases when another increases",
            "spotting clusters",
            "spotting unusual points"
        ],
        "how_to_read": "Each dot is one row. If dots form a pattern, the two columns may be related.",
        "best_for": "two numeric columns, such as price vs discount",
        "not_best_for": "single columns or purely categorical data"
    },

    "table": {
        "plain_name": "Table",
        "simple_definition": "A table shows exact values in rows and columns.",
        "why_used": "It is used when exact numbers matter more than visual pattern recognition.",
        "helps_with": [
            "checking exact values",
            "reviewing ranked results",
            "comparing statistics precisely",
            "validating chart outputs"
        ],
        "how_to_read": "Read each row as one result and each column as a measured value.",
        "best_for": "summaries, rankings, correlation matrices, and audit-style output",
        "not_best_for": "quick visual pattern discovery"
    },

    "box": {
        "plain_name": "Box Plot",
        "simple_definition": "A box plot summarizes the spread of numeric values and highlights outliers.",
        "why_used": "It is used to compare value spread and detect unusual values.",
        "helps_with": [
            "finding outliers",
            "understanding median and spread",
            "comparing numeric values across groups",
            "seeing whether data is tightly or widely spread"
        ],
        "how_to_read": "The box shows the middle range of values. Points far away may be outliers.",
        "best_for": "numeric columns, especially when comparing across categories",
        "not_best_for": "small datasets or text-only columns"
    }
}

def explain_chart(chart_type: str):
    return CHART_EXPLAINERS.get(chart_type, {
        "plain_name": chart_type.title() if chart_type else "Table",
        "simple_definition": "This is a data visualization used to summarize information.",
        "why_used": "It was selected because it matches the structure of the data.",
        "helps_with": ["understanding the data more clearly"],
        "how_to_read": "Read the chart according to its axes and labels.",
        "best_for": "supported data types",
        "not_best_for": "unsupported data types"
    })

def explain_selection(analysis_type: str, chart_type: str, columns: list):
    cols = ", ".join(columns) if columns else "selected features"

    if analysis_type == "numeric_distribution":
        return f"DataForge selected this because '{cols}' is numeric, and numeric columns should be checked for spread, skew, and outliers."

    if analysis_type == "category_breakdown":
        return f"DataForge selected this because '{cols}' is categorical, and category counts help reveal dominant groups or imbalance."

    if analysis_type == "numeric_relationship":
        return f"DataForge selected this because these are numeric columns, and a relationship chart can show whether they move together."

    if analysis_type == "numeric_by_category":
        return f"DataForge selected this because it compares a numeric value across category groups."

    if analysis_type == "correlation":
        return "DataForge selected this because the dataset has multiple numeric columns, so relationships between them can be measured."

    if analysis_type == "top_n":
        return f"DataForge selected this because '{cols}' has many values, so a Top-N view makes the data easier to understand."

    return "DataForge selected this because it appears relevant based on the dataset profile."

def generate_plain_english_takeaway(analysis_type: str, result: dict, columns: list) -> dict:
    """Generate friendly, non-technical definitions and takeaways for non-specialists."""
    stats = result.get("stats", {})
    cols = ", ".join(columns) if columns else "Data"

    if analysis_type == "numeric_distribution":
        mean = stats.get("mean", "N/A")
        median = stats.get("median", "N/A")
        min_v = stats.get("min", "N/A")
        max_v = stats.get("max", "N/A")
        skew = stats.get("skew", 0)
        skew_msg = "values are clustered toward the lower end with some high spikes" if (isinstance(skew, (int, float)) and skew > 0.5) else ("values are clustered toward the higher end" if (isinstance(skew, (int, float)) and skew < -0.5) else "values are fairly evenly balanced around the center")
        return {
            "what_is_this": f"Shows the full spread of numbers and typical ranges for '{cols}'.",
            "plain_meaning": f"On average, '{cols}' is around {mean} (the typical middle value is {median}). Numbers range from a minimum of {min_v} up to {max_v}. Most {skew_msg}.",
            "practical_takeaway": f"Use this to understand typical ranges and detect whether extreme high or low numbers are pulling the averages."
        }

    if analysis_type == "category_breakdown":
        dominant = result.get("statistical_brief", {}).get("dominant_category", "N/A")
        card = stats.get("unique_values", "multiple")
        hhi_status = stats.get("hhi_classification", "Distributed")
        return {
            "what_is_this": f"Counts how many records fall into each category for '{cols}'.",
            "plain_meaning": f"The most dominant group is {dominant}. There are {card} distinct groups in total, and group distribution is {hhi_status.lower()}.",
            "practical_takeaway": f"Focus your attention on the top 2-3 categories which represent the majority of records."
        }

    if analysis_type == "numeric_relationship":
        rho = stats.get("spearman_rho", 0)
        rel = "strong positive link (as one increases, the other usually increases)" if (isinstance(rho, (int, float)) and rho > 0.5) else ("moderate link" if (isinstance(rho, (int, float)) and abs(rho) > 0.2) else "no strong pattern or link")
        return {
            "what_is_this": f"Checks if changing one number affects the other for '{cols}'.",
            "plain_meaning": f"There is a {rel} (correlation score: {rho}). Each dot represents a single row.",
            "practical_takeaway": f"Dots that form a diagonal line suggest predictable trends between both metrics."
        }

    if analysis_type == "numeric_by_category":
        top = result.get("statistical_brief", {}).get("top_group", "N/A")
        return {
            "what_is_this": f"Compares average numbers across different groups ({cols}).",
            "plain_meaning": f"The top performing category is {top}.",
            "practical_takeaway": f"Use this to spot differences between groups, customer segments, or product lines."
        }

    if analysis_type == "correlation":
        strongest = stats.get("strongest_pair", "None")
        max_c = stats.get("max_correlation", 0)
        return {
            "what_is_this": "Compares every numeric column against every other numeric column to find hidden links.",
            "plain_meaning": f"The strongest connection in your data is between {strongest} (score: {max_c}).",
            "practical_takeaway": "Columns with scores close to +1.0 or -1.0 move together and can be used to predict each other."
        }

    if analysis_type == "top_n":
        share = stats.get("top_20_share_pct", "a majority")
        return {
            "what_is_this": f"Ranks the top 20 contributors in '{cols}'.",
            "plain_meaning": f"The top 20 entries account for {share}% of the overall total volume.",
            "practical_takeaway": "Focus your resources on the top contributors who drive the majority of business outcomes."
        }

    return {
        "what_is_this": f"Summarizes data patterns for '{cols}'.",
        "plain_meaning": result.get("insight", "Data patterns detected."),
        "practical_takeaway": "Use these visual patterns to guide operational decisions."
    }
