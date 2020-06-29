from difflib import SequenceMatcher

__all__ = ['sort_results']


def mapper(item):
    return item.get('title').lower(), item


def sort_results(results, term, limit=5):
    def add_title(item):
        if not item.get('title'):
            item['title'] = item.get('english', item.get('japanese', item.get('synonyms', 'No Title')))
        item['ratio'] = SequenceMatcher(None, item.get('title').lower(), term).ratio()
        return item

    results = sorted(list(map(add_title, results)), key=lambda item: item.get('ratio', 0), reverse=True)
    return results[:limit]
