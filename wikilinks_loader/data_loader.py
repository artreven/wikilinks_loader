"""
Contains functions for finding ambiguous entities using Wikilinks data
(see http://www.iesl.cs.umass.edu/data/wiki-links).
"""

from collections import defaultdict
import requests
import urllib, urllib.parse
import os
import sys
import functools


def find_annotations(forms, files):
    """
    Create a dictionary of possible ambiguous annotations for all forms.

    :param files: datafiles to be analyzed. Paths to wikilinks files.
    :param forms: different forms of an entity
    :return: dict {annotation_url: [(form, document_url), ...]}
    """
    if not type(forms) in [list, tuple]:
        forms = [forms]
    ambiguities = defaultdict(list)
    for file_ in files:
        with open(file_, 'r') as data_file:
            for line in data_file:
                three_first_chars = line[:3]
                if three_first_chars == 'URL':
                    line_content = line.split('\t')
                    current_document_url = line_content[1].strip('\n')
                elif three_first_chars == 'MEN':
                    line_content = line.split('\t')
                    mention_title = line_content[-3]
                    if mention_title in forms:
                        mention_url = line_content[-1].strip('\n')
                        annotation_title = get_wiki_annotation(mention_url)
                        annotation_url = 'https://en.wikipedia.org/wiki/{}'.format(annotation_title.replace(' ', '_'))
                        ambiguities[annotation_url].append((mention_title, current_document_url))

    return ambiguities


def find_synonyms(wiki_url, files):
    """
    Find different mentioned synonyms of a concept. Redirects are taken into account.

    :param wiki_url: annotation on wikipedia
    :param files: specify wikilinks files by list of paths
    :return: dictionary {synonim: [(document, offset)]}
    """
    wiki_synonyms = get_wiki_synonyms(wiki_url)
    synonyms = defaultdict(list)
    for file_ in files:
        with open(file_, 'r') as data_file:
            for line in data_file:
                three_first_chars = line[:3]
                if three_first_chars == 'URL':
                    line_content = line.split('\t')
                    current_document = line_content[1].strip('\n')
                elif three_first_chars == 'MEN':
                    line_content = line.split('\t')
                    mention_url = line_content[-1].strip('\n')
                    annotation_title = fully_unquote(mention_url.split('/')[-1]).replace('_', ' ')
                    if annotation_title in wiki_synonyms:
                        syn = line_content[-3]
                        synonyms[syn].append(current_document)

    return synonyms


def find_ambiguous_entities(n_ambiguous, files, threshold=5, k_ann=2):
    """
    Find ambiguous mentions of entities.

    :param n_ambiguous: int - how many ambiguous entities do you want?
    :param threshold: entity is counted ambiguous if there are at least two different annotations mentioned
              at least (threshold) times each.
    :param files: specify wikilinks files by list of paths
    :return: dictionary - {ambiguous_entities: {concepts: times mentioned}}
    """
    def exists_geq(k, it):
        true_it = (x for x in it if x)
        c = 0
        for _ in true_it:
            c += 1
            if c >= k:
                return True
        return False
    # dictionary of entity: {concept:count}
    ambiguations = defaultdict(lambda: defaultdict(int))
    ambiguous_ents = set()
    for file_ in files:
        with open(file_, 'r') as data_file:
            for line in data_file:
                if line[:3] == 'MEN':
                    line_content = line.split('\t')
                    entity = line_content[-3]
                    url = line_content[-1].strip('\n')
                    annotation_title = get_wiki_annotation(url)
                    annotation_url = 'https://en.wikipedia.org/wiki/{}'.format(annotation_title.replace(' ', '_'))
                    ambiguations[entity][annotation_url] += 1
                    if (len(ambiguations[entity].keys()) >= k_ann and exists_geq(k_ann, (x >= threshold
                                                                for x in ambiguations[entity].values()))):
                        ambiguous_ents.add(entity)
                        if len(ambiguous_ents) >= n_ambiguous:
                            ans = {ambiguous_ent: ambiguations[ambiguous_ent] for ambiguous_ent in ambiguous_ents}
                            return ans
    print('Not enough ambigous entities found. Required {n}, found {m}'.format(n=n_ambiguous,
                                                                               m=len(ambiguous_ents)))
    ans = {ambiguous_ent: ambiguations[ambiguous_ent] for ambiguous_ent in ambiguous_ents}
    return ans


def fully_unquote(s):
    """
    urllib.parse.unquote acts only once. in case quotes are nested it is necessary to unquote until no further changes
    occur.
    """
    new_s = urllib.parse.unquote(s)
    c = 0
    while new_s != s:
        s = new_s
        new_s = urllib.parse.unquote(s)
        c += 1
        assert c <= 10
    return new_s

wiki_api_base = 'https://en.wikipedia.org/w/api.php'


@functools.lru_cache(maxsize=128)
def get_wiki_annotation(url):
    """
    Get the final annotation according to wikipedia. Redirects are taken into account.

    :return: title of the final (after redirect) wikipage
    """
    url_title = fully_unquote(url.split('/')[-1]).replace('_', ' ')
    params = {
        'action': 'query',
        'redirects': True,
        'format': 'json',
        'titles': url_title
    }
    wiki_response = requests.get(wiki_api_base, params)
    wiki_json = wiki_response.json()
    assert len(wiki_json['query']['pages'].keys()) == 1
    id_ = list(wiki_json['query']['pages'].keys())[0]
    wiki_title = wiki_json['query']['pages'][id_]['title']
    # wiki_url = 'https://en.wikipedia.org/wiki/{}'.format(title.replace(' ', '_'))
    return wiki_title


@functools.lru_cache(maxsize=128)
def get_wiki_synonyms(wiki_url):
    """
    Get all wiki pages which redirect to wiki_url
    """
    canonical_title = get_wiki_annotation(wiki_url)
    canonical_url = 'https://en.wikipedia.org/wiki/{}'.format(canonical_title.replace(' ', '_'))
    canonical_title = fully_unquote(canonical_url.split('/')[-1]).replace('_', ' ')
    params = {
        'action': 'query',
        'list': 'backlinks',
        'format': 'json',
        'blfilterredir': 'redirects',
        'bllimit': '100',
        'bltitle': canonical_title
    }
    wiki_response = requests.get(wiki_api_base, params)
    wiki_json = wiki_response.json()
    backlinks = wiki_json['query']['backlinks']
    back_titles = [x['title'] for x in backlinks] + [canonical_title]
    return back_titles


def get_most_popular_annotations(ambiguous_entity, k=2):
    """
    Get k most popular annotations for ambiguous_entity.
    """
    freq = [(key, len(value)) for key, value in ambiguous_entity.annotated_corpus.items()]
    freq = sorted(freq, key=lambda x: x[1], reverse=True)
    return [x[0] for x in freq[:k]]


def output_mentions(mentions, path):
    with open(path, 'w') as f:
        for entity in mentions:
            f.write('ENTITY\t{}\n'.format(entity))
            for annotation in mentions[entity]:
                f.write('ANNOTATION\t{annotation}\t{times}\n'.format(annotation=annotation,
                                                                     times=mentions[entity][annotation]))
            f.write('\n\n')


def output_ambiguous_entity(ambiguities, path):
    with open(path, 'w') as f:
        for annotation in ambiguities:
            f.write('\n')
            f.write('ANNOTATION\t{}\n'.format(annotation))
            for form, doc in ambiguities[annotation]:
                f.write('MENTION\t{form}\t{doc}\n'.format(form=form, doc=doc))


def output_forms(forms, path):
    with open(path, 'w') as f:
        for form in forms:
            f.write('FORM\t{}\n'.format(form))
            for doc in forms[form]:
                f.write('MENTION\t{doc}\n'.format(doc=doc))
            f.write('\n')


def check_wikilinks_files(path):
    if os.path.isdir(path):
        wikilinks_filenames = wikilinks_files(path)
        if not all(os.path.exists(file) for file in wikilinks_filenames):
            print('In {dir} not all wikilinks files (in form data-0000x-of-00010) were found.'.format(dir=path))
            sys.exit(1)
    else:
        print('Directory {dir} was not found.'.format(dir=path))
        sys.exit(1)


def wikilinks_files(path):
    """
    :param path: directory where wikilinks files are stored
    :return: a list of wikilinks files (assuming their names are in form data-0000x-of-00010
    """
    filenames = [path + '/data-0000{0}-of-00010'.format(i) for i in range(10)]
    return filenames


# if __name__ == '__main__':
#     import pickle
#     ambiguous_it = (find_ambiguous(range(10), entity_name) for entity_name in ambiguous_entities_names)
#     # number of documents we want for each category
#     doc_num = 150
#     for ae in ambiguous_it:
#         top_concepts = get_most_popular(ae)
#         print('='*80)
#         print('Entity: ', ae.entity, '\tMost popular annotations: ', top_concepts)
#         annotated_urls = {concept: [x[0] for x in ae.annotated_corpus[concept]] for concept in top_concepts}
#         annotated_texts = defaultdict(list)
#         for cpt in annotated_urls.keys():
#             c = 0
#             for text in texts_iterator(annotated_urls[cpt]):
#                 processed_text = doc2text.remove_water(text)
#                 if ae.entity in processed_text:
#                     annotated_texts[cpt].append(processed_text)
#                     c += 1
#                     print('Added {0}th document'.format(c))
#                     if c >= doc_num:
#                         break
#         pickle.dump(annotated_texts, open('annotated_data/' + ae.entity + '_texts', 'wb'))
#         print('Done with ', ae.entity)
