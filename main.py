import os
from bank import Bank
from people import People

def main():
    print("**Welcome to the Banking Application.\nPlease select an option to continue\n")
    bb = Bank()
    while True:
        bb.loadApplicationData()
        print("1: Create an user profile")
        print("2: Log into your user profile")
        print("3: Exit Application")

        userInput = input("> ")

        if userInput == "1":
            bb.addUser()

        if userInput == "2":
            bb.getUser()

        elif userInput == "3":
            exit()

if __name__ == '__main__':
    main()

    
    import pandas as pd
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, LSTM, Dense
from keras.models import Sequential

# 1. Collect a dataset of input-output pairs
# Assuming you have a csv file with columns 'word' and 'definition'
data = pd.read_csv('definition_data.csv')

# 2. Preprocess the data
# Tokenize the input words
tokenizer = Tokenizer()
tokenizer.fit_on_texts(data['word'])
word_seq = tokenizer.texts_to_sequences(data['word'])
# Pad the input sequences to have the same length
max_length = max([len(seq) for seq in word_seq])
word_seq = pad_sequences(word_seq, maxlen=max_length)

# 3. Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(word_seq, data['definition'], test_size=0.2)

# 4. Select a model architecture
model = Sequential()
model.add(Embedding(input_dim=len(tokenizer.word_index)+1, output_dim=100, input_length=max_length))
model.add(LSTM(64))
model.add(Dense(64, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# 5. Train the model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X_train, y_train, batch_size=32, epochs=5)

# 6. Evaluate the model on the test set
score, accuracy = model.evaluate(X_test, y_test, batch_size=32)
print('Test score:', score)
print('Test accuracy:', accuracy)


import pandas as pd

# Make predictions on the test set
predictions = model.predict(X_test)

# Create a DataFrame to store the results
results = pd.DataFrame({'word': data['word'][X_test.index], 'definition': y_test, 'prediction': predictions})

# Write the DataFrame to an Excel file
results.to_excel('model_results.xlsx', index=False)

# input new words
new_words = ['example1', 'example2', 'example3']

# tokenize the new words
new_word_seq = tokenizer.texts_to_sequences(new_words)

# pad the new input sequences
new_word_seq = pad_sequences(new_word_seq, maxlen=max_length)

# use the model to make predictions
new_predictions = model.predict(new_word_seq)

# output the predictions
for word, pred in zip(new_words, new_predictions):
    print(f"{word}: {pred}")

    import pandas as pd

# Read the input Excel file
df = pd.read_excel('input.xlsx')

# Extract the list of words from the file
words = df['word'].tolist()

# Tokenize the words
word_seq = tokenizer.texts_to_sequences(words)

# Pad the input sequences
word_seq = pad_sequences(word_seq, maxlen=max_length)

# Use the model to make predictions
predictions = model.predict(word_seq)

# Create a DataFrame to store the results
results = pd.DataFrame({'word': words, 'prediction': predictions})

# Write the DataFrame to an Excel file
results.to_excel('output.xlsx', index=False)
