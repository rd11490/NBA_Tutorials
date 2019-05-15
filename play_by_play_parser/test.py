class PlayByPlayMap:
    def __init__(self):
        self.data = {}

    def add(self, event, action, input):
        if not event in self.data.keys():
            self.data[event] = {}

        if not action in self.data[event].keys():
            self.data[event][action] = {}

        self.merge_map(self.data[event][action], input)

    def merge_map(self, old, new):
        for k in new.keys():
            if not k in old.keys():
                old[k] = new[k]
            else:
                for n_k in new[k].keys():
                    if not n_k  in old[k].keys():
                        old[k][n_k] = new[k][n_k]
                    else:
                        old[k][n_k] = old[k][n_k] + new[k][n_k]

    def make_sentance(self, event, action):
        return ' '.join([self.take_highest(self.data[event][action][k]) for k in self.data[event][action].keys()])

    def take_highest(self, position):
        out = 'NONE'
        cnt = -1
        for k in position.keys():
            if position[k] > cnt:
                cnt = position[k]
                out = k
        return out

def take_one_row(group):
    return group.head(1)

def parse_sentance(description):
    if type(description) is str:
        lower = description.lower()
        subbed = re.sub(r'\([^)]*\)', '', lower)
        arr = subbed.strip().split(' ')
        str_map = {}
        for ind, gram in enumerate(arr):
            str_map[ind] = {gram: 1}
        return str_map
    return {}


def print_play_type(pbp_map):
    for event in sorted(pbp_map.data.keys()):
        for action in sorted(pbp_map.data[event].keys()):
            res = pbp_map.make_sentance(event, action)
            print('Event: {}, Action: {}'.format(event, action))
            print('Out: {}'.format(res))



play_by_play = pd.read_csv('data/2017-18_pbp_fixed.csv')

play_by_play_for_analysis = play_by_play[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE', 'HOMEDESCRIPTION', 'VISITORDESCRIPTION']]

pbp_map_home = PlayByPlayMap()
pbp_map_away = PlayByPlayMap()

def map_phrase(row):
    pbp_map_home.add(row['EVENTMSGTYPE'], row['EVENTMSGACTIONTYPE'], parse_sentance(row['HOMEDESCRIPTION']))
    pbp_map_away.add(row['EVENTMSGTYPE'], row['EVENTMSGACTIONTYPE'], parse_sentance(row['VISITORDESCRIPTION']))

play_by_play_for_analysis.apply(map_phrase, axis=1)

print("Home")
print_play_type(pbp_map_home)

print("Away")
print_play_type(pbp_map_away)

