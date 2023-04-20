# AGClassifier

Welcome to the AliGater Classifier. This is a tool for quality control (QC) of images produced by 
[AliGater](https://github.com/LudvigEk/aligater).

## Setup
You can download AGClassifier by cloning this repository. We recommend using a virtual environment to install the
dependencies. The following commands will create a conda virtual environment with the required dependencies and activate
it:

```bash
conda create --file agclassifier.yaml -y
conda activate agclassifier
```

## Usage
AGClassifier can be started by running the AGClassifier.py script:
    
```bash
python AGClassifier.py
```

The GUI will then open and ask the user to provide path to the folder containing the images to be classified.
The program will create an 'output' folder in the same directory as the images. This is where the output .yaml file
will be created.
Finally, AGClassifier will also attempt to automatically find the .pickle file that contains the layout particular to the gate.
If a single .pickle file exists in the parent directory of the images folder, that file will be used automatically.
If no file is found or there are several, the user will be asked to select a file.

Once the paths are defined, the fun begins!
The main window will open next. This is where the images are displayed. The user can then use the buttons to either
approve the image or select the necessary corrections.

Select the big START button to commence the QC process.

Good luck!

## Output
The corrections selected by the user will all be stored in a single `corrections.yaml` file. This file will be saved
in the folder specified by the user at startup.
