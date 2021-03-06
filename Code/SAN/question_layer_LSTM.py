import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Embedding, LSTM, Dropout, BatchNormalization


class question_layer_LSTM(Model):

    def __init__(self, num_words, embedding_dim, dropout_rate, seq_length, embedding_matrix, ** kwargs):
        super(question_layer_LSTM, self).__init__(**kwargs)

        # self.embedding = Embedding(num_words,
        #                            embedding_dim,
        #                            input_length=seq_length,
        #                            weights=[embedding_matrix],
        #                            trainable=False)
        self.embedding = Embedding(num_words,
                                   embedding_dim,
                                   input_length=seq_length,
                                   trainable=True)

        self.lstm1 = LSTM(units=1024, return_sequences=True,
                          recurrent_dropout=0.5)
        self.batch1 = BatchNormalization(center=False, scale=False)
        self.dropout1 = Dropout(dropout_rate)
        self.lstm2 = LSTM(units=1024, return_sequences=False,
                          recurrent_dropout=0.5)
        self.batch2 = BatchNormalization(center=False, scale=False)
        self.dropout2 = Dropout(dropout_rate)
        self.dense = Dense(1024, activation='tanh')
        self.batch = BatchNormalization(center=False, scale=False)

    def call(self, inputs):
        # (N, SEQ_LENGTH) -> (N, SEQ_LENGTH, embedding_dim)
        x = self.embedding(inputs)

        # (N, SEQ_LENGTH, embedding_dim) -> (N, SEQ_LENGTH, 512)
        x = self.lstm1(x)
        x = self.batch1(x)
        # x = self.dropout1(x)

        # (N, SEQ_LENGTH, 512) -> (N, 512)
        x = self.lstm2(x)
        x = self.batch2(x)
        # x = self.dropout2(x)

        # (N, 512) -> (N * 1024)
        x = self.dense(x)
        # x = self.batch(x)

        return x
