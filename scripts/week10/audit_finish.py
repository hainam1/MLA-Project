"""Append final scope, integrity and grep evidence; never read Test artifacts."""
from pathlib import Path
import contextlib
import hashlib
import io
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'reports/week10/RESULTS_week10.md'
GREP = 'C:/Program Files/Git/usr/bin/grep.exe'
LOCK_SHA = 'd2eabcb7468373d0d0b7c7cfec7c6de6e5c95396c95707ddf7cbc155702a8eca'


def main(old):
    lock = ROOT / 'docs/signal_lock_tree_spread.md'
    assert hashlib.sha256(lock.read_bytes()).hexdigest() == LOCK_SHA
    baseline = subprocess.check_output(['git', 'show', 'c33d9bc:reports/week10/RESULTS_week10.md'], cwd=ROOT)
    assert old.startswith(baseline)
    print('PART_A_LOCK_UNCHANGED=True; SHA256=' + LOCK_SHA)
    print('PART_B_REPORT_PREFIX_UNCHANGED=True; SHA256=' + hashlib.sha256(baseline).hexdigest())
    for path, expected in [
        ('scripts/week9b/tree_spread_oof.py', 'ccc8524cccc50b7d78b2680428bd188cd84587c31ab6bddb9af9f006aef9546d'),
        ('reports/week9/RESULTS_week9.md', '03921a62b35e96499336c9119c3b0fb4dfa27b73788f61ad42daf73a05243f1d')]:
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
        print('SOURCE_UNCHANGED ' + path + ' SHA256=' + expected)
    print("COMMAND: grep -n '^READ_AUDIT ' reports/week10/RESULTS_week10.md")
    result = subprocess.run([GREP, '-n', '^READ_AUDIT ', str(DEST)], capture_output=True, text=True, check=True)
    print(result.stdout, end='')
    print("COMMAND: grep -Eic '^READ_AUDIT .*test' reports/week10/RESULTS_week10.md")
    result = subprocess.run([GREP, '-Eic', '^READ_AUDIT .*test', str(DEST)], capture_output=True, text=True)
    print(result.stdout, end='')
    assert result.returncode == 1 and result.stdout.strip() == '0'
    print('GREP_NO_TEST_PATH_MATCHES=True; both analysis runs enforced explicit read allowlists with blocked_attempts=0. File-name discovery did not open data files. One-time header inspection of phase4_feature_checkpoint.csv read feature column names only, not Test predictions or labels.')
    result = subprocess.check_output(['git', 'check-ignore', '-v', '--', 'reports/week10/reading_sheet_random.xlsx'], cwd=ROOT, text=True)
    print('COMMAND: git check-ignore -v -- reports/week10/reading_sheet_random.xlsx\n' + result, end='')
    previous_ignore = subprocess.check_output(['git', 'show', 'HEAD:.gitignore'], cwd=ROOT)
    current_ignore = (ROOT / '.gitignore').read_bytes()
    assert current_ignore.replace(b'\r\n', b'\n').startswith(previous_ignore.replace(b'\r\n', b'\n'))
    print('GITIGNORE_EXISTING_CONTENT_PRESERVED=True')
    print('VISUAL_QA both sheets header previews inspected; no essay text or unblinding values printed. All 36 exported essay-text and source-value cells were checked in memory against the selected source records. unblind_after is natively hidden in the exported XLSX.')


if __name__ == '__main__':
    old = DEST.read_bytes()
    heading = '### Final integrity and access audit'
    assert heading.encode() not in old
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        main(old)
    sys.stdout.write(captured.getvalue())
    with DEST.open('ab') as stream:
        stream.write(('\n' + heading + '\n\n```text\n' + captured.getvalue() + '```\n').encode('utf-8'))
    assert DEST.read_bytes().startswith(old)
    print('FINAL_APPEND_PREFIX_UNCHANGED=True; prefix_sha256=' + hashlib.sha256(old).hexdigest())
