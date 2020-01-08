# Load necessary libraries.
import pandas as pd
from tabula import read_pdf

# Load the file.
data_agr = pd.read_csv("./pax_all_agreements_data.csv")

# Get desired columns data.
agr_usable_columns = ['AgtId', 'PPName', 'Con', 'Reg', 'Contp', 'CowWar', 'Dat']
data = data_agr[agr_usable_columns]

# Drop rows which has NaN values: 7 PPName and 678 CowWar.
data = data.dropna()
data['CowWar'] = data['CowWar'].astype(int)

# Obtain and transform CowWars data.
data_wars = read_pdf("./CowWarList.pdf", pages="all")
war_type_number = pd.DataFrame(data_wars['War Type &\rNumber'].str.split('#').tolist(), 
                               columns = ['War Type', 'CowWar'])                        

data_wars = pd.concat([data_wars, war_type_number], axis=1).drop(columns=["War Type &\rNumber", "Year"])
data_wars['CowWar'] = data_wars['CowWar'].astype(int)

# Obtain war name and duration years as a new columns
last_year = '2010'
war_info = {'War Name': [], 'Year From': [], 'Year To': []}
for war_name in data_wars['War Name']:
    war_name_parts = war_name.replace('\r', ' ').split(' ')
    
    war_info['War Name'].append(' '.join(war_name_parts[:-2]))
    
    years_column = war_name_parts[-1].replace('present', last_year)
    years_parts = years_column.split('-')
    
    war_info['Year From'].append(years_parts[0])
    if len(years_parts) > 1:
        war_info['Year To'].append(years_parts[-1])
    else:
        war_info['Year To'].append(years_parts[0])

war_info_df = pd.DataFrame(war_info)

data_wars = data_wars.drop(columns='War Name')
data_wars = data_wars.drop(columns='Reg')
data_wars = pd.concat([data_wars, war_info_df], axis=1)

# Merge two datasets
data = pd.merge(data, data_wars, on=['CowWar'])
data['War Type'] = data['War Type'].str.replace('War', '')
data['War Type'] = data['War Type'].str.strip()

# Add the duration of the war
data['War Duration'] = [(int(ele) - int(data.iloc[i]['Year From']) + 1) for i, ele in enumerate(data['Year To'])]

# Split multiple countries from one row.
indexs_to_drop = []
separated_countries = []
for index, row in data.iterrows():
    distinct_countries = row['Con'].split('/')
    if len(distinct_countries) > 1:
        indexs_to_drop.append(index)
        for country in distinct_countries:
            aux_row = row
            aux_row['Con'] = country          
            separated_countries.append(aux_row.values)
       
# Delete those lines which contain multiples countries.
data = data.drop(data.index[indexs_to_drop])

# Concatenate splited countries into the dataset.
data = pd.concat([data, pd.DataFrame(separated_countries, columns = data.columns)])

# Output to a new data file
data.to_csv(r'.\cleaned_data.csv', index=None, header=True)





