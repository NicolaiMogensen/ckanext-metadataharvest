#!/usr/bin/python
# -*- coding: utf-8 -*-
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

def get_quality_translation(quality):
    qualmap = {
        'good': 'Total ajourført',
        'medium': 'Delvist ajourført',
        'bad': 'Mangelfuldt'
    }
    return qualmap.get(quality, '').decode('utf8')

def find_extra(extras, key):
    for extra in extras:
        if extra.get('key') == key:
            return extra.get('value')
    return False

class MetadataharvestPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'metadataharvest')

    def get_helpers(self):
        return { 
            'find_extra': find_extra,
            'get_quality_translation': get_quality_translation
        } 
