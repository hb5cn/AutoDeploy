# !/usr/local/python
# -*- coding: UTF-8 -*-

import os
import re
import time
import copy
import flask
import logging
import threading
import subprocess

app = flask.Flask(__name__)


class AutoDeploy(object):
    def __init__(self):
        self.home_dir = os.path.split(os.path.realpath(__file__))[0]

        # 初始化日志模块
        self.logging = logging
        # 定义工程的初始路径

        # 定义日志文件输入的路径及文件名
        logfile = '{:s}/LOG/AutoTestLog{:s}.log'.format(self.home_dir, time.strftime('%Y%m%d%H%M%S',
                                                                                     time.localtime(time.time())))
        self.logging.basicConfig(filename=logfile, level=self.logging.INFO,
                                 format='%(asctime)s %(funcName)s %(lineno)d %(levelname)s %(message)s',
                                 datefmt='%Y-%m-%d-%a %H:%M:%S', filemode='w')
        # 设置一个屏幕打印的句柄
        formatter = self.logging.Formatter('%(asctime)s %(funcName)s %(lineno)d %(levelname)s  %(message)s')
        setlevel = self.logging.INFO
        self.logscr = self.logging.StreamHandler()
        self.logscr.setLevel(setlevel)
        self.logscr.setFormatter(formatter)
        self.mainlog = self.logging.getLogger('LOG')
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

    def callautoupdate(self, updatefile, tomcatpath, project):
        self.cleantomcatlog(tomcatpath)
        # 创建shell执行语句。
        cmd = '/bin/bash {:s} 6'.format(updatefile)
        self.mainlog.info('Begin update')
        self.mainlog.info('bash is : %s' % cmd)

        # 开始执行更新版本。
        update = subprocess.Popen(cmd.encode('gbk'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while True:
            nextline = update.stdout.readline().decode(encoding='utf-8')
            self.mainlog.info(nextline.strip())
            if update.poll() == 0:
                break

        # 开始查日志判断是否正常启动。
        catalinalogpath = os.path.join(tomcatpath, 'logs/catalina.out')
        self.judgebossrun(catalinalogpath, project)

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
            # 判断正常启动
            fp_catalina = open(catalinalogpath, encoding='utf-8')
            fp_catalina_content = fp_catalina.read()
            for i in range(0, num_list):
                re_return = self.refinished(fp_catalina_content, project)
                if 'project all finished' == str(re_return):
                    self.mainlog.info('project all finished')
                    return
                else:
                    self.mainlog.info(re_return)

                a = new_project[0]
                for j in range(0, num_list - 1):
                    new_project[j] = new_project[j + 1]
                new_project[-1] = a
                project = copy.copy(new_project)
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


deploy = AutoDeploy()
parameter_log = deploy.mainlog


@app.route('/configparameters', methods=['GET', 'POST'])
def changeconfig_parameters():
    config_file = flask.request.values.get('config_file')
    parameter_log.info('config_file is : {:s}'.format(config_file))

    product_name = flask.request.values.get('product_name')
    parameter_log.info('product_name is : {:s}'.format(product_name))

    svn_path = flask.request.values.get('svn_path')
    parameter_log.info('svn_path is : {:s}'.format(svn_path))

    boss_path = flask.request.values.get('boss_path')
    parameter_log.info('boss_path is : {:s}'.format(boss_path))

    billing_path = flask.request.values.get('billing_path')
    parameter_log.info('billing_path is : {:s}'.format(billing_path))

    other_path = flask.request.values.get('other_path')
    parameter_log.info('other_path is : {:s}'.format(other_path))

    boss_config = flask.request.values.get('boss_config')
    parameter_log.info('boss_config is : {:s}'.format(boss_config))

    billing_config = flask.request.values.get('billing_config')
    parameter_log.info('billing_config is : {:s}'.format(billing_config))

    other_config = flask.request.values.get('other_config')
    parameter_log.info('other_config is : {:s}'.format(other_config))

    boss_changed = flask.request.values.get('boss_changed')
    parameter_log.info('boss_changed is : {:s}'.format(boss_changed))

    billing_changed = flask.request.values.get('billing_changed')
    parameter_log.info('billing_changed is : {:s}'.format(billing_changed))

    other_changed = flask.request.values.get('other_changed')
    parameter_log.info('other_changed is : {:s}'.format(other_changed))

    result = deploy.changeconfig(config_file, product_name, svn_path, boss_path, billing_path, other_path, boss_config,
                                 billing_config, other_config, boss_changed, billing_changed, other_changed)
    return result


@app.route('/runupdate', methods=['GET', 'POST'])
def runautoupdate():
    updatefile = flask.request.values.get('updatefile')
    parameter_log.info('updatefile is : {:s}'.format(updatefile))
    tomcatpath = flask.request.values.get('tomcatpath')
    parameter_log.info('tomcatpath is : {:s}'.format(tomcatpath))
    project = str(flask.request.values.get('project')).split(',')
    parameter_log.info('project is : {}'.format(project))
    upthread = threading.Thread(target=deploy.callautoupdate, args=(updatefile, tomcatpath, project,))
    upthread.start()
    return 'Begin update'


@app.route('/test', methods=['GET', 'POST'])
def test():
    deploy.judgebossrun('F:/PythonTest/AutoDeployWithJenkins(Uincall)/catalina.out', ['xtbilling', 'xtboss'])
    return '2222'


app.run(host='0.0.0.0', port=40000)

if __name__ == '__main__':
    # a = AutoDeploy()
    # a.judgetomcatrun('F:/PythonTest/AutoDeployWithJenkins(Uincall)/catalina.out')
    # a.changeconfig('config_auto_update_v1.9.1.cfg', 'api', 'svn://123.57.180.25/dailyproduct/boss/20190514111130',
    #                '/opt/tomcat227_8083/webapps/', '/opt/tomcat227_8083/webapps/', '',
    #                'svn://svn.uincall.com:3695/project/04_测试/99 部门管理/01 文档管理/10 自动化项目/05 测试环境配置文件备份/'
    #                '101.200.111.227/227-8083/227-8083-bossautodeploy-xtboss-classes',
    #                'svn://svn.uincall.com:3695/project/04_测试/99 部门管理/01 文档管理/10 自动化项目/05 测试环境配置文件备份/'
    #                '101.200.111.227/227-8083/227-8083-bossautodeploy-xtbilling-classes', '', 'no', 'no', 'no')
    # a.main()
    pass
