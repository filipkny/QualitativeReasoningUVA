import copy
from collections import defaultdict

opposite = {
    "+" : "-",
    "-" : "+",
    "0" : "0"
}

class Quantity():
    def __init__(self, name, magnitude_space=('0', '+', 'max'), derivative_space=('-', '0', '+'), magnitude='0', derivative='0',influences=[], proportionalities=[]):
        self.magnitude = magnitude
        self.derivative = derivative
        self.magnitude_space = magnitude_space
        self.derivative_space = derivative_space
        self.name = name
        self.influences = influences
        self.proportionalities = proportionalities

    def __str__(self):
        return self.name + "{" + self.magnitude + "," + self.derivative + "}"

    def change_magnitude_by(self, offset):
        old_mag = self.magnitude
        new_magnitude_index = self.magnitude_space.index(self.magnitude) + offset
        if 0 <= new_magnitude_index < len(self.magnitude_space):
            new_mag = self.magnitude_space[new_magnitude_index]
            self.magnitude = new_mag

            if old_mag != new_mag:
                return True

        return False

    def change_derivative_by(self, offset):
        old_deriv = self.derivative
        new_derivative_index = self.derivative_space.index(self.derivative) + offset
        if 0 <= new_derivative_index < len(self.derivative_space):
            new_derivative = self.derivative_space[new_derivative_index]

            self.derivative = new_derivative

            if old_deriv != new_derivative:
                return True

        return False

    def update_magnitude(self):
        if self.derivative == "+":
            self.change_magnitude_by(1)
        elif self.derivative == "0":
            self.change_magnitude_by(0)
        elif self.derivative == "-":
            self.change_magnitude_by(-1)
        else:
            raise ArithmeticError


class State():
    def __init__(self, quantities):
        self.quantities = quantities

    def __str__(self):
        string = ""
        for quantity in self.quantities.values():
            string += str(quantity) + ", "

        return string

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return str(self) == str(other)

    def update_magnitudes(self):
        for quantity in self.quantities.values():
            quantity.update_magnitude()


class StateGraph1(object):
    def __init__(self, initial_state, influences, proportionalities):
        self.state = initial_state
        self.influences = influences
        self.proportionalities = proportionalities
        self.past_states = {
            0: str(initial_state)
        }
        self.graph = {
            0: None
        }

    def print_current_state(self):
        print(self.state)

    def check_influences(self, accumulator, current_state):
        for influencer, influence in influences.items():
            for influenced, eff in influence.items():
                if current_state.quantities[influencer].magnitude == "+":
                    effect = eff
                elif current_state.quantities[influencer].magnitude == "-":
                    if eff == "+":
                        effect = "-"
                    elif eff == "-":
                        effect = "+"
                else:
                    continue

                accumulator[influenced].append(effect)

    def check_proportionalities(self, accumulator, current_state):
        for proportionaler, proportion in proportionalities.items():
            for proportionaled, eff in proportion.items():
                if current_state.quantities[proportionaler].derivative == "+":
                    effect = eff
                elif current_state.quantities[proportionaler].derivative == "-":
                    if eff == "+":
                        effect = "-"
                    elif eff == "-":
                        effect = "+"
                else:
                    continue
                accumulator[proportionaled].append(effect)

    def accumulate_influences(self, current_state):
        accumulator = defaultdict(list)
        self.check_influences(accumulator, current_state)
        self.check_proportionalities(accumulator, current_state)

        return accumulator

    def update_derivatives(self, accumulator, temp_state):
        new_states = []
        split = False
        for quantity, effects in accumulator.items():
            new_state_plus = copy.deepcopy(temp_state)
            new_state_plus.quantities[quantity].change_derivative_by(+1)
            new_state_minus = copy.deepcopy(temp_state)
            new_state_minus.quantities[quantity].change_derivative_by(-1)

            if "+" in set(effects) and "-" not in set(effects):
                new_states.append(new_state_plus)
            elif "-" in set(effects) and "+" not in set(effects):
                new_states.append(new_state_minus)
            elif "-" in set(effects) and "+" in set(effects):
                new_states.append(new_state_plus)
                new_states.append(new_state_minus)
                new_states.append(copy.deepcopy(self.state))
                split = True

        return new_states, split

    def filter_redundant_states(self, states):
        result = []
        str_states = list(map(lambda x: str(x), states))
        for state in states:
            if str_states.count(str(state)) == 1:
                result.append(state)

        return result


    def compare_state_groups(self, group1, group2):
        return str([str(ele) for ele in group1]) == str([str(ele) for ele in group2])

    def get_new_states(self):
        new_states = [None]
        old_states = []
        temp_state = copy.deepcopy(self.state)
        seen_states = set()
        while not self.compare_state_groups(new_states, old_states):
            accumulator = self.accumulate_influences(temp_state)
            old_states = new_states
            new_states, split = self.update_derivatives(accumulator, temp_state)
            if not split:
                for state in new_states:
                    if state not in seen_states:
                        temp_state = state

                for state in new_states:
                    seen_states.add(state)
            else:
                print(len(new_states))
                print(split)
                continue

        return set(new_states)

    def transition(self):
        self.state.update_magnitudes()
        new_states = self.get_new_states()
        print(new_states)
        self.state = list(new_states)[0]

class StateGraph2(object):
    def __init__(self, initial_state):
        self.state = initial_state
        self.past_states = {
            0: str(initial_state)
        }
        self.graph = {
            0: None
        }

    def print_current_state(self):
        print(self.state)

    def accumulate(self, current_state):
        accumulator = defaultdict(list)
        for quantity_name, quantity in current_state.quantities.items():
            for influence in quantity.influences:
                influenced = influence[0]
                if quantity.magnitude == "+" or \
                   quantity.magnitude == "max":
                    accumulator[influenced].append(influence[1])

            for proportionality in quantity.proportionalities:
                proportionaled = proportionality[0]
                if quantity.derivative == "+":
                    accumulator[proportionaled].append(proportionality[1])
                elif quantity.derivative == "-":
                    accumulator[proportionaled].append(opposite[proportionality[1]])

        return accumulator

    def update_derivatives(self, accumulator):
        new_state = copy.deepcopy(self.state)
        changed = False
        for quantity, effects in accumulator.items():
            all_effects = set(effects)
            if "+" in all_effects and "-" not in all_effects:
                changed = new_state.quantities[quantity].change_derivative_by(+1)
            elif "-" in all_effects and "+" not in all_effects:
                changed = new_state.quantities[quantity].change_derivative_by(-1)
            elif "-" in all_effects and "+" in all_effects:
                continue
            else:
                raise RuntimeError


        return new_state, changed

    def update_all_derivatives(self):
        new_state = None
        old_state = copy.deepcopy(self.state)
        while old_state != new_state:
            old_state = copy.deepcopy(self.state)
            accumulated = self.accumulate(self.state)
            new_state, changed = self.update_derivatives(accumulated)
            self.state = new_state

    def transition(self):
        self.state.update_magnitudes()
        self.update_all_derivatives()

        #
        # accumulated = self.accumulate(self.state)
        # print(accumulated)
        # new_states, changed = self.update_derivatives(accumulated)
        # print(changed)
        # for state in new_states:
        #     print(state)

inflow = Quantity("inflow", magnitude_space=('0', '+'),influences = [('volume','+')])
outflow = Quantity("outflow",influences=[('volume','-')])
volume = Quantity("volume",proportionalities=[('outflow','+'),('height','+')])
height = Quantity("height",proportionalities=[('pressure','+')])
pressure = Quantity("pressure")

quantities = {
    "inflow": inflow,
    "volume": volume,
    "outflow": outflow,
    "height" : height,
    "pressure" : pressure
}
influences = {
    'inflow': {
        'volume': '+'
    },
    'outflow': {
        'volume': '-'
    }
}
proportionalities = {
    'volume': {
        'outflow': '+'
    }
}

state = State(quantities)
print(state)
state.quantities['inflow'].derivative = "+"
state_graph = StateGraph2(state)
state_graph.print_current_state()
state_graph.transition()
state_graph.print_current_state()


# state_graph = StateGraph1(state, influences, proportionalities)
# state_graph.print_current_state()
# state_graph.transition()
# state_graph.print_current_state()
# state_graph.transition()