from typing import Any, Dict, Tuple

import pandas as pd

from tensorflow.keras.utils import Sequence, to_categorical

import pedl
from pedl.frameworks.keras.data import InMemorySequence


def make_data_loaders(
    experiment_config: Dict[str, Any], hparams: Dict[str, Any]
) -> Tuple[Sequence, Sequence]:
    """
    Provides training and validation data for model training.

    This function splits previously-downloaded training and validation CSVs containing features and
    labels together into Keras Sequence's wrapping features and labels separately.
    """

    # The first row of each data set is not a typical CSV header with column labels, but rather a
    # dataset descriptor of the following format:
    #
    # <num observations>,<num features>,<species 0 label>,<species 1 label>,<species 2 label>
    #
    # The remaining rows then contain observations, with the four features followed by label.  The
    # label values in the observation rows take on the values 0, 1, or 2 which correspond to the
    # three species in the header.  Define the columns explicitly here so that we can more easily
    # separate features and labels below.
    label_header = "Species"
    ds_columns = [
        "SepalLength",
        "SepalWidth",
        "PetalLength",
        "PetalWidth",
        label_header,
    ]

    # Ignore header line and read the training and test CSV observations into pandas DataFrame's
    train = pd.read_csv(experiment_config["data"]["train_url"], names=ds_columns, header=0)
    train_features, train_labels = train, train.pop(label_header)
    test = pd.read_csv(experiment_config["data"]["test_url"], names=ds_columns, header=0)
    test_features, test_labels = test, test.pop(label_header)

    # Since we're building a classifier, convert the labels in the raw dataset (0, 1, or 2) to
    # one-hot vector encodings that we'll to construct the Sequence data loaders that PEDL expects.
    train_labels_categorical = to_categorical(train_labels, num_classes=3)
    test_labels_categorical = to_categorical(test_labels, num_classes=3)

    # The training and test sets are so small that we can safely use PEDL's in-memory implementation
    # of keras.utils.Sequence, InMemorySequence.
    train = InMemorySequence(
        data=train_features,
        labels=train_labels_categorical,
        batch_size=pedl.get_hyperparameter("batch_size"),
    )
    test = InMemorySequence(
        data=test_features,
        labels=test_labels_categorical,
        batch_size=pedl.get_hyperparameter("batch_size"),
    )
    return train, test
