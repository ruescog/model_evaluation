# AUTOGENERATED! DO NOT EDIT! File to edit: ../01_core.ipynb.

# %% auto 0
__all__ = ['evaluate']

# %% ../01_core.ipynb 2
from pathlib import Path
from sklearn.model_selection import BaseCrossValidator
from fastai.vision.learner import Learner
from fastai.data.block import DataBlock
from fastai.data.load import DataLoader
from fastai.data.transforms import IndexSplitter

from typing import Callable, Tuple

# %% ../01_core.ipynb 4
def evaluate(
    datablock_hparams: dict, # The hyperparameters used to get and load the data.
    dataloader_hparams: dict, # The hyperparameters used to define how the data is supplied to the learner.
    technique: BaseCrossValidator, # The technique used to split the data.
    learner_hparams: dict,  # The parameters used to build the learner (backbone, cbs...). Those hyperparams are used to build all the models.
    learning_hparams: dict, # The parameters used to train the learner (learning_rate, freeze_epochs)
    learning_mode: str = "finetune" # The learning mode: random or finetune.
):
    
    # Defines all the metrics used in the training and evaluation phases
    metrics = ["validation"]
    other_metrics = learner_hparams["metrics"] if "metrics" in learner_hparams else []
    results = dict([[str(metric), []] for metric in metrics + other_metrics])
    
    # Gets all the data
    get_items_form = "get_items" if "get_items" in datablock_hparams else "get_x"
    get_items = [datablock_hparams[get_items_form], datablock_hparams["get_y"]]
    if "splitter" in datablock_hparams:
        del datablock_hparams["splitter"]

    X = get_items[0](dataloader_hparams["source"])
    y = [get_items[1](x) for x in X]
    for _, validation_indexes in technique.split(X, y):
        db = DataBlock(
            *datablock_hparams,
            splitter = IndexSplitter(validation_indexes)
        )
        dls = db.dataloaders(*dataloader_hparams)
        learner = Learner(dls, *learner_hparams)
        if learning_mode == "random":
            learner.fit_one_cycle(*learning_hparams)
        elif learning_mode == "finetune":
            learner.fine_tune(*learning_hparams)
        else:
            raise Exception(f"{learning_mode} is not a learning_mode. Use 'random' or 'finetune' instead.")
        
        for metric, metric_value in zip(results, learner.validate()):
            results[metric] += [metric_value]
    
    return results
