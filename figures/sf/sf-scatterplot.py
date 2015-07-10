#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np
import json

from matplotlib import pyplot as plt
from matplotlib import cm

from sf import SF

DATADIR = '../../../data/eros/lightcurves'
LABELFILE = '../../../data/eros/labels-with-ids.csv'

erosids = np.genfromtxt(LABELFILE, usecols = (1,), dtype = None)
features = np.load('../../../data/eros/features/features.npy')
labels = np.load('../../../data/eros/features/labels.npy')
dictionary = json.load(open('../../../data/eros/features/dictionary.json', 'r'))

features_sf_A = features[:,dictionary['B-sf-A']]
features_sf_gamma = features[:,dictionary['B-sf-gamma']]

plt.scatter(features_sf_A[labels == 'QSO'], features_sf_gamma[labels == 'QSO'], color = 'red', alpha = 0.5, label = 'QSO')

A_RRL, gamma_RRL = [], []
for erosid in np.random.choice(erosids[(labels == 'RRL')], 3.0*180.0):

	A_RRL.append(features[erosids == erosid][:,dictionary['B-sf-A']][0])
	gamma_RRL.append(features[erosids == erosid][:,dictionary['B-sf-gamma']][0])

A_others, gamma_others = np.array(A_RRL), np.array(gamma_RRL)
plt.scatter(A_RRL, gamma_RRL, color = 'green', alpha = 0.25, label = 'RRL')

A_others, gamma_others = [], []
for erosid in np.random.choice(erosids[(labels != 'QSO') & (labels != 'RRL')], 3.0*180.0):

	A_others.append(features[erosids == erosid][:,dictionary['B-sf-A']][0])
	gamma_others.append(features[erosids == erosid][:,dictionary['B-sf-gamma']][0])
plt.scatter(A_others, gamma_others, color = 'black', alpha = 0.35, label = 'Others')

plt.xlabel('$A$', fontsize = 28)
plt.ylabel('$\gamma$', fontsize = 32)
plt.xlim(-0.025, 0.4)
plt.ylim(-0.1, 3.0)
plt.legend()
plt.savefig('sf-scatterplot.png', dpi = 200, bbox_inches = 'tight', rasterize = True)
