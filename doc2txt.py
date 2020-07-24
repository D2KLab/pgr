import os
import sys
import re
import pdb

try:
    import textract
except ImportError:
    print('There is some error occurring when importing the textract library. Please, see the documentation in order to check your installation.')
    sys.exit(1)

white_list_extension_files = ['.csv', '.doc', '.docx', '.eml', '.epub', '.gif', '.htm', '.html', '.jpeg', '.jpg', '.json', '.log', '.mp3', '.msg', '.odt', '.ogg', '.pdf', '.png', '.pptx', '.ps', '.psv', '.rtf', '.tff', '.tif', '.tiff', '.tsv', '.txt', '.wav', '.xls', '.xlsx']

def doc2txt(argv):
    for arg in sys.argv[1:]:
        convert_to_txt(arg)

def convert_to_txt(input_arg):
    if os.path.isfile(input_arg):
        return do_conversion(input_arg)
    elif os.path.isdir(input_arg):
        for file in os.listdir(input_arg):
            return do_conversion(file)
    else:
        print('The file %s not exists.' % (input_arg))
        sys.exit(2)

def do_conversion(file):
    file_name, file_extension = os.path.splitext(file)

    if file_extension in white_list_extension_files:
        text_bytes = textract.process(file, encoding='utf-8', extension=file_extension)
        text = text_bytes.decode('utf-8')#.encode('utf-8')

        f = open(file_name + '.txt', 'w')
        
        data = purge_urls(text)
        f.write(data)
        f.close()
        return data
    else:
        print('This file extension is not supported. These are the ones supported: ')
        for ext in white_list_extension_files:
            print("%s\n" % (ext))
        sys.exit(2)

def text2str(data, delimiter='.'):
    #file = open(path, 'r')
    unparsed_info = data
    element_list = [] # Make an empty list

    for elements in unparsed_info.split(delimiter):
        e = elements.strip(delimiter)
        if e != '':
		    
            element_list.append(e.replace('\n','')) #Append to list
    
    return element_list

def normalization(text, delimiter='.'):
    '''
    Each line is a complete phrase
    '''
    
    #file_input = open(path, 'r', encoding=encoding)

    #relative_path = os.path.dirname(path)

    
    #file_name, file_extension = os.path.splitext(os.path.basename(path))
    
    unparsed_info = text

    #file_output = open(relative_path + '/' + file_name + "_normalized" + file_extension, 'w', encoding=encoding)
    #file_output = open('log_datas.txt', 'w')
    #print(unparsed_info)
    bc_text = ' '.join(unparsed_info.split('\n'))
    
    sentenceSplit = bc_text.split(".")
    
    datas = ''
    for s in sentenceSplit:
        #data = s.strip(s.strip() + ".\n")
        datas = datas + s.strip() + ".\n"
        

    #file_output.write(datas)
    
    return datas
    #os.remove(relative_path + '/' + file_name + '_purged.txt')
    #os.remove(relative_path + '/' + file_name + '.txt')
    #os.rename(relative_path + '/' + file_name + '_normalized.txt', file_name + '.txt')

def Find(string): 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url]

def purge_urls(text):
    #file_name, file_extension = os.path.splitext(os.path.basename(path))
    #relative_path = os.path.dirname(path)

    #file_input = open(path, 'r', encoding=encoding)

    #file_output = open(relative_path + '/' + file_name + '_purged.txt', 'w')
    #file_index = open(relative_path + '/' + file_name + '_index.txt', 'w')

    unparsed_info = text.replace('-\n', '')
    #print(unparsed_info)
    index_count = 1

    urls = Find(unparsed_info)
    elements = ''
    for element in unparsed_info.splitlines():
        urls = Find(element)
        if len(urls) != 0:
            for url in urls:
                element = element.replace(url, str(index_count), 1)
                elements = elements + element +'\n'
                #file_index.write(str(index_count) + ' - ' + url + '\n')
                index_count = index_count + 1

        char_presence = re.search('[a-zA-Z]', element)
        chapter_present = re.search(r'^\d{1,}\.', element) 

        if char_presence and not chapter_present:
            #file_output.write(element + '\n')
            elements = elements + element +'\n'
    #print(elements)
    #pdb.set_trace()
    #file_output.close()
    #file_input.close()
    #file_index.close()

    return normalization(elements)

if __name__ == "__main__":
    #doc2txt(sys.argv[1:])
    #normalization(sys.argv[1])
    purge_urls(sys.argv[1])