#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np
import json

from matplotlib import pyplot as plt
from itertools import combinations
from scipy import optimize
from scipy import stats
from helpers import fasthistogram

DATADIR = '../../../data/eros/lightcurves'
LABELFILE = '../../../data/eros/labels-with-ids.csv'

erosids = np.genfromtxt(LABELFILE, usecols = (1,), dtype = None)
features = np.load('../../../data/eros/features/features.npy')
labels = np.load('../../../data/eros/features/labels.npy')
dictionary = json.load(open('../../../data/eros/features/dictionary.json', 'r'))

# A: Root-mean-square magnitude difference on a one year timescale
# γ: Logarithmic gradient of mean change in magnitude

def powerlaw(x, A, gamma):
	if A <= 0 or A >= 1 or gamma < 0:
		return -np.inf
	return A * (x / 365.0)**gamma

#for erosid in erosids[labels == 'QSO']:
for erosid in ['lm0207n13467', 'lm0050m11100', 'lm0163k2435', 'lm0293k4406', 'lm0553k3154', 'lm0563m18409', 'lm0573n32998']:
#for erosid in ['lm0163k2435', 'lm0011l26623', 'lm0563m18409']:

	path = '%s.time' % (erosid,)
	print path
	filename = os.path.join(DATADIR, path)
	data = np.loadtxt(filename)
	t, m, dm = data[:,0], data[:,1], data[:,2]

	N = len(m)
	indices = np.array((list(combinations(range(N), 2))))
	i, j = indices.T

	delta_m_ij = m[j] - m[i]
	delta_t_ij = t[j] - t[i]
	sigma_m_i, sigma_m_j = dm[j], dm[i]

	bins = 2000

	timelag = np.linspace(delta_t_ij.min(), delta_t_ij.max(), bins)
	V = np.sqrt(np.pi/2.0) * np.abs(delta_m_ij) - np.sqrt(sigma_m_i**2 + sigma_m_j**2)
	SF = stats.binned_statistic(delta_t_ij, V, bins = bins, statistic = 'mean')[0]

	edges = np.linspace(np.min(delta_t_ij), np.max(delta_t_ij), bins + 1)
	histogram = fasthistogram(delta_t_ij, edges)
	binmapping = np.digitize(delta_t_ij, edges)
	SF = [np.sum(V[binmapping == (i+1)]) for i in xrange(len(histogram))] / histogram

	try:
		popt, pcov = optimize.curve_fit(powerlaw, timelag[~np.isnan(SF)], SF[~np.isnan(SF)], p0 = (0.1, 0.1))
	except RuntimeError:
		pass
	A, gamma = popt
	dA, dgamma = np.sqrt(np.diag(pcov))

	print u'A: %.4f ± %.4f' % (A, dA)
	print u'γ: %.4f ± %.4f' % (gamma, dgamma)

	plt.plot(timelag, SF, '.', color = 'black', alpha = 0.75)
	plt.plot(timelag[~np.isnan(SF)], powerlaw(timelag[~np.isnan(SF)], *popt), 'r-')
	plt.xlabel('$\log({\Delta t})$', size = 32)
	plt.ylabel('$\mathrm{SF}$', size = 32)
	plt.xscale('log')
	plt.xlim(1.0)
	plt.savefig('sf-fit.png', dpi = 200, bbox_inches = 'tight', rasterize = True)
	plt.clf()
