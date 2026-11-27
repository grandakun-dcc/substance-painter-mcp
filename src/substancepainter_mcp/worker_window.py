"""Keep only the dedicated worker minimized, including startup window resets."""

from PySide6.QtCore import QEvent, QObject, QTimer
import substance_painter.ui as ui

_filter = None


class WorkerWindowFilter(QObject):
    def eventFilter(self, watched, event):
        if event.type() in (QEvent.Show, QEvent.WindowStateChange) and not watched.isMinimized():
            QTimer.singleShot(0, watched.showMinimized)
        return False


def start_plugin():
    global _filter
    if _filter is None:
        window = ui.get_main_window()
        _filter = WorkerWindowFilter(window)
        window.installEventFilter(_filter)
        QTimer.singleShot(0, window.showMinimized)


def close_plugin():
    global _filter
    if _filter is not None:
        ui.get_main_window().removeEventFilter(_filter)
        _filter.deleteLater()
        _filter = None
