from django.db import models

# Create your models here.


# class NWADMember(models.Model):
#     member_no = models.AutoField(db_column='member_no', primary_key=True)
#     id = models.CharField(db_column='id', unique=True, max_length=20)
#     password = models.CharField(db_column='password')


class log(models.Model):
    no = models.AutoField(db_column='no', primary_key=True)
    msg = models.TextField(db_column='msg', null=False)
    reg_date = models.DateTimeField(db_column='reg_date', auto_now=True)
    reg_user = models.CharField(db_column='reg_user', max_length=20)

    class Meta:
        managed = True
        db_table = 'log'

    def __str__(self):
        return self.no
    
class member(models.Model):
    member_no = models.AutoField(db_column='member_no', primary_key=True)
    id = models.CharField(db_column='id', null=False, max_length=20, unique=True)
    password = models.TextField(db_column='password')
    name = models.CharField(db_column='name', max_length=5)
    email = models.CharField(db_column='email', max_length=50)
    reg_date = models.DateTimeField(db_column='reg_date', auto_now=True)
    status = models.CharField(db_column='status', max_length=1, default='2') # 1:정상 ,2:가입대기, 3:가입취소, 4:가입반려, 9:탈퇴
    rmk = models.TextField(db_column='rmk', null=True)
    corp_name = models.TextField(db_column='corp_name', max_length=50)

    class Meta:
        managed = True
        db_table = 'member'

    def __str__(self):
        return self.member_no
    
class api(models.Model):
    api_no = models.AutoField(db_column='api_no', primary_key=True)
    member_no = models.ForeignKey(member, related_name="fk_member_api", on_delete=models.CASCADE, db_column="member_no")
    api_name = models.CharField(db_column="api_name", null=False, max_length=20)
    client_id = models.CharField(db_column="client_id", null=False, max_length=20)
    client_secret = models.CharField(db_column="client_secret", null=False, max_length=10)
    service_account = models.CharField(db_column="service_account", null=False, max_length=50)
    private_key = models.TextField(db_column="private_key", null=False)
    scope = models.TextField(db_column="scope", null=False)
    reg_date = models.DateTimeField(db_column='reg_date', auto_now=True)
    rmk = models.TextField(db_column='rmk', null=True)

    class Meta:
        managed = True
        db_table = 'api'

    def __str__(self):

        return self.api_no
    
class bot(models.Model):
    bot_no = models.AutoField(db_column='bot_no', primary_key=True)
    member_no = models.ForeignKey(member, related_name="fk_member_bot", on_delete=models.CASCADE, db_column="member_no")
    bot_id = models.CharField(db_column="bot_id", null=False, max_length=10)
    bot_secret = models.CharField(db_column="bot_secret", null=False, max_length=30)
    bot_name = models.CharField(db_column="bot_name", null=False, max_length=10)
    reg_date = models.DateTimeField(db_column='reg_date', auto_now=True)
    rmk = models.TextField(db_column='rmk', null=True)

    class Meta:
        managed = True
        db_table = 'bot'

    def __str__(self):
        return self.bot_no

    
class token(models.Model):
    token_no = models.AutoField(db_column='token_no', primary_key=True)
    api_no = models.ForeignKey(api, related_name="fk_api_token", on_delete=models.CASCADE, db_column="api_no")
    type = models.CharField(db_column="type", null=False, max_length=20)
    token = models.TextField(db_column="token", null=False)
    scope = models.TextField(db_column="scope", null=False)
    exp_date = models.DateTimeField(db_column='exp_date', null=False)
    reg_date = models.DateTimeField(db_column='reg_date', auto_now=True)
    rmk = models.TextField(db_column='rmk', null=True)

    class Meta:
        managed = True
        db_table = 'token'

    def __str__(self):
        return self.token
    

class scen_type(models.Model):
    scen_type = models.AutoField(db_column='scen_type', primary_key=True)
    title = models.CharField(db_column="title", null=False, max_length=20)
    reg_date = models.DateTimeField(db_column='reg_date', auto_now=True)
    rmk = models.TextField(db_column='rmk', null=True)

    class Meta:
        managed = True
        db_table = 'scen_type'

    def __str__(self):
        return self.scen_type

class scen(models.Model):
    scen_no = models.AutoField(db_column='scen_no', primary_key=True)
    scen_name = models.CharField(db_column="scen_name", null=False, max_length=20)
    member_no = models.ForeignKey(member, related_name="fk_member_scen", on_delete=models.CASCADE, db_column="member_no")
    scen_type = models.ForeignKey(scen_type, related_name="fk_scen_type_scen", on_delete=models.CASCADE, db_column="scen_type")
    api_no = models.ForeignKey(api, related_name="fk_api_scen", on_delete=models.CASCADE, db_column="api_no")
    bot_no = models.ForeignKey(bot, related_name="fk_bot_scen", on_delete=models.CASCADE, db_column="bot_no")
    domain = models.CharField(db_column="domain", null=False, max_length=10)
    channel = models.CharField(db_column="channel", null=False, max_length=40)
    members = models.TextField(db_column="members", null=False)
    status = models.CharField(db_column='status', max_length=1, default='1') # 1:사용 중 ,2:사용 정지, 9:삭제
    reg_date = models.DateTimeField(db_column='reg_date', auto_now=True)
    rmk = models.TextField(db_column='rmk', null=True)

    class Meta:
        managed = True
        db_table = 'scen'

    def __str__(self):
        return self.scen_no

class scen_conn(models.Model):
    conn_no = models.AutoField(db_column='conn_no', primary_key=True)
    scen_no = models.ForeignKey(scen, related_name="fk_scen_scen_conn", on_delete=models.CASCADE, db_column="scen_no")
    reporter = models.CharField(db_column="reporter", null=True, max_length=40)
    approver = models.CharField(db_column="approver", null=True, max_length=40)
    status = models.CharField(db_column='status', max_length=1, default='2') # 1:대화중 ,2:대화 요청중, 3:대화 대기중, 9:대화 종료
    message = models.TextField(db_column='message', null=True)
    reg_date = models.DateTimeField(db_column='reg_date', auto_now=True)
    rmk = models.TextField(db_column='rmk', null=True)

    class Meta:
        managed = True
        db_table = 'scen_conn'

    def __str__(self):
        return self.conn_no
