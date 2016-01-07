"""
Wikilinks Loader

A tool for loading data from Wikilinks (see http://www.iesl.cs.umass.edu/data/wiki-links).

"""

from wikilinks_loader.data_loader import get_most_popular_annotations, find_annotations, find_ambiguous_entities, \
    output_ambiguous_entity, output_mentions, check_wikilinks_files, wikilinks_files, \
    find_synonyms, output_forms, get_wiki_annotation, get_wiki_synonyms

__author__ = 'Artem Revenko (artreven@gmail.com)'
__license__ = 'MIT'

__all__ = ['get_most_popular_annotations', 'find_annotations', 'find_ambiguous_entities',
           'check_wikilinks_files', 'wikilinks_files', 'output_ambiguous_entity', 'output_mentions']



