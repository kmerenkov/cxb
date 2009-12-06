import gedit

import os


HOME_DIR = os.path.expanduser("~")


class Queue(object):
    limit = None
    q = []


    def __init__(self, limit=None):
        self.limit = limit

    def put(self, item):
        if len(self.q) >= self.limit:
            self.q.pop(0)
        self.q.append(item)

    def pop(self):
        return self.q.pop(0) if self.q else None

    def peek(self):
        return self.q[0] if self.q else None

    def __repr__(self):
        return repr(self.q)


class BuffersManager(object):
    _window = None
    _matching_docs = []
    _history = Queue(2)


    def __init__(self, window):
        self._window = window
        gedit.Window.connect(window, 'active-tab-changed', self.on_buffers_switch)

    def get_open_documents(self):
        app = gedit.app_get_default()
        # NOTE get_documents returns all the documents from all open windows,
        # NOTE maybe we need to operate on one window instead?
        return gedit.App.get_documents(app)

    def on_buffers_switch(self, _window=None, _tab=None):
        doc = self._window.get_active_document()
        self._history.put(doc)

    def switch_to_buffer_by_index(self, index):
        tab = gedit.tab_get_from_document(self._matching_docs[index])
        self._window.set_active_tab(tab)
        #self.on_buffers_switch()

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
        # if there's anything in history, insert it before anything else
        last_used = self._history.peek()
        if last_used:
            if last_used in self._matching_docs:
                self._matching_docs.remove(last_used)
            self._matching_docs = [last_used] + self._matching_docs
        return self._matching_docs

