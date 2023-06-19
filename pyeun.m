pe = pyenv;
if pe.Status == "Loaded" && pe.Version ~= "3.10"
    disp('To change the Python version, restart MATLAB, then call pyenv(Version="3.10").')
else
    pyenv('Version', '/Library/Frameworks/Python.framework/Versions/3.10/bin/python3');
end
pyenv("ExecutionMode","OutOfProcess")
values = [00001 true];
pyrunfile("helloworld.py", values=values);