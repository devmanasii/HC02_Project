
import pandas as pd

file_path = "data/processed/nhs_monthly_cleaned.csv"
df = pd.read_csv(file_path)

print("DATASET SHAPE")
print(df.shape)

print("\nMONTHS AVAILABLE")
print(df["Period"].value_counts().sort_index().to_string())

print("\nCOLUMN DATA TYPES")
print(df.dtypes.to_string())

attendance_columns = [
    "A&E attendances Type 1",
    "A&E attendances Type 2",
    "A&E attendances Other A&E Department",
]

print("\nATTENDANCE SUMMARY")
print(df[attendance_columns].describe().round(2).to_string())

print("\nMISSING VALUES IN ATTENDANCE COLUMNS")
print(df[attendance_columns].isna().sum().to_string())

print("\nSAMPLE RECORDS")
print(
    df[["Period", "Org Code", "Org name"] + attendance_columns]
    .head(10)
    .to_string(index=False)
)