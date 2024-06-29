from dash import Dash, html,  dcc, Input, Output, State, no_update, Patch, ALL, ctx
import visualize_categories as vc
import visualize_subs as vs
import visualize_network as vn
import dash_bootstrap_components as dbc
import GPTsummary as gpt

# Initialize the Dash app
app = Dash(__name__, title="ProblemExplorer", external_stylesheets=[dbc.themes.BOOTSTRAP],  external_scripts = [{"src": "https://cdn.tailwindcss.com"}])

app.layout = html.Div([
    html.Div([
        vc.categories_layout,
        vs.subs_layout,
        dcc.Store(id = 'top_posts_data')
    ], className = 'flex flex-col gap-4 col-span-1'),
    html.Div([
        vn.layout,
        html.Div([
            html.Div([
                html.Div("Top Posts", className = 'flex items-center h-2/12 m-2 text-white text-lg'),
                html.Div(html.Div(id = 'top_posts', className = 'm-2 flex flex-col items-center gap-1'), className = 'h-96 overflow-y-scroll overflow-x-hidden')
            ], className = 'w-5/12 bg-zinc-600 rounded-md h-full'),
            html.Div([
                html.Div([
                            dcc.Checklist(id='enable_summary', options=[
                                                      {'label': 'Summary', 'value': 'summary'}
                                                      ],value=[], className = 'flex justify-end'),
                            html.Div(id = 'summary_post', className = ''),
                          ], className = 'bg-zinc-600 rounded-md flex flex-col gap-2 h-4/12 p-2 text-base font-semibold text-white'),
                html.Div([
                    html.Div(id = 'whole_post_title', className = 'text-white text-base font-bold'),
                    html.Div(id = 'whole_post', className = 'm-2 text-white text-sm')
                    ], className = 'flex flex-col gap-2 bg-zinc-600 rounded-md h-64 m-2 overflow-y-scroll'),
                html.Div([
                            dcc.Checklist(id='enable_ideas', options=[
                                                      {'label': 'Ideas', 'value': 'ideas'}
                                                      ],value=[], className = 'flex justify-end'),
                            html.Div(id = 'ideas_post', className = ''),
                          ], className = 'bg-zinc-600 rounded-md flex flex-col gap-2 h-4/12 p-2 text-base font-semibold text-white'),
            ], className = 'flex flex-col gap-1 w-5/12 h-full rounded-md')
        ], className = 'flex flex-row gap-4 w-full h-1/2')
    ], className = 'col-span-2 flex flex-col gap-4 h-full')
], className = 'grid grid-cols-3 space-x-8 font-semibold text-base p-4')




@app.callback(
    Output('summary_post', 'children'),
    Input('problems_network', 'tapNodeData'),
    Input({'type':'post', 'rank':ALL}, 'n_clicks'),
    State('top_posts_data', 'data'),
    State('enable_summary', 'value'),
)
def show_summary(tND, ns, data, v):
    if not any(ns) and not tND:
        return no_update
    if not 'summary' in v:
        return None
    triggered_id = ctx.triggered_id
    if 'rank' in triggered_id:
        rank = ctx.triggered_id['rank']
        post = " ".join((data[rank][0], data[rank][5]))
    else:
        if 'label' not in tND:
            return no_update
        post = " ".join((data[int(tND['id'])][0], data[int(tND['id'])][5]))
    summary = gpt.get_summary(post)
    return summary

@app.callback(
    Output('ideas_post', 'children'),
    Input('problems_network', 'tapNodeData'),
    Input({'type':'post', 'rank':ALL}, 'n_clicks'),
    State('top_posts_data', 'data'),
    State('enable_ideas', 'value'),
)
def show_ideas(tND, ns, data, v):
    if not any(ns) and not tND:
        return no_update
    if not 'ideas' in v:
        return None
    triggered_id = ctx.triggered_id
    if 'rank' in triggered_id:
        rank = ctx.triggered_id['rank']
        post = " ".join((data[rank][0], data[rank][5]))
    else:
        if 'label' not in tND:
            return no_update
        post = " ".join((data[int(tND['id'])][0], data[int(tND['id'])][5]))
    ideas = gpt.get_ideas(post)
    return ideas

if __name__ == '__main__':
    app.run_server(debug=True)