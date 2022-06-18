# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 14:35:41 2022

@author: Mostafa
"""

from collections import defaultdict
import pdfplumber
import re
import sys

from ignored_words import IRRELEVANT_WORDS 

from config import DEFAULT_EXTENSION
from config import before_writing_begins
from config import before_writing_word,after_writing_word,before_writing_pagenum,after_writing_pagenum
from config import after_writing_ends
from config import include_word_in_index
from cmd_args_parser import CmdArgsParser
            
def get_relevant_words(string):
    all_words = re.findall(r"[a-zA-Z]{3,}",string)
    
    relevant_words = []
    for word in all_words:
        word_lowercase = word.lower() 
        if not word_lowercase in IRRELEVANT_WORDS:
            relevant_words.append(word_lowercase)
        
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
    index = defaultdict(list)
    
    with pdfplumber.open(args.pdf_file_path) as pdf_file:
        for idx,page in enumerate(pdf_file.pages):
            text = page.extract_text()
            words = get_relevant_words(text)
            
            for word in words:
                index[word].append(idx+1)
    
    #This is a Dictionary<String, 
    #                     Dictionary<String,Set<Integer>>>
    #That will map each group name to a sub-index of the words that appear in this group's pages
    groups_sub_indices = {}    
    
    with open(args.index_file_path,"w") as index_file:
        
        index_file.write(before_writing_begins(len(index)))
        
        num_words_skipped = 0
        for i,word in enumerate(sorted(index)):
            page_set = sorted(set(index[word]))
            total_num_pages = len(page_set)
            total_num_occurrences = len(index[word])
            if not include_word_in_index(word, total_num_occurrences, total_num_pages, index[word]):
                num_words_skipped += 1
                continue 
            
            index_file.write(before_writing_word(i - num_words_skipped))         
            index_file.write(word)
            index_file.write(after_writing_word(i+1 - num_words_skipped))
            
            for j,page_num in enumerate(page_set):
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
