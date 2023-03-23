Wolf or Not - A web service for labeling tons of images
=======================================================

This is the repository for the *Wolf or Not* project. This project is developed by
the department of sustainable communication networks, University of Bremen,
Germany.

- [comnets.uni-bremen.de](https://comnets.uni-bremen.de/)
- [ComNets @Twitter](https://twitter.com/ComNetsBremen)
- [ComNets @Youtube](https://www.youtube.com/comnetsbremen)


What is this App doing?
=======================

For nowadays computer vision, training data is required. Depending on the
scenario, the labeling of the data requires a lot of time. *Wolf or Not*
automatically detects changes in time-series images and shows a simple dialog
to the user: What is visible on the image.

Using this kind of citizen science leads to a suitable number of labeled
images.

Requirements
============

The main requirements are

* Django
* Pillow
* numpy

Details from our `pip3 freeze` can be found in
[requirements.txt](requirements.txt)

Or use the requirements.txt for your venv / pip installation:
`pip3 install -r requirements.txt`

How to set it up?
=================

The installation is quite easy:

1) Clone this repository:
`git clone git@github.com:ComNets-Bremen/Wolf-or-Not.git`

2) Create basic database structure:
`python3 manage.py migrate`

3) Create a superuser:
`python3 manage.py createsuperuser`

4) Start testserver:
`python3 manage.py runserver`

5) System should now be up and running on your [localhost on port 8000](http://127.0.0.1:8000)

6) Go to the backend: Admin -> Login using the credentials set before

7) The following models are available:

  * Api keys: The keys for the remote tools like the automatic downloader
  * Classes: The classes the user can click on
  * Datasets: Names to group the uploaded images. At least one should be
configured here
  * Images: The images. Upload should be done via the admin -> upload images
menu on the main page. This item is only available if you are logged in and not
from the backend
  * Polls: The votes the users did
  * Properties: The additional properties for the system can be configured here.



Security
========

Before using this code on a public server, you should make yourself familiar
with some potential security considerations:

- The `settings.py` contains a secret key. You should not use the one in the
  repository. For each installation, a separate key should be used. You can
  keep it local by adding it to the `settings_local.py`. A key can be generated
  using the following command:
  `$ python -c 'from django.core.management.utils import get_random_secret_key;
  print(get_random_secret_key())'`
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

Running on a real webserver
===========================

The testserver should never be use in production environments. The [Django
documnetation](https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/modwsgi/)
explains how to set up django using `mod_wsgi` on an apache webserver.

**Security notice** Please make sure you set your own key as mentioned in the
security sections of this document.

Publications
============

- Nothing yet

License
=======

Jens Dede, Sustainable Communication Networks, University of Bremen, jd@comnets.uni-bremen.de, 2023

This code is licensed under the GPLv3. You can find it [here](LICENSE).

Acknowledgements
================

* ..
