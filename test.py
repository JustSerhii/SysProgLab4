grammar_example = {
    'S': ['AC'],
    'A': ['aA', 'b'],
    'C': ['cC', 'ε']
}

def concatenate_sets(sets, k):

    if not sets:
        return set(['ε'])

    concatenated = sets[0]

    for next_set in sets[1:]:
        temp_set = set()
        for prefix in concatenated:
            for suffix in next_set:
                if prefix == 'ε':
                    temp_set.add(suffix)
                elif suffix == 'ε':
                    temp_set.add(prefix)
                else:
                    concatenated_string = prefix + suffix
                    temp_set.add(concatenated_string[:k])
        concatenated = temp_set

    return concatenated


def first_k_combinations(symbols, k, first_k_sets):

    if not symbols:
        return set(['ε'])

    combined_set = first_k_sets.get(symbols[0], {symbols[0]})

    for symbol in symbols[1:]:
        new_set = set()
        for prefix in combined_set:
            for suffix in first_k_sets.get(symbol, {symbol}):
                if prefix.endswith('ε'):
                    combined = prefix[:-1] + suffix
                else:
                    combined = prefix + suffix
                if len(combined) > k:
                    combined = combined[:k]
                new_set.add(combined)
        combined_set = new_set

    return combined_set

def first_k_production(production, k, first_k_sets):

    if not production:
        return set(['ε'])

    first_k_prod = set()
    if production[0] == 'ε':
        return set(['ε'])

    first_k_symbol = first_k_sets.get(production[0], set())
    if 'ε' not in first_k_symbol:
        return set(x[:k] for x in first_k_symbol)

    symbols_sets = [first_k_symbol - set(['ε'])]
    i = 1
    while 'ε' in first_k_symbol and i < len(production):
        first_k_symbol = first_k_sets.get(production[i], set())
        symbols_sets.append(first_k_symbol)
        i += 1

    first_k_prod.update(concatenate_sets(symbols_sets, k))

    if all('ε' in first_k_sets.get(sym, set()) for sym in production):
        first_k_prod.add('ε')

    return first_k_prod


def compute_first_k_sets(grammar, k):
    first_k_sets = {symbol: {symbol} for symbol in grammar if not symbol.isupper()}

    first_k_sets['ε'] = {'ε'}

    for nonterminal in grammar:
        first_k_sets[nonterminal] = set()

    is_changed = True
    while is_changed:
        is_changed = False
        for nonterminal in grammar:
            for production in grammar[nonterminal]:
                first_k_prod = first_k_combinations(production, k, first_k_sets)
                if not first_k_prod.issubset(first_k_sets[nonterminal]):
                    first_k_sets[nonterminal].update(first_k_prod)
                    is_changed = True

    return first_k_sets


def follow_k_combinations(symbols, k, first_k_sets, follow_k_sets):

    if not symbols:
        return set(['ε'])

    combined_set = follow_k_sets.get(symbols[-1], {symbols[-1]})

    for symbol in reversed(symbols[:-1]):
        new_set = set()
        first_k_symbol = first_k_sets.get(symbol, {symbol})
        for suffix in combined_set:
            for prefix in first_k_symbol:
                if prefix.endswith('ε'):
                    combined = prefix[:-1] + suffix
                else:
                    combined = prefix + suffix
                if len(combined) > k:
                    combined = combined[:k]
                new_set.add(combined)
        combined_set = new_set

    return combined_set


def compute_follow_k_sets(grammar, k, first_k_sets):

    follow_k_sets = {nonterminal: set() for nonterminal in grammar}
    start_symbol = next(iter(grammar))
    follow_k_sets[start_symbol] = set(['$'[:k]])

    is_changed = True
    while is_changed:
        is_changed = False
        for nonterminal, productions in grammar.items():
            for production in productions:
                for i, symbol in enumerate(production):
                    if symbol.isupper():  # Only compute for non-terminals
                        beta = production[i + 1:]
                        first_k_beta = first_k_combinations(beta, k, first_k_sets) if beta else {'ε'}
                        follow_beta = {sequence.replace('ε', '') for sequence in first_k_beta}
                        old_size = len(follow_k_sets[symbol])
                        follow_k_sets[symbol].update(follow_beta - {'ε'})
                        if 'ε' in first_k_beta or not beta:
                            follow_k_sets[symbol].update(follow_k_sets[nonterminal])
                        if len(follow_k_sets[symbol]) != old_size:
                            is_changed = True

    return follow_k_sets



grammar_example = {
    'S': ['AC'],
    'A': ['aA', 'b'],
    'C': ['cC', 'ε']
}

first_k_sets_example = compute_first_k_sets(grammar_example, 2)
print(first_k_sets_example)

follow_k_sets_example = compute_follow_k_sets(grammar_example, 2, first_k_sets_example)
print(follow_k_sets_example)

def create_parsing_table(grammar, first_k_sets, follow_k_sets, k):
    parsing_table = {}

    for nonterminal, productions in grammar.items():
        for production in productions:
            if production != 'ε':
                first_k_of_production = first_k_combinations(production, k, first_k_sets)
            else:
                first_k_of_production = follow_k_sets[nonterminal]

            for terminal_sequence in first_k_of_production:
                if terminal_sequence != 'ε':
                    parsing_table[(nonterminal, terminal_sequence)] = production

            if 'ε' in first_k_of_production or production == 'ε':
                for follow_sequence in follow_k_sets[nonterminal]:
                    if follow_sequence:
                        parsing_table[(nonterminal, follow_sequence)] = production

    return parsing_table

def format_parsing_table(parsing_table):
    sorted_table = sorted(parsing_table.items())

    col_width = max(len(str(item)) for row in sorted_table for item in row) + 2  # padding

    print(f"{'Nonterminal':<{col_width}}{'Input':<{col_width}}Production")
    print("-" * col_width * 3)

    for key, value in sorted_table:
        nonterminal, input_seq = key
        print(f"{nonterminal:<{col_width}}{input_seq:<{col_width}}{value}")

parsing_table = create_parsing_table(grammar_example, first_k_sets_example, follow_k_sets_example, 2)
format_parsing_table(parsing_table)

