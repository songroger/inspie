- Intro
:::::::::

Inspie is an ever-expanding set of instagram services to help you meet your application challenges. 
It’s the freedom to manage instagram api on an easy way.

- Installation
:::::::::

1. Clone

.. code-block:: bash

    git clone git@github.com:songroger/inspie.git
    cd inspie
    python setup.py install

2. pip

::

    pip install git+https://github.com/songroger/inspie.git@master

- Usage
:::::::::

.. code-block:: python

    from inspie import InspieAPI

    i = InspieAPI("user", "pwd")
    photo_path = 'img_path'
    caption = "#tag caption!"
    i.upload_photo(photo_path, caption=caption)

see more in examples
