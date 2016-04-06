# rm2gh

Migrates redmine ticket xml export to github issues.

It preserves existing ticket ids and skips low ticket numbers if these already
exist as issues or pull requests on the target github repository.

Usage:

    python migrate.py --user m-kuhn --password tooeasy --repo qgis/QGIS

Help:

    python migrate.py --help

Tickets are expected in the form `ticket-00123.xml` in the same folder as this
script.
