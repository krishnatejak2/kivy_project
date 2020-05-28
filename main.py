from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from functools import partial
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import (ScreenManager, Screen, NoTransition, 
SlideTransition, CardTransition, SwapTransition, 
FadeTransition, WipeTransition, FallOutTransition, RiseInTransition)  
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.stacklayout import StackLayout
from kivy.lang import Builder

from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty,NumericProperty
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

import pandas as pd
import os
import pickle
import sqlite3,csv
import math 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

class excelCell(Label):
    pass
class excelHeader(Button):
    pass
class FileChoosePopup(Popup):
    load = ObjectProperty()
class DownloadChoosePopup(Popup):
    download_to = ObjectProperty()    
class DataSelectPopup(Popup):
    data_check_popup = ObjectProperty() 
class ChangePageNumberPopup(Popup):
    change_page = ObjectProperty()

class ChangeDataPopup(Popup):
    change_data = ObjectProperty()
    val_list = []

    conn = sqlite3.connect("./data/MyData.db")
    cursor = conn.cursor()

    cursor.execute("select Distinct Predicted_Labels from main.Model_Results;")
    data = cursor.fetchall()

    for row in data:
        for element in row:
            val_list.append(str(element))
    
    conn.commit
    conn.close
 
class TextInputPopup(Popup):
    obj = ObjectProperty(None)
    obj_text = StringProperty("")

    def __init__(self, obj, **kwargs):
        super(TextInputPopup, self).__init__(**kwargs)
        self.obj = obj
        self.obj_text = obj.text

class GoBackPopup(Popup):
    go_back_to = ObjectProperty(None)   

    def change_screen(self):   
        sm.current = "model"
        sm.transition.direction = "right"


class ImportScreen(Screen):
    data = ObjectProperty(None,force_dispatch = True)
    the_popup = ObjectProperty(None)
    file_path = StringProperty(None)
 
    def open_popup(self,*args):
        self.the_popup = FileChoosePopup(load=self.load)
        self.the_popup.open()

    def load(self, selection,*args):
        self.file_path = str(selection[0])
        self.the_popup.dismiss()
        print("File selected to load : ",self.file_path)
        # check for non-empty list i.e. file selected
        if self.file_path:
            self.ids.get_file.text = self.file_path

    def upload_data(self,*args):
        if self.ids.get_file.text:
            self.file_path = self.ids.get_file.text
        self.data = pd.read_csv(self.file_path)
        # self.data.to_csv("./data/DataReadFromFile.csv",index=False)
        print("Data uploaded from : ",self.file_path)

        conn = sqlite3.connect("./data/MyData.db")
        cursor = conn.cursor()
        self.data.to_sql("my_data", conn, if_exists="replace")

        cursor.execute("""Drop table IF EXISTS main.Uploaded_Data_Table;""")
        cursor.execute("""create table main.Uploaded_Data_Table as select * from my_data""")
        conn.commit
        conn.close

    def data_check_upload(self,*args):
        
        if self.ids.get_file.text == '' :
            uploadData_popup()
        else : 
            self.upload_data()

    def data_check_popup(self,*args):
        
        if self.data is None:
            if self.ids.get_file.text == '' :
                invalidData_popup()
            if self.ids.get_file.text != '' :
                uploadData_popup()
        else : 
            sm.current = "model"

class ModelScreen(Screen):
    data = ObjectProperty(None,force_dispatch = True)
    selectmodel = ObjectProperty(None)
    selectlabel = ObjectProperty(None)
    mainbutton_model = ObjectProperty(None)
    mainbutton = ObjectProperty(None)
    class_label = ObjectProperty(None)
    model_label = ObjectProperty(None)

    ref_num = 0
    
    def __init__(self, *args, **kwargs):
        super(Screen, self).__init__(*args, **kwargs)
        # self.data = screenObject.data

    def on_enter(self,*args):
        self.ref_num = self.ref_num+1
        conn = sqlite3.connect("./data/MyData.db")
        cursor = conn.cursor()
        # self.data= pd.read_csv("./data/DataReadFromFile.csv")
        self.data = pd.read_sql_query("select * from main.Uploaded_Data_Table;", conn)
        self.data.drop(columns = ['index'],inplace = True)
        conn.commit
        conn.close

        if self.ref_num>1:
            self.remove_widgets()
        self.run_dd_selectmodel()
        self.run_dd_selectlabel()
        
    def run_dd_selectmodel(self,*args):

        self.dropdown = DropDown()
        notes = ['RandomForest']
        for note in notes:
            btn = Button(text=note, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(btn)
        self.mainbutton_model = Button(text='Select Model', size_hint=(1, 1))
        # print('yay' )

        self.mainbutton_model.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton_model, 'text', x))
        self.selectmodel.add_widget(self.mainbutton_model)

    def run_dd_selectlabel(self,*args):
        print("Data : ",self.data.head())
        notes = ['No Data'] if self.data is None else self.data.columns

        self.dropdown_2 = DropDown()
        # notes = ['RandomForest']
        for note in notes:
            btn = Button(text=note, size_hint_y=None, height=40)
            btn.bind(on_release=lambda btn: self.dropdown_2.select(btn.text))
            self.dropdown_2.add_widget(btn)
        self.mainbutton_label = Button(text='Select Label', size_hint=(1, 1))
        # print('yay' )

        self.mainbutton_label.bind(on_release=self.dropdown_2.open)
        self.dropdown_2.bind(on_select=lambda instance, x: setattr(self.mainbutton_label, 'text', x))
        self.selectlabel.add_widget(self.mainbutton_label)    

    def remove_widgets(self,*args):
        # self.selectlabel.remove_widget(self.class_label)
        self.selectlabel.remove_widget(self.mainbutton_label)

        # self.selectmodel.remove_widget(self.model_label)
        self.selectmodel.remove_widget(self.mainbutton_model)
        
    def apply_model(self,*args):
        self.remove_widgets()

        conn = sqlite3.connect("./data/MyData.db")
        cursor = conn.cursor()

        cursor = conn.cursor()
        model_data = pd.DataFrame({"Model": [self.mainbutton_model.text.lower()], 
                                "Target_Variable" : [self.mainbutton_label.text]
                                })
        model_data.to_sql("my_data", conn, if_exists="replace")

        cursor.execute("""Drop table IF EXISTS main.Model_Table;""")
        cursor.execute("""create table main.Model_Table as select * from my_data""")
        

        if self.mainbutton_model.text.lower() == 'randomforest':
            try : 
                label_name = self.mainbutton_label.text
                X = self.data.loc[:, self.data.columns != label_name].values
                y = self.data[label_name].values

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

                sc = StandardScaler()
                X_train = sc.fit_transform(X_train)
                X_total = sc.transform(X)

                clf = RandomForestClassifier(n_estimators=20, random_state=0)
                clf.fit(X_train, y_train)
                y_pred = clf.predict(X_total)

                self.data['Predicted_Labels'] = y_pred
                # self.data.to_csv("./data/PredictedData.csv",index = False)
                self.data.to_sql("my_data", conn, if_exists="replace")

                cursor.execute("""Drop table IF EXISTS main.Model_Results;""")
                cursor.execute("""create table main.Model_Results as select * from my_data""")

                print(confusion_matrix(self.data[label_name],y_pred))
                print(classification_report(self.data[label_name],y_pred))
                print(accuracy_score(self.data[label_name], y_pred))

                sm.current = "analyse"
                sm.transition.direction = "left"
            
            except :
                selectRightColumn_popup()
                sm.current = "model"
                self.remove_widgets()
                self.on_enter()
                
        
        conn.commit
        conn.close

class AnalyseScreen(Screen):
    data_items = ListProperty([])
    page_number = 1
    page_limit = 50
    page_start = 1
    ref_num = 0
    # print("In AnalyseScreen")
    goback_popup = ObjectProperty(None)
    changepage_popup = ObjectProperty(None)
    changedata_popup = ObjectProperty(None)

    def get_column_details(self,*args):
        conn = sqlite3.connect("/Users/krishnateja/Project/Kivy_Project/kivy_project/data/MyData.db")
        cursor = conn.cursor()
        #select data specifics
        cursor.execute("select count(*) from pragma_table_info('Model_Results');")
        no_columns = cursor.fetchone()[0]
        col_names = []
        columns_name = cursor.execute("select name from pragma_table_info('Model_Results');")
        for col in columns_name:
            col_names.append(col[0])

        conn.commit()
        conn.close()
        return [no_columns,col_names]

    def change_page_from_kivy(self,*args):
        self.changepage_popup = ChangePageNumberPopup(change_page=self.change_page)
        self.changepage_popup.open()
    
    def change_page(self,selection,*args):
        self.page_number = int(selection)
        self.ids.pagenumber_id.text = str(selection)
        self.load_model_data()

    def go_to_first_page(self,selection,*args):
        # self.ids.pagenumber_id.text = selection
        self.page_number = 1
        self.ids.pagenumber_id.text = str("1")
        self.load_model_data()
        
    def go_to_previous_page(self,selection,*args):
        if int(selection) == 1 :
            pass
        else :
            self.page_number = int(selection)-1
            self.ids.pagenumber_id.text = str(self.page_number)
            self.load_model_data()

    def go_to_next_page(self,selection,*args):
        self.page_number = int(selection)+1
        self.ids.pagenumber_id.text = str(self.page_number)
        # print(self.page_number)
        self.load_model_data()

    def go_to_last_page(self,selection,*args):
        self.page_number = math.ceil(len(self.data_all)/self.page_limit)
        self.ids.pagenumber_id.text = str(self.page_number)
        self.load_model_data()
            
    def go_back_to(self,*args):
        self.goback_popup = GoBackPopup(go_back_to=self.go_back_to)
        self.goback_popup.open()
    
    def on_enter(self,*args):  
        self.load_model_data()

    def load_model_data(self,*args):  
        
        self.cells.clear_widgets()
        conn = sqlite3.connect("/Users/krishnateja/Project/Kivy_Project/kivy_project/data/MyData.db")
        cursor = conn.cursor()
        
        # get number of columns from model_results from db
        cursor.execute("select count(*) from pragma_table_info('Model_Results');")
        columns = cursor.fetchone()
        if columns is None:
            raise ValueError('No Result!! check the database!')
        else : 
            no_cols = columns[0]

        # get column_names from model_results from db
        columns_name = cursor.execute("select name from pragma_table_info('Model_Results');")
        
        self.cells.cols = no_cols
        for col in columns_name:
            self.cells.add_widget(excelHeader(text=str(col[0])))
        
        self.page_start = (self.page_number-1)*self.page_limit

        self.data = pd.read_sql_query("""select * from main.Model_Results where "index" between {} and {};""".format(self.page_start,self.page_start+self.page_limit-1), conn)
        self.data_all = pd.read_sql_query("""select * from main.Model_Results""", conn)

        self.notes = ['No Data'] if self.data is None else self.data_all.iloc[:,len(self.data.columns)-1].unique()
        # print("Notes :",self.notes)
        # self.buttons = []
        for i in range(len(self.data)):
            for j in range(len(self.data.iloc[i,:])):
                if j == len(self.data.columns)-1:
                    select_button = Button(text=str(self.data.iloc[i,j]), size_hint=(1, 1))
                    select_button.bind(on_release=partial(self.HoldButtonNum,  self.data.iloc[i,0],self.notes))
                    self.cells.add_widget(select_button)  
                                                                       
                else:
                    self.cells.add_widget(excelCell(text=str(self.data.iloc[i,j])))

    def HoldButtonNum(self, *args,**kwargs):
        # print('Button index in list:',  x)
        self.button_index = args[0]
        self.notes = args[1]
        # print(self.notes)
        self.changedata_popup = ChangeDataPopup(change_data = self.change_data) # change_data=self.change_data
        # self.changedata_popup = ChangeDataPopup(get_labels = self.get_labels)
        self.changedata_popup.open()

    def change_data(self,selection,*args):
        
        self.notes = self.notes
        col_details = self.get_column_details()
        no_cols = col_details[0]
        names_list = col_details[1]
        #select data specifics
        if no_cols is None:
            raise ValueError('No Result!! check the database!')
        else : 
            id_row = self.button_index

        if selection == 'Select Label':
            print('No Label Selected!')
            selectLabel_popup()
        else :
            conn = sqlite3.connect("/Users/krishnateja/Project/Kivy_Project/kivy_project/data/MyData.db")
            cursor = conn.cursor()
            cursor.execute("""Update main.Model_Results set Predicted_Labels = %d where "index" = %d ;""" % (int(selection),id_row))
            conn.commit()
            conn.close()
            self.load_model_data(self.page_number)


    def re_train(self):         
        self.cells.clear_widgets()

        conn = sqlite3.connect("./data/MyData.db")
        cursor = conn.cursor()

        model_info_data = pd.read_sql_query("select * from main.Model_Table;", conn)
        model_info_data.drop(columns = ['index'],inplace = True)

        model_data = pd.read_sql_query("select * from main.Model_Results;", conn)
        model_data.drop(columns = ['index'],inplace = True)

        if model_info_data.Model[0] == 'randomforest':
            label_name = model_info_data.Target_Variable[0]
            X = model_data.loc[:, model_data.columns != label_name].values
            y = model_data[label_name].values

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

            sc = StandardScaler()
            X_train = sc.fit_transform(X_train)
            X_total = sc.transform(X)

            clf = RandomForestClassifier(n_estimators=20, random_state=0)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_total)

            model_data['Predicted_Labels'] = y_pred
            model_data.to_sql("my_data", conn, if_exists="replace")

            cursor.execute("""Drop table IF EXISTS main.Model_Results;""")
            cursor.execute("""create table main.Model_Results as select * from my_data""")

            print(confusion_matrix(model_data[label_name],y_pred))
            print(classification_report(model_data[label_name],y_pred))
            print(accuracy_score(model_data[label_name], y_pred))
            
            self.page_number = 1
            self.load_model_data()

        conn.commit
        conn.close


class ExportScreen(Screen):
    # data = ObjectProperty(None)
    def on_enter(self,*args):  
        conn = sqlite3.connect("/Users/krishnateja/Project/Kivy_Project/kivy_project/data/MyData.db")
        cursor = conn.cursor()

        # cursor.execute("SELECT * FROM main.Model_Results ORDER BY 1 ASC")
        self.data = pd.read_sql_query("select * from main.Model_Results ORDER BY 1 ASC;", conn)
        self.data.drop(columns = ['index'],inplace = True)

        conn.commit
        conn.close

    def data_check_popup(self,*args):
        
        if self.ids.get_save_file_name.text == '' :
            downloadData_popup()
        else : 
            self.download_data(self.ids.get_save_file_name.text)  

    def open_popup_for_download(self,*args):
        self.download_file_popup = DownloadChoosePopup(download_to=self.download_to)
        self.download_file_popup.open()

    def download_to(self, selection,indicator,*args):
        if str(indicator) == '1' :
            self.file_path_dl = str(selection)
        else :
            self.file_path_dl = str(selection[0])
        self.download_file_popup.dismiss()
        print("Download to location: ",self.file_path_dl)
        if self.file_path_dl:
            self.ids.get_save_file_name.text = self.file_path_dl    

    def download_data(self,filename_input,*args):
        # self.file_path_dl = os.path.join(self.file_path_dl,filename_input)
        self.data.to_csv(filename_input)
        print("Downloaded to : ",filename_input)

def invalidData_popup():
    pop = Popup(title='Invalid Data Input',
                content=Label(text='Select a csv file to continue'),
                size_hint=(None, None), size=(500, 500))
    pop.open()

def uploadData_popup():
    pop = Popup(title='Upload the selected File',
                content=Label(text='Click on Upload to continue!'),
                size_hint=(None, None), size=(500, 500))
    pop.open()

def downloadData_popup():
    pop = Popup(title='Select a Download Location!',
                content=Label(text='Click on Export to continue!'),
                size_hint=(None, None), size=(500, 500))
    pop.open()

def selectLabel_popup():
    pop = Popup(title='Message!',
                content=Label(text='Select a Label from Dropdown!'),
                size_hint=(None, None), size=(500, 500))
    pop.open()

def selectRightColumn_popup():
    pop = Popup(title='Message!',
                content=Label(text='Select right target column!'),
                size_hint=(None, None), size=(500, 500))
    pop.open()

class MyScreenManager(ScreenManager):
    pass

kv = Builder.load_file("shpl_layout.kv")
sm = MyScreenManager()
sm.add_widget(ImportScreen(name="import"))
sm.add_widget(ModelScreen(name="model"))
sm.add_widget(AnalyseScreen(name="analyse"))
sm.add_widget(ExportScreen(name="export"))
sm.current = "import"


class SHPLApp(App):
    def build(self):
        return sm

if __name__ == "__main__":
    SHPLApp().run()
