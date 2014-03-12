'''
Created on Mar 7, 2014

@author: curly
'''

import datetime
import keywords
import matrices
import normalize
import count
import sentiment

from copy import deepcopy

import numpy as np
from sklearn.covariance import GraphLassoCV
from sklearn import manifold, cluster
from matplotlib.collections import LineCollection
import pylab as pl

##############################################################################
# Retrieve the data
begin = datetime.date( 2011, 1, 3 )
end = datetime.date( 2013, 11, 27 )
tickerList = keywords.getTickerList()
keywordsMap = keywords.getKeywordToIndexMap()
sentCounter = count.SentimentWordCounter( keywordsMap, sentiment.classifier() )
mentionCounter = count.WordCounter( keywordsMap )

empiricalDf = matrices.getEmpiricalDataFrame( tickerList, begin, end )[ tickerList ]
getTfIdf = lambda wordCounter, aggregator: normalize.TfIdf()( matrices.getCountDataFrame( tickerList, wordCounter, empiricalDf.index, aggregator = aggregator ) )[ tickerList ]
tfIdfSentArticle = getTfIdf( sentCounter, None )[ tickerList ]
tfIdfSentDay = getTfIdf( sentCounter, np.sum )[ tickerList ]
tfIdfMentionArticle = getTfIdf( mentionCounter, None )[ tickerList ]
tfIdfMentionDay = getTfIdf( mentionCounter, np.sum )[ tickerList ]

matrices = { 'Empirical' : { 
                            'By Day' : { 'Data' : empiricalDf } 
              },
             'Signed Mentions' : {
                            'By Day' : { 'Data' : tfIdfSentDay },
                            'By Article' : { 'Data' : tfIdfSentArticle }
              },
             'Mentions' : { 
                            'By Day' : { 'Data' : tfIdfMentionDay },
                            'By Article' : { 'Data' : tfIdfMentionArticle }
             },
            }

##############################################################################
# Learn structure
model = GraphLassoCV()

for method, freqs in matrices.items():
    for freq, matrix_types in freqs.items():
        for kind, data in matrix_types.items():
            if kind == 'Data':
                X = data / data.std( axis = 0 )
                model.fit( X )
                model = deepcopy( model )
                matrices[ method ][ freq ][ 'X' ] = X
                matrices[ method ][ freq ][ 'Model' ] = model
                matrices[ method ][ freq ][ 'Covariance' ] = model.covariance_
                matrices[ method ][ freq ][ 'Precision' ] = model.precision_

##############################################################################
# Plot the results
pl.figure(figsize=(10, 6))
pl.subplots_adjust(left=0.02, right=0.98)

# plot the covariances
methods = [ 'Signed Mentions', 'Mentions', 'Empirical' ]
freqs = [ 'By Day', 'By Article' ]
types = [ 'Covariance', 'Precision' ]

allMats = dict( ( matType, tuple( ( method, freq, matrices[method][freq]['Covariance'] ) 
                                  for method in methods 
                                  for freq in freqs
                                  if freq in matrices[method].keys() ) )
                for matType in types )

covs = allMats[ 'Covariance' ]
vmax = covs[0][2].max()
for i, ( method, freq, this_cov ) in enumerate( covs ):
    pl.subplot( 3, 2, i + 1 )
    pl.imshow(this_cov, interpolation='nearest', vmin=-vmax, vmax=vmax,
              cmap = pl.cm.jet )  # @UndefinedVariable
    pl.xticks(())
    pl.yticks(())
    pl.title( '%s Covariance %s' % ( method, freq ) )

pl.show()

# plot the precisions
precs = allMats[ 'Precision' ]
vmax = .9 * precs[0][2].max()
for i, ( method, freq, this_prec ) in enumerate( precs ):
    ax = pl.subplot( 3, 2, i + 1 )
    pl.imshow(np.ma.masked_equal(this_prec, 0),
              interpolation='nearest', vmin=-vmax, vmax=vmax,
              cmap = pl.cm.jet )  # @UndefinedVariable
    pl.xticks(())
    pl.yticks(())
    pl.title( '%s Precision %s' % ( method, freq ) )
    ax.set_axis_bgcolor('.7')

pl.show()

for method in methods:
    for freq in freqs:
        #############################################################################
        #### plot the graph of interactions
        ###############################################################################
        # Find a low-dimension embedding for visualization: find the best position of
        # the nodes (the stocks) on a 2D plane
        
        # We use a dense eigen_solver to achieve reproducibility (arpack is
        # initiated with random vectors that we don't control). In addition, we
        # use a large number of neighbors to capture the large-scale structure.
        if freq not in matrices[ method ].keys():
            continue
        edge_model = matrices[ method ][ freq ][ 'Model' ]
        names = np.array( tickerList )
        
        node_position_model = manifold.LocallyLinearEmbedding( 
            n_components = 2, eigen_solver = 'dense', n_neighbors = 4 )
        
        embedding = node_position_model.fit_transform( X.T ).T
        
        # Cluster using affinity propagation
        
        _, labels = cluster.affinity_propagation( edge_model.covariance_ )
        n_labels = labels.max()
        
        for i in range( n_labels + 1 ):
            print 'Cluster %i: %s' % ( ( i + 1 ), ', '.join( names[labels == i] ) )
        
        ###############################################################################
        # Visualization
        pl.figure( 1, facecolor = 'w', figsize = ( 10, 8 ) )
        pl.clf()
        ax = pl.axes( [0., 0., 1., 1.] )
        pl.axis( 'off' )
        
        # Display a graph of the partial correlations
        partial_correlations = edge_model.precision_.copy()
        d = 1 / np.sqrt( np.diag( partial_correlations ) )
        partial_correlations *= d
        partial_correlations *= d[:, np.newaxis]
        non_zero = ( np.abs( np.triu( partial_correlations, k = 1 ) ) > 0.02 )
        
        # Plot the nodes using the coordinates of our embedding
        pl.scatter( embedding[0], embedding[1], s = 100 * d ** 2, c = labels,
                   cmap = pl.cm.spectral )  # @UndefinedVariable
        
        # Plot the edges
        start_idx, end_idx = np.where( non_zero )
        # a sequence of (*line0*, *line1*, *line2*), where::
        #            linen = (x0, y0), (x1, y1), ... (xm, ym)
        segments = [[embedding[:, start], embedding[:, stop]]
                    for start, stop in zip( start_idx, end_idx )]
        values = np.abs( partial_correlations[non_zero] )
        lc = LineCollection( segments,
                            zorder = 0, cmap = pl.cm.hot_r,  # @UndefinedVariable
                            norm = pl.Normalize( 0, .7 * values.max() ) )
        lc.set_array( values )
        lc.set_linewidths( 15 * values )
        ax.add_collection( lc )
        
        # Add a label to each node. The challenge here is that we want to
        # position the labels to avoid overlap with other labels
        for index, ( name, label, ( x, y ) ) in enumerate( 
                zip( names, labels, embedding.T ) ):
        
            dx = x - embedding[0]
            dx[index] = 1
            dy = y - embedding[1]
            dy[index] = 1
            this_dx = dx[np.argmin( np.abs( dy ) )]
            this_dy = dy[np.argmin( np.abs( dx ) )]
            if this_dx > 0:
                horizontalalignment = 'left'
                x = x + .002
            else:
                horizontalalignment = 'right'
                x = x - .002
            if this_dy > 0:
                verticalalignment = 'bottom'
                y = y + .002
            else:
                verticalalignment = 'top'
                y = y - .002
            pl.text( x, y, name, size = 10,
                    horizontalalignment = horizontalalignment,
                    verticalalignment = verticalalignment,
                    bbox = dict( facecolor = 'w',
                              edgecolor = pl.cm.spectral( label / float( n_labels ) ),  # @UndefinedVariable
                              alpha = .6 ) )
        
        pl.xlim( embedding[0].min() - .15 * embedding[0].ptp(),
                embedding[0].max() + .10 * embedding[0].ptp(), )
        pl.ylim( embedding[1].min() - .03 * embedding[1].ptp(),
                embedding[1].max() + .03 * embedding[1].ptp() )
        pl.title( '%s %s' % ( method, freq ) )
        print ( '%s %s' % ( method, freq ) )
        pl.show()
