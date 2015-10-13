import pandas as pd


def to_df(figure):
    """
    Extracts the data from a Plotly Figure

    Parameters
    ----------
        figure : plotly_figure
            Figure from which data will be 
            extracted
        
        Returns a DataFrame or list of DataFrame
    """
    dfs=[]
    for trace in figure['data']:
        if 'scatter' in trace['type']:
            try:
                if type(trace['x'][0])==float:
                    index=trace['x']
                else:
                    index=pd.to_datetime(trace['x'])
            except:
                index=trace['x']
            if 'marker' in trace:
                d={}
                if 'size' in trace['marker']:
                    size=trace['marker']['size']
                    if type(size)!=list:
                        size=[size]*len(index)
                    d['size']=size
                if 'text' in trace:
                    d['text']=trace['text']
                if 'name' in trace:
                    name=trace['name']
                    if type(name)!=list:
                        name=[name]*len(index)
                    d['categories']=name
                d['y']=trace['y']
                d['x']=trace['x']
                if 'z' in trace:
                    d['z']=trace['z']
                df=pd.DataFrame(d)
            else:
                df=pd.Series(trace['y'],index=index,name=trace['name'])
            dfs.append(df)
        elif trace['type'] in ('heatmap','surface'):
            df=pd.DataFrame(trace['z'].transpose(),index=trace['x'],columns=trace['y'])
            dfs.append(df)
        elif trace['type'] in ('box','histogram'):
            vals=trace['x'] if 'x' in trace else trace['y']
            df=pd.DataFrame({trace['name']:vals})
            dfs.append(df)
    if max(list(map(len,dfs)))==min(list(map(len,dfs))):
        if len(dfs)==1:
            return dfs[0]
        else:
            if type(dfs[0])==pd.core.series.Series:
                return pd.concat(dfs,axis=1)                
            if all(dfs[0].columns==dfs[1].columns):
                    return pd.concat(dfs,axis=0)
            else:
                return pd.concat(dfs,axis=1)
    else:
        try:
            return pd.concat(dfs)
        except:
            return dfs