#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# GENERATE - Generate model file 'training_data' based on json files
#

import os
#
# 0 = all messages are logged (default behavior)
# 1 = INFO messages are not printed
# 2 = INFO and WARNING messages are not printed
# 3 = INFO, WARNING, and ERROR messages are not printed
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
try:
    import nltk
    import pickle
    import numpy
    import pathlib

    from keras.models import Sequential
    from keras.layers import Dense, Activation, Dropout
    # from keras.optimizers import SGD
    from tensorflow.keras.optimizers import SGD
    import random

    import intent
except ModuleNotFoundError as E:
    print(f"{E}. Install required modules.")


# Phase [1]. Loading json database
words=[]
classes = []
documents = []
ignore_words = ['?', '!']
lemmatizer = nltk.stem.WordNetLemmatizer()

dbPath = str(pathlib.Path(__file__).parent.resolve()) + os.path.sep + ".." + os.path.sep + "db"
intents = intent.database(dbPath)

# Phase [2]. Preprocess data
# Words splitting
for intent in intents.list['intents']:
    for pattern in intent['patterns']:
        w = nltk.word_tokenize(pattern)                     # Tokenize each word
        words.extend(w)
        documents.append((w, intent['tag']))                # Add documents in the corpus
        # Add to our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])
# lemmatize and lower each word and remove duplicates
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
# sort classes list
classes = sorted(list(set(classes)))
print("Training model")
print("-----------------------------------------------------------------------")
# documents = combination between patterns and intents
print(f"- Documents           {len(documents)}")
print(f"                      {documents}")
# classes = intents
print(f"- Classes             {len(classes)}")
print(f"                      {classes}")
# words = all words, vocabulary
print(f"- Lemmatized Words    {len(words)}")
print(f"                      {words}")
pickle.dump(words,open(dbPath+os.path.sep+'words.pkl','wb'))
pickle.dump(classes,open(dbPath+os.path.sep+'classes.pkl','wb'))


# Phase [3]. Create training and testing data
print()
print("Creating training data", flush=True)
print("-----------------------------------------------------------------------")
# create our training data
training = []
# create an empty array for our output
output_empty = [0] * len(classes)

# training set, bag of words for each sentence
for doc in documents:
    # initialize our bag of words
    bag = []
    # list of tokenized words for the pattern
    pattern_words = doc[0]
    # lemmatize each word - create base word, in attempt to represent related words
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    # create our bag of words array with 1, if word match found in current pattern
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    
    # output is a '0' for each tag and '1' for current tag (for each pattern)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    
    training.append([bag, output_row])

# shuffle our features and turn into np.array
random.shuffle(training)
training = numpy.array(training, dtype=object)
# create train and test lists. X - patterns, Y - intents
train_x = list(training[:,0])
train_y = list(training[:,1])
print("- Training data created")

# Phase [4]. Build the model
# Create model - 3 layers. First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
# equal to number of intents to predict output intent with softmax
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Fitting and saving the model 
hist = model.fit(numpy.array(train_x), numpy.array(train_y), epochs=200, batch_size=5, verbose=0)
model.save(dbPath+os.path.sep+'model.h5', hist)

print("- Model saved as 'model.h5'")
print()