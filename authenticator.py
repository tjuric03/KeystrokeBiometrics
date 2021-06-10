import logger2_0 as log2
import os
import pandas as pd
from termcolor import colored
import pickle
from tensorflow import keras
import tensorflow as tf

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
        self.autoencoder.save(os.path.join(path,"autoencoder"))

        
    def load_subject(self):
        path = os.path.join("subjects",self.name)
        if not os.path.exists(path):
            msg = f"Subject with name \"{self.name}\" does not exist"
            raise NameError(msg)
        self.scaler = pickle.load(open(os.path.join(path,"scaler.pickle"), 'rb'))
        self.best_threshold = pickle.load(open(os.path.join(path,"best_threshold.pickle"), 'rb'))
        self.autoencoder = tf.keras.models.load_model(os.path.join(path,"autoencoder"))

def predict(model, data, threshold):
        reconstructions = model.predict(data)
        loss = tf.keras.losses.mae(reconstructions, data)
        print(f"Threshold: {threshold}")
        print(f"Reconstruction loss: {loss}")
        return tf.math.less(loss, threshold)

def authenticate():
    name = input("Enter your subject name: ")
    subject = Subject(name)
    subject.load_subject()

    while True:
        print("----------------------------------------")
        print("Please enter the password: \".tie5Roanl\"")
        print("----------------------------------------")

        logger = log2.Logger()
        log2.start_input_thread()
        logger.start_logger()
        if not logger.running:
            break

        if logger.input == ".tie5Roanl":
            logger.times["subject"] = name
            dataframe = pd.DataFrame(columns=log2.DATA_COLUMNS)
            dataframe = dataframe.append(logger.times, ignore_index=True)
            prepared_data = log2.prepare_data(dataframe)
            scaled_data = subject.scaler.transform(prepared_data.drop("subject",axis=1))
            prediction = predict(
                subject.autoencoder,
                scaled_data,
                subject.best_threshold
            )
            if prediction == True:
                print(colored("\n----> Access granted\n","green"))
            else:
                print(colored("\n----> Access denied\n","red"))
        else:
            print(colored("---> Wrong input, please try again!", "red"))


def main():
    authenticate()

if __name__ == "__main__":
    main()