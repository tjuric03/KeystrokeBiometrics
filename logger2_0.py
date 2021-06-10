from pynput.keyboard import Key, Listener
import time
import os
import threading
import pandas as pd
from termcolor import colored


class Logger():
    """
    A class used for logging and timing keyboard inputs.

    Uses the pynput.keyboard.Listener class.
    The logger ends when Key.enter is released

    Methods
    -------
    reset_state()
        Resets internal variables.

    on_press(key)
        The callback to call when a button is pressed.

    on_release(key)
        The callback to call when a button is released.

    start_logger()
        Starts key logging.

    end_logger()
        Ends key logging.
    """

    def __init__(self):
        self.listener = Listener(
            on_press=self.on_press,
            on_release=self.on_release,
        )
        self.input = ""
        self.times = pd.Series()
        self.running = True

    def reset_state(self):
        self.input = ""
        self.times = pd.Series()

    def on_press(self, key):
        if key == Key.backspace:
            print(colored("\n---> Please don't use backspace", "red"))
            self.reset_state()
            self.listener.stop()
        press = time.time_ns() / 10e8
        if key == Key.enter:
            self.times[f"P-{str(key)}"] = press

        if key == Key.esc:
            self.running = False
            self.end_logger()
        # Add all characters into the input/times and ignore
        # keys like "enter" or "space" which don't have .char attribute
        try:
            self.input += key.char
            self.times[f"P-'{key.char}'"] = press
        except AttributeError:
            pass

    def on_release(self, key):
        release = time.time_ns() / 10e8
        if key == Key.enter:
            self.times[f"R-{str(key)}"] = release
            self.end_logger()
        # Add all characters into the input/times and ignore
        # keys like "enter" or "space" which don't have .char attribute
        try:
            self.times[f"R-'{self.listener.canonical(key).char}'"] = release
        except AttributeError:
            pass

    def start_logger(self):
        print("Logger is starting")
        self.listener.start()
        self.listener.join()

    def end_logger(self):
        print("Logger is ending")
        self.listener.stop()

DATA_COLUMNS = [
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
        "R-'r'",
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

def start_input_thread():
        input_thread = threading.Thread(target=input)
        input_thread.setDaemon(True)
        input_thread.start()

class Collector():
    """
    A class for collecting inputs and storing their times in a DataFrame.

    Methods
    -------
    insert_data()
        Adds a new row of input to the data DataFrame.

    collect_inputs(csv=True)
        Uses the Logger class to collect inputs
    """

    def __init__(self):
        self.logger = Logger()
        self.name = ""
        self.data = pd.DataFrame(columns=DATA_COLUMNS)

    def insert_data(self):
        self.logger.times["subject"] = self.name
        self.data = self.data.append(self.logger.times, ignore_index=True)

    def collect_inputs(self, csv=True):
        self.name = input("Enter your subject name: ")
        input_number = int(input("Enter the number of inputs: "))
        time.sleep(0.25)

        i = 0
        while(i < input_number):
            print("----------------------------------------")
            print(f"#{i+1} Please enter the password: \".tie5Roanl\"")
            print("----------------------------------------")

            self.logger = Logger()
            start_input_thread()
            self.logger.start_logger()
            if not self.logger.running:
                break

            if(self.logger.input == ".tie5Roanl"):
                print(colored("---> Success", "green"))
                i += 1
                self.insert_data()
            elif(self.logger.input == ""):
                pass
            else:
                print(colored("---> Wrong input, please try again!", "red"))
        if csv and not self.data.empty:
            save_to_csv(self.data, "raw_data", self.name)


def save_to_csv(data, prefix, name):
    path = f"{prefix}_{name}.csv"
    data.to_csv(
        path, mode="a", header=not os.path.exists(path), index=False)


def prepare_data(raw_dataframe):
    columns = ["period","t","i","e","five","Shift.r","o","a","n","l","Return"]
    prepared_dataframe = pd.DataFrame()
    prepared_dataframe["subject"] = raw_dataframe["subject"]    

    for index,column in enumerate(columns):
        prepared_dataframe["H."+column] = raw_dataframe.iloc[:,2*index+1] - raw_dataframe.iloc[:,2*index]
        if index < 10:
            prepared_dataframe["DD."+columns[index]+"."+columns[index+1]] = raw_dataframe.iloc[:,2*index+2] - raw_dataframe.iloc[:,2*index]
            prepared_dataframe["UD."+columns[index]+"."+columns[index+1]] = raw_dataframe.iloc[:,2*index+2] - raw_dataframe.iloc[:,2*index+1]
        
    return prepared_dataframe

def main():

    collector = Collector()
    collector.collect_inputs(csv=True)
    prepared_data = prepare_data(collector.data)
    save_to_csv(prepared_data,"prepared_data",collector.name)


if __name__ == "__main__":
    main()
