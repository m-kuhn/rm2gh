import xml.etree.ElementTree as ET
import json
import re
import requests
import os
from requests.auth import HTTPBasicAuth
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-u', '--user', dest='user')
parser.add_option('-p', '--password', dest='password')
parser.add_option('-r', '--repo', dest='repo')
parser.add_option('-t', '--test', dest='test', default=True)
parser.add_option('-l', '--limit', dest='limit', default=100000)

(options, args) = parser.parse_args()

if options.user is None or options.password is None or options.repo is None:
    parser.error(
'''
Require options --user (-u), --password (-p) and --repo (-r)

Example
-------

    python migrate.py -u m-kuhn -p tooeasy -r qgis/QGIS
''')

doit = options.test
limit = options.limit

def create_ticket(issue):
    if doit:
        r = requests.post('https://api.github.com/repos/{}/issues'.format(options.repo), data=json.dumps(issue), auth=HTTPBasicAuth(options.user, options.password))
    else:
        json.dumps(issue)

def create_dummy():
    issue = {
        'title': 'Dummy ticket',
        'body': 'This is a dummy ticket to prevent gaps in numbering during the migration process'
    }

    create_ticket(issue)

def migrate_ticket(root):
    assert root.find('project').attrib['id'] != 17

    tracker_map = {
        '1': 'bug',
        '2': 'enhancement',
        '3': ''
    }

    subject = root.find('subject').text
    tracker = root.find('tracker').attrib['id']
    description = root.find('description').text

    comments = []

    journals = root.find('journals')
    if journals is not None:
        for journal in journals:
            notes = journal.find('notes').text
            if not notes:
                notes = ''
            author = journal.find('user').attrib['name']

            notes = '> ' + re.sub('\n', '\n> ', notes)
            comments.append(author + ':' + '\n' + notes)

    issue = {
        'title': subject,
        'body':
    u'''
[This issue has been migrated from the old QGIS issue tracker.](https://hub.qgis.org/issues/{ticket_id})

Description
-----------

{description}

Comments
--------

{comments}
'''.format( ticket_id=ticket_id, description=description, comments=u'\n\n'.join(comments)),
        'labels': [
            tracker_map[tracker]
        ]
    }

    create_ticket(issue)

r = requests.get('https://api.github.com/repos/{}/issues'.format(options.repo), auth=HTTPBasicAuth(options.user, options.password))
print r.text
highest_ticket_number = json.loads(r.text)[0]['number']

files = os.listdir('.')

tickets = sorted([int(f[7:12]) for f in files if f[-4:] == '.xml'])

print 'Migrating {} tickets'.format(len(tickets))
print 'IDs up to {} already taken, maximum ticket id {}'.format(highest_ticket_number, tickets[-1])

for ticket in tickets:
    ticket_id = str(ticket).zfill(5)
    if ticket <= highest_ticket_number:
        print 'skipping ticket {}'.format(ticket_id)
        continue

    if ticket >= limit:
        print 'stopping at ticket {} due to limit'.format(ticket)
        break

    print 'create ticket {}'.format(ticket_id)
    try:
        tree = ET.parse('ticket-{}.xml'.format(ticket_id))
        root = tree.getroot()
        migrate_ticket(root)
    except ET.ParseError:
        print 'ticket {} not found, creating dummy'.format(ticket_id)
        create_dummy()
