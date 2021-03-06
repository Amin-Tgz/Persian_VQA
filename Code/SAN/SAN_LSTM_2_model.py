import json
from constants import *
from prepare_QA import *
from image_layer import *
from attention_layer import *
from prepare_generator import *
from question_layer_LSTM import *
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import SGD, Adam, Adadelta
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.layers import Dense, Input, Dropout
from tensorflow.keras.optimizers.schedules import ExponentialDecay


def SAN_LSTM_2(num_classes, dropout_rate, num_words, embedding_dim, attention_dim, embedding_matrix):

    qs_input = Input(shape=(SEQ_LENGTH,))
    img_input = Input(shape=(512, 14, 14))

    image_embed = image_layer()(img_input)
    ques_embed = question_layer_LSTM(num_words,
                                     embedding_dim,
                                     dropout_rate,
                                     SEQ_LENGTH,
                                     embedding_matrix)(qs_input)

    att = attention_layer(attention_dim)([image_embed, ques_embed])
    att = attention_layer(attention_dim)([image_embed, att])
    att = attention_layer(attention_dim)([image_embed, att])

    att = Dropout(dropout_rate)(att)

    output = Dense(num_classes, activation='softmax')(att)

    model = Model(inputs=[qs_input, img_input], outputs=output)

    return model


def Train(dataset):
    """
    Train SAN_LSTM_2  with 2 attention layer.

    Arguments:
    dataset -- an int: 0 -> english, 1 -> google, 2 -> targoman

    """

    train_generator, val_generator, val_question_ids, embedding_matrix = get_generator(
        dataset)

    save_config(dataset)

    checkpoint = ModelCheckpoint(CHECKPOINT_PATH + '/cp-{epoch: 04d}.ckpt',
                                 save_weights_only=True,
                                 verbose=1)

    model = SAN_LSTM_2(NUM_CLASSES,
                       DROPOUT_RATE,
                       embedding_matrix.shape[0],
                       EMBEDDING_DIM,
                       ATTENTION_DIM,
                       embedding_matrix)

    lr_schedule = ExponentialDecay(initial_learning_rate=LR,
                                   decay_steps=10000,
                                   decay_rate=0.99997592083)
    earlystop_callback = EarlyStopping(monitor='val_loss', patience=3)

    optimizer = Adam(learning_rate=LR)
    # optimizer = Adadelta(learning_rate=LR)

    model.compile(optimizer=optimizer,
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    model.summary()

    # Save the weights using the `checkpoint_path` format
    model.save_weights(CHECKPOINT_PATH +
                       '/cp-{epoch: 04d}.ckpt'.format(epoch=0))

    history = model.fit(x=train_generator,
                        epochs=EPOCHS,
                        validation_data=val_generator,
                        callbacks=[checkpoint, earlystop_callback],
                        workers=6,
                        use_multiprocessing=True)

    # save history
    with open(HISTORY_PATH, 'w') as file:
        json.dump(history.history, file)

    # prediction
    predictions = model.predict(val_generator,
                                workers=6,
                                use_multiprocessing=True,
                                verbose=1)

    ans_vocab = load_ans_vocab()

    result = []
    for q in range(len(val_question_ids)):
        ans = ans_vocab[str(predictions[q].argmax(axis=-1))]
        q_id = int(val_question_ids[q])
        result.append({u'answer': ans, u'question_id': q_id})

    with open(PRED_PATH, 'w') as file:
        json.dump(list(result), file)

    return


def save_config(dataset):
    if dataset == 0:
        DATASET = 'English'
    if dataset == 1:
        DATASET = 'Google'
    if dataset == 2:
        DATASET = 'Targoman'

    config = {'NAME': 'SAN_LSTM_3',
              'EMBEDDING': 'fasttext_300',
              "DATASET": DATASET,
              "OPTIMIZER": 'Adam',
              "EARLY STOPPING": 'val_loss',
              "LOSS": 'categorical_crossentropy',
              'DROPOUT_RATE': DROPOUT_RATE,
              "EMBEDDING_DIM": EMBEDDING_DIM,
              "EPOCHS": EPOCHS,
              "BATCH_SIZE": BATCH_SIZE,
              "SEQ_LENGTH": SEQ_LENGTH,
              "NUM_FILTERS": NUM_FILTERS,
              "FILTER_SIZE": FILTER_SIZE,
              "ATTENTION_DIM": ATTENTION_DIM,
              "NUM_CLASSES": NUM_CLASSES,
              "LR": LR}

    print("save config in" + str(CONFIG_PATH))
    with open(CONFIG_PATH, 'w') as file:
        json.dump(config, file)

    return


# Train(dataset=1)
Train(dataset=1)
