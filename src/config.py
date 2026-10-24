from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


RAW_DIR=ROOT/"data"/"raw"
SNAPSHOT_DIR=ROOT/"data"/"snapshot"

PHONEPE_DIR = RAW_DIR / "phonepe"
NDAP_DIR = RAW_DIR / "ndap_gst"
CPI_DIR = RAW_DIR /"cpi"
NDAP_FILE = "Goods and Service Tax Returns.csv"
CPI_FILE = "cpi_1520.xlsx"

YEARS = list(range(2018, 2025))
QUARTERS = list(range(1, 5))

# import requests
# data=requests.get("https://api.github.com/repos/PhonePe/pulse/contents/data/aggregated/transaction/country/india/state?ref=master")
# states=[]
# for x in data.json():
#     states.append(x["name"])

STATE_LIST=['andaman-&-nicobar-islands',
 'andhra-pradesh',
 'arunachal-pradesh',
 'assam',
 'bihar',
 'chandigarh',
 'chhattisgarh',
 'dadra-&-nagar-haveli-&-daman-&-diu',
 'delhi',
 'goa',
 'gujarat',
 'haryana',
 'himachal-pradesh',
 'jammu-&-kashmir',
 'jharkhand',
 'karnataka',
 'kerala',
 'ladakh',
 'lakshadweep',
 'madhya-pradesh',
 'maharashtra',
 'manipur',
 'meghalaya',
 'mizoram',
 'nagaland',
 'odisha',
 'puducherry',
 'punjab',
 'rajasthan',
 'sikkim',
 'tamil-nadu',
 'telangana',
 'tripura',
 'uttar-pradesh',
 'uttarakhand',
 'west-bengal']


PHONEPE_URL = "https://raw.githubusercontent.com/PhonePe/pulse/refs/heads/master/data/aggregated/transaction/country/india/state/{state}/{year}/{quarter}.json"
# raw=[]
# for s in states:
#     rp=requests.get(url.format(state=s,year=2024,quarter=4))
#     if rp.status_code != 200:
#         print("FAILED:", s, rp.status_code)
#         continue
#     t_count=0
#     t_amount=0
#     for i in rp.json()["data"]["transactionData"]:
#             t_count+=(i['paymentInstruments'][0]["count"])
#             t_amount+=(i['paymentInstruments'][0]["amount"])
#     raw.append({"state":s,"count":t_count,"amount":t_amount})
    
# df=pd.DataFrame(raw)
# df


MAX_RETRIES = 3
TIMEOUT = 20
RETRY_WAIT = 2

