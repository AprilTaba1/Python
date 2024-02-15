#!/usr/bin/env python
# coding: utf-8

# In[31]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')


# # Preparing the MVA Edgenuity data

# In[32]:


#importing the MVA_Edgenuity grade book as well as the list of teachers to identify duplicated names.
df_mva = pd.read_csv("Downloads/MVA Edgenuity Grade Report - Sheet1.csv")
df_mva['School'] = 'MVA'
df_pca = pd.read_csv("Downloads/PCA Edgenuity Grade Report - Sheet1 (1).csv")
df_pca['School'] = 'PCA'
df_cpa = pd.read_csv("Downloads/Cabrillo Edgenuity Grade Report - Sheet1.csv")
df_cpa['School'] = 'CPA'

df = pd.concat([df_mva, df_pca, df_cpa], ignore_index=True)

df_teacher_ref = pd.read_csv("Downloads/MVA Edgenuity Grade Report - Sheet2.csv")


# In[33]:


df.info()


# In[34]:


#master course list
master_course = pd.read_csv("Downloads/Course Master - Sheet1.csv")
master_course["clean_choice_plus"] = master_course["ChoicePlus Academy"].str.replace("*", "").str.strip()

master_course['Edgenuity_master'] = np.where(
    master_course['Edgenuity'].str.strip() == '2 Year Algebra 1 A', 
    '2 Year Algebra 1 A 1', 
    master_course['Edgenuity']
)

master_course_clean = master_course[['clean_choice_plus','Edgenuity_master']]

master_course_clean


# ## Extracting the teacher and course name from Edgenuity data

# In[35]:


df['teacher'] = df['Course Name'].str.split('-').str[2].str.strip()

# Extract what comes before the first dash
df['course_name_short'] = df['Course Name'].str.split('-').str[0].str.strip()

#cleaning. the teacher name column by removing (Sub) and extra spaces.
df['teacher'] = df['teacher'].str.replace(r'\(Sub\)', '', regex=True)
df['teacher'] = df['teacher'].str.strip()



# In[36]:


#pd.set_option('display.max_rows', None)  # Show all rows
  # Show all columns


# In[37]:


df


# In[38]:


df_teacher_ref


# In[39]:


#check for different teachers with the same last name
duplicate_values = df_teacher_ref['Last Name'][df_teacher_ref['Last Name'].duplicated()]


# In[40]:


duplicate_values


# In[41]:


#using the fisrt name to differente between the teachers with the same last name.
#making a new column that includes to differentiated last name: R Scott and S Scott
conditions = [
    (df_teacher_ref['First Name'] == 'Rachel') & (df_teacher_ref['Last Name'] == 'Scott'),
    (df_teacher_ref['First Name'] == 'Shannon') & (df_teacher_ref['Last Name'] == 'Scott')
]
values = ['R Scott', 'S Scott']

# Use numpy.select to create the "updated_last" column
df_teacher_ref['updated_last'] = np.select(conditions, values, default=df_teacher_ref['Last Name'])
df_teacher_ref['updated_last'] = df_teacher_ref['updated_last'].str.strip()


# ## Try fuzzy matching to make the future join more straight forward

# In[42]:


get_ipython().system('pip install fuzzywuzzy')
get_ipython().system('pip install python-Levenshtein')
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


# In[43]:


# Function to compare names using fuzzy matching
def fuzzy_match(name1, name2):
    ratio = fuzz.token_sort_ratio(name1, name2)
    return ratio >= 80  # Adjust the threshold as needed
# Merge DataFrames based on exact matches
merged_df_exact = pd.merge(df, df_teacher_ref, left_on='teacher', right_on='updated_last', how='inner')






# In[44]:


df1_no_exact_match = df[~df['teacher'].isin(merged_df_exact['teacher'])]


# In[45]:


df1_no_exact_match.info()


# In[46]:


def find_fuzzy_match(name):
    match = process.extractOne(name, df_teacher_ref['updated_last'], scorer=fuzz.token_sort_ratio)
    return match[0] if match[1] >= 80 else None


# In[47]:


def clean_and_lowercase(s):
    if isinstance(s, str):
        return s.lower().strip()
    else:
        return s


def find_fuzzy_match(name):
    if pd.notna(name):
        name_cleaned = clean_and_lowercase(name)
        matches = process.extractOne(name_cleaned, df_teacher_ref['updated_last'].apply(clean_and_lowercase), scorer=fuzz.token_sort_ratio)
        
        if matches[1] >= 80:
            return df_teacher_ref.loc[matches[2], 'updated_last']
        
        # Custom rule: Check if one name is a substring of the other
        for ref_name in df_teacher_ref['updated_last']:
            if name_cleaned in clean_and_lowercase(ref_name) or clean_and_lowercase(ref_name) in name_cleaned:
                return ref_name
        
    return None


# In[48]:


# Apply fuzzy matching to find matches for names without an exact match

df1_no_exact_match['fuzzy_match'] = df1_no_exact_match['teacher'].apply(find_fuzzy_match)



# In[49]:


df1_no_exact_match = pd.merge(df1_no_exact_match, df_teacher_ref, left_on='fuzzy_match', right_on='updated_last', how='inner')


# In[50]:


df1_no_exact_match


# In[51]:


# Append df1_no_exact_match and merged_df_exact
result_df = pd.concat([df1_no_exact_match, merged_df_exact], ignore_index=True)

result_df


# In[52]:


#making sure to mark the ambiguous last names (i.e., when two teachers 
#have the same last name but we do not have the first name to differentiate between the two).

#using the fisrt name to differente between the teachers with the same last name.
#making a new column that includes to differentiated last name: R Scott and S Scott
result_df['updated_name'] = np.where(result_df['teacher'] == 'Scott', 'Unclear', result_df['Full Name'])
result_df['course_name_final'] = result_df['course_name_short'].str.split('.').str[0].str.strip()
result_df['modified_grade'] = pd.to_numeric(result_df['Grade'].str.rstrip('%'), errors='coerce') / 100


# In[37]:


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


# In[48]:


result_df


# In[53]:


def reverse_and_replace(text):
    if '_' in text:
        return ' '.join(reversed(text.split('_')))
    elif ',' in text:
        return ' '.join(reversed(text.split(', ')))
    else:
        return text
    
result_df['finall_all_teacher_names'] = result_df['updated_name'].apply(reverse_and_replace)


# In[54]:


#mean_grade = result_df.groupby(['updated_name', 'course_name_short'])['modified_grade'].mean().reset_index()

#mean_grade_2 = result_df.groupby(['course_name_final', 'updated_name'])['modified_grade'].mean().reset_index()



# In[23]:


result_df


# In[ ]:


#sns.set(style="whitegrid")

#g = sns.catplot(x="updated_name",  
 #               y="modified_garade", 
  #              hue="updated_name", 
   #             col="course_name_final", 
    #            data=mean_grade_2)

#g.tight_layout


# In[ ]:


#g = sns.catplot(x="updated_name",  
               # y="modified_garade", 
               # hue="updated_name", 
               # col="course_name_final", 
               # data=mean_grade_2)

#plt.subplots_adjust(top=0.9)  # Adjust the top margin


# In[46]:


result_df.info()


# In[28]:


#result_df.to_csv('all_Edgenuity_cleaned.csv', index=False)


# In[55]:


result_df['course_name_final']= result_df['course_name_final'].str.strip()

master_course_clean['Edgenuity_master']= master_course_clean['Edgenuity_master'].str.strip()

Edgenuity_choice_join = pd.merge(result_df, master_course_clean, left_on='course_name_final', right_on='Edgenuity_master', how='left')


# In[26]:


Edgenuity_choice_join


# In[56]:


Edgenuity_choice_join['match_choice_course'] = Edgenuity_choice_join.apply(lambda row: row['clean_choice_plus'] if not pd.isnull(row['clean_choice_plus']) else row['course_name_final'], axis=1)


# In[28]:


Edgenuity_choice_join


# In[29]:


Edgenuity_choice_join.info()


# In[57]:


Edgenuity_choice_join_short = Edgenuity_choice_join[['User ID','Last Name_x','First Name_x','Course Name','Start Date','Target Date','First Grade',
                                                   'Last Grade','Days Since Last Action','Target Completion','Progress',
                                                    'External User ID', 'School', 'finall_all_teacher_names', 'course_name_final', 'match_choice_course','Edgenuity_master','modified_grade']]


# In[46]:


Edgenuity_choice_join_short


# In[58]:


#mark common courses between edgenuity and choice plus
Edgenuity_choice_join_short['common_with_choice'] = np.where(pd.isna(Edgenuity_choice_join_short['Edgenuity_master']), 
                                                    "No", 
                                                    "Yes")


# In[59]:


Edgenuity_choice_join_short


# In[61]:


#remove subs:
Edgenuity_choice_join_short_no_sub = Edgenuity_choice_join_short[~Edgenuity_choice_join_short['Course Name'].str.contains("\(Sub\)")]


# In[62]:


Edgenuity_choice_join_short_no_sub.to_csv('Edgenuity_Choice_Match_Final_2_15_24.csv', index=False)


# In[ ]:




