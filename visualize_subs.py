import json
import os
import json
import math
import circlify
import random
import cyto as cy
from collections import Counter
from dash import html,  dcc, Input, Output, State, no_update, callback, ALL, ctx
import heapq
from textblob import TextBlob
import dash_bootstrap_components as dbc
import datetime

start_date = datetime.datetime(2023, 4, 1) #first crawling
end_date = datetime.datetime.now()
daterange = []
start_ts = start_date.timestamp()
end_ts = end_date.timestamp()
inc = start_date
while len(daterange)<9:
    inc += datetime.timedelta(days=(end_date - start_date).days / 10)
    daterange.append(inc)

tsmarks = {int(dates.timestamp()) : {'label': dates.strftime('%b.'), 'style': {'color': 'white'}} for dates in daterange}
tsmarks[int(start_ts)] = {'label': start_date.strftime('%Y'), 'style': {'color': 'white'}}
tsmarks[int(end_ts)] = {'label': end_date.strftime('%Y'), 'style': {'color': 'white'}}

filters = [
        html.Div([
            "Show Top",
            dcc.Input(20, id='number_problems', type='number', min = 5, max = 100, step=1, className='bg-zinc-700 hover:bg-zinc-600 font-semibold px-1 py-0 rounded-md w-1/6'),
            "Problems"
        ],className = 'flex flex-row gap-1'),
        html.Div([
            html.Div("Weights for Rank:"),
            dcc.Input(1, id='weight_upvotes', type='number', min = -10, max = 10, step=0.1, className='bg-zinc-700 hover:bg-zinc-600 font-semibold px-1 py-0 rounded-md w-1/6'),
            html.Img(src = 'assets/upvote.png', className = 'h-4 w-4 aspect-square shrink-0 grow-0'),
            dcc.Input(0.2, id='weight_comments', type='number', min = -10, max = 10, step=0.1, className='bg-zinc-700 hover:bg-zinc-600 font-semibold px-1 py-0 rounded-md w-1/6'),
            html.Img(src = 'assets/comment.png', className = 'h-4 w-4 aspect-square shrink-0 grow-0'),
        ],className = 'flex flex-row gap-2' ),
        html.Div([
        html.Div("Post created at:"),
            dcc.RangeSlider(
            start_ts, end_ts,
            value=[(end_ts-start_ts)/6+start_ts, (end_ts-start_ts)*10/12+start_ts],
            marks = tsmarks,
            updatemode = 'drag',
            id='ts_slider',
            className = 'w-full',
            allowCross = False),
        ], className = 'flex flex-row gap-1' )
]
filters_modal = dbc.Modal([

                    dbc.ModalHeader("Filters for Posts", className = 'flex flex-row gap-2 font-bold text-xl'),
                    dbc.ModalBody(filters, className = 'flex flex-col gap-4'),
                    dbc.ModalFooter("Filters will be applied on next 'View Problems'")
                ], className = 'text-white font-semibold',
            id="filter_modal",
            is_open=False
                )
                
subs_layout = html.Div([
    filters_modal,
    dcc.Store(id = 'colors_data'),
    cy.communities_network,
    html.Div([
        html.Button("View Problems", id= 'view_problems', className = 'rounded-md px-2 py-2 border-2 border-red-600 bg-red-200 text-zinc-800 font-semibold h-12'),
        html.Button("Filters", id = 'filters', className = 'rounded-md px-2 py-2 bg-zinc-700 text-white font-semibold h-12')
    ], className = 'flex flex-row gap-4 w-full justify-center')
])

def get_colors(leaves):
    children = ["Colors:"]
    colors_data = {}
    for i, leaf in enumerate(leaves):
        color = cy.palette[i][random.randint(0,38)]
        children.append(html.Div([
            html.Div(style = {'backgroundColor': color}, className = 'h-2 w-2 mt-1 rounded-md aspect-square'),
            html.Div(leaf)
        ], className = 'flex flex-row gap-2'))
        colors_data[leaf] = color
    return children, colors_data

def get_community_elements(nodes):
    ids, sizes = zip(*nodes)

    max_size = max(sizes)
    min_size = min(sizes)
    
    # Compute circle positions 
    circles = circlify.circlify(
        sizes, 
        show_enclosure=False, 
        target_enclosure=circlify.Circle(x=0, y=0, r=1)
    )

    circles = circles[::-1]

    elements = []
    for i, (node_id, circle) in enumerate(zip(ids, circles)):
        relative_size = (sizes[i]-min_size)/(max_size-min_size)
        elements.append({
            'data': {
                'id': node_id,
                'label': node_id,
                'color': cy.color_palette_red_white[39-round(relative_size*39)],
                'size': f"{math.ceil(circle.r * 100)}px",
                'font': f"{math.ceil(circle.r * 10)}px"
            },
            'position': {
                'x': circle.x * 50,
                'y': circle.y * 50
            }
        })
    
    return elements

def get_filtered_problems(data, top, weight_upvotes, weight_comments, timeframe):
    date_format = "%Y-%m-%d"

    def is_in_timeframe(post):
        try:
            time = datetime.datetime.strptime(post[3].split("T")[0], date_format).timestamp()
        except Exception as e:
            print(e)
            return False
        return time >= timeframe[0] and time <= timeframe[1]
        
    data = list(filter(is_in_timeframe, data))

    top_problems = heapq.nlargest(top, data, key=lambda x: int(x[2])*weight_upvotes + int(x[1])*weight_comments)
    return top_problems

def get_problem_cards(filtered_problems):

    def determine_color(text):
        num_colors = len(cy.color_sentiment)
        polarity = TextBlob(text).sentiment.polarity
        index = round((polarity + 1) * (num_colors - 1) / 2)
        return cy.color_sentiment[index]


    children = [
        html.Div(
            p[0],
            title = "".join((p[0], " : ", p[4].split("com")[1])),
            id = {'type': 'post', 'rank': i},
            className = 'w-11/12 h-10 cursor-pointer rounded-md flex items-center justify-start mx-2 whitespace-nowrap truncate',
            style =  {'backgroundColor': determine_color(p[5])}
        )
        for i, p in enumerate(filtered_problems)
    ]

    return children

@callback(
    Output('communities_network', 'elements'),
    Output('selected_categories', 'data'),
    Input('view_subreddits', 'n_clicks'),
    State('categories_selection_dropdown', 'value'),
    prevent_initial_call = True
)
def put_elements(n, leaves):
    if not n:
        return no_update, no_update
    all_subs = []
    
    for category in leaves:
        try:
            with open(f'problems/{category.replace(" ", "_")}.json', 'r') as file:
                category_problems = json.load(file)
        except Exception as e:
            print(e)
        
        all_subs.extend([problem[4].split("/")[4] for problem in category_problems])
    
    counter = Counter(all_subs)
    nodes = sorted([(sid, count) for sid, count in list(counter.items()) if count>1], key=lambda x: x[1], reverse=True)
    
    return get_community_elements(nodes), leaves


@callback(
    Output('top_posts', 'children'),
    Output('top_posts_data', 'data'),
    Output('colors', 'children'),
    Output('colors_data', 'data'),
    Output('problems_network', 'stylesheet'),
    Input('view_problems', 'n_clicks'),
    State('selected_categories', 'data'),
    State('communities_network', 'selectedNodeData'),
    State('communities_network', 'elements'),
    State('number_problems', 'value'),
    State('weight_upvotes', 'value'),
    State('weight_comments', 'value'),
    State('ts_slider', 'value'),
    prevent_initial_call = True
)
def show_problems(n, leaves, sND, elements, number_problems, weight_upvotes, weight_comments, ts_value):
    if not n:
        return no_update
    
    if not sND:
        sND = [e['data'] for e in elements if 'position' in e]
    selected_subreddits = set(sN['id'] for sN in sND)

    all_problems = []
    for category in leaves:
        try:
            with open(f'problems/{category.replace(" ", "_")}.json', 'r') as file:
                category_problems = json.load(file)
        except Exception as e:
            print(e)
        if len(sND)>0:
            all_problems.extend([cp + [category] for cp in category_problems if cp[4].split("/")[4] in selected_subreddits])
        else:
            all_problems.extend(category_problems)
    
    filtered_problems = get_filtered_problems(all_problems, number_problems, weight_upvotes, weight_comments, ts_value)
    children = get_problem_cards(filtered_problems)
    colors_children, colors_data = get_colors(leaves)
    return children, filtered_problems, colors_children, colors_data, cy.stylesheet


@callback(
    Output('filter_modal', 'is_open'),
    Input('filters', 'n_clicks'),
    prevent_initial_call = True
)
def open_filters_modal(n):
    if not n:
        return no_update
    return True
