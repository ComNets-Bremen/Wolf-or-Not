Tools for SimpleLabel
=====================

This directory contains the tools and scripts for data preparation.


Re-encode video using ffmpeg
----------------------------

Videos from surveillance cameras are often stored as a `.mkv` file. Those can
not be read by the scripts. The following command will convert the `.mkv` file
to an `.mp4` file:

`ffmpeg -i input_file.mkv -codec copy output_file.mp4`




Required libraries (venv)
=========================

The following libraries are required. It is recommended to install those inside
a virtual environment (venv) using pip:

* imutils
* numpy
* opencv-python
