# RE:BT-Espresso, Representation Exploitation of BT-Espresso for Behavior Trees Learned from Robot Demonstrations 

IMPORTANT: The repo is not clean in the slightest as it is divulging near deadlines. This will be cited as "`open-source`" in the sense that all code can be audited/read. I personally find pseudo code within papers more difficult to read than poorly written real code. If you are looking for the algorithm described within the paper, you will want to look at `BehaviorTreeDev/BehaviorTreeBuilder.py` starting with function `bt_espresso_mod`.

---
## Install
1. Clone repo
2. Install python3 dependencies below (you can create a  python3 [virtual environment](https://docs.python.org/3/library/venv.html) and activate it if you would like first)
3. Fix [graphviz error via package install](#graphviz-pip-error)
4. Fix [pyeda library error](#pyeda-literal-error)

## Running Experiments
In the top level directory, to run all experiments:
`python3 run_experiments.py [-r, --recolor] [-c --config]`
where `-r` is an optional flag to also re-color the trees and `-c` allows a specification of a single experiment. By default, all experiments are run.

## Experiment Pipeline
1. DataSim
2. BuildBT
3. [OPTIONAL] ReColorBT
4. RunResults


## Dependencies

- [Python 3](https://www.python.org/downloads/)
- [pandas](https://pandas.pydata.org/pandas-docs/stable/index.html) 
- [scikit-learn](https://scikit-learn.org/stable/index.html)
- [imblearn](https://imbalanced-learn.readthedocs.io/en/stable/index.html)
- [graphviz](https://graphviz.readthedocs.io/en/stable/index.html)
- [matplotlib](https://matplotlib.org/) 
- [lxml](https://lxml.de/)
- [py_trees](https://py-trees.readthedocs.io/en/devel/)
- [pyeda](https://pypi.org/project/pyeda/)
- [networkx](https://networkx.org/)

Easy copy paste:
```
pip3 install pandas sklearn graphviz imblearn matplotlib lxml py_trees pyeda networkx
sudo apt-get install graphviz
```
There are two other install issues due to issue with `graphiz` and `pyeda` packages. You will need to do the fixes below.

### graphviz pip error
graphiz for python is broken. Instead, install via package manager:
```bash
sudo apt-get install graphviz
```
For OSX, use `brew` instead.

### pyeda literal error
There is a bug is Pyeda library. See [#17](https://github.com/interaction-lab/BTFromSARDemostration/issues/17) for fix.



