""" Basic script for training and testing two ProtoModels and comparing their prototypes """
import torch
import torch.nn as nn
import torch.nn.functional as F
from data_parsing import load_mnist, load_svhn
from models.proto_model import ProtoModel
from models.transfer_model import TransferModel

proto_model_config_1 = {
    "input_dim": 784,
    "hidden_layers": [128, 128],
    "hidden_activations": [nn.ReLU(), None],
    "latent_dim": 128,
    "recon_activation": nn.Sigmoid(),
    "num_prototypes": 10,
    "num_classes": 10,
    "use_convolution": False
}

proto_model_config_2 = {
    "input_dim": 784,
    "hidden_layers": [128, 128],
    "hidden_activations": [nn.ReLU(), None],
    "latent_dim": 128,
    "recon_activation": nn.Sigmoid(),
    "num_prototypes": 10,
    "num_classes": 10,
    "use_convolution": True
}

# Hyperparameters
NUM_EPOCHS = 20
BATCH_SIZE = 64
LEARNING_RATE = 0.001

def train(model_name, epochs=NUM_EPOCHS, train_new=True, save_model=True, weights=(1, 1, 1, 1)):

    # load MNIST data
    mnist_train_dl, mnist_test_dl = load_mnist.load_mnist_dataloader(BATCH_SIZE)
    svhn_train_dl, svhn_test_dl = load_svhn.load_svhn_dataloader(BATCH_SIZE, greyscale=True)

    # create ProtoModel
    model_1 = ProtoModel(proto_model_config_1, LEARNING_RATE)
    model_2 = ProtoModel(proto_model_config_2, LEARNING_RATE)

    # assume pre-trained source model
    model_1 = ProtoModel.load_model("mnist_linear_1.pth", proto_model_config_1, LEARNING_RATE)

    tm = TransferModel(model_1, model_2, epochs=epochs, weights=weights)

    if train_new:
        tm.fit_combined_loss(mnist_train_dl, svhn_train_dl)
    else:
        tm = TransferModel.load_model(f"{model_name}.pth", model_1, model_2)

    res = tm.evaluate(svhn_test_dl)
    print(res)

    tm.visualize_prototypes(f"{model_name}_proto.jpg")
    tm.visualize_samples(mnist_train_dl, svhn_train_dl, f"{model_name}_sample.jpg")
    print(f"weights: {weights}")

    if save_model:
        tm.save_model(f"{model_name}.pth")


if __name__ == "__main__": 
    train("tm_loss_opt")