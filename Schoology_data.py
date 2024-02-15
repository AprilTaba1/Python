#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


#importing the schoology grade book 
df = pd.read_csv("Downloads/Schoology Report - Sheet1.csv")
HQT = pd.read_csv("Downloads/HQT Master List - Sheet1.csv")


# In[3]:


df = pd.merge(df, HQT, how='left', on='Section Name')


# In[40]:


df.info()


# In[4]:


df['teacher'] = df['Section Name'].apply(lambda x: x.split('-')[0].strip())


# In[5]:


def remove_common_substring(row):
    teacher_words = row['teacher'].split()
    common_words = [word for word in teacher_words if word in row['Course Name']]
    for common_word in common_words:
        row['teacher'] = row['teacher'].replace(common_word, '')
    return row['teacher']

# Apply the custom function to create the new column
df['new_teacher'] = df.apply(remove_common_substring, axis=1)

df['new_teacher'] = df['new_teacher'].str.strip()


# In[6]:


df


# In[23]:


df['new_teacher'].unique()


# In[7]:


def remove_spaces_after_underscore(text):
    parts = text.split('_')
    if len(parts) > 1:
        return '_'.join([parts[0], parts[1].lstrip()])
    return text

# Apply the custom function to create the new column
df['new_teacher_1'] = df['new_teacher'].apply(remove_spaces_after_underscore)


# In[8]:


def extract_part(text):
    parts = text.split('_')
    if len(parts) > 1:
        return parts[0] + '_' + parts[1].split(' ')[0]
    return text

# Apply the custom function to create the new column
df['new_teacher_2'] = df['new_teacher_1'].apply(extract_part)


# In[9]:


strings_to_replace = [
    'Fall 2023', 'Fall 23', 'A', 'Art  1A', 'Job Skills 1A', 'Job Skills 2A', 'ELD II', 'World Geography  A',
    'Woodshop 1A', 'Performing Arts  1A', 'Culinary Arts 1A', 'Photography I A', 'World Language  1A',
    'Psychology 1A', 'Automotive Technology 1A', 'Speech and Debate II A', 'Art  III A', 'Community Service II A',
    'Dance  II A', 'Instrumental Music  I A', 'Job Skills II A', 'Leadership II A', 'Literature I A',
    'Life Skills in Science IIA', 'Cosmetology II A', 'World Geography A', 'logic elective 1A', 'Instrumental Music 2A',
    'Photography 2A', 'Photography  1B', 'Instrumental Music 1B', 'Life Skills Essentials for Independent Living IVA',
    'Life Skills in English IVA', 'Life Skills in Mathematics IV A', 'Life Skills in Social Studies II A', 
    'Cosmetology  I', 'Theater  I', 'Job Skills', 'Section 1'
]

# Custom function to replace strings based on exact matches
def replace_teacher_name(teacher):
    if teacher in strings_to_replace:
        return 'none'
    return teacher

# Apply the custom function to create the new column
df['new_teacher_3'] = df['new_teacher_2'].apply(replace_teacher_name)


# In[10]:


replacement_dict = {
    'Murphy':'Murphy_Garcia_Heather',
    'Regua': 'Regua-Avila_Kimberly',
    'Ogawa': 'Ogawa_Guy',
    'Valencia': 'Valencia-Benitez_Diana',
    'Sjostrand': 'Sjostrand-Logan',
    'Fisher': 'Fisher-Lasker_Emery',
    'Eaton': 'Eaton_Carlie'
}

# Apply the changes and create the new column directly
df['Final_teacher_name'] = df['new_teacher_3'].replace(replacement_dict)


# In[11]:


df['Program'] = df['Course Name'].apply(lambda x: 'Choice Plus' if '*' in x else 'Course Outline')


# In[12]:


df.info()


# In[13]:


df['course_name_final'] = df['Course Name'].str.replace('*', '')


# In[14]:


def reverse_and_replace(text):
    if '_' in text:
        return ' '.join(reversed(text.split('_')))
    elif ',' in text:
        return ' '.join(reversed(text.split(', ')))
    else:
        return text

# Apply the custom function to create the new column
df['updated_name'] = df['Final_teacher_name'].apply(reverse_and_replace)


# In[36]:


df


# In[15]:


df['final_all_teacher_names'] = np.where(df['updated_name'] == 'none', df['HQT'], df['updated_name'])


# In[16]:


df


# In[15]:


#mean_grade = df.groupby(['course_name_final', 'Program','updated_name'])['Grades'].mean().reset_index()


# In[125]:


#mean_grade


# In[127]:


#df.to_csv('Schoology_cleaned.csv', index=False)
#mean_grade.to_csv('Schoology_summarized.csv', index=False)


# In[17]:


df.info()


# In[18]:


master_course = pd.read_csv("Downloads/Course Master - Sheet1.csv")
master_course["clean_choice_plus"] = master_course["ChoicePlus Academy"].str.replace("*", "").str.strip()


# In[19]:


master_course


# In[21]:


df['Course Name']= df['Course Name'].str.strip()

master_course['Outline']= master_course['Outline'].str.strip()
master_course['clean_choice_plus']= master_course['clean_choice_plus'].str.strip()

master_course_short = master_course[['Outline', 'clean_choice_plus']]

master_choice_join = pd.merge(df, master_course_short, left_on='Course Name', right_on='Outline', how='left')


# In[22]:


master_choice_join


# In[31]:


master_choice_join.to_csv('master_choice_join_two.csv', index=False)


# In[ ]:





# In[29]:


master_choice_join['match_choice_course'] = np.where(pd.isna(master_choice_join['Outline']), master_choice_join['course_name_final'], master_choice_join['clean_choice_plus'])


# In[30]:


master_choice_join


# In[32]:


master_choice_join['common_with_choice'] = np.where(pd.isna(master_choice_join['Outline']), 
                                                    "No", 
                                                    "Yes")


# In[33]:


master_choice_join


# In[43]:


Schoology_Choice_Outline_Match_final_2_15_24.info()


# In[46]:


columns_to_drop = ['new_teacher', 'new_teacher_1', 'new_teacher_2','new_teacher_3','clean_choice_plus','updated_name']


Schoology_Choice_Outline_Match_final_2_15_24= master_choice_join.drop(columns=columns_to_drop)


# In[47]:


Schoology_Choice_Outline_Match_final_2_15_24


# In[48]:


#remove subs

Schoology_Choice_Outline_Match_final_2_15_24 = Schoology_Choice_Outline_Match_final_2_15_24[Schoology_Choice_Outline_Match_final_2_15_24['HQT'] != "Sub"]


# In[49]:


Schoology_Choice_Outline_Match_final_2_15_24.to_csv('Schoology_Choice_Outline_Match_final_2_15_24.csv', index=False)


# In[ ]:




