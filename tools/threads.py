from PyQt5.QtCore import QThread, pyqtSignal

from file_observer import FileObserver


class OpenFolderThread(QThread):
    def __init__(self, observer: FileObserver, directory, parent=None):
        super(OpenFolderThread, self).__init__(parent)
        self._observer = observer
        self._directory = directory

    def run(self):
        self._observer.update_file_path(self._directory)
