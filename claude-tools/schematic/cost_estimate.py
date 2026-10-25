"""JLCPCB PCBA cost estimate at several quantities.
Inputs: out/bom.csv (run_kicad.sh), out/jlc_prices.json (jlc_dump.sh), out/netlist.xml.
Fees from jlcpcb.com/help/article/pcb-assembly-price (page updated 9 Sep 2026, read 14 Oct 2026).
Usage: python3 cost_estimate.py > ../../COST-ESTIMATE.txt   -> 10 (Economic), 100 (Economic, panelised)
Bare PCB is NOT included (needs board size); add it from the JLCPCB quote once layout fixes the outline."""
import csv, json, re, xml.etree.ElementTree as ET
from collections import defaultdict

ECON = dict(name='Economic', setup=8.18, stencil=1.53, panel=0.0, smt_joint=0.0016, manual_joint=0.0164,
            hand_labour=3.58, feeder_ext=3.07, feeder_all=0.0, min_smt_per_board=0.0, confirm=0.45,
            packing=0.0, fixture=0.0)
ECON_PANEL = dict(ECON, name='Economic, panelised', panel=8.21)
STD = dict(name='Standard', setup=25.56, stencil=8.21, panel=0.0, smt_joint=0.0016, manual_joint=0.0164,
           hand_labour=3.58, feeder_ext=0.0, feeder_all=1.53, min_smt_per_board=0.48, confirm=0.45,
           packing=0.50, fixture=None)   # fixture by quantity, see fixture_fee()
XRAY = [(10, 1.64), (50, 0.82), (200, 0.49), (500, 0.33), (1000, 0.25), (3000, 0.16), (99999, 0.082)]
XRAY_REFS = ()  # ESP32-C3-WROOM-02U has castellated edge pads: no X-ray (D1)
COLUMNS = [(10, ECON), (100, ECON_PANEL)]
# Bare PCB: no quote until the layout fixes the outline. Placeholder = irrigation board's quote (100x80 mm,
# 15 Oct 2026, A$ at 1.435): an upper bound, since V0.2 is 37 mm x (<100) mm.
PCB_QUOTE = {10: 7.18 / 1.435, 100: 100.31 / 1.435}
MODBUS_REFS = {'U5', 'C13', 'R20', 'R21', 'R22', 'R23', 'D5', 'J3'}   # RS485, fitted by default (D29)

def fixture_fee(n):
    for lim, f in [(29, 16.42), (99, 24.63), (199, 41.04), (349, 82.09), (499, 123.13), (10**6, 164.18)]:
        if n <= lim: return f
def is_tht(fp): return any(k in fp for k in ('THT', 'TerminalBlock', 'PinHeader', 'JST_PH'))
def refs(s):
    out = []
    for t in s.split(','):
        m = re.match(r'([A-Z]+)(\d+)-[A-Z]+(\d+)$', t)
        out += [f'{m[1]}{i}' for i in range(int(m[2]), int(m[3]) + 1)] if m else [t]
    return out
def price(rec, q):
    for p in rec['componentPrices']:
        if p['startNumber'] <= q and (p['endNumber'] == -1 or q <= p['endNumber']): return p['productPrice']
    return rec['componentPrices'][-1]['productPrice']

J = json.load(open('out/jlc_prices.json'))
pins = defaultdict(set)
for node in ET.parse('out/netlist.xml').getroot().iter('node'):
    pins[node.get('ref')].add(node.get('pin'))
G = {}   # group BOM rows by LCSC code: feeder fee and minimum buy are per part number
for r in csv.DictReader(open('out/bom.csv')):
    if r['DNP'] or not r['LCSC']: continue
    g = G.setdefault(r['LCSC'], dict(r, Refs='', Qty=0, Value=r['MPN'] if r['MPN'] != r['Value'] else r['Value']))
    g['Refs'] += (',' if g['Refs'] else '') + r['Refs']; g['Qty'] += int(r['Qty'])

smt_j = tht_j = xray = 0; ext = []; lines = []
for code, r in G.items():
    R = refs(r['Refs']); rec = J[code]
    kind = 'Basic' if rec['componentLibraryType'] == 'base' else ('PrefExt' if rec.get('preferredComponentFlag') else 'Ext')
    if kind == 'Ext': ext.append(code)
    j = sum(len(pins[x]) for x in R)
    if is_tht(r['Footprint']): tht_j += j
    else: smt_j += j
    xray += sum(1 for x in R if x in XRAY_REFS)
    lines.append((r, rec, kind))

def buy_qty(rec, q, n):
    return max(q * n + (rec.get('lossNumber') or 0), rec.get('leastPatchNumber') or 0)

def estimate(n, F):
    parts = sum(buy_qty(rec, int(r['Qty']), n) * price(rec, buy_qty(rec, int(r['Qty']), n)) for r, rec, _ in lines)
    xr_n = xray * n; xr_rate = next(p for lim, p in XRAY if xr_n <= lim)
    smt = smt_j * F['smt_joint'] * n
    fees = {
        'Setup + stencil + confirm': F['setup'] + F['stencil'] + F['confirm'] + F['panel'],
        'SMT joints': max(smt, F['min_smt_per_board'] * n),
        'Through-hole joints (manual)': tht_j * F['manual_joint'] * n + F['hand_labour'],
        'Feeder loading': len(ext) * F['feeder_ext'] + len(lines) * F['feeder_all'],
        'X-ray (module)': xr_n * xr_rate,
        'Fixture + packing': (fixture_fee(n) if F['fixture'] is None else F['fixture']) + F['packing'],
        'Components': parts,
        'Bare PCB (placeholder, see notes)': PCB_QUOTE.get(n, 0.0),
    }
    return fees

LEGEND = """Columns (part table):
  Type    Basic   = JLCPCB Basic part, permanently on a machine feeder: no feeder fee (Economic).
          PrefExt = 'Preferred Extended': Extended, but exempt from the feeder fee on Economic PCBA.
          Ext     = Extended: $3.07 feeder-loading fee once per part number per order (Economic).
  /brd    quantity per board.
  buy@N   quantity JLCPCB buys for N boards = max(/brd x N + JLCPCB's attrition allowance for that part,
          JLCPCB's minimum order for that part). E.g. a 0603 resistor at 10 boards: 1 x 10 + 10 = 20.
  $@N     buy@N x unit price at that quantity's price tier.
"""
NOTES = """Notes:
  * Bare PCB is a placeholder until layout: the irrigation board's JLCPCB quote (100 x 80 mm), an upper bound
    for this 37 mm-high board. Replace with the real quote after layout.
  * Shipping, tax and import duty not included.
  * JLCPCB's FAQ says Economic PCBA above 30 pieces needs panelising; the panel fee ($8.21) is included
    in the 100-board column.
  * No X-ray: the ESP32-C3-WROOM-02U has castellated edge pads (X-ray applies to leadless/BGA parts).
  * Not fitted (DNP) parts cost nothing: J4, J5, J6, J7 and the sensor options R19, C11.\n  * RS485 / Modbus is fitted; leaving it off saves the amount shown at the end (no feeder fees: all Basic\n    parts, and J3 is the same part number as J2/J12).
"""

def modbus():
    """Cost of the RS485 parts (U5, C13, R20-R23, D5, J3): what a board without Modbus saves."""
    rows = []
    for r in csv.DictReader(open('out/bom.csv')):
        R = [x for x in refs(r['Refs']) if x in MODBUS_REFS]
        if R and r['LCSC']:
            rows.append((dict(r, Refs=','.join(R)), len(R), sum(len(pins[x]) for x in R)))
    recs = {r['LCSC']: J.get(r['LCSC']) or __import__('jlc_query').q(r['LCSC'], 1)[0] for r, _, _ in rows}
    out = []
    for n in (10, 100):
        parts = sum(buy_qty(recs[r['LCSC']], q, n) * price(recs[r['LCSC']], buy_qty(recs[r['LCSC']], q, n)) for r, q, _ in rows)
        joints = sum(j * (ECON['manual_joint'] if is_tht(r['Footprint']) else ECON['smt_joint'])
                     for r, _, j in rows) * n
        shared = {r['LCSC'] for r in csv.DictReader(open('out/bom.csv'))
                  if r['LCSC'] and not r['DNP'] and any(x not in MODBUS_REFS for x in refs(r['Refs']))}
        ext_fee = sum(ECON['feeder_ext'] for r, _, _ in rows if recs[r['LCSC']]['componentLibraryType'] != 'base'
                      and not recs[r['LCSC']].get('preferredComponentFlag') and r['LCSC'] not in shared)
        out.append((n, parts, joints, ext_fee))
    return rows, out

if __name__ == '__main__':
    print(LEGEND)
    hdr = f'{"Refs":26} {"Value":22} {"LCSC":10} {"Type":7} {"/brd":>4} {"buy@10":>6} {"$@10":>7} {"buy@100":>7} {"$@100":>7}'
    print(hdr)
    for r, rec, kind in lines:
        q = int(r['Qty']); b10, b100 = buy_qty(rec, q, 10), buy_qty(rec, q, 100)
        print(f'{r["Refs"][:26]:26} {r["Value"][:22]:22} {r["LCSC"]:10} {kind:7} {q:4} {b10:6} {b10 * price(rec, b10):7.2f}'
              f' {b100:7} {b100 * price(rec, b100):7.2f}')
    print(f'\nPer board: {smt_j} SMT joints, {tht_j} through-hole joints, {len(lines)} part numbers '
          f'({len(ext)} Extended with fee).\n')
    E = [(n, F, estimate(n, F)) for n, F in COLUMNS]
    print(f'{"":32}' + ''.join(format(str(n) + ' ' + F['name'], '>24') for n, F, _ in E))
    for k in E[0][2]:
        print(f'{k:32}' + ''.join(f'{"$" + format(fees[k], ".2f"):>24}' for _, _, fees in E))
    print(f'{"TOTAL (excl. shipping)":32}' + ''.join(f'{"$" + format(sum(fees.values()), ".2f"):>24}' for _, _, fees in E))
    print(f'{"Per board":32}' + ''.join(f'{"$" + format(sum(fees.values()) / n, ".2f"):>24}' for n, _, fees in E))
    print('\nSame, per board:')
    for k in E[0][2]:
        print(f'{k:32}' + ''.join(f'{"$" + format(fees[k] / n, ".2f"):>24}' for n, _, fees in E))
    print(f'{"Per board":32}' + ''.join(f'{"$" + format(sum(fees.values()) / n, ".2f"):>24}' for n, _, fees in E))
    print('\n' + NOTES)
    print('Extended (fee-bearing on Economic):', ' '.join(ext))
    rows, M = modbus()
    print('\nRS485 / Modbus (D29): included above. A board without Modbus can leave these off and save:')
    print('  parts: ' + ', '.join(f"{r['Refs']} {r['Value']}" for r, _, _ in rows))
    for n, parts, joints, fee in M:
        tot = parts + joints + fee
        print(f'  {n:3} boards: components ${parts:.2f} + assembly joints ${joints:.2f} + feeder fees ${fee:.2f}'
              f' = ${tot:.2f}  (${tot / n:.2f} per board)')
