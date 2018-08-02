import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

quita = 200
app = QApplication(sys.argv)
screen = app.primaryScreen()
size = screen.size()
label = QLabel()
label.resize(size.width() - quita, size.height() - quita)
pixmap = QPixmap(sys.argv[1])
pixmap_scaled = pixmap.scaled(size.width()-quita, size.height()-quita, Qt.KeepAspectRatio)
label.setPixmap(pixmap_scaled)
label.show()

sys.exit(app.exec_())
