
from pathlib import Path
import pandas as pd


# =====================================================
# 1. DEFINE PROJECT PATHS
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "original"
    / "September-26-AE-by-provider-B5lUR.xls"
)

OUTPUT_FOLDER = PROJECT_ROOT / "data" / "processed"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# =====================================================
# 2. DEFINE COLUMN NAMES
# =====================================================

COLUMN_NAMES = [
    "Code",
    "Region",
    "Provider_Name",
    "Attendances_Type1",
    "Attendances_Type2",
    "Attendances_Type3",
    "Total_Attendances",
    "Under4h_Type1",
    "Under4h_Type2",
    "Under4h_Type3",
    "Total_Under4h",
    "Over4h_Type1",
    "Over4h_Type2",
    "Over4h_Type3",
    "Total_Over4h",
    "Percent_Within4h_All",
    "Percent_Within4h_Type1",
    "Percent_Within4h_Type2",
    "Percent_Within4h_Type3",
    "Emergency_Admissions_Type1",
    "Emergency_Admissions_Type2",
    "Emergency_Admissions_Type3_4",
    "Total_Emergency_Admissions_via_AE",
    "Other_Emergency_Admissions",
    "Total_Emergency_Admissions",
    "Patients_DTA_Over4h",
    "Patients_DTA_Over12h",
    "System_or_ICB",
]

NUMERIC_COLUMNS = [
    "Attendances_Type1",
    "Attendances_Type2",
    "Attendances_Type3",
    "Total_Attendances",
    "Under4h_Type1",
    "Under4h_Type2",
    "Under4h_Type3",
    "Total_Under4h",
    "Over4h_Type1",
    "Over4h_Type2",
    "Over4h_Type3",
    "Total_Over4h",
    "Percent_Within4h_All",
    "Percent_Within4h_Type1",
    "Percent_Within4h_Type2",
    "Percent_Within4h_Type3",
    "Emergency_Admissions_Type1",
    "Emergency_Admissions_Type2",
    "Emergency_Admissions_Type3_4",
    "Total_Emergency_Admissions_via_AE",
    "Other_Emergency_Admissions",
    "Total_Emergency_Admissions",
    "Patients_DTA_Over4h",
    "Patients_DTA_Over12h",
]


# =====================================================
# 3. LOAD EXCEL DATA
# =====================================================

def load_dataset():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Excel file not found:\n{INPUT_FILE}\n"
            "Check that the file is inside data/original/."
        )

    print("=" * 60)
    print("LOADING EXCEL DATA")
    print("=" * 60)

    # Read without headers because the worksheet contains
    # report titles and grouped headings above the real header.
    raw = pd.read_excel(
        INPUT_FILE,
        sheet_name="Provider Level Data",
        header=None,
    )

    # Remove completely empty columns.
    raw = raw.dropna(axis=1, how="all")

    print("Raw worksheet shape:", raw.shape)

    # Excel row 16 corresponds to Python index 15.
    header_row = raw.iloc[15].tolist()

    if len(header_row) != len(COLUMN_NAMES):
        raise ValueError(
            f"Expected {len(COLUMN_NAMES)} columns, "
            f"but found {len(header_row)} columns after "
            "removing empty columns."
        )

    # Python index 16 starts at Excel row 17.
    # This preserves England's aggregate row.
    df = raw.iloc[16:].copy()
    df.columns = COLUMN_NAMES

    # Remove blank rows.
    df = df.dropna(how="all").reset_index(drop=True)

    print("Loaded dataset shape:", df.shape)

    return df


# =====================================================
# 4. CLEAN TEXT FIELDS
# =====================================================

def clean_text(df):
    print("\n" + "=" * 60)
    print("CLEANING TEXT FIELDS")
    print("=" * 60)

    text_columns = [
        "Code",
        "Region",
        "Provider_Name",
        "System_or_ICB",
    ]

    for column in text_columns:
        df[column] = df[column].apply(
            lambda value: (
                value.replace("\xa0", " ").strip()
                if isinstance(value, str)
                else value
            )
        )

    # Remove whitespace-only strings, if any.
    df[text_columns] = df[text_columns].replace(
        r"^\s*$",
        pd.NA,
        regex=True,
    )

    return df


# =====================================================
# 5. SEPARATE ENGLAND SUMMARY AND PROVIDERS
# =====================================================

def separate_summary(df):
    print("\n" + "=" * 60)
    print("SEPARATING NATIONAL SUMMARY")
    print("=" * 60)

    england_mask = df["Provider_Name"].eq("England")

    england_summary = df.loc[england_mask].copy()
    providers = df.loc[~england_mask].copy()

    if len(england_summary) == 0:
        print("Warning: England summary row was not found.")
    else:
        print("England summary rows:", len(england_summary))

    print("Individual provider rows:", len(providers))

    # Reset indexes for both datasets.
    england_summary = england_summary.reset_index(drop=True)
    providers = providers.reset_index(drop=True)

    return providers, england_summary


# =====================================================
# 6. CONVERT NUMERIC COLUMNS
# =====================================================

def convert_numeric_columns(df):
    print("\n" + "=" * 60)
    print("CONVERTING NUMERIC COLUMNS")
    print("=" * 60)

    for column in NUMERIC_COLUMNS:
        # A dash means unavailable/not applicable in some
        # fields; it must not automatically become zero.
        df[column] = df[column].replace("-", pd.NA)

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    print("Numeric conversion completed.")

    return df


# =====================================================
# 7. CHECK DATA QUALITY
# =====================================================

def check_data_quality(df, dataset_name):
    print("\n" + "=" * 60)
    print(f"DATA QUALITY REPORT: {dataset_name}")
    print("=" * 60)

    print("Dataset shape:", df.shape)

    print("\nColumn data types:")
    print(df.dtypes)

    print("\nMissing values by column:")
    print(df.isnull().sum())

    print("\nTotal missing cells:", int(df.isnull().sum().sum()))

    print("\nDuplicate complete rows:", int(df.duplicated().sum()))

    if "Code" in df.columns:
        print(
            "Missing provider codes:",
            int(df["Code"].isnull().sum()),
        )

    if "Provider_Name" in df.columns:
        print(
            "Missing provider names:",
            int(df["Provider_Name"].isnull().sum()),
        )


# =====================================================
# 8. SAVE PROCESSED DATASETS
# =====================================================

def save_dataset(df, filename):
    output_file = OUTPUT_FOLDER / filename

    df.to_csv(
        output_file,
        index=False,
    )

    print(f"\nSaved successfully:\n{output_file}")


# =====================================================
# 9. MAIN PROGRAM
# =====================================================

def main():
    try:
        # Load source Excel file.
        df = load_dataset()

        # Clean text fields.
        df = clean_text(df)

        # Separate national summary from providers.
        providers, england_summary = separate_summary(df)

        # Convert numeric values in both datasets.
        providers = convert_numeric_columns(providers)

        if not england_summary.empty:
            england_summary = convert_numeric_columns(
                england_summary
            )

        # Generate quality reports.
        check_data_quality(
            providers,
            "Individual Providers",
        )

        if not england_summary.empty:
            check_data_quality(
                england_summary,
                "England Summary",
            )

        # Save cleaned datasets.
        save_dataset(
            providers,
            "providers_cleaned.csv",
        )

        save_dataset(
            england_summary,
            "england_summary.csv",
        )

        # Save the combined cleaned dataset too.
        combined = pd.concat(
            [england_summary, providers],
            ignore_index=True,
        )

        save_dataset(
            combined,
            "provider_level_cleaned.csv",
        )

        # Display a sample of provider data.
        print("\n" + "=" * 60)
        print("FIRST FIVE PROVIDER RECORDS")
        print("=" * 60)

        print(
            providers[
                [
                    "Code",
                    "Region",
                    "Provider_Name",
                    "Total_Attendances",
                    "Total_Under4h",
                    "Total_Over4h",
                    "Percent_Within4h_All",
                ]
            ].head()
        )

        print("\nPreprocessing completed successfully!")

    except FileNotFoundError as error:
        print("\nFILE ERROR:")
        print(error)

    except ValueError as error:
        print("\nDATA FORMAT ERROR:")
        print(error)

    except Exception as error:
        print("\nUNEXPECTED ERROR:")
        print(type(error).__name__, "-", error)


if __name__ == "__main__":
    main()