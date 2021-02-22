# Web Chat with Suggestions

### IATA 2020/21  Chris Werner
A chat application with suggestions running on Python, Flask and AIML

### Setup Instructions
After checking out from Github or unzipping, perform the following steps:

#### 1: Environment
You can use your own python enviroment if you want, but I recommend
you set one up with venv _inside_ the project directory.

Either way you need Python 3.6+ installed on your system already

    cd iatatp2chat
    python -m venv venv
   
Now, and _whenever you're working from the command line_ in a new
terminal, you will need to engage the local environment. Do this now:

    source venv/bin/activate
 
The startup script expects that you have a this venv directory locally, so
you will have to use flask directly if you don't do this.

The next step you can do anytime the requirements are updated and checked in.
Or any time you want to be sure: it won't change anything if you're already up to date.

    python -m pip install -r requirements.txt 
 
### Running the App
Make sure your environment is setup (above) then in a terminal in the project
 directory type:

    source start_webchat.sh
    
If you don't have venv set up, use this instead:
    
    flask run

If you get some error about flask not being found, then you probably didnt set up
or activate your environment or didn't install the requirements. 
Try `which python` to make sure the python executable is in the project venv, 
and go to step 1 above.

When it runs you should see a message telling flask is running on http://127.0.0.1:5000/
Point your browser there and have fun.
    
### Updating the App after Git Pull
    python -m pip install -r requirements.txt 

