# Use with Nosetests

import nose.tools as nt

from wikilinks_loader.data_loader import *


def test_get_wiki_annotation():
    url3 = 'https://en.wikipedia.org/wiki/Vladimir_Putin'
    url2 = 'http://en.wikipedia.org/wiki/putin'
    url1 = 'http://en.wikipedia.org/wiki/VVP'
    url4 = 'http://en.wikipedia.org/wiki/Vladimir%20Putin'
    title1 = get_wiki_annotation(url1)
    title2 = get_wiki_annotation(url2)
    title3 = get_wiki_annotation(url3)
    title4 = get_wiki_annotation(url4)
    assert title1 == title2 == title3 == title4


def test_get_wiki_synonims():
    wiki_url1 = 'https://en.wikipedia.org/wiki/Putin'
    wiki_url2 = 'https://en.wikipedia.org/wiki/Vladimir%20Putin'
    wiki_synonims1 = get_wiki_synonyms(wiki_url1)
    wiki_synonims2 = get_wiki_synonyms(wiki_url2)
    title1 = fully_unquote(wiki_url1.split('/')[-1])
    title2 = fully_unquote(wiki_url2.split('/')[-1])
    assert title1 in wiki_synonims2
    assert title2 in wiki_synonims1


# def test_find_synonims():
#     wiki_url1 = 'https://en.wikipedia.org/wiki/Putin'
#     files = wikilinks_files('/home/artreven/Downloads/dataset_mentions/')
#     forms = find_synonyms(wiki_url1, files)
#     assert 'President Putin' in forms
#
#
# def test_find_annotations():
#     forms = ['Putin', 'VVP']
#     files = wikilinks_files('/home/artreven/Downloads/dataset_mentions/')
#     annotations = find_annotations(forms, files)
#     assert 'https://en.wikipedia.org/wiki/Vladimir_Putin' in annotations
