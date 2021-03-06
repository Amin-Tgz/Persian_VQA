import logging
import numpy as np
from constants import *
from tensorflow.keras.utils import Sequence
from tensorflow.keras.utils import normalize
from tensorflow.keras.utils import to_categorical

# logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('data_generator.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class DataGenerator(Sequence):

    def __init__(self, questions, image_ids, image_path, answers, batch_size, shuffle=True):

        self.questions = questions
        self.image_ids = image_ids
        self.image_path = image_path
        self.answers = answers
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.on_epoch_end()

    def __len__(self):
        """
        Denotes the number of batches per epoch.

        """
        return int(np.ceil(self.questions.shape[0] / self.batch_size))

    def __getitem__(self, index):
        """
        Generate one batch of data

        """
        # Generate indexes of the batch
        if ((index+1)*self.batch_size <= self.questions.shape[0]):
            indexes = self.indexes[index *
                                   self.batch_size:(index + 1) * self.batch_size]
        else:
            indexes = self.indexes[index * self.batch_size:]

        # Generate data
        [x_seqs, x_ims], y = self.__data_generation(indexes)

        logger.info("get %i/%i batches of data." % (index+1, self.__len__()))
        return [x_seqs, x_ims], y

    def on_epoch_end(self):
        """
        Updates indexes after each epoch'
        """
        self.indexes = np.arange(self.questions.shape[0])
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

        logger.info("end of epoch and shuffle data.")

    def __data_generation(self, indexes):
        """
        Generates data containing batch_size samples
        """
        batch = indexes.shape[0]

        x_seqs = np.empty((batch, SEQ_LENGTH))
        x_ims = np.empty((batch, 512, 14, 14))
        y = np.empty((batch, NUM_CLASSES), dtype=int)

        for i, idx in enumerate(indexes):
            # Store sample
            x_seqs[i] = self.questions[idx]
            x_ims[i] = np.load(self.image_path[self.image_ids[idx]])

            # Store class
            y[i] = self.answers[idx]

        # (B, 512, 14, 14) -> (B, 196, 512)
        x_ims = np.reshape(
            x_ims, (-1, x_ims.shape[1], x_ims.shape[2]*x_ims.shape[3]))
        x_ims = np.transpose(x_ims, axes=[0, 2, 1])
        logger.info("successfully create one batch of data.")
        return [x_seqs, x_ims], y
