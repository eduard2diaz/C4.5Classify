from sklearn.datasets import load_iris
import graphviz
import matplotlib.pyplot as plt
from sklearn import tree
"""X, y = load_iris(return_X_y=True)
clf = tree.DecisionTreeClassifier()
clf = clf.fit(X, y)
tree.plot_tree(clf)
dot_data = tree.export_graphviz(clf, out_file=None)
graph = graphviz.Source(dot_data)
graph.render("iris")"""
conj=[]
conj.append()
conj.append({'name':'eduardo','edad':29})
conj.insert('value',{'name':'eduardo','edad':29})
print(conj)