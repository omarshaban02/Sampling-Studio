
PATH = 'signals/mitbih_train.csv'

# pip install aspose-pdf

from re import T
from turtle import color
from PyQt5.QtCore import QTimer
import pandas as pd
import pyqtgraph as pg
import random
import pyqtgraph.exporters
import copy
import aspose.pdf as ap
import numpy as np


PATH = 'signals/mitbih_train.csv'

class Signal(object):
    def __init__(self, data:list =[], title:str= '', color:tuple = (0,0,0)) -> None:
        self.completed = False
        self.plotted_data = []
        self.data = data
        self.stop_drawing = False
        self.current_sample_index = 0 
        self.current_sample = 0
        self.is_active = False 
        self.plot_data_item = pg.PlotDataItem()
        self._color = color
        self._title = None
        self._on_click_event_handler = lambda e: None
        self.plot_data_item.setCurveClickable(state=True , width = 6) # Width is Tolerance
        self.bounds_paddings = [0.5, 10, 0.5, 5] # top, right, bottom, left
        self._bounds = [] # top, right, bottom, left
        self.mean = np.mean(self.data).round(9)
        self.variance = np.var(self.data).round(9)
        self.std = np.std(self.data).round(9)
        self.samples_number =len(self.data)

    @property
    def bounds(self):
        self._bounds = []
        self._bounds.append(max(self.data)+self.bounds_paddings[0])
        self._bounds.append(len(self.data)+self.bounds_paddings[1])
        self._bounds.append(min(self.data)-self.bounds_paddings[2])
        self._bounds.append(0-self.bounds_paddings[3])
        return self._bounds
    
    @bounds.setter
    def bounds(self, value):
        raise ValueError('this property is read only')

    @property
    def on_click_event_handler(self):
        return self._on_click_event_handler
    
    @on_click_event_handler.setter
    def on_click_event_handler(self, func):
        self._on_click_event_handler = func
        self.plot_data_item.sigClicked.connect(self._on_click_event_handler)

    @property
    def title(self):
        return self._title
    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        pen = pg.mkPen(self.color, width=2)
        self.plot_data_item.setPen(pen)

    @title.setter
    def title(self,value: pg.TextItem):  
        self._title = value 

    def setTitleColor(self, color: tuple) -> None:
        self.title.setColor(color)

    # update current sample, plot data and current sample index.
    def advance(self):
        if not(self.stop_drawing or self.completed):
            self.current_sample = self.data[self.current_sample_index]
            self.plotted_data.append(self.current_sample)
            self.current_sample_index += 1
            if len(self.data) == len(self.plotted_data):
                self.completed = True
                self.stop_drawing = True
                self.is_active = False
                self.color = self.color # when signal is completed, I make it unactivated So, I update the pen (color, width)

    def pause(self)-> None:
        self.stop_drawing = True

    def resume(self)-> None:
        self.stop_drawing = False

    def plot(self)-> None: #update the signal graph
        self.plot_data_item.clear()
        self.plot_data_item.setData(self.plotted_data)

    def restart(self)->None:
        self.plotted_data = []
        self.completed = False
        self.stop_drawing = False
        self.current_sample = 0
        self.current_sample_index = 0

class SignalViewerLogic(object):
    def __init__(self, view: pg.PlotWidget)-> None:
        
        self.view= view
        self.timer = QTimer()
        self.timer.timeout.connect(self.draw)
        self.signals: list(Signal) = [] # storing loaded signals from the file
        self.plotted_signals: list(Signal) = [] # storing all signals in the view
        self._active_signals: list(Signal) = [] # storing the active signals e.g. clicked signals
        self._rate = 20 # samples per second
        self.timer.start(int(1000/self._rate)) # The delay that the draw method takes for each call
        self.view_width = 50 #initial width
        self.view_height = 1 #initial height
        self._xRange = [0, self.view_width]
        self._yRange = [0, self.view_height]
        self._display_axis = True
        self._display_grid = True
        self.view.setXRange(self._xRange[0],self._xRange[1],padding=0)
        self.view.setYRange(self._yRange[0],self._yRange[1],padding=0)
        self.view.scene().sigMouseClicked.connect(self.ignore_focus)
        self.display_grid = True
        self.display_axis = True
        self._apply_limits = False
        self._background_color = (255, 255, 255)
        self.background_color = self._background_color
        self._display_axis_labels = True
        self.display_axis_labels = True
        self._xScrollBar = None
        self._yScrollBar = None
        self.view_limits = []
        self.apply_limits = False
        self.xScrollBar_event = lambda: self.view.setXRange(self.xScrollBar.value(), self.xScrollBar.value()+self.xRange[1]-self.xRange[0], padding=0)
        self.yScrollBar_event = lambda: self.view.setYRange(self.yScrollBar.value(), self.yScrollBar.value()+self.yRange[1]-self.yRange[0], padding=0)
        self.view.sigRangeChanged.connect(self._update_scrollBar)
        self._xScrollBar_active = False
        self._yScrollBar_active = False
        

    def set_xScrollBar_active(self,value):
        self._xScrollBar_active = value

    def set_yScrollBar_active(self,value):
        self._yScrollBar_active = value

    def ignore_focus(self, e):
        if e.double() == True:
            for signal in self.plotted_signals:
                signal.is_active = False
                pen = pg.mkPen(signal.color, width=2)
                signal.plot_data_item.setPen(pen)
    def _update_scrollBar(self):
        if not(self.xScrollBar is None or self._xScrollBar_active):
            if self.apply_limits:
                self.xScrollBar.setMaximum(int(self.view_limits[1]))
                self.xScrollBar.setMinimum(int(self.view_limits[3]))
             # update the extreme values of the scrollbar 
            xMin = int(self.xRange[0])
            xMax = int(self.xRange[1])
            if self.xScrollBar.maximum() < xMax:
                self.xScrollBar.setMaximum(xMax)
            if self.xScrollBar.minimum() > xMin:
                self.xScrollBar.setMinimum(xMin)
            self.xScrollBar.setValue(xMin)
           
        if not(self.yScrollBar is None or self._yScrollBar_active):
            if self.apply_limits:
                self.yScrollBar.setMaximum(int(self.view_limits[0]))
                self.yScrollBar.setMinimum(int(self.view_limits[2]))
            # update the extreme values of the scrollbar 
            yMin = int(self.yRange[0])
            yMax = int(self.yRange[1])
            if self.yScrollBar.maximum() < yMax:
                self.yScrollBar.setMaximum(yMax)
            if self.yScrollBar.minimum() > yMin:
                self.yScrollBar.setMinimum(yMin)
            self.yScrollBar.setValue(yMin)

    @property
    def xScrollBar(self):
        return self._xScrollBar
    
    @xScrollBar.setter
    def xScrollBar(self, value):
        self._xScrollBar = value
        self.xScrollBar.setValue(0)
        self.xScrollBar.setMinimum(0)
        self.xScrollBar.setMaximum(180)
        self.xScrollBar.sliderReleased.connect(lambda: self.set_xScrollBar_active(False))
        self.xScrollBar.sliderPressed.connect(lambda: self.set_xScrollBar_active(True))
        self.xScrollBar.valueChanged.connect(self.xScrollBar_event)

    @property
    def yScrollBar(self):
        return self._yScrollBar
    
    @yScrollBar.setter
    def yScrollBar(self,value):
        self._yScrollBar = value
        self.yScrollBar.setValue(0)
        self.yScrollBar.setMinimum(0)
        self.yScrollBar.setMaximum(1)
        self.yScrollBar.sliderReleased.connect(lambda: self.set_yScrollBar_active(False))
        self.yScrollBar.sliderPressed.connect(lambda: self.set_yScrollBar_active(True))
        self.yScrollBar.valueChanged.connect(self.yScrollBar_event)

    @property
    def display_axis_labels(self):
        return self._display_axis_labels
    
    @display_axis_labels.setter
    def display_axis_labels(self,value):
        self._display_axis_labels = value
        if self._display_axis_labels:
            self.view.setLabel('bottom', text='Frequency (Hz)')
            self.view.setLabel('left', text='Amplitude (mV)')
        else:
            self.view.setLabel('bottom', text=None)
            self.view.setLabel('left', text=None)

    @property
    def background_color(self):
        return self._background_color

    @background_color.setter
    def background_color(self,value):
        self._background_color = value
        self.view.setBackground(value) 

    @property
    def apply_limits(self):
        return self._apply_limits
    
    @apply_limits.setter
    def apply_limits(self,value):
        self._apply_limits = value
        if self._apply_limits == True:
            yMax = yMin = xMax=xMin = 0
            for signal in self.plotted_signals:
                bounds = signal.bounds
                if yMax < bounds[0]:
                    yMax = bounds[0]
                if xMax < bounds[1]:
                    xMax = bounds[1]
                if yMin > bounds[2]:
                    yMin = bounds[2]
                if xMin > bounds[3]:
                    xMin = bounds[3]
            if yMax !=0 and yMin !=0 and xMax!=0 and xMin != 0:
                self.view.setLimits(yMax = yMax, xMax = xMax, yMin = yMin, xMin = xMin)
            self.view_limits= []
            self.view_limits.append(yMax)
            self.view_limits.append(xMax)
            self.view_limits.append(yMin)
            self.view_limits.append(xMin)
        else:
            self.view.setLimits(xMin=None,xMax=None,yMin=None,yMax=None)
            self.view_limits = []

    @property
    def display_axis(self):
        return self._display_axis
    
    @display_axis.setter
    def display_axis(self, value):
        self._display_axis = value
        self.view.showAxes((self.display_axis, False, False, self.display_axis))
    @property
    def display_grid(self):
        return self._display_grid
    
    @display_grid.setter
    def display_grid(self, value):
        self._display_grid = value
        self.view.showGrid(x=self.display_grid, y=self.display_grid)

    @property
    def rate(self):
        return self._rate
    
    @rate.setter
    def rate(self, value):
        self.timer.stop()
        self._rate = value
        duration = 1000/self._rate
        self.timer.start(int(duration))
        
    @property
    def active_signals(self):
        self._active_signals = []
        for signal in self.plotted_signals:
            if signal.is_active:
                self._active_signals.append(signal)
        return self._active_signals
    
    @property
    def yRange(self)-> list:
        return self.view.viewRange()[1]
    
    @yRange.setter
    def yRange(self, value: list):
        self.view.setYRange(value[0], value[1],padding=0)
        self._yRange = self.view.viewRange()[1]

    @property
    def xRange(self)-> list:
        return self.view.viewRange()[0]
        
    
    @xRange.setter
    def xRange(self, value: list):
        self.view.setXRange(value[0], value[1],padding=0)
        self._xRange = self.view.viewRange()[0]
    
    def set_title(self, title: str):
        self.view.setTitle(title)

    def load_dataset(self,filename: str, loaded_signals: int = None)-> None:
        signals =[]
        if loaded_signals is None:
            signals = pd.read_csv(filename).to_numpy()
        else:
            signals = pd.read_csv(filename).head(loaded_signals).to_numpy()

        for s in signals:
            sig = Signal(data=s)
            self.signals.append(sig)

    #deprecated methods
    '''def zoom_in(self,scale: int)-> None:
        self.view.scaleBy(s = (scale,scale))

    def zoom_out(self,scale: int)-> None:
        f = 1/scale
        self.view.scaleBy(s = (f,f))

    

    def zoom(self,scale: int)-> None:
        v = self.view.getViewBox()
        v.scaleBy(s = (scale,scale))
        self.view.plotItem.scaleBy(s = (scale,scale))'''

    def activate_signal(self, index: int)-> None:
        signal = self.signals[index]
        signal.is_active = True
        pen = pg.mkPen(signal.color, width=3)
        signal.plot_data_item.setPen(pen)

    # the default direction is along positive y-axis as step is positive integer
    def vertical_shift(self,step: int)->None:
        self.yRange = [self.yRange[0]+step,self.yRange[1]+step]
       
    # the default direction is along positive x-axis as step is positive integer
    def horizontal_shift(self,step: int)-> None:
        self.xRange = [self.xRange[0]+step,self.xRange[1]+step]
        
    # go to the home view
    def home_view(self, scrollBar1 =None, scrollBar2 = None)-> None:
        self.xRange = [0, self.view_width]
        self.yRange = [0, self.view_height]
        

    # apply the action on the active signals
    def play(self):
        signals = self.active_signals
        for signal in signals:
            signal.resume()
        
    # apply the action on the active signals
    def pause(self):
        signals = self.active_signals
        for signal in signals:
            signal.pause()
    # apply the action on the active signals
    def replay(self):
        signals = self.active_signals
        for signal in signals:
            signal.restart()
    # apply the action on the active signals
    def set_signal_title(self,signal: Signal, text: str):
        pos_x = int(random.random()*100)
        pos_y = signal.data[pos_x]
        title = pg.TextItem(text=text,color = signal.color)
        title.setPos(pos_x,pos_y)
        signal.title = title



    # apply the action on the active signals
    def exportImage(self,name,format=None):
        exporter = pg.exporters.ImageExporter(self.view.plotItem)
        if format is None:
            exporter.export(f'{name}.png')
        else:
            exporter.export(f'{name}.{format}')
            
    def exportPDF(self,name):

        # create document
        document = ap.Document()

        # Insert a empty page in a PDF
        page = document.pages.add()

        # Add Image
        self.exportImage(name)#20, 730, 120, 830
        page.add_image(f"{name}.png", ap.Rectangle(20, 870, 550, 570,True))

         # Add Header
        header = ap.text.TextFragment("Details about the Signals")
        header.text_state.font = ap.text.FontRepository.find_font("Arial")
        header.text_state.font_size = 24
        header.horizontal_alignment = ap.HorizontalAlignment.CENTER
        #header.position = ap.text.Position(130, 720)
        header.position = ap.text.Position(120, 550)
        page.paragraphs.add(header)

        # Add table
        table = ap.Table()
        table.column_widths = "80"
        table.border = ap.BorderInfo(ap.BorderSide.BOX, 1.0, ap.Color.dark_slate_gray)
        table.default_cell_border = ap.BorderInfo(ap.BorderSide.BOX, 0.5, ap.Color.black)
        table.default_cell_padding = ap.MarginInfo(2,2,2,2)
        table.margin.bottom = 10
        table.default_cell_text_state.font = ap.text.FontRepository.find_font("Helvetica")
        headerRow = table.rows.add()
        headerRow.cells.add("Signal Name")
        headerRow.cells.add("Number of Samples")
        headerRow.cells.add("Mean")
        headerRow.cells.add("Variance")
        headerRow.cells.add("Standard Deviation")

        for i in range(headerRow.cells.count):
            headerRow.cells[i].background_color = ap.Color.gray
            headerRow.cells[i].default_cell_text_state.foreground_color = ap.Color.white_smoke

        for sig in self.plotted_signals:
            dataRow = table.rows.add()
            dataRow.cells.add(str(sig.title.toPlainText()))
            dataRow.cells.add(str(sig.samples_number))
            dataRow.cells.add(str(sig.mean))
            dataRow.cells.add(str(sig.variance))
            dataRow.cells.add(str(sig.std))
        page.paragraphs.add(table)

        # Add watermark
        artifact = ap.WatermarkArtifact()
        ts = ap.text.TextState()
        ts.font_size = 75
        ts.foreground_color = ap.Color.blue
        ts.font = ap.text.FontRepository.find_font("Courier")
        artifact.set_text_and_state("      ABDULLAH OMRAN", ts)
        artifact.artifact_horizontal_alignment = ap.HorizontalAlignment.CENTER
       # artifact.artifact_vertical_alignment = ap.VerticalAlignment.CENTER

        artifact.rotation = 45
        artifact.opacity = 0.2
        artifact.is_background = True
        document.pages[1].artifacts.append(artifact)
        # Save document
        document.save(f'{name}.pdf')


    # apply the action on the active signals
    # draw active signals
    # this method is called by the rate specified above, default is 20 times per second
    def draw(self):
        for signal in self.plotted_signals:
           if not(signal.stop_drawing or signal.completed):
                if signal.current_sample_index > self.xRange[1]:
                    self.horizontal_shift(1)
                signal.advance()
                signal.plot()
                
                if signal.title in self.view.allChildItems():
                    self.view.removeItem(signal.title)
           else:
                if signal.title not in self.view.allChildItems():
                    self.view.addItem(signal.title)
                

    def signal_onclick(self,e):
        signal = None
        for s in self.plotted_signals:
            if id(e) == id(s.plot_data_item):
                signal = s
                break    
        if signal is not None:
            if signal.is_active:
                signal.is_active = False
                pen = pg.mkPen(signal.color, width=2)
                e.setPen(pen)
            else:
                signal.is_active = True
                pen = pg.mkPen(signal.color, width=3)
                e.setPen(pen)

    # add signal to the plotted signal and active signals and start drawing it
    def add_signal(self, index: int, name: str, color = (255,255,255)):
        signal = self.signals[index]
        signal.is_active = True
        signal.color = color
        signal.on_click_event_handler = lambda e: self.signal_onclick(e)
        self.set_signal_title(signal,name)
        self.plotted_signals.append(signal)
        pen = pg.mkPen(signal.color, width=3)
        signal.plot_data_item.setPen(pen)
        self.view.addItem(signal.plot_data_item)
        # related to view limits if it is enabled
        #  update them so that the limits are applicable on the new signal
        if self.apply_limits == True:
            self.apply_limits = True
    
        
    # apply the action on the active signals
    # clear the active signals
    def remove(self):
        for signal in self.active_signals:
            self.view.removeItem(signal.plot_data_item)
            if signal.title in self.view.allchildItems():
                self.view.removeItem(signal.title)
            self.plotted_signals.remove(signal)
    # clear the screen
    def clear(self):
        self.plotted_signals = []
    
    def moveTo(self, other):
        for signal in self.active_signals:
            signal_index = self.signals.index(signal)
            other.signals.insert(signal_index,self.signals.pop(signal_index))
            self.plotted_signals.pop(self.plotted_signals.index(signal))
            self.view.removeItem(signal.title)
            self.view.removeItem(signal.plot_data_item)
            if signal not in other.plotted_signals:
                other.add_signal(other.signals.index(signal),str(signal.title.toPlainText()),signal.color)

    def hide_signal(self):
        for signal in self.active_signals:
            self.view.removeItem(signal.plot_data_item)

    def show_hidden_signal(self):
        for signal in self.active_signals:
            self.view.addItem(signal.plot_data_item)

    def clear(self):
        self.signals = []
        self.plotted_signals = []
        self.view.clear()
    def linkTo(self, other: pg.PlotWidget):
        if other is not None:
            self.view.setXLink(other.view)
            self.view.setYLink(other.view)
        else:
            self.view.setXLink(None)
            self.view.setYLink(None)
