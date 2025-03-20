import pandas as pd

# Define ward locations as extracted from the text
ward_locations = {
    1: ["Sector 1 to 10 of Uttara Model Town", "Abdullapur (partial)", "Purakarai (partial)", "Shailpur (partial)",
        "Faidabad (partial)", "Baunia (partial)", "Dakshin Khan (partial)", "Ranavola (partial)"],
    17: ["Khilkhet", "Kuril", "Kuratali", "Joarsahara", "Olipara (partial)", "Jagannathpur", "Nikunja – 1 and 2",
         "Haji camp", "Bashundhara R/A", "Jamuna Future Park", "Tanpara"],
    2: ["Mirpur Section-12", "Block-A", "Block-B", "Block-C", "Block-D", "Block-E", "Block-T", "Block-D",
        "Block-P (North Kalshi)", "Section-9", "Block-B", "Burir Tech", "Kalshi Sarkar Bari",
        "Block-P Extended Sagupta"],
    3: ["Mirpur Section-10", "Block-A", "Block-B", "Block-C", "Block-D", "Section-11", "Block-C",
        "Road / AV: -5 Medina Nagar",
        "Avenue-3"],
    4: ["Mirpur Section-13", "Section 13 / A", "13 / B", "13 / C", "Tinsed", "Section-14", "Baishteki", "Section-15"],
    5: ["Mirpur Section-11", "Section-11 Block-A", "Block-B", "Block-C", "Block-D", "Block-E", "Block-F",
        "Palashnagar"],
    6: ["Pallabi", "Extended Pallabi", "New Pallabi Section-6", "Milkvita Road", "Sujatnagar", "Harunabad",
        "Mallika Housing Arambagh", "Arifabad", "Chhayanir", "Section-6", "Block-C", "Block-D", "Block-E",
        "Block-T", "Block-J", "Alubdi", "Duaripara", "6-J", "Rupnagar Tinshed", "Easton Housing second phase area"],
    7: ["Mirpur Section-2", "Block-A", "Block-B", "Block-C", "Block-D", "Block-E", "Block-F", "Block-G", "(1)",
        "Block-H", "Block-K", "Block-J Rupargarh Residential Area", "Section-6 Block-A", "Section-2", "Block-C",
        "Flat 5 Building", "Duaripara", "6-a", "6-b", "6-t", "6-j"],
    8: ["Mirpur Section-1", "Wapda Colony", "Block-A", "Block-B", "Block-C", "Block-D", "Block-E", "Block-F", "Block-G",
        "Block-H", "Commercial Plots", "Local House", "House-B", "House-C", "Al Kamal Housing", "Zoo Residential Area",
        "Nawab Bagh", "Goran Chatbari", "BISF Staff Quarters", "Kumirshah Mazar & Box Nagar", "North Bishal",
        "Priyanka Housing (Section-1) New C Block", "Botanical Garden Residential Area"],

    15: ["Manikdi", "Matikata", "Balughat", "Lalarasai", "Dhamalcourt", "Alubdirtech", "Baigartech", "Barontech",
         "Bhashantech"],
    18: ["Baridhara Residential Area Block-I", "K & J Kalachandpur", "Nardda", "Shahjadpur (A, B & C)"],

    19: ["Banani", "Gulshan 1", "Gulshan 2", "Karail"],

    20: ["Mohakhali", "Mohakhali-Gulshan 1 Link Road", "Institute of Public Health", "Niketan"],

    21: ["North Badda", "South Badda", "Central Badda", "East Merul Badda", "West Merul Badda", "Gupipara Badda"],

    22: ["Bansree", "West Rampura", "East Rampura", "Ulan", "Bagichar Tech", "Nasir Tech", "Omar Ali Lane",
         "West Hajipara", "Badda to Gulshan-1 Link Road"],

    23: ["Khilgaon ‘B’ Zone", "Khilgaon East Hajipara",
         "Malibagh Chowdhury Para (including North Mahalla of Noor Mosque)",
         "Malibagh", "Malibagh Bazar Road", "(Sabujbagh part)"],

    24: ["Tejgaon Industrial Area", "Begunbari", "Kunipara"],

    25: ["Nakhalpara", "Arjatpara", "Civil Aviation Staff Quarters"],

    35: ["Boromagbazar", "Dilurod", "New Eskaton Road", "West Magbazar", "Madhya Peyarabagh", "Greenway",
         "North Nayatola 1st part"],

    36: ["Mirertech", "Mirbagh", "Madhubag", "North Nayatola 2nd Part", "East Nayatola", "South Nayatola",
         "Magbazar Wireless Colony"],
    9: ["Golartech", "Chhota Dayabari", "Boro Dayabari", "Zahurabad", "Anandnagar", "Kotbari", "Charani Para",
        "Baroanipara", "Bagbari", "Harirampur", "Kar Bazar", "Jahanabad", "Ishipara", "Rbadhan Bari",
        "Gabtali Bus Terminal", "Gabtali Bazar", "Gabtali Bazar Raw market"],

    10: ["Mazar Road", "Mirpur Road (partial)", "1st Colony", "2nd Colony", "3rd Colony", "Darussalam Area",
         "Gaidartek", "Lalkuthi", "Baten Nagar Residential Area"],

    11: ["Kalyanpur", "Paikpara", "Madhya Paikpara", "Darussalam Road (partial)"],

    12: ["Ahmednagar (partial)", "Shahalibagh", "South Bishil", "Paikpara", "Tolarbagh (North, Central and South)"],

    13: ["Borobagh", "Manipur", "Pirerbagh (North-South, West-East)", "Shewrapara (West and Central)"],

    14: ["Rokeya Smarani", "Mirpur Road", "Senpara Parbata", "Kazipara (West and East)", "Shewrapara (West and East)"],

    16: ["Kafrul", "North Kafrul", "South Kafrul", "West Kafrul (Taltala)", "Ibrahimpur", "Kachukhet Road"],
    26: ["Karwan Bazar Commercial Area", "Karwan Bazar Lane", "Kazi Nazrul Islam Avenue (Farmgate)", "Green Road",
         "Tejturi Bazar East", "Tejturi Bazar West", "Station Road",
         "Tejkunipara (Shaheed Bir Uttam Ziaur Rahman Road)",
         "Bashundhara City Market"],

    27: ["Testuri Bazar Chowk", "Testuri Bazar Chowklen", "Sajal Square", "Green Road", "Bir Uttam KM",
         "Shafiullah Road",
         "Manipuri Para", "Bir Uttam Shaheed Ziaur Rahman Road"],

    28: ["Shyamoli Bagh", "West Agargaon", "Agargaon Administrative Area"],

    29: ["Mohammadpur Block-C", "Taj Mahal Road Block-F", "Shahjahan Road", "Metropolitan Housing",
         "Co-operative Housing Society", "Mohpur-F", "Juhuri Mahalla"],

    30: ["Baitul Aman Housing", "Pisciculture Housing", "Naboday Housing", "Prominent Panthshala Housing",
         "Turag Housing",
         "Akkach Housing", "Beribadh Ibne Sina Housing", "Ekta Housing", "Uttar Adabor", "Mohammadpur", "Dhaka",
         "Mofiz Housing", "Mehedi Bagh Housing", "Unique Housing", "Adarsh Chayanir", "Mohammadpur Housing", "Adabar",
         "Secretech"],

    31: ["Azam Road", "Asad Avenue", "Razia Sultana Road", "Taj Mahal Road", "Shera Shahsuri Road", "Nurjahan Road",
         "Zakir Hossain Road", "Shahjahan Road", "Aurangzeb Road", "Kazi Nazrul Islam Road Block-E"],

    32: ["Lalmatia Block-A", "Lalmatia Block-B", "Lalmatia Block-C", "Lalmatia Block-D", "Lalmatia Block-E",
         "Laamatia Block-F", "Lalmatia Block-G", "Sir Syed Road", "Humayun Road", "Babar Road", "Iqbal Road",
         "Aurangzeb Road", "Khilji Road", "Asad Avenue", "Mohpur Colony",
         "Md. Pur Co-operative Housing Society Ltd. Block-A",
         "Ghaznabi Road", "(PCCulture) Lalmatia Housing Estate New Colony"],

    33: ["Mohammadia Housing Limited", "Mohammadia Housing Society", "Kaderabad Housing Estate", "Katasur", "Bashbari",
         "Chanmia Housing", "Chand Housing", "Chand Udyan Bachila", "Bachila Road", "Nabinagar Housing", "Dhaka Udyan",
         "Dhaka S&L. Town", "Beri Dam", "Bochila Model Town", "Chandrima Model Town", "Bochila City Developers",
         "Satmasjid Housing Cooperative Society Ltd.", "Japan Garden City", "Bijnibivar Housing", "Naboday Housing",
         "Brothers", "Future Town", "Latif Real House"],

    34: ["West Dhanmondi", "Mother Care Hospital", "Sultanganj", "Rayer Bazar East", "Zafarabad", "Metro Housing"],
    44: ["Amaiya", "Barbari", "Chamurkhan", "Kanchkura", "Snanghata", "Bhaturia", "Palashia", "Chhota Palashia",
         "Poradia", "Ratuti", "Varardi", "Aktertek", "Bauthar", "Betuli", "Karim’s Bagh", "Dobadia"],

    45: ["Uttarkhan (southern part)", "Uttarkhan (northern part)"],

    46: ["Babur Para", "Barbagh", "Oja Para", "Rajabari", "Munda", "Poolar Tech", "Bhatulia", "Mausaid", "Baduri Para",
         "Chanpara", "Faujarbari", "Gobindpur", "Khanjurdia", "Kumud Khola", "Mainartech", "Ninnirtek", "Noakhola",
         "Sauwartek"],
    39: ["Nurerchala West", "Nurerchala East", "KhilbariTech West", "KhilbariTech East"],

    40: ["Bhatara (partial)", "Chholmaid", "Nayanagar North", "Nayanagar South"],

    43: ["Talna", "Dhelna", "Nakuni", "Manjertech", "Mastul", "Patira", "Dumni", "Kanthaldia", "Bagdia", "Amdia"],
    37: ["Daokandi", "Tekpara Badda", "Sona Katra", "Sekandarbagh", "Madhya Badda", "Mollapara", "Beparipara",
         "Post Office Road", "Louhertech"],

    38: ["Madhyapara", "Mollapara", "Mollapara Adarsh Nagar", "Uttar Badda Purbapara", "Uttar Badda Mainartek",
         "Bawalipara", "Uttar Badda Purbapara (Abdullahbagh)", "Uttar Badda Mishri Tola", "Uttar Badda Hajipara"],

    41: ["Pukurpara", "Dakshinpara", "Taltola", "Uttarpara West", "Uttarpara East", "Panchkhola", "Merulkhola",
         "Magardia", "East Padardia", "West Padardia"],

    42: ["Boro Beraid Purbapara", "Boro Beraid Bhuiyanpara", "Boro Beraid Rishipara", "Boro Beraid Araddapara",
         "Chhota Beraid Dagardia", "Ashkartek", "Chandertek", "Panchdirtek", "Harardia",
         "Boro Beraid Moralpara (North)",
         "Boro Beraid Moralpara (South)", "Boro Beraid Agarpara", "Boro Beraid Chatkipara", "Boro Beraid Chinadipara",
         "Fakirkhali"]

}

# Convert to DataFrame
data = []
for ward, locations in ward_locations.items():
    for location in locations:
        data.append({"Ward No.": ward, "Location": location})

df = pd.DataFrame(data)

# Save to CSV
csv_file_path = "/mnt/data/ward_locations.csv"
df.to_csv(csv_file_path, index=False)

# Provide the CSV file path
csv_file_path
