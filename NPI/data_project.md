1/ Read all the monthly doctor data and sort doctors with different practices.

After splitting the dataset into chunks to enable loading them while the doctors practices codes are encoded to the real names using the ucc_taxonomy_241.csv file as in the code in data.py , 
[nucc_taxonomy_241.csv](nucc_taxonomy_241.csv)
In the other file analysis.py, I will create a function that will split the practices in the taxonomy names columns since some doctors are specialized in several practices.

Then, I will load the dataframes that i have saved already and i will only consider NPI and taxonomy names columns to show what are the practicies for each doctor applying the SortDoctorsPractices() function. for each chunk i will only show the first 3 rows.

2/ Remove the doctors from the deactivation zip.

3/ After removal, get counts of all the active doctors based on the practices.

4/ Use a Piechart or any visualization to show the percentage other any other charts you think that can visualize better.

5/ Using Pandas to see if the following doctors are in the NPI data.