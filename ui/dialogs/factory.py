# ui/dialogs/factory.py
class DialogFactory:
    @staticmethod
    def create_dialog(dialog_type, parent, **kwargs):
        dialogs = {
            'section': SeccionDialog,
            'citation': CitationDialog,
            'help': HelpDialog
        }
        dialog_class = dialogs.get(dialog_type)
        if dialog_class:
            return dialog_class(parent, **kwargs)
        raise ValueError(f"Tipo de diálogo desconocido: {dialog_type}")