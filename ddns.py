import requests
import json
import sys

if len(sys.argv) <= 2:
  sys.exit("Not enough arguments")

token = sys.argv[1]
domain = sys.argv[2]

tmp = domain.split('.')
zone = tmp[-2] + '.' + tmp[-1]
headers = {
  'Authorization': 'Bearer ' + token,
  'Content-Type':'application/json'
}

check = requests.get('https://api.cloudflare.com/client/v4/user/tokens/verify', headers=headers)
if json.loads(check.text)['success'] is not True:
  sys.exit("Token is invalid")

newip = requests.get("http://checkip.amazonaws.com/").text

zone = json.loads(requests.get('https://api.cloudflare.com/client/v4/zones', params={'name': zone}, headers=headers).text)
if zone['success'] is not True:
  sys.exit(zone['errors'])
zoneid = zone['result'][0]['id']

dnsrecord = json.loads(requests.get('https://api.cloudflare.com/client/v4/zones/' + zoneid + '/dns_records', params={'name': domain}, headers=headers).text)
if dnsrecord['success'] is not True:
  sys.exit(dnsrecord['errors'])
dnsid = dnsrecord['result'][0]['id']

url = 'https://api.cloudflare.com/client/v4/zones/' + zoneid + '/dns_records/' + dnsid
params = {
  'name': domain,
  'type': 'A',
  'content': newip,
  'ttl': 1,
  'proxied': 'true'
}
update = requests.put(url, headers=headers, data=json.dumps(params))
jsondata = json.loads(update.text)

if jsondata['success']:
  print("IP updated!")
else:
  sys.exit(jsondata['errors'])