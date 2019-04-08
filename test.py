import itertools
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

    # ---- ASSUMPTIONS ------
    # If volume is max, then tap cannot be postive (mag or deriv)
    states = states[~((states[:, 1] == 2) & (states[:, 0] == 1))]
    states = states[~((states[:, 1] == 2) & (states[:, 3] == 1))]

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
            for j in range(3):
                derivative = state[j+3]
                old_mag = state[j]
                new_mag = transitions[i][j]
                if derivative > 0 and new_mag < old_mag or \
                   derivative < 0 and new_mag > old_mag or \
                   derivative == 0 and new_mag != old_mag or \
                   derivative > 0 and new_mag == 0 or \
                   derivative < 0 and new_mag == 2 or \
                   abs(old_mag - new_mag) == 2:
                    transitions = np.delete(transitions, (i), axis=0)
                    i -= 1
                    break

            i += 1

        # Derivative filtering
        i = 0
        while i < len(transitions):
            for j in range(3):
                old_derivative = state[j + 3]
                new_derivative = transitions[i][j + 3]
                accumlator = accumulate_effects(state, j)
                if 1 in accumlator and -1 not in accumlator and old_derivative > new_derivative or \
                   -1 in accumlator and 1 not in accumlator and new_derivative > old_derivative or \
                    abs(old_derivative - new_derivative) == 2:

                    # len(accumlator) == 0 and old_derivative != new_derivative:

                    transitions = np.delete(transitions, (i), axis=0)
                    i -= 1
                    break

            # Misc checks

            # If volume is max there can be no inflow
            if state[1] == 2 and transitions[i][3] == 1:
                transitions = np.delete(transitions, (i), axis=0)
                i -= 1
                break

            # If inflow has positive magnitude then outflow derivative must be positive
            if (state[0] == 1 and state[2] == 0) and transitions[i][4] != 1:
                transitions = np.delete(transitions, (i), axis=0)
                i -= 1
                break

            i += 1



        all_transitions[state_id] = transitions

    return all_transitions

def print_connections(states_idxs, transitions):
    for state, transfs in transitions.items():
        print("{} ---> {}".format(states_idxs[state],transfs))

def array2print(state, bonus=False):
    result = ""
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

def create_representation_graph(states, edges, file_path, states_idxs, bonus=False):

    graph = Digraph(comment='The Qualitative Model')
    graph.node_attr.update(color='lightblue2', style='filled')

    for state, transfs in edges.items():
        graph.node(array2print(states_idxs[state],bonus=bonus))
        for transf in transfs:
            graph.edge(array2print(states_idxs[state],bonus=bonus),array2print(transf, bonus=bonus))

    graph.render(file_path, view=True)


# Get all possible combinations of states and derivatives
# states_bonus = generate_all_states(magnitudes_bonus, derivatives_bonus)
# states_bonus = filter_bonus(states_bonus)
# states_idxs_bonus, transitions_bonus = create_transitions(states_bonus)
# num_transitions_bonus = print_num_transitions(transitions_bonus)
# print("# states",len(states_bonus))
# transitions_bonus = filter_transitions(states_idxs_bonus, transitions_bonus)
# print_connections(states_idxs_bonus, transitions_bonus)
# print(len(transitions_bonus[1]))
# print(len(states_bonus))
# num_transitions = print_num_transitions(transitions_bonus)
# create_representation_graph(states_bonus,transitions_bonus, 'test', states_idxs_bonus,bonus=True)
# print(len(states_bonus))


# Filter impossible states
states = generate_all_states(magnitudes, derivatives)
states = filter(states)
states_idxs, transitions = create_transitions(states)
num_transitions = print_num_transitions(transitions)
transitions = filter_transitions(states_idxs, transitions)
num_transitions = print_num_transitions(transitions)
print_connections(states_idxs,transitions)
create_representation_graph(states,transitions, 'test',states,bonus=False)
print(len(states))

# Create and count transitions


