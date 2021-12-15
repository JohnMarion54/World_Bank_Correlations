from World_Bank_Correlations import World_Bank_Correlations

import requests
import pandas as pd
import world_bank_data as wb

def test_wb_corr():
    thing1=wb.get_series('1.0.HCount.1.90usd', mrv=50).reset_index()
    thing2=wb.get_series('3.0.IncShr.q1',mrv=50).reset_index()
    thing3=wb.get_series('3.0.Gini',mrv=50).reset_index()
    merged1=pd.merge(thing1,thing2,how='inner',on=['Country','Year'])
    merged2=pd.merge(thing1,thing3,how='inner',on=['Country','Year'])
    corr1=merged1.loc[:,'1.0.HCount.1.90usd'].corr(merged1.loc[:,'3.0.IncShr.q1'])
    corr2=merged2.loc[:,'1.0.HCount.1.90usd'].corr(merged2.loc[:,'3.0.Gini'])
    assert wb_corr(thing1,3,'3.0.IncShr.q1').loc['Income Share of First Quintile','Correlation']==corr1 #test with only one indicator
    assert wb_corr(thing1,3,['3.0.Gini','3.0.IncShr.q1']).loc['Gini Coefficient','Correlation']==corr2 #test with multiple indicators
    mumbo=pd.DataFrame()
    jumbo=pd.DataFrame()
    tumbo=pd.DataFrame()
    for country in thing1['Country'].unique():
        m=thing1[thing1['Country']==country]
        m.loc[:,'lag1']=m.iloc[:,3].shift(-1)
        m.loc[:,'pct_chg1']=(((m.iloc[:,3]-m.loc[:,'lag1'])/m.loc[:,'lag1'])*100)
        mumbo=pd.concat([mumbo,m])
    for country in thing2['Country'].unique():
        j=thing2[thing2['Country']==country]
        j.loc[:,'lag2']=j.iloc[:,3].shift(-1)
        j.loc[:,'pct_chg2']=(((j.iloc[:,3]-j.loc[:,'lag2'])/j.loc[:,'lag2'])*100)
        jumbo=pd.concat([jumbo,j])
    for country in thing3['Country'].unique():
        t=thing3[thing3['Country']==country]
        t.loc[:,'lag3']=t.iloc[:,3].shift(-1)
        t.loc[:,'pct_chg3']=(((t.iloc[:,3]-t.loc[:,'lag3'])/t.loc[:,'lag3'])*100)
        tumbo=pd.concat([tumbo,t])
    merged_pct1=pd.merge(mumbo,jumbo,how="inner",on=['Country','Year'])
    merged_pct2=pd.merge(mumbo,tumbo,how="inner",on=['Country','Year'])
    corr_chg1=merged_pct1['pct_chg1'].corr(merged_pct1['pct_chg2'])
    corr_chg2=merged_pct2['pct_chg1'].corr(merged_pct2['pct_chg3'])
    assert corr_chg1==wb_corr(thing1,3,'3.0.IncShr.q1',True).loc['Income Share of First Quintile','Correlation_change']
    assert corr_chg2==wb_corr(thing1,3,['3.0.IncShr.q1','3.0.Gini'],True).loc['Gini Coefficient','Correlation_change']    

def test_wb_topic_corrs():
    cors=[]
    indicators=[]
    sample_data=wb.get_series('1.0.HCount.1.90usd', mrv=50).reset_index()
    topic_df=pd.read_xml(requests.get('http://api.worldbank.org/v2/topic/1/indicator?per_page=50').content)
    for i in range(0,len(topic_df)):
        try:
            indicator=topic_df['id'][i]
            thing=pd.DataFrame(wb.get_series(indicator,mrv=50))
        except:
            pass
        merged=pd.merge(sample_data,thing,how='inner',on=['Country','Year'])
        cors.append(merged.iloc[:,3].corr(merged.iloc[:,(merged.shape[1]-1)]))
        indicators.append(topic_df['{http://www.worldbank.org}name'][i])
    result=pd.DataFrame(list(zip(indicators,cors)),columns=['Indicator','Correlation']).sort_values(by='Correlation',key=abs,ascending=False).set_index('Indicator').head(5)
    assert wb_topic_corrs(sample_data,3,1,k=5).iloc[0,0]==result.iloc[0,0]
    highest_corr_check=wb.get_series('SL.AGR.EMPL.MA.ZS', mrv=50).reset_index()
    merged_check=pd.merge(sample_data,highest_corr_check,how='inner',on=['Country','Year'])
    result_corr=merged_check.loc[:,'1.0.HCount.1.90usd'].corr(merged_check.loc[:,'SL.AGR.EMPL.MA.ZS'])
    assert result.iloc[0,0]==result_corr
    mumbo=pd.DataFrame()
    jumbo=pd.DataFrame()
    for country in sample_data['Country'].unique():
        m=sample_data[sample_data['Country']==country]
        m.loc[:,'lag']=m.loc[:,'1.0.HCount.1.90usd'].shift(-1)
        m.loc[:,'pct_chg1']=(((m.loc[:,'1.0.HCount.1.90usd']-m.loc[:,'lag'])/m.loc[:,'lag'])*100)
        mumbo=pd.concat([mumbo,m])
    high_chg_check=wb.get_series('ER.H2O.FWAG.ZS',mrv=50).reset_index()
    for country in high_chg_check['Country'].unique():
        j=high_chg_check[high_chg_check['Country']==country]
        j.loc[:,'lag2']=j.loc[:,'ER.H2O.FWAG.ZS'].shift(-1)
        j.loc[:,'pct_chg2']=(((j.loc[:,'ER.H2O.FWAG.ZS']-j.loc[:,'lag2'])/j.loc[:,'lag2'])*100)
        jumbo=pd.concat([jumbo,j])
    next_check=pd.merge(mumbo,jumbo,how='inner',on=['Country','Year'])
    chg_check_result=next_check.loc[:,'pct_chg1'].corr(next_check.loc[:,'pct_chg2'])
    assert wb_topic_corrs(sample_data,3,1,3,True).iloc[1,2]==chg_check_result

def test_wb_corrs_search():
    sample_data=wb.get_series('3.0.Gini',mrv=50).reset_index()
    inc_share_top=wb.get_series('3.0.IncShr.q5',mrv=50).reset_index()
    merged_test=pd.merge(sample_data,inc_share_top,how='inner',on=['Country','Year'])
    corr_result=merged_test.loc[:,'3.0.Gini'].corr(merged_test.loc[:,'3.0.IncShr.q5'])
    assert wb_corrs_search(sample_data,3,'income share',3).loc['Income Share of Fifth Quintile',"Correlation"]==corr_result
    quint2=wb.get_series('3.0.IncShr.q2',mrv=50).reset_index()
    mumbo=pd.DataFrame()
    jumbo=pd.DataFrame()
    for country in sample_data['Country'].unique():
        m=sample_data[sample_data['Country']==country]
        m.loc[:,'lag_dat']=m.loc[:,'3.0.Gini'].shift(-1)
        m.loc[:,'pct_chg_dat']=(((m.loc[:,'3.0.Gini']-m['lag_dat'])/m['lag_dat'])*100)
        mumbo=pd.concat([mumbo,m])
    for country in quint2['Country'].unique():
        j=quint2[quint2['Country']==country]
        j.loc[:,'lag_ind']=j.loc[:,'3.0.IncShr.q2'].shift(-1)
        j.loc[:,'pct_chg_ind']=(((j.loc[:,'3.0.IncShr.q2']-j['lag_ind'])/j['lag_ind'])*100)
        jumbo=pd.concat([jumbo,j])
    merged_pct_test=pd.merge(mumbo,jumbo,how='inner',on=['Country','Year'])
    change_cor_result=merged_pct_test.loc[:,'pct_chg_dat'].corr(merged_pct_test.loc[:,'pct_chg_ind'])
    assert wb_corrs_search(sample_data,3,'income share',3,True).loc['Income Share of Second Quintile','Correlation_change']==change_cor_result, "ouchie"

