import mysql.connector
import re

"""
To use:
USE DATABASE 13F;
SHOW TABLES; <- Shows all the tables within the 13F database
DESCRIBE _____ <- (table_name) to see the table schema
SELECT * FROM companies WHERE company_name LIKE '%INPUT TEXT%' - to find all related companies
Ex. SELECT * FROM companies WHERE company_name LIKE '%Bridgewater Associates%'
It will return both the companies and their cik key which you can use to find the 13F filings of the company
"""

#Inserts all company names with their CIK keys into companies table in 13F database for MySQL
def insert_data_into_company_table():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="darrenliu",
        database="13f"
    )
    cursor = db.cursor()

    with open(r"13F/edgar_api/cik-lookup-data.txt", "r") as file:
        for line in file:
            if line.strip():
                # All text before semicolon is for company_name and after semicolon, is 10 digit cik number when split
                match = re.match(r"(.*?)(\d{10})\s*:", line.strip())
                if match:
                    company_name = match.group(1).strip()  
                    cik_key = match.group(2).strip() 
                    print(f"Company Name: {company_name}, CIK: {cik_key}")
                    cursor.execute("INSERT INTO companies (company_name, cik_key) VALUES (%s, %s)", (company_name, cik_key))
                else:
                    print(f"No match for line: {line.strip()}")

    db.commit()
    cursor.close()
    db.close()


