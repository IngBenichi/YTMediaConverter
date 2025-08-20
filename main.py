import sys
from PyQt5.QtWidgets import (
    QApplication
)
from design import SonicMingle

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SonicMingle()
    window.show()
    sys.exit(app.exec_())
