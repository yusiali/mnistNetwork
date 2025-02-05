#  Optimized neural network with 98% precision after 20 epochs of training
#  major changes from v1: - switched from batch gradient descent to mini-batch gradient descent
#                         - added momentum to descent algo
#                         - better initialization of weights
from sklearn.datasets import fetch_openml
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix

# import MNIST dataset
X, y = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)

# normalize value
X = X / 255

# one-hot encode labels to digits
digits = 10
examples = y.shape[0]
y = y.reshape(1, examples)
Y_new = np.eye(digits)[y.astype('int32')]
Y_new = Y_new.T.reshape(digits, examples)

# reshape & shuffle digits
m = 60000  # number of images in training set (remaining 10,000 are used for testing)
m_test = X.shape[0] - m
X_train, X_test = X[:m].T, X[m:].T
Y_train, Y_test = Y_new[:, :m], Y_new[:, m:]
shuffle_index = np.random.permutation(m)  # randomly shuffles training set order for good measure
X_train, Y_train = X_train[:, shuffle_index], Y_train[:, shuffle_index]

# example digit recognition test
i = 12
plt.imshow(X_train[:, i].reshape(28, 28), cmap=matplotlib.cm.binary)  # prints example digit from database
plt.axis('off')
plt.show()

c = 0
for n in Y_train[:, i]:
    if n == 1:
        print("Digit:", c)  # prints recognized digit from example
    c += 1


#  cost function using cross-entropy to calculate loss in accuracy
def compute_loss(Y, Y_hat):
    L_sum = np.sum(np.multiply(Y, np.log(Y_hat)))
    m = Y.shape[1]
    L = -(1 / m) * L_sum
    return L


def feed_forward(X, params):
    cache = {}
    cache["Z1"] = np.matmul(params["W1"], X) + params["b1"]
    cache["A1"] = sigmoid(cache["Z1"])
    cache["Z2"] = np.matmul(params["W2"], cache["A1"]) + params["b2"]
    cache["A2"] = np.exp(cache["Z2"]) / np.sum(np.exp(cache["Z2"]), axis=0)
    return cache


#  backprop function is fed caches from feed forward function
def back_prop(X, Y, params, cache):
    dZ2 = cache["A2"] - Y
    dW2 = (1 / m_batch) * np.matmul(dZ2, cache["A1"].T)
    db2 = (1 / m_batch) * np.sum(dZ2, axis=1, keepdims=True)

    dA1 = np.matmul(params["W2"].T, dZ2)
    dZ1 = dA1 * sigmoid(cache["Z1"]) * (1 - sigmoid(cache["Z1"]))
    dW1 = (1 / m_batch) * np.matmul(dZ1, X.T)
    db1 = (1 / m_batch) * np.sum(dZ1, axis=1, keepdims=True)

    grads = {"dW1": dW1, "db1": db1, "dW2": dW2, "db2": db2}
    return grads


#  function used in forward propagation
def sigmoid(z):
    s = 1 / (1 + np.exp(-z))
    return s


#  initialize hyperparameters
n_x = X_train.shape[0]
n_h = 64  # hidden layer
learning_rate = 4
beta = .9
batch_size = 128
batches = -(-m // batch_size)

# initialize weights
params = {"W1": np.random.randn(n_h, n_x) * np.sqrt(1 / n_x),
          "b1": np.zeros((n_h, 1)) * np.sqrt(1 / n_x),
          "W2": np.random.randn(digits, n_h) * np.sqrt(1 / n_h),
          "b2": np.zeros((digits, 1)) * np.sqrt(1 / n_h)}

V_dW1 = np.zeros(params["W1"].shape)
V_db1 = np.zeros(params["b1"].shape)
V_dW2 = np.zeros(params["W2"].shape)
V_db2 = np.zeros(params["b2"].shape)

#  training loop
for i in range(20):  # runs thru 20 epochs
    permutation = np.random.permutation(X_train.shape[1])
    X_train_shuffled = X_train[:, permutation]
    Y_train_shuffled = Y_train[:, permutation]

    for j in range(batches):
        begin = j * batch_size
        end = min(begin + batch_size, X_train.shape[1] - 1)
        X = X_train_shuffled[:, begin:end]
        Y = Y_train_shuffled[:, begin:end]
        m_batch = end - begin

        cache = feed_forward(X, params)
        grads = back_prop(X, Y, params, cache)

        #  calculate moving average of gradients
        V_dW1 = (beta * V_dW1 + (1 - beta) * grads["dW1"])
        V_db1 = (beta * V_db1 + (1 - beta) * grads["db1"])
        V_dW2 = (beta * V_dW2 + (1 - beta) * grads["dW2"])
        V_db2 = (beta * V_db2 + (1 - beta) * grads["db2"])

        params["W1"] -= learning_rate * V_dW1
        params["b1"] -= learning_rate * V_db1
        params["W2"] -= learning_rate * V_dW2
        params["b2"] -= learning_rate * V_db2

    cache = feed_forward(X_train, params)
    train_cost = compute_loss(Y_train, cache["A2"])
    cache = feed_forward(X_test, params)
    test_cost = compute_loss(Y_test, cache["A2"])
    print("Epoch {}: training cost = {}, test cost = {}.".format(i + 1, train_cost, test_cost))

cache = feed_forward(X_test, params)
predictions = np.argmax(cache["A2"], axis=0)
labels = np.argmax(Y_test, axis=0)

print(confusion_matrix(predictions, labels))  # grid of digit recognition precision
print(classification_report(predictions, labels))  # precision report after training
