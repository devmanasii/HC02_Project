
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

input_file = Path("data/processed/heat_model_predictions.csv")
output_dir = Path("outputs")
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file)
df["Month"] = pd.to_datetime(df["Month"])

plt.figure(figsize=(10, 6))

plt.plot(
    df["Month"],
    df["Total_AE_Attendances"],
    marker="o",
    label="Actual Attendance"
)

plt.plot(
    df["Month"],
    df["Heat_Model_Prediction"],
    marker="s",
    label="Heat Model"
)

plt.plot(
    df["Month"],
    df["Previous_Month_Baseline"],
    marker="^",
    label="Previous-Month Baseline"
)

plt.title("Actual vs Predicted Hospital Demand")
plt.xlabel("Month")
plt.ylabel("Total A&E Attendances")
plt.xticks(df["Month"], df["Month"].dt.strftime("%b %Y"), rotation=30)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

output_file = output_dir / "heat_model_comparison.png"
plt.savefig(output_file, dpi=300)
plt.show()

print(f"Chart saved: {output_file}")

