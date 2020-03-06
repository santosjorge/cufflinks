THEMES = {
		'ggplot' : {
			'colorscale':'ggplot',
			'linewidth':1.3,
			'linecolor':'pearl',
			'bargap' : .01,
			'layout' : {
				'legend' : {'bgcolor':'white','font':{'color':'grey10'}},
				'paper_bgcolor' : 'white',
				'plot_bgcolor' : 'grey14',
				"title" : {"font":{"color":"charcoal"},"x":0.5},
				'yaxis' : {
					'tickfont' : {'color':'grey10'},
					'gridcolor' : 'lightivory',
					'titlefont' : {'color':'grey10'},
					'zerolinecolor' : 'lightivory',
					'showgrid' : True
				},
				'xaxis' : {
					'tickfont' : {'color':'grey10'},
					'gridcolor' : 'lightivory',
					'titlefont' : {'color':'grey10'},
					'zerolinecolor' : 'lightivory',
					'showgrid' : True
				},
				'titlefont' : {'color':'charcoal'}
			},
			'annotations' : {
				'fontcolor' : 'grey10',
				'arrowcolor' : 'grey10'
			}

		},
		'pearl' : {
			'colorscale':'original',
			'linewidth':1.3,
			'bargap' : .01,
			'layout' : {
				'legend' : {'bgcolor':'pearl02','font':{'color':'pearl06'}},
				'paper_bgcolor' : 'pearl02',
				'plot_bgcolor' : 'pearl02',
				"title" : {"font":{"color":"pearl06"},"x":0.5},
				'yaxis' : {
					'tickfont' : {'color':'pearl06'},
					'gridcolor' : 'pearl03',
					'titlefont' : {'color':'pearl06'},
					'zerolinecolor' : 'pearl03',
					'showgrid' : True
				},
				'xaxis' : {
					'tickfont' : {'color':'pearl06'},
					'gridcolor' : 'pearl03',
					'titlefont' : {'color':'pearl06'},
					'zerolinecolor' : 'pearl03',
					'showgrid' : True
				},
				'titlefont' : {'color':'pearl06'}
			},
			'annotations' : {
				'fontcolor' : 'pearl06',
				'arrowcolor' : 'pearl04'
			},
			'3d' : {
				'yaxis' : {
					'gridcolor' : 'pearl04',
					'zerolinecolor'  : 'pearl04'
				},
				'xaxis' : {
					'gridcolor' : 'pearl04',
					'zerolinecolor'  : 'pearl04'
				}
			}
		},
		'solar' : {
			'colorscale':'original',
			'linewidth':1.3,
			'bargap' : .01,
			'layout' : {
				'legend' : {'bgcolor':'charcoal','font':{'color':'pearl'}},
				"title" : {"font":{"color":"white"},"x":0.5},
				'paper_bgcolor' : 'charcoal',
				'plot_bgcolor' : 'charcoal',
				'yaxis' : {
					'tickfont' : {'color':'grey12'},
					'gridcolor' : 'grey08',
					'titlefont' : {'color':'pearl'},
					'zerolinecolor' : 'grey09',
					'showgrid' : True
				},
				'xaxis' : {
					'tickfont' : {'color':'grey12'},
					'gridcolor' : 'grey08',
					'titlefont' : {'color':'pearl'},
					'zerolinecolor' : 'grey09',
					'showgrid' : True
				},
				'titlefont' : {'color':'pearl'}
			},
			'annotations' : {
				'fontcolor' : 'pearl',
				'arrowcolor' : 'grey11'
			}
		},
		'space' : {
			'colorscale':'original',
			'linewidth':1.3,
			'bargap' : .01,
			'layout' : {
				'legend' : {'bgcolor':'grey03','font':{'color':'pearl'}},
				'paper_bgcolor' : 'grey03',
				'plot_bgcolor' : 'grey03',
				"title" : {"font":{"color":"pearl"},"x":0.5},
				'yaxis' : {
					'tickfont' : {'color':'grey12'},
					'gridcolor' : 'grey08',
					'titlefont' : {'color':'pearl'},
					'zerolinecolor' : 'grey09',
					'showgrid' : True
				},
				'xaxis' : {
					'tickfont' : {'color':'grey12'},
					'gridcolor' : 'grey08',
					'titlefont' : {'color':'pearl'},
					'zerolinecolor' : 'grey09',
					'showgrid' : True
				},
				'titlefont' : {'color':'pearl'}
			},
			'annotations' : {
				'fontcolor' : 'pearl',
				'arrowcolor' : 'red'
			}
		},
		'white' : {
			'colorscale':'original',
			'linewidth':1.3,
			'bargap' : .01,
			'layout' : {
				'legend' : {'bgcolor':'white','font':{'color':'pearl06'}},
				'paper_bgcolor' : 'white',
				'plot_bgcolor' : 'white',
				"title" : {"font":{"color":"pearl06"},"x":0.5},
				'yaxis' : {
					'tickfont' : {'color':'pearl06'},
					'gridcolor' : 'pearl03',
					'titlefont' : {'color':'pearl06'},
					'zerolinecolor' : 'pearl03',
					'showgrid' : True
				},
				'xaxis' : {
					'tickfont' : {'color':'pearl06'},
					'gridcolor' : 'pearl03',
					'titlefont' : {'color':'pearl06'},
					'zerolinecolor' : 'pearl03',
					'showgrid' : True
				},
				'titlefont' : {'color':'pearl06'}
			},
			'annotations' : {
				'fontcolor' : 'pearl06',
				'arrowcolor' : 'pearl04'
			},
			'3d' : {
				'yaxis' : {
					'gridcolor' : 'pearl04',
					'zerolinecolor'  : 'pearl04'
				},
				'xaxis' : {
					'gridcolor' : 'pearl04',
					'zerolinecolor'  : 'pearl04'
				}
			}
		},
		'polar' : {
			'colorscale':'polar',
			'linewidth':1.3,
			'bargap' : .01,
			'layout' : {
				'legend' : {'bgcolor':'polardust','font':{'color':'polargrey'}},
				'paper_bgcolor' : 'polardust',
				'plot_bgcolor' : 'polardust',
				"title" : {"font":{"color":"polardark"},"x":0.5},
				'yaxis' : {
					'tickfont' : {'color':'polargrey'},
					'gridcolor' : 'pearl03',
					'titlefont' : {'color':'polargrey'},
					'zerolinecolor' : 'pearl03',
					'showgrid' : True
				},
				'xaxis' : {
					'tickfont' : {'color':'polargrey'},
					'gridcolor' : 'pearl03',
					'titlefont' : {'color':'polargrey'},
					'zerolinecolor' : 'pearl03',
					'showgrid' : True
				},
				'titlefont' : {'color':'polardark'}
			},
			'annotations' : {
				'fontcolor' : 'polardark',
				'arrowcolor' : 'pearl04'
			},
			'3d' : {
				'yaxis' : {
					'gridcolor' : 'pearl04',
					'zerolinecolor'  : 'pearl04'
				},
				'xaxis' : {
					'gridcolor' : 'pearl04',
					'zerolinecolor'  : 'pearl04'
				}
			}
		},
		'henanigans' : {
			'colorscale':'original',
			'linewidth':1.3,
			'bargap' : .01,
			'layout' : {
				'legend' : {'bgcolor':'henanigans_bg','font':{'color':'henanigans_light2'}},
				'paper_bgcolor' : 'henanigans_bg',
				'plot_bgcolor' : 'henanigans_bg',
				"title" : {"font":{"color":"henanigans_light2"},"x":0.5},
				'yaxis' : {
					'tickfont' : {'color':'henanigans_light1'},
					'gridcolor' : 'henanigans_grey1',
					'titlefont' : {'color':'henanigans_light1'},
					'zerolinecolor' : 'henanigans_grey2',
					'showgrid' : True
				},
				'xaxis' : {
					'tickfont' : {'color':'henanigans_light1'},
					'gridcolor' : 'henanigans_grey1',
					'titlefont' : {'color':'henanigans_light1'},
					'zerolinecolor' : 'henanigans_grey2',
					'showgrid' : True
				},
				'titlefont' : {'color':'henanigans_light2'}
			},
			'annotations' : {
				'fontcolor' : 'henanigans_orange2',
				'arrowcolor' : 'henanigans_orange2'
			},
			'3d' : {
				'yaxis' : {
					'gridcolor' : 'henanigans_grey1',
					'zerolinecolor'  : 'henanigans_grey1'
				},
				'xaxis' : {
					'gridcolor' : 'henanigans_grey1',
					'zerolinecolor'  : 'henanigans_grey1'
				}
			}
		}
	}



