from coordinates import Coordinate, UnityCoordinate
from iw_interpret import Cell
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
from datetime import datetime
from enums import Data

class SampleTableManager:
    def __init__(self, floor):
        data = []
        columns = self._GetAPs()
        #TODO: APE and WPE are a hack. 
        # It's for looking at all predictions and comparing it to the real coords
        # This needs a real strategy
        columns.extend(['x', 'y', 'z', 'cardinal', 'timestamp', 'APE', 'WPE'])
        self.df = pd.DataFrame(data, columns=columns)
        now = datetime.now()
        self.filename = f"data/samplesf{floor}M{now.month}D{now.day}h{now.hour}m{now.hour}.csv"
        
    def _GetAPs(self):
        df = pd.read_excel(Data.AP_MAC)
        return df["AP Name"].to_list()
    
    def AddSample(self, coordinate: UnityCoordinate, cardinal: str, cells: list[Cell], ape, wpe):
        data = {}
        
        for cell in cells:
            data[cell.name] = [cell.signal]
            
        data['x'] = [coordinate.x]
        data['y'] = [coordinate.y]
        data['z'] = [coordinate.z]
        data['cardinal'] = [cardinal]
        data['timestamp'] = [datetime.now().strftime("%H:%M:%S")]   
        data['APE'] = [ape]
        data['WPE'] = [wpe]
            
        self.df = pd.concat([self.df, pd.DataFrame(data)])
    
    def WriteCSV(self):
        #Fills in any missing signals with 1 because found signals are negative
        self.df = self.df.fillna(1)
        
        self.df.to_csv(self.filename)
    