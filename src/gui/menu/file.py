import os
import tkinter as tk
from src.common import config, utils
from src.gui.interfaces import MenuBarItem, Configurable
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno


class File(MenuBarItem):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'File', **kwargs)
        # parent.add_cascade(label='File', menu=self)

        self.add_command(
            label='New Routine',
            command=utils.async_callback(self, File._new_routine),
            state=tk.DISABLED
        )
        self.add_command(
            label='Save Routine',
            command=utils.async_callback(self, File._save_routine),
            state=tk.DISABLED
        )
        self.add_separator()
        self.add_command(
            label='Visual Flow Editor',
            command=utils.async_callback(self, File._open_flow_editor),
            state=tk.DISABLED
        )
        self.add_command(
            label='Convert CSV to JSON',
            command=utils.async_callback(self, File._convert_csv_to_json),
            state=tk.DISABLED
        )
        self.add_separator()
        self.add_command(label='Load Command Book', command=utils.async_callback(self, File._load_commands))
        self.add_command(
            label='Load Routine',
            command=utils.async_callback(self, File._load_routine),
            state=tk.DISABLED
        )

    def enable_routine_state(self):
        self.entryconfig('New Routine', state=tk.NORMAL)
        self.entryconfig('Save Routine', state=tk.NORMAL)
        self.entryconfig('Load Routine', state=tk.NORMAL)
        self.entryconfig('Visual Flow Editor', state=tk.NORMAL)
        self.entryconfig('Convert CSV to JSON', state=tk.NORMAL)

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot create a new routine while Auto Maple is enabled')
    def _new_routine():
        if config.routine.dirty:
            if not askyesno(title='New Routine',
                            message='The current routine has unsaved changes. '
                                    'Would you like to proceed anyways?',
                            icon='warning'):
                return
        config.routine.clear()

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot save routines while Auto Maple is enabled')
    def _save_routine():
        file_path = asksaveasfilename(initialdir=get_routines_dir(),
                                      title='Save routine',
                                      filetypes=[('*.csv', '*.csv')],
                                      defaultextension='*.csv')
        if file_path:
            config.routine.save(file_path)

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot load routines while Auto Maple is enabled')
    def _load_routine():
        if config.routine.dirty:
            if not askyesno(title='Load Routine',
                            message='The current routine has unsaved changes. '
                                    'Would you like to proceed anyways?',
                            icon='warning'):
                return
        file_path = askopenfilename(initialdir=get_routines_dir(),
                                    title='Select a routine',
                                    filetypes=[('Routine Files', '*.csv *.json'), 
                                             ('CSV files', '*.csv'),
                                             ('JSON files', '*.json')])
        if file_path:
            config.routine.load(file_path)
            import_root = Import_Settings("CBR")
            import_root.set("last_routine",file_path)
            import_root.save_config()

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot open flow editor while Auto Maple is enabled')
    def _open_flow_editor():
        from src.gui.flow_editor import FlowEditorWindow
        from src.routine.routine_converter import RoutineConverter
        
        # Convert current routine to flow format if it exists
        routine_flow = None
        if config.routine.path and len(config.routine) > 0:
            try:
                if config.routine.path.endswith('.csv'):
                    routine_flow = RoutineConverter.csv_to_json(config.routine.path)
                elif config.routine.path.endswith('.json'):
                    from src.routine.routine_schema import RoutineFlow
                    routine_flow = RoutineFlow.load(config.routine.path)
            except Exception as e:
                print(f"[!] Error loading routine into flow editor: {e}")
        
        window = FlowEditorWindow(config.gui.root, routine_flow)
        window.focus()

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot convert routines while Auto Maple is enabled')
    def _convert_csv_to_json():
        from src.routine.routine_converter import RoutineConverter
        from tkinter.messagebox import showinfo, showerror
        
        csv_path = askopenfilename(initialdir=get_routines_dir(),
                                  title='Select CSV routine to convert',
                                  filetypes=[('CSV files', '*.csv')])
        if csv_path:
            json_path = asksaveasfilename(initialdir=get_routines_dir(),
                                        title='Save as JSON',
                                        filetypes=[('JSON files', '*.json')],
                                        defaultextension='*.json')
            if json_path:
                try:
                    RoutineConverter.csv_to_json(csv_path, json_path)
                    showinfo("Success", f"Converted {os.path.basename(csv_path)} to JSON format!")
                except Exception as e:
                    showerror("Error", f"Conversion failed: {e}")

    @staticmethod
    @utils.run_if_disabled('\n[!] Cannot load command books while Auto Maple is enabled')
    def _load_commands():
        if config.routine.dirty:
            if not askyesno(title='Load Command Book',
                            message='Loading a new command book will discard the current routine, '
                                    'which has unsaved changes. Would you like to proceed anyways?',
                            icon='warning'):
                return
        file_path = askopenfilename(initialdir=os.path.join(config.RESOURCES_DIR, 'command_books'),
                                    title='Select a command book',
                                    filetypes=[('*.py', '*.py')])
        if file_path:
            config.bot.load_commands(file_path)
            import_root = Import_Settings("CBR")
            import_root.set("last_cb",file_path)
            import_root.save_config()

def get_routines_dir():
    target = os.path.join(config.RESOURCES_DIR, 'routines', config.bot.command_book.name)
    if not os.path.exists(target):
        os.makedirs(target)
    return target

class Import_Settings(Configurable):
    DEFAULT_CONFIG = {
        'last_cb': None,
        'last_routine': None
    }