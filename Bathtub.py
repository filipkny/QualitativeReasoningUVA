import copy
from collections import defaultdict

quantity_values = {
    "inflow": ['0', '+'],
    "outflow": ['0', '+', 'max'],
    "volume": ['0', '+', 'max']
}

influences = {
    'inflow' : {
        'volume' : '+'
    },
    'outflow' : {
        'volume' : '-'
    }
}

proportionalities = {
    'outflow' : {
        'volume' : '+'
    }
}

equivalences = {
    'volume' : {
        'outflow' : ['max','0']
    },
}

class State(object):
    def __init__(self, id):
        self.id = id
        self.inflow = ['0', '0'],
        self.outflow = ['0', '0'],
        self.volume =  ['0', '0']




class Bathtub(object):
    def __init__(self):

        self.current_state = {
            'inflow' : ['0', '0'],
            'outflow' : ['0', '0'],
            'volume' : ['0', '0']
        }
        self.saved_states = [self.current_state]
        self.state_graph = {
            0: None
        }

    def __str__(self):
        return str(self.current_state)

    def transition(self):
        for quantity, [magnitude,derivative] in self.current_state.items():
            if derivative == '+':
                self.current_state[quantity][0] = '+'
            elif derivative == '-':
                if magnitude == '+':
                    self.current_state[quantity][0] = '0'
                elif magnitude == '0':

    def update_derivatives(self):
        pass
        # STATE is initialized

        # Compute the influences
        derivatives = self.calc_influences()

        # Compute all new possible states
        new_states = self.update_all(influences)


    def update_all(self, influences):
        # new_state = copy.deepcopy(self.current_state)
        # for quantity, influence_list in influences.items():
        #     if influence_list.count('+') > influence_list.count('-'):
        #         new_state[quantity] = '+'
        #     elif influence_list.count('+') < influence_list.count('-'):
        #         new_state[quantity] = '-'
        #     else:
        #         pass
        #

        return None

    def calc_influences(self):
        for giver in influences.keys():
            for taker in influences[giver].keys():
                influence = influences[giver][taker]
                change = self.influence(giver, influence)
                influence_acc[taker].append(change)

        return influence_acc

    def influence(self, giver, sign):
        giver_magnitude = self.current_state[giver][0]
        if (sign == '+' and giver_magnitude == '+') or (sign == '-' and giver_magnitude == '-'):
            return '+'
        elif (sign == '-' and giver_magnitude == '+') or (sign == '+' and giver_magnitude == '-'):
            return '-'

bathtub = Bathtub()
print(bathtub)
bathtub.current_state['inflow'][1] = '+'
bathtub.transition()
bathtub.update_derivatives()
print(bathtub)
