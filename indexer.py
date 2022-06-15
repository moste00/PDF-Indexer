# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 14:35:41 2022

@author: Mostafa
"""

import pdfplumber
import re
import sys

from ignored_words import IRRELEVANT_WORDS 

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
            self.index_file_path = re.search("TXT=.+\.txt",cmd_string).group()[4:]
        except AttributeError:
            self.parsing_errors.append( "No text File Path Recognized\n"
                                       +"Please Make Sure You Include The Extension Like This : foobarbaz.txt")
        
        self.groups = []
        #Try parsing ranged page groups
        ranged_groups = re.findall("[a-zA-Z0-9]+=[0-9]+\.\.[0-9]+",cmd_string)
        if ranged_groups:
            for group in ranged_groups:
                group_fields = group.split("=")
                group_name = group_fields[0]
                group_range = group_fields[1].split("..")
                    
                min_num,max_num = int(group_range[0]),int(group_range[1])
                if min_num > max_num:
                    min_num,max_num = max_num,min_num
                        
                self.groups.append(RangePageGroup(group_name, min_num, max_num))
        
            
def get_relevant_words(string):
    all_words = re.findall(r"[a-zA-Z]{2,}",string)
    
    return {word.lower() for word in all_words 
                         if not word.lower() in IRRELEVANT_WORDS}

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
        print("Parse Error! \n"+error)
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
        for word in sorted(index):
            index_file.write(word)
            index_file.write(":\n")
            
            for page_num in index[word]:
                index_file.write(str(page_num)+",")
                
                for group in args.groups:
                    if group.contains(page_num):
                        if group.name in groups_sub_indices:
                            groups_sub_indices[group.name][word] = {i for i in index[word] if group.contains(i)}
                        else:
                            groups_sub_indices[group.name] = {
                                                             word: 
                                                                 {i for i in index[word] if group.contains(i)}
                                                             }
                        
            index_file.write("\n")
            
    for group_name in groups_sub_indices:
        with open(group_name+".txt","w") as group_file:
            for word in groups_sub_indices[group_name]:
                group_file.write(word)
                group_file.write(":\n")
                
                for page_num in groups_sub_indices[group_name][word]:
                    group_file.write(str(page_num)+",")
                    
                group_file.write("\n")