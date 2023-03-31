# AGClassifier

Welcome to the AliGater Classifier. This is a tool for quality control (QC) of images produced by 
[AliGater](https://github.com/LudvigEk/aligater).

## Setup
You can download AGClassifier by cloning this repository. We recommend using a virtual environment to install the
dependencies. The following commands will create a virtual environment with the required dependencies and activate it:

```bash
conda create --file agclassifier.yaml -y
conda activate agclassifier
```

## Usage
AGClassifier can be started by running the AGClassifier.py script:
    
```bash
python AGClassifier.py
```

The GUI will then open and ask the user to provide three paths:
1. The path to the folder containing the images to be classified.
2. The path to the folder where the classified images should be saved.
3. The path where the layout 'pickle' file is located. This file is specific to the gate that is being evaluated.

Once these three have been provided, the fun begins!
The main window will open next. This is where the images are displayed. The user can then use the buttons to either
approve the image or select the necessary corrections.

Select the big START button to commence the QC process.

Good luck!

## Output
The corrections selected by the user will all be stored in a single `corrections.yaml` file. This file will be saved
in the folder specified by the user at startup.