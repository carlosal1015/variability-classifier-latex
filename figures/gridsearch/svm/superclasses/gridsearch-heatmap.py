#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

import sys
import os
import numpy as np
import pickle

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from optparse import OptionParser

parser = OptionParser()
usage = 'Usage: ./%prog[--jobs] [--folds]'
parser = OptionParser(usage = usage)

parser.add_option('--grid', dest = 'grid', default = '', type = 'str', help = 'Path to a grid object file.')
parser.add_option('--save', dest = 'save', default = None, type = 'str', help = 'Save the image to a file instead of showing it.')
parser.add_option('--dpi', dest = 'dpi', default = 300, type = 'int', help = 'DPI when saving the file.')
parser.add_option('--bilinear', dest = 'bilinear', default = False, action = 'store_true', help = 'Enable bilinear interpolation.')
parser.add_option('--midpoint', dest = 'midpoint', default = None, type = 'float', help = 'Midpoint of the heatmap.')
(options, args) = parser.parse_args()

if os.path.exists(options.grid):
	grid = pickle.load(open(options.grid, 'r'))
else:
	print 'No grid object found at %s.' % (options.grid,)
	sys.exit(1)

class MidpointNormalize(Normalize):

	def __init__(self, vmin = None, vmax = None, midpoint = None, clip = False):
		self.midpoint = midpoint
		Normalize.__init__(self, vmin, vmax, clip)

	def __call__(self, value, clip = None):
		x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
		return np.ma.masked_array(np.interp(value, x, y))

if grid.param_grid.has_key('gamma') and grid.param_grid.has_key('C'):
	x, labelx = grid.param_grid['gamma'], '$\gamma$'
	y, labely = grid.param_grid['C'], '$C$'
elif grid.param_grid.has_key('n_estimators') and grid.param_grid.has_key('max_features'):
	x, labelx = grid.param_grid['n_estimators'], '$t$'
	y, labely = grid.param_grid['max_features'], '$m$'
else:
	print 'Don\'t know what to do with the parameter grid.'
	sys.exit(1)

scores = [a[1] for a in grid.grid_scores_]
scores = np.array(scores).reshape(len(y), len(x))

number2latex = lambda string: '$' + string.split('e')[0] + '\cdot 10^{' + str(int(string.split('e')[1])) + '}$'
colormap = plt.cm.Spectral_r

plt.figure(figsize = (8, 6))
plt.subplots_adjust(left = 0.2, right = 0.95, bottom = 0.2, top = 0.95)

if options.midpoint:
	if options.bilinear:
		plt.imshow(scores, interpolation = 'bilinear', cmap = colormap, norm = MidpointNormalize(midpoint = options.midpoint))
	else:
		plt.imshow(scores, interpolation = 'nearest', cmap = colormap, norm = MidpointNormalize(midpoint = options.midpoint))
else:
	if options.bilinear:
		plt.imshow(scores, interpolation = 'bilinear', cmap = colormap)
	else:
		plt.imshow(scores, interpolation = 'nearest', cmap = colormap)

plt.xticks(np.arange(len(x)), [number2latex('%.2e' % (i,)) for i in x], rotation = 45)
plt.yticks(np.arange(len(y)), [number2latex('%.2e' % (i,)) for i in y])
plt.xlabel(labelx)
plt.ylabel(labely)
plt.colorbar(format = '%.3f')
if options.save:
	plt.savefig(options.save, dpi = options.dpi, bbox_inches = 'tight')
else:
	plt.show()
