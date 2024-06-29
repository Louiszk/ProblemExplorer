import dash_cytoscape as cyto


stylesheet = [
            {
                'selector': 'node',
                'style': {
                    'label': '',
                    #'font-size': 'data(font)',
                    'color': 'black',
                    "text-wrap": "wrap",
                    'background-color': 'data(color)',    
                    'width': 'data(size)',
                    'height': 'data(size)',
                }},
            {
                'selector': '.word',
                'style': {
                    'background-opacity': '0',
                    'opacity': '0.8',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-size': 'data(font)',
                    'label': '',
                    'width': '20px',
                    'height': '20px'
                }},
                {
                'selector': 'edge',
                'style': {
                    'line-color': 'black',
                    'width': '2px'
                }},
                {'selector': '#x',
                 'style': {}}
]

stylesheet2 = [
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'font-size': 'data(font)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'background-color': 'data(color)',
                    "text-wrap": "wrap",
                    'width': 'data(size)',
                    'height': 'data(size)',
                }},
            {
                'selector': 'node:selected',
                'style': {
                    'border-width': '2px',
                    'border-color': '#7e0000',
                }},
                {
                'selector': 'edge',
                'style': {
                    'line-color': 'black',
                    'width': '2px'
                }}
]



communities_network = cyto.Cytoscape(
            id='communities_network',
            minZoom=0.01, 
            #zoomingEnabled=False,  
            boxSelectionEnabled = True,
            style={'width': '90%', 'height': '400px'},
            stylesheet= stylesheet2,
            layout = {'name': 'preset'}
            )

problems_network = cyto.Cytoscape(
            id='problems_network',
            minZoom=0.01, 
            #zoomingEnabled=False,  
            boxSelectionEnabled = True,
            style={'width': '100%', 'height': '600px'},
            stylesheet= stylesheet,
            layout = {'name': 'preset'}
            )


color_palette_green_yellow = ['#005800', '#065c03', '#0d6007', '#13640b', '#196910', '#1e6d14', '#237218', '#28761b', '#2c7a1f', '#317f23', '#368326', '#3a882a',
                              '#3f8c2e', '#449131', '#499535', '#4e9a38', '#539e3c', '#58a340', '#5da743', '#62ac47', '#68b14b', '#6db54e', '#73ba52', '#79be56',
                                '#7fc35a', '#85c75d', '#8bcc61', '#92d065', '#99d468', '#a0d96c', '#a7dd6f', '#afe173', '#b7e576', '#c0e97a', '#c9ed7d',
                                  '#d2f180', '#dcf583', '#e7f886', '#f2fc88', '#fdff8a']

color_palette_green = ['#002000', '#002500', '#002a00', '#002f00', '#003500', '#003a00', '#003f00', '#004500', '#004a00', '#005000', '#005500', '#005b00', '#006100',
                        '#006600', '#006c00', '#007200', '#007800', '#007e00', '#0c8407', '#188a10', '#228f17', '#2b951e', '#329b24', '#39a12b', '#40a630', '#47ac36', '#4db23c',
                        '#54b841', '#5abe47', '#60c44d', '#66ca52', '#6dd058', '#73d65d', '#79dc63', '#7fe269', '#85e86e', '#8bee74', '#91f57a', '#98fb7f', '#a8ff8f']

color_palette_red = ['#980000', '#9b0000', '#9d0000', '#a00001', '#a20001', '#a50001', '#a70001', '#aa0001', '#ac0001', '#af0001', '#b10001', '#b40001', '#b70001',
                      '#b90001', '#bc0001', '#be0001', '#c10001', '#c40001', '#c60001', '#c90001', '#cc0001', '#ce0001', '#d10001', '#d40001', '#d60001', '#d90001',
                        '#dc0001', '#de0001', '#e10001', '#e40001', '#e60001', '#e90001', '#ec0000', '#ef0000', '#f10000', '#f40000', '#f70000', '#f90000', '#fc0000', '#ff0000']

color_palette_pink = ['#8b0028', '#900030', '#960038', '#9b0040', '#a10048', '#a60150', '#ab0458', '#af0760', '#b40b68', '#b91070', '#bd1477', '#c1197f', '#c61d86',
                       '#ca228e', '#ce2695', '#d12b9c', '#d530a3', '#d935aa', '#dc3ab0', '#df3fb7', '#e244bd', '#e549c3', '#e84ec9', '#eb53ce', '#ee59d4',
                       '#f05ed9', '#f264de', '#f569e2', '#f66fe7', '#f875eb', '#fa7bee', '#fb81f2', '#fd87f5', '#fe8df7', '#ff93fa', '#ff99fc', '#ffa0fd', '#ffa7fe', '#ffadff', '#ffb3ff']

color_palette_yellow = ['#c07100', '#c27505', '#c4780b', '#c67c10', '#c77f15', '#c98319', '#cb861d', '#cd8a21', '#cf8e24', '#d19128', '#d3952b', '#d4982f',
                         '#d69c32', '#d8a035', '#daa338', '#dba73c', '#ddaa3f', '#dfae42', '#e0b245', '#e2b548', '#e4b94b', '#e5bc4e', '#e7c052', '#e8c455', '#eac758',
                         '#ebcb5b', '#edcf5e', '#eed261', '#f0d664', '#f1da68', '#f3dd6b', '#f4e16e', '#f6e571', '#f7e974', '#f8ec77', '#faf07b', '#fbf47e', '#fcf781', '#fefb84', '#ffff87']

color_palette_blue = ['#0000a4', '#160aa7', '#2313a9', '#2d1bac', '#3521ae', '#3c28b1', '#432eb3', '#4934b5', '#4f3ab8', '#5440ba', '#5946bd', '#5f4cbf', '#6451c1', 
                      '#6857c4', '#6d5dc6', '#7263c9', '#7669cb', '#7b6fcd', '#7f74d0', '#837ad2', '#8780d4', '#8b86d7', '#908cd9', '#9492db', '#9898dd',
                       '#9b9ee0', '#9fa4e2', '#a3aae4', '#a7b0e7', '#abb6e9', '#afbdeb', '#b2c3ed', '#b6c9f0', '#bacff2', '#bdd5f4', '#c1dcf6', '#c4e2f8', '#c8e8fb', '#cbeffd', '#cff5ff']

color_palette_orange = ['#fb6a00', '#fb6d00', '#fb6f00', '#fc7200', '#fc7400', '#fc7700', '#fc7900', '#fd7b01', '#fd7e01', '#fd8001', '#fd8202', '#fd8502', '#fe8703', '#fe8904', '#fe8c05',
                        '#fe8e06', '#fe9007', '#fe9208', '#fe9409', '#ff970b', '#ff990c', '#ff9b0e', '#ff9d10', '#ff9f11', '#ffa113','#ffa414', '#ffa616', '#ffa818',
                          '#ffaa1a', '#ffac1c', '#ffae1d', '#ffb01f', '#ffb221', '#ffb423', '#ffb725', '#ffb927', '#ffbb29', '#ffbd2c', '#ffbf2e', '#ffc130']

color_palette_violet = ['#400048', '#44024c', '#47054f', '#4b0853', '#4f0c57', '#530f5a', '#57135e', '#5b1662', '#5f1965', '#631c69', '#671f6d', '#6b2271', '#6f2575',
                         '#732878', '#772b7c', '#7b2e80', '#7f3184', '#833488', '#87378c', '#8b3a90', '#903d94', '#944098', '#98439c', '#9c46a0', '#a149a4',
                         '#a54ca8', '#a94fac', '#ae52b0', '#b255b5', '#b658b9', '#bb5bbd', '#bf5ec1', '#c361c5', '#c865ca', '#cc68ce', '#d16bd2', '#d56ed6', '#da71db', '#de75df', '#e378e3']

color_palette_red_white = ['#bc0000', '#bf0802', '#c21004', '#c51707', '#c81c0a', '#cb210e', '#cd2611', '#d02b14', '#d32f17', '#d5341a', '#d8381d', '#da3c20', '#dc4123', '#de4526', '#e14929'
                           , '#e34d2c', '#e5512f', '#e65532', '#e85935', '#ea5d39', '#ec613c', '#ed653f', '#ef6942', '#f16d46', '#f27149', '#f3744d', '#f57850', '#f67c54', '#f78057', '#f8845b',
                             '#f9885e', '#fa8c62', '#fb9065', '#fc9469', '#fd986d', '#fd9b71', '#fe9f75', '#fea378', '#ffa77c', '#ffab80']

color_sentiment = ['#00429d', '#2552a5', '#3962ac', '#4871b2', '#567fb8', '#628cbd', '#6e99c2', '#79a4c6', '#84afca', '#8eb8cd', '#98c1d0', '#a1c9d2', '#aad0d3', '#b3d6d5', '#bbdbd5',
                    '#c3dfd6', '#cbe2d5', '#d2e4d5', '#d8e6d4', '#dee7d3', '#e4e7d1', '#e9e7cf', '#ede5cc', '#f1e3ca', '#f4e1c7', '#f6dec3', '#f8dabf', '#fad6bc', '#fad1b7', '#fbccb3', '#fcbea8',
                      '#fdb6a3', '#fdae9e', '#fda598', '#fd9d93', '#fc958e', '#fb8d89', '#f98585', '#f77d80', '#f5767c', '#f36e77', '#f06773', '#ed606f', '#e9586b', '#e55167', '#e14b64', '#dd4460', '#d93d5c',
                        '#d43659', '#cf3056', '#ca2a52', '#c4234f', '#bf1d4c', '#b91749', '#b31147', '#ad0b44', '#a70641', '#a0023f', '#9a013c', '#93003a']

palette =  [color_palette_green_yellow, color_palette_orange, color_palette_blue, color_palette_red, color_palette_yellow, color_palette_pink,color_palette_violet, color_palette_green, color_palette_red_white]