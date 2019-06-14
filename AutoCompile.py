# !/usr/local/python
# -*- coding: UTF-8 -*-

import os
import time
import flask
import shutil
import urllib3
import smtplib
import datetime
import traceback
import threading
import subprocess
import logging.handlers
from urllib.parse import quote
from xml.etree import ElementTree
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

app = flask.Flask(__name__)


class CompileBase(object):
    def __init__(self):
        self.home_dir = os.path.split(os.path.realpath(__file__))[0]

        # 初始化日志模块
        self.mainlog = logging.getLogger()
        self.mainlog.setLevel(logging.INFO)
        # 定义日志文件输入的路径及文件名
        logfile = '{:s}/LOG/AutoCompile.log'.format(self.home_dir)
        if os.path.exists(logfile):
            os.remove(logfile)

        # 设置一个本地打印的句柄
        formatter = logging.Formatter('%(asctime)s %(funcName)s %(lineno)d %(thread)d %(levelname)s  %(message)s')

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

    def updatesvn(self, path):
        if not os.path.exists(path):
            email_text = '要更新的SVN路径没有被找到，SVN路径是 : {}'.format(path)
            self.sendemail('admin', email_text, '更新SVN的路径没有被找到')
            return 'update svn path is not exists : %s' % path
        self.mainlog.info('Update SVN is : %s' % path)
        update_cmd = 'svn update "{}"'.format(path)
        cleanup_cmd = 'svn cleanup "{}"'.format(path)
        status_cmd = 'svn status --no-ignore "{}"'.format(path)
        # status_cmd = status_cmd.encode('gbk')
        self.mainlog.info('Begin update %s' % str(path))
        # 先用svn cleanup命令清理一下目录，实际效果甚微，只能解决冲突的问题。
        svnout = os.popen(cleanup_cmd)
        svnlog = str(svnout.read())
        # 执行一下svn status命令，查看一下目录的所有文件及文件夹的状态。
        status_pipe = subprocess.Popen(status_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        status_out, status_stderr = status_pipe.communicate()
        # 用\r\n切割成列表，将所有有异常的文件及文件夹列出来
        for line in status_out.decode('utf-8').split("\r\n"):
            try:
                # 用'       '来进行分割，无论是修改还是无版本控制，一律删除，以SVN上为准。
                rm_path = line.split('       ')[1]
                if os.path.isfile(rm_path):
                    self.mainlog.info('Delete abnormal svn file : %s' % rm_path)
                    os.remove(rm_path)
                elif os.path.isdir(rm_path):
                    self.mainlog.info('Delete abnormal svn floder : %s' % rm_path)
                    shutil.rmtree(rm_path)
            except IndexError:
                pass
        # 使用svn update命令更新当前目录。
        svnout = os.popen(update_cmd)
        svnlog += str(svnout.read())
        self.mainlog.info(svnlog)
        self.mainlog.info('Update done.')
        return 'update done'

    def runant(self, buildxml):
        compile_status = ''
        if not os.path.exists(buildxml):
            email_text = 'ant的build文件没有被找到，SVN路径是 : {}'.format(buildxml)
            self.sendemail('admin', email_text, 'ant的build文件没有被找到')
            return 'buildxml is not exists : %s' % buildxml
        build_log = '{}.log'.format(os.path.basename(buildxml))
        if os.path.exists(build_log):
            os.remove(build_log)
        build_cmd = 'ant -f {}'.format(buildxml)
        self.mainlog.info('Begin ant : %s' % buildxml)
        fp_build = open(build_log, 'ab+')
        # 使用命令调用ant编译命令
        build_pipe = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while True:
            nextline = build_pipe.stdout.readline().decode(encoding='utf-8')
            fp_build.write(nextline.encode('utf-8'))
            self.mainlog.info(nextline.strip())
            success_count = str(nextline).find('BUILD SUCCESSFUL')
            if int(success_count) >= 0:
                compile_status = 'success'
            if build_pipe.poll() == 0 and nextline.strip() == '':
                # noinspection PyBroadException
                try:
                    build_pipe.kill()
                except Exception:
                    self.mainlog.error(traceback.format_exc())
                break
        fp_build.close()
        # 判断是否编译成功
        if 'success' == compile_status:
            self.mainlog.info('编译成功')
            return 'build success'
        else:
            self.mainlog.info(compile_status)
            # 如果编译失败，则发送邮件。
            self.mainlog.info('编译失败')
            self.sendemail('admin', '编译失败，编译日志请参看附件。', '编译失败', build_log)
            return 'build fail'

    def makeversion(self, path):
        ver_floder = os.path.join(path, 'version')
        if os.path.exists(ver_floder):
            shutil.rmtree(ver_floder)
        os.mkdir(ver_floder)
        self.mainlog.info('Make version file')
        time_now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        ver_file = 'version_boss_{}'.format(time_now)
        ver_f_path = os.path.join(ver_floder, ver_file)
        f_ver = open(ver_f_path, 'w')
        f_ver.close()

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


cp_base = CompileBase()
app_log = cp_base.mainlog


@app.route('/upsvn', methods=['GET', 'POST'])
def updatesvn():
    updatepath = flask.request.values.get('updatepath')
    app_log.info('Need update Path is : {:s}'.format(updatepath))
    update_result = cp_base.updatesvn(updatepath)
    if 'update done' == update_result:
        return 'Update svn : "%s" success.' % updatepath
    else:
        return update_result


@app.route('/cplbossandbilling', methods=['GET', 'POST'])
def compilebossandbilling():
    bosspath = flask.request.values.get('bosspath')
    app_log.info('Bosspath update Path is : {:s}'.format(bosspath))
    billingpath = flask.request.values.get('billingpath')
    app_log.info('Billingpath update Path is : {:s}'.format(billingpath))
    bossbuildpath = flask.request.values.get('bossbuildpath')
    app_log.info('Bossbuildpath update Path is : {:s}'.format(bossbuildpath))
    billingbuildpath = flask.request.values.get('billingbuildpath')
    app_log.info('Billingbuildpath update Path is : {:s}'.format(billingbuildpath))
    bossreleasesource = flask.request.values.get('bossreleasesource')
    app_log.info('Bossreleasesource update Path is : {:s}'.format(bossreleasesource))
    bossreleaseto = flask.request.values.get('bossreleaseto')
    app_log.info('Bossreleaseto update Path is : {:s}'.format(bossreleaseto))
    billingreleasesource = flask.request.values.get('billingreleasesource')
    app_log.info('Billingreleasesource update Path is : {:s}'.format(billingreleasesource))
    billingreleaseto = flask.request.values.get('billingreleaseto')
    app_log.info('Billingreleaseto update Path is : {:s}'.format(billingreleaseto))
    isnext = flask.request.values.get('isnext')
    app_log.info('isnext is : {:s}'.format(isnext))
    jenkinsurl = flask.request.values.get('jenkinsurl')
    jenkinsurl = quote(jenkinsurl, safe=";/?:@&=+$,")
    app_log.info('jenkinsurl is : {:s}'.format(jenkinsurl))
    update_result = cp_base.updatesvn(bosspath)
    if 'update done' != update_result:
        return update_result
    update_result = cp_base.updatesvn(billingpath)
    if 'update done' != update_result:
        return update_result
    bossthread = MyThread(cp_base.runant, [bossbuildpath])
    bossthread.start()
    billingthread = MyThread(cp_base.runant, [billingbuildpath])
    billingthread.start()
    if 'build success' == bossthread.get_result() == billingthread.get_result():
        if os.path.exists(bossreleaseto):
            shutil.rmtree(bossreleaseto)
        app_log.info('Copy boss floder.')
        cp_base.makeversion(bossreleasesource)
        # 将编译完成的boss整个release目录拷贝到tomcat中的xtboss目录。
        shutil.copytree(bossreleasesource, bossreleaseto)

        if os.path.exists(billingreleaseto):
            shutil.rmtree(billingreleaseto)
        app_log.info('Copy billing floder.')
        cp_base.makeversion(billingreleasesource)
        # 将编译完成的billing整个release目录拷贝到tomcat中的xtbilling目录。
        shutil.copytree(billingreleasesource, billingreleaseto)
    else:
        return bossthread.get_result(), billingthread.get_result()

    if 'true' == str(isnext):
        app_log.info('Begin Call Jenkins Run autodeploy.')
        app_log.info('Jenkins Url is : %s' % str(jenkinsurl))
        http = urllib3.PoolManager()
        http.request('GET', jenkinsurl)
    return 'Update xtboss and xtbilling SVN done, run ant done.'


app.run(host='0.0.0.0', port=40001)
