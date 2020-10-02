import requests
import json

url = 'http://0.0.0.0:5000/v0.1/annotate'
file = {'file': open('/home/easyrights/Documents/pgr/documentation/es/Asylum_and_Employment_Procedimiento_plazas.pdf','rb')}
values = {"service": "TESTSN", "pilot": "TESTPN"}
data = {'data': json.dumps(values)}
response = requests.post(url, data=data, files=file)
#response.encoding = 'ISO-8859-1'

print(response.request.body)