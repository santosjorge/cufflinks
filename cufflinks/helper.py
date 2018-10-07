import json
import os
from . import utils


def _get_params():
    path=path=os.path.join(os.path.dirname(__file__), '../helper/params.json')
    f=open(path)
    d=json.loads(f.read())
    f.close()
    return d

def _help(figure):
    d=_get_params()
    figure=figure.lower()
    if figure in d['figures']:
        fig={}
        fig['description']=d['figures'][figure].get('description','')
        fig['examples']=d['figures'][figure].get('examples','')
        fig['parameters']={figure:{'params':{}},'all':{'params':{}}}
        for k,v in d['parameters'].items():
            for _ in [figure,'all']:
                if _ in v['applies']:
                    param={}
                    if figure in v['exceptions']:
                        if v['exceptions'][figure]:
                            param['description']=v['exceptions'][figure]
                        else:
                            break
                    else:
                        param['description']=v['description']
                    param['type']=v.get('type','')
                    param['position']=v.get('position','')
                    if 'group' in v:
                        if v['group'] not in fig['parameters'][_]:
                            fig['parameters'][_][v['group']]={}
                        fig['parameters'][_][v['group']][k]=param
                    else:
                        fig['parameters'][_]['params'][k]=param
        return fig
    else:
        raise Exception('Figure {0} was not found'.format(figure.upper()))

def _get_aka(figure):
    d=_get_params()
    if figure in d['figures']:
        return figure
    else:
        aka={}
        for k,v in d['figures'].items():
            if 'aka' in v:
                for _ in d['figures'][k]['aka']:
                    aka[_]=k
        if figure in aka.keys():
            print('Did you mean: "{0}"?\n'.format(aka[figure]))
            return aka[figure]
        else:
            raise Exception('Figure {0} was not found'.format(figure.upper()))


def _printer(figure=None):
    if not figure:
        d=_get_params()
        keys=list(d['figures'].keys())
        keys.sort()
        print("Use 'cufflinks.help(figure)' to see the list of available parameters for the given figure.")
        print("Use 'DataFrame.iplot(kind=figure)' to plot the respective figure")
        print('Figures:')
        for k in keys:
            print('\t{0}'.format(k))
    else:
        figure=_get_aka(figure)
        fig=_help(figure)
        print(figure.upper())
        if type(fig['description'])==str:
            print(fig['description'])
        else:
            for _ in fig['description']:
                print(_)
        print('\n')
        print('Parameters:\n{0}'.format('='*11))  
        def get_tabs(val):
            return ' '*4*val
        def print_params(params,tabs=0):
            _keys = list(params.keys())
            _keys.sort()
            positions={}
            for k,v in params.items():
                if v.get('position',False):
                    positions[k]=(int(v['position']))
            for k,v in positions.items():
                if v==-1:
                    _keys.append(_keys.pop(_keys.index(k)))
                else:
                    _keys.insert(v,_keys.pop(_keys.index(k)))
            for k in _keys:
                v=params[k]
                print("{0}{1} : {2}".format(get_tabs(tabs),k,v['type']))
                if type(v['description'])==str:
                    print("{0}{1}".format(get_tabs(tabs+1),v['description']))
                else:
                    for __ in v['description']:
                        print("{0}{1}".format(get_tabs(tabs+1),__))
        
        # Params
        print_params(fig['parameters'][figure].pop('params'),1)
        print('\n')
        print_params(fig['parameters']['all'].pop('params'),1)
        d=utils.deep_update(fig['parameters'][figure],fig['parameters']['all'])

        for k,v in d.items():
                print('\n{0}{1}'.format(get_tabs(1),k.upper()))
                print_params(v,2)


        if 'examples' in fig:
            print('\nEXAMPLES')
            for _ in fig['examples']:
                print('{0}>> {1}'.format(get_tabs(1),_))