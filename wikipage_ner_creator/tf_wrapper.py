import pickle
import re
from random import random

import nltk as nltk
from gensim.models.fasttext import load_facebook_vectors
from keras.utils import to_categorical
from keras_preprocessing.sequence import pad_sequences
from numpy import array
from numpy import cumsum
import numpy as np
from matplotlib import pyplot
from pandas import DataFrame
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import TimeDistributed
from keras.layers import Bidirectional

# create a sequence classification instance
from tensorflow.python.estimator import keras

from fasttxt import getModel
from wikipage_ner_creator import MapperExtention, HebNer
test_tf_model = {}
options = {
	"BIOES" : True,
	"GPE":True,
	"FAC":True
}
labels_enc = HebNer(options=options).get_labels_enc()

def get_sequence(n_timesteps):
	# create a sequence of random numbers in [0,1]
	X = array([random() for _ in range(n_timesteps)])
	# calculate cut-off value to change class values
	limit = n_timesteps / 4.0
	# determine the class outcome for each item in cumulative sequence
	y = array([0 if x < limit else 1 for x in cumsum(X)])
	# reshape input and output data to be suitable for LSTMs
	X = X.reshape(1, n_timesteps, 1)
	y = y.reshape(1, n_timesteps, 1)
	return X, y


def get_lstm_model(sampales, n_timesteps, vectors_dims,classification_dim):
	model = Sequential()
	model.add(LSTM(sampales, input_shape=(n_timesteps, vectors_dims), return_sequences=True, go_backwards=True))
	model.add(TimeDistributed(Dense(classification_dim, activation='softmax')))
	model.compile(loss='categorical_crossentropy', optimizer='adam')
	return model

def preper_data(Xs,ys, n_timesteps):
	Xs = pad_sequences(Xs, maxlen=n_timesteps,
	                   padding='post', truncating='post', value=0.0)
	ys = pad_sequences(ys, maxlen=n_timesteps,
	                   padding='post', dtype="str", truncating='post', value=0)
	ys = to_categorical(ys)
	return Xs,ys

def test_model(model,Xs,ys,batch_size=10):
	loss = list()

	# fit model for one epoch on this sequence
	hist = model.test(Xs, ys, batch_size)#, verbose=0)
	loss.append(hist.history['loss'])
	return loss

def train_model(model,Xs,ys, epochs=10,batch_size=10):
	loss = list()

	# fit model for one epoch on this sequence
	hist = model.fit(Xs, ys, epochs, batch_size)#, verbose=0)
	loss.append(hist.history['loss'])
	return loss

def word_to_vector(we_model,text):
	data = we_model[text]
	test_tf_model[text] = data
	return data

def label_to_vector(label):
	return [labels_enc[label],]


def getLabeledData(n_sampales, we_model):
	mapperExt = MapperExtention.WikiMapperExtention("../Data/Output/Mapping")
	dbData = mapperExt.get_top_wiki_data(n_sampales)
	Xs = []
	Xs_text = []
	ys = []
	for page in dbData:
		page_text = page[6]
		sentences = re.findall(r'[\s\S]*?\n\.;;;O',page_text)
		for sentence in filter(lambda s:s,sentences):
			senX = []
			senX_t = []
			seny = []
			lines = filter(lambda l:l,sentence.split('\n'))
			#count = 0

			for line in [l.split(';') for l in lines if l]:
				if(line[3]):
					print(line)
					text = line[0]
					label = line[3]
					senX_t.append(text)
					senX.append(word_to_vector(we_model,text))
					seny.append(label_to_vector(label))
			#		count += 1
			#zero padding when needed
			#diff = n_timesteps-count
			#if(diff > 0):
			#	senX_t.extend([""]*diff)
			#	senX.extend([word_to_vector(text)]*diff)
			#	seny.extend(["O"]*diff)
			Xs_text.append(senX_t)
			Xs.append(senX)
			ys.append(seny)

	return Xs_text,Xs,ys

n_timesteps = 20
n_sampales = 20
results = DataFrame()

if __name__ == "__main__":
	ft_model = pickle.load(open("test_tf_model","rb"))
	#ft_model = load_facebook_vectors("../Data/wiki.he.fasttext.model.bin")
	Xs_text,Xs,ys = getLabeledData(n_sampales,ft_model)
	Xs, ys = preper_data(Xs,ys,n_timesteps)

	n_vectors_dims = len(Xs[0][0])
	n_classification_dim = len(ys[0][0])
	# lstm forwards
	model = get_lstm_model(n_sampales, n_timesteps, n_vectors_dims,n_classification_dim)
	results['lstm_forw'] = train_model(model,Xs,ys)
	# lstm backwards
	#model = get_lstm_model(n_timesteps, True)
	#results['lstm_back'] = train_model(model, n_timesteps)
	# bidirectional concat
	#model = get_bi_lstm_model(n_timesteps, 'concat')

	#results['bilstm_con'] = train_model(model, n_timesteps)
	# line plot of results
	results.plot()
	pyplot.show()
	print("dssdsd")
	#pickle.dump(test_tf_model,open("test_tf_model","wb+"))