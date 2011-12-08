#coding: utf-8
import sys
import csv
from urllib import urlopen

from recon.interactive import interactive
from recon.local import CSVLocalEndpoint

COUNTRIES_URL = 'iso_3166_2_countries.csv'

COUNTRIES_EX = {
    u'Iran, Islamic Rep.': 'IR', 
    u'Kosovo': 'XK', 
    u'Russian Federation': 'RU', 
    u'China': 'CN', 
    u'Kyrgyz Republic': 'KR', 
    u'Macedonia, FYR': 'MK', 
    u'Congo, Rep.': 'CD',
    u'Egypt, Arab Rep.': 'EG', 
    u'Slovak Republic': 'SK',
    u'S\xe3o Tom\xe9 and Princip': 'ST', 
    u'Lao PDR': 'LA', 
    u'Serbia and Montenegro': 'CS', 
    u'Yemen, Rep.': 'YE',
    u"Cote d'Ivoire": 'CI'
    }

def cleanup(file_name):
    fh = urlopen(COUNTRIES_URL)
    uri = lambda r: r['ISO 3166-1 2 Letter Code']
    endpoint = CSVLocalEndpoint(fh, 'Common Name', uri_maker=uri)
    fh = open(file_name, 'rb')
    data = []
    for row in csv.DictReader(fh):
        entry = {}
        for k,v in row.items():
            v = v.decode('latin-1')
            if 'Proceeds' in k:
                k = 'amount'
                if v:
                    v = v.replace(",", "")
                    v = float(v) * 1000000
                    v = unicode(v)
            elif 'Year' in k:
                k = 'time'
            elif 'Country' in k:
                res = interactive(endpoint.reconcile, v)
                if res:
                    entry['Country Code'] = res.uri
                elif not len(v):
                    v = 'Unknown Country'
                    entry['Country Code'] = 'XX'
                else:
                    entry['Country Code'] = COUNTRIES_EX[v]
            entry[k] = v
        data.append(entry)
    return data

if __name__ == '__main__':
    data1 = cleanup("PrivatizationData00_08.csv")
    data2 = cleanup("PrivatizationData88_99.csv")
    data = data1 + data2
    headers = set()
    for r in data:
        headers = headers.union(r.keys())
    writer = csv.DictWriter(open('wp-privatizations.csv', 'wb'),
            fieldnames=headers)
    writer.writerow(dict([(d, d) for d in headers]))
    for row in data:
        row = dict([(k, v.encode('utf-8')) for k,v in row.items()])
        writer.writerow(row)
