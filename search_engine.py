def binary_search(arr, word, case_sensitive=False):
    """
    Returns the index in an array of KWIC indices 
    """

    # Force lowercase if case insensitive
    if not case_sensitive:
        word = word.lower()

    return recursive_binary_search(arr, word, 0, len(arr) - 1, case_sensitive)


def recursive_binary_search(array, word, left, right, case_sensitive):
    """
    Recursively performs binary search on an array of indices. Comparisons
    are done based on alphabetical order of current "mid" value and the word
    to search for.
    :param array: list of strings to search in
    :param word: string to search for
    :param left: left possible index of word in array
    :param right: right possible index of word in array
    :param case_sensitive: True if case sensitivity should be enforced
    :return: the index that the word is contained at, -1 if not found.
    """

    # Stop if no indices left to search
    if right < left:
        return -1

    # Compute middle index
    mid = int((left + right) / 2)
    # Get middle word
    mw = array[mid][0].split(' ')[0]
    # Force lowercase if case insensitive
    if not case_sensitive:
        mw = mw.lower()

    # Return desired index accordingly
    if mw == word:
        return mid
    if word < mw.lower():
        return recursive_binary_search(array, word, left, mid - 1, case_sensitive)
    if word > mw.lower():
        return recursive_binary_search(array, word, mid + 1, right, case_sensitive)


def parse_keyword_combinations(search_query):
    """
    Parses the given query and determines what groupings of tokens must appear
    in returned search results. Output consists of a list, where each member is
    a list of tokens. The contents of one sub-list indicates queries where all
    contained tokens must match for any given result.
    :param search_query: a string of space separated keywords
    :return: a tuple containing a list of clauses, where each clause is a list of
    keywords AND'd together and the clauses themselves are OR'd together, and a set
    of strings containing the keywords that have been NOT'd.
    """

    # Tokenize search query
    tokenized = search_query.split(' ')
    # ORs are implied; filter them out
    tokenized = [term for term in tokenized if term != "OR"]
    # Remove leading/trailing ANDs
    if len(tokenized) > 0 and tokenized[0] == 'AND':
        tokenized.pop(0)
    if len(tokenized) > 0 and tokenized[-1] == 'AND':
        tokenized.pop()
    # Remove trailing NOT
    if len(tokenized) > 0 and tokenized[-1] == 'NOT':
        tokenized.pop()

    # Find locations of keyword "NOT"
    not_locations = [i for i in range(len(tokenized)) if tokenized[i] == 'NOT']
    # Get list of terms that are to be negative
    negations = set([tokenized[i + 1] for i in not_locations])
    # NOT terms and associate keywords can now be removed
    for i in not_locations[::-1]:
        tokenized.pop(i + 1)  # keyword
        tokenized.pop(i)  # NOT

    # Find locations of actual keywords
    keyword_locations = [i for i in range(len(tokenized)) if tokenized[i] != 'AND']
    # Each clause if a series of terms ANDed together
    clauses, clause_num = [], 0
    for pos in range(len(keyword_locations)):
        # See if new sublist needs to be made
        if clause_num == len(clauses):
            clauses.append([])
        # Add current keyword to current AND chain
        clauses[clause_num].append(tokenized[keyword_locations[pos]])
        # If next keyword is next in tokenized
        if pos + 1 < len(keyword_locations) and keyword_locations[pos + 1] == keyword_locations[pos] + 1:
            # New clause will begin
            clause_num += 1

    # Convert to simple space-separate strings
    # for i in range(len(clauses)):
    #     clauses[i] = ' '.join(clauses[i])

    # Return list of OR'd AND clauses and list of blacklisted words
    return clauses, negations


def contains_words(index_string, words, case_sensitive):
    """
    Determines if the given index_string contains all tokens within words.
    :param index_string: The string within which to search for tokens
    :param words: The list of tokens to find in the index_string
    :param case_sensitive: True if differences in case matter, False otherwise
    :return: True if all words are found in the index_string, False otherwise
    """

    # Base case
    if len(words) == 0:
        return True

    # Remove duplicates, hash contents
    words = set(words)
    # Case sensitivity
    if case_sensitive:
        index_string = index_string.lower()

    # Iterate through index_string
    for token in index_string.split(' '):
        # Case sensitivity
        if case_sensitive:
            token = token.lower()
        # Check this is one of the words
        if token in words:
            # Stop checking for that word
            words.remove(token)
            # All words found? Return True
            if len(words) == 0:
                return True

    return False


def test_querying():
    # Set case sensitivity setting
    sensitivity = input('Type "1" to enable case sensitivity: ') == '1'
    query = input('Search Query: ')
    for token in query.split(' '):
        index = binary_search(indices, token, case_sensitive=sensitivity)
        if index == -1:
            print('{} not found.'.format(token))
        else:
            print('{} found at index {}.'.format(token, index))


def test_op_parsing():
    query = input('Search Query: ')
    c, n = parse_keyword_combinations(query)

    print('AND combinations:')
    for comb in c:
        print(comb)

    print('\nNOT words:')
    for word in n:
        print(word)


if __name__ == '__main__':
    # dummy index table
    indices = sorted([
        ('bunny monday', ['apple.com', 'material.io']),
        ('cat', ['google.com']),
        ('dog', ['microsoft.com']),
        ('engine', ['twitch.tv']),
        ('hard wall', ['stackoverflow.com', 'nintendo.com']),
        ('jump', ['youtube.com']),
        ('monday bunny', ['apple.com', 'material.io']),
        ('tuesday', ['dbrand.com']),
        ('wall hard', ['stackoverflow.com', 'nintendo.com']),
    ], key=lambda s: s[0].lower())

    query = input('Search Query: ')
    clause_list, n = parse_keyword_combinations(query)
    cs = (input('Case sensitive? (y/n) ').lower() + ' ')[0] == 'y'

    results = []
    # go through each clause
    for c in clause_list:
        # find matching index position based on first term in clause
        index = binary_search(indices, c[0], case_sensitive=cs)
        # Ignore if no initial match found
        if index == -1:
            continue
        # Ignore if match contains words that were blacklisted
        if not len(n) == 0 and contains_words(indices[index][0], n, case_sensitive=cs):
            continue
        # Ignore if match doesn't have remaining words in clause
        if not contains_words(indices[index][0], c[1:], case_sensitive=cs):
            continue
        # Match must be good
        results.append(index)

    # Show all urls that would be returned
    urls = []
    for index in results:
        urls += indices[index][1]
    print(set(urls))