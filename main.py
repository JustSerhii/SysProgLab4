class ASTNode:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        self.children = [] if children is None else children
        self.leaf = leaf

    def __str__(self, level=0):
        ret = "\t" * level + repr(self.type) + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        if self.leaf is not None:
            ret += "\t" * (level + 1) + repr(self.leaf) + "\n"
        return ret

    def __repr__(self):
        return self.__str__()



def read_grammar(grammar_str):
    grammar = {}
    lines = grammar_str.strip().splitlines()  # Використовуємо strip() для видалення зайвих пробілів та порожніх рядків
    for line in lines:
        if line and ' -> ' in line:  # Перевіряємо, чи рядок не порожній і чи містить роздільник
            head, body = line.split(' -> ')
            productions = body.split(' | ')
            grammar[head] = productions
        elif line:
            # Тепер цей блок виконуватиметься тільки для непорожніх рядків, які не відповідають формату
            print(f"Попередження: Рядок '{line}' не відповідає очікуваному формату і буде пропущено.")
    return grammar

grammar_str = """
S -> AB
A -> a | ε
B -> b
"""
grammar = read_grammar(grammar_str)

def first_func(symbol, grammar, first_sets):
    """
    Обчислює First множину для символу.
    """
    # Якщо це термінал або епсілон, First - це сам символ
    if not symbol.isupper() or symbol == 'ε':
        return {symbol}

    # Якщо це нетермінал, додаємо перший символ кожної продукції
    first = set()
    productions = grammar[symbol]
    for prod in productions:
        if prod == 'ε':  # Для епсілон продукцій
            first.add('ε')
        else:
            for char in prod:
                char_first = first_func(char, grammar, first_sets)
                first.update(char_first - {'ε'})
                if 'ε' not in char_first:
                    break
            else:
                first.add('ε')
    return first


def follow_func(symbol, grammar, first_sets, follow_sets):
    """
    Обчислює Follow множину для символу.
    """
    # Для початкового символу додаємо кінець вхідного рядка $
    if symbol == 'S':
        follow_sets[symbol] = set('$')
    else:
        follow_sets[symbol] = set()

    # Переглядаємо всі продукції, де зустрічається symbol
    for key, productions in grammar.items():
        for prod in productions:
            if symbol in prod:
                symbol_index = prod.index(symbol)
                # Якщо символ не в кінці продукції
                if symbol_index + 1 < len(prod):
                    next_symbol = prod[symbol_index + 1]
                    follow_sets[symbol].update(first_sets[next_symbol] - {'ε'})
                # Якщо символ в кінці продукції або наступний символ веде до ε
                if symbol_index + 1 == len(prod) or 'ε' in first_sets[prod[symbol_index + 1]]:
                    if key != symbol:  # щоб уникнути рекурсії
                        follow_sets[symbol].update(follow_sets[key])


# Обчислюємо First і Follow множини для всіх нетерміналів
first_sets = {symbol: first_func(symbol, grammar, {}) for symbol in grammar}
follow_sets = {}
for symbol in grammar:
    follow_func(symbol, grammar, first_sets, follow_sets)

# Виведемо результати
print('First sets:')
print(first_sets)
print('Follow sets:')
print(follow_sets)

# Таблиця парсингу для LL(1) аналізатора
def create_parsing_table(grammar, first_sets, follow_sets):
    """
    Створює таблицю парсингу для LL(1) аналізатора.
    """
    parsing_table = {}

    for head, productions in grammar.items():
        for prod in productions:
            if prod != 'ε':
                # Обчислюємо First для кожного символу в продукції
                first_of_prod = set()
                for char in prod:
                    first_of_char = first_func(char, grammar, first_sets)
                    first_of_prod.update(first_of_char - {'ε'})
                    # Якщо символ не веде до ε, перериваємо
                    if 'ε' not in first_of_char:
                        break
                else:
                    # Якщо всі символи в продукції ведуть до ε, додаємо ε до First множини
                    first_of_prod.add('ε')

                for terminal in first_of_prod:
                    parsing_table[(head, terminal)] = prod
            else:
                for terminal in follow_sets[head]:
                    parsing_table[(head, terminal)] = prod

    return parsing_table


# Створюємо таблицю парсингу з використанням визначених First та Follow множин
parsing_table = create_parsing_table(grammar, first_sets, follow_sets)

print('Parsing table:')
# Виведемо створену таблицю парсингу
print(parsing_table)


def parse_input(input_string, parsing_table, grammar):
    """
    Функція для парсингу вхідного рядка використовуючи LL(1) аналізатор.
    """
    # Стек для аналізу
    stack = ['$', 'S']
    # Додаємо кінець вхідного рядка
    input_string += '$'

    # Індекс для вхідного рядка
    index = 0

    # Парсинг вхідного рядка
    while stack[-1] != '$':
        top = stack.pop()
        current_input = input_string[index]

        if top.isupper():
            # Використовуємо таблицю аналізатора для нетерміналів
            if (top, current_input) in parsing_table:
                production = parsing_table[(top, current_input)]
                # Додаємо продукцію в стек у зворотньому порядку
                stack.extend(reversed(production))
            else:
                # Помилка: немає продукції для даного вхідного символу
                return f"Syntax error: no rule for {top} with input {current_input}"
        else:
            # Вхідний символ збігається з вершиною стеку
            if top == current_input:
                index += 1  # Читаємо наступний символ
            else:
                # Помилка: очікуваний символ не збігається з вхідним
                return f"Syntax error: expected {top}, but found {current_input}"

    # Перевірка, чи весь вхідний рядок був прочитаний
    if input_string[index] == '$':
        return "Input successfully parsed"
    else:
        return "Syntax error: input not fully parsed"


# Приклади для парсингу
successful_input = "ab"
error_input = "aa"

# Парсимо обидва приклади
successful_parse_result = parse_input(successful_input, parsing_table, grammar)
error_parse_result = parse_input(error_input, parsing_table, grammar)

print(f"\nFor input {successful_input}:")
print(successful_parse_result)

print(f"\nFor input {error_input}:")
print(error_parse_result)


# Перероблена функція для побудови AST з правильним керуванням стеком і вузлами

def build_ast(input_string, parsing_table, grammar):
    """
    Побудова Абстрактного Синтаксичного Дерева (AST) для даного вхідного рядка, використовуючи надану граматику
    та таблицю парсингу.
    """
    input_string += '$'  # Додаємо символ кінця до вхідного рядка
    index = 0  # Індекс для відстеження поточного символу вхідного рядка

    # Ініціалізуємо стек із стартовим символом
    start_symbol = next(iter(grammar.keys()))
    root_node = ASTNode(type=start_symbol)
    stack = [(start_symbol, root_node)]

    while stack:
        top_symbol, top_node = stack[-1]
        current_input = input_string[index]

        if top_symbol.isupper():  # Якщо верхній елемент стеку є нетерміналом
            key = (top_symbol, current_input)
            if key in parsing_table:  # Перевіряємо, чи є правило продукції
                production = parsing_table[key]
                # Вилучаємо нетермінал
                stack.pop()
                # Додаємо дочірні вузли для продукції
                for symbol in reversed(production):  # Перевертаємо для збереження правильного порядку при вилученні зі стеку
                    if symbol != 'ε':  # Пропускаємо епсілон
                        new_node = ASTNode(type=symbol)
                        top_node.children.insert(0, new_node)  # Додаємо нові вузли як дітей поточного вузла
                        stack.append((symbol, new_node))
                    else:
                        # Для епсілону ми не додаємо вузол і не просуваємо вхідний рядок
                        new_node = ASTNode(type='ε')
                        top_node.children.insert(0, new_node)
            else:
                # Якщо правило продукції не відповідає, це помилка
                return "Syntax error: no rule for {top_symbol} with input '{current_input}'", None
        else:
            if top_symbol == current_input:  # Якщо верхній елемент стеку відповідає поточному вхідному символу
                # Знайдено відповідність, вилучаємо термінал і переходимо до наступного символу у вхідному рядку
                stack.pop()
                index += 1
            elif top_symbol == 'ε':
                # Для епсілону ми не додаємо вузол і не просуваємо вхідний рядок
                stack.pop()
            else:
                # Якщо не відповідає, виводимо помилку
                return "Syntax error: expected '{top_symbol}', but found '{current_input}'", None

        if current_input == '$':  # Кінець вхідного рядка
            break

    return "Input successfully parsed", root_node

# Побудова AST для вхідного рядка "ab" за допомогою раніше визначеної таблиці парсингу і граматики
ast_result, ast_root = build_ast(successful_input, parsing_table, grammar)
if ast_result == "Input successfully parsed":
    print("\nAST:")
    print(ast_root)  # Це неявно викличе ast_root.__str__()

class RecursiveDescentParser:
    def __init__(self, input_string):
        self.input = input_string
        self.index = 0
        self.length = len(input_string)

    def look_ahead(self):
        # Повертає наступний символ без його споживання
        return self.input[self.index] if self.index < self.length else '$'

    def consume(self, symbol):
        # Споживає наступний символ, якщо він відповідає
        if self.look_ahead() == symbol:
            self.index += 1
        else:
            raise ValueError(f"Unexpected symbol {self.input[self.index]}. Expected: {symbol}")

    def parse_S(self):
        # S -> AB
        self.parse_A()
        self.parse_B()

    def parse_A(self):
        # A -> a | ε
        if self.look_ahead() == 'a':
            self.consume('a')
        # Якщо наступний символ не 'a', припускаємо, що це епсілон і нічого не робимо

    def parse_B(self):
        # B -> b
        self.consume('b')

    def parse(self):
        # Починаємо парсинг зі стартового символу
        self.parse_S()

        # Якщо ми успішно спожили весь вхідний рядок, ми завершили
        if self.index == self.length:
            return "Input successfully parsed"
        else:
            raise ValueError("Input not fully parsed")

# Створюємо екземпляр парсера з вхідним рядком
parser = RecursiveDescentParser("ab")

# Аналізуємо вхідний рядок
try:
    result = parser.parse()
    print(result)
except ValueError as e:
    print(e)