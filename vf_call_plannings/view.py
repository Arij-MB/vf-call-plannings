from datetime import datetime
from .model import Maranfleet, Maran_error_report, R4s_ports, Vf_call_plannings, Fleet_vt
from django.db import connection


def maran_check():
    Maran_error_report.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE maran_error_report;")

    Vf_call_plannings.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE vf_call_plannings;")

    # Retrieve the most recent Maranfleet object for each unique IMO number and port combination in the db
    for imo, port in Maranfleet.objects.order_by('-date_of_scrapping').values_list('imo', 'port').distinct():
        maran = Maranfleet.objects.filter(imo=imo, port=port).order_by('-date_of_scrapping').first()

        if maran.date_of_action != '-':
            date_str = maran.date_of_action
            date_time_obj = datetime.strptime(date_str, '%b %d, %H:%M')
            # date_only = date_time_obj.strftime('%b %d')
            date_only = date_time_obj.strftime('%d/%m/2023')
            date_obj = datetime.strptime(date_only, '%d/%m/%Y').date()
        else:
            maran.is_checked = 1
            maran.save()

        # case 1*  (port == NULL) && (unlocode == NULL) || (port == NULL) && (unlocode.nospace.length <>5)
        # if (maran.port is None and maran.unlocode is None) or (
        #         maran.port is None and len(maran.unlocode.replace(" ", "")) != 5):
        # we cannot use is None because of cronulla
        if (maran.port == 'NULL' and maran.unlocode == 'NULL') or (
                    maran.port == 'NULL' and len(maran.unlocode.replace(" ", "")) != 5):
            # print('Processing case 1...')
            Maran_error_report.objects.update_or_create(
                imo=maran.imo,
                defaults={
                    'port': maran.port,
                    'unlocode': maran.unlocode,
                    'action': maran.action,
                    'date_of_action': date_obj,
                    'date_of_scrapping': maran.date_of_scrapping,
                    'status': "No Port Data"})
            maran.is_checked = 1
            maran.save()

        # case 2* ELSE IF (unlocode.nospace NOT exists to P.Port.unlocode)
        elif maran.unlocode.replace(" ", "") not in R4s_ports.objects.values_list('un_locode', flat=True):
               # and not Vf_call_plannings.objects.filter(
            # ship_imo=maran.imo).exists():  # a flat list of unlocode values instead of a list of tuple
            Maran_error_report.objects.update_or_create(
                imo=maran.imo,
                defaults={
                    'port': maran.port,
                    'unlocode': maran.unlocode,
                    'action': maran.action,
                    'date_of_action': date_obj,
                    'date_of_scrapping': maran.date_of_scrapping,
                    'status': "No UNLOCODE Found"})
            maran.is_checked = 1
            maran.save()

        # case 3*   (port <>NULL) && (action == ETA)
        elif maran.port != 'NULL' and maran.action == 'ETA':
            ports = R4s_ports.objects.filter(name__icontains=maran.port.strip())
            fleets = Fleet_vt.objects.filter(sid__iexact=maran.imo.strip())
            fleet_name = fleets.first().fleetname
            # print('Processing case 3...')
            if ports.exists():
                # port = ports.first().name
                unlocode = ports.first().un_locode
                Vf_call_plannings.objects.update_or_create(
                    ship_imo=maran.imo,
                    defaults={
                        'fleet_name': fleet_name,
                        'date': date_obj,
                        'port_name': maran.port,
                        'port_unlocode': unlocode
                    })
                maran.is_checked = 1
                maran.save()

            else:
                if not Vf_call_plannings.objects.filter(ship_imo=maran.imo).exists():
                    Maran_error_report.objects.update_or_create(
                        imo=maran.imo,
                        defaults={
                            'port': maran.port,
                            'unlocode': maran.unlocode,
                            'action': maran.action,
                            'date_of_action': date_obj,
                            'date_of_scrapping': maran.date_of_scrapping,
                            'status': f"{maran.port.strip()} Is Not Found"
                        })
                maran.is_checked = 1
                maran.save()

        # FOR rest rows of S
        elif maran.port != 'NULL' and maran.unlocode != 'NULL':
            # print('Processing case else...')
            if maran.action != 'ATA':
                if maran.action == 'ETA':
                    fleets = Fleet_vt.objects.filter(sid__iexact=maran.imo.strip())
                    fleet_name = fleets.first().fleetname
                    Vf_call_plannings.objects.update_or_create(
                        ship_imo=maran.imo,
                        defaults={
                            'fleet_name': fleet_name,
                            'date': date_obj,
                            'port_name': maran.port,
                            'port_unlocode': maran.unlocode
                        })
                    maran.is_checked = 1
                    maran.save()
                else:
                    print('Processing just update is_checked...')
                    maran.is_checked = 1
                    maran.save()
            else:
                # No information of how to treat the case where ATA& NULL unlocode
                maran.is_checked = 0
                maran.save()
