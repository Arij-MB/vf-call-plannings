from datetime import datetime
from .model import Maranfleet, Maran_error_report, R4s_ports, Vf_call_plannings
from django.db import connection


def maran_check():
    Maran_error_report.objects.all().delete()
    # Truncate the Maran_error_report table
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE maran_error_report;")

    # Retrieve the most recent Maranfleet object for each unique IMO number and port combination in the db
    for imo, port in Maranfleet.objects.order_by('-date_of_scrapping').values_list('imo', 'port').distinct():
        maran = Maranfleet.objects.filter(imo=imo, port=port).order_by('-date_of_scrapping').first()


        # I added this just in case we have an imo with no action_date
        if maran.date_of_action != '-':
            date_str = maran.date_of_action
            date_time_obj = datetime.strptime(date_str, '%b %d, %H:%M')
            # date_only = date_time_obj.strftime('%b %d')
            date_only = date_time_obj.strftime('%d/%m/2023')

        else:
            Maran_error_report.objects.update_or_create(
                imo=maran.imo,
                defaults={
                    'port': maran.port,
                    'unlocode': maran.unlocode,
                    'action': maran.action,
                    'date_of_action': maran.date_of_action,
                    'date_of_scrapping': maran.date_of_scrapping,
                    'status': "Unavailable Date Of Action"}),
            maran.is_checked = 1
            maran.save()

        # case 1*  (port == NULL) && (unlocode == NULL) || (port == NULL) && (unlocode.nospace.length <>5)
        if (maran.port is None and maran.unlocode is None) or (
                maran.port is None and len(maran.unlocode) != 5):
            # print('Processing case 1...')
            Maran_error_report.objects.update_or_create(
                imo=maran.imo,
                defaults={
                    'port': maran.port,
                    'unlocode': maran.unlocode,
                    'action': maran.action,
                    'date_of_action': date_only,
                    'date_of_scrapping': maran.date_of_scrapping,
                    'status': "No Port Data"})
            maran.is_checked = 1
            maran.save()

        # case 2* ELSE IF (unlocode.nospace NOT exists to P.Port.unlocode)
        elif maran.unlocode not in R4s_ports.objects.values_list('un_locode', flat=True) \
                and not Vf_call_plannings.objects.filter(
            ship_imo=maran.imo).exists():  # a flat list of unlocode values instead of a list of tuple
            # print('Processing case 2...')
            Maran_error_report.objects.update_or_create(
                imo=maran.imo,
                defaults={
                    'port': maran.port,
                    'unlocode': maran.unlocode,
                    'action': maran.action,
                    'date_of_action': date_only,
                    'date_of_scrapping': maran.date_of_scrapping,
                    'status': "No UNLOCODE Found"})
            maran.is_checked = 1
            maran.save()

        # case 3*   (port <>NULL) && (action == ETA)
        elif maran.port is not None and maran.action == 'ETA':
            #ports = R4s_ports.objects.filter(name__iexact=maran.port.strip())
            ports = R4s_ports.objects.filter(name__icontains=maran.port.strip())
            # print('Processing case 3...')
            if ports.exists() and not maran.is_checked:
                port = ports.first().name
                unlocode = ports.first().un_locode
                Vf_call_plannings.objects.update_or_create(
                    ship_imo=maran.imo,
                    defaults={
                        'date': date_only,
                        'port_name': port,
                        'port_country': maran.country,
                        'port_unlocode': unlocode
                    })
                maran.is_checked = 1
                maran.save()
            elif not Vf_call_plannings.objects.filter(ship_imo=maran.imo).exists():
                Maran_error_report.objects.update_or_create(
                    imo=maran.imo,
                    defaults={
                        'port': maran.port,
                        'unlocode': maran.unlocode,
                        'action': maran.action,
                        'date_of_action': date_only,
                        'date_of_scrapping': maran.date_of_scrapping,
                        'status': f"{maran.port.strip()} Is Not Found"
                    })
                maran.is_checked = 1
                maran.save()

        # FOR rest rows of S
        else:
            # print('Processing case else...')
            if maran.action != 'ATA':
                if maran.action == 'ETA':

                    print(date_only)

                    Vf_call_plannings.objects.update_or_create(
                        ship_imo=maran.imo,
                        defaults={
                            'date': date_only,
                            'port_name': maran.port,
                            'port_country': maran.country,
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
