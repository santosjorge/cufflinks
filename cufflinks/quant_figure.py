
from __future__ import absolute_import

import json
import copy
import pandas as pd

from . import tools
from . import ta
from . import utils
from . import colors
from . import auth
from . import date_tools

def get_layout_kwargs():
    return tools.__LAYOUT_KWARGS
def get_annotation_kwargs():
    return tools.__ANN_KWARGS
def get_shapes_kwargs():
    return tools.__SHAPES_KWARGS

class QuantFig(object):
    
    def __init__(self,df,kind='candlestick',columns=None,**kwargs):
        self.df=df
        self.studies={}
        self.data={}
        self.theme={}
        self.panels={}
        self.layout={}
        self.trendlines=[]

        self._d=ta._ohlc_dict(df,columns=columns)
        
        annotations={
            'values':[],
            'params':utils.check_kwargs(kwargs,get_annotation_kwargs(),{},clean_origin=True)
        }
        ann_values=kwargs.pop('annotations',None)
        if ann_values:
            if type(ann_values)==list:
                annotations['values'].extend(ann_values)
            else:
                annotations['values'].append(ann_values)

        self.data.update(showlegend=kwargs.pop('datalegend',True),name=kwargs.pop('name','Trace 1'),kind=kind)
        # self.data.update(resample=None,slice=None)

        self.layout['shapes']=utils.check_kwargs(kwargs,get_shapes_kwargs(),{},clean_origin=True)
        for k,v in list(self.layout['shapes'].items()):
            if not isinstance(v,list):
                self.layout['shapes'][k]=[v]
        self.layout['rangeselector']=kwargs.pop('rangeselector',{'visible':False})
        self.layout['rangeslider']=kwargs.pop('rangeslider',False) 
        self.layout['margin']=kwargs.pop('margin',dict(t=40,b=40,r=40,l=40))
        self.layout['annotations']=annotations
        self.layout['showlegend']=kwargs.pop('showlegend',True)
        self.layout.update(utils.check_kwargs(kwargs,get_layout_kwargs(),{},clean_origin=True))
        
        self.theme['theme']=kwargs.pop('theme',auth.get_config_file()['theme'])
        self.theme['up_color']=kwargs.pop('up_color','java')
        self.theme['down_color']=kwargs.pop('down_color','grey')
        
        
        self.panels['min_panel_size']=kwargs.pop('min_panel_size',.15)
        self.panels['spacing']=kwargs.pop('spacing',.08)
        self.panels['top_margin']=kwargs.pop('top_margin',0.9)
        self.panels['bottom_margin']=kwargs.pop('top_margin',0)
        self.kwargs=kwargs

    # @property
    # def df(self):
    #     d=self._df.copy()
    #     resample=self.data.get('resample',None)
    #     slice=self.data.get('slice',None)
    #     if slice:
    #         d=eval('d.ix[{0}]'.format(slice))
    #     if resample:
    #         pass    

    #     return self._df

    def update(self,**kwargs):
        if 'annotations' in kwargs:
            self.layout['annotations'].update(kwargs.pop('annotations'))
        else:
            pass
    
    def figure(self,**kwargs):
        kwargs['asFigure']=True
        return self.iplot(**kwargs)
    
    def panel_domains(self,n=2,min_panel_size=.15,spacing=0.08,top_margin=1,bottom_margin=0):
        d={}
        for _ in range(n+1,1,-1):
            lower=round(bottom_margin+(min_panel_size+spacing)*(n+1-_),2)
            d['yaxis{0}'.format(_)]=dict(domain=(lower,lower+min_panel_size))
        top=d['yaxis2']['domain']
        d['yaxis2']['domain']=(top[0],top_margin)
        return d
    
    def _get_trendline(self,date0=None,date1=None,on=None,kind='trend',to_strftm='%Y-%m-%d',from_strfmt='%d%b%y',**kwargs):
        
        ann_values=copy.deepcopy(get_annotation_kwargs())
        ann_values.extend(['x','y'])
        ann_kwargs=utils.check_kwargs(kwargs,ann_values,{},clean_origin=True)
        def position(d0,d1):
            return d0+(d1-d0)/2

        date0=kwargs.pop('date',date0)    
        date0=date_tools.stringToString(date0,from_strfmt,to_strftm) if '-' not in date0 else date0
        
        if kind=='trend':
            date1=date_tools.stringToString(date1,from_strfmt,to_strftm) if '-' not in date1 else date1
            on='close' if not on else on
            df=pd.DataFrame(self.df[self._d[on]])
            y0=kwargs.get('y0',df.ix[date0].values[0])
            y1=kwargs.get('y1',df.ix[date1].values[0])
            
        
        if kind in ('support','resistance'):
            mode=kwargs.pop('mode','starttoend')
            if not on:
                on='low' if kind=='support' else 'high'
            df=pd.DataFrame(self.df[self._d[on]])
            y0=kwargs.get('y0',df.ix[date0].values[0])
            y1=kwargs.get('y1',y0)
            if mode=='starttoend':
                date0=df.index[0]
                date1=df.index[-1]
            elif mode=='toend':
                date1=df.index[-1]
            elif mode=='fromstart':
                date1=date0
                date0=df.index[0]

        if isinstance(date0,pd.tslib.Timestamp):
            date0=date_tools.dateToString(date0,to_strftm)
        if isinstance(date1,pd.tslib.Timestamp):
            date1=date_tools.dateToString(date1,to_strftm)
        d={'x0':date0,'x1':date1,'y0':y0,'y1':y1}
        d.update(**kwargs)
        shape=tools.get_shape(**d)        

        
        if ann_kwargs.get('text',False):
            ann_kwargs['x']=ann_kwargs.get('x',date_tools.dateToString(position(date_tools.stringToDate(date0,to_strftm),date_tools.stringToDate(date1,to_strftm)),to_strftm))
            ann_kwargs['y']=ann_kwargs.get('y',position(shape['y0'],shape['y1']))
        else:
            ann_kwargs={}
        return {'shape':shape,'annotation':ann_kwargs}

    def add_trendline(self,date0,date1,on='close',text=None,**kwargs):
        d={'kind':'trend','date0':date0,'date1':date1,'on':on,'text':text}
        d.update(**kwargs)
        self.trendlines.append(d)

    def add_support(self,date,on='low',mode='starttoend',text=None,**kwargs):
        d={'kind':'support','date':date,'mode':mode,'on':on,'text':text}
        d.update(**kwargs)
        self.trendlines.append(d)

    def add_resistance(self,date,on='high',mode='starttoend',text=None,**kwargs):
        d={'kind':'resistance','date':date,'mode':mode,'on':on,'text':text}
        d.update(**kwargs)
        self.trendlines.append(d)

    def add_annotations(self,annotations,**kwargs):
        ann_kwargs=utils.check_kwargs(kwargs,get_annotation_kwargs(),{},clean_origin=True)
        if type(annotations)==list:
            self.layout['annotations']['values'].extend(annotations)
        else:
            self.layout['annotations']['values'].append(annotations)
        if ann_kwargs:
            self.layout['annotations']['params'].update(**ann_kwargs)

    def add_shapes(self,**kwargs):
        kwargs=utils.check_kwargs(kwargs,get_shapes_kwargs(),{},clean_origin=True)
        for k,v in list(kwargs.items()):
            if k in self.layout['shapes']:
                self.layout['shapes'][k].append(v)
            else:
                self.layout['shapes'][k]=[v]

    def add_study(self,name,params={}):
        if 'kind' in params:
                if params['kind'] in self._valid_studies:
                    self.studies[name]=params
                else:
                    raise Exception('Invalid study: {0}'.format(params['kind']))
        else:
            raise Exception('Study kind required')

    def _add_study(self,study):
        name=study['name']
        if not name:
            d={'boll':'Bollinger Bands',
               'rsi':'RSI',
               'sma':'SMA({periods})',
               'volume':'volume',
               'macd':'MACD'}
            _study_name=d[study['kind']]
            study['name']=_study_name.format(periods=study['params'].get('periods',''))
                
        if study['kind'] in self.studies:
            id='{0} ({1})'.format(study['kind'],study['params']['periods'])
        else:
            id=study['kind']

        _id=id
        n=1
        while id in self.studies:
            id='{0} ({1})'.format(_id,n)
            n+=1
        self.studies[id]=study
       
    def add_volume(self,colorchange=True,column=None,name='',**kwargs):
        if not column:
            column=self._d['volume']
        up_color=kwargs.pop('up_color',self.theme['up_color'])
        down_color=kwargs.pop('down_color',self.theme['down_color'])
        study={'kind':'volume',
               'name':name,
               'params':{'changecolor':True,'base':'close','column':column,
                         'str':None},
              'display':utils.merge_dict({'up_color':up_color,'down_color':down_color},kwargs)}
        self._add_study(study)

    def add_macd(self,fast_period=12,slow_period=26,signal_period=9,column=None,
                 str=None,name='',**kwargs):
        if not column:
            column=self._d['close']
        study={'kind':'macd',
               'name':name,
               'params':{'fast_period':fast_period,'slow_period':slow_period,
                         'signal_period':signal_period,'column':column,
                         'str':str},
              'display':utils.merge_dict({'legendgroup':True},kwargs)}
        self._add_study(study)

    
    def add_sma(self,periods=20,column=None,str=None,
                           name='',**kwargs):
        if not column:
            column=self._d['close']
        study={'kind':'sma',
               'name':name,
               'params':{'periods':periods,'column':column,
                         'str':str},
              'display':utils.merge_dict({'legendgroup':False},kwargs)}
        self._add_study(study)
        
    def add_rsi(self,periods=20,rsi_upper=70,rsi_lower=30,showbands=True,column=None,str=None,
                           name='',**kwargs):
        if not column:
            column=self._d['close']
        study={'kind':'rsi',
               'name':name,
               'params':{'periods':periods,'column':column,
                         'str':str},
              'display':utils.merge_dict({'legendgroup':True,'rsi_upper':rsi_upper,
                         'rsi_lower':rsi_lower,'showbands':showbands},kwargs)}
        self._add_study(study)
    
    def add_bollinger_bands(self,periods=20,boll_std=2,column=None,str=None,fill=True,
                           name='',**kwargs):
        if not column:
            column=self._d['close']
        study={'kind':'boll',
               'name':name,
               'params':{'periods':periods,'boll_std':boll_std,'column':column,
                        'str':str},
              'display':utils.merge_dict({'legendgroup':True,'fill':fill},kwargs)}
        self._add_study(study)

    def add_ema(self):
        pass

    def add_cmci(self):
        pass

    def add_trender(self):
        pass

    def add_dmi(self):
        pass

    def add_ptps(self):
        pass

    def add_stochastic(self):
        pass
            
    def _get_study_figure(self,study_id,**kwargs):
        study=copy.deepcopy(self.studies[study_id])
        kind=study['kind']
        display=study['display']
        display['theme']=display.get('theme',self.theme['theme'])
        params=study['params']
        name=study['name']
        params.update(include=False)
        local_kwargs={}

        
        def get_params(locals_list,params,display,append_study=True):
            locals_list.append('legendgroup')
            local_kwargs=utils.check_kwargs(display,locals_list,{},True)
            display.update(kwargs)
            if append_study:
                display=dict([('study_'+k,v) for k,v in display.items()])
            params.update(display)
            return local_kwargs,params
 
        if kind=='volume':
            bar_colors=[]
            local_kwargs,params=get_params([],params,display,False)
            base=self.df[self._d[params['base']]]
            up_color=colors.normalize(display['up_color']) if 'rgba' not in display['up_color'] else display['up_color']
            down_color=colors.normalize(display['down_color']) if 'rgba' not in display['down_color'] else display['down_color']
            
            for i in range(len(base)):
                if i != 0:
                    if base[i] > base[i-1]:
                        bar_colors.append(up_color)
                    else:
                        bar_colors.append(down_color)
                else:
                    bar_colors.append(down_color)
            fig=self.df[params['column']].figure(kind='bar',theme=params['theme'])
            fig.data[0].update(marker=dict(color=bar_colors,line=dict(color=bar_colors)),
                      opacity=0.8)

        if kind=='sma':
            local_kwargs,params=get_params([],params,display)
            fig=self.df.ta_figure(study=kind,**params)

        if kind=='boll':
            local_kwargs,params=get_params(['fill','fillcolor'],params,display)
            fig=self.df.ta_figure(study=kind,**params)
            if local_kwargs['fill']:
                fillcolor=local_kwargs.pop('fillcolor',fig.data[2].line.get('color','rgba(200,200,200,.1)'))
                fillcolor=colors.to_rgba(fillcolor,.1)
                fig.data[2].update(fill='tonexty',fillcolor=fillcolor)
        
        if kind=='rsi':
            locals_list=['rsi_lower','rsi_upper','showbands']
            local_kwargs,params=get_params(locals_list,params,display)
            fig=self.df.ta_figure(study=kind,**params)
            del fig.layout['shapes']
            if local_kwargs['showbands']:
            	up_color=kwargs.get('up_color',self.theme['up_color'])
            	down_color=kwargs.get('down_color',self.theme['down_color'])
                for _ in ('rsi_lower','rsi_upper'):
                    trace=fig.data[0].copy()
                    trace.update(y=[local_kwargs[_] for x in trace['x']])
                    trace.update(name='')
                    color=down_color if 'lower' in _ else up_color
                    trace.update(line=dict(color=color,width=1))
                    fig.data.append(trace)
        
        if kind=='macd':
            local_kwargs,params=get_params([],params,display)
            fig=self.df.ta_figure(study=kind,**params)

        if local_kwargs.get('legendgroup',False):
            fig.update_traces(legendgroup=name,showlegend=False)
            fig.data[0].update(showlegend=True,name=name)
        
        return fig
    
    def iplot(self,**kwargs):
        
        asFigure=kwargs.pop('asFigure',False)
        showstudies=kwargs.pop('showstudies',True)
        study_kwargs=utils.kwargs_from_keyword(kwargs,{},'study',True)
        datalegend=kwargs.pop('datalegend',self.data.get('showlegend',True))
        panel_data={}
        for k in ['min_panel_size','spacing','top_margin','bottom_margin']:
            panel_data[k]=kwargs.pop(k,self.panels[k])

        d=self.kwargs
        layout=copy.deepcopy(self.layout)
        annotations=layout.pop('annotations')
        shapes=layout.pop('shapes')
        if not 'shapes' in shapes:
            shapes['shapes']=[]
        for trend in self.trendlines:
            _trend=self._get_trendline(**trend)
            shapes['shapes'].append(_trend['shape'])
            if 'text' in _trend['annotation']:
                annotations['values'].append(_trend['annotation'])
        shape_kwargs=utils.check_kwargs(kwargs,get_shapes_kwargs(),{},clean_origin=True)
        for k,v in list(shape_kwargs.items()):
            if k in shapes:
                shapes[k].append(v)
            else:
                shapes[k]=[v]
        for _ in [self.data,layout,
                  self.theme,{'annotations':annotations['values']},
                  annotations['params'],shapes]:
            if _:
                d=utils.merge_dict(d,_)
        d=utils.deep_update(d,kwargs)
        d=tools.updateColors(d)
        fig=self.df.figure(**d)
        if d['kind'] not in ('candle','candlestick','ohlc'):
            fig.move_axis(yaxis='y2')
        else:
            if not datalegend:
                fig.data[0]['decreasing'].update(showlegend=False)
                fig.data[0]['increasing'].update(showlegend=False)
        panel_data['n']=1
        which=fig.axis['which']['y']
        which.sort()
        max_panel=int(which[-1][1:])
        figures=[]
        if showstudies:
            kwargs=utils.check_kwargs(kwargs,['theme','up_color','down_color'],{},False)
            kwargs.update(**study_kwargs)
            for k,v in list(self.studies.items()):
                study_fig=self._get_study_figure(k,**kwargs)
                if v['kind'] in ('boll','sma'):
                    study_fig.move_axis(yaxis='y2')                
                if v['kind'] in ('rsi','volume','macd'):
                    max_panel+=1
                    panel_data['n']+=1
                    study_fig.move_axis(yaxis='y{0}'.format(max_panel))
                figures.append(study_fig)
            figures.append(fig)
            fig=tools.merge_figures(figures)
            fig['layout']['xaxis1']['anchor']='y2'
        domains=self.panel_domains(**panel_data)
        fig.layout.update(**domains)
        if not d.get('rangeslider',False):
	        try:
	            del fig['layout']['yaxis1']
	        except:
	            pass
        if asFigure:
            return fig
        else:
            return fig.iplot()
    
    def __getitem__(self,key):
            return self.__dict__[key]
        
    def __repr__(self):
        _d=self.__dict__.copy()
        del _d['df']
        print(json.dumps(_d,sort_keys=True, indent=4))
        return ''