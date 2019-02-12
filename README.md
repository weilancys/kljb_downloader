# kljb_downloader
A web crawler/downloader in python for one of my personal favorite radio programs "可乐加冰".

The downloader crawls https://www.ysts8.com for audio sources of all 11 seasons of the program and utilizes selenium to automate the info extraction from the website. It also has thread support. As a result, when running the downloader, multiple browser windows would pop up.

After downloading, a "download_report.txt" would be generated in current folder.

Please note that you need selenium webdrivers to be installed in your current python env in order for the downloader to work. The downloader uses webdriver for Chrome, therefore Chrome should be installed as well.
https://github.com/SeleniumHQ/selenium/tree/master/py#drivers

You are advised to use the downloader in a virtual environment created with the requirements.txt file.

Please refer to kljb_threaded_downloader.py --help for usage information.
