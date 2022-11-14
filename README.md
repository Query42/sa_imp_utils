# sa_imp_utils
A set of thread-reading and -parsing utilities for use with the SA Forums and 
Imp Zone. 

## Setup: 
- [Install python locally](https://wiki.python.org/moin/BeginnersGuide/Download)
- In a local terminal, run `pip3 install -r requirements.txt`.
- (Optional) enter your SA username/password into your local `config.ini`. This 
is only visible to your local machine and the SA forums, never sent anywhere 
else. 
    - If you opt not to enter your credentials, the forums will be viewed as an 
    unregistered user, enabling all the word filters. I added functionality to
    filter out posts by Adbot, so those shouldn't affect the results. Shouldn't 
    be necessary for the trophy scanning functionality.
    - If you do enter your credentials, be aware that when the utilities scan a 
    thread, they will generally mark the entire thing as read for your account. 
    I might work in some way to avoid that someday but for now that's the way it 
    is.

---

## Currently working utilities:

### IZGC Trophy Scanner

To run, call `python read_izgc_trophies.py` from the project root. This tool
prints a list of imps and trophies earned since the previous execution. It also
saves a record of new trophies earned to the local file
`trophy_timestamps.json`

The first time you run this utility, it will add the current end of the thread
to the `config.ini` file and not find any new trophies.

You may run this command against all pages in the thread with
`python read_izgc_trophies.py --all-pages`. This will find new trophies even if
it is the first execution of the script.
