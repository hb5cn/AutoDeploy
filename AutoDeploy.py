# !/usr/local/python
# -*- coding: UTF-8 -*-

import os
import sys
import time
import flask
import logging
import traceback

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
        fp = open(config_path, 'w', encoding='utf-8')
        fp.write(newcontent)
        fp.close()

        return 'Change done.'

    # def main(self):
        # self.changeconfig(config_file, )
        # self.changeconfig('config_auto_update_v1.9.1.cfg', 'api',
        #                   'svn://123.57.180.25/dailyproduct/boss/20190514111130',
        #                   '/opt/tomcat227_8083/webapps/', '/opt/tomcat227_8083/webapps/', '',
        #                   'svn://svn.uincall.com:3695/project/04_测试/99 部门管理/01 文档管理/10 自动化项目/'
        #                   '05 测试环境配置文件备份/101.200.111.227/227-8083/227-8083-bossautodeploy-xtboss-classes',
        #                   'svn://svn.uincall.com:3695/project/04_测试/99 部门管理/01 文档管理/10 自动化项目/'
        #                   '05 测试环境配置文件备份/101.200.111.227/227-8083/227-8083-bossautodeploy-xtbilling-classes', '',
        #                   'no', 'no', 'no')


@app.route('/configparameters', methods=['GET', 'POST'])
def changeconfig_parameters():
    deploy = AutoDeploy()
    parameter_log = deploy.mainlog

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


app.run(port=40000)

if __name__ == '__main__':
    # a = AutoDeploy()
    # a.changeconfig('config_auto_update_v1.9.1.cfg', 'api', 'svn://123.57.180.25/dailyproduct/boss/20190514111130',
    #                '/opt/tomcat227_8083/webapps/', '/opt/tomcat227_8083/webapps/', '',
    #                'svn://svn.uincall.com:3695/project/04_测试/99 部门管理/01 文档管理/10 自动化项目/05 测试环境配置文件备份/'
    #                '101.200.111.227/227-8083/227-8083-bossautodeploy-xtboss-classes',
    #                'svn://svn.uincall.com:3695/project/04_测试/99 部门管理/01 文档管理/10 自动化项目/05 测试环境配置文件备份/'
    #                '101.200.111.227/227-8083/227-8083-bossautodeploy-xtbilling-classes', '', 'no', 'no', 'no')
    # a.main()
    pass


