# wikilinks_loader

A package for loading data from [wikilinks](http://www.iesl.cs.umass.edu/data/wiki-links) files. The package is designed
for performing the following tasks:

1.  Finding ambiguous entities.

    Parameters:
    
    *   number of required mentions for each annotation;
    *   number of required annotations.
    
2.   Finding different annotations for a given surface form.
3.   Finding synonyms for a given annotation.

Annotation is always a link to Wikipedia URL. Redirections are taken into account, i.e. the output annotation is the
final one after all redirections.

To learn more about wikilinks dataset see the [technical report](https://web.cs.umass.edu/publication/docs/2012/UM-CS-2012-015.pdf)
or visit [their homepage](http://www.iesl.cs.umass.edu/data/wiki-links).
