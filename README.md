# RE:BT-Espresso enhanced by GFACTOR algorithm. 

This git repository is a fork from RE:BT-Espresso. This README will guide you to generate the results presented in the paper _Learning Behavior Trees from Planning Experts Using Data Mining and Logic Factorization_ submitted at AAAI23. This repository is the so called SETUPII in the paper


## Install
1. Install python3.8
2. (Optional) create a  python3 [virtual environment](https://docs.python.org/3/library/venv.html) and activate it
3. Install packages in python
  ```pip install joblib py_trees pandas wheel sklearn imblearn graphviz matplotlib pydot networkx sympy pyeda```
  - If you have troubles installing pyeda in windows, we provide the wheel file. Run the command
  ```pip install pyeda-0.28.0-cp38-cp38-win_amd64.whl```
  - There is a bug is Pyeda library that also need to be fixed. See [#17](https://github.com/interaction-lab/BTFromSARDemostration/issues/17) for fix.
  - If you get an UnicodeEncodeError navigate to your site packages (typically here ~/.local/lib/python3.8/site-packages, open file ```pydot.py``` and change the encoding in lines 1825 to ```'utf-8'```

## Reproducing the results for the Tree Structure

Open a terminal in the top level directory. Note that these steps are sequential and it is highly reccomanded to run them in order. We provide in the ```output``` folder the files (created during the steps) that are needed to run the following steps. Copy paste the file in the right directoty and run the next step

1. Repeat 11 times (number of simulations)
    1. To create the simulation data copy paste in the terminal:
      ```python run_experiments.py -k -g```
    _Expected output_: in the folder sim_data 99 folders (exprx)

    2. To collect the tre structure analysis copy paste in the terminal:
      ```python tree_structure_simulation.py```

        _Expected output_: ```graphAnalysis.csv``` in the \GraphAnalysis directory
    3. (Only the first time) In the file ``tree_structure_simulation.py`` comment lines 109,113 and remove the comment from line 110
2. To compute the results presented in the paper copy paste in the terminal:
      ```python tree_structure.py ```
    Figures 5 and 6 will be printed one after the other



