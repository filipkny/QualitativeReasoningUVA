import itertools
from collections import defaultdict

import numpy as np
from graphviz import Digraph



num2sign_mag = {
    0: "0",
    1: "+",
    2: "max"
}
num2sign_deriv = {
    -1: "-",
    0: "0",
    1: "+"
}
quantities = {
    0: "Inflow",
    1: "Volume",
    2: "Outflow"
}

quantities_bonus = {
    0: "Inflow",
    1: "Volume",
    2: "Height",
    3: "Pressure",
    4: "Outflow"
}
# Number of variables
variables_bonus = 5
variables = 3

# 0, plus, max domain for all the variables
magnitudes_bonus= [[0.0, 1.0, 2.0],]*variables_bonus
magnitudes = [[0.0, 1.0, 2.0],]*variables

derivatives_bonus = [[-1, 0, 1],
          [ -1, 0, 1],
          [ -1, 0, 1],
          [ -1, 0, 1],
          [ -1, 0, 1]]

derivatives = [[-1, 0, 1],
                [ -1, 0, 1],
                [ -1, 0, 1]]

influences = {
    1: [(0,1),(2,-1)] # volume <-- I+ -- Inflow,Outflow
}
proportions = {
    2: [(1,1)] # Outflow <-- P+ --> Volume
}
def generate_all_states(magnitudes, derivatives):

    st_var = list(itertools.product(*magnitudes))
    st_der = list(itertools.product(*derivatives))
    states = list(itertools.product(st_var, st_der))
    S = []
    for i in range(len(states)):
        S.append(states[i][0] + states[i][1])

    return np.asarray(S)

def filter_bonus(states):
    for i in range(5):
        # Filter -> MAX magnitude and + Derivative
        states = states[~((states[:,i] == 2) & (states[:,i+5] == 1))]

        # Filter -> 0 magnitude and - Derivative
        states = states[~((states[:,i] == 0) & (states[:,i+5] == -1))]

    for derivative in [-1, 0, 1]:
        # Filter -> height derivative and pressure derivative must be equal
        states = states[~((states[:,7] == derivative) & (states[:,8] != derivative))]
        # Filter -> 1 volume derivative and outflow derivative not 1
        states = states[~((states[:,6] == derivative) & (states[:,7] != derivative))]
        # Filter -> volume derivative and height derivative must be equal
        states = states[~((states[:,6] == derivative) & (states[:,9] != derivative))]


    # Filter -> Inflow cannot be max
    states = states[~((states[:,0] == 2))]

    # Filter -> If volume is max, outflow is max
    states = states[~((states[:,1] == 2) & (states[:,4] != 2))]
    states = states[~((states[:,4] == 2) & (states[:,1] != 2))]

    # Filter -> If volume is 0 outflow is 0
    states = states[~((states[:, 1] == 0) & (states[:, 4] != 0))]
    states = states[~((states[:, 4] == 0) & (states[:, 1] != 0))]

    # Filter -> Outflow derivative is -1, inflow magnitude is 1 and derivative of volume is not 1
    states = states[~((states[:, 4] == -1) & (states[:, 0] == 1) & (states[:,6] != 1))]
    states = states[~((states[:, 4] == 1) & (states[:, 0] == 0) & (states[:,6] != -1))]

    # Particular values, such as 0 and max correspond for volume, height, pressure and
    # outflow.
    for magnitude in [0,2]:
        states = states[~((states[:, 1] == magnitude) & ((states[:, 2] != magnitude) | (states[:, 3] != magnitude) | (states[:, 4] != magnitude)))]
        states = states[~((states[:, 2] == magnitude) & ((states[:, 1] != magnitude) | (states[:, 3] != magnitude) | (states[:, 4] != magnitude)))]
        states = states[~((states[:, 3] == magnitude) & ((states[:, 2] != magnitude) | (states[:, 1] != magnitude) | (states[:, 4] != magnitude)))]
        states = states[~((states[:, 4] == magnitude) & ((states[:, 2] != magnitude) | (states[:, 3] != magnitude) | (states[:, 1] != magnitude)))]


    # ---- ASSUMPTIONS ------
    # If volume is max, then tap cannot be postive (mag or deriv)
    states = states[~((states[:, 1] == 2) & (states[:, 0] == 1))]
    states = states[~((states[:, 1] == 2) & (states[:, 5] == 1))]

    return states

def filter(states):
    for i in range(2):
        # Filter -> MAX magnitude and + Derivative
        states = states[~((states[:,i] == 2) & (states[:,i+3] == 1))]

        # Filter -> 0 magnitude and - Derivative
        states = states[~((states[:,i] == 0) & (states[:,i+3] == -1))]

    # Filter -> 1 volume derivative and outflow derivative not 1
    for derivative in [-1, 0, 1]:
        states = states[~((states[:, 4] == derivative) & (states[:, 5] != derivative))]

    # Filter -> Inflow cannot be max
    states = states[~((states[:, 0] == 2))]

    # Filter -> If volume is max, outflow is max
    states = states[~((states[:, 1] == 2) & (states[:, 2] != 2))]
    states = states[~((states[:, 2] == 2) & (states[:, 1] != 2))]

    # Filter -> If volume is 0 outflow is 0
    states = states[~((states[:, 1] == 0) & (states[:, 2] != 0))]
    states = states[~((states[:, 2] == 0) & (states[:, 1] != 0))]

    # Filter -> Outflow derivative is -1, inflow magnitude is 1 and derivative of volume is not 1
    states = states[~((states[:, 2] == -1) & (states[:, 0] == 1) & (states[:, 4] != 1))]
    states = states[~((states[:, 2] == 1) & (states[:, 0] == 0) & (states[:, 4] != -1))]
    states = states[~((states[:, 2] == 0) & (states[:, 0] == 0) & (states[:, 4] != 0))]

    # If inflow is positive and outflow is 0, both volume and outflow have positive derivative
    states = states[~((states[:, 0] == 1) & (states[:, 2] == 0) & ((states[:, 4] != 1) & (states[:,5] != 1)))]

    states = states[~((states[:, 1] == 2) & (states[:, 0] != 0) & (states[:, 3] != 0))]

    return states

def create_transitions(states):
    transitions = {}
    states_idxs = {}
    for i in range(len(states)):
        states_idxs[i] = states[i]
        transitions[i] = np.delete(states,(i),axis=0)

    return states_idxs, transitions

def print_num_transitions(all_transitions):
    total = 0
    for transitions in all_transitions.values():
        total += len(transitions)

    print("# transitions:" + str(total))
    return total

def accumulate_effects(state, quantity):
    accumulator = []
    for influence in influences.get(quantity,[]):
        influece_sign = influence[1]
        old_state_mag = state[influence[0]]
        if influece_sign > 0 and old_state_mag> 0 or \
            influece_sign < 0 and old_state_mag < 0:
            accumulator.append(1)
        elif influece_sign < 0 and old_state_mag > 0 or \
             influece_sign > 0 and old_state_mag < 0:
            accumulator.append(-1)


    for prop in proportions.get(quantity,[]):
        prop_sign = prop[1]
        old_state_deriv = state[prop[0]+3]
        if prop_sign > 0 and old_state_deriv > 0 or \
            prop_sign < 0 and old_state_deriv < 0:
            accumulator.append(1)
        elif prop_sign < 0 and old_state_deriv > 0 or \
             prop_sign > 0 and old_state_deriv < 0:
            accumulator.append(-1)

    return accumulator

def filter_transitions(states_idxs, all_transitions):

    for state_id, transitions in all_transitions.items():
        state = states_idxs[state_id]

        # Check magnitudes
        i = 0
        while i < len(transitions):
            new_state = transitions[i]
            for j in range(3):
                derivative = state[j+3]
                old_mag = state[j]
                new_mag = transitions[i][j]

                if derivative > 0 and new_mag < old_mag or \
                   derivative < 0 and new_mag > old_mag or \
                   derivative > 0 and new_mag == 0 or \
                   derivative < 0 and new_mag == 2 or \
                   derivative == 0 and new_mag != old_mag or \
                   abs(old_mag - new_mag) == 2:
                    transitions = np.delete(transitions, (i), axis=0)
                    i -= 1
                    break

            i += 1

        # Derivative filtering
        i = 0
        while i < len(transitions):
            breaking = False
            new_state = transitions[i]

            for j in range(3):
                old_derivative = state[j + 3]
                new_derivative = transitions[i][j + 3]
                accumlator = accumulate_effects(state, j)
                if abs(new_derivative - old_derivative) == 2:
                    transitions = np.delete(transitions, (i), axis=0)
                    i -= 1
                    breaking = True
                    break


            # # # Misc checks
            if not breaking:
                # If volume is max there can be no inflow
                if state[1] == 2 and transitions[i][3] == 1:
                    transitions = np.delete(transitions, (i), axis=0)
                    i -= 1
                    break

                # If inflow has positive magnitude then outflow derivative must be positive
                if (state[0] == 1 and state[2] == 0) and transitions[i][4] != 1:
                    transitions = np.delete(transitions, (i), axis=0)
                    i -= 1

                if (state[1] == 1 and state[1 + 3] == 1) and transitions[i][1] != 2:
                    transitions = np.delete(transitions, (i), axis=0)
                    i -= 1

            i += 1



        all_transitions[state_id] = transitions

    return all_transitions

def print_connections(states_idxs, transitions):
    for state, transfs in transitions.items():
        print("{} ---> {}".format(states_idxs[state],transfs))

def array2print(state,id = -1, bonus=False):
    result = str(id) + "\n"
    offset = None
    for i in range(int(len(state)/2)):
        if bonus:
            offset = 5
            Q = quantities_bonus[i]
        else:
            offset = 3
            Q = quantities[i]

        result += Q + "{" + num2sign_mag[int(state[i])] + ", " + num2sign_deriv[int(state[i+offset])] + "}\n"

    return result

def find_state_id(state_idxs, state):
    for key, state_repr in state_idxs.items():
        if np.array_equal(state,state_repr ):
            return key

    return None

def create_representation_graph(states, edges, file_path, states_idxs, bonus=False):

    graph = Digraph(comment='The Qualitative Model')
    graph.node_attr.update(color='lightblue2', style='filled')

    for s, transfs in edges.items():
        str_rep1 = array2print(states_idxs[s],id = s,bonus=bonus)
        graph.node(str_rep1)
        for transf in transfs:
            s_id = find_state_id(states_idxs,transf)
            str_rep2 = array2print(transf,id = s_id,bonus=bonus)
            graph.edge(str_rep1,str_rep2)

    graph.render(file_path, view=True)



def compare_states(state1, state2):
    comparison = ""
    for i in [0, 1, 2]:
        quantity = quantities[i]
        influence = influences.get(i,[])
        props = proportions.get(i,[])

        comparison += quantity + ":"
        mag1 = state1[i]
        mag2 = state2[i]
        der1 = state1[i+3]
        der2 = state2[i+3]
        comparison += " magnitude"
        if mag2 > mag1:
            comparison += " increased"
        elif mag1 > mag2:
            comparison += " decreased"
        else:
            comparison += " remained the same"

        comparison += " and the derivative"

        deriv_change = 0
        if der2 > der1:
            comparison += " increased"
            deriv_change = 1
        elif der1 > der2:
            comparison += " decreased"
            deriv_change = -1
        else:
            comparison += " remained the same"

        if der1 != der2:
            if i == 0:
                comparison += " due to exogenous reasons"
            if i == 1:
                comparison += " due to"
                if state1[0] > 0:
                    comparison += " inflow positive influence"
                if state1[2] < 0:
                    comparison += " outflow negative influenc"
            if i == 2:
                comparison += " due to volume positive proportionality"

        comparison += "\n"

    return comparison

def read_state(state):
    str = ""
    for i in range(3):
        quantitiy = quantities[i]
        str += quantitiy + ": "
        mag = state[i]
        deriv = state[i+3]
        str += "has {} magnitude ".format(num2sign_mag[mag])
        str += "and {} derivative ".format(num2sign_deriv[deriv])
        str += "\n"

    return str

def build_trace_dict(transitions):
    trace_dict = defaultdict(list)
    node_ids = defaultdict(list)
    for node_id, tranfs in transitions.items():
        for transf in tranfs:
            trace_dict[node_id].append(compare_states(states_idxs[node_id],transf))
            node_ids[node_id].append(find_state_id(states_idxs, transf))

    return trace_dict, node_ids

def find_shortest_path(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    if not start in graph.keys():
        return None
    shortest = None
    for node in graph[start]:
        if node not in path:
            newpath = find_shortest_path(graph, node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath
    return shortest

def trace(path):
    print("Path {}".format(path))

    print("Node {}".format(path[0]))
    print(read_state(states_idxs[path[0]]))
    for i in range(1, len(path)):
        print("-- Transition {} -> {} --".format(path[i-1],path[i]))
        print(compare_states(states_idxs[path[i-1]],states_idxs[path[i]]))
        print("Node: {}".format(path[i]))
        print(read_state(states_idxs[path[i]]))

# Generate and filter impossible states
states = generate_all_states(magnitudes, derivatives)
states = filter(states)

# Generate and filter transitions
states_idxs, transitions = create_transitions(states)
transitions = filter_transitions(states_idxs, transitions)


# Build graph
create_representation_graph(states,transitions,'state_graaph',states_idxs,bonus=False)

# Trace
# Generate ID only graph structure
traces, transfer_ids = build_trace_dict(transitions)
example_path = find_shortest_path(transfer_ids,0,20)


trace(example_path)