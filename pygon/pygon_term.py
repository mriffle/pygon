# pygon_term.py
class PyGONTerm:
    def __init__(self, term_id, name, definition, parents=None):
        self.id = term_id
        self.name = name
        self.definition = definition
        if parents is None:
            parents = []
        self.parents = list(parents)