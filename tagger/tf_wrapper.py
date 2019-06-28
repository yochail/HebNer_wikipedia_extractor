from random import random
from numpy import array
from numpy import cumsum
from matplotlib import pyplot
from pandas import DataFrame
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import TimeDistributed
from keras.layers import Bidirectional

# create a sequence classification instance
from wikipage_ner_creator import MapperExtention


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


def get_lstm_model(sampales, n_timesteps, vectors_dims):
	model = Sequential()
	model.add(LSTM(sampales, input_shape=(n_timesteps, vectors_dims), return_sequences=True, go_backwards=True))
	model.add(TimeDistributed(Dense(1, activation='softmax')))
	model.compile(loss='categorical_crossentropy', optimizer='adam')
	return model

def train_model(model,Xs,ys, n_timesteps):
	loss = list()
	for i in range(len(Xs)):
		# generate new random sequence
		X, y = Xs[i],y[i]
		# fit model for one epoch on this sequence
		hist = model.fit(X, y, epochs=100, batch_size=10)#, verbose=0)
		loss.append(hist.history['loss'][0])
	return loss



def getLabeledData(n_sampales, n_timesteps):
	mapperExt = MapperExtention.WikiMapperExtention("../Data/Mapping")
	dbData = mapperExt.get_labeled_data(100)
	Xs = []
	ys = []
	for page in dbData:
		page_text = page[6]
		sentences = page.split(".\n")
		for sentence in sentences:
			senX = []
			seny = []
			lines = sentence.split('\n')
			count = 0
			for line in [l.split(';') for l in lines]:
				if(count<n_timesteps):
					text = line[0]
					label = line[3]
					senX.append(text)
					seny.append(label)
			#zero padding when needed
			if(count<n_timesteps):




n_timesteps = 20
n_sampales = 1000
results = DataFrame()


Xs,ys,n_vectors_dims = getLabeledData(n_sampales,n_timesteps)

# lstm forwards
model = get_lstm_model(n_sampales, n_timesteps, n_vectors_dims)
results['lstm_forw'] = train_model(model,Xs,ys, n_timesteps)
# lstm backwards
model = get_lstm_model(n_timesteps, True)
results['lstm_back'] = train_model(model, n_timesteps)
# bidirectional concat
#model = get_bi_lstm_model(n_timesteps, 'concat')

#results['bilstm_con'] = train_model(model, n_timesteps)
# line plot of results
results.plot()
pyplot.show()