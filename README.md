Wolf or Not - A web service for labeling tons of images
=======================================================

This is the repository for the *Wolf or Not* project. This project is developed by
the department of sustainable communication networks, University of Bremen,
Germany.

- [comnets-bremen.de](https://comnets-bremen.de/)
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

The dependencies are managed using [uv]{https://docs.astral.sh/uv}.
Details can be found in the [pyproject.toml](pyproject.toml).

You can install the dependencies using `uv sync`.

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

Docker?
=======

This repository contains everything to run a docker container:

- Rename the `example-.env` to `.env` and adapt it to your needs
- `docker compose build`
- `docker compose up`

Should be sufficient to bring the container up. For real world applications,
you should consider running this container behind a reverse proxy like [Caddy](https://caddyserver.com/docs/quick-starts/reverse-proxy) or [traefik](https://traefik.io/traefik).


Security
========

Before using this code on a public server, you should make yourself familiar
with some potential security considerations:

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
documentation](https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/modwsgi/)
explains how to set up django using `mod_wsgi` on an apache webserver.

You should also find everything to deploy this tool using docker compose.

**Security notice** Please make sure you set your own key as mentioned in the
security sections of this document.

Publications
============

- *Jens Dede and Anna Förster*: **Animals in the Wild: Using Crowdsourcing to enhance the labelling of Camera Trap Images**, 2nd DISCOLI Workshop on DIStributed COLlective Intelligence (DISCOLI 2023), Pafos, Cyprus, June 19-21, 2023

License
=======

Jens Dede, Sustainable Communication Networks, University of Bremen, jd@comnets.uni-bremen.de, 2026

This code is licensed under the GPLv3. You can find it [here](LICENSE).

Acknowledgements
================

* ..
