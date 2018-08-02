from PyQt5.QtWidgets import (QWidget, QApplication, QCheckBox, QPushButton,
                             QFileDialog, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5 import QtCore
import sys
import numpy as np
from functools import partial
import os
import matplotlib.pyplot as plt
import pandas as pd
import subprocess
import time

class ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(750, 500, 400, 200)
        self.setWindowTitle('QComboBox')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.muestra()

    def muestra(self):
        self.lista = [f for f in os.listdir(os.getcwd()) if f[-4:] == '.png']
        self.botnext = QPushButton('Siguiente', self)
        self.botnext.clicked.connect(partial(self.siguiente, 1))
        self.nocal = QPushButton('NoCalificar', self)
        self.nocal.clicked.connect(partial(self.siguiente, 0))
        self.botrew = QPushButton('Anterior', self)
        self.botrew.clicked.connect(partial(self.siguiente, 2))
        self.aplicar = QPushButton('Aplicar', self)
        self.aplicar.clicked.connect(self.aplica)
        self.labconta = QLabel("0 de {0}".format(len(self.lista)), self)

        self.arrcatecheck = []
        labfiltro = QLabel("Mejor filtro", self)
        self.chkcalnames = ['Buena', 'Mala', 'Posible']
        for chkname in self.chkcalnames:
            self.arrcatecheck.append(QCheckBox(chkname, self))

        self.arrfiltcheck = []
        self.lbl = QLabel("Califica la imagen", self)
        self.chkfiltnames = ['mean']
        for chkname in self.chkfiltnames:
            self.arrfiltcheck.append(QCheckBox(chkname, self))
        self.arrfiltcheck[0].setChecked(True)

        cajachecks = QVBoxLayout()
        cajachecks.addWidget(self.lbl)
        for chkbx in self.arrcatecheck:
            cajachecks.addWidget(chkbx)
        cajaboton = QVBoxLayout()
        cajaboton.addWidget(self.botnext)
        cajaboton.addWidget(self.botrew)
        cajaboton.addWidget(self.aplicar)
        cajaboton.addWidget(self.nocal)
        cajaboton.addWidget(self.labconta)
        cajafiltros = QVBoxLayout()
        cajafiltros.addWidget(labfiltro)
        for chkbx in self.arrfiltcheck:
            cajafiltros.addWidget(chkbx)

        cajaglobal = QHBoxLayout()
        cajaglobal.addLayout(cajachecks)
        cajaglobal.addLayout(cajafiltros)
        cajaglobal.addLayout(cajaboton)
        self.preparar_datos()
        self.mostrar_imagen()
        self.setLayout(cajaglobal)
        self.show()

    def preparar_datos(self):
        if not os.path.exists('calificaciones.txt'):
            self.data = pd.DataFrame(columns=['Imagen',
                                              'Filtro', 'Calificacion'])
            self.data.set_index("Imagen", inplace=True)
            self.contador = 0
        else:
            self.data = pd.read_csv('calificaciones.txt', header=0)
            self.data.set_index("Imagen", inplace=True)
            self.contador = self.lista.index(self.data.iloc[-1].name)
        print(self.data)
        print("{0} imagenes calificadas\n".format(len(self.data)))

    def siguiente(self, n):
        try:
            if self.viewer:
                self.viewer.terminate()
                self.viewer.kill()
        except:
            print("La ventana estaba cerrada")
        if n == 1:
            imagen = self.lista[self.contador]
            ind, = np.where([f.isChecked() for f in self.arrfiltcheck])[0]
            filtro = self.chkfiltnames[ind]
            ind, = np.where([f.isChecked() for f in self.arrcatecheck])[0]
            calificacion = self.chkcalnames[ind]
            self.data.ix[imagen] = [filtro, calificacion]
            self.contador += 1
            print(self.data.ix[imagen])
        elif n==2:
            self.contador -= 1
        else:
            self.contador += 1
        self.labconta.setText('{0} de {1}'.format(self.contador + 1,
                                                  len(self.lista)))
        self.limpiar_cajas()
        self.mostrar_imagen()

    def limpiar_cajas(self):
        for box in self.arrcatecheck:
            box.setChecked(False)
        for box in self.arrfiltcheck:
            box.setChecked(True)

    def mostrar_imagen(self):
        imagen = self.lista[self.contador]
        path = os.path.join(os.getcwd(), imagen)
        if sys.platform == 'linux':
            self.viewer = subprocess.Popen(['eog', path])
            time.sleep(1)
            os.system('wmctrl -lp | grep "{0}" | cut -d" " -f1 > tmp'.format(imagen[:4]))
            with open('tmp', 'r') as ftmp:
                winid = ftmp.read().replace('\n', '')
            os.system('wmctrl -i -r {0} -b toggle,maximized_vert,maximized_horz'.format(winid))
        else:
            comando = ["python", "mostrar_imagen.py"]
            self.viewer = subprocess.Popen(comando + [path])

    def aplica(self):
        self.data.to_csv('calificaciones.txt')
        self.viewer.terminate()
        self.viewer.kill()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ventana()
    ret = app.exec_()
    ex.aplica()
    os.remove('tmp')
    sys.exit(ret)
