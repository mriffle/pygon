from .pygon_helpers import download_obo_file, load_obo, get_ancestors, get_descendants
from .pygon_term import PyGONTerm


class PyGON:
    def __init__(self, obo_file=None, ignore_obsolete=False):
        self.terms = {}
        self.children = {}
        self.ignore_obsolete = ignore_obsolete

        if obo_file is None:
            obo_file = download_obo_file()

        load_obo(obo_file, self.terms, self.children, self.ignore_obsolete)

    def get_term(self, term_id):
        if term_id not in self.terms:
            raise ValueError(f"Term ID '{term_id}' not found in the terms dictionary.")
        return self.terms.get(term_id)

    def get_term_name(self, term_id):
        if term_id not in self.terms:
            raise ValueError(f"Term ID '{term_id}' not found in the terms dictionary.")
        term = self.get_term(term_id)
        return term.name if term else ''

    def get_term_definition(self, term_id):
        if term_id not in self.terms:
            raise ValueError(f"Term ID '{term_id}' not found in the terms dictionary.")
        term = self.get_term(term_id)
        return term.definition if term else ''

    def get_term_parents(self, term_id):
        if term_id not in self.terms:
            raise ValueError(f"Term ID '{term_id}' not found in the terms dictionary.")
        term = self.get_term(term_id)
        return term.parents if term else []

    def get_children(self, term_id):
        if term_id not in self.terms:
            raise ValueError(f"Term ID '{term_id}' not found in the terms dictionary.")
        return self.children.get(term_id, set())

    def get_term_ancestors(self, term_id):
        return get_ancestors(term_id, self.terms)

    def get_term_descendants(self, term_id):
        if term_id not in self.terms:
            raise ValueError(f"Term ID '{term_id}' not found in the terms dictionary.")
        return get_descendants(term_id, self.children)

