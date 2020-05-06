#!/usr/bin/env python
# coding: utf-8

# # Introduction

# In this project, we'll play the role of data analyst and pretend our stakeholders want to know the following:
# 
# Are employees who only worked for the institutes for a short period of time resigning due to some kind of dissatisfaction? What about employees who have been there longer?
# 
# Are younger employees resigning due to some kind of dissatisfaction? What about older employees?
# 
# They want us to combine the results for both surveys to answer these questions. However, although both used the same survey template, one of them customized some of the answers. In the guided steps, we'll aim to do most of the data cleaning and get you started analyzing the first question.

# # Import Dataset

# In[2]:


import pandas as pd
import numpy as np


# In[3]:


dete_survey = pd.read_csv("dete_survey.csv", na_values = "Not Stated" )
tafe_survey = pd.read_csv("tafe_survey.csv")


# # Remove Unnecessary Columns

# In[4]:


dete_survey_updated = dete_survey.drop(dete_survey.columns[28:49], axis = 1)
tafe_survey_updated = tafe_survey.drop(tafe_survey.columns[17:66], axis = 1)                                      
                                       


# So far we have removed unnecessary columns that are unrelated to our analysis

# # Rename The Columns

# In[5]:


dete_survey_updated.columns = dete_survey_updated.columns.str.lower().str.strip().str.replace(" ", "_")




# In[6]:


mapping = {'Record ID': 'id', 'CESSATION YEAR': 'cease_date', 'Reason for ceasing employment': 'separationtype', 'Gender. What is your Gender?': 'gender', 'CurrentAge. Current Age': 'age',
       'Employment Type. Employment Type': 'employment_status',
       'Classification. Classification': 'position',
       'LengthofServiceOverall. Overall Length of Service at Institute (in years)': 'institute_service',
       'LengthofServiceCurrent. Length of Service at current workplace (in years)': 'role_service'}


tafe_survey_updated = tafe_survey_updated.rename(mapping, axis =1)


# Just now we have updated the columns name in order to concatenate the datasets together.

# # Filter The Data

# In[7]:


dete_survey_updated["separationtype"].value_counts()


# In[8]:


tafe_survey_updated["separationtype"].value_counts()


# In[9]:


dete_survey_updated["separationtype"] = dete_survey_updated["separationtype"].str.split("-").str[0]


# In[10]:


dete_survey_updated["separationtype"].value_counts()


# In[11]:


dete_resignations = dete_survey_updated[dete_survey_updated["separationtype"] == "Resignation"].copy()


# In[12]:


tafe_resignations = tafe_survey_updated[tafe_survey_updated["separationtype"] == "Resignation"].copy()


# # Clean The Column

# In[13]:


dete_resignations["cease_date"] = dete_resignations["cease_date"].str.split("/").str[-1].astype("float")


# In[14]:


dete_resignations["cease_date"] = dete_resignations["cease_date"].astype("float")


# In[15]:


dete_resignations["cease_date"].value_counts(dropna = False)


# In[16]:


dete_resignations["dete_start_date"].value_counts(dropna = False)


# In[17]:


tafe_resignations["cease_date"].value_counts()


# # Insert New Column

# In[18]:


dete_resignations["institute_service"] = dete_resignations["cease_date"]-dete_resignations["dete_start_date"]


# # Classify The Data

# In[19]:


tafe_resignations['Contributing Factors. Dissatisfaction'].value_counts(dropna=False)


# In[20]:


tafe_resignations['Contributing Factors. Job Dissatisfaction'].value_counts(dropna=False)


# In[21]:


def update_vals(value):
    if value == "-":
        return False
    elif pd.isnull(value):
        return np.nan
    else:
        return True


# In[22]:


tafe_resignations['dissatisfied'] = tafe_resignations[['Contributing Factors. Dissatisfaction','Contributing Factors. Job Dissatisfaction']].applymap(update_vals).any(1, skipna = False)


# In[23]:


tafe_resignations_up = tafe_resignations.copy()


# In[24]:


dete_resignations['dissatisfied'] = dete_resignations[['job_dissatisfaction',
       'dissatisfaction_with_the_department', 'physical_work_environment',
       'lack_of_recognition', 'lack_of_job_security', 'work_location',
       'employment_conditions', 'work_life_balance',
       'workload']].any(1, skipna=False)


# In[25]:


dete_resignations_up = dete_resignations.copy()


# In[26]:


dete_resignations_up['dissatisfied'].value_counts(dropna=False)


# # Add New Column

# In[27]:


dete_resignations_up["institute"] = "DETE"


# In[28]:


tafe_resignations_up["institue"] = "TAFE" 


# # Combine Dataframe

# In[29]:


combined = pd.concat([dete_resignations_up,tafe_resignations_up], ignore_index = True)


# # Clean New Dataframe

# In[30]:


combined_updated = combined.dropna(axis =1, thresh = 500).copy()


# In[31]:


combined_updated["institute_service"].value_counts(dropna = False)


# In[32]:


combined_updated['institute_service_up'] = combined_updated['institute_service'].astype('str').str.extract(r'(\d+)')
combined_updated['institute_service_up'] = combined_updated['institute_service_up'].astype('float')


# combined_updated['institute_service_up'].value_counts()

# # Convert The Data

# In[100]:


def convert(val):
    if val >= 11:
        return "Veteran"
    elif 7<=val<11:
        return "Established"
    elif 3<=val<7:
        return "Experienced"
    elif pd.isnull(val):
        return np.nan
    else:
        return "New"


# In[34]:


combined_updated["service_cat"] = combined_updated['institute_service_up'].apply(convert)


# In[117]:


combined_updated["service_cat"].value_counts(dropna=False)


# # Analyze The Data Based On Exit Stage

# In[35]:


combined_updated["dissatisfied"].value_counts(dropna=False)


# In[36]:


combined_updated["dissatisfied"] = combined_updated["dissatisfied"].fillna(False)


# In[37]:


combined_updated["dissatisfied"].value_counts()


# In[42]:


new = combined_updated.pivot_table(values = "dissatisfied", index = "service_cat")


# In[115]:


new 


# In[41]:


get_ipython().magic('matplotlib inline')


# In[44]:


new.plot(kind = 'bar', rot = 30)


# From the initial analysis above, we can tentatively conclude that employees with 7 or more years of service are more likely to resign due to some kind of dissatisfaction with the job than employees with less than 7 years of service. However, we need to handle the rest of the missing data to finalize our analysis.

# # Analyze The Data Based On Age

# In[69]:


combined_updated["age_new"] = combined_updated["age"].str.replace("  ", "-").str.replace("56 or older", "56-60").str.replace("61 or older", "61-65").str.replace("20 or younger","18-20")


# In[71]:


combined_updated["age_new"].value_counts()


# In[72]:


combined_updated["age_new2"]= combined_updated["age_new"].astype('str').str.extract(r'(\d+)')


# In[102]:


combined_updated["age_new2"] = combined_updated["age_new2"].astype("float")


# In[103]:


combined_updated2 = combined_updated.copy()


# In[104]:


def classify(value):
    if value > 45:
        return "Senior"
    elif 30 <=value <= 45:
        return "Middle-Age"
    elif pd.isnull(value):
        return np.nan
    else:
        return "Junior"


# In[106]:


combined_updated2["age_cat"] = combined_updated2["age_new2"].apply(classify)


# In[109]:


combined_updated2["age_cat"].value_counts(dropna=False)


# In[110]:


new2 = combined_updated2.pivot_table(index = 'age_cat', values = 'dissatisfied')


# In[113]:


new2.plot(kind='bar', rot = 30)


# From our analysis, we can conclude that senior employees (aged above 45 years old) are more likely to resign due to dissatisfaction with the company. The rest of age categories which are junior and middle-age are almost equal in resigning due to dissatisfaction. 

# In[114]:


new2


# In[ ]:




