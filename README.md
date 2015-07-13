### On the (Predictive) Performance of Photometric Variability Classifiers
*Automated, Supervised Machine Learning Approaches Using Support Vector Machines, Random Forests & Gradient Boosted Trees.*

- **Author**: Markus Beuckelmann
- **Supervisors**: PD Dr. Coryn Bailer–Jones, Dr. Kester Smith, Dr. Dae–Won Kim
- **Examinors**: PD Dr. Coryn Bailer–Jones, PD Dr. Christian Fendt
- **Institution**: [Max Planck Institute for Astronomy](http://www.mpia.de) (MPIA)
- **Submision**: July 2015
- **Abstract**: *This work assesses the predictive performance of different automated, supervised Machine Learning approaches for the classification of astrophysical variables based on their photometric variability. We extract 64 ad–hoc features in R_E , B_E and R_E − B_E from 32683 EROS–2 light curves of known periodic, semi–periodic and aperiodic sources in the Large Magellanic Cloud (LMC). To characterize the periodicity of the signals, we make use of both Lomb–Scargle and the conditional entropy (CE) algorithm for period–finding. In this context, we present a fast Python/Cython implementation of the CE algorithm. To provide further separation of quasars in feature space, we implement the structure function to quantify the source’s intrinsic stochastic variability. Using a training set containing labels for 9 superclasses and 25 subclasses provided by [Kim et al. [2014]](http://www.aanda.org/articles/aa/pdf/2014/06/aa23252-13.pdf), we train three different models on the extracted features, namely Support Vector Machines (SVMs), Random Forest (RF) and Gradient Boosted Trees (GBT), and optimize the model’s hyperparameters for the average, weighted F1–score for superclasses and subclasses by performing a grid search using 5–fold cross–validation. We find that the decision tree based models, RF and GBT, outperform the SVM in both superclass and subclass classification. The highest scores are achieved by the GBT classifier with an average, weighted F1–score of (98.43 ± 0.07) % for superclass classification and (86.30 ± 0.37) % for subclass classification.*
- This is a report accounting for a Bachelor of Science (B.Sc.) thesis in Physics at Heidelberg University (Germany).

#### Selected figures

...
