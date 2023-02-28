import os, fnmatch
import os
import subprocess
import sys
import time

import requests

from dotenv import load_dotenv

from github import Github
from tqdm import tqdm
from googletrans import Translator
import re
import json
from nbconvert import HTMLExporter
from nbformat.v4 import to_notebook

import csv

def all_job(repo, path):
    # global except_bs64
    # global except_bs64_path
    f = open(repo.name + '.csv', 'a', newline='')
    writer = csv.writer(f)
    for file in repo.get_contents(path):
        try:
            if file.type == "dir":
                all_job(repo, file.path)
            elif file.path.endswith(".ipynb"):

                print("1- ", file.path)
                html_test = file.html_url.replace('https://', "https://colab.research.google.com/")
                html_test = html_test.replace('github.com', "github")
                file_content = repo.get_contents(file.path).decoded_content.decode(encoding='UTF-8', errors='strict')
                json_object = json.loads(file_content)

                remove_colab(json_object, trans=True)

                json_object['cells'].insert(0, add_link_colab(html_test))
                writer.writerow([file.path, "Done"])
                # pour update le repo github documente cette ligne
                repo.update_file(file.path, "auto colab", json.dumps(json_object, indent=4), file.sha)
                html_job(repo, file, file_content)



        # break
        except Exception as e:
            print(e)
            print("except 2", file.path)
            if file.path.endswith(".ipynb"):
                try:

                    file_content = github_file_to_bytes(file.download_url)
                except Exception as e:
                    print(e)
                # print(file_content)
                json_object = json.loads(file_content)

                # print(json_object)

                remove_colab(json_object, trans=True)

                json_object['cells'].insert(0, add_link_colab(html_test))

                # pour update le repo github documente cette ligne
                # repo.update_file(file.path, "auto colab", json.dumps(json_object, indent=4), file.sha)
                html_job_local(repo, file, file_content)

                writer.writerow([file.path, "Done with 2nd"])
            # except_bs64.append(html_test)
            # except_bs64_path.append(file.path)
    f.close()

def findEdit(directory, filePattern):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in fnmatch.filter(files, filePattern):
            filepath = os.path.join(path, filename)
            with open(filepath) as f:
                s = f.read()
            json_object = json.loads(s)
            remove_colab(json_object, trans=True)
            # s = s.replace(find, replace)
            with open(filepath, "w") as f:
                f.write(s)


def translate_text(liste):
    translator = Translator()
    return [translator.translate(i, dest='fr').text + "\n" for i in liste]


def remove_colab(js_file, trans=False):
    # translator = Translator()
    cpt = 0
    if "metadata" in js_file:
        if 'colab' in js_file['metadata']:
            del js_file['metadata']['colab']
        elif "colab_type" in js_file['cells'][0]['metadata']:
            js_file['cells'] = js_file['cells'][1:]
    for cell in tqdm(js_file['cells'], ascii=True, desc='remove_colab'):
        if cell['cell_type'] == "markdown" and trans:
            cell['source'] = translate_text(cell['source'])
            # print(cell.source)
def html_job_local(repo, file, file_content):
    # Get the repository you want to create the folder in
    # g = Github(os.getenv('TOKEN'))
    # repo_html = repo.get_contents("notebook")
    file_name = "notebook/"+file.path.replace('ipynb', 'html')
    exporter = HTMLExporter()
    file_content = to_notebook(json.loads(file_content))
    body, resources = exporter.from_notebook_node(file_content)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    print("Hada filname",file_name)
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(body)
        f.close()



def html_job(repo, file, file_content):
    # Get the repository you want to create the folder in
    # g = Github(os.getenv('TOKEN'))
    # repo_html = repo.get_contents("notebook")
    file_name = file.path.replace('ipynb', 'html')
    exporter = HTMLExporter()
    file_content = to_notebook(json.loads(file_content))
    body, resources = exporter.from_notebook_node(file_content)
    try:
        # file = repo_html.get_contents(file_name)
        print('update', file_name)
        repo.update_file("notebook/" + file_name, "update file", body, file.sha)
    except:
        print('create', file_name)
        repo.create_file("notebook/" + file_name, "create file", body)


def list_files(repo, path):
    for file in repo.get_contents(path):
        if file.type == "dir":
            list_files(repo, file.path)
        else:
            print(file.path, file.html_url)


def add_link_colab(html_link):
    colab = {
        "cell_type": "markdown",
        "metadata": {
            "id": "view-in-github",
            "colab_type": "text"
        },
        "source": [
            "<a href=\"" + html_link + "\" target=\"_blank\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
        ]
    }
    return colab


def add_link_colab_local(html_link):
    colab = {
        "cell_type": "markdown",
        "metadata": {
            "id": "view-in-github",
            "colab_type": "text"
        },
        "source": [
            "<a href=\"https://colab.research.google.com/github/" + html_link + "\" target=\"_blank\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
        ]
    }
    return colab

def github_file_to_bytes(path):
    time.sleep(1)
    print("Downloading : ", path)
    return subprocess.check_output(['curl', '-L', path])
    # print(content_encoded)
    # content = base64.b64decode(content_encoded)
    #
    # return content



findEdit("C:\\KPLR\\github_process\\repos", "*.ipynb")