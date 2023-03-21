Wolf or Not - A web service for labeling tons of images
=======================================================

This is the repository for the SimpleLabel project. This project is developed by
the department of sustainable communication networks, University of Bremen,
Germany.

- [comnets.uni-bremen.de](https://comnets.uni-bremen.de/)
- [ComNets @Twitter](https://twitter.com/ComNetsBremen)
- [ComNets @Youtube](https://www.youtube.com/comnetsbremen)


What is this App doing?
=======================

For nowadays computer vision, training data is required. Depending on the
scenario, the labeling of the data requires a lot of time. SimpleLabel
automatically detects changes in time-series images and shows a simple dialog
to the user: What is visible on the image.

Using this kind of citizen science leads to a suitable number of labeled
images.


Security
========

Before using this code on a public server, you should make yourself familiar
with some potential security considerations:

- The `settings.py` contains a secret key. You should not use the one in the
  repository. For each installation, a separate key should be used. You can
  keep it local by adding it to the `settings_local.py`.
- The code is not checked for security. Maybe you should walk through it
  and check if running it on your server is safe.
- Maybe running the system on an isolated server is a good idea?
- Anyhow, we will not take any responsibility for the code and the project.

Downloading images
==================

The original images can be downloaded using a separate URL by either
authenticated users (in the browser) or via a call with an authentication token:

`curl https://<server-address>/simplelabel/original-img/<image_UUID>/ -H 'Authorization: Token aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'`

The token has to be configured using the API model.

Publications
============

- Nothing yet

License
=======

Jens Dede, Sustainable Communication Networks, University of Bremen, jd@comnets.uni-bremen.de, 2022

This code is licensed under the GPLv3. You can find it [here](LICENSE).

Acknowledgements
================

* ...
