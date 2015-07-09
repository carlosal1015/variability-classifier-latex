#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import numpy as np

from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Cursor
from optparse import OptionParser
from datetime import datetime

from fitting import MultiFourierFit
from helpers import phase

DATADIR = '../../../data/eros'
LIGHTCURVEDIR = os.path.join(DATADIR, 'lightcurves')

algorithms = ['fasper', 'gatspy-fast', 'ce-adaptive', 'ce']

parser = OptionParser()
usage = 'Usage: ./%prog --lightcurves <FILE>[,...] --algorithm <' + '|'.join(algorithms) + '> --band [R|G|RB] --minimum <PERIOD> --maximum <PERIOD>'
parser = OptionParser(usage = usage)
parser.add_option('--lightcurves', dest = 'lightcurves', default = [], help = 'Specify a lightcurve to work on.')
parser.add_option('--algorithm', dest = 'algorithm', default = algorithms[0], help = 'Specify the algorithm to be used.')
parser.add_option('--band', dest = 'band', default = 'R', help = 'Specify the band to be used.')
parser.add_option('--minimum', dest = 'minimum', default = None, type = float, help = 'Specify the minimum period to be searched for.')
parser.add_option('--maximum', dest = 'maximum', default = None, type = float, help = 'Specify the maximum period to be searched for.')
parser.add_option('--resolution', dest = 'resolution', default = 0.01, type = float, help = 'Specify the resolution (difference between two adjacent candidate periods).')
parser.add_option('--points', dest = 'points', default = False, action = 'store_true', help = 'Indicate the datapoints in the periodogram.')
(options, args) = parser.parse_args()

if not options.lightcurves:
	print 'Please specify a lightcurve.'
	sys.exit(1)

options.lightcurves = options.lightcurves.split(',')
options.lightcurves = [element + '.time' for element in options.lightcurves if not element.endswith('.time')]

if options.algorithm in algorithms:
	print 'Using %s algorithm to determine the period...' % (options.algorithm,)
else:
	print 'Algorithm %s is not implemented.' % (options.algorithm,)
	sys.exit(1)

for filename in options.lightcurves:

	path = os.path.join(LIGHTCURVEDIR, filename)
	if not os.path.exists(path):
		print 'No lightcurve found at "%s".' % (path,)
		continue

	data = np.loadtxt(path)
	if options.band == 'R':
		t, m, dm = data[:,0], data[:,1], data[:,2]
	elif options.band == 'B':
		t, m, dm = data[:,0], data[:,3], data[:,4]
	elif options.band == 'RB':
		t, R, dR, B, dB = data[:,0], data[:,1], data[:,2], data[:,3], data[:,4]
		m, dm = R - B, dR - dB
	else:
		print '%s is not a valid band.' % (options.band)
		continue

	mask = np.abs(m) < 50
	t, m, dm = t[mask], m[mask], dm[mask]

	minimum, maximum = options.minimum, options.maximum
	if not minimum:
		minimum = 0.03
	if not maximum:
		maximum = int(0.5 * (np.max(t) - np.min(t)))

	print 'Searching for periods between %.2f and %.2f days (resolution %.4f days)...' % (minimum, maximum, options.resolution)

	################################################################################
	# fasper implementation
	################################################################################

	if options.algorithm == 'fasper':

		from fasper import fasper

		oversampling = 8.0
		minimum_period = minimum # in days

		# Average nyquist frequency
		average_nyquist_frequency = 0.5 * len(t) / (np.max(t) - np.min(t))
		# Average nyquist period
		average_nyquist_period = 1.0 / average_nyquist_frequency
		hifac = int(average_nyquist_period / minimum_period)
		if hifac < 200:
			hifac = 200

		# hifac = average_nyquist_period / minimum_period = maximum_frequency / average_nyquist_frequency
		# maximum_frequency = 1.0 / minimum_period

		#print 'Average nyquist frequency: %.4f' % (average_nyquist_frequency,)
		#print 'Average nyquist period: %.4f' % (average_nyquist_period,)
		#print 'HIFAC: %d' % (hifac,)

		starttime = datetime.now()
		freqs, periodogram, n, index, fap = fasper(t, m, oversampling, hifac)
		endtime = datetime.now()
		periods = 1.0 / freqs

		# Restrict range
		periods, periodogram = periods[periods <= maximum], periodogram[periods <= maximum]
		period = periods[np.argmax(periodogram)]
		extra = ''

	################################################################################
	# gastpy/LombScargleFast
	################################################################################

	elif options.algorithm == 'gatspy-fast':

		from gatspy.periodic import LombScargleFast

		oversampling = 4.0
		hifac = 200
		starttime = datetime.now()
		model = LombScargleFast().fit(t, m, dm)
		periods, periodogram = model.periodogram_auto(oversampling = oversampling, nyquist_factor = hifac)
		endtime = datetime.now()

		# Restrict range
		periods, periodogram = periods[periods <= maximum], periodogram[periods <= maximum]
		period = periods[np.argmax(periodogram)]
		extra = ''

	################################################################################

	################################################################################
	# Conditional entropy (adaptive grid)
	################################################################################

	elif options.algorithm == 'ce-adaptive':

		from ce import ConditionalEntropy

		starttime = datetime.now()
		model = ConditionalEntropy(t, m, verbose = True)
		periods, periodogram = model.periodogram()
		period = model.best_periods[0]
		endtime = datetime.now()

		print 'Periods: ' + str(model.best_periods)
		print 'Scores: ' + str(model.best_scores)

		extra = ''

	################################################################################

	################################################################################
	# Conditional entropy
	################################################################################

	elif options.algorithm == 'ce':

		from ce import conditionalentropy

		starttime = datetime.now()
		grid = np.arange(0.03, 20, 0.01)
		periods, periodogram = conditionalentropy(t, m, grid)
		period = periods[np.argmin(periodogram)]
		endtime = datetime.now()

		print 'Best period: ' + str(period)

		extra = ''

	################################################################################

	print
	print 'Runtime: %s' % (endtime - starttime)
	print 'Best period: %.4f days' % (period,)
	print 'Number of periods on the grid: %.2f' % (len(periodogram),)

	fig, ax = plt.subplots(nrows = 1, figsize = (12, 6))

	ax.plot(periods, periodogram, label = '$P = %.4f$' %(period,) + extra)
	if options.points:
		ax.plot(periods, periodogram, 'k.')

	ax.set_xlim(0, 2 * period)
	ax.set_xlabel('$T$ $[\mathrm{d}]$', size = 32)
	if options.algorithm.startswith('ce'):
		ax.set_ylabel(r'$\text{CE}$', size = 28)
	else:
		ax.set_ylabel('Power', size = 32)
	ax.tick_params(axis = 'both', labelsize = 17)
	ax.tick_params(axis = 'x', pad = 10)
	properties = dict(boxstyle = 'round', facecolor = 'white', alpha = 0.75)
	ax.axvline(x = period, linewidth = 0.5, linestyle = 'dashed', color = 'black')
	ax.legend()

	figurepath = '%s-%s.png' % (options.lightcurves[0].replace('.time', ''), options.algorithm)
	print 'Saving to %s...' % (figurepath,)
	fig.savefig(figurepath, dpi = 200, bbox_inches = 'tight', rasterize = True)
	plt.show()
