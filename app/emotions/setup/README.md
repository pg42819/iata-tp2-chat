# Training the Emotions Model 

To setup for the emotional anaylsis in webchat, we must first
train and store a Bayesian model.
At runtime, this is not needed, as the trained, and stored 
(pickled) model is part of the GitHub repository.
It is needed to start from scratch, however, and was part of
this project, so the steps are laid out here.

### 1. Downloads
Run the nltk_downloader.py python script in this directory.
This will download and unzip files in your user home directory
under nltk_data (which it will create on the fly)

### 2. Training
Run the nltk_emotion_traner.py script in this directory.
This will train a Bayesian classifier on labeled twitter messages
and store the model in pickled form in the models directory.


### 3. Testing 

From the command line you can run the nltk_emotions script:
Example:

    python nltk_emotions.py Wonderful day

Output:

    Analyzing: "Wonderful day"
    Emotion: "Positive"

 
    