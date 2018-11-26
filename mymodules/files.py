#!/usr/bin/env python3
from bs4 import BeautifulSoup as soup
import os
import re
import sys

exclude_functions = ["error", "success", "function", "press"]
not_in_functions = ["function", "//", "*", '"']


def get_all_files (file_location):
    files = []
    for foldername, subfolders, filenames in os.walk(file_location):
        for filename in filenames:
            filename_full = os.path.join(foldername, filename)
            filetpl = (foldername, filename, filename_full)
            files.append[filetpl]
    return files

def get_files_by_type(file_type, file_location):
    files = []
    for foldername, subfolders, filenames in os.walk(file_location):
        for filename in filenames:
            filename_noext, file_extension = os.path.splitext(filename)
            if file_extension == file_type:
                filename_full = os.path.join(foldername, filename)
                filetpl = (foldername, filename, filename_full)
                files.append(filetpl)
    return files

def get_view_and_controller(file_location):
    views = get_artifact_by_type("view.xml", file_location)
    controllers = get_artifact_by_type("controller.js", file_location)
    viewctrls = []
    for view in views:
        controller = get_ctrl_from_view(view)
        if controller is not None:
          for ctrl in controllers:
                if ctrl[3] != None and ctrl[3] == controller:
                    viewctrl = (view[0],view[1],ctrl[0],ctrl[1], controller)
                    viewctrls.append(viewctrl)
                        
    return viewctrls

def get_artifact_by_type(artifact, file_location):
    try:
        files = []
        for foldername, subfolders, filenames in os.walk(file_location):
            filetpl = None
            for filename in filenames:
                if artifact is 'util':
                    filetpl = get_util_artifacts(foldername, artifact, filename)
                elif artifact in filename:
                    filetpl = get_view_ctrl_artifacts(foldername, artifact, filename)

                if filetpl is not None:
                        files.append(filetpl)  
        files = list(set(files))
        files.sort(key=lambda tup: (tup[0], tup[1]))
        return files
    except:
        return None

def get_util_artifacts(foldername, artifact, filename):
    filetpl = None
    if "controller.js" not in filename:
        filename_noext, file_extension = os.path.splitext(filename)
        if file_extension == ".js":
            filename_full = os.path.join(foldername, filename)
            filetpl = (foldername, filename, filename_full)
    return filetpl

def get_view_ctrl_artifacts(foldername, artifact, filename):
    filename_noext, file_extension = os.path.splitext(filename)
    filename_full = os.path.join(foldername, filename)
    filetpl = None
    if artifact == "view.xml":
        filetpl = (foldername, filename, filename_full)
    if artifact == "controller.js":
        controllerdefname = get_controller_def_name(filename_full)
        filetpl = (foldername, filename, filename_full, controllerdefname)
    return filetpl

def get_controller_def_name(file):
    try:
        try:
            controller = open(file, 'r', encoding='utf-8')
            lines = controller.read()
        except:
            controller = open(file)
            lines = controller.read()

        regex = re.compile(r'extend\([\'\"].*[\'\"],')
        matchstr = regex.search(lines)
        matchstr = matchstr.group()
        regex = re.compile(r'[\'\"].*[\'\"]')
        matchstr = regex.search(matchstr)
        return matchstr.group()[1:-1]
    except Exception:
        pass

def get_ctrl_from_view(file):
    if "view.xml" in file[1]:
        fileobj = open(file[2])
        bs = soup(fileobj, "lxml")
        # print (bs)
        tagarray = bs.findAll(lambda tag: tag.name == "mvc:view")
        if len(tagarray) == 0:
            tagarray = bs.findAll(lambda tag: tag.name == "core:view")    
        controller = None
        if len(tagarray) > 0:
            try:
                controller = tagarray[0]["controllername"]
            except:
                pass

            return controller

def get_file_content(file):    
    fileobj = open(file, 'r', encoding='utf-8')
    filecontent = fileobj.readlines()        
    return (fileobj, filecontent)

def valid_for_funcname_probe(decodedline):
    for stringpart in not_in_functions:
        if stringpart in decodedline:
            return False
    return True

def split_line_at_chars(line, charlist):
    split = []
    for charc in charlist:
        if charc in line:
            split = line.split(charc)
    return split

def sanitize_decoded_line_prefixes(decodedline):
    exclude_prefixes = [","]
    if(decodedline[0] in exclude_prefixes):
        return decodedline[1:len(decodedline)]
    return decodedline

def get_decoded_line(line):
    try:
        regex = re.compile(r'[^{$#()",\}]*[=:]*function')
        byteline = bytes(line, encoding='ascii')
        decodedline = byteline.decode("unicode-escape")
        if regex.search(line):
            split = split_line_at_chars(line, [":", "="])
            byteline = bytes(split[0], encoding='ascii')
            decodedline = byteline.decode("unicode-escape").strip(' \t\n\r')
            decodedline = decodedline.replace("var ", '')
            return sanitize_decoded_line_prefixes(decodedline)
        return None
    except:
        return None

def get_functions_from_js(file):
    try:
        file_parts = get_file_content(file)
        fnnames = []
        for line in file_parts[1]:
            try:
                decodedline = get_decoded_line(line)
                if decodedline is not None and decodedline not in exclude_functions and valid_for_funcname_probe(decodedline):
                    fnnames.append(decodedline)
            except:
                pass
        return list(set(fnnames))
    except:
        return []
