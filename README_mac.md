# Macvim Installation Instructions

(Instructions provided by [Nathan Farrar](https://github.com/nfarrar) - Thanks!)

On OSX it's common for users to install python using homebrew and set it as the
default python interpreter in their shellrc files. Then, if you install
vgeeknote, the libs & geeknote run using that python, not the system python.

When installing macvim, it will use the system's python interpreter by default
rather than the homebrew installed python. If you attempt to run a python
script that that requires dependencies that were installed to the homebrew
python rather than the system python, you just get nasty error messages.

To see if this is the issue, you can run:

    vim --version

And if you see:

    -I/System/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7

Then the problem is the one described above. The fix is to uninstall macvim,
then reinstall with the following flags:

    brew install macvim --with-lua --override-system-vim

And now vim --version should show:

    -I/usr/local/Cellar/python/2.7.8_2/Frameworks/Python.framework/Versions/2.7/include/python2.7

