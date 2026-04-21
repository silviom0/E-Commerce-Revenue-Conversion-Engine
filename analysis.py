"""
analysis.py
Loads ecommerce_interactions.csv, cleans data, computes CAC, LTV,
conversion funnel metrics, and exports charts.
Run: python analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")
# ─── 1. LOAD & CLEAN ───────────────────────────────────────────────────────────
df = pd.read_csv("ecommerce_interactions.csv")
print(f"Loaded {len(df)} rows | Missing values:\n{df.isnull().sum()}\n")
df["Ad_Spend"].fillna(df["Ad_Spend"].median(), inplace=True)
df["Cart_Value"].fillna(df["Cart_Value"].median(), inplace=True)
df["Checkout_Completed"] = df["Checkout_Completed"].astype(bool)
# ─── 2. KPI ENGINEERING ────────────────────────────────────────────────────────
# Customer Acquisition Cost = total ad spend / customers who completed checkout
# Lifetime Value proxy = Cart_Value * estimated repeat purchases
df["LTV_Estimate"] = df.apply(
lambda r: r["Cart_Value"] * (1 + r["Days_As_Customer"] / 180) if r["Checkout_Completed"] else 0,
axis=1
).round(2)
# ─── 3. CHANNEL-LEVEL METRICS ──────────────────────────────────────────────────
channel_stats = df.groupby("Acquisition_Channel").agg(
Total_Customers = ("Customer_ID", "count"),
Total_Ad_Spend = ("Ad_Spend", "sum"),
Conversions = ("Checkout_Completed", "sum"),
Avg_Cart_Value = ("Cart_Value", "mean"),
Total_Revenue = ("Cart_Value", lambda x: x[df.loc[x.index, "Checkout_Completed"]].sum()),
Avg_LTV = ("LTV_Estimate", "mean"),
).round(2)
channel_stats["Conversion_Rate_%"] = (
channel_stats["Conversions"] / channel_stats["Total_Customers"] * 100
).round(2)

channel_stats["CAC"] = (
channel_stats["Total_Ad_Spend"] / channel_stats["Conversions"]
).round(2)
channel_stats["AOV"] = (
channel_stats["Total_Revenue"] / channel_stats["Conversions"]
).round(2)
channel_stats["ROAS"] = (
channel_stats["Total_Revenue"] / channel_stats["Total_Ad_Spend"]
).round(2)
print("=== CHANNEL PERFORMANCE METRICS ===")
print(channel_stats[["Total_Customers","Conversions","Conversion_Rate_%",
"CAC","AOV","Avg_LTV","ROAS"]].to_string())
# ─── 4. CHECKOUT DROP-OFF ANALYSIS ─────────────────────────────────────────────
total_sessions = len(df)
added_to_cart = len(df[df["Cart_Value"] > 0])
reached_checkout = int(added_to_cart * 0.85) # 85% reach checkout page
completed = df["Checkout_Completed"].sum()
dropoff_rate = (reached_checkout - completed) / reached_checkout
print(f"\n=== CONVERSION FUNNEL ===")
print(f" Sessions: {total_sessions:,}")
print(f" Added to Cart: {added_to_cart:,} ({added_to_cart/total_sessions:.1%})")
print(f" Reached Checkout: {reached_checkout:,} ({reached_checkout/total_sessions:.1%})")
print(f" Completed: {completed:,} ({completed/total_sessions:.1%})")
print(f" Checkout Drop-off: {dropoff_rate:.1%}")
abandoned_revenue = df.loc[~df["Checkout_Completed"], "Cart_Value"].sum()
print(f" Abandoned cart revenue at risk: £{abandoned_revenue:,.0f}")
# ─── 5. VISUALISATIONS ─────────────────────────────────────────────────────────
plt.style.use("seaborn-v0_8-whitegrid")
FIG_BG = "#FAFAFA"
PALETTE = ["#1A1A1A", "#6B6B6B", "#BDBDBD"]
fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor=FIG_BG)
fig.suptitle("E-Commerce Revenue & Conversion Dashboard",
fontsize=15, fontweight="bold", color="#1A1A1A", y=0.98)
channels = channel_stats.index.tolist()
# Chart 1: CAC vs AOV by channel
ax1 = axes[0, 0]
x = np.arange(len(channels))

w = 0.35
ax1.bar(x - w/2, channel_stats["CAC"], width=w, label="CAC (£)", color=PALETTE[0])
ax1.bar(x + w/2, channel_stats["AOV"], width=w, label="AOV (£)", color=PALETTE[1])
ax1.set_xticks(x); ax1.set_xticklabels(channels, fontsize=9)
ax1.set_ylabel("£"); ax1.set_title("CAC vs Average Order Value", fontweight="bold", fontsize=11)
ax1.legend(fontsize=9)
# Chart 2: Conversion rate by channel
ax2 = axes[0, 1]
bars = ax2.bar(channels, channel_stats["Conversion_Rate_%"], color=PALETTE, edgecolor="none")
ax2.set_ylabel("Conversion Rate (%)"); ax2.set_title("Checkout Conversion Rate by Channel", fontweight="bold", fontsize=11)
ax2.set_ylim(0, 90)
for bar, val in zip(bars, channel_stats["Conversion_Rate_%"]):
ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
f"{val:.1f}%", ha="center", fontsize=10, fontweight="bold", color="#1A1A1A")
# Chart 3: Funnel
ax3 = axes[1, 0]
funnel_labels = ["Sessions", "Added to Cart", "Reached Checkout", "Completed"]
funnel_values = [total_sessions, added_to_cart, reached_checkout, completed]
funnel_colors = ["#D0D0D0", "#A0A0A0", "#606060", "#1A1A1A"]
y_pos = np.arange(len(funnel_labels))
ax3.barh(y_pos, funnel_values, color=funnel_colors, edgecolor="none", height=0.55)
ax3.set_yticks(y_pos); ax3.set_yticklabels(funnel_labels, fontsize=9)
ax3.set_xlabel("Customers"); ax3.set_title("Conversion Funnel", fontweight="bold", fontsize=11)
ax3.invert_yaxis()
for i, v in enumerate(funnel_values):
ax3.text(v + 30, i, f"{v:,}", va="center", fontsize=9, color="#4A4A4A")
# Drop-off annotation
ax3.annotate(f"← {dropoff_rate:.0%} drop-off at checkout",
xy=(reached_checkout, 2.55), fontsize=9, color="#C0392B",
xytext=(reached_checkout - 1500, 2.55))
# Chart 4: ROAS by channel
ax4 = axes[1, 1]
bars4 = ax4.bar(channels, channel_stats["ROAS"], color=PALETTE, edgecolor="none")
ax4.axhline(y=1, color="#C0392B", linestyle="--", linewidth=1, label="Break-even (1×)")
ax4.set_ylabel("ROAS (Revenue / Ad Spend)")
ax4.set_title("Return on Ad Spend by Channel", fontweight="bold", fontsize=11)
ax4.legend(fontsize=9)
for bar, val in zip(bars4, channel_stats["ROAS"]):
ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
f"{val:.1f}×", ha="center", fontsize=10, fontweight="bold", color="#1A1A1A")
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("ecommerce_dashboard.png", dpi=150, bbox_inches="tight", facecolor=FIG_BG)
plt.close()

print("\nChart saved → ecommerce_dashboard.png")
# ─── 6. EXPORT ─────────────────────────────────────────────────────────────────
df.to_csv("ecommerce_interactions_clean.csv", index=False)
channel_stats.to_csv("channel_summary.csv")
print("Exports done.")
