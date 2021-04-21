# Behavior Tree Robot Action Policy from SAR WoZ Interaction Data

##### This repository was made to facilitate the investigations in developing behavior tree robot action policy from Socially Assistive Robot (SAR) Wizard of Oz (WoZ) Interaction Data. This pipeline processes logged data from a WoZ interaction and generates behavior trees, along with data on the accuracy of the conversion process. These behavior trees are ready to be used alongside the BehaviorTree.CPP library, and redeployed back in the robot.

---
## Install
1. Clone repo
2. Install python3 dependencies below (you can create a  python3 [virtual environment](https://docs.python.org/3/library/venv.html) and activate it if you would like first)
3. Fix [graphviz error via package install](#graphviz-pip-error)
4. Fix [pyeda library error](#pyeda-literal-error)

## To run an example:

- Navigate to `BehaviorTreeDev/`
- `python3`: run `python3 run.py -c example/config.json`


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

Easy copy paste:
```
pip3 install pandas sklearn graphviz imblearn matplotlib lxml py_trees pyeda
sudo apt-get install graphviz
```
There are two other install issues due to issue with `graphiz` and `pyeda` packages. You will need to do the fixes below.

### graphviz pip error
graphiz for python is broken. Instead, install via package manager:
```bash
sudo apt-get install graphviz
```
For OSX, likely you will need to `brew install` but this is yet to be tested.

### pyeda literal error
There is a bug is Pyeda library. See [#17](https://github.com/interaction-lab/BTFromSARDemostration/issues/17) for fix.



