#!/usr/bin/env python3
"""
A python module to aid and automate CTF web challenges.

Authors: John (@Magicks52), David (@DavidTimothyNam), Arya (@AryaGill)
Tested: Python 3.10.4 on Kali Linux and Python 3.9.5 on Ubuntu
"""

import base64
import bs4
import codecs
import os
import re
import requests


def extract_comments(source_code: str) -> list:
    """Accepts source code of a website as a string and parses comments."""

    all_comments = []
    # set up html to be parsed, find html comments
    soup = bs4.BeautifulSoup(source_code, "html.parser")
    # get html comments
    all_comments += soup.findAll(
        text=lambda text: isinstance(text, bs4.Comment)
    )
    # get php, css, js, multi-line comments /* */
    all_comments += re.findall(r"/\*.+?\*/", source_code)
    # get single-line javascript comments
    all_comments += re.findall(r"//.+?$", source_code)
    return all_comments


def extract_comments_from_file(file_path: str) -> list:
    """Return a list of all comments in the file at the specified path."""

    with open(file_path, "rb") as f:
        comments = extract_comments(f.read().decode("utf-8", "ignore"))
    return comments


def get_files_in_dir(path_to_directory: str) -> list:
    """Accepts a path to a directory and returns a list of filepaths of every
    file in the directory."""

    list_of_files = []
    for root, dirs, files in os.walk(path_to_directory):
        for file in files:
            # append relative filepaths
            list_of_files.append(os.path.join(root, file))
    return list_of_files


def parse_file_for_flag(crib: str, file_path: str) -> list:
    """Parses file for crib. Assumes file has valid utf-8 bytes."""

    with open(file_path, 'rb'):
        flags = parse_for_flag(crib, file_path..read().decode("utf-8", "ignore"))
    return flags


def parse_for_flag(crib: str, text: str) -> list:
    """Accepts a CTF flag crib and uses it to find plaintext, rot13 encoded,
    and base64 encoded flags in given text."""

    crib = crib.strip("{")
    regex_string = ""
    for character in crib:
        regex_string += character
        regex_string += ".{0,2}"
    # regex string will match flag with any padding of less than 2 characters
    # in between each flag character (above)
    regex_string += r"\{.*?\}"
    # Pattern of plaintext, rot13, and base64
    plaintext_pattern = re.compile(regex_string)
    rot13_pattern = re.compile(codecs.encode(regex_string, "rot-13"))
    base64_first_three = base64.b64encode(bytes(crib, "utf-8")).decode()
    base64_pattern = re.compile(
        f"{base64_first_three[0:3]}[+\\\\A-Za-z0-9]+[=]{{0,2}}\s"
    )
    # Get list of possible flags
    possible_flags = []
    plaintext_flags = plaintext_pattern.findall(text)
    rot13_flags = rot13_pattern.findall(text)
    base64_flags = base64_pattern.findall(text)
    # append decoded flag with description of encoding to possible flags
    if plaintext_flags:
        possible_flags += [
            "plaintext flag: {}".format(x) for x in plaintext_flags
        ]
    if rot13_flags:
        possible_flags += [
            "rot13 flag: {}".format(codecs.decode(x, "rot-13"))
            for x in rot13_flags
        ]
    if base64_flags:
        possible_flags += [
            "base64 flag: {}".format(
                base64.b64decode(bytes(x, "utf-8")).decode()
            )
            for x in base64_flags
        ]
    # print possible flags and exit
    if possible_flags:
        for flag in possible_flags:
            print(flag)
    return possible_flags


class Client:
    """A class to connect to a remote server and download files."""

    def __init__(self, url: str, directory: str) -> None:
        self.url = url
        self.directory = directory
        self.webwizard_dir = os.path.join(directory, "webwizard_output/")

    def check_robots(self) -> bool:
        """Makes a GET request to robots.txt and returns True if http response
        is 200, and False if anything else."""

        robots_link = self.url + "robots.txt"
        r = requests.get(robots_link)
        # if the page actualy exists
        return r.status_code == 200

    def crawl_robots(self) -> dict:
        """Accesses robots.txt and if the page exists, returns a dictionary
        with organized information."""

        robots_link = self.url + "robots.txt"
        r = requests.get(robots_link)
        # if the page actualy exists
        if r.status_code == 200:
            robots_info = {
                "comments": [],
                "user-agent": [],
                "disallow": [],
                "allow": [],
                "sitemap": [],
            }
            # organize the information in robots.txt
            robots = r.content.decode().split("\n")
            for line in robots:
                if "#" in line:
                    robots_info["comments"].append(line)
                else:
                    entry = line.split(" ")
                    # ignore empty entries
                    if len(entry) != 1:
                        if entry[0] == "User-agent:":
                            robots_info["user-agent"].append(entry[1])
                        elif entry[0] == "Disallow:":
                            robots_info["disallow"].append(entry[1])
                        elif entry[0] == "Allow:":
                            robots_info["allow"].append(entry[1])
                        elif entry[0] == "Sitemap:":
                            robots_info["sitemap"].append(entry[1])
        # if the page doesn't exist
        else:
            # return empty dict
            robots_info = {}
        return robots_info

    def extract_comments(self) -> list:
        """Returns a list of all comments from mirrored website."""

        # get list of filepaths for each file in the folder
        subfile_list = get_files_in_dir(self.webwizard_dir)
        # parse all subfiles for comments
        comments = []
        for subfile in subfile_list:
            comments += extract_comments_from_file(subfile)
        return comments

    def get_cookies(self) -> dict:
        """Gets any cookies sent from the server from that URL. Returns a
        dictionary of all cookies received."""

        session = requests.Session()
        response = session.get(self.url)
        return session.cookies.get_dict()

    def get_all_cookies(self) -> dict:
        pass

    def get_remote_files(self, link: str) -> list:
        """Parse file at the specified link for other remote files, return a
        list of URLs to remote files."""
        # TODO: mirror php files (ex.  <form role="form" action="login.php" method="post">)
        css_files = []
        image_files = []
        script_files = []
        all_files = []
        # make a GET request to the website url, append \n
        # so properly ends with a newline
        r = requests.get(link)
        # set up HTML to be parsed for source files
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        # find all '<link>' tags and use the path from the 'href'
        # attribute to find filepaths of css files
        for css_file in soup.find_all("link"):
            if css_file.attrs.get("href"):
                file_path = css_file.attrs.get("href")
                # if 'file_path' is not a full URL yet, append the
                # first part of the URL (the domain name)
                if "http" not in file_path:
                    file_path = link + file_path
                    # check to see if css file was already referenced
                    # elsewhere in the source code
                    if file_path not in css_files:
                        css_files.append(file_path)
        # find all '<img>' tags and use the path from the 'src'
        # attribute to find filepaths of image files
        for image in soup.find_all("img"):
            if image.attrs.get("src"):
                file_path = image.attrs.get("src")
                if "http" not in file_path:
                    file_path = link + file_path
                    if file_path not in image_files:
                        image_files.append(file_path)
        # find all '<script>' tags and use the path from the 'src'
        # attribute to find filepaths of javascript files
        for script in soup.find_all("script"):
            if script.attrs.get("src"):
                file_path = script.attrs.get("src")
                if "http" not in file_path:
                    file_path = link + file_path
                    if file_path not in script_files:
                        script_files.append(file_path)
        # make a list of all the URLs to all the files to download
        all_files = css_files + image_files + script_files
        return all_files

    def mirror(self, link: str) -> None:
        # TODO: ask David why this function takes a link instead of using self.url
        # TODO: consider whether to add a directory attribute to __init__
        """Accepts URL and mirrors website in output directory named
        'webwizard_output/'."""
        # get a list of all remote files to mirror
        all_files = self.get_remote_files(link)
        # make 'webwizard_output/' directory
        if not os.path.isdir(self.webwizard_dir):
            os.mkdir(self.webwizard_dir)
        # function to prepend 'webwizard_output_dir'
        prepend_directory = lambda x: os.path.join(self.webwizard_dir, x)
        # make directories that mirror website structure and download
        # all files
        for url in all_files:
            path = url[len(link) :].split("/")
            if len(path) > 1:
                file_name = path[-1]
                folders = path[:-1]
                local_path = prepend_directory("/".join(folders))
                # make directories if they don't exist
                if not os.path.isdir(local_path):
                    os.makedirs(local_path)
                # download all files
                i = requests.get(url)
                with open(f"{local_path}/{file_name}", "wb") as source_file:
                    source_file.write(i.content)
            else:
                # if the file being requested is at the root of the website,
                # write it directly to 'webwizard_output/'
                i = requests.get(url)
                with open(prepend_directory(path[0]), "wb") as source_file:
                    source_file.write(i.content)
        # download 'index.html'
        with open(prepend_directory("index.html"), "wb") as index_file:
            # make a GET request to the website url, append \n
            # so properly ends with a newline
            r = requests.get(link)
            source_code = r.content + b"\n"
            index_file.write(source_code)
        return None

    def parse_website_for_flag(self, crib: str) -> list:
        """Parse mirrored website for specified crib and returns list of
        possible flags."""
        # get list of filepaths for each file in the folder
        subfile_list = get_files_in_dir(self.webwizard_dir)
        # parse all subfiles for flag
        flags = []
        for subfile in subfile_list:
            with open(subfile, "rb") as subf:
                # remove bad utf-8 characters from image files
                text = subf.read().decode("utf-8", "ignore")
                flags += parse_for_flag(crib, text)
        return flags