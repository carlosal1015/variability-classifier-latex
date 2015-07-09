#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import pickle
import json
import numpy as np
from matplotlib import pyplot as plt

from helpers import tolatex

FEATURES = '../../../data/eros/features/features.npy'
LABELS = '../../../data/eros/features/labels.npy'
DICTIONARYFILE = '../../../data/eros/features/dictionary.json'
dictionary = json.load(open(DICTIONARYFILE, 'r'))
featurenames = sorted(dictionary)

if len(sys.argv) < 2:
	print 'No path specified.'
	sys.exit(1)
else:
	path = sys.argv[1]
	if not os.path.exists(path):
		print '"%s" is not a valid file.' % (path,)
		sys.exit(1)

data = pickle.load(open(path, 'r'))

x = [featurenames[element] for element in np.argsort(data)[::-1]][:20]
y = np.sort(data[:20])[::-1] * 100.0

fig, ax = plt.subplots(nrows = 1, figsize = (12, 6))

indices = ind = np.arange(len(x))
width = 0.0

ax.bar(indices + width, y, color = 'red', alpha = 0.65)
ax.set_xticklabels([])
ax.set_xlabel('Features', size = 23)
ax.set_ylabel('Feature importance [$\%$]', size = 23)
ax.set_yscale('log')
ax.set_xlim(-1, 22)
ax.grid(False)

for i, label in enumerate(x):
	if i == 0:
		ax.text(i + 0.25, y[i] - 0.15*y[i], ' '.join(tolatex(label)), va = 'top', rotation = 90)
	else:
		ax.text(i + 0.25, y[i] + 0.15*y[i], ' '.join(tolatex(label)), va = 'bottom', rotation = 45)

	ax.text(i + 0.4, 0.0125, '%.d' % (i + 1,), va = 'bottom', ha = 'center', color = 'white')
	#ax.text(i + 0.25, 0.0125, '%.2f $\%%$' % (y[i],), va = 'bottom', rotation = 90, color = 'white')

figurepath = '%s.png' % (path.replace('.pkl', ''),)
print 'Saving to %s...' % (figurepath,)
fig.savefig(figurepath, dpi = 200, bbox_inches = 'tight', rasterize = True)
plt.show()
