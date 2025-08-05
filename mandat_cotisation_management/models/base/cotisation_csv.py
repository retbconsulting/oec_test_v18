import csv
from odoo import api, SUPERUSER_ID

def import_cotisations(env):
    with open('/chemin/vers/fichier.csv', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            env['oec.cotisation'].create({
                'partner_id': int(row['partner_id']),
                'year': row['year'],
                'total': float(row['total']),
                'state': 'validated',
            })
