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
import io, re, public, os, sys, files, json, panelSite, database, files, ftp

# 设置运行目录
os.chdir("/www/server/panel")

# 添加包引用位置并引用公共包
sys.path.append("class/")

# 配置全局变量
BT_SITE = panelSite.panelSite()
BT_DATA = database.database()
BT_FILE = files.files()

cacheList = []
cacheDict = {}


class Site:
    def __init__(self, domain, second_domain):
        self.domain = domain
        self.second_domain = second_domain

    @property
    def domain(self):
        return self.domain

    @domain.setter
    def name(self, domain):
        self.domain = domain

    @property
    def second_domain(self):
        return self.second_domain

    @second_domain.setter
    def second_domain(self, second_domain):
        self._age = second_domain


# 取通用对象
class dict_obj:
    def __contains__(self, key):
        return getattr(self, key, None)

    def __setitem__(self, key, value): setattr(self, key, value)

    def __getitem__(self, key): return getattr(self, key, None)

    def __delitem__(self, key): delattr(self, key)

    def __delattr__(self, key): delattr(self, key)

    def get_items(self): return self


# 在非命令行模式下引用面板缓存和session对象
if __name__ != '__main__':
    from BTPanel import cache, session, redirect


class batchsite_main:
    __setupPath = 'plugin/batchsite';
    __plugin_path = "/www/server/panel/plugin/batchsite/"
    __host_path = "/etc/hosts"
    __config = None

    # 构造方法
    def __init__(self):
        pass

    def save_domain_list(self, args):
        if not 'siteList' in args: return public.returnMsg(False, '参数不正确!')
        global cacheList
        siteList = json.loads(args.siteList)
        list = []
        if len(cacheList) > 0:
            cacheList.clear()
        else:
            for site in siteList:
                list.append(Site(site['domain'], site['second_domain']))
            cacheList = list
            result = {}
            result['size'] = len(cacheList);
        return {"status": "Success", "size": result['size']}

    def delete_domain_list(self, args):
        pass

    def get_domain_list(self, args):
        jsonFile = self.__setupPath + '/batchsite_config.json';
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
        global cacheList
        for site in cacheList:
            domain = site.domain
            second_domain = site.second_domain
            if self.CheckDomainExist(domain):
                return {"status": "error", "msg": "试图添加的域名[" + domain + "]已经存在！"}

            # 构造创建网站必须的参数
            site = dict_obj()
            site.webname = json.dumps({"domain": domain, "domainlist": [second_domain], "count": 0})
            site.path = "/www/wwwroot/" + domain
            site.type = args.type
            site.type_id = args.type_id
            site.version = args.version
            site.port = args.port
            site.ps = "[" + domain + "] 一键部署"
            site.codeing = args.codeing

            site.ftp = args.ftp
            site.ftp_username = args.ftp_username
            site.ftp_password = args.ftp_username

            site.sql = args.sql
            site.datauser = args.datauser
            site.datapassword = args.datapassword

            result = BT_SITE.AddSite(site)
            result['status']

            # 导入数据库
            data = dict_obj()
            data.file = site.path + "/base/install/db/db.sql"
            data.name = site.datauser
            BT_DATA.InputSql(data)

            # 创建FTP
            BTftp = ftp.ftp()
            FTP = dict_obj()
            FTP.ftp_username = site.datauser
            FTP.ftp_password = public.GetRandomString(16)
            FTP.path = site.path
            FTP.ps = site.ps
            BTftp.AddUser(FTP)

            # 删除原目录下的 install 文件夹
            os.popen("rm -rf " + site.path + "/base/install/")
            file = dict_obj()
            file.filename = site.path
            file.user = "www"
            file.access = "777"
            file.all = "True"
            BT_FILE.SetFileAccess(file)
        pass


# 读取linux 的host 文件
def GetHostConfig(self, get):
    Hosts = public.ReadFile(self.__host_path)
    Domains = []

    # 按行切割配置文件
    host = Hosts.split("\n")
    # 使用空格切割每行中的数据
    for _host in host:
        info = _host.split(" ")
        i = 0
        for domain in info:
            if domain == " " or domain == "":
                pass
            else:
                _domain = {"host": "", "ip": ""}
                if i == 0:
                    ip = domain
                else:
                    _domain["host"] = domain
                    _domain["ip"] = ip
                if _domain["ip"] == "":
                    pass
                else:
                    Domains.append(_domain)
            i = i + 1
    num = len(Domains)
    return {"status": "succecss", "domains": Domains, "num": num}


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


# 判断域名是否存在
def CheckDomainExist(self, cdomain):
    # 获得当前配置文件下的所有域名
    Domains = self.GetHostConfig("")
    for domain in Domains["domains"]:
        if domain["host"] == cdomain:
            return True
    return False
