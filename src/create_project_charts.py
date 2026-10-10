
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

# Chart 1: Monthly hospital demand
df = pd.read_csv("data/processed/balanced_monthly_attendance.csv")
df["Month"] = pd.to_datetime(df["Month"])

plt.figure(figsize=(11, 5))
plt.plot(df["Month"], df["Total_AE_Attendances"], marker="o")
plt.title("Monthly A&E Attendance Demand (Jan 2025–Aug 2026)")
plt.xlabel("Month")
plt.ylabel("Total A&E attendances")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / "monthly_hospital_demand.png", dpi=150)
plt.close()

# Chart 2: Actual vs forecast
forecast = pd.read_csv("data/processed/forecast_comparison.csv")
forecast["Month"] = pd.to_datetime(forecast["Month"])

plt.figure(figsize=(10, 5))
plt.plot(forecast["Month"], forecast["Total_AE_Attendances"],
         marker="o", label="Actual demand")
plt.plot(forecast["Month"], forecast["Previous_Month_Forecast"],
         marker="o", linestyle="--", label="Previous-month forecast")
plt.plot(forecast["Month"], forecast["Previous_Year_Forecast"],
         marker="o", linestyle="--", label="Previous-year forecast")
plt.title("Actual vs Forecast A&E Attendance (Mar–Aug 2026)")
plt.xlabel("Month")
plt.ylabel("Total A&E attendances")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / "actual_vs_forecast.png", dpi=150)
plt.close()

# Chart 3: Attendance vs temperature in 2025
analysis = pd.read_csv("data/processed/monthly_analysis_2025.csv")

plt.figure(figsize=(8, 5))
plt.scatter(analysis["Avg_Max_Temp_C"],
            analysis["Total_AE_Attendances"])
plt.xlabel("Average daily maximum temperature (°C)")
plt.ylabel("Total A&E attendances")
plt.title("Monthly Attendance vs Temperature (2025)")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(output_dir / "attendance_vs_temperature.png", dpi=150)
plt.close()

print("Charts created successfully:")
print("outputs/monthly_hospital_demand.png")
print("outputs/actual_vs_forecast.png")
print("outputs/attendance_vs_temperature.png")
