#pylint:disable= C0114, C0116, W0401, W0614, W0621, W0108, W0212, C3001,C0413, W0107, R0915


from pathlib import Path
from distutils.dir_util import copy_tree
import sys
import os
import copy
from pprint import pprint
# import sysconfig
import pytest
from natlinkcore import config

from natlinkcore.configure import natlinkconfig_cli
from natlinkcore.configure import natlinkconfigfunctions

thisDir = Path(__file__).parent
configDir = os.path.normpath(thisDir/'../src/natlinkcore/configure')
# sys.path.insert(0, configDir)
# print(f'sys.path: {sys.path}')

# import natlinkconfig_cli
# import natlinkconfigfunctions

def return_true(*args):
    return True

@pytest.fixture
def cli():
    """return the (non interactive) cli
    """
    _cli = natlinkconfig_cli._main()
    return _cli



def test_run_natlinkconfig_cli():
    _nc = natlinkconfigfunctions.NatlinkConfig()
    _config = _nc.Config
    _doc_path = _nc.documents_path
    _home_path = _nc.home_path
    _natlinkconfig_path = _nc.natlinkconfig_path
    print(f'natlinkconfig_path: {_natlinkconfig_path}')
    _cli = natlinkconfig_cli._main()
    print(f'natlinkconfig_cli: {_cli}')
    
    pass

def test_config_cli(cli, capsys):
    """test the basics of the natlinkconfig_cli program
    """
    cli.do_i('dummy')
    output = capsys.readouterr().out.rstrip()
    
    assert output.find('NatlinkDirectory') > 0
    
def test_check_elevated_mode_tt(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result True
    """
    def return_true():
        return True
    # def return_false():
    #     return False
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    monkeypatch.setattr(cli, 'want_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is True
    
def test_check_elevated_mode_ff(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result True
    """
    # def return_true():
    #     return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_false)
    monkeypatch.setattr(cli, 'want_elevated', return_false)
    result = cli.check_elevated_mode()
    assert result is True
    
def test_check_elevated_mode_tf(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result False
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    monkeypatch.setattr(cli, 'want_elevated', return_false)
    result = cli.check_elevated_mode()
    assert result is False
    
def test_check_elevated_mode_ft(cli, monkeypatch):
    """try the variants of am_elevated and want_elevated
    result False
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_false)
    monkeypatch.setattr(cli, 'want_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is False

def test_check_elevated_mode_with_do_F(cli, monkeypatch):
    """try the variants of am_elevated overridden by do_F
    result is then True (after first a False)
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_false)
    monkeypatch.setattr(cli, 'want_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is False
    # now force accepting am_elevated:
    cli.do_F('dummy')
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    result = cli.check_elevated_mode()
    assert result is True
    
def test_check_elevated_mode_with_do_f(cli, monkeypatch):
    """try the variants of am_elevated overridden by do_F
    result is then True (after first a False)
    """
    def return_true():
        return True
    def return_false():
        return False
    monkeypatch.setattr(cli, 'am_elevated', return_true)
    monkeypatch.setattr(cli, 'want_elevated', return_false)
    result = cli.check_elevated_mode()
    assert result is False
    # now force accepting am_elevated to false, non elevated
    cli.do_f('dummy')
    monkeypatch.setattr(cli, 'am_elevated', return_false)
    result = cli.check_elevated_mode()
    assert result is True
    

def test_prefix_home_appdata(cli):
    """check the existence of environment variables for shortening the path of a directory
    
    No "~" any more, use "localappdata". Most used for natlink config files!!!
    Also check "appdata", which expands to the roaming appdata directory (Handle with care!!!)
    
    Check this with values on your computer, monkeypatching does not seem to worth the trouble...
    """
    to_prefix = config.expand_path('%localappdata%\\Microsoft')
    prefixed  = cli.Config.prefix_home_appdata(to_prefix)
    assert prefixed == '%localappdata%\\Microsoft'

    expanded = config.expand_path(prefixed)
    assert os.path.isdir(expanded)
    
    # check %appdata% (roaming)
    to_prefix = config.expand_path('%appdata%\\Microsoft')
    prefixed  = cli.Config.prefix_home_appdata(to_prefix)
    assert prefixed == '%appdata%\\Microsoft'

    expanded = config.expand_path(prefixed)
    assert os.path.isdir(expanded)
    
    # check %personalhome% (~)
    to_prefix = config.expand_path('%personalhome%\\Documents')
    prefixed  = cli.Config.prefix_home_appdata(to_prefix)
    assert prefixed == '%personalhome%\\Documents'

    expanded = config.expand_path(prefixed)
    assert os.path.isdir(expanded)
    assert to_prefix == expanded
    
    # expand the previous "~":
    prefixed = "~\\Documents"
    expanded = config.expand_path(prefixed)
    assert os.path.isdir(expanded)
    prefixed_new  = cli.Config.prefix_home_appdata(expanded)
    assert prefixed_new == '%personalhome%\\Documents'
    
    
def test_enable_disable_vocola(vocola_config_setup, cli, monkeypatch):
    """enable and disable vocola.
    
    ALSO: trying the test procedure from conftest.py
    ASSUME: vocola is already a valid module!!! in this test pipping the package vocola2
            is skipped...
    """
    monkeypatch.setattr(cli.Config, "pip_package", return_true)
    natlink_config_dir, vocola_userdir = vocola_config_setup
    
    print(f'natlink_config_dir: {natlink_config_dir}')
    print(f'vocola_userdir: {vocola_userdir}')
    assert os.path.isdir(natlink_config_dir)
    assert os.path.isdir(vocola_userdir)
    assert os.path.isfile(natlink_config_dir/'natlink.ini')

    #copy a simple sample, only enx files
    copy_tree(str(thisDir/"samples"/"vocola_userdir_1"),str(vocola_userdir))
    
    folder_dict = get_folder_dict(vocola_userdir)
    # should be equal to above directory vocola_userdir_2
    exp_dict = {'_vocola.vcl': ['include Unimacro.vch;',
                                '# vocola file for alternate language: enx',
                                'Paste Test = HeardWord("Paste", "Box");',
                                'prompt test = ">>>QH>>> ";'],
                'firefox.vcl': ['include Unimacro.vch;',
                                '# vocola file for alternate language: enx',
                                '# Voice commands for firefox',
                                'go to search = {ctrl+t}{ctrl+k};',
                                'view source = {ctrl+u};']}
    
    
    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AT START OF test_enable_disable_vocola:')
        print('If this is the correct start content of vocola_userdir')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False

    
    cli.do_v(vocola_userdir)
    assert cli.Config.status.vocolaIsEnabled()

   # check new state:
    folder_dict = get_folder_dict(vocola_userdir)
    exp_dict_uniactions = copy.copy(folder_dict)
    exp_dict_uniactions['Uniactions.vch'] = '403 lines'  # only vch include file added in directory

    if exp_dict_uniactions != folder_dict:
        print('\n=================================\n')
        print('AFTER enable_vocola (do_v):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False

 

    # basic test with 
    cli.do_V(None)
    result = cli.Config.status.vocolaIsEnabled()
    assert not result
    
    folder_dict = get_folder_dict(vocola_userdir)

    if exp_dict_uniactions != folder_dict:
        print('\n=================================\n')
        print('AFTER disable_vocola (do_V):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False
    
    
    
    cli.do_v(vocola_userdir)
    assert cli.Config.status.vocolaIsEnabled()
    
    assert cli.Config.status.getVocolaTakesUniactions() is False

    folder_dict = get_folder_dict(vocola_userdir)

    if exp_dict_uniactions != folder_dict:
        print('\n=================================\n')
        print('AFTER second enable_vocola (do_v):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False


    
    ## try to activate this option
    cli.do_a(vocola_userdir)
    
    assert cli.Config.status.getVocolaTakesUniactions() is True

    folder_dict = get_folder_dict(vocola_userdir)

    exp_dict_includeline = {'Uniactions.vch': '403 lines',
                           '_vocola.vcl': ['include Uniactions.vch;',
                                         '# vocola file for alternate language: enx',
                                         'Paste Test = HeardWord("Paste", "Box");',
                                         'prompt test = ">>>QH>>> ";'],
                         'firefox.vcl': ['include Uniactions.vch;',
                                         '# vocola file for alternate language: enx',
                                         '# Voice commands for firefox',
                                         'go to search = {ctrl+t}{ctrl+k};',
                                         'view source = {ctrl+u};']}


    if exp_dict_includeline != folder_dict:
        print('\n=================================\n')
        print('AFTER enable VocolaTakesUniactions (do_a):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False



    ## try to deactivate this option
    # NOTE: this option also removes Uniactions.vch
    cli.do_A(vocola_userdir)
    assert cli.Config.status.getVocolaTakesUniactions() is False

    folder_dict = get_folder_dict(vocola_userdir)

    exp_dict = {'_vocola.vcl': ['# vocola file for alternate language: enx',
                 'Paste Test = HeardWord("Paste", "Box");',
                 'prompt test = ">>>QH>>> ";'],
                'firefox.vcl': ['# vocola file for alternate language: enx',
                                '# Voice commands for firefox',
                                'go to search = {ctrl+t}{ctrl+k};',
                                'view source = {ctrl+u};']}

    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER disable VocolaTakesUniactions (do_A):')
        print('If this is the correct content of vocola_userdir now')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False
    
    
    folder_dict = get_folder_dict(vocola_userdir)
    assert exp_dict == folder_dict

    cli.do_V(None)
    assert cli.Config.status.vocolaIsEnabled() is False
    assert not result   

    folder_dict = get_folder_dict(vocola_userdir)
    assert exp_dict == folder_dict


    ## try to activate this option when vocola is disabled:
    ## option passes, only config file is checked.
    cli.do_a(vocola_userdir)
    result = cli.Config.status.getVocolaTakesUniactions()
    assert not result

    ## try to deactivate this option when vocola is disabled:
    cli.do_A(vocola_userdir)
    assert cli.Config.status.getVocolaTakesUniactions() is False
    
def test_vocola_include_lines(vocola_config_setup, cli, monkeypatch):
    """check if the include lines are inserted/deleted with the option a/A

    it is about the functions: includeUniactionsVchLineInVocolaFiles and removeUniactionsVchLineInVocolaFiles
    in natlinkconfigfunctions.py.

    ASSUME: vocola is already a valid module!!! in this test pipping the package vocola2
            is skipped...
    """
    join, isfile = os.path.join, os.path.isfile
    monkeypatch.setattr(cli.Config, "pip_package", return_true)
    natlink_config_dir, vocola_userdir = vocola_config_setup
    print(f'natlink_config_dir: {natlink_config_dir}')
    print(f'vocola_userdir: {vocola_userdir}')
    assert os.path.isdir(natlink_config_dir)
    assert os.path.isdir(vocola_userdir)
    assert os.path.isfile(natlink_config_dir/'natlink.ini')

    #copy a sample enx and nld, which should end up in empty files or files
    #only containting the wanted include line...
    copy_tree(str(thisDir/"samples"/"vocola_userdir_2"),str(vocola_userdir))
    
    folder_dict = get_folder_dict(vocola_userdir)
    # should be equal to above directory vocola_userdir_2
    exp_dict = {'empty.vcl': [],
    'nld---empty_nld.vcl': [],
    'nld---oldlines_nld.vcl': ['include Unimacro.vch;',
                               'include ../Unimacro.vch;',
                               'include usc.vch;',
                               'include Uniactions.vch;'],
    'oldlines.vcl': ['include Unimacro.vch;',
                     'include ../Unimacro.vch;',
                     'include usc.vch;',
                     'include Uniactions.vch;',
                     'include Unimacro.vch;']}
                
    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AT START OF test_vocola_include_lines:')
        print('If this is the correct start content of vocola_userdir')
        print('please change your test file above accordingly\n')

        pprint(folder_dict)
        assert False

    assert cli.Config.status.vocolaIsEnabled() is False
    includeFile = join(vocola_userdir, 'Uniactions.vch')
    assert not isfile(includeFile)
    cli.do_v(vocola_userdir)
    assert cli.Config.status.vocolaIsEnabled()
    assert isfile(includeFile)  # should have been copied, irrespective of the VocolaTakesUniactions option
    result = cli.Config.status.getVocolaTakesUniactions()
    assert result is False
    
    
    folder_dict = get_folder_dict(vocola_userdir)
    
    exp_dict = {'Uniactions.vch': '403 lines',
                'empty.vcl': [],
                'nld---empty_nld.vcl': [],
                'nld---oldlines_nld.vcl': [],
                'oldlines.vcl': []}  
    
    
    if exp_dict != folder_dict:
        print('\n=================================\n')
        print('AFTER do_v: if this is the correct content of vocola_userdir in this state')
        print('Please change your test file accordingly\n')
        
        pprint(folder_dict)
        assert False
    
    
def get_folder_dict(folderpath):
    """return the contenst in a dict, assume all text files
    
    rstrip all lines
    """
    join = os.path.join
    D = {}
    folderdir = str(folderpath)
    len_prefix = len(folderdir)
    
    for dirpath, _dirnames, files in os.walk(folderdir):
        # print(f'Found directory: {dirpath}')
        subdir = dirpath[len_prefix+1:]
        key_prefix = f'{subdir}---' if subdir else ''
        for fi in files:
            with open(join(dirpath, fi), 'r', encoding='utf-8') as f:
                lines = [line.rstrip(' \n') for line in f if line.strip()]
            D[key_prefix + fi] = lines if len(lines) < 10 else f'{len(lines)} lines'
            
    return D
    
def _main():
    """run pytest for this module
    """
    # pytest.main(['-s', 'test_natlinkconfig.py::test_vocola_include_lines'])
    pytest.main(['-s', 'test_natlinkconfig.py'])

 
if __name__ == "__main__":
    _main()

