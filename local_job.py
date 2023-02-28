from colab_share import *


lien_split_ipynb=make_dir_file_ipynb(except_bs64)
make_dir_file(lien_split_ipynb)
for i in lien_split_ipynb:
    try:
        # print(os.getcwd())
        # print('----------')
        os.chdir(os.getenv('file_path'))
        os.chdir(i['path'])
        print(os.getcwd())
        print('1----------')
        print(i['path'])
        file1 = open(i['ipynb'],"r")
        print("Output of Readlines after appending")
        FileContent=file1.read()
        file1.close()
        json_object = json.loads(FileContent)
        remove_colab(json_object)
        json_object['cells'].insert(0,add_link_colab(i['url']))
        # print(json_object['cells'][:2])
        file1 = open(i['ipynb'],"w")#write mode
        file1.write(json.dumps(json_object))
        file1.close()
        # print('----------')
    except :
        print('warning', i)
        pass

