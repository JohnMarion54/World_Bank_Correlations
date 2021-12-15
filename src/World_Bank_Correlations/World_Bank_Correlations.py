import requests
import pandas as pd
import world_bank_data as wb
import xml.etree.ElementTree as ET
from math import sqrt

def wb_corr(data, col, indicator, change=False):
    pd.options.mode.chained_assignment = None
    """
    Returns the relationship that an input variable has with a chosen variable or chosen variables from the World Bank data, sorted by the strength of relationship
    Relationship can be either the correlation between the input variable and the chosen indicator(s) or the correlation in the annual percent changes
    
    Parameters
    ----------
    data: A pandas dataframe that contains a column of countries called "Country," a column of years called "Year," and a column of data for a variable
    col: The integer index of the column in which the data of your variable exists in your dataframe
    indicator: The indicator or list of indicators to check the relationship with the input variable. Can be a character string of the indicator ID or a list
        of character strings. Indicator IDs can be found through use of the World Bank APIs
    change: A Boolean value. When set to True, the correlation between the annual percent change of the input variable and the annual percent change of 
        chosen indicator(s) will be found and used to order the strength of relationships
    
    Returns
    ----------
    Pandas DataFrame
        A Pandas DataFrame containing the indicator names as the index and the correlation between the indicator and the input variable. If change set to True,
            another column including the correlation between the annual percent changes of the variables will be included. The DataFrame is ordered on the
            correlation if change is set to False and on the correlation of percent changes if change is set to True.
            The number of rows in the DataFrame will correspond to the number of indicators that were requested. The number of columns will be 1 if change is 
                set to False and 2 if change is True. 
    
    Examples
    ----------
    >>> import ____
    >>> wb_corr(my_df, 2, '3.0.Gini') #where my_df has columns Country, Year, Data
        |Indicator       | Correlation  | n
        --------------------------------------
        |Gini Coefficient| -0.955466    | 172
        
    >>> wb_corr(wb.get_series('SP.POP.TOTL',mrv=50).reset_index,3,['3.0.Gini','1.0.HCount.1.90usd'],True) # To compare one WB indicator with others
        | Indicator                      | Correlation  | n   | Correlation_change | n_change
        ----------------------------------------------------------------------------------------
        | Poverty Headcount ($1.90 a day)|   -0.001202  |172  |       0.065375     | 134
        | Gini Coefficient               |    0.252892  |172  |       0.000300     | 134
    
    """
    assert type(indicator)==str or type(indicator)==list, "indicator must be either a string or a list of strings"
    assert type(col)==int, "col must be the integer index of the column containing data on the variable of interest"
    assert 'Country' in data.columns, "data must have a column containing countries called 'Country'"
    assert 'Year' in data.columns, "Data must have a column containing years called 'Year'"
    assert col<data.shape[1], "col must be a column index belonging to data"
    assert type(change)==bool, "change must be a Boolean value (True or False)"
    cors=[]
    indicators=[]
    n=[]
    if type(indicator)==str:
        assert indicator in list(pd.read_xml(requests.get('http://api.worldbank.org/v2/indicator?per_page=21000').content)['id']), "indicator must be the id of an indicator in the World Bank Data. Indicators can be found using the World Bank APIs. http://api.worldbank.org/v2/indicator?per_page=21000 to see all indicators or http://api.worldbank.org/v2/topic/_/indicator? to see indicators under a chosen topic (replace _ with integer 1-21)"
        thing=pd.DataFrame(wb.get_series(indicator,mrv=50))
        merged=pd.merge(data,thing,how='inner',on=['Country','Year'])
        cors.append(merged.iloc[:,col].corr(merged.iloc[:,(merged.shape[1]-1)]))
        indicators.append(pd.DataFrame(wb.get_series(indicator,mrv=1)).reset_index()['Series'][0])
        n.append(len(merged[merged.iloc[:,col].notnull() & merged.iloc[:,(merged.shape[1]-1)].notnull()]))
        if change==False:
            return pd.DataFrame(list(zip(indicators,cors,n)),columns=['Indicator','Correlation','n']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
        if change==True:
            mumbo=pd.DataFrame()
            cors_change=[]
            n_change=[]
            for country in data['Country'].unique():
                s=data[data['Country']==country]
                s.loc[:,'lag_dat']=s.iloc[:,col].shift(-1)
                s.loc[:,'pct_chg_dat']=(((s.iloc[:,col]-s['lag_dat'])/s['lag_dat'])*100)
                mumbo=pd.concat([mumbo,s]) #This now includes the percent change for the bottom 40
            t=thing.reset_index()
            jumbo=pd.DataFrame()
            for country in t['Country'].unique():
                y=t[t['Country']==country]
                y.loc[:,'lag_ind']=y.iloc[:,3].shift(-1)
                y.loc[:,'pct_chg_ind']=(((y.iloc[:,3]-y['lag_ind'])/y['lag_ind'])*100)
                jumbo=pd.concat([jumbo,y]) #The indicator data now includes percent change for the indicator
            merged_pct=pd.merge(mumbo,jumbo,how='left',on=['Country','Year']) #inner?
            cors_change.append(merged_pct.loc[:,'pct_chg_dat'].corr(merged_pct.loc[:,'pct_chg_ind']))
            n_change.append(len(merged_pct[merged_pct.loc[:,'pct_chg_dat'].notnull() & merged_pct.loc[:,'pct_chg_ind'].notnull()]))
            return pd.DataFrame(list(zip(indicators,cors,n,cors_change,n_change)),columns=['Indicator','Correlation','n','Correlation_change','n_change']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
    if type(indicator)==list:
        for indic in indicator:
            assert type(indic)==str, "Elements of indicator must be strings"
            assert indic in list(pd.read_xml(requests.get('http://api.worldbank.org/v2/indicator?per_page=21000').content)['id']), "indicator must be the id of an indicator in the World Bank Data. Indicators can be found using the World Bank APIs. http://api.worldbank.org/v2/indicator?per_page=21000 to see all indicators or http://api.worldbank.org/v2/topic/_/indicator? to see indicators under a chosen topic (replace _ with integer 1-21)"
        for i in range(0,len(indicator)):
            thing=pd.DataFrame(wb.get_series(indicator[i],mrv=50)).reset_index()
            merged=pd.merge(data,thing,how='inner',on=['Country','Year'])
            cors.append(merged.iloc[:,col].corr(merged.iloc[:,(merged.shape[1]-1)]))  
            indicators.append(pd.DataFrame(wb.get_series(indicator[i],mrv=1)).reset_index()['Series'][0])
            n.append(len(merged[merged.iloc[:,col].notnull() & merged.iloc[:,(merged.shape[1]-1)].notnull()]))
        if change==False:
            return pd.DataFrame(list(zip(indicators,cors,n)),columns=['Indicator','Correlation','n']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
        if change==True:
            cors_change=[]
            n_change=[]
            for i in range(0,len(indicator)):
                mumbo=pd.DataFrame()
                jumbo=pd.DataFrame()
                thing=pd.DataFrame(wb.get_series(indicator[i],mrv=50)).reset_index()
                for country in data['Country'].unique():
                    s=data[data['Country']==country]
                    s.loc[:,'lag_dat']=s.iloc[:,col].shift(-1)
                    s.loc[:,'pct_chg_dat']=(((s.iloc[:,col]-s['lag_dat'])/s['lag_dat'])*100)
                    mumbo=pd.concat([mumbo,s])
                for country in thing['Country'].unique():
                    y=thing[thing['Country']==country]
                    y.loc[:,'lag_ind']=y.iloc[:,3].shift(-1)
                    y.loc[:,'pct_chg_ind']=(((y.iloc[:,3]-y['lag_ind'])/y['lag_ind'])*100)
                    jumbo=pd.concat([jumbo,y])
                merged_pct=pd.merge(mumbo,jumbo,how='left',on=['Country','Year'])
                cors_change.append(merged_pct.loc[:,'pct_chg_dat'].corr(merged_pct.loc[:,'pct_chg_ind']))
                n_change.append(len(merged_pct[merged_pct.loc[:,'pct_chg_dat'].notnull() & merged_pct.loc[:,'pct_chg_ind'].notnull()]))
        return pd.DataFrame(list(zip(indicators,cors,n,cors_change,n_change)),columns=['Indicator','Correlation','n','Correlation_change','n_change']).sort_values(by='Correlation_change',key=abs,ascending=False).set_index('Indicator')
    pd.options.mode.chained_assignment = orig_value


def wb_topic_corrs(data,col,topic,k=5,change=False,nlim=1,cor_lim=0,t_lim=0):
    pd.options.mode.chained_assignment = None
    """
    Returns the relationship that an input variable has with the indicators in a chosen topic from the World Bank data, sorted by the strength of relationship.
    Relationship can be either the correlation between the input variable and the chosen indicator(s) or the correlation in the annual percent changes
    
    Parameters
    ----------
    data: A pandas dataframe that contains a column of countries called "Country," a column of years called "Year," and a column of data for a variable
    col: The integer index of the column in which the data of your variable exists in your dataframe
    topic: A character string of the topic name or the integer corresponding to the topic. Topics can be found through the World Bank APIs
    k: An integer indicating the number of variables to return. The k variables with the strongest relationships to the input variable will be returned.
    change: A Boolean value. When set to True, the correlation between the annual percent change of the input variable and the annual percent change of 
        chosen indicator(s) will be found and used to order the strength of relationships
    nlim: An integer indicating the minimum n of indicators to be reported.
    cor_lim: A real number indicating the minimum absolute value of the correlation between the input variable and World Bank indicators to be reported
    t_lim: A real number indicating the minimum t score of the correlation between the input variable and World Bank indicators to be reported.
    
    Returns
    ----------
    Pandas DataFrame
        A Pandas DataFrame containing the indicator names as the index and the correlation between the indicator and the input variable. If change set to True,
            another column including the correlation between the annual percent changes of the variables will be included. The DataFrame is ordered on the
            correlation if change is set to False and on the correlation of percent changes if change is set to True.
            The number of rows in the DataFrame will be, at most, k. The number of columns will depend on the settings of change, nlim, and t_lim.
    
    Examples
    ----------
    >>> import ____
    >>> wb_topic_corrs(my_df,2,1) #Where my_df has columns Country, Year, Data
        | Indicator                                              | Correlation   | n
        ------------------------------------------------------------------------------
        |Access to non-solid fuel, rural (% of rural population) |0.457662       |1519
        |Access to electricity, rural (% of rural population)    |0.457662       |1519
        |Average precipitation in depth (mm per year)            |-0.442344      |353
        |Annual freshwater withdrawals, agriculture (% of total f|-0.429246      |313
        |Livestock production index (2014-2016 = 100)            |0.393510       |1696
        
    >>> wb_topic_corrs(wb.get_series('3.0.Gini',mrv=50).reset_index(),3,'Energy & Mining',change=True,cor_lim=.2) #To check a WB variable against its own or another topic
        | Indicator                                              | Correlation   | n     | Correlation_change | n_change
        ----------------------------------------------------------------------------------------------------------------
        |Access to electricity (% of population)                 |-0.434674      |172    | -0.232096          | 134
        |Access to electricity, urban (% of urban population)    |-0.276086      |172    | -0.225105          | 134
        |Electricity production from coal sources (% of total)   |0.066986       |172    | 0.200032           | 62

    """
    assert type(topic)==int or type(topic)==str, "indicator must be either a string or an integer corresponding to the topic. A list of topics can be found through the World Bank API: http://api.worldbank.org/v2/topic?"
    assert type(col)==int, "col must be the integer index of the column containing data on the variable of interest"
    assert 'Country' in data.columns, "data must have a column containing countries called 'Country'"
    assert 'Year' in data.columns, "data must have a column containing years called 'Year'"
    assert col<data.shape[1], "col must be a column index belonging to data"
    assert type(change)==bool, "change must be a Boolean value (True or False)"
    assert type(k)==int, "k must be an integer"
    assert type(nlim)==int, "n must be an integer"
    assert (type(cor_lim)==float or type(cor_lim)==int), "cor_lim must be a real number"
    assert (type(t_lim)==float or type(t_lim)==int), "n_lim must be a real number"
    
    if topic=='Agricultural & Rural Development' or topic==1:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/1/indicator?per_page=50').content)
    if topic=='Aid Effectiveness'or topic==2:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/2/indicator?per_page=80').content)
    if topic=='Economy & Growth'or topic==3:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/3/indicator?per_page=310').content)
    if topic=='Education'or topic==4:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/4/indicator?per_page=1015').content)
    if topic=='Energy & Mining'or topic==5:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/5/indicator?per_page=55').content)
    if topic=='Environment'or topic==6:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/6/indicator?per_page=145').content)
    if topic=='Financial Sector'or topic==7:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/7/indicator?per_page=210').content)
    if topic=='Health'or topic==8:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/8/indicator?per_page=651').content)
    if topic=='Infrastructure'or topic==9:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/9/indicator?per_page=80').content)
    if topic=='Social Protection & Labor'or topic==10:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/10/indicator?per_page=2150').content)
    if topic=='Poverty'or topic==11:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/11/indicator?per_page=150').content)
    if topic=='Private Sector'or topic==12:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/12/indicator?per_page=200').content)
    if topic=='Public Sector'or topic==13:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/13/indicator?per_page=120').content)
    if topic=='Science & Technology'or topic==14:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/14/indicator?per_page=15').content)
    if topic=='Social Development'or topic==15:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/15/indicator?per_page=35').content)
    if topic=='Urban Development'or topic==16:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/16/indicator?per_page=35').content)
    if topic=='Gender'or topic==17:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/17/indicator?per_page=315').content)
    if topic=='Millenium Development Goals'or topic==18:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/18/indicator?per_page=30').content)
    if topic=='Climate Change'or topic==19:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/19/indicator?per_page=85').content)
    if topic=='External Debt'or topic==20:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/20/indicator?per_page=520').content)
    if topic=='Trade'or topic==21:
        top_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/21/indicator?per_page=160').content)
    cors=[]
    indicators=[]
    n=[]
    t=[]
    if change==False:
        for i in range(0,(len(top_df['id']))):
            try:
                indicator=top_df.loc[i,'id']
                thing=pd.DataFrame(wb.get_series(indicator,mrv=50))
            except:
                pass
            merged=pd.merge(data,thing,how='inner',on=['Country','Year'])
            cor_i=(merged.iloc[:,col].corr(merged.iloc[:,(merged.shape[1]-1)]))
            cors.append(cor_i)
            indicators.append(top_df['{http://www.worldbank.org}name'][i])
            n_i=(len(merged[merged.iloc[:,col].notnull() & merged.iloc[:,(merged.shape[1]-1)].notnull()]))
            n.append(n_i)
            t.append((cor_i*(sqrt((n_i-2)/(1-(cor_i*cor_i))))))
        if t_lim==0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n)),columns=['Indicator','Correlation','n']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n>nlim) & ((almost_there.Correlation>cor_lim) | (almost_there.Correlation<-cor_lim))].head(k)
        if t_lim != 0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n,t)),columns=['Indicator','Correlation','n','t']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n>nlim) & ((almost_there.Correlation>cor_lim) | (almost_there.Correlation<-cor_lim)) & ((almost_there.t>t_lim) | (almost_there.t<-t_lim))].head(k)
    if change==True:
        cors_change=[]
        n_change=[]
        t_change=[]
        mumbo=pd.DataFrame()
        for country in data['Country'].unique():
            s=data[data['Country']==country]
            s.loc[:,'lag_dat']=s.iloc[:,col].shift(-1)
            s.loc[:,'pct_chg_dat']=(((s.iloc[:,col]-s['lag_dat'])/s['lag_dat'])*100)
            mumbo=pd.concat([mumbo,s])
        for i in range(0,(len(top_df['id']))):
            try:
                indicator=top_df.loc[i,'id']
                thing=pd.DataFrame(wb.get_series(indicator,mrv=50))
            except:
                pass
            merged=pd.merge(data,thing,how='inner',on=['Country','Year'])
            cor_i=(merged.iloc[:,col].corr(merged.iloc[:,(merged.shape[1]-1)]))
            cors.append(cor_i)
            n_i=len(merged[merged.iloc[:,col].notnull() & merged.iloc[:,(merged.shape[1]-1)].notnull()])
            n.append(n_i)
            t.append((cor_i*(sqrt((n_i-2)/(1-(cor_i*cor_i))))))
            indicators.append(top_df.loc[i,'{http://www.worldbank.org}name'])
            jumbo=pd.DataFrame()
            thing_df=thing.reset_index()
            for country in thing_df['Country'].unique():
                y=thing_df[thing_df['Country']==country]
                y.loc[:,'lag_ind']=y.iloc[:,3].shift(-1)
                y.loc[:,'pct_chg_ind']=(((y.iloc[:,3]-y['lag_ind'])/y['lag_ind'])*100)
                jumbo=pd.concat([jumbo,y])
            merged_pct=pd.merge(mumbo,jumbo,how='left',on=['Country','Year'])
            cor_chg_i=merged_pct.loc[:,'pct_chg_dat'].corr(merged_pct.loc[:,'pct_chg_ind'])
            cors_change.append(cor_chg_i)
            n_chg_i=len(merged_pct[merged_pct.loc[:,'pct_chg_dat'].notnull() & merged_pct.loc[:,'pct_chg_ind'].notnull()])
            n_change.append(n_chg_i)
            if (cor_chg_i==1 or cor_chg_i==-1):
                t_change.append(None)
            else:
                t_change.append(cor_chg_i*sqrt(((n_chg_i-2)/(1-(cor_chg_i*cor_chg_i)))))
        if t_lim==0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n,cors_change,n_change)),columns=['Indicator','Correlation','n','Correlation_change','n_change']).sort_values(by='Correlation_change',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n_change>nlim) & ((almost_there.Correlation_change>cor_lim) | (almost_there.Correlation_change<-cor_lim))].head(k)
        if t_lim!=0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n,t,cors_change,n_change,t_change)),columns=['Indicator','Correlation','n','t','Correlation_change','n_change','t_change']).sort_values(by='Correlation_change',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n_change>nlim) & ((almost_there.Correlation_change>cor_lim) | (almost_there.Correlation_change<-cor_lim)) & ((almost_there.t_change>t_lim) | (almost_there.t_change<(-t_lim)))].head(k)
    pd.options.mode.chained_assignment = orig_value


def wb_corrs_search(data,col,search,k=5,change=False,nlim=1,cor_lim=0,t_lim=0):
    pd.options.mode.chained_assignment = None
    """
    Returns the relationship that an input variable has with the variables from the World Bank data that match a search, sorted by the strength of relationship
    Relationship can be either the correlation between the input variable and the chosen indicator(s) or the correlation in the annual percent changes
    
    Parameters
    ----------
    data: A pandas dataframe that contains a column of countries called "Country," a column of years called "Year," and a column of data for a variable
    col: The integer index of the column in which the data of your variable exists in your dataframe
    search: The search to conduct. Variables that match the given search will be identified and their relationships with the input variable found.
    k: An integer indicating the number of variables to return. The k variables with the strongest relationship with the input variable will be returned.
    change: A Boolean value. When set to True, the correlation between the annual percent change of the input variable and the annual percent change of 
        chosen indicator(s) will be found and used to order the strength of relationships
    nlim: An integer indicating the minimum n of indicators to be reported.
    cor_lim: A real number indicating the minimum absolute value of the correlation between the input variable and World Bank indicators to be reported
    t_lim: A real number indicating the minimum t score of the correlation between the input variable and World Bank indicators to be reported.
    
    Returns
    ----------
    Pandas DataFrame
        A Pandas DataFrame containing the indicator names as the index and the correlation between the indicator and the input variable. If change set to True,
            another column including the correlation between the annual percent changes of the variables will be included. The DataFrame is ordered on the
            correlation if change is set to False and on the correlation of percent changes if change is set to True.
            The number of rows in the dataframe will be, at most, k. The number of columns will depend on the settings of change, nlim, and t_lim.
            
    Examples
    ----------
    >>> import ____
    >>> wb_corrs_search(my_df,2,"income share") #Where my_df has columns Country, Year, Data
        |Indicator                         | Correlation  | n
        ---------------------------------------------------------
        |Income share held by highest 10%  | -0.994108    | 1741
        |Income share held by highest 20%  | -0.993918    | 1741
        |Income share held by third 20%    | 0.977071     | 1741
        |Income share held by second 20%   | 0.973005     | 1741
        |Income Share of Fifth Quintile    | -0.962370    | 160

    >>> wb_corrs_search(wb.get_series('3.0.Gini',mrv=50).reset_index(),3,"income share",change=True,t_lim=.5)
        |Indicator                       | Correlation  | n    | t         | Correlation_change    | n_change  | t_change
        -------------------------------------------------------------------------------------------------------------
        |Income Share of Fifth Quintile  | 0.991789     |160   |97.479993  |0.983675               |125        |60.623743
        |Income Share of Second Quintile | -0.985993    |160   |-74.309907 |-0.925918              |125        |-27.186186
        |Income Share of Third Quintile  | -0.964258    |160   |-45.744148 |-0.918473              |125        |-25.756680
        |Income share held by highest 20%| 0.970095     |172   |52.110510  |0.872767               |134        |20.542079
        |Income share held by highest 10%| 0.952781     |172   |40.910321  |0.857376               |134        |19.138677
    
    """
    assert type(search)==str, "search must be a character string."
    assert 'Country' in data.columns, "data must have a column containing countries called 'Country'"
    assert 'Year' in data.columns, "data must have a column containing years called 'Year'"
    assert type(col)==int, "col must be an integer of a column index that exists in data"
    assert col<data.shape[1], "col must be a column index belonging to data"
    assert type(change)==bool, "change must be a Boolean value (True or False)"
    assert type(k)==int, "k must be an integer"
    assert type(nlim)==int, "n must be an integer"
    assert (type(cor_lim)==float or type(cor_lim)==int), "cor_lim must be a real number"
    assert (type(t_lim)==float or type(t_lim)==int), "n_lim must be a real number"
    inds=wb.search_indicators(search).reset_index()
    cors=[]
    indicators=[]
    n=[]
    t=[]
    for indic in inds['id']:
        thing=pd.DataFrame(wb.get_series(indic,mrv=50))
        merged=pd.merge(data,thing,how='left',on=['Country','Year'])
        cor_i=merged.iloc[:,col].corr(merged.iloc[:,(merged.shape[1]-1)])
        cors.append(cor_i)
        indicators.append(pd.DataFrame(wb.get_series(indic,mrv=1)).reset_index()['Series'][0])
        n_i=len(merged[merged.iloc[:,col].notnull() & merged.iloc[:,(merged.shape[1]-1)].notnull()])
        n.append(n_i)
        t.append((cor_i*(sqrt((n_i-2)/(1-(cor_i*cor_i))))))
    if change==False:
        if t_lim==0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n)),columns=['Indicator','Correlation','n']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n>nlim) & ((almost_there.Correlation>cor_lim) | (almost_there.Correlation<-cor_lim))].head(k)
        if t_lim!=0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n,t)),columns=['Indicator','Correlation','n','t']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n>nlim) & ((almost_there.Correlation>cor_lim) | (almost_there.Correlation<-cor_lim)) & ((almost_there.t>t_lim) | (almost_there.t<-t_lim))].head(k)
    if change==True:
        cors_chg=[]
        n_change=[]
        t_change=[]
        mumbo=pd.DataFrame()
        for country in data['Country'].unique():
            m=data[data['Country']==country]
            m.loc[:,'lag_dat']=m.iloc[:,col].shift(-1)
            m.loc[:,'pct_chg_dat']=(((m.iloc[:,col]-m['lag_dat'])/m['lag_dat'])*100)
            mumbo=pd.concat([mumbo,m])
        for indic in inds['id']:
            jumbo=pd.DataFrame()
            thing2=pd.DataFrame(wb.get_series(indic,mrv=50)).reset_index()
            for country in thing2['Country'].unique():
                j=thing2[thing2['Country']==country]
                j.loc[:,'lag_ind']=j.iloc[:,3].shift(-1)
                j.loc[:,'pct_chg_ind']=(((j.iloc[:,3]-j['lag_ind'])/j['lag_ind'])*100)
                jumbo=pd.concat([jumbo,j])
            merged_pct=pd.merge(mumbo,jumbo,how='inner',on=['Country','Year'])
            cor_chg_i=merged_pct.loc[:,'pct_chg_dat'].corr(merged_pct.loc[:,'pct_chg_ind'])
            cors_chg.append(cor_chg_i)
            n_chg_i=len(merged_pct[merged_pct.loc[:,'pct_chg_dat'].notnull() & merged_pct.loc[:,'pct_chg_ind'].notnull()])
            n_change.append(n_chg_i)
            if (cor_chg_i==1 or cor_chg_i==-1):
                t_change.append(None)
            else:
                t_change.append(cor_chg_i*sqrt(((n_chg_i-2)/(1-(cor_chg_i*cor_chg_i)))))
        if t_lim==0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n,cors_chg,n_change)),columns=['Indicator','Correlation','n','Correlation_change','n_change']).sort_values(by='Correlation_change',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n_change>nlim) & ((almost_there.Correlation_change>cor_lim) | (almost_there.Correlation_change<-cor_lim))].head(k)
        if t_lim!=0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n,t,cors_chg,n_change,t_change)),columns=['Indicator','Correlation','n','t','Correlation_change','n_change','t_change']).sort_values(by='Correlation_change',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n_change>nlim) & ((almost_there.Correlation_change>cor_lim) | (almost_there.Correlation_change<-cor_lim)) & ((almost_there.t_change>t_lim) | (almost_there.t_change<-t_lim))].head(k)
    pd.options.mode.chained_assignment = orig_value

def wb_every(data,col,k=5,change=False,nlim=1,cor_lim=0,t_lim=0):
    assert 'Country' in data.columns, "data must have a column containing countries called 'Country'"
    assert 'Year' in data.columns, "data must have a column containing years called 'Year'"
    assert type(col)==int, "col must be an integer of a column index that exists in data"
    assert col<data.shape[1], "col must be a column index belonging to data"
    assert type(change)==bool, "change must be a Boolean value (True or False)"
    assert type(k)==int, "k must be an integer"
    assert type(nlim)==int, "n must be an integer"
    assert (type(cor_lim)==float or type(cor_lim)==int), "cor_lim must be a real number"
    assert (type(t_lim)==float or type(t_lim)==int), "n_lim must be a real number"
    pd.options.mode.chained_assignment = None
    here_we_go=pd.read_xml(requests.get('http://api.worldbank.org/v2/indicator?per_page=20100').content)
    cors=[]
    indicators=[]
    n=[]
    t=[]
    for indic in here_we_go['id']:
        try:
            thing=pd.DataFrame(wb.get_series(indic,mrv=50)).reset_index()
        except:
            pass
        merged=pd.merge(data,thing,how='left',on=['Country','Year'])
        n_i=(len(merged[merged.iloc[:,col].notnull() & merged.iloc[:,(merged.shape[1]-1)].notnull()]))
        n.append(n_i)
        cor_i=merged.iloc[:,col].corr(merged.iloc[:,(merged.shape[1]-1)])
        cors.append(cor_i)
        t.append((cor_i*(sqrt((n_i-2)/(1-(cor_i*cor_i))))))
        indicators.append(thing.loc[0,'Series'])
    if change==False:
        if t_lim==0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n)),columns=['Indicator','Correlation','n']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n>nlim) & ((almost_there.Correlation>cor_lim) | (almost_there.Correlation<-cor_lim))].head(k)
        if t_lim != 0:
            almost_there = pd.DataFrame(list(zip(indicators,cors,n,t)),columns=['Indicator','Correlation','n','t']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator')
            return almost_there.loc[(almost_there.n>nlim) & ((almost_there.Correlation>cor_lim) | (almost_there.Correlation<-cor_lim)) & ((almost_there.t>t_lim) | (almost_there.t<-t_lim))].head(k)
    if change==True:
        cors_change=[]
        n_change=[]
        t_change=[]
        mumbo=pd.DataFrame()
        for country in data['Country'].unique():
            s=data[data['Country']==country]
            s.loc[:,'lag_dat']=s.iloc[:,col].shift(-1)
            s.loc[:,'pct_chg_dat']=(((s.iloc[:,col]-s['lag_dat'])/s['lag_dat'])*100)
            mumbo=pd.concat([mumbo,s])
        for indic in here_we_go['id']:
            jumbo=pd.DataFrame()
            try:
                thing=pd.DataFrame(wb.get_series(indic,mrv=50)).reset_index()
            except:
                pass
            for country in thing['Country'].unique():
                t=thing[thing['Country']==country]
                t.loc[:,'lag_ind']=t.iloc[:,3].shift(-1)
                t.loc[:,'pct_chg_ind']=(((t.iloc[:,3]-t['lag_ind'])/t['lag_ind'])*100)
                jumbo=pd.concat([jumbo,t])
            merged_pct=pd.merge(mumbo,jumbo,how='left',on=['Country','Year'])
            cor_chg_i=merged_pct.loc[:,'pct_chg_dat'].corr(merged_pct.loc[:,'pct_chg_ind'])
            cors_change.append(cor_chg_i)
            n_chg_i=len(merged_pct[merged_pct.loc[:,'pct_chg_dat'].notnull() & merged_pct.loc[:,'pct_chg_ind'].notnull()])
            n_change.append(n_chg_i)
            if (cor_chg_i==1 or cor_chg_i==-1):
                t_change.append(None)
            else:
                t_change.append(cor_chg_i*sqrt(((n_chg_i-2)/(1-(cor_chg_i*cor_chg_i)))))
    if t_lim==0:
        almost_there = pd.DataFrame(list(zip(indicators,cors,n,cors_change,n_change)),columns=['Indicator','Correlation','n','Correlation_change','n_change']).sort_values(by='Correlation_change',key=abs,ascending=False).set_index('Indicator')
        return almost_there.loc[(almost_there.n_change>nlim) & ((almost_there.Correlation_change>cor_lim) | (almost_there.Correlation_change<-cor_lim))].head(k)
    if t_lim!=0:
        almost_there = pd.DataFrame(list(zip(indicators,cors,n,t,cors_change,n_change,t_change)),columns=['Indicator','Correlation','n','t','Correlation_change','n_change','t_change']).sort_values(by='Correlation_change',key=abs,ascending=False).set_index('Indicator')
        return almost_there.loc[(almost_there.n_change>nlim) & ((almost_there.Correlation_change>cor_lim) | (almost_there.Correlation_change<-cor_lim)) & ((almost_there.t_change>t_lim) | (almost_there.t_change<(-t_lim)))].head(k)
