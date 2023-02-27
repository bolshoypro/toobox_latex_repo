import pandas as pd
import numpy as np
import re

def examples_to_frame(path):
    with open(path, encoding='utf-8') as file:
        string =file.read()

    df = pd.Series(string.split('\n')).iloc[2:].str.split(n=1, expand=True).replace({None, np.NaN})

    df = df.join (df[1].where(df[0].isin(['\\id', '\\ref'])).ffill(), rsuffix = '_r').set_index('1_r')
    df.rename({'1': 1}, axis=1, inplace=True)
    columns = ['\\tx', '\\mb','\\ge',	'\\ps',	'\\ft', '\\gr', '\\nt']
    dataf = pd.DataFrame(columns = columns)
    for i, row in df.iterrows():
        addon = pd.DataFrame(data = {row[0]: [row[1]]}, index= [i])
        if list(dataf.index) != []  and (dataf.iloc[[-1]].index == addon.index):
            dataf.fillna(addon, inplace=True)
        else:
            dataf = pd.concat([dataf, addon])
    dataf = dataf[columns]
    dataf.columns =  [col.strip('\\') for col in dataf.columns]
    dataf.dropna(thresh=4, inplace=True)
    return dataf


def write_examples(dataf, dest_folder):  
    for ref in dataf.ref:
        example = dataf.loc[ref].loc[['mb', 'ge', 'ft']].str.replace('  ', ' ') 
        example.index = ['\gla', '\glb', '\glft']
        example_str = example.to_string().replace('\n', '//\n')+'//'

        # labels = ['VN','NMLZ','INT','EZ.ATTR','NEG','DEFOC', 'IPFV','PFV','REV', 'DAT', 'ACC', 'PL','SG','1', '2','3', 'CAUS', 'INCH', 'P.', 'REFL', 'EXPE', 'BEN', ]
        # repl_dict = {x: r"{\sc "+str(x).lower()+"}" for x in labels}
        # for k in repl_dict:
        #     example_str = example_str.replace(k, repl_dict[k])
        
        while "  " in example_str:
              example_str = example_str.replace('  ', ' ')
        example_str = example_str.strip()         
        example_str = example_str.replace(' -', '-').replace('- ', '-')
        example_str = re.sub('\.//$',r'\\rq.//', example_str)
        example_str = re.sub('(?<!\.)//$',r'\\rq//', example_str)

        if 'Intended:' in example_str:
            example_str = example_str.replace(r'\glft Intended:', r'\glft Intended: \lq ')
            example_str = example_str.replace(r'\gla ', r'\gla *')
        else:
            example_str = example_str.replace(r'\glft', r'\glft \lq ')

        with open (f'{dest_folder}/{ref}.tex', 'w', encoding='utf-8') as file:
            file.write(example_str)
            
def  format_columns(table, mb_columns=None, ft_columns=None):
    if mb_columns is not None:
        for col in mb_columns:
            table[col] = table[col].apply(lambda x: '\\textit{'+f'{x}'+r'}')
            table[col] = table[col].str.replace('\xa0', ' ').str.replace('\t', ' ')

    while any(table[col].apply(lambda x: "  " in x)):            
        table[col] = table[col].str.replace('  ', ' ')

    table[col] = table[col].str.replace('- ', '-').str.replace(' -', '-')
    if ft_columns is not None:
        for col in ft_columns:
            table[col] = table[col].apply(lambda x: r'\lq '+f'{x}').str.replace('.', '\\rq.', regex=False).str.replace('  ', ' ')
    return table


            
def table_to_latex(table, caption, label, column_format = '|p{3.5cm}|p{3.7cm}|p{3.5cm}|p{3.7cm}|'):
    file_name = label.split(':')[-1]
    table.style.hide(axis= "index").to_latex(f'tables/{file_name}.tex',
                                        environment='longtable',
                                        column_format= column_format,
                                        caption = caption,
                                        label= label,
                                        hrules=True)

def examples_to_paradigm(examples, tonal_pattern, caption='Paradigm', label='table:para' ):
    examples = examples[['mb', 'ft']].copy()
    while any(examples .mb.apply(lambda x: '  ' in x)):
        examples .mb = examples .mb.str.replace('  ', ' ')
    examples.mb.str.replace('- ', '-').str.replace(' -', '-')
    examples.mb = examples.mb.str.replace('màà','').str.strip()
    examples.mb = examples.mb.str.replace('Sèydú','').str.strip()
    examples.ft = examples.ft.str.replace('Seydou', 'He/she').str.strip()
    examples.ft = examples.ft.str.replace('a house', '').str.strip()
    examples.ft = examples.ft.str.replace('(a) house', '', regex=False).str.strip()
    examples.ft = examples.ft.str.strip()
    examples  = format_columns(examples , mb_columns=['mb'], ft_columns=['ft'])
    examples.columns = ['Form',  'Translation']
    examples['Category'] = ['1SG', '2SG', '3SG', '1PL', '2PL', '3PL']
    examples['Tonal Pattern'] = tonal_pattern
    examples = examples [['Category', 'Form', 'Tonal Pattern', 'Translation']]
    column_format = '|l|l|l|l|'
    table_to_latex(examples , caption, label, column_format)