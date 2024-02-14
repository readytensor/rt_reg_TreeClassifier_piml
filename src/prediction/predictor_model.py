import os
import warnings
from typing import Optional, List, Union

import joblib
import numpy as np
import pandas as pd
from piml.models import TreeClassifier
from sklearn.exceptions import NotFittedError

warnings.filterwarnings("ignore")


PREDICTOR_FILE_NAME = "predictor.joblib"


class Classifier:
    """A wrapper class for the Tree binary classifier."""

    model_name = "Tree Binary Classifier"

    def __init__(
        self,
        feature_names: Optional[List[str]] = None,
        feature_types: Optional[List[str]] = None,
        criterion: str = "gini",
        max_depth: int = 5,
        min_samples_split: Union[int, float] = 2,
        min_samples_leaf: Union[int, float] = 5,
        splitter: str = "best",
        min_weight_fraction_leaf: float = 0.0,
        max_features: Optional[Union[int, float, str]] = None,
        random_state: int = 0,
        max_leaf_nodes: int = None,
        **kwargs,
    ):
        """Construct a new TreeClassifier.

        Args:
            feature_names (Optional[List[str]]): The list of feature names.
            feature_types (Optional[List[str]]): The list of feature types. Available types include “numerical” and “categorical”.
            criterion (str): {“gini”, “entropy”, “log_loss”},
                The function to measure the quality of a split.
                Supported criteria are “gini” for the Gini impurity and “log_loss” and “entropy” both for the Shannon information gain.

            splitter (str): {“best”, “random”},
                The strategy used to choose the split at each node.
                Supported strategies are “best” to choose the best split and “random” to choose the best random split.

            max_depth (int): The maximum depth of the tree. If None, then nodes are
            expanded until all leaves are pure or until all leaves contain less than min_samples_split samples.

            min_samples_split (Union[int, float]): The minimum number of samples required to split an internal node:
                If int, then consider min_samples_split as the minimum number.
                If float, then min_samples_split is a fraction and ceil(min_samples_split * n_samples) are the minimum number of samples for each split.

            min_samples_leaf (Union[int, float]): The minimum number of samples required to be at a leaf node.
            A split point at any depth will only be considered if it leaves at least min_samples_leaf training samples in each of the left and right branches.
            This may have the effect of smoothing the model, especially in regression.
                If int, then consider min_samples_leaf as the minimum number.
                If float, then min_samples_leaf is a fraction and ceil(min_samples_leaf * n_samples) are the minimum number of samples for each node.

            min_weight_fraction_leaf (float): The minimum weighted fraction of the sum total of weights (of all the input samples) required to be at a leaf node.
            Samples have equal weight when sample_weight is not provided.

            max_features (Union[int, float, str]): {“auto”, “sqrt”, “log2”},
            The number of features to consider when looking for the best split:
                If int, then consider max_features features at each split.
                If float, then max_features is a fraction and max(1, int(max_features * n_features_in_)) features are considered at each split.
                If “auto”, then max_features=sqrt(n_features).
                If “sqrt”, then max_features=sqrt(n_features).
                If “log2”, then max_features=log2(n_features).
                If None, then max_features=n_features.

            max_leaf_nodes (int): Grow a tree with max_leaf_nodes in best-first fashion.
            Best nodes are defined as relative reduction in impurity. If None then unlimited number of leaf nodes.

        """
        self.feature_names = feature_names
        self.feature_types = feature_types
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.splitter = splitter
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.random_state = random_state
        self.kwargs = kwargs
        self.model = self.build_model()
        self._is_trained = False

    def build_model(self) -> TreeClassifier:
        """Build a new binary classifier."""
        model = TreeClassifier(
            feature_names=self.feature_names,
            feature_types=self.feature_types,
            criterion=self.criterion,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            splitter=self.splitter,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            max_features=self.max_features,
            max_leaf_nodes=self.max_leaf_nodes,
            random_state=self.random_state,
            **self.kwargs,
        )
        return model

    def fit(self, train_inputs: pd.DataFrame, train_targets: pd.Series) -> None:
        """Fit the binary classifier to the training data.

        Args:
            train_inputs (pandas.DataFrame): The features of the training data.
            train_targets (pandas.Series): The labels of the training data.
        """
        self.model.fit(train_inputs, train_targets)
        self._is_trained = True

    def predict(self, inputs: pd.DataFrame) -> np.ndarray:
        """Predict class labels for the given data.

        Args:
            inputs (pandas.DataFrame): The input data.
        Returns:
            numpy.ndarray: The predicted class labels.
        """
        return self.model.predict(inputs)

    def predict_proba(self, inputs: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities for the given data.

        Args:
            inputs (pandas.DataFrame): The input data.
        Returns:
            numpy.ndarray: The predicted class probabilities.
        """
        return self.model.predict_proba(inputs)

    def evaluate(self, test_inputs: pd.DataFrame, test_targets: pd.Series) -> float:
        """Evaluate the binary classifier and return the accuracy.

        Args:
            test_inputs (pandas.DataFrame): The features of the test data.
            test_targets (pandas.Series): The labels of the test data.
        Returns:
            float: The accuracy of the binary classifier.
        """
        if self.model is not None:
            return self.model.score(test_inputs, test_targets)
        raise NotFittedError("Model is not fitted yet.")

    def save(self, model_dir_path: str) -> None:
        """Save the binary classifier to disk.

        Args:
            model_dir_path (str): Dir path to which to save the model.
        """
        if not self._is_trained:
            raise NotFittedError("Model is not fitted yet.")
        joblib.dump(self, os.path.join(model_dir_path, PREDICTOR_FILE_NAME))

    @classmethod
    def load(cls, model_dir_path: str) -> "Classifier":
        """Load the binary classifier from disk.

        Args:
            model_dir_path (str): Dir path to the saved model.
        Returns:
            Classifier: A new instance of the loaded binary classifier.
        """
        model = joblib.load(os.path.join(model_dir_path, PREDICTOR_FILE_NAME))
        return model

    def __str__(self):
        return (
            f"Model name: {self.model_name} ("
            f"bootstrap: {self.bootstrap}, "
            f"max_samples: {self.max_samples}, "
            f"n_estimators: {self.n_estimators})"
        )


def train_predictor_model(
    train_inputs: pd.DataFrame, train_targets: pd.Series, hyperparameters: dict
) -> Classifier:
    """
    Instantiate and train the predictor model.

    Args:
        train_X (pd.DataFrame): The training data inputs.
        train_y (pd.Series): The training data labels.
        hyperparameters (dict): Hyperparameters for the classifier.

    Returns:
        'Classifier': The classifier model
    """
    classifier = Classifier(**hyperparameters)
    classifier.fit(train_inputs=train_inputs, train_targets=train_targets)
    return classifier


def predict_with_model(
    classifier: Classifier, data: pd.DataFrame, return_probs=False
) -> np.ndarray:
    """
    Predict class probabilities for the given data.

    Args:
        classifier (Classifier): The classifier model.
        data (pd.DataFrame): The input data.
        return_probs (bool): Whether to return class probabilities or labels.
            Defaults to True.

    Returns:
        np.ndarray: The predicted classes or class probabilities.
    """
    if return_probs:
        return classifier.predict_proba(data)
    return classifier.predict(data)


def save_predictor_model(model: Classifier, predictor_dir_path: str) -> None:
    """
    Save the classifier model to disk.

    Args:
        model (Classifier): The classifier model to save.
        predictor_dir_path (str): Dir path to which to save the model.
    """
    if not os.path.exists(predictor_dir_path):
        os.makedirs(predictor_dir_path)
    model.save(predictor_dir_path)


def load_predictor_model(predictor_dir_path: str) -> Classifier:
    """
    Load the classifier model from disk.

    Args:
        predictor_dir_path (str): Dir path where model is saved.

    Returns:
        Classifier: A new instance of the loaded classifier model.
    """
    return Classifier.load(predictor_dir_path)


def evaluate_predictor_model(
    model: Classifier, x_test: pd.DataFrame, y_test: pd.Series
) -> float:
    """
    Evaluate the classifier model and return the accuracy.

    Args:
        model (Classifier): The classifier model.
        x_test (pd.DataFrame): The features of the test data.
        y_test (pd.Series): The labels of the test data.

    Returns:
        float: The accuracy of the classifier model.
    """
    return model.evaluate(x_test, y_test)
