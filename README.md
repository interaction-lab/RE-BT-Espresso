# Behavior Tree Robot Action Policy from SAR WoZ Interaction Data

##### This repository was made to facilitate the investigations in developing behavior tree robot action policy from Socially Assistive Robot (SAR) Wizard of Oz (WoZ) Interaction Data. This pipeline processes logged data from a WoZ interaction and generates behavior trees, along with data on the accuracy of the conversion process. These behavior trees are ready to be used alongside the BehaviorTree.CPP library, and redeployed back in the robot.

IMPORTANT: The repo is not clean in the slightest as it is divulging near deadlines. This will be cited as "`open-source`" in the sense that all code can be audited/read. I personally find pseudo code within papers more difficult to read than poorly written real code. If you are looking for the algorithm described within the paper, you will want to look at `BehaviorTreeDev/BehaviorTreeBuilder.py` starting with function `bt_espresso_mod`.

---
## Install
1. Clone repo
2. Install python3 dependencies below (you can create a  python3 [virtual environment](https://docs.python.org/3/library/venv.html) and activate it if you would like first)
3. Fix [graphviz error via package install](#graphviz-pip-error)
4. Fix [pyeda library error](#pyeda-literal-error)

## Running:
- For running the builder etc, navigate to `BehaviorTreeDev/`
    - BehaviorTreePipeline: `python3 run.py -c example/config.json`
    - Recoloring Output: `python3 color_bt_trees.py -d .` (replace `.` with any parent directory of the output, example defaults to the `output` directory)
- For simulating data, navigate to `DataSim`
    1. `python3 bt_sim.py path/to/tree/config/you/want` (likely under `/config`)
    2. Run it on the behavior tree builder, recreate a config based on `BehaviorTreeDev/example/config.json` with conrrect output data paths, variables, etc.


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



