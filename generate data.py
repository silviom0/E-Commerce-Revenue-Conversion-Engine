"""
generate_data.py
Generates a synthetic e-commerce customer interaction dataset (10,000 rows).
Run: python generate_data.py
Output: ecommerce_interactions.csv
"""

import pandas as pd
import numpy as np
np.random.seed(99)
N = 10000
CHANNELS = ["Instagram", "TikTok", "Google Search"]
CHANNEL_WEIGHTS = [0.35, 0.28, 0.37]
# Each channel has different economics
CHANNEL_PARAMS = {
"Instagram": {"cpc": (1.20, 3.50), "cart_mean": 68, "cart_std": 28, "checkout_rate": 0.61},
"TikTok": {"cpc": (0.40, 1.80), "cart_mean": 52, "cart_std": 22, "checkout_rate": 0.58},
"Google Search": {"cpc": (2.50, 6.00), "cart_mean": 91, "cart_std": 35, "checkout_rate": 0.72},
}
customer_ids = [f"CUS-{str(i).zfill(6)}" for i in range(1, N + 1)]
channels = np.random.choice(CHANNELS, size=N, p=CHANNEL_WEIGHTS)
ad_spend, cart_values, checkout_completed, days_as_customer = [], [], [], []
for ch in channels:
p = CHANNEL_PARAMS[ch]
# Ad spend per customer (cost per click range)
spend = round(np.random.uniform(*p["cpc"]) * np.random.randint(1, 6), 2)
ad_spend.append(spend)
# Cart value
cart = round(max(5, np.random.normal(p["cart_mean"], p["cart_std"])), 2)
cart_values.append(cart)
# Checkout: base rate with slight noise
completed = np.random.random() < (p["checkout_rate"] + np.random.normal(0, 0.05))
checkout_completed.append(bool(completed))
# Days as customer (newer customers convert less)
days = int(np.random.exponential(scale=180))

days_as_customer.append(days)
df = pd.DataFrame({
"Customer_ID": customer_ids,
"Acquisition_Channel": channels,
"Ad_Spend": ad_spend,
"Cart_Value": cart_values,
"Checkout_Completed": checkout_completed,
"Days_As_Customer": days_as_customer,
})
# Inject ~2% missing in Ad_Spend and Cart_Value
for col in ["Ad_Spend", "Cart_Value"]:
df.loc[np.random.random(N) < 0.02, col] = np.nan
df.to_csv("ecommerce_interactions.csv", index=False)
print(f"Dataset generated: {len(df)} rows → ecommerce_interactions.csv")
print(df.head())
print(f"\nCheckout rate overall: {df['Checkout_Completed'].mean():.1%}")
print(df["Acquisition_Channel"].value_counts())
