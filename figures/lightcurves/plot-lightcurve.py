#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Cursor
from optparse import OptionParser
from datetime import datetime

from fasper import fasper
from fitting import MultiFourierFit
from helpers import phase

DATADIR = '../../../data/eros'
LIGHTCURVEDIR = os.path.join(DATADIR, 'lightcurves')

parser = OptionParser()
usage = 'Usage: ./%prog --lightcurves <FILE> --band <BAND> [--interactive] [--name <NAME>]'
parser = OptionParser(usage = usage)
parser.add_option('--lightcurves', dest = 'lightcurves', default = [], help = 'Specify a lightcurve to work on.')
parser.add_option('--interactive', dest = 'interactive', default = False, action = 'store_true', help = 'Enable interactive mode.')
parser.add_option('--band', dest = 'band', default = 'b', help = 'Specify the photometric band to use.')
parser.add_option('--name', dest = 'name', default = '', help = 'Specify a filename for saving.')
(options, args) = parser.parse_args()

if not options.lightcurves:
	print 'Please specify a lightcurve.'
	sys.exit(1)

options.lightcurves = options.lightcurves.split(',')
options.lightcurves = [element + '.time' for element in options.lightcurves if not element.endswith('.time')]

for filename in options.lightcurves:

	path = os.path.join(LIGHTCURVEDIR, filename)
	if not os.path.exists(path):
		print 'No lightcurve found at "%s".' % (path,)
		continue

	data = np.loadtxt(path)
	if options.band == 'r':
		t, m, dm = data[:,0], data[:,1], data[:,2]
	else:
		t, m, dm = data[:,0], data[:,3], data[:,4]
	mask = np.abs(m) < 50
	t, m, dm = t[mask], m[mask], dm[mask]

	minimum = 0.03
	maximum = int(0.5 * (np.max(t) - np.min(t)))

	print 'Searching for periods between %.2f and %.2f days...' % (minimum, maximum)

	oversampling = 8.0
	minimum_period = minimum # in days

	# Average nyquist frequency
	average_nyquist_frequency = 0.5 * len(t) / (np.max(t) - np.min(t))
	# Average nyquist period
	average_nyquist_period = 1.0 / average_nyquist_frequency
	hifac = int(average_nyquist_period / minimum_period)
	if hifac < 200:
		hifac = 200

	starttime = datetime.now()
	freqs, periodogram, n, index, fap = fasper(t, m, oversampling, hifac)
	endtime = datetime.now()
	periods = 1.0 / freqs

	# Restrict range
	periods, periodogram = periods[periods <= maximum], periodogram[periods <= maximum]
	period = periods[np.argmax(periodogram)]
	extra = ', $\mathrm{FAP} = %.1e$' % (fap,)

	fig, ax = plt.subplots(nrows = 1, figsize = (12, 6))

	f = MultiFourierFit(phase(t, period), m, 5)
	ax.errorbar(phase(t, period), m, yerr = dm, fmt = '.k', ecolor = 'gray', label = filename.replace('.time', ''))
	ax.plot(np.linspace(0, 1, 1e3), f.fourier(np.linspace(0, 1, 1e3)), 'r-', lw = 2, label = r'$T_{\text{LS}} = %.2f$' %(period,))
	ax.set_ylim((m.mean() - 3 * m.std(), m.mean() + 3 * m.std()))
	ax.set_xlabel('$\phi$', size = 38)
	if options.band == 'r':
		ax.set_ylabel('$m$ ($R_E$)', size = 36)
	else:
		ax.set_ylabel('$m$ ($B_E$)', size = 36)
	ax.invert_yaxis()
	ax.legend()

	if options.name:
		figurepath = os.path.join(options.name + '.png')
	else:
		figurepath = os.path.join(filename.split('.time')[0] + '.png')

	if options.interactive:
		plt.show()
	else:
		print 'Saving to %s...' % (figurepath,)

		fig.savefig(figurepath, dpi = 200, bbox_inches = 'tight', rasterize = True)
