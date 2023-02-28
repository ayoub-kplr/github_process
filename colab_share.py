import base64
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

os.environ['TOKEN'] = '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'


# except_bs64=[]
# except_bs64_path=[]

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


def hello():
    print("hello")


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


def make_dir_file_git(lien_except):
    return [{"url": i, "path": './' + "".join(i.replace('https://github.com/', '').split('blob/main/'))} for i in
            lien_except]


def make_file(lien_except):
    return [i.update({"file": '/'.join(i['path'].split('/')[:-1]), 'ipynb': './' + i['path'].split('/')[-1]}) for i in
            lien_except]


def update_github(repo, path, ipynb):
    for file in tqdm(repo.get_contents(path), ascii=True, desc=f'Epoch {path}'):
        try:
            if file.path.endswith(ipynb):
                print("except 2", file.path)
                html_test = file.html_url.replace('https://', "https://colab.research.google.com/")
                html_test = html_test.replace('github.com', "github")
                file_content = repo.get_contents(file.path).decoded_content.decode(encoding='UTF-8', errors='strict')
                json_object = json.loads(file_content)

                remove_colab(json_object, trans=True)

                json_object['cells'].insert(0, add_link_colab(html_test))

                # pour update le repo github documente cette ligne
                repo.update_file(file.path, "one file", json.dumps(json_object, indent=4), file.sha)
                # break
                print(ipynb, " done")
                # break
            else:
                print("erreur")
        except:
            print('kooo')
            pass


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


def github_file_to_bytes(path):
    time.sleep(1)
    print("Downloading : ", path)
    return subprocess.check_output(['curl', '-L', path])
    # print(content_encoded)
    # content = base64.b64decode(content_encoded)
    #
    # return content


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


def main(repo='', path='', ipynb=''):
    """il faut modifier le nom_user si tu veux changer de user et
    specifier le repo_name si tu veux specifier un repo en particulier

    Args:
        repo (str, optional): _description_. Defaults to ''.
        path (str, optional): _description_. Defaults to ''.
        ipynb (str, optional): _description_. Defaults to ''.
    """

    load_dotenv()
    nom_user = 'kplr-training'
    repo_name = "ayoub-kplr/Statistics-With-Python"  # "ayoub-kplr/Data-Statistics-Python" AI-Architecture-Cloud

    g = Github(os.getenv('TOKEN'))
    user = g.get_user()
    if len(sys.argv) > 1:
        repo = g.get_repo(sys.argv[1])
        update_github(repo, sys.argv[2], sys.argv[3])
    else:
        # repos = [i.full_name for i in g.get_user().get_repos() if i.full_name.startswith(nom_user)]#kplr-training
        # for repo in repos:
        repo = g.get_repo(repo_name)
        all_job(repo, "")
        # Data-Preparation/1-Débuter-avec-Pandas/Exercices-et-Solutions/1_Exercices.ipynb


if __name__ == "__main__":
    # if len(sys.argv) == 1:
    main(sys.argv)
    # else :
    #     param = sys.argv[1]
    #     repo = sys.argv[2]
    #     path = sys.argv[3]
    #     ipynb = sys.argv[4]
    #     main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
