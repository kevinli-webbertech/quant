import pandas as pd
import os


def load_taxonomy_mapping(mapping_file='chunks/nucc_taxonomy_241.csv'):
    print("Loading taxonomy mapping from:", mapping_file)
    if not os.path.exists(mapping_file):
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
    taxonomy_df = pd.read_csv(mapping_file)
    print("Mapping file loaded. Columns:", taxonomy_df.columns.tolist())
    # Create a dictionary mapping 'Code' to 'Display Name'
    taxonomy_dict = dict(zip(taxonomy_df['Code'], taxonomy_df['Display Name']))
    return taxonomy_dict


def process_npi_file(raw_file='chunks/npidata_pfile_20050523-20250112.csv', output_file='processed_npi.csv'):
    print("Loading raw file from:", raw_file)
    if not os.path.exists(raw_file):
        raise FileNotFoundError(f"Raw file not found: {raw_file}")

    # For debugging purposes, try reading only the first 10 rows.
    # (Remove or comment out nrows=10 once you know the file reads correctly.)
    df = pd.read_csv(raw_file, nrows=10, low_memory=False)
    print("Raw file loaded. Number of rows read:", len(df))
    print("Columns in raw file:", df.columns.tolist())

    # Define the expected taxonomy columns.
    expected_taxonomy_columns = [
        'Healthcare Provider Taxonomy Code_1',
        'Healthcare Provider Taxonomy Code_2',
        'Healthcare Provider Taxonomy Code_3',
        'Healthcare Provider Taxonomy Code_4',
        'Healthcare Provider Taxonomy Code_5',
        # Add more columns here if needed.
    ]

    # Check which of the expected taxonomy columns are present.
    available_tax_cols = [col for col in expected_taxonomy_columns if col in df.columns]
    print("Available taxonomy columns found:", available_tax_cols)
    if not available_tax_cols:
        print("None of the expected taxonomy code columns were found in the raw file.")
        return None

    # Create a new column 'codes' that collects all non-null taxonomy codes.
    df['codes'] = df[available_tax_cols].apply(
        lambda row: [str(code).strip() for code in row if pd.notnull(code) and str(code).strip() != ''],
        axis=1
    )
    print("Sample 'codes' (first 5 rows):")
    print(df['codes'].head().tolist())

    # Load the taxonomy mapping dictionary.
    taxonomy_dict = load_taxonomy_mapping()

    # Map each list of codes to their display names and store in 'taxonomy names'.
    df['taxonomy names'] = df['codes'].apply(
        lambda codes: [taxonomy_dict.get(code, 'Unknown') for code in codes]
    )
    print("Sample 'taxonomy names' (first 5 rows):")
    print(df['taxonomy names'].head().tolist())

    # Save the processed DataFrame.
    df.to_csv(output_file, index=False)
    print(f"Processed file saved as {output_file}")
    return df


if __name__ == '__main__':
    processed_df = process_npi_file()
    if processed_df is not None:
        print("Processing complete. Columns in processed file:")
        print(processed_df.columns.tolist())
    else:
        print("Processing did not complete successfully.")
