# Behavior Tree Robot Action Policy from SAR WoZ Interaction Data

---

Adam Wathieu, Summer 2020

---

##### This repository was made to facilitate the investigations in developing behavior tree robot action policy from Socially Assistive Robot (SAR) Wizard of Oz (WoZ) Interaction Data. This pipeline processes logged data from a WoZ interaction and generates behavior trees, along with data on the accuracy of the conversion process. These behavior trees are ready to be used alongside the BehaviorTree.CPP library, and redeployed back in the robot.

---
## Install
1. Clone repo
2. Create python3 [virtual environment](https://docs.python.org/3/library/venv.html) and activate it
3. Install python3 requirements via `pip3 install -r requirements.txt`
4. Fix [graphviz error via package install](#graphviz-pip-error)
5. Fix [pyeda library error](#pyeda-literal-error)

## To run:

- Navigate to `BehaviorTreeDev/`
- edit `config.json`
- You can run in two ways, via `python3` and via `bash`. Bash will be deprecated in the future.
	- `python3`: run `python3 run.py`
	- `bash`: run`./clean_script.sh config.json` in command line



## Dependencies (with pip installation commands)

- [Python 3](https://www.python.org/downloads/)
- [pandas](https://pandas.pydata.org/pandas-docs/stable/index.html) (`pip install pandas`)
- [scikit-learn](https://scikit-learn.org/stable/index.html) (`pip install -U scikit-learn`)
- [numpy](https://numpy.org/) (`pip install numpy`)
- [imblearn](https://imbalanced-learn.readthedocs.io/en/stable/index.html) (`pip install -U imbalanced-learn`)
- [graphviz](https://graphviz.readthedocs.io/en/stable/index.html) (`pip install graphviz`)
- [matplotlib](https://matplotlib.org/) (`pip install matplotlib`)
- [lxml](https://lxml.de/) (`pip install lxml`)

See `requirements.txt` for all python3 packages. There are two other install issues due to issue with `graphiz` and `pyeda` packages. Fixes below.

### graphviz pip error
graphiz for python is broken. Instead, install via package manager:
```bash
sudo apt-get install graphviz
```
For OSX, likely you will need to `brew install` but this is yet to be tested.

### pyeda literal error
There is a bug is Pyeda library. See [#17](https://github.com/interaction-lab/BTFromSARDemostration/issues/17) for fix.

---

The behavior tree XML file(s) that are generated from the pipeline follow the XML format for behavior trees presented in [BehaviorTree.CPP](https://www.behaviortree.dev/) and [Groot](https://github.com/BehaviorTree/Groot).

