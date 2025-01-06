#imports 
import pandas as pd
import matplotlib.pyplot as plt 

# Load the CSV Files
enrollment_df = pd.read_csv('C:/Users/Mitch/OneDrive/Documents/LSU Data Project/Enrollment - 5 Years.csv')
award_code_df = pd.read_csv('C:/Users/Mitch/OneDrive/Documents/LSU Data Project/Award Code Info.csv')
student_award_df = pd.read_csv('C:/Users/Mitch/OneDrive/Documents/LSU Data Project/Student Award Packages - 5 Years.csv')
dept_student_work_payroll_df = pd.read_csv('C:/Users/Mitch/OneDrive/Documents/LSU Data Project/Dept Student Work Payroll.csv')

#convert term name to financial year 
# dealing with int error
def term_to_finyear(term_name):
    try:
        term, year = term_name.split()
        year = int(year)
        if term == "Fall":
            return year + 1 
        elif term in ["Spring", "Summer"]:
            return year
        else: 
            return year 
    except Exception as e: 
        print(f"Error processing term_name {term_name}: {e}")
        return None
    
#apply function and create a new finyear column
enrollment_df['FINYEAR'] = enrollment_df['TERM_NAME'].apply(term_to_finyear)

#normalize column names
def normalize_column_names(df):
    df.columns = df.columns.str.strip().str.upper().str.replace(' ', '_')
    return df

enrollment_df = normalize_column_names(enrollment_df)
award_code_df = normalize_column_names(award_code_df)
student_award_df = normalize_column_names(student_award_df)
dept_student_work_payroll_df = normalize_column_names(dept_student_work_payroll_df)


#convert pay date to financial year 
#dealing with keyerror so doing this after column normalization
#dealing with date conversion issue so converting to datetime first
dept_student_work_payroll_df['PAY_DATE'] = pd.to_datetime(dept_student_work_payroll_df['PAY_DATE'], errors = 'coerce')

def pay_date_to_finyear(PAY_DATE):
    try:
        year = PAY_DATE.year
        if PAY_DATE.month >= 7: # July to December 
            return year + 1
        else: #January to June
            return year
    except Exception as e: 
        print(f"Error processing pay_date {PAY_DATE}: {e}")
        return None 
    
#apply the function and create a new finyear column
dept_student_work_payroll_df['FINYEAR'] = dept_student_work_payroll_df['PAY_DATE'].apply(pay_date_to_finyear)

#Impute missing data
student_award_df = student_award_df.fillna(0)


#check for missing values
enrollment_missing = enrollment_df.isnull().sum()
award_code_missing = award_code_df.isnull().sum()
student_award_missing= student_award_df.isnull().sum()
dept_student_work_payroll_missing = dept_student_work_payroll_df.isnull().sum()

# Need to sum finyear pay amounts for student work
grouped_payroll_df = dept_student_work_payroll_df.groupby(['ID', 'FINYEAR'])['PAY_AMOUNT'].sum().reset_index()

grouped_payroll_df = pd.merge(dept_student_work_payroll_df, grouped_payroll_df, on=['ID', 'FINYEAR'], suffixes=('', '_TOTAL'))

grouped_payroll_df = grouped_payroll_df.drop_duplicates()
#print("this is the grouped payroll")
#print(grouped_payroll_df)



#identify common keys
#merge data frames 
merged_df_1 = pd.merge(student_award_df, enrollment_df, on=['ID', 'FINYEAR'], how='inner')
#print("After merging student award df with enrollment df")
#print(merged_df_1.head())

merged_df_2 = pd.merge(merged_df_1, dept_student_work_payroll_df, on=['ID', 'FINYEAR'], how='left')
merged_df_2 = merged_df_2.fillna(0)
merged_df_2 = merged_df_2.drop_duplicates()
#print("After merging merge 1 with dept student work payroll")
#print(merged_df_2.head())
#print("merged 2 columns", merged_df_2.columns)
merged_df_3 = pd.merge(merged_df_2, grouped_payroll_df, on=['ID', 'FINYEAR'], how='left')
merged_df_3 = merged_df_3.fillna(0)
merged_df_3 = merged_df_3.drop_duplicates()
print("Merged3 DF columns")
print(merged_df_3.columns)

#merge dataframe with award codes
#merged_df_4 = pd.merge(merged_df_3,award_code_df, on='AWARD_CODE', how='left')

#define relevant columns
relevant_columns = ['ID', 'FINYEAR', 'LAST_NAME', 'FIRST_NAME', 'COLLEGE', 'MAJOR', 'FEE_RESIDENCE']

#sum the amt columns 
sum_amt_df = merged_df_3.copy()
sum_amt_df['AMT_TOTAL'] = sum_amt_df[['AMT1', 'AMT2', 'AMT3', 'AMT4', 'AMT5', 'AMT6', 'AMT7', 'AMT8', 'PAY_AMOUNT_TOTAL']].sum(axis=1, skipna=True)

#new dataframe with relevant columns and sum fo amts
analyze_this_df = sum_amt_df[relevant_columns +['AMT_TOTAL']]

#I am getting a df with 33334 rows, trying to drop duplicates
analyze_this_df = analyze_this_df.drop_duplicates()

print("New Relevant columns df")
print(analyze_this_df)
#print(analyze_this_df.tail())
 
#define totals 
total_aid_per_year = analyze_this_df.groupby('FINYEAR')['AMT_TOTAL'].sum()

total_aid_per_major = analyze_this_df.groupby('MAJOR')['AMT_TOTAL'].sum() 

total_aid_per_college = analyze_this_df.groupby('COLLEGE')['AMT_TOTAL'].sum() 

total_aid_per_residence = analyze_this_df.groupby('FEE_RESIDENCE')['AMT_TOTAL'].sum() 

#map y and N to actual labels
#Reset index to perform the mapping
total_aid_per_residence = total_aid_per_residence.reset_index()
label_map = {'Y': 'In-State', 'N': 'Out-of-State'}
total_aid_per_residence['FEE_RESIDENCE'] = total_aid_per_residence['FEE_RESIDENCE'].map(label_map)
total_aid_per_residence.set_index('FEE_RESIDENCE', inplace=True)


#plot total data by type
#print("Total Aid Distribution by Year")
total_aid_per_year.plot(kind='bar', xlabel='Financial Year', ylabel='Total Aid', title='Total Aid Distribution by Year')
plt.show()

#print("Total Aid Distribution by Major")
total_aid_per_major.plot(kind='barh', xlabel='Major', ylabel='Total Aid (in ten millions)', title='Total Aid Distribution by Major')
plt.show()

#print("Total Aid Distribution by College")
total_aid_per_college.plot(kind='barh', xlabel='College', ylabel='Total Aid (in ten millions)', title='Total Aid Distribution by College')
plt.show()

#print("Total Aid Distribution by Residence")
total_aid_per_residence['AMT_TOTAL'].plot(kind='pie', autopct='%1.1f%%', title='Percentage of Aid by Residence')
plt.show()

amt_total_sum = analyze_this_df['AMT_TOTAL'].sum()
print(f"Sum of column 'AMT_TOTAL' : {amt_total_sum}") 




#print("missing values")
#print(enrollment_missing)
#print(award_code_missing)
#print(student_award_missing)
#print(dept_student_work_payroll_missing)

# Check for duplicate rows in each dataframe
#print("Duplicates in enrollment_df:", enrollment_df.duplicated().sum())
#print("Duplicates in award_code_df:", award_code_df.duplicated().sum())
#print("Duplicates in student_award_df:", student_award_df.duplicated().sum())
#print("Duplicates in dept_student_work_payroll_df:", dept_student_work_payroll_df.duplicated().sum())

# Check unique values for merging keys in each dataframe
#print("Unique IDs in enrollment_df:", enrollment_df['ID'].nunique())
#print("Unique IDs in student_award_df:", student_award_df['ID'].nunique())
#print("Unique IDs in dept_student_work_payroll_df:", dept_student_work_payroll_df['ID'].nunique())
#print("Unique FINYEAR in enrollment_df:", enrollment_df['FINYEAR'].nunique())
#print("Unique FINYEAR in student_award_df:", student_award_df['FINYEAR'].nunique())
#print("Unique FINYEAR in dept_student_work_payroll_df:", dept_student_work_payroll_df['FINYEAR'].nunique())


