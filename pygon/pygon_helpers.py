import sys
import urllib.request
from urllib.error import URLError
from urllib.parse import urljoin
from io import StringIO
from collections import defaultdict
from .pygon_term import PyGONTerm


def download_obo_file():
    """
    Download the .obo file from the specified URL.

    Returns:
        StringIO: The contents of the downloaded .obo file as a StringIO object.

    Raises:
        URLError: If there is an error downloading the file.
    """
    url = 'http://purl.obolibrary.org/obo/go/go-basic.obo'
    try:
        print(f"Downloading .obo file from {url}...")
        with urllib.request.urlopen(url) as response:
            obo_data = response.read().decode('utf-8')
        print("Download complete.")
        return StringIO(obo_data)
    except URLError as exception:
        print(f"Error downloading .obo file: {exception}")
        raise


def load_obo(obo_file, terms, children, ignore_obsolete):
    """
    Load the Gene Ontology data from the .obo file.

    Args:
        obo_file (StringIO): The contents of the .obo file.
        terms (dict): A dictionary to store the loaded GO terms.
        children (defaultdict): A dictionary to store the parent-child relationships between GO terms.
        ignore_obsolete (bool): Whether to ignore obsolete terms.
    """
    root_terms = ['biological_process', 'molecular_function', 'cellular_component']
    prefix_actions = {
        'id:': lambda v: v[4:].strip(),
        'name:': lambda v: v[6:].strip(),
        'def:': lambda v: v[5:].strip(),
        'alt_id:': lambda v: alt_ids.append(v[8:].strip()),
        'is_obsolete:': lambda v: v[13:].strip() == 'true',
        'is_a:': lambda v: parents.add(handle_is_a(v[6:], term_id, children))
    }
    term_id = ''
    name = ''
    definition = ''
    alt_ids = []
    is_obsolete = False
    has_is_a = False
    parents = set()
    for line in obo_file:
        line = line.strip()
        if line == '[Term]':
            if term_id != '':
                if not ignore_obsolete or not is_obsolete:
                    create_term(term_id, name, definition, alt_ids, is_obsolete, has_is_a, root_terms, terms, parents)
            term_id = ''
            name = ''
            definition = ''
            alt_ids = []
            is_obsolete = False
            has_is_a = False
            parents = set()
        else:
            for prefix, action in prefix_actions.items():
                if line.startswith(prefix):
                    value = action(line)
                    if prefix == 'id:':
                        term_id = value
                    elif prefix == 'name:':
                        name = value
                    elif prefix == 'def:':
                        definition = value
                    elif prefix == 'is_obsolete:':
                        is_obsolete = value
                    elif prefix == 'is_a:':
                        has_is_a = True
                    break
    if term_id != '':
        if not ignore_obsolete or not is_obsolete:
            create_term(term_id, name, definition, alt_ids, is_obsolete, has_is_a, root_terms, terms, parents)

    print(f"Loaded {len(terms)} GO terms from OBO")


def handle_is_a(value, term_id, children):
    """
    Handle the 'is_a' relationship between GO terms.

    Args:
        value (str): The value of the 'is_a' line in the .obo file.
        term_id (str): The ID of the current GO term.
        children (defaultdict): A dictionary to store the parent-child relationships between GO terms.

    Returns:
        str: The ID of the parent term.
    """
    parent_id = value.split('!')[0].strip()
    if parent_id not in children:
        children[parent_id] = set()
    children[parent_id].add(term_id)
    return parent_id


def create_term(term_id, name, definition, alt_ids, is_obsolete, has_is_a, root_terms, terms, parents):
    """
    Create a new GO term object and add it to the terms dictionary.

    Args:
        term_id (str): The ID of the GO term.
        name (str): The name of the GO term.
        definition (str): The definition of the GO term.
        alt_ids (list): A list of alternative IDs for the GO term.
        is_obsolete (bool): Whether the GO term is obsolete.
        has_is_a (bool): Whether the GO term has an 'is_a' relationship.
        root_terms (list): A list of root terms in the Gene Ontology.
        terms (dict): A dictionary to store the loaded GO terms.
        parents (set): A set of parent term IDs.
    """
    if not is_obsolete:
        if not has_is_a and name not in root_terms:
            print(f"Warning: Term '{term_id}' does not have an 'is_a' property.", file=sys.stderr)
        term = PyGONTerm(term_id, name, definition, parents=parents)
        terms[term_id] = term
        for alt_id in alt_ids:
            terms[alt_id] = term


def get_ancestors(term_id, terms):
    """
    Get all the ancestors of a given GO term.

    Args:
        term_id (str): The ID of the GO term.
        terms (dict): A dictionary of loaded GO terms.

    Returns:
        set: A set of ancestor term IDs.

    Raises:
        ValueError: If the term ID is not found in the terms dictionary.
    """

    if term_id not in terms:
        return set()

    ancestors = set()
    queue = [term_id]
    while queue:
        current_term = queue.pop(0)
        if current_term not in terms:
            raise ValueError(f"Term ID '{current_term}' not found in the terms dictionary.")
        queue.extend(parent_id for parent_id in terms[current_term].parents if parent_id not in ancestors)
        ancestors.update(terms[current_term].parents)
    return ancestors


def get_descendants(term_id, children):
    """
    Get all the descendants of a given GO term.

    Args:
        term_id (str): The ID of the GO term.
        children (defaultdict): A dictionary of parent-child relationships between GO terms.

    Returns:
        set: A set of descendant term IDs.
    """
    descendants = set()
    stack = [term_id]
    while stack:
        current_term = stack.pop()
        if current_term in children:
            stack.extend(child_id for child_id in children[current_term] if child_id not in descendants)
            descendants.update(children[current_term])
    return descendants
