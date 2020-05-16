from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty,StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder
import pandas as pd
import os
import pickle

# kv = Builder.load_file("shpl.kv")

class FileChoosePopup(Popup):
    load = ObjectProperty()

class DownloadChoosePopup(Popup):
    download_to = ObjectProperty()    

class Tab(TabbedPanel):
    file_path = StringProperty("No file chosen")
    file_path_dl = StringProperty("No file chosen")
    the_popup = ObjectProperty(None)
    download_file_popup = ObjectProperty(None)

    def open_popup(self):
        self.the_popup = FileChoosePopup(load=self.load)
        self.the_popup.open()
    
    def open_popup_for_download(self):
        self.download_file_popup = DownloadChoosePopup(download_to=self.download_to)
        self.download_file_popup.open()

    def download_to(self, selection,filename_input):
        self.file_path_dl = os.path.join(selection, filename_input)
        self.download_file_popup.dismiss()
        print("Download to : ",self.file_path_dl)  

    def load(self, selection):
        self.file_path = str(selection[0])
        self.the_popup.dismiss()
        print("File selected to load : ",self.file_path)
        # check for non-empty list i.e. file selected
        if self.file_path:
            self.ids.get_file.text = self.file_path            
    
    def upload_data(self):
        self.data = pd.read_csv(self.file_path)

    def apply_model(self,model_type):
        if model_type.lower() == 'randomforest':
            Pkl_Filename = './data/finalized_model.sav'
            with open(Pkl_Filename, 'rb') as file:  
                Pickled_LR_Model = pickle.load(file)
            
            test_predict = Pickled_LR_Model.predict(self.data)
            print(test_predict)

            self.data['Predicted_Labels'] = test_predict

    def download_data(self):
        self.data.to_csv(self.file_path_dl)


class SHPLApp(App):
    def build(self):
        return Tab()

if __name__ == "__main__":
    SHPLApp().run()
