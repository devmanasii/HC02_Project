
from pathlib import Path
import pandas as pd

out = Path("outputs")
out.mkdir(exist_ok=True)

forecast = pd.read_csv("data/processed/forecast_comparison.csv")
forecast["Month"] = pd.to_datetime(forecast["Month"])

balanced = pd.read_csv(
    "data/processed/balanced_monthly_attendance.csv"
)

seasonal = forecast["Previous_Year_Forecast"]
actual = forecast["Total_AE_Attendances"]
mae = (actual - seasonal).abs().mean()
mape = ((actual - seasonal).abs() / actual).mean() * 100

report = f"""# HC02: Predicting Hospital Demand During Extreme Heat

## Project objective
Analyze monthly A&E attendance, examine its relationship with
temperature, and compare simple demand forecasting baselines.

## Data used
- NHS attendance: January 2025 to August 2026
- Weather: January to December 2025
- Balanced attendance series: 183 providers reporting in all
  20 months
- Weather location: one London-area location

## Forecast evaluation
Evaluation period: March to August 2026

Previous-month baseline:
- MAE: 115,789 attendances
- RMSE: 148,523 attendances
- MAPE: 5.01%

Previous-year seasonal baseline:
- MAE: 105,352 attendances
- RMSE: 107,955 attendances
- MAPE: 4.53%

Seasonal baseline calculated from the saved forecast results:
- MAE: {mae:,.0f} attendances
- MAPE: {mape:.2f}%

## Limitations
- The evaluation covers only six months.
- Weather data covers 2025 only and one London-area location.
- The analysis does not establish that heat causes increased
  hospital attendance.
- This prototype does not yet demonstrate a validated,
  heat-specific prediction model.

## Generated visualizations
- monthly_hospital_demand.png
- actual_vs_forecast.png
- attendance_vs_temperature.png

## Next steps
Obtain geographically representative weather data, incorporate
heatwave indicators, and validate a model using a longer
historical period.
"""

(out / "HC02_Project_Summary.md").write_text(
    report, encoding="utf-8"
)

print("Project summary created: outputs/HC02_Project_Summary.md")