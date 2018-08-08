import os
from patsy import dmatrix
import pandas as pd
import numpy as np
from biom import load_table
import click
from skbio.stats.composition import clr, clr_inv


@click.group()
def songbird():
    pass


@songbird.command()
@click.option('--input-biom',
              help='Input abundances')
@click.option('--metadata-file',
              help='Input microbial abundances for testing')
@click.option('--formula',
              help='statistical formula specifying the covariates to test for.')
@click.option('--training-column', default=None,
              help=('The column in the metadata file used to specify training and testing.'
                    'These columns should be specifically labeled (Train) and (Test)'))
@click.option('--num-random-test-examples', default=10,
              help='Number of random training examples if --training-column is not specified')
@click.option('--epoch',
              help='Number of epochs to train', default=10)
@click.option('--batch_size',
              help='Size of mini-batch', default=32)
@click.option('--beta_prior',
              help=('Width of normal prior for the coefficients  '
                    'Smaller values will regularize parameters towards zero. '
                    'Values must be greater than 0.'),
              default=1.)
@click.option('--learning-rate',
              help=('Gradient descent decay rate.'),
              default=1e-1)
@click.option('--clipnorm',
              help=('Gradient clipping size.'),
              default=10.)
@click.option('--min-sample-count',
              help=("The minimum number of counts a sample needs for it to be "
                     "included in the analysis"),
              default=1000)
@click.option('--min-feature-count',
              help=("The minimum number of counts a feature needs for it to be "
                     "included in the analysis"),
              default=5)
@click.option('--checkpoint-interval',
              help=('Number of seconds before a saving a checkpoint'),
              default=3600)
@click.option('--summary-interval',
              help=('Number of seconds before a storing a summary.'),
              default=60)
@click.option('--summary-dir', default='summarydir',
              help='Summary directory to save cross validation results.')
def multinomial(input_biom, metadata_file, training_column, num_random_test_examples,
                epoch, batch_size, beta_prior,
                learning_rate, clipnorm, min_sample_count, min_feature_count,
                checkpoint_interval, summary_interval, summary_dir):

    # load metadata and tables
    metadata = pd.read_table(
        metadata_file, dtype={cols[0]: object})
    metadata = metadata.set_index(cols[0])
    table = load_table(input_biom)

    # match them
    metadata = metadata.loc[table.ids(axis='sample')]

    sample_filter = lambda val, id_, md: (
        (id_ in metadata.index) and np.sum(val) > min_sample_count)
    read_filter = lambda val, id_, md: np.sum(val) > min_feature_count
    metadata_filter = lambda val, id_, md: id_ in metadata.index

    table = table.filter(metadata_filter, axis='sample')
    table = table.filter(sample_filter, axis='sample')
    table = table.filter(read_filter, axis='observation')
    metadata = metadata.loc[table.ids(axis='sample')]

    sort_f = lambda xs: [xs[metadata.index.get_loc(x)] for x in xs]
    table = table.sort(sort_f=sort_f, axis='sample')
    metadata = dmatrix(formula, metadata, return_type='dataframe')

    metadata_filter = lambda val, id_, md: id_ in metadata.index
    table = table.filter(metadata_filter, axis='sample')

    # convert to dense representation
    dense_table = table.to_dataframe().to_dense()

    # split up training and testing
    if training_column is None:
        idx = np.random.random(metadata.shape[0])
        i = np.argsort(idx)[num_random_test_examples]
        threshold = idx[i]
        train_idx = idx > threshold

    else:
        train_idx = metadata[training_column] == "Train"

    trainX = metadata.loc[train_idx].values
    testX = metadata.loc[~test_idx].values

    trainY = dense_table.loc[train_idx].values
    testY = table.loc[~test_idx].values

    model = MultRegression(learning_rate=learning_rate, clipnorm=clipnorm,
                           beta_mean=beta_prior,
                           batch_size=batch_size,
                           save_path = summary_dir)
    with tf.Graph().as_default(), tf.Session() as session:
        model(session, trainX, trainY, testX, testY,
              summary_interval=summary_interval, checkpoint_interval=checkpoint_interval)
        model.fit(epoch=epoch)

    md_ids = np.array(metadata.columns)
    obs_ids = table.ids(axis='observation')

    beta_ = clr(clr_inv(np.hstack((np.zeros((p, 1)), model.B))))
    pd.DataFrame(
        beta_, index=md_ids, columns=obs_ids,
    ).to_csv(os.path.join(summary_dir, 'beta.csv'))

