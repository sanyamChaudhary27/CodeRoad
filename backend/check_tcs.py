import sqlite3, json, subprocess, tempfile, os

code = (
    "def solve(arr, x):\n"
    "    hash_map = {}\n"
    "    for i, num in enumerate(arr):\n"
    "        complement = x - num\n"
    "        if complement in hash_map:\n"
    "            return [hash_map[complement], i]\n"
    "        hash_map[num] = i\n"
    "    return []\n"
)

# Use the generic driver from judge_service
driver = (
    "\nimport sys as _sys\n"
    "import inspect as _inspect\n"
    "def _main():\n"
    "    raw_input = _sys.stdin.read().strip()\n"
    "    if not raw_input: return\n"
    "    try: input_data = list(map(int, raw_input.split()))\n"
    "    except ValueError: input_data = raw_input.split()\n"
    "    if 'solve' not in globals(): return\n"
    "    solve_func = globals()['solve']\n"
    "    sig = _inspect.signature(solve_func)\n"
    "    params = list(sig.parameters.values())\n"
    "    if len(params) == 1: result = solve_func(input_data)\n"
    "    elif len(params) == 2:\n"
    "        if isinstance(input_data, list) and len(input_data) >= 2:\n"
    "            result = solve_func(input_data[:-1], input_data[-1])\n"
    "        else: result = solve_func(input_data, None)\n"
    "    else: result = solve_func(*input_data[:len(params)])\n"
    "    if result is None: print('')\n"
    "    elif isinstance(result, (list, tuple)): print(' '.join(str(v) for v in result))\n"
    "    elif isinstance(result, bool): print(str(result).lower())\n"
    "    else: print(result)\n"
    "_main()\n"
)

conn = sqlite3.connect('coderoad.db')
cur = conn.cursor()
cur.execute('SELECT test_cases FROM challenges ORDER BY created_at DESC LIMIT 1')
row = cur.fetchone()
conn.close()

tcs = json.loads(row[0])
print(f'Found {len(tcs)} test cases')

with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as f:
    f.write(code + driver)
    path = f.name

print()
for i, t in enumerate(tcs):
    inp = t['input']
    exp = str(t['expected_output']).strip()
    r = subprocess.run(['python', path], input=inp, text=True, capture_output=True, timeout=5)
    actual = r.stdout.strip()
    ok = 'PASS' if actual == exp else 'FAIL'
    print(f"TC{i+1} [{ok}]: input='{inp}', got='{actual}', expected='{exp}', stderr='{r.stderr[:50]}'")

os.remove(path)
