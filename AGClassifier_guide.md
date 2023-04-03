# AGClassifier setup

## Installation of Conda
We will use the package manager Conda to make sure that all the dependencies are installed correctly. If you already have
Conda installed, you can skip this step.

Got to [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html) and download the
installer that corresponds to your operating system (Windows/macOS/Linux). Select the one that says **Python 3.10**.

Once the installer is downloaded, run it and complete the installation steps.

In order to confirm the installation was successful, open the Terminal ('Command Prompt' if on Windows 10) and type:
`conda -V`.

## Installation of Git
We will use Git to download the AGClassifier repository. If you already have Git installed, you can skip this step.

Got to [https://git-scm.com/downloads](https://git-scm.com/downloads) and download the installer that corresponds to your
operating system (Windows/macOS/Linux).

Once the installer is downloaded, run it and complete the installation steps. On Windows, you can follow [this guide](https://www.geeksforgeeks.org/how-to-install-git-on-windows-command-line/) if
you'd like. This will install Git Bash, which is a terminal that is very similar to the one on Linux/macOS.

Ensure that Git is installed by opening the Terminal/Git Bash and typing:
`git --version`.

## Downloading AGClassifier

AGClassifier can be downloaded by cloning the GitHub repository. Open the Terminal/Git Bash and
navigate to the folder where you want to download AGClassifier. Then type:
```
git clone https://github.com/LudvigEk/AGClassifier.git
```

This will download the repository to the current folder. You can now navigate to the folder by typing:
```
cd AGClassifier
```

Once you are inside the folder, you can install the dependencies by typing:
```
conda env create -f agclassifier.yaml
```

This will create a new conda environment called `agclassifier` and install all the dependencies. You can now activate the
environment by typing:

```
conda activate agclassifier
```

Now we can finally run AGClassifier!

## Running AGClassifier

To run AGClassifier, simply type:
```
python AGClassifier.py
```
