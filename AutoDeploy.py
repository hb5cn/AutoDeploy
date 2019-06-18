# !/usr/local/python
# -*- coding: UTF-8 -*-

import os
import re
import time
import copy
import flask
import shutil
import smtplib
import urllib3
import logging
import traceback
import threading
import subprocess
import logging.handlers
# from urllib.parse import quote
from xml.etree import ElementTree
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

app = flask.Flask(__name__)


class AutoDeploy(object):
    def __init__(self):
        self.home_dir = os.path.split(os.path.realpath(__file__))[0]
        os.chdir(self.home_dir)

        # 初始化日志模块
        self.mainlog = logging.getLogger()
        self.mainlog.setLevel(logging.INFO)
        # 定义日志文件输入的路径及文件名
        logfile = '{:s}/LOG/AutoTestLog.log'.format(self.home_dir)
        if os.path.exists(logfile):
            os.remove(logfile)

        # 设置一个本地打印的句柄
        formatter = logging.Formatter('%(asctime)s %(funcName)s %(lineno)d %(levelname)s  %(message)s')

        log_file_handler = logging.handlers.TimedRotatingFileHandler(filename=logfile, when="MIDNIGHT", interval=1,
                                                                     backupCount=30)
        log_file_handler.suffix = "%Y-%m-%d.log"
        log_file_handler.setFormatter(formatter)
        self.mainlog.addHandler(log_file_handler)
        # 设置一个屏幕打印的句柄
        self.logscr = logging.StreamHandler()
        self.logscr.setLevel(logging.INFO)
        self.logscr.setFormatter(formatter)
        self.mainlog.addHandler(self.logscr)

    def changeconfig(self, config_file, product_name, svn_path, boss_path, billing_path, other_path, boss_config,
                     billing_config, other_config, boss_changed, billing_changed, other_changed):
        """
        修改自动升级工具config里的内容。

        :param config_file: config_auto_update_v1.9.1.cfg
        :param product_name: api
        :param svn_path: svn://123.57.180.25/dailyproduct/boss/20190514111130
        :param boss_path: /opt/tomcat227_8083/webapps/
        :param billing_path: /opt/tomcat227_8083/webapps/
        :param other_path:
        :param boss_config: svn://svn.uincall.com:3695/project/04_测试/99 部门管理/01 文档管理/10 自动化项目/
        05 测试环境配置文件备份/101.200.111.227/227-8083/227-8083-bossautodeploy-xtboss-classes
        :param billing_config: svn://svn.uincall.com:3695/project/04_测试/99 部门管理/01 文档管理/10 自动化项目/
        05 测试环境配置文件备份/101.200.111.227/227-8083/227-8083-bossautodeploy-xtbilling-classes
        :param other_config:
        :param boss_changed: no
        :param billing_changed: no
        :param other_changed: no
        :return:
        """
        # config路径。
        if config_file in os.listdir(self.home_dir):
            config_path = os.path.join(self.home_dir, config_file)
        elif os.path.exists(config_file):
            config_path = config_file
        else:
            self.mainlog.error('Can\'t find %s' % config_file)
            return 'error Can\'t find config_file'

        # 获取config文件原始内容。
        assert os.path.exists(config_path), '{0} is not exists.'.format(config_path)
        fp = open(config_path, encoding='utf-8')
        config_content = fp.readlines()
        fp.close()
        newcontent = ''

        for content in config_content:
            content = str(content)
            if content.find('#') >= 0:
                newcontent += content
                continue

            # 将product_name进行替换。
            if content.find('product_name=') >= 0:
                self.mainlog.info('Change Product : {0:s}'.format(product_name))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(product_name))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), product_name)

            # 将patchsvn_path=进行替换。
            elif content.find('patchsvn_path=') >= 0:
                self.mainlog.info('Change Svn_Path : {0:s}'.format(svn_path))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(svn_path))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), svn_path)

            # 将install_path_xtboss=进行替换。
            elif content.find('install_path_xtboss=') >= 0:
                self.mainlog.info('Change install_path_xtboss : {0:s}'.format(boss_path))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(boss_path))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), boss_path)

            # 将install_path_xtbilling=进行替换。
            elif content.find('install_path_xtbilling=') >= 0:
                self.mainlog.info('Change install_path_xtbilling : {0:s}'.format(billing_path))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(billing_path))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), billing_path)

            # 将install_path_other=进行替换。
            elif content.find('install_path_other=') >= 0:
                self.mainlog.info('Change install_path_other : {0:s}'.format(other_path))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(other_path))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), other_path)

            # 将config_svnpath_xtboss=进行替换。
            elif content.find('config_svnpath_xtboss=') >= 0:
                self.mainlog.info('Change config_svnpath_xtboss : {0:s}'.format(boss_config))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(boss_config))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), boss_config)

            # 将config_svnpath_xtbilling=进行替换。
            elif content.find('config_svnpath_xtbilling=') >= 0:
                self.mainlog.info('Change config_svnpath_xtbilling : {0:s}'.format(billing_config))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(billing_config))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), billing_config)

            # 将config_svnpath_other=进行替换。
            elif content.find('config_svnpath_other=') >= 0:
                self.mainlog.info('Change config_svnpath_other : {0:s}'.format(other_config))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(other_config))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), other_config)

            # 将config_changed_xtboss=进行替换。
            elif content.find('config_changed_xtboss=') >= 0:
                self.mainlog.info('Change config_changed_xtboss : {0:s}'.format(boss_changed))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(boss_changed))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), boss_changed)

            # 将config_changed_xtbilling=进行替换。
            elif content.find('config_changed_xtbilling=') >= 0:
                self.mainlog.info('Change config_changed_xtbilling : {0:s}'.format(billing_changed))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(billing_changed))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), billing_changed)

            # 将config_changed_other=进行替换。
            elif content.find('config_changed_other=') >= 0:
                self.mainlog.info('Change config_changed_other : {0:s}'.format(other_changed))
                source_str = content.split('=')[1].strip('\r\n')
                try:
                    assert source_str is not ''
                    content = content.replace(source_str, "'{0:s}'".format(other_changed))
                except AssertionError:
                    content = "{:s}'{:s}'\n".format(content.strip('\r\n'), other_changed)

            newcontent += content

        # 将替换后的全部内容写入原文件
        fp = open(config_path, 'rb+')
        fp.write(newcontent.encode('utf-8'))
        fp.close()

        return 'Change done.'

    def callautoupdate(self, updatefile, updatemode, tomcatpath, project, isnext, jenkinsurl):
        self.cleantomcatlog(tomcatpath)
        http = urllib3.PoolManager()
        # 创建shell执行语句。
        cmd = '{:s} {:s}'.format(updatefile, updatemode)
        self.mainlog.info('Begin update')
        self.mainlog.info('bash is : %s' % cmd)

        # 开始执行更新版本。
        update = subprocess.Popen(cmd.encode('gbk'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        self.mainlog.info('Sub process pid is : %s' % str(update.pid))
        f_autoupdate = open('tmp_update.log', 'w')
        f_update_cont = ''
        while True:
            up_status = 0
            nextline = update.stdout.readline().decode(encoding='utf-8')
            self.mainlog.info(nextline.strip())
            f_update_cont += nextline
            # if update.poll() == 0 and nextline.strip() == '':
            if nextline.strip().lower().find('has been successful') >= 0:
                up_status = 1
            elif nextline.strip().lower().find('sorry') >= 0:
                up_status = 2
            if up_status != 0:
                self.mainlog.info('the exit code is : %s' % str(up_status))
                # noinspection PyBroadException
                try:
                    self.mainlog.info('Kill sub process')
                    time.sleep(3)
                    os.system('/bin/bash killsh.sh %s' % updatefile)
                except Exception:
                    self.mainlog.error(traceback.format_exc())
                break

        f_autoupdate.write(f_update_cont)
        f_autoupdate.close()

        if 1 == up_status:
            os.remove('tmp_update.log')
        elif 2 == up_status:
            self.mainlog.info('Begin Send autoupdate tool error email.')
            self.sendemail('admin', '升级工具升级失败，请参看附件', '升级工具升级失败', 'tmp_update.log')
            os.remove('tmp_update.log')
            return 'error'

        # 开始查日志判断是否正常启动。
        catalinalogpath = os.path.join(tomcatpath, 'logs/catalina.out')
        boss_result = self.judgebossrun(catalinalogpath, project)

        if 'error' == str(boss_result):
            # 如果启动失败，则给admin用户发送邮件。
            catalinalog_path = os.path.join(tomcatpath, 'logs/catalina.out')
            fp_catalina = open(catalinalog_path, encoding='utf-8')
            self.mainlog.info('Begin Send tomcat startup error email.')
            self.sendemail('admin', fp_catalina.read(), 'Tomcat启动失败', catalinalog_path)
            return 'error'

        # 开始回调jenkins，执行自动化脚本。
        if 'true' == isnext:
            self.mainlog.info('Begin Call Jenkins Run RF.')
            self.mainlog.info('Jenkins Url is : %s' % str(jenkinsurl))
            http.request('GET', jenkinsurl)

        # 开始删除自动升级工具文件夹里旧的文件夹。
        self.cleanupautoupfloder(updatefile)

        return boss_result

    def cleantomcatlog(self, tomcatpath):
        log_path = os.path.join(tomcatpath, 'logs')
        assert os.path.exists(log_path)
        # 将logs下的文件列出来。
        logfile_list = os.listdir(log_path)
        if 'catalina.out' in logfile_list:
            # 找到catalina.out说明是tomcat的日志目录，进行清空。
            self.mainlog.info('Remove logs file.')
            rm_cmd = 'rm -f {}/*'.format(log_path)
            self.mainlog.info('bash is : %s' % rm_cmd)
            os.system(rm_cmd)
        elif len(logfile_list).__eq__(0):
            # 如果目录是空的，说明已经清理过了。
            pass
        else:
            # 没找到catalina.out说明给出的tomcat路径是错误的，或者tomcat里不是默认布局。
            raise Exception('The logs floder is not in ', tomcatpath)

    def judgebossrun(self, catalinalogpath, project):
        self.mainlog.info('Begin judge boss is run')
        project = list(project)
        num_list = len(project)
        new_project = copy.copy(project)
        while True:
            log_status = ''
            # 判断启动完成
            fp_catalina = open(catalinalogpath, encoding='utf-8')
            fp_catalina_content = fp_catalina.read()
            for i in range(0, num_list):
                re_return = self.refinished(fp_catalina_content, project)
                if 'project all finished' == str(re_return):
                    self.mainlog.info('project all finished')
                    log_status = 'done'
                else:
                    self.mainlog.info(re_return)
                a = new_project[0]
                for j in range(0, num_list - 1):
                    new_project[j] = new_project[j + 1]
                new_project[-1] = a
                project = copy.copy(new_project)

            # 判断是不是已经出现Exception，表示已经结束但是项目启动有问题。
            re_str = r'Exception|error'
            re_result = re.search(re_str, str(fp_catalina_content))
            if re_result:
                self.mainlog.error('Tomcat Start Fail.')
                return 'error'
            if 'done' == log_status:
                self.mainlog.info('Tomcat Start Success.')
                return 'success'
            fp_catalina.close()
            time.sleep(5)

    def refinished(self, fp_catalina_content, projrct):
        """
        递归判断各个项目有没有正确结束。
        :param fp_catalina_content:F:/PythonTest/AutoDeployWithJenkins(Uincall)/catalina.out
        :param projrct:'xtbilling', 'xtboss'
        :return:project all finished
        """
        re_str = r'{}.*has finished.*ms'.format(projrct[0])
        re_result = re.search(re_str, fp_catalina_content)
        if re_result:
            log_str = '{} is in the {}'.format(projrct[0], re_result.span())
            self.mainlog.info(log_str)
            del projrct[0]
            if len(projrct).__eq__(0):
                return 'project all finished'
            else:
                return_str = self.refinished(fp_catalina_content, projrct)
                if return_str:
                    return return_str
        else:
            result_str = 'can\'t find {} finished'.format(projrct[0])
            return result_str

    def sendemail(self, mail_type, mail_text, subject, enclosure=''):
        # 读取emailname配置文件。
        emailroot = ElementTree.parse('emailname.xml')
        # 获取收件人列表。
        mailto_name = emailroot.find('./{}'.format(mail_type))
        mailto_admin = emailroot.find('./admin')
        mailto_list = []
        for i in range(0, len(mailto_name)):
            mailto_list.append(mailto_name[i].text)
        if 'admin' is not mail_type:
            for i in range(0, len(mailto_admin)):
                mailto_list.append(mailto_admin[i].text)
        # 获取邮件认证相关信息。
        mail_host = emailroot.find('mailserver').text
        mail_user = emailroot.find('sendaccount').text
        mail_pass = emailroot.find('sendpassword').text
        me = '<' + mail_user + '>'
        msg = MIMEMultipart()
        msg.attach(MIMEText(mail_text, _subtype='plain', _charset='GBK'))
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = ';'.join(mailto_list)
        if '' != enclosure:
            part_attach = MIMEApplication(open(enclosure, 'rb').read())
            part_attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(enclosure))
            msg.attach(part_attach)
        # 发送邮件。
        # noinspection PyBroadException
        try:
            server = smtplib.SMTP()
            server.connect(mail_host)
            server.login(mail_user, mail_pass)
            server.sendmail(me, mailto_list, msg.as_string())
            server.close()
        except Exception:
            self.mainlog.error(traceback.format_exc())

    def cleanupautoupfloder(self, updatefile):
        self.mainlog.info('List auto update floder.')
        updatefloder = os.path.dirname(updatefile)
        # 获取自动升级文件夹里的文件夹列表。
        floder_list = os.listdir(updatefloder)
        originalctime = 0
        originalfilepath = ''
        # 从列表中排除auto_update_v1.9.3.sh和config_auto_update_v1.9.1.cfg、nohup.out三个文件。
        for file in floder_list:
            if str(file).find('config_auto_update') >= 0:
                floder_list.remove(file)
            elif str(file).find('auto_update') >= 0:
                floder_list.remove(file)
            elif str(file).find('svn') >= 0:
                floder_list.remove(file)
            elif str(file).find('nohup.out') >= 0:
                os.remove(os.path.join(updatefloder, file))
            else:
                self.mainlog.info('Remove old floder.')
                # 判断文件的创建时间，仅保留最近的文件夹，其余的删除。
                floder_path = os.path.join(updatefloder, file)
                floder_ctime = os.path.getctime(floder_path)
                if 0 == originalctime:
                    originalctime = floder_ctime
                    originalfilepath = floder_path
                elif floder_ctime >= originalctime:
                    try:
                        shutil.rmtree(floder_path)
                    except NotADirectoryError:
                        os.remove(floder_path)
                    self.mainlog.info('Remove : %s' % floder_path)
                else:
                    try:
                        shutil.rmtree(originalfilepath)
                    except NotADirectoryError:
                        os.remove(originalfilepath)
                    originalctime = floder_ctime
                    originalfilepath = floder_path
                    self.mainlog.info('Remove : %s' % originalfilepath)
        self.mainlog.info('Remove done.')

    def checkcomplete(self, svnpath):
        version = svnpath.split('/')[-1]
        print(version)
        # 判断xtboss或者xtbilling文件夹是否存在

        self.findrealpath(svnpath, version)

    def findrealpath(self, svnpath, version):
        cmd = 'svn list --verbose "{}"'.format(svnpath)
        self.mainlog.info('run svn list.')
        self.mainlog.info('svn list path is : %s' % svnpath)
        check_p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        check_stdout, check_stderr = check_p.communicate()
        for line in check_stdout.decode('gbk').split('\r\n'):
            cut_str_pattern = r'\d{2}:\d{2}\s+'
            re_result = re.search(cut_str_pattern, line)
            if re_result:
                cut_str = re_result.group()
                content = str(line).split(cut_str)[1]
            else:
                break
            if content.find('/') == -1:
                continue
            if content.find(version) >= 0:
                newpath = '{}/{}'.format(svnpath, version)
                return self.findrealpath(newpath, version)
            elif content.find('xtboss') >= 0:
                print(svnpath)
                return svnpath
            elif content.find('xtbilling') >= 0:
                print(svnpath)
                return svnpath
            elif content.find('WEB-INF') >= 0:
                print(svnpath)
                return svnpath


# MyThread.py线程类
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.result = ''
        self.func = func
        self.args = args

    def run(self):
        time.sleep(2)
        self.result = self.func(*self.args)

    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        return self.result


deploy = AutoDeploy()
parameter_log = deploy.mainlog


@app.route('/configparameters', methods=['GET', 'POST'])
def changeconfig_parameters():
    config_data = flask.request.get_json()
    config_file = config_data['config_file']
    parameter_log.info('config_file is : {:s}'.format(config_file))

    product_name = config_data['product_name']
    parameter_log.info('product_name is : {:s}'.format(product_name))

    svn_path = config_data['patchsvn_path']
    parameter_log.info('svn_path is : {:s}'.format(svn_path))

    boss_path = config_data['install_path_xtboss']
    parameter_log.info('boss_path is : {:s}'.format(boss_path))

    billing_path = config_data['install_path_xtbilling']
    parameter_log.info('billing_path is : {:s}'.format(billing_path))

    other_path = config_data['install_path_other']
    parameter_log.info('other_path is : {:s}'.format(other_path))

    boss_config = config_data['config_svnpath_xtboss']
    parameter_log.info('boss_config is : {:s}'.format(boss_config))

    billing_config = config_data['config_svnpath_xtbilling']
    parameter_log.info('billing_config is : {:s}'.format(billing_config))

    other_config = config_data['config_svnpath_other']
    parameter_log.info('other_config is : {:s}'.format(other_config))

    boss_changed = config_data['config_changed_xtboss']
    parameter_log.info('boss_changed is : {:s}'.format(boss_changed))

    billing_changed = config_data['config_changed_xtbilling']
    parameter_log.info('billing_changed is : {:s}'.format(billing_changed))

    other_changed = config_data['config_changed_other']
    parameter_log.info('other_changed is : {:s}'.format(other_changed))

    other_changed = config_data['config_changed_other']
    parameter_log.info('other_changed is : {:s}'.format(other_changed))

    jenkinsurl = config_data['jenkinsurl']
    parameter_log.info('jenkinsurl is : {:s}'.format(jenkinsurl))

    isupdate = config_data['isupdate']
    parameter_log.info('isupdate is : {:s}'.format(isupdate))

    deploy.checkcomplete(svn_path)

    result = deploy.changeconfig(config_file, product_name, svn_path, boss_path, billing_path, other_path, boss_config,
                                 billing_config, other_config, boss_changed, billing_changed, other_changed)

    # 开始回调jenkins，执行自动化脚本。
    if '是' == isupdate:
        parameter_log.info('Begin run autoupdate update tomcat.')
        parameter_log.info('Jenkins Url is : %s' % str(jenkinsurl))
        urllib3.PoolManager().request('GET', jenkinsurl)

    return result


@app.route('/runupdate', methods=['GET', 'POST'])
def runautoupdate():
    update_data = flask.request.get_json()

    updatefile = update_data['updatefile']
    parameter_log.info('updatefile is : {:s}'.format(updatefile))

    updatemode = update_data['updatemode']
    parameter_log.info('updatemode is : {:s}'.format(updatemode))

    tomcatpath = update_data['tomcatpath']
    parameter_log.info('tomcatpath is : {:s}'.format(tomcatpath))

    project = str(update_data['project']).split(',')
    parameter_log.info('project is : {}'.format(project))

    isnext = update_data['isnext']
    parameter_log.info('isnext is : {:s}'.format(isnext))

    jenkinsurl = update_data['jenkinsurl']
    # jenkinsurl = quote(jenkinsurl, safe=";/?:@&=+$,")
    parameter_log.info('jenkinsurl is : {:s}'.format(jenkinsurl))

    upthread = MyThread(deploy.callautoupdate, [updatefile, updatemode, tomcatpath, project, isnext, jenkinsurl])
    upthread.start()
    upthread.join()
    if 'error' == upthread.get_result():
        flask.make_response().status_code = 500
        return 'Tomcat Start Fail'
    elif 'success' == upthread.get_result():
        return 'success'
    else:
        return 'error'


@app.route('/test', methods=['GET', 'POST'])
def test():
    deploy.checkcomplete('svn://svn.uincall.com:3695/project/05_发布/02_线上需求&Bug发布/01_XTBoss_201902/MsgGate_v3.0.2spc005')
    return '11111'


app.run(host='0.0.0.0', port=40000)
