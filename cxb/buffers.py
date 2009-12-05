import gedit

import os


HOME_DIR = os.path.expanduser("~")


class BuffersManager(object):
    _matching_docs = []


    def get_open_documents(self):
        app = gedit.app_get_default()
        # NOTE get_documents returns all the documents from all open windows,
        # NOTE maybe we need to operate on one window instead?
        return gedit.App.get_documents(app)

    def switch_to_buffer_by_index(self, window, index):
        tab = gedit.tab_get_from_document(self._matching_docs[index])
        window.set_active_tab(tab)

    def format_name(self, name):
        return os.path.basename(name) if name else ''

    def format_uri(self, uri):
        return uri.replace(HOME_DIR, "~") if uri else ''

    def find_matching_buffers(self, pattern):
        def match(data, pattern):
            return pattern.lower() in data.lower() if data else False
        def match_name(doc, pattern):
            return match(self.format_name(doc.get_uri_for_display()), pattern)
        def match_uri(doc, pattern):
            return match(self.format_uri(doc.get_uri()), pattern)
        docs = self.get_open_documents()
        found_in_names = [ d for d in docs if match_name(d, pattern) ]
        found_in_uris = [ d for d in docs if (match_uri(d, pattern) and d not in found_in_names) ]
        self._matching_docs = found_in_names + found_in_uris
        return self._matching_docs

