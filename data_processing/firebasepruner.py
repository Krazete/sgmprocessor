import json
from time import time
from data_processing import file

with open('data_processing/input/sgmobilegallery-export.json', 'r') as fp:
    data = json.load(fp)
now = time() * 1000

for variant in data:
    for fense in data[variant]:
        for vote in data[variant][fense].copy():
            votetime = data[variant][fense][vote].get('timestamp', 0)
            if (now - votetime > 2 * 31536000000): # 2 years
                data[variant][fense].pop(vote)

file.save(data, 'data_processing/output/firebase-pruned.json', True)

# Firebase Data Structure
# {
#     "variant": {
#         "defense": {
#             "DlSjIzQkKxQv6buTkGluRKvwsyC3": {
#                 "ip": "24.117.46.102",
#                 "timestamp": 1679085715700,
#                 "vote": 3
#             }
#         },
#         "offense": {
#             "li2beOxGprOLnaBpYvanx2N1Xhf2": {
#                 "ip": "83.149.21.19",
#                 "vote": 5
#             }
#         }
#     }
# }
