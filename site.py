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
        self.second_domain = second_domain

    @property
    def datauser(self):
        return self.datauser

    @datauser.setter
    def datauser(self, datauser):
        self.datauser = datauser

    @property
    def datapassword(self):
        return self.datapassword

    @datapassword.setter
    def datapassword(self, datapassword):
        self.datapassword = datapassword

    @property
    def ftp_username(self):
        return self.ftp_username

    @datapassword.setter
    def ftp_username(self, ftp_username):
        self.ftp_username = ftp_username

    @property
    def ftp_password(self):
        return self.ftp_password

    @ftp_password.setter
    def datapassword(self, ftp_password):
        self.ftp_password = ftp_password
