import pandas as pd
import streamlit as st

# Load the dataframes
sources_df = pd.read_csv("sources25.csv", encoding='latin-1')
sjr_df = pd.read_csv("SJR23.csv", encoding='latin-1')
matrix_sco_df = pd.read_csv("matrixSCO.csv", encoding='latin-1')

# Extract unique journal titles and ISSNs
title_options = sources_df['Title'].dropna().unique().tolist()
issn_options = sources_df['ISSN'].dropna().astype(str).apply(lambda x: x.lstrip('0')).tolist()
eissn_options = sources_df['EISSN'].dropna().astype(str).apply(lambda x: x.lstrip('0')).tolist()
all_options = title_options + issn_options + eissn_options

# Create the autocomplete widget
query = st.selectbox('Search:', all_options)

def display_journal_info(query):
    query = query.strip().lstrip('0')  # Remove all leading zeros

    # Check for matches, ignoring leading zeros
    sources_df['ISSN_clean'] = sources_df['ISSN'].astype(str).apply(lambda x: x.lstrip('0'))
    sources_df['EISSN_clean'] = sources_df['EISSN'].astype(str).apply(lambda x: x.lstrip('0'))

    if query in sources_df['Title'].values:
        source_info = sources_df[sources_df['Title'] == query].iloc[0]
    elif query in sources_df['ISSN_clean'].values:
        source_info = sources_df[sources_df['ISSN_clean'] == query].iloc[0]
    elif query in sources_df['EISSN_clean'].values:
        source_info = sources_df[sources_df['EISSN_clean'] == query].iloc[0]
    else:
        st.write("No matching journal found.")
        return

    title, issn, eissn, sid = source_info[['Title', 'ISSN', 'EISSN', 'SID']]

    # Get info from sjr_df
    sjr_info = sjr_df[sjr_df['SID'] == sid]

    # Display basic journal information
    st.write(f"Title: {title}")
    st.write(f"ISSN: {issn}")
    st.write(f"EISSN: {eissn}")

    if not sjr_info.empty:
        # Print SJR only once for the first row
        first_row = sjr_info.iloc[0]  # Get the first row
        st.write(f"SJR(2023): {first_row['SJR']}")

        for _, row in sjr_info.iterrows():
            st.write(f"Subject Area: {row['Description']}")
            st.write(f"ASJC: {row['ASJC']}")
            st.write(f"Quartile: {row['Quartile']}")

            # Get ASJC code and extract first two digits
            asjc_code = str(row['ASJC'])[:2]

            # Filter matrix_sco_df based on ASJC code
            matching_rows = matrix_sco_df[matrix_sco_df['ASJC'].astype(str).str.startswith(asjc_code)]

            if not matching_rows.empty:
                # Get unique PN values for the matching rows
                pn_values = matching_rows['PN'].dropna().unique().tolist()
                st.write(f"Професионално направление: {', '.join(map(str, pn_values))}")
            else:
                st.write(f"No matching PN values found for {title} (ASJC: {asjc_code})")

if query:
    display_journal_info(query)
