import difflib

__all__ = ['sort_results']


def mapper(item):
    return item.get('title').lower(), item


def add_title(item):
    if not item.get('title'):
        item['title'] = item.get('english', item.get('japanese', item.get('synonyms', 'No Title')))
    return item


def sort_results(results, term):
    results = list(map(add_title, results))
    checks = dict(map(mapper, results))
    high_rate = difflib.get_close_matches(term.lower(), checks.keys())

    def check(item):
        if item.get('title').lower() in high_rate:
            return False
        else:
            return item

    results = []
    for high in high_rate:
        results.append(checks.pop(high))

    return [*results, *list(filter(check, results))]
