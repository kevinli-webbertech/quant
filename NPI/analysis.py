import pandas as pd
import matplotlib.pyplot as plt
import os
import ast

def SortDoctorsPractices(df):
    # If the "taxonomy names" column is stored as a string representation of a list,
    # convert it back to a list. (If it’s already a list, this step won’t change it.)
    df['taxonomy names'] = df['taxonomy names'].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    df_ex = df.explode('taxonomy names')
    df_ex.reset_index(drop=True, inplace=True)
    return df_ex

def remove_deactivated_doctors(df):
    # Fill NA values with 0 for simplicity.
    df = df.fillna(0)
    # Separate out reactivated doctors (where "NPI Reactivation Date" is not 0).
    reactivated_doctors = df[df['NPI Reactivation Date'] != 0]
    # Keep only rows where "NPI Deactivation Date" is 0.
    df_active = df[df['NPI Deactivation Date'] == 0]
    # Concatenate the active and reactivated doctors.
    active_doctors = pd.concat([df_active, reactivated_doctors])
    return active_doctors

def active_doctors_count_based_on_practice(df):
    df2 = df.groupby('taxonomy names').size().reset_index(name='count of doctors')
    df2.set_index('taxonomy names', inplace=True)
    return df2

def process(file):
    df = pd.read_csv(file)
    df_ex = SortDoctorsPractices(df)
    active_doctors = remove_deactivated_doctors(df_ex)
    active_doctors_count = active_doctors_count_based_on_practice(active_doctors)
    return active_doctors_count

def aggregate_and_plot(processed_file='processed_npi.csv'):
    if not os.path.exists(processed_file):
        raise FileNotFoundError(f"Processed file not found: {processed_file}")

    # Process the single processed file.
    total_counts = process(processed_file)
    total_counts = total_counts.reset_index()
    # Sort by count (descending order)
    total_counts = total_counts.sort_values(by='count of doctors', ascending=False)

    # Create a pie chart of the top 20 taxonomy categories.
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(total_counts['count of doctors'][:20],
           labels=total_counts['taxonomy names'][:20],
           autopct='%1.1f%%',
           startangle=140)
    ax.set_title('Percentage of Doctors by Practice')
    return fig, total_counts

if __name__ == '__main__':
    fig, data = aggregate_and_plot()
    plt.show()
