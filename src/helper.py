import numpy as np
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt


from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge  

from src import utils



def cv(X, y, base_estimator, n_folds, random_seed=154):
    """Estimate the in- and out-of-sample error of a model using cross
    validation.

    Parameters
    ----------
    X: np.array
      Matrix of predictors.
    y: np.array
      Target array.
    base_estimator: sklearn model object.
      The estimator to fit.  Must have fit and predict methods.
    n_folds: int
      The number of folds in the cross validation.

    """

    kf = KFold(n_splits=n_folds, random_state=random_seed)
    test_cv_errors, train_cv_errors = np.empty(n_folds), np.empty(n_folds)

    for idx, (train, test) in enumerate(kf.split(X)):
        # Split into train and test for predictors and response
        xtrain = X[train]
        ytrain = y[train]
        xtest = X[test]
        ytest = y[test]    
                
        # Standardize data, fit on training set, transform training and test.
        Xyscaler = utils.XyScaler()
        Xyscaler.fit(xtrain, ytrain)    
        xtrain_s, ytrain_s = Xyscaler.transform(xtrain, ytrain)
        xtest_s, ytest_s = Xyscaler.transform(xtest, ytest)
    
        # Fit ridge regression to training data.
        model = base_estimator
        model.fit(xtrain_s, ytrain_s)    
    
        # Make predictions.
        y_hat = model.predict(xtest_s)
        y_hat_train = model.predict(xtrain_s)
    
        # Calculate MSE.
        mse_test = mean_squared_error(y_hat, ytest_s)
        mse_train = mean_squared_error(y_hat_train, ytrain_s)
    
        # Record the MSE in a numpy array.
        test_cv_errors[idx] = mse_test
        train_cv_errors[idx] = mse_train
        
    return train_cv_errors, test_cv_errors


def train_at_various_alphas(X, y, model, alphas, n_folds=10):  
    """Train a regularized regression model using cross validation at various
    values of alpha.
    
    Parameters
    ----------
    
    X: np.array
      Matrix of predictors.
      
    y: np.array
      Target array.
      
    model: sklearn model class
      A class in sklearn that can be used to create a regularized regression
      object.  Options are `Ridge` and `Lasso`.
      
    alphas: numpy array
      An array of regularization parameters.
      
    n_folds: int
      Number of cross validation folds.
      
    Returns
    -------
    
    cv_errors_train, cv_errors_test: tuple of DataFrame
      DataFrames containing the training and testing errors for each value of
      alpha and each cross validation fold.  Each row represents a CV fold, and
      each column a value of alpha.
    """
    
    
    
    cv_errors_train = pd.DataFrame(np.empty(shape=(n_folds, len(alphas))),
                                     columns=alphas)
    cv_errors_test = pd.DataFrame(np.empty(shape=(n_folds, len(alphas))),
                                        columns=alphas)    
    
    for alpha in alphas:
        train_errors, test_errors = cv(X, y, model(alpha=alpha), n_folds) 
        cv_errors_train[alpha] = train_errors
        cv_errors_test[alpha] = test_errors    
    
    return cv_errors_train, cv_errors_test
