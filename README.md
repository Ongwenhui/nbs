# Dependencies
Matlab 2021b or newer<br>
Python 3.10 installed on base (3.11 not supported by matlab)<br>
awsiotsdk and awscrt packages installed on base

# nbsiot.m
Under <code>pyenv('Version', '/Library/Frameworks/Python.framework/Versions/3.10/bin/python3');</code>, replace the filepath with the absolute filepath to the Python executable installed on your computer.<br>
Replace the values in <code>values</code> with the participant ID and a boolean value to turn the playback on and off respectively.<br>
Under <code>pyrunfile()</code>, replace the first argument with the filepath to <code>sendtoiot.py</code>. For simplicity's sake, I recommend putting the python script in the same directory so that nothing needs to be edited.

# sendtoiot.py
Replace <code>PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, PATH_TO_AMAZON_ROOT_CA_1</code> with the filepaths to the files included in the archive.. For simplicity's sake, I recommend putting everything in the same directory so that nothing needs to be edited.<br>