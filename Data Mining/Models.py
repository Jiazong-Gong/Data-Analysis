import sklearn
import torch
from torch import nn as nn
from sklearn import svm, tree
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import *
from sklearn.metrics import *
sns.set()


# Linear Classifier
def LClassifier(X, y):
    clf = LogisticRegression(max_iter=1000)
    clf = clf.fit(X, y)
    return clf


# Decision Tree Classifier
def DTClassifier(X, y):
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X, y)
    return clf


# SVM Classifier
def SVMClassifier(X, y):
    clf = svm.SVC()
    clf.fit(X, y)
    return clf


# Neural Network Classifier
class Net(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(Net, self).__init__()
        self.classifier = nn.Sequential(
            # nn.BatchNorm1d(input_size),
            nn.Linear(input_size, hidden_size),
            nn.Sigmoid(),
            # nn.BatchNorm1d(num_features=hidden_size),
            nn.Linear(hidden_size, num_classes),
            nn.Sigmoid()
        )

    def forward(self, x):
        out = self.classifier(x)
        return out


# obtain prediction
def prediction(network, data):
    train_input = data.iloc[:, :-1]
    train_target = data.iloc[:, -1]

    inputs = torch.Tensor(train_input.values).float()
    targets = torch.Tensor(train_target.values - 1).long()

    # outputs = network(inputs)
    outputs = network(inputs)
    _, predicted = torch.max(outputs, 1)
    return predicted, targets


# K-means Clustering
def Clustering(data, k):
    Kmean = KMeans(n_clusters=k)
    Kmean.fit(data)
    return Kmean


# Linear NN
class LinearNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(LinearNN, self).__init__()
        self.Regression = nn.Sequential(
            # nn.BatchNorm1d(input_size),
            nn.Linear(input_size, hidden_size),
            nn.Sigmoid(),
            # nn.BatchNorm1d(num_features=hidden_size),
            nn.Linear(hidden_size, num_classes),
            nn.Sigmoid()
        )

    def forward(self, x):
        out = self.Regression(x)
        return out


# Regression Tree
def DTRegression(X, y):
    reg = tree.DecisionTreeRegressor()
    reg = reg.fit(X, y)
    return reg


def make_roc(classifier, classifier_name, cv, X, y):
    tprs = []
    aucs = []
    accs = []
    mean_fpr = np.linspace(0, 1, 100)
    fig, ax = plt.subplots()
    for i, (train, test) in enumerate(cv.split(X, y)):
        classifier.fit(X[train], y[train])
        viz = plot_roc_curve(classifier, X[test], y[test],
                             name='ROC fold {}'.format(i),
                             alpha=0.3, lw=1, ax=ax)
        predictions = classifier.predict(X[test])
        accuracy = accuracy_score(y[test], predictions)
        interp_tpr = np.interp(mean_fpr, viz.fpr, viz.tpr)
        interp_tpr[0] = 0.0
        tprs.append(interp_tpr)
        aucs.append(viz.roc_auc)
        accs.append(accuracy)
    print(accuracy)
    ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
            label='Chance', alpha=.8)

    mean_tpr = np.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = auc(mean_fpr, mean_tpr)
    std_auc = np.std(aucs)
    ax.plot(mean_fpr, mean_tpr, color='b',
            label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
            lw=2, alpha=.8)

    std_tpr = np.std(tprs, axis=0)
    tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
    ax.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                    label=r'$\pm$ 1 std. dev.')

    ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05],
           title=classifier_name)
    ax.legend(loc="lower right")
    plt.show()
    
    
# Confusion matrix visualization
# Referred to: https://github.com/DTrimarchi10/confusion_matrix
def make_confusion_matrix(cf,
                          group_names=None,
                          categories='auto',
                          count=True,
                          percent=True,
                          cbar=True,
                          xyticks=True,
                          xyplotlabels=True,
                          figsize=None,
                          cmap='Blues',
                          title=None):
    '''
    This function will make a pretty plot of an sklearn Confusion Matrix cm using a Seaborn heatmap visualization.
    Arguments
    ---------
    cf:            confusion matrix to be passed in
    group_names:   List of strings that represent the labels row by row to be shown in each square.
    categories:    List of strings containing the categories to be displayed on the x,y axis. Default is 'auto'
    count:         If True, show the raw number in the confusion matrix. Default is True.
    normalize:     If True, show the proportions for each category. Default is True.
    cbar:          If True, show the color bar. The cbar values are based off the values in the confusion matrix.
                   Default is True.
    xyticks:       If True, show x and y ticks. Default is True.
    xyplotlabels:  If True, show 'True Label' and 'Predicted Label' on the figure. Default is True.
    sum_stats:     If True, display summary statistics below the figure. Default is True.
    figsize:       Tuple representing the figure size. Default will be the matplotlib rcParams value.
    cmap:          Colormap of the values displayed from matplotlib.pyplot.cm. Default is 'Blues'
                   See http://matplotlib.org/examples/color/colormaps_reference.html

    title:         Title for the heatmap. Default is None.
    '''

    # CODE TO GENERATE TEXT INSIDE EACH SQUARE
    blanks = ['' for i in range(cf.size)]

    if group_names and len(group_names) == cf.size:
        group_labels = ["{}\n".format(value) for value in group_names]
    else:
        group_labels = blanks

    if count:
        group_counts = ["{0:0.0f}\n".format(value) for value in cf.flatten()]
    else:
        group_counts = blanks

    if percent:
        group_percentages = ["{0:.2%}".format(value) for value in cf.flatten() / np.sum(cf)]
    else:
        group_percentages = blanks

    box_labels = [f"{v1}{v2}{v3}".strip() for v1, v2, v3 in zip(group_labels, group_counts, group_percentages)]
    box_labels = np.asarray(box_labels).reshape(cf.shape[0], cf.shape[1])

    # Accuracy is sum of diagonal divided by total observations
    accuracy = np.trace(cf) / float(np.sum(cf))

    # if it is a binary confusion matrix, show some more stats
    if len(cf) == 2:
        # Metrics for Binary Confusion Matrices
        precision = cf[1, 1] / sum(cf[:, 1])
        recall = cf[1, 1] / sum(cf[1, :])
        f1_score = 2 * precision * recall / (precision + recall)
        stats_text = "\n\nAccuracy={:0.3f}\nPrecision={:0.3f}\nRecall={:0.3f}\nF1 Score={:0.3f}".format(
            accuracy, precision, recall, f1_score)
    else:
        stats_text = "\n\nAccuracy={:0.3f}".format(accuracy)

    # SET FIGURE PARAMETERS ACCORDING TO OTHER ARGUMENTS
    if figsize == None:
        # Get default figure size if not set
        figsize = plt.rcParams.get('figure.figsize')

    if xyticks == False:
        # Do not show categories if xyticks is False
        categories = False

    # MAKE THE HEATMAP VISUALIZATION
    plt.figure(figsize=figsize)
    sns.heatmap(cf, annot=box_labels, fmt="", cmap=cmap, cbar=cbar, xticklabels=categories, yticklabels=categories)

    if xyplotlabels:
        plt.ylabel('True label')
        plt.xlabel('Predicted label' + stats_text)
    else:
        plt.xlabel(stats_text)

    if title:
        plt.title(title)