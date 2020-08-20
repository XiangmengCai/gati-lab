{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Please specify:\n",
      "--f \t\tfolder path \t\t\t\t\t\t\t(default: current folder)\n",
      "--root \t\troot name \t\t\t\t\t\t\t(default: 'run')\n",
      "--o\t\toutput pdf name \t\t\t\t\t\t(default: output.pdf)\n",
      "--filt \t\t'true' or 'false' obtain filtered.star file \t\t\t(default: false)\n",
      "--sigmafac \tcutoff for 'filt', how many sigma above mean \t\t\t(default: 1)\n",
      "--mic\t\tminimum cutoff for CTFFIND/Gctf resolution estimate \t\t(default: none)\n",
      "\n",
      "I cannot find any data.star files in the provided folder!\n"
     ]
    },
    {
     "ename": "SystemExit",
     "evalue": "",
     "output_type": "error",
     "traceback": [
      "An exception has occurred, use %tb to see the full traceback.\n",
      "\u001b[0;31mSystemExit\u001b[0m\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/Users/Expo/opt/anaconda3/lib/python3.8/site-packages/IPython/core/interactiveshell.py:3351: UserWarning: To exit: use 'exit', 'quit', or Ctrl-D.\n",
      "  warn(\"To exit: use 'exit', 'quit', or Ctrl-D.\", stacklevel=1)\n"
     ]
    }
   ],
   "source": [
    "#!/usr/bin/python\n",
    "# -*- coding: utf-8 -*-\n",
    "\n",
    "## Script to investigate convergence behaviour in relion 3D classification\n",
    "## Copyright Cornelius Gati 2020 - SLAC Natl Acc Lab - cgati@stanford.edu\n",
    "\n",
    "import os\n",
    "import sys\n",
    "import numpy as np\n",
    "import matplotlib\n",
    "import matplotlib.pyplot as plt\n",
    "import matplotlib.mlab as mlab\n",
    "import operator\n",
    "import collections\n",
    "import matplotlib.backends.backend_pdf\n",
    "\n",
    "# from operator import itemgetter\n",
    "\n",
    "################INPUT\n",
    "\n",
    "print ('Please specify:')\n",
    "print ('--f \t\tfolder path \t\t\t\t\t\t\t(default: current folder)')\n",
    "print ('--root \t\troot name \t\t\t\t\t\t\t(default: \\'run\\')')\n",
    "print ('--o\t\toutput pdf name \t\t\t\t\t\t(default: output.pdf)')\n",
    "print ('--filt \t\t\\'true\\' or \\'false\\' obtain filtered.star file \t\t\t(default: false)')\n",
    "print ('--sigmafac \tcutoff for \\'filt\\', how many sigma above mean \t\t\t(default: 1)')\n",
    "print ('--mic\t\tminimum cutoff for CTFFIND/Gctf resolution estimate \t\t(default: none)')\n",
    "\n",
    "folder = '.'\n",
    "rootname = 'run'\n",
    "output = 'output.pdf'\n",
    "plottype = 'bar'\n",
    "micfilt = ''\n",
    "filtstar = 'false'\n",
    "sigmafac = 1\n",
    "\n",
    "for (si, s) in enumerate(sys.argv):\n",
    "    if s == '--f':\n",
    "        folder = sys.argv[si + 1]\n",
    "\n",
    "    if s == '--root':\n",
    "        rootname = sys.argv[si + 1]\n",
    "\n",
    "    if s == '--o':\n",
    "        output = sys.argv[si + 1]\n",
    "\n",
    "    if s == '--plot':\n",
    "        plottype = sys.argv[si + 1]\n",
    "\n",
    "    if s == '--filt':\n",
    "        filtstar = sys.argv[si + 1]\n",
    "\n",
    "    if s == '--sigmafac':\n",
    "        sigmafac = sys.argv[si + 1]\n",
    "\n",
    "    if s == '--mic':\n",
    "        micfilt = sys.argv[si + 1]\n",
    "\n",
    "#### List all files in folder and sort by name\n",
    "\n",
    "filesdir = sorted(os.listdir(folder))\n",
    "unwanted = []\n",
    "\n",
    "## Check number of iterations\n",
    "\n",
    "iterationlist = []\n",
    "iterationtemp = []\n",
    "iterations = []\n",
    "filesdir = sorted(filesdir)\n",
    "\n",
    "for datafile in filesdir:\n",
    "    if 'data.star' in datafile and 'sub' not in datafile:\n",
    "        if 'it001' in datafile and len(folder) == 0:  # Get rootname by looking at first iteration if not specified\n",
    "            rootname = datafile.split('_it')[0]\n",
    "        if 'ct' in datafile.split('_')[-3]:\n",
    "            if int((datafile.split('_')[-2])[2:]) \\\n",
    "                != int((datafile.split('_')[-3])[2:]):\n",
    "                iterationtemp.append(datafile)\n",
    "        if 'ct' not in datafile.split('_')[-3]:\n",
    "            iterationtemp.append(datafile)\n",
    "\n",
    "        # if 'ct' in datafile.split('_')[-3]:\n",
    "        # if int(datafile.split('_')[-2][2:]) != int(datafile.split('_')[-3][2:]):\n",
    "        # ....iterationtemp.append(datafile)\n",
    "\n",
    "        iterations.append(int((datafile.split('_')[-2])[2:]))\n",
    "\n",
    "### Open PDF for output of figures\n",
    "\n",
    "pdf = matplotlib.backends.backend_pdf.PdfPages('%s' % output)\n",
    "\n",
    "## List of all input files used\n",
    "\n",
    "iterationlist = sorted(iterationtemp, key=lambda x: x.split('_')[-2])\n",
    "if len(iterations) == 0:\n",
    "    print ('')\n",
    "    print ('I cannot find any data.star files in the provided folder!')\n",
    "    sys.exit()\n",
    "\n",
    "iterations = max(iterations) + 1\n",
    "\n",
    "##Print used input data.star files\n",
    "\n",
    "print ('')\n",
    "for files in iterationlist:\n",
    "    print ('Using %s as input' % files)\n",
    "\n",
    "##Check number of particles, number of classes, number of micrographs\n",
    "\n",
    "part = 0\n",
    "classes = []\n",
    "micrographlist = []\n",
    "checklist = []\n",
    "checklistcol = []\n",
    "anglerot = []\n",
    "rescol = []\n",
    "\n",
    "with open('%s/%s_it016_data.star' % (folder, rootname), 'rb') as f:\n",
    "    for l in f:\n",
    "        if l[0] == '_' and 10 < len(l) < 50:  # check header\n",
    "            if l.split()[0] == '_rlnClassNumber':  # check header for ClassNumber column\n",
    "                classcolumn = int((l.split()[1])[1:]) - 1\n",
    "            if l.split()[0] == '_rlnMicrographName':  # check header for MicrographName column\n",
    "                miccolumn = int((l.split()[1])[1:]) - 1\n",
    "            if l.split()[0] == '_rlnImageName':  # check header for ParticleName column\n",
    "                particolumn = int((l.split()[1])[1:]) - 1\n",
    "            if l.split()[0] == '_rlnAngleRot':  # check header for ParticleName column\n",
    "                anglerot = int((l.split()[1])[1:]) - 1\n",
    "            if l.split()[0] == '_rlnCtfMaxResolution':  # check header for CtfMaxResolution column\n",
    "                rescol = int((l.split()[1])[1:]) - 1\n",
    "\n",
    "            if '_rln' in l.split()[0]:\n",
    "                checklist.append(int((l.split()[1])[1:]) - 1)\n",
    "                checklistcol.append(l.split()[0])\n",
    "\n",
    "        if '@' in l and l.split()[0] != 'opticsGroup1':\n",
    "            part += 1\n",
    "            classes.append(int(l.split()[classcolumn]))\n",
    "            micrographlist.append(l.split()[miccolumn])\n",
    "\n",
    "classes = max(classes)\n",
    "\n",
    "print ('')\n",
    "print ('Plots will be generated for the following columns:',\n",
    "       checklistcol)\n",
    "\n",
    "## Initial colorbar\n",
    "\n",
    "fig = plt.figure()\n",
    "ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])\n",
    "cmap = plt.get_cmap('jet', int(classes) + 1)\n",
    "norm = matplotlib.colors.Normalize(vmin=1, vmax=int(classes) + 2)\n",
    "\n",
    "# ticks = np.arange(1, int(classes)+1)\n",
    "\n",
    "cb1 = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm,\n",
    "        orientation='horizontal')\n",
    "\n",
    "# colorbar stuff\n",
    "\n",
    "labels = np.arange(0, classes + 2)\n",
    "\n",
    "# cb1 = plt.colorbar(mat, ticks=labels)\n",
    "\n",
    "loc = labels + .5\n",
    "cb1.set_ticks(loc)\n",
    "cb1.set_ticklabels(labels)\n",
    "cb1.ax.tick_params(labelsize=16)\n",
    "cb1.set_label('Class #')\n",
    "cb1.set_label('Color for each class')\n",
    "\n",
    "# cb1.set_label('Class \\'0\\' means unassigned when using small subset')\n",
    "\n",
    "a = ax1.get_xticks().tolist()\n",
    "a[0] = 'no class'\n",
    "a[1:-1] = labels[1:-1]\n",
    "ax1.set_xticklabels(a)\n",
    "\n",
    "pdf.savefig()\n",
    "\n",
    "# plt.show()\n",
    "\n",
    "###### Go into each iteration_data.star file and read in information, such as particle class assignments etc.\n",
    "\n",
    "groupnumarray = np.zeros((part, iterations), dtype=np.double)  # Class assignments over all iterations\n",
    "checkarray = np.empty((part, len(checklist)), dtype=np.double)  # Stats of final iteration\n",
    "check = np.empty((part, 2, iterations), dtype=np.double)  # Stats of final iteration\n",
    "changes = []\n",
    "\n",
    "micnumdict = collections.defaultdict(list)\n",
    "\n",
    "print ('')\n",
    "for datafile in iterationlist:\n",
    "\n",
    "    miciterdict = collections.defaultdict(list)\n",
    "    if 'ct' in datafile:\n",
    "        iteration = int((datafile.split('_')[-2])[2:])\n",
    "    if 'ct' not in datafile:\n",
    "        iteration = int((datafile.split('_')[-2])[2:])\n",
    "\n",
    "    particle = 0\n",
    "    changesum = 0\n",
    "    if int(iteration) > 1:\n",
    "        with open('%s/%s' % (folder, datafile), 'rb') as f:\n",
    "            for l in f:\n",
    "                if '@' in l:\n",
    "                    groupnum = l.split()[classcolumn]  # # Class number\n",
    "                    if int(groupnum) > int(classes):\n",
    "                        groupnum = 0\n",
    "                    micrograph = l.split()[miccolumn]  # # Micrograph name\n",
    "                    particlename = l.split()[particolumn]  # # Particle Name\n",
    "\n",
    "                    groupnumarray[particle, iteration] = groupnum\n",
    "                    miciterdict[micrograph].append(groupnum)\n",
    "                    if int(iteration) == iterations - 1:  # last iteration: all columns of star file to checkarray\n",
    "                        for i in range(0, int(checklist[-1] + 1)):\n",
    "                            if 'mrc' not in l.split()[i]:  # No filenames in checklist\n",
    "                                colval = l.split()[i]\n",
    "                                if 'group' in l.split()[i]:\n",
    "                                    colval = int((l.split()[i])[-2:])\n",
    "                                checkarray[particle, i] = colval\n",
    "                            else:\n",
    "                                checkarray[particle, i] = 0\n",
    "\n",
    "                    if int(iteration) >= iterations - 2:\n",
    "                        for i in range(0, len(checklist) - 1):\n",
    "                            check[particle, 0, iteration] = \\\n",
    "                                l.split()[anglerot]\n",
    "                            check[particle, 1, iteration] = \\\n",
    "                                l.split()[classcolumn]\n",
    "\n",
    "                    if groupnumarray[particle, iteration] \\\n",
    "                        == groupnumarray[particle, int(iteration) - 1]:\n",
    "                        change = 'nan'\n",
    "                        change1 = 0\n",
    "                    if groupnumarray[particle, iteration] \\\n",
    "                        != groupnumarray[particle, int(iteration) - 1]:\n",
    "                        change = groupnum\n",
    "                        change1 = 1\n",
    "                        changesum += 1\n",
    "\n",
    "                    particle += 1\n",
    "    changes.append(changesum)\n",
    "\n",
    "    print ('Iteration %s: %s particles changed class assignments' \\\n",
    "        % (iteration, changesum))\n",
    "\n",
    "    # # After each iteration create Histogram of class assignments for each micrograph\n",
    "\n",
    "    miciterdict = collections.OrderedDict(sorted(miciterdict.items(),\n",
    "            key=operator.itemgetter(0)))\n",
    "    for (key, value) in miciterdict.iteritems():\n",
    "        michisto = []\n",
    "        for numb in value:\n",
    "            michisto.append(float(numb))\n",
    "        classes = int(classes)\n",
    "        michisto = np.histogram(michisto, bins=classes, range=(1,\n",
    "                                classes + 1))\n",
    "        micnumdict[key].append(michisto[0].tolist())\n",
    "\n",
    "######## Plot rotational and translational accuracy over each iteration\n",
    "\n",
    "rotationcol = 2\n",
    "translationcol = 3\n",
    "rotation = np.zeros((int(classes) + 1, iterations), dtype=np.double)\n",
    "translation = np.zeros((int(classes) + 1, iterations), dtype=np.double)\n",
    "\n",
    "for datafile in iterationlist:\n",
    "    iteration = int((datafile.split('_')[-2])[2:])\n",
    "    with open('%s/%s_model.star' % (folder, datafile[:-10]), 'rb') as f:\n",
    "        for l in f:\n",
    "            if '_rlnAccuracyRotations' in l:\n",
    "                rotationcol = int(l.split('#')[-1]) - 1\n",
    "            if '_rlnAccuracyTranslations' in l:\n",
    "                translationcol = int(l.split('#')[-1]) - 1\n",
    "            if 'class' in l and 'mrc' in l and 'mrcs' not in l:\n",
    "                classnum = int((l.split('.mrc')[0])[-3:])\n",
    "                rotation[classnum, iteration] = l.split()[rotationcol]\n",
    "                translation[classnum, iteration] = \\\n",
    "                    l.split()[translationcol]\n",
    "\n",
    "rotation = np.array(rotation[1:])\n",
    "translation = np.array(translation[1:])\n",
    "\n",
    "if len(set(rotation[0])) == 1:\n",
    "    print ('You did not perform image alignment during classification - skipping these two plots!')\n",
    "\n",
    "if len(set(rotation[0])) > 1:\n",
    "\n",
    "# Rotational\n",
    "\n",
    "    cmap = plt.get_cmap('jet', int(classes) + 1)\n",
    "    plt.figure(num=None, dpi=80, facecolor='white')\n",
    "    plt.title('RotationalAccuracy', fontsize=16, fontweight='bold')\n",
    "    plt.xlabel('Iteration #', fontsize=13)\n",
    "    plt.ylabel('RotationalAccuracy', fontsize=13)\n",
    "    plt.grid()\n",
    "    colors = np.arange(1, int(classes) + 1)\n",
    "    d = 0\n",
    "    for (c, r) in zip(colors, rotation):\n",
    "        d = c\n",
    "        plt.plot(r[:], linewidth=3, color=cmap(c), label='Class %s' % d)\n",
    "    ticks = np.arange(2, iterations)\n",
    "    plt.xlim(2, iterations)\n",
    "    plt.legend(loc='best')\n",
    "    pdf.savefig()\n",
    "\n",
    "    # plt.show()\n",
    "\n",
    "# Translational\n",
    "\n",
    "    cmap = plt.get_cmap('jet', int(classes) + 1)\n",
    "    plt.figure(num=None, dpi=80, facecolor='white')\n",
    "    plt.title('TranslationalAccuracy', fontsize=16, fontweight='bold')\n",
    "    plt.xlabel('Iteration #', fontsize=13)\n",
    "    plt.ylabel('TranslationalAccuracy', fontsize=13)\n",
    "    plt.grid()\n",
    "    colors = np.arange(1, int(classes) + 1)\n",
    "    d = 0\n",
    "    for (c, t) in zip(colors, translation):\n",
    "        d = c\n",
    "        plt.plot(t[:], linewidth=3, color=cmap(c), label='Class %s' % d)\n",
    "    ticks = np.arange(2, iterations)\n",
    "    plt.xlim(2, iterations)\n",
    "    plt.legend(loc='best')\n",
    "    pdf.savefig()\n",
    "\n",
    "    # plt.show()\n",
    "\n",
    "###########################################################################\n",
    "\n",
    "### Sort group assignment array column by column\n",
    "\n",
    "sortindices = np.lexsort(groupnumarray[:, 1:].T)\n",
    "groupnumarraysorted = groupnumarray[sortindices]\n",
    "\n",
    "### Heat map of group sizes\n",
    "\n",
    "H = groupnumarraysorted[:, :]\n",
    "cmap = plt.get_cmap('jet', int(classes) + 1)\n",
    "norm = matplotlib.colors.Normalize(vmin=0, vmax=int(classes) + 1)\n",
    "plt.figure(num=None, dpi=120, facecolor='white')\n",
    "plt.title('Class assignments of each particle', fontsize=16,\n",
    "          fontweight='bold')\n",
    "plt.xlabel('Iteration #', fontsize=13)\n",
    "plt.ylabel('Particle #', fontsize=13)\n",
    "mat = plt.imshow(H, aspect='auto', interpolation='nearest', cmap=cmap,\n",
    "                 norm=norm)\n",
    "\n",
    "# colorbar stuff\n",
    "\n",
    "labels = np.arange(0, classes + 2)\n",
    "\n",
    "# labels[-1] = 'unassigned'\n",
    "\n",
    "cb1 = plt.colorbar(mat, ticks=labels)\n",
    "loc = labels + .5\n",
    "\n",
    "# print loc\n",
    "\n",
    "cb1.set_ticks(loc)\n",
    "a[0] = 'no class'\n",
    "a[1:-1] = labels[1:-1]\n",
    "cb1.set_ticklabels(a)\n",
    "cb1.ax.tick_params(labelsize=16)\n",
    "cb1.set_label('Class #')\n",
    "plt.xlim(2, iterations - .5)\n",
    "\n",
    "pdf.savefig()\n",
    "\n",
    "# plt.show()\n",
    "\n",
    "### Plot heat map of the last 5 iterations (close-up)\n",
    "\n",
    "H = groupnumarraysorted[:, :]\n",
    "cmap = plt.get_cmap('jet', int(classes) + 1)\n",
    "norm = matplotlib.colors.Normalize(vmin=0, vmax=int(classes) + 1)\n",
    "plt.figure(num=None, dpi=120, facecolor='white')\n",
    "plt.title('Class assignments of each particle - last 5 iterations',\n",
    "          fontsize=16, fontweight='bold')\n",
    "plt.xlabel('Iteration #', fontsize=13)\n",
    "plt.ylabel('Particle #', fontsize=13)\n",
    "mat = plt.imshow(H, aspect='auto', interpolation='nearest', cmap=cmap,\n",
    "                 norm=norm)\n",
    "\n",
    "# colorbar stuff\n",
    "\n",
    "labels = np.arange(0, classes + 2)\n",
    "cb1 = plt.colorbar(mat, ticks=labels)\n",
    "loc = labels + .5\n",
    "cb1.set_ticks(loc)\n",
    "a[0] = 'no class'\n",
    "a[1:-1] = labels[1:-1]\n",
    "cb1.set_ticklabels(a)\n",
    "cb1.ax.tick_params(labelsize=16)\n",
    "cb1.set_label('Class #')\n",
    "plt.xlim(iterations - 6.5, iterations - .5)\n",
    "pdf.savefig()\n",
    "\n",
    "# plt.show()\n",
    "\n",
    "#########################################################################################################################################################\n",
    "### Sort group assignment array column by column\n",
    "\n",
    "check = check[sortindices]\n",
    "\n",
    "#### Jumper analysis\n",
    "\n",
    "checkdict = collections.defaultdict(list)\n",
    "checktest = []\n",
    "labelsY = []\n",
    "\n",
    "for c in check:\n",
    "    checkdict[c[:][1][-1]].append(c[:][1][-2])\n",
    "for (key, value) in checkdict.iteritems():\n",
    "    (hist, bins) = np.histogram(value, bins=np.arange(1, int(classes)\n",
    "                                + 2))  # , normed=True)\n",
    "    checktest.append(hist)\n",
    "    labelsY.append(int(key))\n",
    "\n",
    "fig = plt.figure(num=None, dpi=80, facecolor='white')\n",
    "ax = fig.add_subplot(111)\n",
    "plt.title('Class assignment of each particle - last iteration',\n",
    "          fontsize=16, fontweight='bold')\n",
    "plt.xlabel('Class assignment iteration %s' % (int(iterations) - 2),\n",
    "           fontsize=13)\n",
    "plt.ylabel('Class assignment iteration %s' % (int(iterations) - 1),\n",
    "           fontsize=13)\n",
    "plt.grid()\n",
    "ticks = np.arange(0, int(classes) + 1)\n",
    "labelsX = np.arange(1, int(classes) + 2)\n",
    "plt.xticks(ticks, labelsX)\n",
    "plt.yticks(ticks, labelsY)\n",
    "plt.imshow(checktest, aspect='auto', interpolation='nearest',\n",
    "           origin='lower')  # FIXME values in box\n",
    "cb2 = plt.colorbar(ticks=np.arange(0, 1, 0.1))\n",
    "cb2.set_label('Fraction of particles went into group #')\n",
    "plt.figtext(0, 0,\n",
    "            'Particle class assignment changes in the last iteration')\n",
    "pdf.savefig()\n",
    "\n",
    "# plt.show()\n",
    "\n",
    "######################################################################################################################\n",
    "###########################################################################\n",
    "#### Class assignments per micrograph of the last iteration\n",
    "\n",
    "### Convert dictionary to 2D array\n",
    "\n",
    "micval = []\n",
    "micfirst = []\n",
    "micticks = []\n",
    "for mics in micnumdict:\n",
    "    (max_index, max_value) = max(enumerate(micnumdict[mics][-1]),\n",
    "                                 key=operator.itemgetter(1))\n",
    "    micval.append(micnumdict[mics][-1])\n",
    "    micticks.append(mics)\n",
    "\n",
    "### Sort last iter by most prominent group\n",
    "\n",
    "micval = np.array(micval)\n",
    "\n",
    "### Plot heat map last iteration\n",
    "\n",
    "cmap = plt.get_cmap('jet', np.max(micval) - np.min(micval) + 1)\n",
    "plt.figure(num=None, dpi=80, facecolor='white')\n",
    "plt.title('Class assignments of each micrograph - last iteration',\n",
    "          fontsize=16, fontweight='bold')\n",
    "plt.xlabel('Class #', fontsize=13)\n",
    "plt.ylabel('Micrograph #', fontsize=13)\n",
    "ticks = np.arange(0, int(classes) + 1)\n",
    "labels = np.arange(1, int(classes) + 2)\n",
    "plt.xticks(ticks, labels)\n",
    "plt.grid()\n",
    "plt.imshow(micval, aspect='auto', interpolation='nearest', cmap=cmap)\n",
    "cb3 = plt.colorbar()\n",
    "cb3.set_label('Total number of particles in class #')\n",
    "plt.figtext(0, 0,\n",
    "            'Micrographs contributing to certain classes (e.g. important when merging datasets)'\n",
    "            )\n",
    "pdf.savefig()\n",
    "\n",
    "# plt.show()\n",
    "\n",
    "###### Find out how often particles are jumping\n",
    "\n",
    "scorelist = []\n",
    "for g in groupnumarraysorted[:, 2:]:\n",
    "\n",
    "    count = 1\n",
    "    stayed = 0\n",
    "    g = g[::-1]  # # reverse order\n",
    "    for (i, ig) in enumerate(g):\n",
    "        if i > 0 and count > 0:\n",
    "\n",
    "            if len(set(g)) == 1:\n",
    "                stayed = 0\n",
    "                count = 0\n",
    "            if int(ig) == int(g[i - 1]):\n",
    "                count += 1\n",
    "            if int(ig) != int(g[i - 1]):\n",
    "                stayed = count\n",
    "                count = 0\n",
    "\n",
    "    g = g.tolist()\n",
    "    counter = [[x, g.count(x)] for x in set(g)]\n",
    "\n",
    "    # score3 = (iterations-2)/float(len(counter))\n",
    "\n",
    "    score2 = float(len(counter))\n",
    "    score1 = stayed / score2 / (iterations - 2)\n",
    "    scorelist.append(score1)\n",
    "\n",
    "plt.figure(num=None, dpi=80, facecolor='white')\n",
    "plt.title('Particle jump score', fontsize=16, fontweight='bold')\n",
    "plt.xlabel('Score = (# class assignments/# of iterations)', fontsize=13)\n",
    "plt.ylabel('# of particles with score normalized', fontsize=13)\n",
    "plt.grid()\n",
    "\n",
    "# histbins = sorted(set(scorelist))\n",
    "\n",
    "histbins = np.arange(0, .5, 0.05)\n",
    "plt.hist(scorelist, bins=histbins, normed=True)\n",
    "mean1 = np.mean(scorelist)\n",
    "variance1 = np.var(scorelist)\n",
    "sigma1 = np.sqrt(variance1)\n",
    "\n",
    "# x1 = np.linspace(min(scorelist), max(scorelist), 100)\n",
    "\n",
    "x1 = np.linspace(0, .5, 100)\n",
    "plt.figtext(0, 0, 'Gaussian sigma: %s, variance: %s, mean: %s'\n",
    "            % (sigma1, variance1, mean1))\n",
    "plt.plot(x1, scipy.stats.norm.pdf(x1, mean1, sigma1))\n",
    "pdf.savefig()\n",
    "\n",
    "### Number of assignment changes per iteration\n",
    "\n",
    "plt.figure(num=None, dpi=80, facecolor='white')\n",
    "plt.title('Total assignment changes per iteration', fontsize=16,\n",
    "          fontweight='bold')\n",
    "plt.xlabel('Iteration #', fontsize=13)\n",
    "plt.ylabel('# of changed assignments', fontsize=13)\n",
    "plt.grid()\n",
    "plt.plot(changes[2:])\n",
    "pdf.savefig()\n",
    "\n",
    "# plt.show()\n",
    "\n",
    "#########################################################################################################################################################\n",
    "\n",
    "checkarraysorted = checkarray[sortindices]\n",
    "\n",
    "### Plot histogram of each column in data.star sorted by the class assignments of the last iteration\n",
    "\n",
    "histocolarray = collections.defaultdict(list)\n",
    "\n",
    "for column in checkarraysorted.transpose():\n",
    "    lastitgrouparray = collections.defaultdict(list)\n",
    "    for (ci, col) in enumerate(column):\n",
    "        lastitgrouparray[groupnumarraysorted[:, -1][ci] - 1].append(col)\n",
    "\n",
    "        # print groupnumarraysorted[:,-1][ci]-1, ci, col\n",
    "\n",
    "    for (key, value) in lastitgrouparray.iteritems():\n",
    "        histocolarray[key].append(value)\n",
    "\n",
    "        # print key....#STILL has 0,3,4!!!\n",
    "\n",
    "fincolarray = collections.defaultdict(list)\n",
    "\n",
    "for (key, value) in histocolarray.iteritems():\n",
    "    for (vi, v) in enumerate(value):\n",
    "\n",
    "        # print key, vi, v....................########### LOSING KEY\n",
    "\n",
    "        fincolarray[vi].append(v)\n",
    "\n",
    "for (key2, value2) in fincolarray.iteritems():\n",
    "    rangeval = []  # temp2 = [];\n",
    "    temp = []\n",
    "\n",
    "    for (vi2, v2) in enumerate(value2):\n",
    "        for v3 in v2:\n",
    "            rangeval.append(v3)\n",
    "\n",
    "    if len(set(rangeval)) > 1:\n",
    "        for (vi2, v2) in enumerate(value2):\n",
    "            temp.append(v2)\n",
    "\n",
    "    if len(temp) > 0:\n",
    "        plt.figure(num=None, dpi=120, facecolor='white')\n",
    "\n",
    "        if plottype == 'bar':\n",
    "            (n, bins, patches) = plt.hist(temp, range=(min(rangeval),\n",
    "                    max(rangeval)), histtype='bar')\n",
    "            cmap = plt.get_cmap('jet', classes + 1)\n",
    "            colors = np.arange(0, classes + 1)\n",
    "            for (c, p) in zip(colors, patches):\n",
    "\n",
    "                # d = c+1\n",
    "\n",
    "                d = int(histocolarray.keys()[c]) + 1  # recolor based on class HACK\n",
    "                plt.setp(p, 'facecolor', cmap(d))\n",
    "\n",
    "            # plt.colorbar(ticks=np.arange(1, int(classes)+1))\n",
    "\n",
    "        plt.title('Histogram Column %s' % checklistcol[int(key2)],\n",
    "                  fontsize=16, fontweight='bold')\n",
    "        plt.xlabel('%s' % checklistcol[int(key2)], fontsize=13)\n",
    "        plt.ylabel('# particles per bin', fontsize=13)\n",
    "        plt.grid()\n",
    "        pdf.savefig()\n",
    "\n",
    "        # plt.show()\n",
    "\n",
    "########################## DELETE UNWANTED PARTICLES FROM INITIAL STAR FILE ##FIXME\n",
    "\n",
    "particcount = 0\n",
    "initstarfile = '%s_it001_data.star' % rootname\n",
    "a1 = open('%s_filtered.star' % rootname, 'w')\n",
    "if filtstar != 'false' or micfilt != '':\n",
    "\n",
    " # #######################\n",
    "\n",
    "    print ('The mean jump score is: \t\t\t\t\t%s' % mean1)\n",
    "    if sigmafac == 1:\n",
    "        print ('You did not specify a cutoff, I will use a sigma of 1 above mean: %s' \\\n",
    "            % (float(mean1) + float(sigmafac) * float(sigma1)))\n",
    "    if sigmafac != 1:\n",
    "        print ('I will use a cutoff of: \t\t\t\t\t%s' % (float(mean1)\n",
    "                + float(sigmafac) * float(sigma1)))\n",
    "    cutoff = float(mean1) + float(sigmafac) * float(sigma1)\n",
    "\n",
    "    for (i, score) in enumerate(scorelist):\n",
    "        if score > cutoff:\n",
    "            unwanted.append(i)\n",
    "\n",
    " # #######################\n",
    "\n",
    "    with open(initstarfile, 'rb') as g:\n",
    "        for m in g:\n",
    "            if '@' not in m:\n",
    "                a1.write(m)\n",
    "            if '@' in m:\n",
    "                if micfilt != '':\n",
    "                    if float(m.split()[rescol]) <= float(micfilt):\n",
    "                        a1.write(m)\n",
    "\n",
    "                # print('micfilt')\n",
    "\n",
    "                if filtstar != 'false':\n",
    "                    if particcount not in unwanted:\n",
    "                        a1.write(m)\n",
    "\n",
    "                # print('nomicfilt')\n",
    "\n",
    "                if filtstar != 'false' and micfilt != '':\n",
    "                    if float(m.split()[rescol]) <= float(micfilt) \\\n",
    "                        and particcount not in unwanted:\n",
    "                        a1.write(m)\n",
    "\n",
    "                # print('both')\n",
    "\n",
    "                particcount += 1\n",
    "    print ('Saved %s_filtered.star file ommitting %s out of %s particles that changed classes too often' \\\n",
    "        % (rootname, len(unwanted), particcount))\n",
    "a1.close()\n",
    "\n",
    "print ('Saved all plots in %s' % output)\n",
    "pdf.close()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}