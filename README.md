# World_Bank_Correlations

A package to investigate relationships between World Bank variables. The package offers several methods to explore potential relationships with the over 20,000 variables in the World Bank data, and each has several options for displaying results. This package builds on the World Bank Data package built by MWOUTS (available here: https://github.com/mwouts/world_bank_data) and the World Bank API (which can be explored here: https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information).

## Installation

```bash
$ pip install World_Bank_Correlations
```

## Relationship with a Specific Indicator or Indicators

```bash
import pandas as pd
import lxml
import wb_data as wb
import requests
from World_Bank_Correlations import World_Bank_Correlations as wbc
wbc.wb_corr(data, col, indicator, change=False) 
```
where data is a dataframe containing data regarding your variable of interest, a column called "Country" and a column called "Year." Col is the integer index of the column containing data, and indicator is either the id of the World Bank variable to check or a list containing the ids of variables to check. This, as all commands in this package, can also be used to find the relationship between a World Bank indicator and other indicators by using wb.get_series() from the World Bank Data package as the data argument and 3 as the column argument. Otherwise, it can be used to find the relationships with a variable about which data is read from elsewhere. If change is set to True, the correlation between the annual percent changes of your input variable and the designated World Bank indicators will be found and displayed. 

Output is a dataframe with the names of indicators as the index, organized by the absolute value of the correlation if change is False and by the correlation between the annual percent changes when change is False. 

ex:
```bash
sample=wb.get_series('3.0.Gini',mrv=50).reset_index()
wbc.wb_corr(sample,3,'SP.POP.TOTL')
```

## Relationships with Indicators by Topic
```bash
wbc.wb_topic_corrs(data, col, topic, k=5, change=False, nlim=1, cor_lim=0, t_lim=0)
```
This command will find the relationship between your variable of interest and all of the indicators listed under one of the 21 topics as defined by the World Bank, searchable through their API, and displays the k strongest relationships. Topic can either be the integer associated with the topic or a string with the name of the topic. nlim sets the minimum number of observations that can be used to find a relationship, cor_lim sets the minimum absolute value of correlations to be displayed, and t_lim sets the minimum absolute value of the t-score of correlations to be displayed. All minimum options apply to correlation if change is set to False and to the correlation between the annual percent changes if change is set to True. 

Output is a dataframe with the k strongest relationships, displaying the indicator as the index, the correlation, the number of observations that were used to find the correlation based on the availabilty of data, and additional information as requested.

ex:
```bash
Bot40=pd.read_csv('C:\\Users\\John Marion\\...\\Bottom_40.csv')
Bot40.columns
```
Index(['Country', 'Year', 'income_share_bottom_40'], dtype='object')

```bash
wbc.wb_topic_corrs(Bot40,2,1,k=3,change=True,t_lim=.5)
```

## Relationship with Indicators by Search

```bash
wbc.wb_corrs_search(data,col,search,k=5,change=False,nlim=1,cor_lim=0,t_lim=0)
```
This allows users to find the k strongest relationships between an input variable of interest and all World Bank indicators that match an input keyword search. 

ex:
```bash
wbc.wb_corrs_search(wb.get_series('3.0.Gini',mrv=50).reset_index(), 3, "income share", n_lim=25)
```

## Strongest Relationship with any Indicators in the World Bank Data

```bash
wb_every(data, col, k=5, change=False, nlim=1, cor_lim=0, t_lim=0):
```
The above will find the k strongest relationships between your input variable and all of the available variables in the World Bank data. Take caution before running, as it will require significant time. 

ex: 
```bash
wbc.wb_every(wb.get_series('3.0.Gini',mrv=50).reset_index(), 3, nlim=50)
```


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`World_Bank_Correlations` was created by A John Marion. It is licensed under the terms of the MIT license.

## Credits

`World_Bank_Correlations` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
