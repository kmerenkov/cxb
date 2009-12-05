import os

import gtk, gtk.glade
import gedit

from buffers import BuffersManager


GLADE_TEMPLATE_FILE = os.path.dirname(__file__) + "/cxb.glade"
MENU_TEMPLATE = """<ui>
<menubar name="MenuBar">
    <menu name="CXBMenu" action="CXBMenuAction">
        <placeholder name="CXB Options">
            <menuitem name="CXB" action="CXBAction"/>
        </placeholder>
    </menu>
</menubar>
</ui>
"""


class PluginWindow(object):
    plugin = None
    gedit_window = None
    plugin_window = None
    template = None
    text_entry = None
    hit_list = None
    list_model = gtk.ListStore(str, str)
    action_group = gtk.ActionGroup("CXBPluginActions")
    menu_action = gtk.Action(name="CXBMenuAction", label="Snap", tooltip="Snap tools", stock_id=None )
    snapopen_action = gtk.Action(name="CXBAction", label="Switch...\t", tooltip="Switch between buffers", stock_id=gtk.STOCK_OPEN)
    ui_id = None # ???
    buffer_manager = BuffersManager()


    def __init__(self, plugin, gedit_window):
        self.plugin = plugin
        self.gedit_window = gedit_window
        self.init_menu()
        self.init_glade()

    def cleanup(self):
        self.remove_menu()

    def init_menu(self):
        manager = self.gedit_window.get_ui_manager()
        self.action_group.add_action(self.menu_action)
        self.snapopen_action.connect("activate", lambda a: self.on_snapopen_action())
        self.action_group.add_action_with_accel(self.snapopen_action, "<Ctrl>b" )
        manager.insert_action_group(self.action_group, 0)
        self.ui_id = manager.new_merge_id()
        manager.add_ui_from_string(MENU_TEMPLATE)
        manager.ensure_update()

    def remove_menu(self):
        manager = self.gedit_window.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()

    def init_glade(self):
        self.template = gtk.glade.XML(GLADE_TEMPLATE_FILE)
        # setup window
        self.plugin_window = self.template.get_widget("CXBWindow")
        self.plugin_window.connect("key-release-event", self.on_window_key)
        self.plugin_window.set_transient_for(self.gedit_window)
        # setup buttons
        self.template.get_widget("ok_button").connect("clicked", self.switch_to_buffer)
        self.template.get_widget("cancel_button").connect("clicked", lambda a: self.plugin_window.hide())
        #setup entry field
        self.text_entry = self.template.get_widget("entry_name")
        self.text_entry.connect("key-release-event", self.on_pattern_entry)
        #setup list field
        self.hit_list = self.template.get_widget("hit_list")
        self.hit_list.connect("select-cursor-row", self.on_select_from_list)
        self.hit_list.connect("button_press_event", self.on_list_mouse)
        self.hit_list.set_model(self.list_model)
        column = gtk.TreeViewColumn("Name" , gtk.CellRendererText(), text=0)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column2 = gtk.TreeViewColumn("File", gtk.CellRendererText(), text=1)
        column2.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.hit_list.append_column(column)
        self.hit_list.append_column(column2)
        self.hit_list.get_selection().set_mode(gtk.SELECTION_BROWSE)

    def on_window_key(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.plugin_window.hide()
    
    def fill_in_results(self):
        def make_row(document):
            return [self.buffer_manager.format_name(doc.get_uri_for_display()),
                    self.buffer_manager.format_uri(doc.get_uri())]
        pattern = self.text_entry.get_text()
        documents = self.buffer_manager.find_matching_buffers(pattern)
        self.list_model.clear()
        for doc in documents:
            self.list_model.append(make_row(doc))

    def on_pattern_entry(self, widget, event):
        if event.keyval == gtk.keysyms.Return:
            self.switch_to_buffer(event)
            return
        self.fill_in_results()
        self.hit_list.get_selection().select_path((0,))

    #mouse event on list
    def on_list_mouse(self, widget, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.switch_to_buffer(event)

    #key selects from list (passthrough 3 args)
    def on_select_from_list(self, widget, event):
        self.switch_to_buffer(event)

    def switch_to_buffer(self, event):
        _list_store, rows = self.hit_list.get_selection().get_selected_rows()
        if rows:
            doc_idx = rows[0][0]
            self.buffer_manager.switch_to_buffer_by_index(self.gedit_window, doc_idx)
            self.text_entry.set_text('')
            self.plugin_window.hide()

    #on menuitem activation (incl. shortcut)
    def on_snapopen_action(self):
        self.plugin_window.set_title("Switch to a buffer...")
        self.fill_in_results()
        self.plugin_window.show()
        self.text_entry.select_region(0, -1)
        self.text_entry.grab_focus()

