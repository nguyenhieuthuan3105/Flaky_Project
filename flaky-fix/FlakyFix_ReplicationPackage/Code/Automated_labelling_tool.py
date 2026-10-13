import difflib as diff
import pandas as pd
import re as regex

def get_diff(test_case):
    diff_ = diff.ndiff(test_case['flaky_version'].split('\n'), test_case['fixed_version'].split('\n'))
    diff_ = '\n'.join([dif for dif in diff_ if not dif.startswith('?')])
    return diff_

def get_diff_added_deleted_lines(test_case):
    diff_ = diff.ndiff(test_case['flaky_version'].split('\n'), test_case['fixed_version'].split('\n'))
    diff_lines = '\n'.join([dif for dif in diff_ if dif.startswith('- ') or dif.startswith('+ ')])
    return diff_lines

def get_deleted_lines(test_case):
    additions = ''
    for dif in diff.ndiff(test_case['flaky_version'].split('\n'), test_case['fixed_version'].split('\n')):
        if dif.startswith('- '):
            additions += dif + '\n'
    return additions.strip()

def get_added_lines(test_case):
    additions = ''
    for dif in diff.ndiff(test_case['flaky_version'].split('\n'), test_case['fixed_version'].split('\n')):
        if dif.startswith('+ '):
            additions += dif + '\n'
    return additions.strip()

def get_deleted_tokens(test_case):
    deletions = ''
    for dif in diff.ndiff(test_case['flaky_version'], test_case['fixed_version']):
        if dif.startswith('- ') or '\n' in dif:
            deletions += dif.replace('- ', '').replace('+ ', '')
    return deletions.strip()

def get_added_tokens(test_case):
    additions = ''
    for dif in diff.ndiff(test_case['flaky_version'], test_case['fixed_version']):
        if dif.startswith('+ ') or '\n' in dif:
            additions += dif.replace('+ ', '').replace('- ', '')
    return additions.strip()

def auto_generate_labels(test_case):
    added_tokens = test_case['added_tokens'].lower()
    deleted_tokens = test_case['deleted_tokens'].lower()
    added_lines = test_case['added_lines'].lower()
    deleted_lines = test_case['deleted_lines'].lower()

    label = ''

    if added_tokens.replace(' ', '') == deleted_lines.replace(' ', ''):
        label += 'no_change' + ','
    if regex.search('=\s*0;\s*', added_tokens) or (regex.search('=\s*0\s*;', added_lines) and regex.search('=\s*0', added_tokens)) or regex.search('\.(reset|clear|remove|purge).*?\(.*?\)', added_lines):
        label += 'reset_variable' + ','
    if 'sortfield' in added_lines or 'sort_properties' in added_lines or 'sorted' in added_lines or '.sort' in added_lines or 'order by' in added_tokens:
        label += 'reorder_data' + ','
    if regex.search('jsonparser\s*\(\s*\)\s*;', added_lines) or 'jsonparser.' in added_lines:
        label += 'change_data_format' + ','
    if ('map' in deleted_lines and 'hashmap' in added_lines and 'hash' in added_tokens) or ('map' in deleted_lines and 'linkedhashmap' in added_lines and 'linkedhash' in added_tokens) or ('hashmap' in deleted_lines and 'linkedhashmap' in added_lines and 'linked' in added_tokens) or ('set' in deleted_lines and 'hashset' in added_lines and 'hash' in added_tokens) or ('set' in deleted_lines and 'linkedhashset' in added_lines and 'linkedhash' in added_tokens) or ('hashset' in deleted_lines and 'linkedhashset' in added_lines and 'linked' in added_tokens) or (regex.search('(map|set)(\s|<)', added_lines) and not regex.search('(map|set)(\s|<)', deleted_lines)) or (regex.search('new\s(map|set|hashmap|hashset|linkedhashmap|linkedhashset|treemap|treeset)', added_lines)) or '.aslist' in added_lines:
        label += 'change_data_structure' + ','
    if regex.search('\.getmethods\s*\(\s*\)', deleted_lines) and regex.search('=\s*getmethods\s*\(', added_lines):
        label += 'call_static_method' + ','
    if ('assertequals' in deleted_lines and 'match.that(s).isequalto' in added_lines) or ('.matches' in added_lines):
        label += 'string_matching' + ','
    if ('assertequals' in deleted_lines and (regex.search('asserttrue\(.*?\.equals', added_lines) or regex.search('asserttrue\(.*?\.contains', added_lines) or regex.search('asserttrue\(.*?==', added_lines))) or ('assertequals' in added_lines and (regex.search('asserttrue\(.*?\.equals', deleted_lines) or regex.search('asserttrue\(.*?==', deleted_lines))) or ('containsexactly' in deleted_lines and 'containsonly' in added_lines) or ('containsexactly' in added_lines and 'containsonly' in deleted_lines):
        label += 'change_assertion' + ','
    if (('assertequals' in deleted_lines or 'assertthat' in deleted_lines or 'asserttrue' in deleted_lines) and ('assertjsonstringequals' in added_lines or 'jsonassert.assertequals' in added_lines or 'assertjsonequalsnonstrict' in added_lines)):
        label += 'change_assertion' + ','
    if 'ziptomap' in added_lines:
        label += 'change_assertion' + ','
    if ('assertjsonequalsnonstrict' in added_lines) or ('containsexactly' in deleted_lines and regex.search('contains\s*\(', added_lines)) or ('contains' in deleted_lines and 'containsinanyorder' in added_lines) or ('containsexactly' in deleted_lines and 'containsexactlyinanyorder' in added_lines) or ('isof' in deleted_lines and 'hascontentinanyorder' in added_lines):
        label += 'change_condition' + ','
    if regex.search('try\s*{', added_tokens):
        label += 'handle_exceptions' + ','
    if regex.search('throws\s*\D*exception', deleted_lines) and not regex.search('throws\s*\D*exception', added_lines):
        label += 'handle_exceptions' + ','
    if regex.search('throws\s*\D*exception', added_lines) and not regex.search('throws\s*\D*exception', deleted_lines):
        label += 'handle_exceptions' + ','    
    if regex.search('catch\s*\(\s*\D+exception', deleted_lines) and regex.search('catch\s*\(\s*exception', added_lines):
        label += 'handle_exceptions'
    if regex.search('catch\s*\(\s*\D+exception', added_lines) and regex.search('catch\s*\(\s*exception', deleted_lines):
        label += 'handle_exceptions' + ','
    if regex.search('catch\s*\(\s*\D+exception', added_lines) and regex.search('catch\s*\(\s*exception', deleted_lines):
        label += 'handle_exceptions' + ','
    if sorted(list(deleted_tokens.replace(' ', ''))) == sorted(list(added_tokens.replace(' ', ''))) and added_tokens.replace(' ', '') != ''  and deleted_lines.replace(' ', '') != '':
        label += 'reorder_parameters' + ','
    if 'select *' in deleted_lines and 'select *' not in added_lines:
        label += 'reorder_data' + ',' # label += 'expand_select' + ','
    if regex.search('(\&\&|\|\|)', deleted_tokens):
        if regex.search('(\&\&|\|\|)', added_tokens):
            label += 'change_condition' + ','
        else:
            label += 'change_condition' + ','
    if regex.search('(\&\&|\|\|)', added_tokens):
        if regex.search('(\&\&|\|\|)', deleted_tokens):
            label += 'change_condition' + ','
        else:
            label += 'change_condition' + ','
    if 'thread.sleep' in added_tokens:
        label += 'sleep' + ','
    if 'timezone' in added_tokens:
        label += 'change_timezone' + ','
    if 'timeout' in added_tokens:
        label += 'set_timeout' + ','
    rgx_added = regex.search('(\s+|\.)assert[a-z]+\s*\(', added_lines)
    rgx_deleted = regex.search('(\s+|\.)assert[a-z]+\s*\(', deleted_lines)
    if rgx_added and rgx_deleted:
        if rgx_added[0] != rgx_deleted[0] and 'change_assertion' not in label and 'change_assertion' not in label:
            label += 'change_assertion' + ','

    label = label if not label.endswith(',') else label[:-1]

    if label == '':
        label = 'misc'
    
    return label

fixes = pd.read_csv('../Data/IDOFT_fixed_random.csv')
fixes['diff'] = fixes.apply(get_diff, axis=1)
fixes['added_deleted_lines'] = fixes.apply(get_diff_added_deleted_lines, axis=1)
fixes['deleted_lines'] = fixes.apply(get_deleted_lines, axis=1)
fixes['added_lines'] = fixes.apply(get_added_lines, axis=1)
fixes['deleted_tokens'] = fixes.apply(get_deleted_tokens, axis=1)
fixes['added_tokens'] = fixes.apply(get_added_tokens, axis=1)
fixes['Auto_labels'] = fixes.apply(auto_generate_labels, axis=1)

fixes.to_csv('../Results/IDoFT_flaky_fixes_diff.csv')