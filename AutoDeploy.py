# !/usr/local/python
# -*- coding: UTF-8 -*-

import os
import sys
import socket
import traceback


class AutoDeploy(object):
    def __init__(self):
        self.home_dir = os.path.split(os.path.realpath(__file__))[0]

    def changeconfig(self, config_file, product_name):
        # config路径。
        config_path = os.path.join(self.home_dir, config_file)

        # 获取config文件原始内容。
        assert os.path.exists(config_path), '{0} is not exists.'.format(config_path)
        fp = open(config_path, 'r')
        config_content = fp.readlines()
        fp.close()
        newcontent = ''

        # 将product_name进行替换
        for content in config_content:
            if content.find('product_name=') >= 0:
                print('Change Product : {0:s}'.format(product_name))
                content = content.replace(content.split('=')[1], "'{0}'".format(str(product_name)))
            newcontent += content

        # 将替换后的全部内容写入原文件
        fp = open(config_path, 'w')
        fp.write(newcontent)
        fp.close()


if __name__ == '__main__':
    a = AutoDeploy()
    a.changeconfig('config_auto_update_v1.9.1.cfg', 'api')
