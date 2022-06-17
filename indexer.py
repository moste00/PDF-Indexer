# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 14:35:41 2022

@author: Mostafa
"""

import pdfplumber
import re
import sys

from ignored_words import IRRELEVANT_WORDS 

from config import DEFAULT_EXTENSION
from config import before_writing_begins
from config import before_writing_word,after_writing_word,before_writing_pagenum,after_writing_pagenum
from config import after_writing_ends

#A Page Group is a name given to a bunch of pages
#It's an interface with a single method 
#contains(page_number : Int) : Bool 
#That returns whether the page number belongs to the page
class PageGroup:
    def __init__(self,name):
        self.name = name
    
class RangePageGroup(PageGroup):
    def __init__(self,name,start_page_number,end_page_number):
        self.start = start_page_number
        self.end = end_page_number
        PageGroup.__init__(self, name)
    
    def contains(self,page_number):
        return page_number >= self.start and page_number <= self.end

class SetPageGroup(PageGroup):
    def __init__(self,name,page_numbers):
        self.page_numbers = page_numbers
        PageGroup.__init__(self, name)
    
    def contains(self,page_number):
        return page_number in self.page_numbers
        
class CmdArgsParser:
    
    def __init__(self,cmd_string):
        self.parsing_errors = []
        
        #Try parsing the pdf path 
        try:
            self.pdf_file_path = re.search("PDF=.+\.pdf",cmd_string).group()[4:]
        except AttributeError:
            self.parsing_errors.append( "No PDF File Path Recognized\n"
                                       +"Please Make Sure You Include The Extension Like This : foobarbaz.pdf")
        #Try parsing the index text file path
        try:
            self.index_file_path = re.search("IDX=.+\.[a-zA-Z0-9]{3}",cmd_string).group()[4:]
        except AttributeError:
            self.parsing_errors.append( "No Index File Path Recognized\n"
                                       +"Please Make Sure You Include The Extension Like This : foobarbaz.ext")
        
        self.groups = []
        #Try parsing ranged page groups
        ranged_groups = re.findall("[a-zA-Z0-9]+=[0-9]+\.\.[0-9]+",cmd_string)
        if ranged_groups:
            for group in ranged_groups:
                group_fields = group.split("=")
                group_name = group_fields[0]
                group_range = group_fields[1].split("..")
                
                #Sort group start and group end 
                min_num,max_num = int(group_range[0]),int(group_range[1])
                if min_num > max_num:
                    min_num,max_num = max_num,min_num
                
                #Insert default extension if group name has no extension
                if group_name.rfind(".") == -1:
                    group_name = group_name + DEFAULT_EXTENSION
                    
                self.groups.append(RangePageGroup(group_name, min_num, max_num))
        
            
def get_relevant_words(string):
    all_words = re.findall(r"[a-zA-Z]{3,}",string)
    
    relevant_words = set({})
    for word in all_words:
        word_lowercase = word.lower() 
        if not word_lowercase in IRRELEVANT_WORDS:
            relevant_words.add(word_lowercase)
        
    return relevant_words

###################################################################################################################
###################################################################################################################
###################################################################################################################
###################################################################################################################
#                                                       MAIN
###################################################################################################################
###################################################################################################################
################################################################################################################### 
###################################################################################################################
args = CmdArgsParser(' '.join(sys.argv))
if args.parsing_errors:
    for error in args.parsing_errors:
        print("################################# Parse Error! ################################# \n"+error)
else:
    #This is a Dictionary<String, Set<Integer>> that will map each relevant word to the set of pages where it appears         
    index = {}
    
    with pdfplumber.open(args.pdf_file_path) as pdf_file:
        for idx,page in enumerate(pdf_file.pages):
            text = page.extract_text()
            words = get_relevant_words(text)
            
            for word in words:
                #If word was encountered before
                if word in index:
                    #Add current page number to the set of page numbers where the word appears
                    index[word].add(idx+1)
                #If this is a new word
                else:
                    #add it to the index with the current page number as the only page (yet) where it appears  
                    index[word] = {idx+1}
    
    #This is a Dictionary<String, 
    #                     Dictionary<String,Set<Integer>>>
    #That will map each group name to a sub-index of the words that appear in this group's pages
    groups_sub_indices = {}    
    
    with open(args.index_file_path,"w") as index_file:
        
        index_file.write(before_writing_begins(len(index)))
        
        for i,word in enumerate(sorted(index)):
            index_file.write(before_writing_word(i))         
            index_file.write(word)
            index_file.write(after_writing_word(i+1))
            
            total_num_pages = len(index[word])
            for j,page_num in enumerate(index[word]):
                index_file.write(before_writing_pagenum(j, total_num_pages))
                index_file.write(str(page_num))
                index_file.write(after_writing_pagenum(j+1, total_num_pages))

                #While we're iterating over the master index
                #Build the sub indices of each group
                for group in args.groups:
                    if group.contains(page_num):
                        if group.name in groups_sub_indices:
                            groups_sub_indices[group.name][word] = {i for i in index[word] if group.contains(i)}
                        else:
                            groups_sub_indices[group.name] = {
                                                             word: 
                                                                 {i for i in index[word] if group.contains(i)}
                                                             }
        index_file.write(after_writing_ends())                
            
            
    for group_name in groups_sub_indices:
        with open(group_name,"w") as group_file:
            group_file.write(before_writing_begins(len(groups_sub_indices[group_name])))
            
            for i,word in enumerate(groups_sub_indices[group_name]):
                group_file.write(before_writing_word(i))  
                group_file.write(word)
                group_file.write(after_writing_word(i+1))
                
                total_num_pages = len(groups_sub_indices[group_name][word])
                for j,page_num in enumerate(groups_sub_indices[group_name][word]):
                    group_file.write(before_writing_pagenum(j, total_num_pages))
                    group_file.write(str(page_num))
                    group_file.write(after_writing_pagenum(j+1, total_num_pages))
                    
            group_file.write(after_writing_ends())