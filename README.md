# World_Bank_Correlations

A package to investigate relationships between World Bank variables. The package offers several methods to explore potential relationships with the over 20,000 variables in the World Bank data, and each has several options for displaying results. This package builds on the World Bank Data package built by MWOUTS (available here: https://github.com/mwouts/world_bank_data) and the World Bank API (which can be explored here: https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information).

## Installation

```bash
$ pip install World_Bank_Correlations
```

# Usage

For all functions below, the input data contains information on a variable of interest. Among the columns should be one named "Country," one named "Year," and one with the data concerning the variable of interest. The integer column index that contins information on the variable should be used as the value for col. In all functions, if the relationship(s) between a World Bank indicator and one or more others is desired, data can be substituted with a call of wb.get_series() with the id of the indicator of interest and the desired value for mrv (see examples below and documentation on the package's Github page). If using wb.get_series(), it is necessary to use wb.get_series().reset_index() to ensure similarilty between column names in the resultant dataset and those created through the World Bank API. 

In each function, if change is set to False, then any settings of nlim, cor_lim, or t_lim apply to the relationship between the input variable and World Bank variable. If change is set to True, these limits apply to the correlation between the annual percent changes of the two variables.

In all functions, the output is a dataframe sorted by the absolute value of the correlation between your input variable and the desired World Bank variables if change is set to False. If change is set to True, the dataframe will be ordered on the correlation between the annual percent change of the input variable and the annual percent change of the World Bank variables chosen to investigate. 

For functions where relevant: nlim sets the minimum number of observations that can be used to find a relationship, cor_lim sets the minimum absolute value of correlations to be displayed, and t_lim sets the minimum absolute value of the t-score of correlations to be displayed. All minimum options apply to nominal correlation if change is set to False and to the correlation between the annual percent changes if change is set to True. 

---

## Relationship with a Specific Indicator or Indicators

```bash
wbc.wb_corr(data, col, indicator, change=False)
```

Find the relationship(s) between your chosen variable of interest and one or more specific World Bank variables. Indicator can be either a string of the id corresponding to the variable to test against or a list of such strings.

Ex:
```bash
import pandas as pd
import lxml
import wb_data as wb
import requests
from World_Bank_Correlations import World_Bank_Correlations as wbc
sample=wb.get_series('3.0.Gini',mrv=50).reset_index()
wbc.wb_corr(sample,3,['SP.POP.TOTL','1.0.HCount.1.90usd'])
```

---

## Relationships with Indicators by Topic
```bash
wbc.wb_topic_corrs(data, col, topic, k=5, change=False, nlim=1, cor_lim=0, t_lim=0)
```
This command will find the relationship between your variable of interest and all of the indicators listed under one of the 21 topics as defined by the World Bank, searchable through their API, and displays the k strongest relationships. Topic can either be the integer associated with the topic or a string with the name of the topic. 


ex:
```bash
Bot40=pd.read_csv('C:\\Users\\John Marion\\...\\Bottom_40.csv')
Bot40.columns
```
Index(['Country', 'Year', 'income_share_bottom_40'], dtype='object')

```bash
wbc.wb_topic_corrs(Bot40,2,1,k=3,change=True,t_lim=.5)
```

---

## Relationship with Indicators by Search

```bash
wbc.wb_corrs_search(data,col,search,k=5,change=False,nlim=1,cor_lim=0,t_lim=0)
```
This allows users to find the k strongest relationships between an input variable of interest and all World Bank indicators whose names match an input keyword search. 

ex:
```bash
wbc.wb_corrs_search(wb.get_series('3.0.Gini',mrv=50).reset_index(), 3, "income share", n_lim=25)
```

---

## Strongest Relationship with any Indicators in the World Bank Data

```bash
wb_every(data, col, k=5, change=False, nlim=1, cor_lim=0, t_lim=0):
```
The above will find the k strongest relationships between your input variable and all of the available variables in the World Bank data. Take caution before running, as it will require significant time. 

ex: 
```bash
wbc.wb_every(wb.get_series('3.0.Gini',mrv=50).reset_index(), 3, nlim=50)
```

---

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`World_Bank_Correlations` was created by A John Marion. It is licensed under the terms of the MIT license.

## Credits

`World_Bank_Correlations` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
