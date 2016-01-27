ckanext-metadataharvest
=========
ckanext-metadataharvest is [CKAN](https://github.com/ckan/ckan) extension for harvesting Copenhagen Kommune metadata portal. It will fetch datasets that have datakk value set to True and update datasets with matching name.


Installing
-------
__NB! This module is developed on CKAN v2.4.0, compatibility with other version is not ensured__
```sh
#activate virtualenv
source /usr/lib/ckan/default/bin/activate
cd /usr/lib/ckan/default/src
git clone git@github.com:cphsolutionslab/ckanext-metadataharvest.git
cd ckanext-customuserprivileges
#install dependencies
pip install -r dev-requirements.txt
python setup.py develop
sudo nano /etc/ckan/default/production.ini
# Enable plugin in configuration
# ckan.plugins = datastore ... metadataharvest
```
Usage
-------
The extension creates a command for synchronization. To execute the command periodically, add following cron job:
```
# this job runs daily at 03:55
55 3 * * * cd /usr/lib/ckan/default/src/ckanext-metadataharvest && /usr/lib/ckan/default/bin/python /usr/lib/ckan/default/bin/paster harvest --url=http://ckan-url-here.com --config=/etc/ckan/default/production.ini
```
Remember to `http://ckan-url-here.com` with the address of ckan you want to harvest
