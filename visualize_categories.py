from dash import Dash, html,  dcc, Input, Output, State, no_update, Patch, callback, clientside_callback
import json
import plotly.graph_objects as go


def get_sunburst_data(data, path):
    labels = ['All categories']
    parents = ['']
    values = [100]
    path = path[1:] if path[0]=='/' else path
    path = path.split("/")

    for i in range(len(path)):
    
        if i>0:
            values.append(40)
            labels.append(path[i])
            parents.append(path[i-1])

        if i+1 >= len(path):
            for child in data.get('children', []):
                labels.append(child['name'])
                parents.append(path[i])
                values.append(40/len(data.get('children', [])))
        else:
            children_index = [j for j, d in enumerate(data['children']) if d['name']==path[i+1]][0]
            data = data['children'][children_index]
       
   
    return labels, parents, values

def get_categories(data, path=''):
    categories = []
    current_path = f"{path}/{data['name']}" if path!='' else data['name']

    if 'children' in data:
        for child in data['children']:
            categories.extend(get_categories(child, current_path))
    
    categories.append({'label': data['name'], 'value': current_path})

    return categories


def get_end_categories(data, path):
    path = path[1:] if path[0]=='/' else path
    path = path.split("/")
    leaves = set()

    def recursive_extract(d):
            if 'children' in d:
                for child in d['children']:
                    recursive_extract(child)
            else:
                leaves.add(d['name'])
    
    def test_end_state(d2):
        end_state = True
        if 'children' in d2:
            for child in d2['children']:
                if 'children' in child:
                    end_state = False
        return end_state

    for i in range(len(path)):
        if i+1 >= len(path):
            recursive_extract(data)
            end_state = test_end_state(data)
        else:
            children_index = [j for j, c in enumerate(data['children']) if c['name']==path[i+1]][0]
            data = data['children'][children_index]
    
    return list(leaves), end_state

categories_layout = html.Div([
    dcc.Dropdown(id = 'categories_dropdown', options = ["All categories"], value="All categories",
                 className = 'w-1/2'),
    dcc.Graph(figure = go.Figure(data = go.Sunburst(rotation=290, branchvalues="total", marker=dict(
        colorscale='RdBu'), hovertemplate='<b>%{label}<extra></extra>' ),
                                  layout = go.Layout(margin=dict(t=0, l=0, r=0, b=0))), config={'displayModeBar': False}, style={"transform": "translateX(-30%)"}, id = 'sunburst_chart'),
    dcc.Store(id = 'full_categories'),
    dcc.Store(id = 'current_labels'),
    html.Button(id = "sunburst_chart_click", className = 'hidden'),
    html.Div([
        html.Div("", id = 'selection_info', className = 'font-semibold text-zinc-600 text-base'),
        dcc.Dropdown(options = [], value = [], multi = True, className = 'w-3/4', id = 'categories_selection_dropdown'),
        dcc.Store(id = "selected_categories"),
        html.Button("View Subreddits", id= 'view_subreddits', disabled = True, className = 'rounded-md px-2 py-2 border-2 border-red-600 bg-red-200 text-zinc-800 font-semibold h-12 cursor-not-allowed'),
    ])
])


#Initializing
@callback(
    Output('full_categories', 'data'),
    Output('current_labels', 'data'),
    Output('categories_dropdown', 'options'),
    Input('full_categories', 'id') #fire instantly
)
def fill_stores(id):
    with open('filtered_categories.json') as f:
        data = json.load(f)
    
    labels, parents, values = get_sunburst_data(data, "All categories")
    dropdown_categories = get_categories(data)
    return data, [labels, parents, values], dropdown_categories

# Callback to update the Sunburst chart
@callback(
    Output('sunburst_chart', 'figure'),
    Input('current_labels', 'data'),
    prevent_initial_call = True
)
def update_sunburst(data):
    
    labels, parents, values = data
    
    sb_patch = Patch()
    sb_patch['data'][0]['labels'] = labels
    sb_patch['data'][0]['parents'] = parents
    sb_patch['data'][0]['values'] = values
    return sb_patch

@callback(
    Output('current_labels', 'data', allow_duplicate=True),
    Output('selection_info', 'children'),
    Output('categories_selection_dropdown', 'options'),
    Output('categories_selection_dropdown', 'value'),
    Input('sunburst_chart_click', 'title'),
    State('full_categories', 'data'),
    prevent_initial_call = True
)
def change_sub_categories(title, data):
    clicked_label = title
    current = title.split("/")[-1]
    end_categories, end_state = get_end_categories(data, clicked_label)

    return get_sunburst_data(data, clicked_label), f"You've selected {current}" if end_state else "", \
    end_categories if end_state else [], end_categories if end_state else []

@callback(
    Output('view_subreddits', 'className'),
    Output('view_subreddits', 'disabled'),
    Input('categories_selection_dropdown', 'value'),
    prevent_initial_call = True
)
def disable_button(v):
    return 'rounded-md px-2 py-2 border-2 border-red-600 bg-red-200 text-zinc-800 font-semibold h-12' if len(v)>0 else 'rounded-md px-2 py-2 border-2 border-red-600 bg-red-200 text-zinc-800 font-semibold h-12 cursor-not-allowed', \
    not len(v)>0

#Remove Default Interactions
clientside_callback(
'''
function (n){
    label = document.getElementById("sunburst_chart_click").innerHTML;
    console.log(label);
    label = label.replaceAll('&amp;', '&')
    return label;
}
''',
    Output('sunburst_chart_click', 'title'),
    Input('sunburst_chart_click', 'n_clicks'),
    prevent_initial_call = True
)

@callback(
    Output('current_labels', 'data', allow_duplicate=True),
    Input('categories_dropdown', 'value'),
    State('full_categories', 'data'),
    prevent_initial_call = True
)
def update_categories_with_dropdown(value, data):
    return get_sunburst_data(data, value)