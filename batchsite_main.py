#!/usr/bin/python
# coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Author: Every <907139945@qq.com>
# +-------------------------------------------------------------------
# |   宝塔批量建站工具 batchsite
# +-------------------------------------------------------------------
import io,re, public, os, sys, json, panelSite, database, \
    files, ftp, copy, site, data,glob

try:
    import xlrd as xlrd
except:
    os.system('python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple xlrd')
    import xlrd as xlrd
try:
    import pandas as pd
except:
    os.system('python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pandas')
    import pandas as pd

# 添加包引用位置并引用公共包
sys.path.append("class/")

# 配置全局变量
BT_SITE = panelSite.panelSite()
BT_DATA = database.database()
BT_FILE = files.files()
BT_DOMAIN_DATA = data.data()


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
    SETUP_PATH = 'plugin/batchsite'
    PANEL_PATH = '/www/server/panel';
    PLUGIN_PATH = PANEL_PATH + "/plugin/batchsite/"
    CONFIG_PATH = SETUP_PATH + "/config/"
    PLUGIN_CONFIG = PLUGIN_PATH + "config/config.json"
    PLUGIN_RESULT_LOG = PLUGIN_PATH + "config/result_log.json"
    SITE_ADD_FILE = PLUGIN_PATH + 'config/addsites.json'
    SITE_DEL_FILE = PLUGIN_PATH + 'config/delsites.json'
    BAG_PATH = PLUGIN_PATH + 'install/'
    DOMAIN_EXCLE = 'domain.xlsx'
    EXCLE_PATH = CONFIG_PATH + DOMAIN_EXCLE
    AP_EXCLE_PATH = PLUGIN_PATH + DOMAIN_EXCLE

    # 构造方法
    def __init__(self):
        pass

    # 保存domain list数据到local
    def saveDomainList(self, args):
        if not 'siteList' in args: return public.returnMsg(False, '参数不正确!')
        siteList = json.loads(args.siteList)
        site_file = self.SITE_ADD_FILE;
        self.setWriteFile(siteList, site_file)
        if os.path.exists(self.SITE_ADD_FILE):
            result = {}
            result['size'] = len(siteList);
            return {"status": "Success", "size": result['size']}
        if not os.path.exists(self.SITE_ADD_FILE):
            return public.returnMsg(False, 'DIR_DEL_ERR')

    #  通用替换文件 写入
    def setWriteFile(self, args, filePath):
        if os.path.exists(filePath):
            os.remove(filePath)
        if not os.path.exists(filePath):
            public.WriteFile(filePath, json.dumps(args))

    #  通用替换文件 读取
    def getReadFile(self, filePath):
        if not os.path.exists(filePath):
            return public.returnMsg(False, 'DIR_NOT_EXISTS_ERR')
        sites_data = json.loads(public.ReadFile(filePath))
        return sites_data

    # 上传 域名文件
    def uploadDomainTxt(self, args):
        data = self.UploadFile(args)
        return {"data": data}

    # 使用 pandas 之前需要先执行: pip install pandas
    # 上传 域名添加 Excel 文件
    def uploadAddDomainExcel(self, args):
        path = self.SITE_ADD_FILE
        rdata = self.uploadExcel(args, path)
        return rdata

    # 上传 域名删除 Excel 文件
    def uploadDelDomainExcel(self, args):
        path = self.SITE_DEL_FILE
        rdata = self.uploadExcel(args, path)
        return rdata

    # 获取上传删除域名 Excel 文件 返回json数据
    def getDelDomainList(self, args):
        jsonFile = self.SITE_DEL_FILE
        rdata = self.getDomainList(jsonFile)
        return rdata

    # 获取上传添加域名 Excel 文件 返回json数据
    def getAddDomainList(self, args):
        jsonFile = self.SITE_ADD_FILE
        rdata = self.getDomainList(jsonFile)
        return rdata

    def getDomainList(self, jsonFile):
        if not os.path.exists(jsonFile):
            return {"status": "false", "msg": "未上传Excel文件，请上传Excel文件"}
        data = json.loads(public.readFile(jsonFile));
        tmp = [];
        for d in data:
            tmp.append(d);
        data = tmp;
        result = {}
        result['data'] = data;
        return {"status": "success", "data": result['data']}

    def uploadExcel(self, args, path):
        file = self.UploadFile(args)
        df = pd.read_excel(file)
        json = df.to_json(orient='records')
        if os.path.exists(path):
            os.remove(path)
        if not os.path.exists(path):
            public.WriteFile(path, json)
        return {"data": json, "path": path}

    # 上传文件 接收 file
    def UploadFile(self, get):
        from flask import request
        file = request.files['file']
        return file

    # 批量删除 站点
    def delDomainList(self, args):
        data = json.loads(args.siteList)
        # site_file = self.SITE_DEL_FILE;
        # sites_data = self.getReadFile(site_file)
        successSize = [];
        failureSize = [];

        for site in data:
            site_obj = dict_obj()
            site_obj.id = site["id"]
            site_obj.webname = site["name"]
            site_obj.path = site["path"]
            site["database"] = '1'
            site["ftp"] = '1'
            site_obj.database = site['database']
            site_obj.ftp = site['ftp']
            # 批量删除站点
            data = BT_SITE.DeleteSite(site_obj)
            if data['status'] == True:
                successSize.append(data.copy())
            if data['status'] == False:
                failureSize.append(data.copy())
        count = successSize + failureSize
        return {"status": "success",
                "site": {"count": len(count), "successSize": len(successSize), "failureSize": len(failureSize)}
                }

    def replaceStr(self, site_obj):
        import glob
        xmls = glob.glob(site_obj.path + site_obj.sqlConfigPath)
        for one_xml in xmls:
            print(one_xml)
            f = open(one_xml, 'r+')
            all_the_lines = f.readlines()
            f.seek(0)
            f.truncate()
            for line in all_the_lines:
                line = line.replace(site_obj.oldSqlName, site_obj.datauser)
                line = line.replace(site_obj.oldSqlUser, site_obj.datauser)
                line = line.replace(site_obj.oldSqlPW, site_obj.datapassword)
                f.write(line)
            f.close()

    # 批量替换文件
    def replaceFiles(self):
        sitePath = [
            "www.xxx.cn",
        ]

        for site in sitePath:
            os.popen("cd /www/wwwroot/" + site + "/templets/default && rm -f taglist.htm")
            os.popen(
                "cp /www/server/panel/plugin/batchsite/config/taglist.htm " + "/www/wwwroot/" + site + "/templets/default")

    # 批量添加站点域名
    def addDomainList(self, args):
        # 获取用户确认后的 site信息
        # sites_data = self.getReadFile(self.SITE_ADD_FILE)
        # result = {}
        # result['size'] = len(sites_data);
        # # data = json.loads(args.domain_info)
        # for site in sites_data:
        #     return {"status": "Success", "data":sites_data}

        data = json.loads(args.domain_info)
        site_file = self.SITE_ADD_FILE;
        sites_data = self.getReadFile(site_file)

        successSize = [];
        failureSize = [];

        # # 获取前端表单数据
        for site in sites_data:
            domain = site["domain"]
            second_domain = site["second_domain"]
            # if self.checkDomainExist(domain):
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

            #替换老数据库属性变量
            site_obj.sqlConfigPath = data['sqlConfigPath']
            site_obj.oldSqlName = data['oldSqlName']
            site_obj.oldSqlUser = data['oldSqlUser']
            site_obj.oldSqlPW = data['oldSqlPW']

            zipPath = data["zip"]
            sqlPath = data['sqlPath']
            domainPath = data['path'] + domain

            # 添加网站
            psa = BT_SITE.AddSite(site_obj)
            if "siteStatus" in psa.keys():
                successSize.append(psa.copy())
            if "status" in psa.keys():
                failureSize.append(psa.copy())

            # 保存 建站日志到 本地
            # resultSize.append(successSize)
            # resultSize.append(failureSize)
            # self.setWriteFile(successSize, self.PLUGIN_RESULT_LOG)
            # return {"status": "Success", "failureSize": failureSize}

            # 删除网站目录下的所有无用的文件
            os.popen("cd " + domainPath + " && rm -rf *")

            # 解压文件
            os.popen("cd " + self.BAG_PATH + " && unzip -o " + zipPath + " -d " + domainPath + "/")

            cmd = ""
            # 判断网站根目录下是否存在 index.php 文件
            while not os.path.exists(domainPath + "/index.php"):
                for file in os.listdir(domainPath):
                    if os.path.isdir(domainPath + "/" + file):
                        # 将文件夹拷贝到上级文件夹
                        os.popen("mv " + domainPath + "/" + file + "/* " + domainPath)
                        # 删除原文件
                        os.popen("cd " + domainPath + " && rm -rf " + file)

            self.replaceStr(site_obj)

            # 导入数据库
            dataObj = dict_obj()
            dataObj.file = data['path'] + domain + sqlPath
            dataObj.name = site_obj.datauser
            BT_DATA.InputSql(dataObj)

            # 创建FTP
            # BTftp = ftp.ftp()
            FTP = dict_obj()
            FTP.ftp_username = site_obj.ftp_username
            FTP.ftp_password = site_obj.ftp_password
            # FTP.path = domainPath
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
            public.WriteFile(domainPath + "/config.inc.php", PhpConfig.encode("UTF-8"))
            # 删除原目录下的 install 文件夹
            os.popen("rm -rf " + domainPath + "/base/install/")
            file = dict_obj()
            file.filename = domainPath
            file.user = "www"
            file.access = "755"
            file.all = "True"
            files.files().SetFileAccess(file)

        count = successSize + failureSize
        self.setWriteFile(successSize, self.PLUGIN_RESULT_LOG)
        return {"status": "Success", "site":
            {"count": len(count), "successSize": len(successSize), "failureSize": len(failureSize)}}

    # return {"status": "Success", "site": {"Success": domain, "Failure": site_obj.datauser,
    #                                       "data_pass": site_obj.datapassword, "site_path": domainPath,
    #                                       "ftp_username": site_obj.ftp_username, "ftp_password": site_obj.ftp_password}}

    # 获取宝塔 域名列表
    def getBtData(self, args):
        # data = json.loads(args.data)
        site_obj = dict_obj()
        site_obj.table = "sites"
        site_obj.limit = 2000
        site_obj.p = "1"
        order = ""
        if order == "desc":
            site_obj.order = "id " + order
        else:
            site_obj.order = order
        site_obj.type = "-1"

        rdata = BT_DOMAIN_DATA.getData(site_obj)
        attr = {'id', 'name', 'path'}
        rdataList = []
        for dic in rdata["data"]:
            rdataDict = {key: value for key, value in dic.items() if key in attr}
            rdataList.append(rdataDict)
        frame = pd.DataFrame(rdataList)
        exclePath = self.AP_EXCLE_PATH
        frame.to_excel(exclePath, index=False)
        if not os.path.exists(exclePath):
            return public.returnMsg(False, 'DIR_NOT_EXISTS_ERR')
        return {"status": "success", "path": exclePath}

    # 判断域名是否存在
    def checkDomainExist(self, cdomain):
        # 获得当前配置文件下的所有域名
        Domains = self.GetHostConfig("")
        for domain in Domains["domains"]:
            if domain["host"] == cdomain:
                return True
        return False

    # 获取新站点的ID
    def getSiteNewID(self):
        MaxId = public.M("sqlite_sequence").where('name=?', ("sites")).field('seq').find()
        if "seq" in MaxId:
            Id = MaxId["seq"]
        else:
            Id = 0
        return int(Id) + 1

    # 获得可以一键部署的文件列表
    def getInstallList(self, args):
        self.FileDir = []
        dir = dict_obj()
        dir.path = self.BAG_PATH
        dir.back = 1
        List = self.getFileDirList(dir)
        for file in List:
            # 检查文件是不是 zip 格式的压缩文件
            if not re.match("\S{1,}.zip", str(file)) or not os.path.isfile(self.BAG_PATH + file):
                List.remove(file)
        return {"status": "Success", "List": List}

    # 递归获得指定文件下下的所有文件
    def getFileDirList(self, args):
        for file in os.listdir(args.path):
            path = os.path.join(file)
            if os.path.isdir(path):
                rec = dict_obj()
                rec.back = 0
                rec.path = path
                self.getFileDirList(rec)
            else:
                self.FileDir.append(path)
        if int(args.back) == 1:
            return self.FileDir

    # 获得当前的php 的版本信息
    def optionPHPVersion(self, args):
        version = BT_SITE.GetPHPVersion(args)
        return {"status": "Success", "list": version}
