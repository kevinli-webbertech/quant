import xml.etree.ElementTree as ET
import pandas as pd

"""
Static function: it doesn't rely on self object. This is `this` in java.
We can repurpose this for a lot of other functions for reusability.
1067983
Examples:
c = SEC13F()
c.find_common_holdings_multi_cik(['1350694', '1067983', '1037389', '1610520'])
"""
#def aggregate_holdings(*args):
def aggregate_holdings(df_list):
    if not df_list:
        return "No DataFrame/s provided."

    company_sets = [set(df['Company Name']) for df in df_list if 'Company Name' in df.columns]

    if not company_sets:
        return "No 'Company Name' column found in any DataFrame."

    overlapping_stocks = set.intersection(*company_sets)

    if not overlapping_stocks:
        return "No matches found."

    return ", ".join(overlapping_stocks)

# Convert shares and total value of each stock held into billions(B), millions(M), & K depending on the value
def divisibleBy(number):
    string = ''
    if number >= 1000000000:
        string =  str(round(number / 1000000000)) + "B"
    elif number >= 1000000:
        string = str(round(number / 1000000)) + "M"
    else:
        string = str(round(number / 1000)) + "K"
    return string

"""
    Converts an XML string to a Pandas DataFrame.

    Args:
        xml_string (str): The XML string to convert.
        root_tag (str): The root tag of the XML document.
        record_tag (str): The tag name for individual records/rows in the XML.

    Returns:
        pd.DataFrame: A Pandas DataFrame representing the XML data.
"""
# Please refer to
#https://www.google.com/search?q=xml+request+response+to+pandas&oq=xml+request+response+to+pandas&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQIRigATIHCAIQIRigATIHCAMQIRigATIHCAQQIRigATIHCAUQIRigATIHCAYQIRifBTIHCAcQIRifBTIHCAgQIRifBTIHCAkQIRifBdIBCDU0ODFqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8

def xml_to_pandas(xml_string, root_tag, record_tag):

    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {e}")

    if root.tag != root_tag:
        raise ValueError(f"Root tag '{root.tag}' does not match expected '{root_tag}'")

    records = root.findall(f".//{record_tag}")

    if not records:
        return pd.DataFrame()

    data = []
    for record in records:
        record_data = {}
        for element in record:
            record_data[element.tag] = element.text
        data.append(record_data)
    return pd.DataFrame(data)


