### Behavior Tree Robot Action Policy from SAR WoZ Interaction Data

---

Adam Wathieu, Summer 2020

---

##### This repository was made to facilitate the investigations in developing behavior tree robot action policy from Socially Assistive Robot (SAR) Wizard of Oz (WoZ) Interaction Data. This pipeline processes logged data from a WoZ interaction and generates behavior trees, along with data on the accuracy of the conversion process. These behavior trees are ready to be used alongside the BehaviorTree.CPP library, and redeployed back in the robot.

---

Dependencies (with pip installation commands)

- [Python 3](https://www.python.org/downloads/)
- [pandas](https://pandas.pydata.org/pandas-docs/stable/index.html) (`pip install pandas`)
- [scikit-learn](https://scikit-learn.org/stable/index.html) (`pip install -U scikit-learn`)
- [numpy](https://numpy.org/) (`pip install numpy`)
- [imblearn](https://imbalanced-learn.readthedocs.io/en/stable/index.html) (`pip install -U imbalanced-learn`)
- [graphviz](https://graphviz.readthedocs.io/en/stable/index.html) (`pip install graphviz`)
- [matplotlib](https://matplotlib.org/) (`pip install matplotlib`)
- [lxml](https://lxml.de/) (`pip install lxml`)

To run:

- Edit `config.json`
- Navigate to appropirate directory, and execute `./clean_script.sh config.json` in command line

---

The behavior tree XML file(s) that are generated from the pipeline follow the XML format for behavior trees presented in [BehaviorTree.CPP](https://www.behaviortree.dev/) and [Groot](https://github.com/BehaviorTree/Groot).

