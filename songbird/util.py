import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.utils import check_random_state
from skbio.stats.composition import clr_inv as softmax
from biom import Table


def random_multinomial_model(num_samples, num_features,
                             reps=1,
                             low=2, high=10,
                             beta_mean=0,
                             beta_scale=5,
                             mu = 1,
                             sigma = 1,
                             seed=0):
    """ Generates a table using a random poisson regression model.

    Here we will be simulating microbial counts given the model, and the
    corresponding model priors.

    Parameters
    ----------
    num_samples : int
        Number of samples
    num_features : int
        Number of features
    tree : np.array
        Tree specifying orthonormal contrast matrix.
    low : float
        Smallest gradient value.
    high : float
        Largest gradient value.
    beta_mean : float
        Mean of beta prior (for regression coefficients)
    beta_scale : float
        Scale of beta prior (for regression coefficients)
    mu : float
        Mean sequencing depth (in log units)
    sigma : float
        Variance for sequencing depth

    Returns
    -------
    table : biom.Table
        Biom representation of the count table.
    metadata : pd.DataFrame
        DataFrame containing relevant metadata.
    beta : np.array
        Regression parameter estimates.
    """
    N, D = num_samples, num_features

    # generate all of the coefficient using the random poisson model
    state = check_random_state(seed)
    beta = state.normal(beta_mean, beta_scale, size=(2, num_features-1))
    B = np.hstack((np.zeros((2, 1)), beta))

    X = np.hstack([np.linspace(low, high, num_samples // reps)]
                  for _ in range(reps))
    X = np.sort(X)
    X = np.vstack((np.ones(N), X)).T

    probs = softmax(X @ B)
    n = state.poisson(state.lognormal(mu, sigma, size=N))
    #n = state.poisson(mu, size=N)

    table = np.vstack(
        state.multinomial(n[i], probs[i, :])
        for i in range(N)
    ).T

    samp_ids = ['S%d' % i for i in range(num_samples)]
    feat_ids = ['F%d' % i for i in range(num_features)]
    balance_ids = ['L%d' % i for i in range(num_features-1)]

    table = Table(table, feat_ids, samp_ids)
    metadata = pd.DataFrame(X, columns=['Ones', 'X'], index=samp_ids)
    beta = pd.DataFrame(beta.T, columns=['Intercept', 'beta'], index=balance_ids)

    return table, metadata, beta
