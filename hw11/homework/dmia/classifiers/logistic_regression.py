import numpy as np
from scipy import sparse


class LogisticRegression:
    def __init__(self):
        self.w = None
        self.loss_history = None

    def train(self, X, y, learning_rate=1e-3, reg=1e-5, num_iters=100,
                batch_size=200, verbose=False):
        def train(self, X, y, learning_rate=1e-3, reg=1e-5, num_iters=100,
                batch_size=200, verbose=False):
        X = LogisticRegression.append_biases(X)
        num_train, dim = X.shape
        if self.w is None:
            self.w = np.random.randn(dim) * 0.01

        self.loss_history = []

        for it in range(num_iters):
            indices = np.random.choice(num_train, batch_size, replace=True)
            X_batch = X[indices]
            y_batch = y[indices]

            loss, gradW = self.loss(X_batch, y_batch, reg)
            self.loss_history.append(loss)

            self.w -= learning_rate * gradW

            if verbose and it % 100 == 0:
                print('iteration %d / %d: loss %f' % (it, num_iters, loss))

        return self

    def predict_proba(self, X, append_bias=False):
        if append_bias:
            X = LogisticRegression.append_biases(X)

        logits = X.dot(self.w)

        probs_class_1 = 1 / (1 + np.exp(-logits))
        probs_class_0 = 1 - probs_class_1

        y_proba = np.vstack([probs_class_0, probs_class_1]).T

        return y_proba

    def predict(self, X):
        y_proba = self.predict_proba(X, append_bias=True)
        y_pred = np.argmax(y_proba, axis=1)
        return y_pred

    def loss(self, X_batch, y_batch, reg):
        num_train = X_batch.shape[0]

        logits = X_batch.dot(self.w)  # shape: (N,)

        probs = 1 / (1 + np.exp(-logits))  # shape: (N,)

        eps = 1e-15  
        loss = -np.mean(y_batch * np.log(probs + eps) + (1 - y_batch) * np.log(1 - probs + eps))


        loss += reg * np.sum(self.w[:-1] ** 2)

        error = probs - y_batch  # shape: (N,)
        grad = X_batch.T.dot(error) / num_train  # shape: (D,)

        grad[:-1] += 2 * reg * self.w[:-1]

        return loss, grad

    @staticmethod
    def append_biases(X):
        return sparse.hstack((X, np.ones(X.shape[0])[:, np.newaxis])).tocsr()
