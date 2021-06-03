from pynput.keyboard import Key, Listener, Controller
import time
import pandas as pd
import os
from termcolor import colored
import pickle
import tensorflow as tf
from tensorflow import keras

class Subject():
    def __init__(self, name, autoencoder=None, best_threshold=0, scaler=None):
        self.name = name
        self.autoencoder = autoencoder
        self.best_threshold = best_threshold
        self.scaler = scaler
        
    def save_subject(self):
        path = os.path.join("subjects",self.name)
        if not os.path.exists(path):
            os.makedirs(path)
        pickle.dump(self.scaler, open(os.path.join(path,"scaler.pickle"),"wb"))
        pickle.dump(self.best_threshold, open(os.path.join(path,"best_threshold.pickle"),"wb"))
        # scaler = load(open('scaler.pickle', 'rb'))
        self.autoencoder.save(os.path.join(path,"autoencoder"))
        #autoencoder = tf.keras.models.load_model("autoencoder") 
        
    def load_subject(self):
        path = os.path.join("subjects",self.name)
        if not os.path.exists(path):
            msg = f"Subject with name \"{self.name}\" does not exist"
            raise NameError(msg)
        self.scaler = pickle.load(open(os.path.join(path,"scaler.pickle"), 'rb'))
        self.best_threshold = pickle.load(open(os.path.join(path,"best_threshold.pickle"), 'rb'))
        self.autoencoder = tf.keras.models.load_model(os.path.join(path,"autoencoder"))

class Collector():
    def __init__(self):
        self.columns = [
            "P-'.'",
            "R-'.'",
            "P-'t'",
            "R-'t'",
            "P-'i'",
            "R-'i'",
            "P-'e'",
            "R-'e'",
            "P-'5'",
            "R-'5'",
            "P-'R'",
            "R-'R'",
            "P-'o'",
            "R-'o'",
            "P-'a'",
            "R-'a'",
            "P-'n'",
            "R-'n'",
            "P-'l'",
            "R-'l'",
            "P-Key.enter",
            "R-Key.enter",
            "subject"
        ]
        self.dataframe = pd.DataFrame(columns=self.columns)
        self.series = pd.Series()
        self.password = ""
        self.subject = None
        self.end = False
        self.ignore_keys = [Key.delete, Key.ctrl_r, Key.ctrl_l,
                            Key.ctrl, Key.caps_lock, Key.alt, Key.alt_gr,
                            Key.alt_l, Key.alt_r, Key.up, Key.left, Key.right, Key.down, Key.shift_r, Key.shift_l,
                            Key.insert, Key.tab, Key.home, Key.tab]
        self.keyboard = Controller()

    def add_to_dataframe(self):
        self.series["subject"] = self.subject.name
        self.dataframe = self.dataframe.append(self.series, ignore_index=True)

    def on_press(self, key):
        if key in self.ignore_keys:
            pass
        elif key == Key.backspace:
            print(colored("\n---> Please don't use backspace","red"))
            self.series = pd.Series()
            self.password = ""
            self.keyboard.press(Key.enter)
            return False
        elif (key == Key.esc):
            self.end = True
            self.keyboard.press(Key.enter)
            return False

        elif (key != Key.shift):
            press = time.time_ns() / 10e8
            #print(f"{key} pressed {press}")
            if(key != Key.enter):
                self.password += key.char
            self.series = self.series.append(
                pd.Series([press], index=[f"P-{str(key)}"]))

    def on_release(self, key):
        if (key != Key.shift):
            release = time.time_ns() / 10e8
            #print(f"{key} released {release}")
            if (str(key) == "'r'"):
                self.series = self.series.append(
                    pd.Series([release], index=[f"R-{str(key).upper()}"]))
            else:
                self.series = self.series.append(
                    pd.Series([release], index=[f"R-{str(key)}"]))

            # Stops listener
            if (key == Key.enter):
                # Check if input is correct
                if (self.password == ".tie5Roanl"):
                    print(colored("---> Success","green"))
                    self.add_to_dataframe()
                else :
                    print(colored("---> Wrong input, please try again!","red"))
                # Reset the Series and password
                self.series = pd.Series()
                self.password = ""
                return False

    def collect_inputs(self):
        name = input("Enter your subject name: ")
        self.subject = Subject(name)
        input_number = int(input("Enter the number of inputs: "))
        
        i = 0
        while(i < input_number):
            time.sleep(0.25)
            if self.end == True:
                return
            print("----------------------------------------")
            print(f"#{i+1} Please enter the password: \".tie5Roanl\"")
            print("----------------------------------------")
            with Listener(
                on_press=self.on_press,
                on_release=self.on_release
            ) as listener:
                _ = input()
                if self.password == ".tie5Roanl":
                    i += 1
                listener.join()
                

    def authenticate(self):
        name = input("Enter your subject name: ")
        self.subject = Subject(name)
        self.subject.load_subject()
        
        while True:
            #time.sleep(0.25)
            if self.end == True:
                return
            print("----------------------------------------")
            print("Please enter the password: \".tie5Roanl\"")
            print("----------------------------------------")
            with Listener(
                on_press=self.on_press,
                on_release=self.on_release
            ) as listener:
                _ = input()
                listener.join()

            if not self.dataframe.empty:
                prepared_dataframe = prepare_data(self.dataframe)
                scaled_dataframe = self.subject.scaler.transform(prepared_dataframe.drop("subject",axis=1))
                prediction = predict(
                    self.subject.autoencoder,
                    scaled_dataframe,
                    self.subject.best_threshold
                )
                if prediction == True:
                    print(colored("\n----> Access granted\n","green"))
                else:
                    print(colored("\n----> Access denied\n","red"))
                # Reset dataframe
                self.dataframe = pd.DataFrame(columns=self.columns)
        

def predict(model, data, threshold):
        reconstructions = model.predict(data)
        loss = tf.keras.losses.mae(reconstructions, data)
        print(f"Threshold: {threshold}")
        print(f"Reconstruction loss: {loss}")
        return tf.math.less(loss, threshold)

def prepare_data(raw_dataframe):
    columns = ["period","t","i","e","five","Shift.r","o","a","n","l","Return"]
    prepared_dataframe = pd.DataFrame()
    
    # Hold times
    for index,column in enumerate(columns):
        prepared_dataframe["subject"] = raw_dataframe["subject"]
        prepared_dataframe["H."+column] = raw_dataframe.iloc[:,2*index+1] - raw_dataframe.iloc[:,2*index]
        if index < 10:
            prepared_dataframe["DD."+columns[index]+"."+columns[index+1]] = raw_dataframe.iloc[:,2*index+2] - raw_dataframe.iloc[:,2*index]
            prepared_dataframe["UD."+columns[index]+"."+columns[index+1]] = raw_dataframe.iloc[:,2*index+2] - raw_dataframe.iloc[:,2*index+1]

    #for i in range(10):
        
    return prepared_dataframe


def main():
    collector = Collector()

    # collector.collect_inputs()
    # print(collector.dataframe)
    # path = f"raw_data_{collector.subject.name}.csv"
    # collector.dataframe.to_csv(
    #     path, mode="a", header=not os.path.exists(path), index=False)

    # raw_dataframe = pd.read_csv(path)
    # prepared_dataframe = prepare_data(raw_dataframe)
    # prepared_dataframe.to_csv(f"prepared_data_{collector.subject.name}.csv",index=False)
    # print(prepared_dataframe)

    collector.authenticate()


if __name__ == "__main__":
    main()
