'''
root/codes/block_definitions/utilities/operators...

Overview:
strictly just tensorflow basic layers...unsure of organization but leaving as-is for now

Rules:
'''

### packages
import tensorflow as tf
import numpy as np
from copy import deepcopy

### sys relative to root dir
import sys
from os.path import dirname, realpath
sys.path.append(dirname(dirname(dirname(dirname(realpath(__file__))))))

### absolute imports wrt root
from codes.block_definitions.utilities import argument_types
from codes.utilities.custom_logging import ezLogging


### init dict
operator_dict = {}


def input_layer(input_tensor):
    return tf.keras.layers.InputLayer()(input_tensor)

operator_dict[input_layer] = {"inputs": [tf.keras.layers],
                              "output": tf.keras.layers,
                              "args": []
                             }


def dense_layer(input_tensor, num_units=128, activation=tf.nn.relu):
    # Flatten tensor into a batch of vectors
    pool2_flat = tf.keras.layers.Flatten()(input_tensor)
    # Densely connected layer with 1024 neurons
    logits = tf.keras.layers.Dense(units=num_units, activation=activation)(pool2_flat)
    return logits


operator_dict[dense_layer] = {"inputs": [tf.keras.layers],
                              "output": tf.keras.layers,
                              "args": [argument_types.ArgumentType_Pow2, argument_types.ArgumentType_TFActivation]
                             }


def conv_layer(input_tensor, filters=64, kernel_size=3, activation=tf.nn.relu):
    kernel_size = (kernel_size, kernel_size)
    # Convolutional Layer
    # Computes 32 features using a 5x5 filter with ReLU activation.
    # Padding is added to preserve width and height.
    return tf.keras.layers.Conv2D(filters=filters,
                                  kernel_size=kernel_size,
                                  padding="same",
                                  activation=activation,
                                  data_format="channels_last"
                                 )(input_tensor)

operator_dict[conv_layer] = {"inputs": [tf.keras.layers],
                             "output": tf.keras.layers,
                             "args": [argument_types.ArgumentType_Pow2, argument_types.ArgumentType_TFFilterSize, argument_types.ArgumentType_TFActivation]
                            }


def identity_layer(input):
    output_tensor = model.add(Lambda(lambda input: input))
    return output_tensor

operator_dict[identity_layer] = {"inputs": [tf.keras.layers],
                                 "outputs": tf.keras.layers,
                                 "args": []
                                }


