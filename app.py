from flask import Flask, render_template, request, jsonify
import json
from itertools import combinations

app = Flask(__name__)

# ─────────────────────────────────────────────
# MERGE SORT  (Unit I – Divide & Conquer)
# ─────────────────────────────────────────────
def merge_sort(arr, key=lambda x: x):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left  = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    return merge(left, right, key)

def merge(left, right, key):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ─────────────────────────────────────────────
# SHARED: NET BALANCES
# ─────────────────────────────────────────────
def get_balances(participants, transactions):
    balance = {p: 0 for p in participants}
    for t in transactions:
        balance[t['debtor']]   -= t['amount']
        balance[t['creditor']] += t['amount']
    return balance


# ─────────────────────────────────────────────
# MODE 1: GREEDY SETTLEMENT
# ─────────────────────────────────────────────
def greedy_settlement(participants, transactions):
    balance = get_balances(participants, transactions)

    debtors   = [[p, -b] for p, b in balance.items() if b < 0]
    creditors = [[p,  b] for p, b in balance.items() if b > 0]

    debtors   = merge_sort(debtors,   key=lambda x: x[1])
    creditors = merge_sort(creditors, key=lambda x: -x[1])

    optimized = []
    steps = []
    i, j = 0, 0
    step_num = 1

    while i < len(debtors) and j < len(creditors):
        debtor_name,   debt   = debtors[i]
        creditor_name, credit = creditors[j]

        settle = min(debt, credit)
        optimized.append({
            'from':   debtor_name,
            'to':     creditor_name,
            'amount': round(settle, 2)
        })
        steps.append({
            'step': step_num,
            'debtor': debtor_name,
            'creditor': creditor_name,
            'amount': round(settle, 2),
            'note': f"Settle min(₹{round(debt,2)}, ₹{round(credit,2)}) = ₹{round(settle,2)}"
        })
        step_num += 1

        debtors[i][1]   -= settle
        creditors[j][1] -= settle

        if debtors[i][1] < 0.001:   i += 1
        if creditors[j][1] < 0.001: j += 1

    return optimized, balance, steps


# ─────────────────────────────────────────────
# MODE 2: PRIORITY SETTLEMENT
# ─────────────────────────────────────────────
def priority_settlement(participants, transactions):
    balance = get_balances(participants, transactions)

    debtors   = sorted([{'name': p, 'amount': -b} for p, b in balance.items() if b < 0],
                       key=lambda x: -x['amount'])
    creditors = sorted([{'name': p, 'amount':  b} for p, b in balance.items() if b > 0],
                       key=lambda x: -x['amount'])

    suggestions = []
    d_list = [[d['name'], d['amount']] for d in debtors]
    c_list = [[c['name'], c['amount']] for c in creditors]
    i, j = 0, 0
    while i < len(d_list) and j < len(c_list):
        settle = min(d_list[i][1], c_list[j][1])
        suggestions.append({
            'from': d_list[i][0],
            'to':   c_list[j][0],
            'amount': round(settle, 2)
        })
        d_list[i][1] -= settle
        c_list[j][1] -= settle
        if d_list[i][1] < 0.001: i += 1
        if c_list[j][1] < 0.001: j += 1

    return debtors, creditors, suggestions, balance


# ─────────────────────────────────────────────
# MODE 3: SETTLEMENT PATHS (DFS / Backtracking)
# ─────────────────────────────────────────────
def find_paths(participants, transactions):
    # Build adjacency: debtor -> creditor -> amount
    graph = {}
    for t in transactions:
        d, c, a = t['debtor'], t['creditor'], t['amount']
        if d not in graph:
            graph[d] = {}
        graph[d][c] = graph[d].get(c, 0) + a

    balance = get_balances(participants, transactions)
    debtors   = [p for p, b in balance.items() if b < 0]
    creditors = [p for p, b in balance.items() if b > 0]

    all_paths = []

    def dfs(node, target, path, visited):
        if node == target:
            all_paths.append(list(path))
            return
        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, target, path, visited)
                    path.pop()
                    visited.remove(neighbor)

    for debtor in debtors:
        for creditor in creditors:
            visited = {debtor}
            dfs(debtor, creditor, [debtor], visited)

    # Score paths: fewer hops = better
    scored = []
    for p in all_paths:
        scored.append({
            'path': p,
            'hops': len(p) - 1,
            'path_str': ' → '.join(p)
        })

    scored.sort(key=lambda x: x['hops'])

    optimal = scored[0] if scored else None
    return scored, optimal, graph, balance


# ─────────────────────────────────────────────
# MODE 4: ZERO-SUM GROUPING (DP-style subset)
# ─────────────────────────────────────────────
def zero_sum_groups(participants, transactions):
    balance = get_balances(participants, transactions)
    non_zero = {p: round(b, 2) for p, b in balance.items() if abs(b) > 0.001}
    names = list(non_zero.keys())

    groups = []
    used = set()

    for size in range(2, len(names) + 1):
        for combo in combinations(names, size):
            if any(c in used for c in combo):
                continue
            total = sum(non_zero[c] for c in combo)
            if abs(total) < 0.001:
                group_members = list(combo)
                group_balances = {m: non_zero[m] for m in group_members}

                # Internal greedy settlement within group
                d_list = [[p, -b] for p, b in group_balances.items() if b < 0]
                c_list = [[p,  b] for p, b in group_balances.items() if b > 0]
                d_list.sort(key=lambda x: -x[1])
                c_list.sort(key=lambda x: -x[1])
                settlements = []
                ii, jj = 0, 0
                while ii < len(d_list) and jj < len(c_list):
                    settle = min(d_list[ii][1], c_list[jj][1])
                    settlements.append({'from': d_list[ii][0], 'to': c_list[jj][0], 'amount': round(settle, 2)})
                    d_list[ii][1] -= settle
                    c_list[jj][1] -= settle
                    if d_list[ii][1] < 0.001: ii += 1
                    if c_list[jj][1] < 0.001: jj += 1

                groups.append({
                    'members': group_members,
                    'balances': group_balances,
                    'settlements': settlements
                })
                for c in combo:
                    used.add(c)

    ungrouped = [p for p in names if p not in used]
    return groups, ungrouped, balance


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/priority')
def priority_page():
    return render_template('priority.html')

@app.route('/paths')
def paths_page():
    return render_template('paths.html')

@app.route('/zero-sum')
def zero_sum_page():
    return render_template('zero_sum.html')


# ─────────────────────────────────────────────
# API ENDPOINTS
# ─────────────────────────────────────────────
def validate_input(data):
    participants = data.get('participants', [])
    transactions = data.get('transactions', [])
    if len(participants) < 2:
        return None, None, 'Need at least 2 participants'
    if not transactions:
        return None, None, 'No transactions provided'
    for t in transactions:
        if t['debtor'] == t['creditor']:
            return None, None, 'Debtor and creditor cannot be the same person'
        if t['amount'] <= 0:
            return None, None, 'Amount must be positive'
    return participants, transactions, None


@app.route('/api/minimize', methods=['POST'])
def minimize():
    data = request.get_json()
    participants, transactions, err = validate_input(data)
    if err:
        return jsonify({'error': err}), 400

    sorted_transactions = merge_sort(transactions, key=lambda x: x['amount'])
    optimized, balance, steps = greedy_settlement(participants, transactions)

    return jsonify({
        'original_count':  len(transactions),
        'optimized_count': len(optimized),
        'optimized':       optimized,
        'sorted_transactions': sorted_transactions,
        'balances':        balance,
        'transactions':    transactions,
        'steps':           steps
    })


@app.route('/api/priority', methods=['POST'])
def priority_api():
    data = request.get_json()
    participants, transactions, err = validate_input(data)
    if err:
        return jsonify({'error': err}), 400

    debtors, creditors, suggestions, balance = priority_settlement(participants, transactions)
    return jsonify({
        'debtors':    debtors,
        'creditors':  creditors,
        'suggestions': suggestions,
        'balances':   balance
    })


@app.route('/api/paths', methods=['POST'])
def paths_api():
    data = request.get_json()
    participants, transactions, err = validate_input(data)
    if err:
        return jsonify({'error': err}), 400

    paths, optimal, graph, balance = find_paths(participants, transactions)
    return jsonify({
        'paths':   paths,
        'optimal': optimal,
        'balance': balance
    })


@app.route('/api/zero-sum', methods=['POST'])
def zero_sum_api():
    data = request.get_json()
    participants, transactions, err = validate_input(data)
    if err:
        return jsonify({'error': err}), 400

    groups, ungrouped, balance = zero_sum_groups(participants, transactions)
    return jsonify({
        'groups':     groups,
        'ungrouped':  ungrouped,
        'balance':    balance
    })


if __name__ == '__main__':
    app.run(debug=True)
