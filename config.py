# -*- coding: utf-8 -*-
"""
Created on Fri Jun 17 16:42:23 2022

@author: Mostafa
"""


#If page group names don't contain extensions, this will be the used extension for the file of the page group
DEFAULT_EXTENSION = ".txt"


#Those callbacks will be called at specific events during the index printing process
#This allows you to control the format of the resulting file at a really fine-grained level

#Called one time at the very begining of the writing process to the index file
#Takes the total number of words that will be written to the file, in case you need it for metadata. 
def before_writing_begins(total_num_words):
    return ""

#Called immediately before writing a word to the index file
def before_writing_word(num_words_written_so_far):
    return ""
#Called immediately after writing a word to the index file
def after_writing_word(num_words_written_so_far):
    return ":"

#Called immediately before writing a page number
def before_writing_pagenum(page_numbers_written_so_far, total_page_numbers):
    return ""
#Called immediately after writing a page number
def after_writing_pagenum(page_numbers_written_so_far, total_page_numbers):
    if page_numbers_written_so_far == total_page_numbers: return "\n"
    return ","

#Called once when the writing to the file ends
def after_writing_ends():
    return ""