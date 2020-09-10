import re,io


def replaceStr(obj):
    import glob
    xmls = glob.glob('D:\common.inc.php')
    for one_xml in xmls:
        print(one_xml)
        f = open(one_xml, 'r+')
        all_the_lines = f.readlines()
        f.seek(0)
        f.truncate()
        for line in all_the_lines:
            line = line.replace('root', obj.datauser)
            line = line.replace('9568', obj.datauser)
            line = line.replace('xuxinqjw_com', obj.datapassword)
            f.write(line)
        f.close()

if __name__ == '__main__':
    # 取通用对象
    class dict_obj:
        def __contains__(self, key):
            return getattr(self, key, None)

        def __setitem__(self, key, value): setattr(self, key, value)

        def __getitem__(self, key): return getattr(self, key, None)

        def __delitem__(self, key): delattr(self, key)

        def __delattr__(self, key): delattr(self, key)

        def get_items(self): return self


    obj = dict_obj()

    obj.datauser = "aaa"
    obj.datapassword = "bbb"

    replaceStr(obj)
