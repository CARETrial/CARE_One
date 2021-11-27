# Imports
from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib

# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')

"""
    Data History line plot chart widget
"""
class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.05, right=0.975, top=1.0, bottom=0.090)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)            # Inherit from QWidget
        self.canvas = MplCanvas()                           # Create canvas object
        self.toolbar = NavigationToolbar(self.canvas, self) # create mpl toolbar control
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.toolbar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

"""
    Data History boxplot chart widget
"""
class MplCanvas2(Canvas):
    def __init__(self):
        self.fig = Figure(figsize=(1, 6))
        self.ax1 = self.fig.add_subplot(1, 6, 1)
        self.ax2 = self.fig.add_subplot(1, 6, 2)
        self.ax3 = self.fig.add_subplot(1, 6, 3)
        self.ax4 = self.fig.add_subplot(1, 6, 4)
        self.ax5 = self.fig.add_subplot(1, 6, 5)
        self.ax6 = self.fig.add_subplot(1, 6, 6)
        self.fig.subplots_adjust(left=0.05, right=0.99, wspace=0.6)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

class MplWidget2(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)            # Inherit from QWidget
        self.canvas = MplCanvas2()                           # Create canvas object
        self.toolbar = NavigationToolbar(self.canvas, self) # create mpl toolbar control
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.toolbar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

"""
   Patient overview boxplot trend chart widget
"""
class MplCanvas3(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Hour (24-hour notation)')
        self.fig.subplots_adjust(left=0.06, right=0.99,bottom=0.22)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

# Matplotlib widget
class MplWidget3(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)            # Inherit from QWidget
        self.canvas = MplCanvas3()                           # Create canvas object
        self.toolbar = NavigationToolbar(self.canvas, self) # create mpl toolbar control
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.toolbar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

"""
    Data History Asynchrony analysis pie chart widget
"""
class MplCanvas4(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.000, right=1.000, top=0.920, bottom=0.000)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

# Matplotlib widget
class MplWidget4(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)            # Inherit from QWidget
        self.canvas = MplCanvas4()                           # Create canvas object
        self.toolbar = NavigationToolbar(self.canvas, self) # create mpl toolbar control
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.toolbar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

"""
    Data History boxplot chart widget
"""
class MplCanvas5(Canvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(top=0.88,
                                bottom=0.11,
                                left=0.16,
                                right=0.9,
                                hspace=0.2,
                                wspace=0.2)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

class MplWidget5(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)            # Inherit from QWidget
        self.canvas = MplCanvas5()                           # Create canvas object
        self.toolbar = NavigationToolbar(self.canvas, self) # create mpl toolbar control
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.toolbar)
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)