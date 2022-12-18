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
    be necessary for the trophy scanning functionality (unless the paywall is
    up...)
  - If you do enter your credentials, be aware that when the utilities scan a
    thread for the first time, they will mark it as read for your account. You
    can avoid this by manually putting a page to start from for a given thread
    into your `config.ini` file like so:  
    [3991238]  
    page = 336  
    last_post = 0
  - If you are logged in, the utilities will attempt to set your last read
    post to where it was prior to running them. They will not be able to do
    this if for some reason your last read post on the forums is before the
    page set as the first page in the config file (for instance, if your last
    read post is on page 50 and the utilities start reading from page 60, they
    will mark the whole thread read because they will not know where to reset)

---

## Currently working utilities:

### IZGC Trophy Scanner

To run, call `python read_izgc_trophies.py` from the project root. This tool
prints a list of imps and trophies earned since the previous execution. It also
saves a record of new trophies earned to the local file
`trophy_timestamps.json`

The first time you run this utility, it will add the current end of the thread
to the `config.ini` file and not find any new trophies (unless you manually set
a thread start point as detailed above).

You may run this command against all pages in the thread with
`python read_izgc_trophies.py --all-pages`. This will find new trophies even if
it is the first execution of the script.

You may also run this command starting at a set page with
`python read_izgc_trophies.py --start-page {page number}`.