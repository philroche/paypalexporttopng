paypalexporttopng
=================

Paypal export payments sent to PNG files

I needed to print each of my paypal invoices but there's currently no way to do this easily.

The runexport.py script uses Ghost.py to scrape the paypal website and takes screenshots of your invoices.

The print_files.sh file will trim the whitespace from the PNGs and send to your default printer.

copy sample_settings.py to settings.py and update with your details. You might also want to update the filter dates in runexport.py.

At the moment it searches from 01/01/2013 to 15/08/2013.

Dependencies are Ghost.py and PySide and if you use print_files.sh you'll need imagemagick.

If you've have many transactions I recommend `sudo ulimit -SHn 65535` to temporarily increase the number of open files allowed.