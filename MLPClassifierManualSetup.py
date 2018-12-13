from sklearn.neural_network import MLPClassifier
import numpy as np

class MLPClassifierOverride(MLPClassifier):
    # Overriding _init_coef method
    def set_coeffs(self, coef, intercept):
        self.custom_coef = coef
        self.custom_intercept = intercept
        self.init_coef_calls = 0

    def _init_coef(self, fan_in, fan_out):
        if self.activation == 'logistic':
            init_bound = np.sqrt(2. / (fan_in + fan_out))
        elif self.activation in ('identity', 'tanh', 'relu'):
            init_bound = np.sqrt(6. / (fan_in + fan_out))
        else:
            raise ValueError("Unknown activation function %s" %
                             self.activation)
        coef_init = self.custom_coef[self.init_coef_calls]

        intercept_init = self.custom_intercept[self.init_coef_calls]

        self.init_coef_calls += 1

        return coef_init, intercept_init

    def predict(self, X):
        y_pred = self._predict(X)

        if self.n_outputs_ == 1:
            y_pred = y_pred.ravel()

        return self._label_binarizer.inverse_transform(y_pred)