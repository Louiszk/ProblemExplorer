import json
import cyto as cy
from collections import Counter
from dash import html,  dcc, Input, Output, State, no_update, callback, ALL, ctx, Patch
import re
import math
import problem_texts
import spacy
import numpy as np
import umap

nlp = spacy.load('en_core_web_sm')

# Load GloVe model
def load_glove_model(file_path):
    print("Loading GloVe Model")
    glove_model = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            split_line = line.split()
            word = split_line[0]
            embedding = np.array(split_line[1:], dtype=np.float64)
            glove_model[word] = embedding
    print(f"{len(glove_model)} words loaded!")
    return glove_model

glove_path = 'glove.6B/glove.6B.50d.txt'
glove_model = load_glove_model(glove_path)

weights = {'NOUN': 1.0, 'PROPN': 1.0, 'VERB': 0.25, 'ADJ': 0.1}

def get_weighted_embedding(doc, title):
    embeddings = []
    words = []
    for token in doc:
        if token.pos_ in weights and len(token.text) > 1:
            if token.text in glove_model:
                weight = weights[token.pos_]*2 if token.text in title else weights[token.pos_]
                embeddings.append(weight * glove_model[token.text])
            words.append(token.text.lower())
    if embeddings:
        
        return np.mean(embeddings, axis=0), words
    else:
        return np.zeros(50), words


@callback(
    Output('problems_network', 'elements'),
    Input('top_posts_data', 'data'),
    State('colors_data', 'data'),
    State('weight_upvotes', 'value'),
    State('weight_comments', 'value'),
    prevent_initial_call=True
)
def show_problems_network(data, colors_data, wu, wc):
    documents = [" ".join((p[0], p[5])) for p in data]

    def case_insensitive_replace(text, old, new):
        pattern = re.compile(re.escape(old), re.IGNORECASE)
        return pattern.sub(new, text)
    
    # remove problem phrases
    new_docs = []
    for document in documents:
        new_doc = document
        for phrase in problem_texts.remove_phrases:
            if phrase.lower() in new_doc.lower():
                new_doc = case_insensitive_replace(new_doc, phrase, "")
        new_docs.append(new_doc)

    print("Getting Embeddings")
    embeddings = []
    all_words = []
    embedding_words = []
    for post, d in zip(new_docs, data):
        doc = nlp(post)
        embedding, word_list = get_weighted_embedding(doc, d[0])
        embeddings.append(embedding)
        all_words.extend(word_list)
        embedding_words.append(word_list)

    
    #wordcloud
    all_words_counter = Counter(all_words)
    upper_limit = 60
    all_words_counter = {k:c for k, c in sorted(all_words_counter.items(), key=lambda item: item[1], reverse=True)[:upper_limit] if k in glove_model and c>1} 
    wordcloud_embedding = np.array([glove_model[word] for word in all_words_counter])

    print("DR with UMAP")
    umap_model = umap.UMAP(n_components=2, random_state=42, n_neighbors=10, metric='cosine')
    reduced_embeddings = umap_model.fit_transform(np.vstack((embeddings, wordcloud_embedding)))

    
    nodes = [{'data': {'id': str(i), 'label': post[0],
                'size': f"{math.ceil(math.log2(max(2, int(post[1])*wc+ int(post[2])*wu))*100)}px",
                #'font': f"{math.ceil(math.log2(max(1, int(post[1])))*10)}px",
                'color': colors_data[post[6]]},
               'position': {'x': pos[0]*2000, 'y': pos[1]*2000}}
             for i, (post, pos) in enumerate(zip(data, reduced_embeddings[:len(embeddings)]))]

    
    word_nodes = []
    placed_bboxes = []
    wordcloud_embedding_reduced = reduced_embeddings[len(embeddings):]
    for i, (word, wordcount) in enumerate(all_words_counter.items()):
         
        position = wordcloud_embedding_reduced[i] * 2000
        font_size = math.ceil(math.log2(wordcount)*100)
        
        position_x = position[0]
        position_y = position[1]
        #collision detection words
        def calculate_bounding_box(word, font_size, x, y):
            word_length = len(word)
            width = word_length * font_size * 0.6  
            height = font_size * 0.8
            return x - width / 2, y - height / 2, x + width / 2, y + height / 2

        # Function to check for overlap
        def is_overlapping(box1, box2):
            # Calculate intersection area
            x_overlap = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
            y_overlap = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
            intersection_area = x_overlap * y_overlap
            
            return intersection_area > 40
        bbox = calculate_bounding_box(word, font_size, position[0], position[1])
        
        collision = True
        iterations = 0
        while collision and iterations < 20:
            collision = False
            iterations += 1
            for other_bbox in placed_bboxes:
                if is_overlapping(bbox, other_bbox):
                    collision = True
                    # Calculate the center of the other bounding box
                    other_center_x = (other_bbox[0] + other_bbox[2]) / 2
                    other_center_y = (other_bbox[1] + other_bbox[3]) / 2

                    # Calculate the angle of collision
                    dx = position_x - other_center_x
                    dy = position_y - other_center_y
                    if dx == 0:
                        # Adjust position only along y-axis
                        angle = math.pi / 2  # 90 degrees
                        position_y += math.copysign(move_distance, dy)
                    elif dy == 0:
                        # Adjust position only along x-axis
                        angle = 0  # 0 degrees
                        position_x += math.copysign(move_distance, dx)
                    else:
                        angle = math.atan2(dy, dx)
                        move_distance = 30
                        position_x += math.cos(angle) * move_distance
                        position_y += math.sin(angle) * move_distance
                    bbox = calculate_bounding_box(word, font_size, position_x, position_y)
                    break

        placed_bboxes.append(bbox)
        

        word_nodes.append({'data': {'id': word,
                'font': f"{font_size}px"},
                #'color': , maybe here some font color to encode ...
               'position': {'x': position_x, 'y': position_y},
               'classes': 'word'})
        
    edges = [] #connect same subreddits?
    elements = nodes + word_nodes + edges

    return elements

def get_hover_div(image_url, title, url, sub, upvotes, comments, date):
    hover_div = html.Div([
            html.Div(html.Img(src=image_url, className = 'h-10 w-10 aspect-square shrink-0 grow-0 ml-4 rounded-md'),className = 'h-full w-2/12 flex items-center'),
                            html.Div(html.Div([
                                                html.Div(html.A(title, title = 'Open Post on Reddit', href = url, target='_blank', className = 'hover:underline text-white hover:text-white font-semibold align-top block truncate'),className=' flex items-start w-full'),
                                                html.Div(html.A(sub, href = f"https://www.reddit.com/{sub}", title = f'Open Subreddit', target='_blank', className = ' h-4 w-full text-xs text-gray-300 block truncate hover:text-white') ,className=' flex items-start w-full')
                                            ],className='w-full flex flex-col gap-1 justify-start'), className = 'w-5/12 h-full flex items-center'),
                                html.Div([html.Img(src = 'assets/upvote.png', className = 'h-4 w-4 aspect-square shrink-0 grow-0'),
                                          html.Div(upvotes, className = 'text-sm font-semibold text-gray-300'),
                                          html.Img(src = 'assets/comment.png', className = 'h-4 w-4 aspect-square shrink-0 grow-0'),
                                          html.Div(comments, className = 'text-sm font-semibold text-gray-300')
                                          ], className =  'h-full w-3/12 flex flex-row gap-2 items-center justify-center'),

                                html.Div(date, className =  'text-sm font-semibold text-gray-300 h-full w-2/12 flex flex-row gap-1 items-center justify-center'),
                                ], className = 'flex flex-row justify-start rounded-md h-14 w-full mr-2 bg-zinc-800')
    return hover_div

layout = html.Div([

            html.Div([
                html.Div(id = 'hover_info', className = 'absolute z-10 w-1/3'),
                cy.problems_network
            ], className = 'w-10/12'),
            html.Div([
                html.Div(id = 'colors', className = 'flex flex-col gap-1 m-2 bg-zinc-800 rounded-md text-white font-semibold'),
                dcc.Checklist(id='display_words', options=[
                                                      {'label': 'Show Wordcloud', 'value': 'show'}
                                                      ],value=[], labelStyle={'display': 'block', 'marginLeft': '2px'})
            ],className = 'w-2/12 flex flex-col gap-4'),
], className = 'flex flex-row gap-1')


def get_highlighted_content(content):
    doc = nlp(content)

    highlighted_content = []
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN']:
            highlighted_content.append(html.Span(token.text + ' ', style={'color': '#439eaa'}))
        elif token.pos_ == 'VERB':
            highlighted_content.append(html.Span(token.text + ' ', style={'color': '#e4665d'}))
        elif token.pos_ == 'ADJ':
            highlighted_content.append(html.Span(token.text + ' ', style={'color': '#2bbe69'}))
        else:
            highlighted_content.append(token.text + ' ')
    return highlighted_content

@callback(
    Output('whole_post', 'children', allow_duplicate=True),
    Output('whole_post_title', 'children', allow_duplicate=True),
    Output('problems_network', 'stylesheet', allow_duplicate=True),
    Input('problems_network', 'tapNodeData'),
    State('top_posts_data', 'data'),
    State('problems_network', 'stylesheet'),
    prevent_initial_call = True
)
def show_whole_post_node(tND, data, stylesheet):
    if not tND or 'label' not in tND:
        return no_update, no_update, no_update
    for i, style in enumerate(stylesheet):
        if style['selector'][0]=='#':
            stylesheet[i] = {
                'selector': f"#{tND['id']}",
                'style': {
                    'border-width': '40px',
                    'border-color': 'data(color)',
                    'background-color': '#ffffff'
                }}
    return get_highlighted_content(data[int(tND['id'])][5]), tND['label'], stylesheet


@callback(
    Output('problems_network', 'stylesheet', allow_duplicate=True),
    Input('display_words', 'value'),
    prevent_initial_call = True
)
def display_words(v):
    stylesheet_patch = Patch()
    if 'show' in v:
        stylesheet_patch[1]['style']['label'] = 'data(id)'
    else:
        stylesheet_patch[1]['style']['label'] = ''

    return stylesheet_patch

with open(f'get_data/communities.json', 'r') as file:
    all_subs = json.load(file)

@callback(
    Output('hover_info', 'children'),
    Input('problems_network', 'mouseoverNodeData'),
    State('top_posts_data', 'data'),
    prevent_initial_call = True
)
def show_hover_info(moND, data):
    if not moND or not 'label' in moND:
        return no_update
    
    hover_data = data[int(moND['id'])]
    subreddit = "/".join(("r", hover_data[4].split("/")[4]))
    hover_info = None
    for sub in all_subs:
        if sub[1]==subreddit:
            hover_info = get_hover_div(sub[4], moND['label'], hover_data[4], subreddit, hover_data[2], hover_data[1], hover_data[3].split("T")[0])
    if not hover_info:
        hover_info = get_hover_div('assets/reddit.jpg', moND['label'], hover_data[4], subreddit, hover_data[2], hover_data[1], hover_data[3].split("T")[0])
    return hover_info
    

@callback(
    Output('whole_post', 'children'),
    Output('whole_post_title', 'children'),
    Input({'type':'post', 'rank':ALL}, 'n_clicks'),
    State('top_posts_data', 'data'),
    prevent_initial_call=True
)
def show_whole_post(ns, data):
    if not any(ns):
        return no_update

    rank = ctx.triggered_id['rank']
    post_content = data[rank][5]
    post_title = data[rank][0]

    return get_highlighted_content(post_content), post_title