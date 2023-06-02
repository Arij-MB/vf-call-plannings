from django.db import models


class Maran_error_report(models.Model):
    id = models.AutoField(primary_key=True)
    imo = models.CharField(max_length=10, null=True)
    port = models.TextField(max_length=50, null=True)
    unlocode = models.TextField(max_length=6, null=True)
    date_of_action = models.TextField(max_length=30, null=True)
    action = models.TextField(max_length=20, null=True)
    status = models.CharField(max_length=255)
    date_of_scrapping = models.TextField(max_length=30, null=True)

    class Meta:
        db_table = 'maran_error_report'


class Maranfleet(models.Model):
    imo = models.CharField(max_length=10, null=True)
    port = models.TextField(max_length=50, null=True)
    country = models.TextField(max_length=50, null=True)
    unlocode = models.TextField(max_length=6, null=True)
    date_of_action = models.TextField(max_length=30, null=True)
    action = models.TextField(max_length=20, null=True)
    prediction = models.TextField(max_length=20, null=True)
    date_of_scrapping = models.TextField(max_length=30, null=True)
    is_checked = models.BooleanField(null=True)


    class Meta:
        db_table = 'scrapper_maranfleet'


class R4s_ports(models.Model):
    name = models.TextField(max_length=255)
    #country = models.TextField(max_length=255)
    un_locode = models.TextField(max_length=255)
    latitude = models.TextField(max_length=255)
    longitude = models.TextField(max_length=255)
    # psc_id = models.CharField(max_length=255)
    #corresponding_un_locode = models.TextField(max_length=255)
    #reporting_MoU = models.TextField(max_length=255)
    # created_at = models.CharField(max_length=255)
    # updated_at = models.CharField(max_length=255)

    class Meta:
        db_table = 'r4s_ports'


class Vf_call_plannings(models.Model):
    id = models.AutoField(primary_key=True)
    ship_imo = models.TextField(max_length=7, null=False)
    date = models.DateField(null=False)
    port_name = models.TextField(max_length=255, null=False)
    # port_country = models.TextField(max_length=30, null=False)
    port_unlocode = models.TextField(max_length=5, null=False)

    class Meta:
        db_table = 'vf_call_plannings'
