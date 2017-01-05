import sys
import copy
import ckanapi
from ckan.lib.cli import CkanCommand
from ckan.logic import get_action
from ckan import model



class Harvest(CkanCommand):
    ''' Harvests remote CKAN instance metadata
        Usage:
          harvest --url=http://metadata.bydata.dk
            - Harvests URL and updates local datasets with matching name
    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):
        super(Harvest, self).__init__(name)
        self.parser.add_option('-u', '--url', dest='url', default=False, help='CKAN URL to harvest')

    def _fetch_metadata(self, url):
        api = ckanapi.RemoteCKAN(url)
        response = api.action.package_search(rows=1000000, q='datakk:True')
        return response['results']

    def _process(self, remote_data):
        response = get_action('package_search')({}, {'rows': 1000000})
        local_data = response['results']

        def find_by_name(name):
            #Lookup could be optimized, not a problem at the moment
            for ds in local_data:
                if ds['name'] == name:
                    return ds
            return None

        def extract_extras(extras):
            #Unpacks list of objects to a key/value dict
            extra_map = {}
            for extra in extras:
                extra_map[extra['key']] = extra['value']
            return extra_map

        def pack_extras(extra_map):
            #Packs key/value dict into list of objects
            extras = []
            for key in extra_map:
                extras.append({'key': key, 'value': extra_map[key]})
            return extras

        def check_extras(local, remote, update_data):
            #Checks and updates extras if changed

            #update_frequency, data_quality, quality_note are in metadata schema,
            #therefore they are not present in remote extras, but in remote directly

            update = False
            local_extras = extract_extras(local.get('extras'))
            remote_frequency = remote.get('update_frequency')

            if local_extras.get('update_frequency') != remote_frequency:
                local_extras['update_frequency'] = remote_frequency
                update = True

            remote_quality = remote.get('data_quality')
            if local_extras.get('data_quality') != remote_quality:
                local_extras['data_quality'] = remote_quality
                update = True

            remote_note = remote.get('quality_note')
            if local_extras.get('quality_note') != remote_note:
                local_extras['quality_note'] = remote_note
                update = True

            #Other arbitary keys
            remote_extras = extract_extras(remote.get('extras', []))
            for key in remote_extras:
                if local_extras.get(key) != remote_extras[key]:
                    local_extras[key] = remote_extras[key]
                    update = True

            if update:
                update_data['extras'] = pack_extras(local_extras)
                


        def check_tags(local, remote, update_data):
            #If tags don't match, overwrite with remote tags
            local_tags = [t['name'] for t in local['tags']]
            remote_tags = [t['name'] for t in remote['tags']]
            if local_tags != remote_tags:
                update_data['tags'] = [{'state': 'active', 'name': t} for t in remote_tags]

        #Main()
        for remote in remote_data:
            local = find_by_name(remote['name'])
            if local is None:
                # print("Did not find dataset with name {}, skipping".format(remote['name'].encode('utf-8')))
                continue

            #Create deep copy of current data that we can diff for changes afterwards
            update_data = copy.deepcopy(local)

            check_tags(local, remote, update_data)
            check_extras(local, remote, update_data)

            #NB! I have fixed the metadata module to fix the mappings

            if remote.get('maintainer') != local.get('maintainer'):
                update_data['maintainer'] = remote.get('maintainer')

            if remote.get('author') != local.get('author'):
                update_data['author'] = remote.get('author')

            if remote.get('author_email') != local.get('author_email'):
                update_data['author_email'] = remote.get('author_email')

            if remote.get('notes') != local.get('notes'):
                update_data['notes'] = remote.get('notes')

            if remote.get('title') != local.get('title'):
                update_data['title'] = remote.get('title')

            if(local != update_data):
                print("Updating dataset {}".format(remote['name'].encode('utf-8')))
                context = {'model':model, 'session':model.Session}
                get_action('package_update')(context, update_data)
            else:
                print("No changes detected for dataset {}".format(remote['name'].encode('utf-8')))


    def command(self):
        self._load_config()

        if not self.options.url:
            print("required --url option missing")
            sys.exit(1)

        remote = self._fetch_metadata(self.options.url)
        return self._process(remote)
