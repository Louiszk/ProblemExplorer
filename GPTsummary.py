from openai import OpenAI
import json 

with open(f'api_key.json', 'r') as file:
    key = json.load(file)["key"]
client = OpenAI( api_key = key)

problem_prompt = '''You are now a problem summarizer expert.
                You can only respond with these two possible outcomes (excluding now):
                    1. A Summary of the problem in the provided text.
                    2. In case you did not understand the post or what the problem is return 'No Summary Available'. Nothing else.
                You will not answer with anything else except these two outcomes.
                Please no additional text.
                Be precise and as short as possible with your Summary.
                If you understood your task, answer with "Ok." and nothing else.'''

ideas_prompt = '''You are now a genius, creative idea finder.
                The following post will state some kind of problem and you will find ideas for the overall type of problem.
    
                You can only respond with the Ideas.
                You will not answer with anything else. Please no additional text.
                Be precise but extremely creative with your Ideas.
                Let us do an example,
                  the first post is: "So I've been using pre-ground lavazza qualita rossa and my coffee always turns out to be sour and ashy.
                    I'm using moka pot on gas stove low heat, water just under the valve, no tamping the grounds. I tried using hot, room temp water,
                      leveling grounds with finger, changing heat but nothing really works. Only difference is how good the extraction looks.
                        Am I doing something wrong? I would be thankful for any advice."'''

def get_summary(post):
    try:
        summary = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": problem_prompt,
            },
            {
                "role":"assistant",
                "content": "Ok."
            },
            {
                "role": "user",
                "content": f'''Thank You, this is the first post:
                {post}
                '''
            }
        ],
        model="gpt-3.5-turbo",
        )
        summary = summary.choices[0].message.content
        print(summary)
    except Exception as e:
        print("OpenAI: ", e)
        summary = 'Could not summarize Post :('
    return summary

def get_ideas(post):
    try:
        ideas = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": ideas_prompt,
            },
            {
                "role":"assistant",
                "content": '''Switch to freshly ground coffee beans instead of pre-ground for better flavor.
                            Experiment with finer grinds for improved extraction in the moka pot.
                            Maintain consistent, gentle heat to avoid bitterness and monitor brewing time to prevent over-extraction.
                            Ensure the moka pot is clean to prevent ashy flavors.'''
            },
            {
                "role": "user",
                "content": f'''Perfect, you understood it. Here is the second post:
                {post}
                ''',
            }
        ],
        model="gpt-3.5-turbo",
        )
        ideas = ideas.choices[0].message.content
        print(ideas)
    except Exception as e:
        print("OpenAI: ", e)
        ideas = 'Could not find Ideas :('
    return ideas

if __name__ == "__main__":
    post = "Too much coffee. Any advice? I own a DeLonghi La Specialista which has been my trusty sidekick for a good while. A few days ago, I ran into a puzzling issue. Initially, the machine faced problems with grinding the coffee beans. When attempting to grind, it sounded like the beans were getting stuck, and it just wouldn't grind. After multiple attempts of removing all beans and giving it a thorough cleaning, voilÃ ! It started grinding correctly again. However, that's not where the story ends. As I had a small amount of coffee in the basket, I decided to run the reset program just in case. I pressed the x2 and 'my' buttons simultaneously. Since then, every time I try to grind coffee (on the x1 setting), the machine grinds an excessive amount. I'm talking almost double what it should. The basket completely overflows before the machine stops. Obviously, this isn't normal, and I'm at a loss on how to fix it. Has anyone experienced something similar or has any advice on what I could do to resolve this? Thanks in advance! "
    get_ideas(post)