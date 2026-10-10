
import pandas as pd

file = "data/processed/heat_model_data.csv"
df = pd.read_csv(file)

matched = df.dropna(subset=["Avg_Max_Temp_C"]).copy()

print("HEAT MODEL DATA SUMMARY")
print("Total attendance months:", len(df))
print("Months with weather:", len(matched))
print("Months without weather:", df["Avg_Max_Temp_C"].isna().sum())

print("\nMATCHED MONTHS")
print(
    matched[
        [
            "Month",
            "Total_AE_Attendances",
            "Avg_Max_Temp_C",
            "Highest_Temp_C",
            "Hot_Days",
        ]
    ].to_string(index=False)
)

print("\nCORRELATIONS")
print(
    matched[
        [
            "Total_AE_Attendances",
            "Avg_Max_Temp_C",
            "Highest_Temp_C",
            "Hot_Days",
        ]
    ].corr().round(3).to_string()
)

print("\nSaved dataset:")
print(file)