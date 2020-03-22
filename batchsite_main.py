#!/usr/bin/python
# coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: xxx <xxxx@qq.com>
# +-------------------------------------------------------------------

# +--------------------------------------------------------------------
# |   宝塔第三方应用开发DEMO
# +--------------------------------------------------------------------
import io, re, public, os, sys, json, panelSite, database, files, ftp, copy, site

# 设置运行目录
os.chdir("/www/server/panel")

# 添加包引用位置并引用公共包
sys.path.append("class/")

# 配置全局变量
BT_SITE = panelSite.panelSite()
BT_DATA = database.database()
BT_FILE = files.files()


# 取通用对象
class dict_obj:
    def __contains__(self, key):
        return getattr(self, key, None)

    def __setitem__(self, key, value): setattr(self, key, value)

    def __getitem__(self, key): return getattr(self, key, None)

    def __delitem__(self, key): delattr(self, key)

    def __delattr__(self, key): delattr(self, key)

    def get_items(self): return self


cacheDict = {}
cacheList = []

from flask import session

#在非命令行模式下引用面板缓存和session对象
if __name__ != '__main__':
    from BTPanel import cache,session,redirect

    #设置缓存(超时10秒) cache.set('key',value,10)
    #获取缓存 cache.get('key')
    #删除缓存 cache.delete('key')

    #设置session:  session['key'] = value
    #获取session:  value = session['key']
    #删除session:  del(session['key'])

class batchsite_main:
    __SETUP_PATH = 'plugin/batchsite'
    __PLUGIN_PATH = os.getenv("BT_PANEL")
    __PLUGIN_CONFIG = __PLUGIN_PATH + "config/config.json"
    __PLUGIN_RESULT_LOG = __PLUGIN_PATH + "config/result_log.json"
    __HOST_PATH = "/etc/hosts"
    __CONFIG = None
    __SITE_FILE = __PLUGIN_PATH + 'addsites.json'
    __BAG_PATH = __PLUGIN_PATH + 'install'

    # 构造方法
    def __init__(self):
        # 如果 不存在配置文件 则自动初始化配置文件
        if not os.path.exists(self.__PLUGIN_CONFIG):
            self.Plugin_Init()
        # 读取根目录下的 config.json
        config = json.loads(public.ReadFile(self.__PLUGIN_CONFIG))
        self.__bag_path = config["bag"]
        # 如果 不存在插件的安装目录 创建
        if not os.path.exists(self.__bag_path):
            os.mkdir(self.__bag_path)

    # 保存domain list数据到local
    def save_domain_list(self, args):
        if not 'siteList' in args: return public.returnMsg(False, '参数不正确!')
        siteList = json.loads(args.siteList)
        site_file = self.__SITE_FILE;
        self.set_write_file(siteList, site_file)
        if os.path.exists(self.__SITE_FILE):
            result = {}
            result['size'] = len(siteList);
            return {"status": "Success", "size": result['size']}
        if not os.path.exists(self.__SITE_FILE):
            return public.returnMsg(False, 'DIR_DEL_ERR')

    #  通用替换文件 写入
    def set_write_file(self, args, filePath):
        if os.path.exists(filePath):
            os.remove(filePath)
        if not os.path.exists(filePath):
            public.WriteFile(filePath, json.dumps(args))

    #  通用替换文件 读取
    def get_read_file(self, filePath):
        if not os.path.exists(filePath):
            return public.returnMsg(False, 'DIR_NOT_EXISTS_ERR')
        sites_data = json.loads(public.ReadFile(filePath))
        return sites_data

    def delete_domain_list(self, args):
        pass

    def get_domain_list(self, args):
        jsonFile = self.__SETUP_PATH + '/batchsite_config.json';
        if not os.path.exists(jsonFile): return public.returnMsg(False, '配置文件不存在!');
        data = {}
        data = json.loads(public.readFile(jsonFile));
        tmp = [];
        for d in data:
            tmp.append(d);
        data = tmp;
        result = {}
        result['data'] = data;
        return {"status": "Success", "data": result['data']}

    # 批量添加站点域名
    def add_domain_list(self, args):
        # 获取用户确认后的 site信息
        # sites_data = self.get_read_file(self.__SITE_FILE)
        # result = {}
        # result['size'] = len(sites_data);
        # # data = json.loads(args.domain_info)
        # for site in sites_data:
        #     return {"status": "Success", "data":sites_data}

        data = json.loads(args.domain_info)
        site_file = self.__SITE_FILE;
        sites_data = self.get_read_file(site_file)

        successSize = [];
        failureSize = [];

        # # 获取前端表单数据
        for site in sites_data:
            domain = site["domain"]
            second_domain = site["second_domain"]
            # if self.CheckDomainExist(domain):
            #     return {"status": "error", "msg": "试图添加的域名[" + domain + "]已经存在！"}

            # 构造创建网站必须的参数
            site_obj = dict_obj()
            site_obj.webname = json.dumps({"domain": domain, "domainlist": [second_domain], "count": 0})
            site_obj.path = data['path'] + domain
            site_obj.type = data['type']
            site_obj.type_id = 0
            site_obj.version = data['version']
            site_obj.port = data['port']
            site_obj.ps = "[" + domain + "] 一键部署"
            site_obj.codeing = "utf8"
            site_obj.ftp = "true"
            site_obj.ftp_username = site['ftp_username']
            site_obj.ftp_password = site['ftp_password']

            site_obj.sql = "true"
            site_obj.datauser = site['datauser']
            site_obj.datapassword = site['datapassword']
            site_obj.zip = data["zip"]

            # 添加网站
            psa = BT_SITE.AddSite(site_obj)
            if "siteStatus" in psa.keys():
                successSize.append(psa.copy())
            if "status" in psa.keys():
                failureSize.append(psa.copy())

            # 保存 建站日志到 本地
            # resultSize.append(successSize)
            # resultSize.append(failureSize)
            # self.set_write_file(successSize, self.__PLUGIN_RESULT_LOG)
            # return {"status": "Success", "failureSize": failureSize}

            # 删除网站目录下的所有无用的文件
            os.popen("cd " + site_obj.path + " && rm -rf *")

            # 解压文件
            os.popen("cd " + self.__bag_path + " && unzip -o " + site_obj.zip + " -d " + site_obj.path + "/")

            cmd = ""
            # 判断网站根目录下是否存在 index.php 文件
            while not os.path.exists(site_obj.path + "/index.php"):
                for file in os.listdir(site_obj.path):
                    if os.path.isdir(site_obj.path + "/" + file):
                        # 将文件夹拷贝到上级文件夹
                        os.popen("mv " + site_obj.path + "/" + file + "/* " + site_obj.path)
                        # 删除原文件
                        os.popen("cd " + site_obj.path + " && rm -rf " + file)
            # 导入数据库
            # data = dict_obj()
            # data.file = site_obj.path + "/base/install/db/db.sql"
            # data.name = site_obj.datauser
            # BT_Data.InputSql(data)

            # 创建FTP
            # BTftp = ftp.ftp()
            FTP = dict_obj()
            FTP.ftp_username = site_obj.ftp_username
            FTP.ftp_password = site_obj.ftp_password
            # FTP.path = site_obj.path
            # FTP.ps = site_obj.ps
            # BTftp.AddUser(FTP)

            # 修改配置文件
            # 构建PHP 的配置文件
            PhpConfig = '''<?php
                #[数据库参数]
                $dbHost="127.0.0.1";
                $dbName="%s";
                $dbUser="%s";
                $dbPass="%s";
    
                #[数据表前缀]
                $TablePre="dev";
    
                #[语言]
                $sLan="zh_cn";
    
                #[网址]
                $SiteUrl="http://%s";
    
                #----------------------------------#
                ?>
                ''' % (site_obj.datauser, site_obj.datauser, site_obj.datapassword, domain)
            # 写入站点
            public.WriteFile(site_obj.path + "/config.inc.php", PhpConfig.encode("GB2312"))
            # 删除原目录下的 install 文件夹
            os.popen("rm -rf " + site_obj.path + "/base/install/")
            file = dict_obj()
            file.filename = site_obj.path
            file.user = "www"
            file.access = "755"
            file.all = "True"
            files.files().SetFileAccess(file)

        count = successSize + failureSize
        self.set_write_file(successSize, self.__PLUGIN_RESULT_LOG)
        return {"status": "Success", "site":
            {"count": len(count), "successSize": len(successSize), "failureSize": len(failureSize)}}

    # return {"status": "Success", "site": {"Success": domain, "Failure": site_obj.datauser,
    #                                       "data_pass": site_obj.datapassword, "site_path": site_obj.path,
    #                                       "ftp_username": site_obj.ftp_username, "ftp_password": site_obj.ftp_password}}

    # 判断域名是否存在
    def CheckDomainExist(self, cdomain):
        # 获得当前配置文件下的所有域名
        Domains = self.GetHostConfig("")
        for domain in Domains["domains"]:
            if domain["host"] == cdomain:
                return True
        return False



    # 获取新站点的ID
    def GetSiteNewID(self):
        MaxId = public.M("sqlite_sequence").where('name=?', ("sites")).field('seq').find()
        if "seq" in MaxId:
            Id = MaxId["seq"]
        else:
            Id = 0
        return int(Id) + 1

        # 添加域名记录

    def AddDomainConfig(self, get):
        if self.CheckDomainExist(get.domain):
            return {"status": "error", "msg": "试图添加的域名[" + get.domain + "]已经存在！"}

        # 遍历配置文件 寻找是否存在相同的 ip 地址
        Hosts = public.ReadFile(self.__host_path)
        # 按行切割配置文件
        host = Hosts.split("\n")
        lip = -1
        i = 0
        # 使用空格切割每行中的数据
        for _host in host:
            ip = _host.split(" ")
            if get.ip == ip[0]:
                lip = i
                pass
            else:
                i = i + 1
        if lip == -1:
            Hosts = Hosts + "\n" + get.ip + "  " + get.domain
            public.WriteFile(self.__host_path, Hosts)
        else:
            host[lip] = host[lip] + "  " + get.domain
            num = len(host) - 1
            i = 0
            NHosts = ""
            while i != num:
                NHosts = NHosts + host[i] + "\n"
                i = i + 1
            public.WriteFile(self.__host_path, NHosts)
        return {"status": "success", "msg": "域名[" + get.domain + "]添加成功！"}

        # 删除域名记录

    def DelDomainConfig(self, get):
        if not self.CheckDomainExist(get.domain):
            return {"status": "error", "msg": "试图删除的域名[" + get.domain + "]不存在！"}
        else:
            # 遍历找到当前域名所在的位置
            Hosts = public.ReadFile(self.__host_path)
            Domains = []
            NHosts = ""
            # 按行切割配置文件
            host = Hosts.split("\n")

            # 使用空格切割每行中的数据
            for _host in host:
                info = _host.split(" ")
                i = 0
                m = -1
                for domain in info:
                    if get.domain == domain:
                        info[i] = ""
                        m = i
                    i = i + 1
                num = len(info)
                line = ""
                i = 0
                # 组装当前行的数据
                while i != num:
                    line = line + info[i]
                    if i != m:
                        line = line + " "
                    i = i + 1
                NHosts = NHosts + line + "\n"
            public.WriteFile(self.__host_path, NHosts)
            return {"status": "success", "msg": "域名[" + get.domain + "]删除成功！"}

        # 修改域名记录

    def EditDomainConfig(self, get):
        if not self.CheckDomainExist(get.olddomain):
            return {"status": "error", "msg": "试图修改的域名[" + get.olddomain + "]不存在！"}
        else:
            olddomain = public.dict_obj()
            newdomain = public.dict_obj()
            olddomain.domain = get.olddomain
            olddomain.ip = get.ip
            newdomain.domain = get.newdomain
            newdomain.ip = get.ip
            self.DelDomainConfig(olddomain)
            res = self.AddDomainConfig(newdomain)
            if res["status"] == "success":
                return {"status": "success", "msg": "域名[" + get.olddomain + "]修改成功！"}
            else:
                return res

    # 获得可以一键部署的文件列表
    def GetInstallList(self, args):
        self.FileDir = []
        dir = dict_obj()
        dir.path = self.__bag_path
        dir.back = 1
        List = self.GetFileDirList(dir)
        for file in List:
            # 检查文件是不是 zip 格式的压缩文件
            if not re.match("\S{1,}.zip", str(file)) or not os.path.isfile(self.__bag_path + file):
                List.remove(file)
        return {"status": "Success", "List": List}

    # 递归获得指定文件下下的所有文件
    def GetFileDirList(self, args):
        for file in os.listdir(args.path):
            path = os.path.join(file)
            if os.path.isdir(path):
                rec = dict_obj()
                rec.back = 0
                rec.path = path
                self.GetFileDirList(rec)
            else:
                self.FileDir.append(path)
        if int(args.back) == 1:
            return self.FileDir
