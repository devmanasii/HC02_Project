
from pathlib import Path
import pandas as pd

file = Path("data/original/September-26-AE-by-provider-B5lUR.xls")

# Inspect the main provider-level worksheet
df = pd.read_excel(
    file,
    sheet_name="Provider Level Data",
    header=None
)

print("Shape:", df.shape)
print("\nFirst 25 rows:")
print(df.head(25).to_string(index=False, header=False))

print("\nNon-empty cells in the first 15 rows:")
for i in range(min(15, len(df))):
    values = df.iloc[i].dropna().astype(str).tolist()
    print(f"Row {i}: {values}")