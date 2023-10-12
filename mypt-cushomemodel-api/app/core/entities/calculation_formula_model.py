import math

from app.http.models.average_bandwidth_of_equipment import AverageBandwidthOfEquipment
from app.http.models.configs import Configs
from app.http.models.equipments import Equipments
from app.http.models.house_model_type import HouseModelType
from app.http.models.internet_packages import InternetPackages
from app.http.serializers.config_serializer import ConfigsSerializer
from app.http.serializers.equipments_serializer import EquipmentsSerializer
from app.http.serializers.internet_packages_serializer import InternetPackagesSerializer


def calculation_model(data):
    try:
        average_bandwidth = list(AverageBandwidthOfEquipment.objects.all())
        average_user = average_bandwidth[0].average_bandwidth
        average_camera = average_bandwidth[-1].average_bandwidth

        number_of_devicess = 0

        id_type = data['idType']
        customer_type = data['customerType'].lower()

        # tính số người dùng wifi / user_wifi
        if id_type == 4:
            user_wifi = data['rowsPerFloor'] * (data['floors'] + 1) * data['roomsPerRow'] \
                        * data['peoplePerRoom']
        else:
            user_wifi = data['userWifi']

        if id_type not in (1, 3) and data['otherCheck'] == 1:
            number_of_devices = math.ceil(user_wifi * 1.5 * (data['concurrentUsageRate'] / 100) + data['userLAN'] +
                                          (data['otherUserWifi'] * 1.5))
            bandwidth_require = math.ceil((user_wifi * 1.5 * (data['concurrentUsageRate'] / 100) + data[
                'otherUserWifi'] * 1.5 + data['userLAN']) * average_user + data['userCamera'] * average_camera)
        else:
            number_of_devices = math.ceil(user_wifi * 1.5 * (data['concurrentUsageRate'] / 100) + data['userLAN'])
            bandwidth_require = math.ceil((user_wifi * 1.5 * (data['concurrentUsageRate'] / 100) +
                                           data['userLAN']) * average_user + data['userCamera'] * average_camera)

        internet_packages = list_internet_package(bandwidth_require=bandwidth_require, customer_type=customer_type,
                                                  upload_alot_check=data['uploadAlotCheck'],
                                                  lux_package_check=data['luxPackageCheck'])

        modems = list_modem(number_of_devices=number_of_devices, customer_type=customer_type,
                            net_packages=internet_packages)

        access_points = list_access_point(modem=modems, data=data, user_wifi=user_wifi)

        conclusion = conclusion_calculate_model(net_present=data['internetPackages'],
                                                net_result=internet_packages,
                                                bandwidth_require=bandwidth_require,
                                                modem_present=data['routers'],
                                                modem_result=modems,
                                                number_of_devices=number_of_devicess,
                                                ap_present=data['accessPoints'],
                                                ap_result=access_points,
                                                total_ap_present=data['totalAP'])

        result = {
            'userWifi': user_wifi,
            'totalAP': {
                'model': access_points['modelTotalAP'],
                'other': access_points['otherTotalAP']
            },
            'internetPackages': internet_packages,
            'routers': modems,
            'accessPoints': {
                'model': access_points['model'],
                'other': access_points['other']
            },
            'conclusion': conclusion['conclusion'],
            'statusSurvey': conclusion['status'],
        }

        return result
    except Exception as ex:
        print(f'Error/Loi: {str(ex)}')
        return None


def list_internet_package(bandwidth_require, customer_type, upload_alot_check, lux_package_check):
    net_packages = []
    if lux_package_check == 1:
        data_net_package = InternetPackages.objects.filter(
            lux=1, is_active=InternetPackages.IS_AVAILABILITY
        ).order_by('-download_speed', '-upload_speed')
        data_net_package = InternetPackagesSerializer(data_net_package, many=True,
                                                      fields=['id', 'name', 'downloadSpeed', 'uploadSpeed'])
        data_net_package = [dict(item) for item in data_net_package.data]

        largest_lux_package = data_net_package[0]
        smallest_lux_package = data_net_package[-1]

        if bandwidth_require % largest_lux_package['downloadSpeed'] == 0:
            total_lux_package = bandwidth_require // largest_lux_package['downloadSpeed']
            net_packages = [largest_lux_package] * total_lux_package
        else:
            while bandwidth_require > 0:
                if bandwidth_require >= largest_lux_package['downloadSpeed']:
                    net_packages.append(largest_lux_package)
                else:
                    for idx in range(len(data_net_package) - 1):
                        if bandwidth_require > data_net_package[idx + 1]['downloadSpeed']:
                            net_packages.append(data_net_package[idx])
                            break
                        elif bandwidth_require <= smallest_lux_package['downloadSpeed']:
                            net_packages.append(smallest_lux_package)
                            break
                bandwidth_require -= largest_lux_package['downloadSpeed']
    else:  # Nếu upload nhiều thì auto chọn gói Meta, ngược lại băng thông dưới 150 chọn giga, trên 150 chọn sky
        if customer_type == 'cá nhân':
            data_net_package = InternetPackages.objects.filter(
                customer_type=InternetPackages.CUSTOMER_TYPE_CA_NHAN, is_active=InternetPackages.IS_AVAILABILITY
            ).order_by('-download_speed', '-upload_speed')
            data_net_package = InternetPackagesSerializer(data_net_package, many=True,
                                                          fields=['id', 'name', 'downloadSpeed', 'uploadSpeed'])
            data_net_package = [dict(item) for item in data_net_package.data]

            largest_package = data_net_package[0]
            second_largest_package = data_net_package[1]
            smallest_package = data_net_package[-1]

            if bandwidth_require <= largest_package['downloadSpeed']:
                if upload_alot_check != 1:
                    data_net_package.remove(data_net_package[0])

                closest_greater = None

                if upload_alot_check == 1:  # nếu UPLOAD NHIỀU thì cứ chọn gói cước phù hợp nhất, không care Upload Speed
                    for item in data_net_package:
                        if closest_greater is None or bandwidth_require <= item['downloadSpeed'] < closest_greater['downloadSpeed']:
                            closest_greater = item
                else:
                    for item in data_net_package:
                        if closest_greater is None or bandwidth_require <= item['downloadSpeed']:
                            closest_greater = item

                net_packages.append(closest_greater)
            else:
                # nếu count_one_package = 1 thì loại gói có Upload Speed lớn nhất sau lần pick đầu tiên
                count_one_package = 0
                # nếu KHÔNG UPLOAD NHIỀU thì loại gói có Upload Speed lớn nhất
                if upload_alot_check != 1:
                    data_net_package.remove(largest_package)
                while bandwidth_require > 0:

                    # chọn gói lớn nhất trong list
                    closest_greater = None
                    if upload_alot_check == 1:  # nếu UPLOAD NHIỀU thì chọn gói có Upload Speed lớn hơn, trong list data_net_package order_by('-downloadSpeed', '-upload_speed')
                        for item in data_net_package:
                            if closest_greater is None or bandwidth_require <= item['downloadSpeed'] < closest_greater['downloadSpeed']:
                                closest_greater = item

                    else:  # nếu KHÔNG UPLOAD NHIỀU thì cứ chọn gói cước phù hợp nhất, không care Upload Speed
                        for item in data_net_package:
                            if closest_greater is None or bandwidth_require <= item['downloadSpeed'] <= closest_greater['downloadSpeed']:
                                closest_greater = item

                    if count_one_package == 0 and upload_alot_check == 1:
                        data_net_package.remove(data_net_package[0])
                        count_one_package += 1
                    net_packages.append(closest_greater)
                    bandwidth_require -= closest_greater['downloadSpeed']
        else:  # ( if customer_type == 'doanh nghiệp': )
            data_net_package = InternetPackages.objects.filter(
                customer_type=InternetPackages.CUSTOMER_TYPE_DOANH_NGHIEP,
                is_active=InternetPackages.IS_AVAILABILITY
            ).order_by('-download_speed', '-upload_speed')
            data_net_package = InternetPackagesSerializer(data_net_package, many=True,
                                                          fields=['id', 'name', 'downloadSpeed',
                                                                  'uploadSpeed'])
            data_net_package = [dict(item) for item in data_net_package.data]
            largest_package = data_net_package[0]
            smallest_package = data_net_package[-1]
            if bandwidth_require % largest_package['downloadSpeed'] == 0:
                total_lux_package = bandwidth_require // largest_package['downloadSpeed']
                net_packages = [largest_package] * total_lux_package
            else:
                while bandwidth_require > 0:
                    if bandwidth_require >= largest_package['downloadSpeed']:
                        net_packages.append(largest_package)
                    else:
                        for idx in range(len(data_net_package) - 1):
                            if bandwidth_require > data_net_package[idx + 1]['downloadSpeed']:
                                net_packages.append(data_net_package[idx])
                                break
                            elif bandwidth_require <= smallest_package['downloadSpeed']:
                                net_packages.append(smallest_package)
                                break
                    bandwidth_require -= largest_package['downloadSpeed']
    unique_list = []
    for item in net_packages:
        if item not in unique_list:
            item['quantity'] = net_packages.count(item)
            unique_list.append(item)
    return unique_list


def list_modem(number_of_devices, customer_type, net_packages):
    check_number_of_devices = number_of_devices
    total_quantity_net_package = sum([item['quantity'] for item in net_packages])  # Tổng số gói cước cần cước

    total_quantity_net_package_check = total_quantity_net_package  # Tổng số gói cước đã tính được để kiểm tra
    total_quantity_WAN_modem = 0  # Tổng số cổng WAN của modem đã tính được
    total_LANWifi_modem = 0  # Tổng số cổng LAN/Wifi của modem đã tính được
    queryset = Equipments.objects.filter(modem_rule=Equipments.MODEM_RULE_TYPE_MODEM,
                                         device_origin=Equipments.DEVICE_ORIGIN_INSIDE,
                                         is_active=Equipments.IS_ACTIVE).order_by('lan_wifi', 'wifi', 'quantity_wan',
                                                                                  '-code_id')
    serializer_modem = EquipmentsSerializer(queryset, many=True,
                                            fields=['id', 'codeID', 'name', 'LANWifi', 'wifi',
                                                    'quantityWAN', 'wifi24Pow', 'wifi5Pow']).data
    result_modem = []
    if customer_type == 'doanh nghiệp':
        modems = [dict(item) for item in serializer_modem if item['wifi'] == 0]
    else:  # customer_type == 'ca_nhan'
        modems = sorted(serializer_modem, key=lambda x: (x['LANWifi'], x['wifi'], x['quantityWAN'], x['codeID']))

    # có thiết bị phù hợp thì lấy modem phù hợp nhất
    if modems:
        if number_of_devices <= modems[-1]['LANWifi']:
            closest_greater = None
            for item in modems[::-1]:
                if item['LANWifi'] >= number_of_devices:
                    if closest_greater is None or item['LANWifi'] < closest_greater['LANWifi']:
                        if item['quantityWAN'] >= total_quantity_net_package:
                            closest_greater = item
            total_quantity_WAN_modem += closest_greater['quantityWAN']
            total_LANWifi_modem += closest_greater['LANWifi']
            result_modem.append(closest_greater)
        else:  # nếu lớn hơn thiết bị có năng lực tối đa thì tính theo phương thức cộng dồn
            modem_required = math.ceil((number_of_devices / modems[-1]['LANWifi']))
            if modem_required > total_quantity_net_package:  # nếu số modem cần lớn hơn số lượng gói cước cần
                return result_modem
            if total_quantity_net_package == 1:  # nếu các gói cước đều có năng lực giống nhau
                average_number_of_devices = math.ceil(number_of_devices / total_quantity_net_package)
                for item in modems:
                    if (average_number_of_devices <= item['LANWifi'] and
                            item['quantityWAN'] >= total_quantity_net_package):
                        item.pop('codeID')
                        total_quantity_WAN_modem += item['quantityWAN']
                        result_modem.append(item)
            elif total_quantity_net_package > 1:  # nếu các gói cước đều có năng lực khác nhau
                modems = modems[::-1]
                largest_modem = modems[0]
                total_quantity_wan = total_quantity_net_package
                valid_modems = []
                while number_of_devices > 0:
                    closest_greater = None
                    if number_of_devices >= largest_modem['LANWifi']:
                        result_modem.append(largest_modem)
                        valid_modems.append(largest_modem)
                        total_quantity_wan -= largest_modem['quantityWAN']
                        total_LANWifi_modem += largest_modem['LANWifi']
                        total_quantity_WAN_modem += largest_modem['quantityWAN']
                    else:
                        for item in modems:
                            if item['LANWifi'] >= number_of_devices:
                                if closest_greater is None or item['LANWifi'] < closest_greater['LANWifi']:
                                    closest_greater = item
                                    valid_modems.append(closest_greater)
                        # kiểm tra tổng các modem có sổ cổng WAN vẫn không >= số lượng gói cước cần nếu đã tính được
                        # tổng các modem đáp ứng SL user:
                        if (total_quantity_wan - closest_greater['quantityWAN']) > 0 >= (
                                number_of_devices - closest_greater['LANWifi']):
                            for valid_modem in valid_modems[::-1]:
                                if total_quantity_wan - valid_modem['quantityWAN'] <= 0:
                                    closest_greater = valid_modem
                                    break
                        result_modem.append(closest_greater)
                        total_quantity_wan -= closest_greater['quantityWAN']
                        total_LANWifi_modem += closest_greater['LANWifi']
                        total_quantity_WAN_modem += closest_greater['quantityWAN']
                    number_of_devices -= largest_modem['LANWifi']
    else:
        return []

    if check_number_of_devices - total_LANWifi_modem > 0:
        return []
    else:  # lấy những thiết bị có ID mới nhất nhưng phải cùng năng lực và có thể đáp ứng cổng WAN
        for index in range(len(result_modem)):
            for item in modems:
                if item['LANWifi'] == result_modem[index]['LANWifi'] and item['wifi'] == result_modem[index]['wifi'] \
                        and (total_quantity_net_package_check <= (
                        total_quantity_WAN_modem - result_modem[index]['quantityWAN']) + item['quantityWAN']) \
                        and item['codeID'] > result_modem[index]['codeID']:
                    result_modem[index] = item
                    # pass
    # chỗ này liệt kê các modem cần và quantity là đếm số lượng từng modem riêng biệt
    unique_list = []
    if len(result_modem) > 0:
        for item in result_modem:
            if item not in unique_list:
                item['quantity'] = result_modem.count(item)
                if 'quantityWAN' in item:
                    item.pop('quantityWAN')
                    item.pop('codeID')
                unique_list.append(item)
    return unique_list


def list_access_point(modem, data, user_wifi):
    model = HouseModelType.objects.get(id=data['idType'])
    other = HouseModelType.objects.get(id=2)
    result = {
        'modelTotalAP': 0,
        'otherTotalAP': 0,
        'model': [],
        'other': [],
    }

    access_points = EquipmentsSerializer(Equipments.objects.filter(
        modem_rule__in=(Equipments.MODEM_RULE_TYPE_ACCESS_POINT, Equipments.MODEM_RULE_TYPE_BOTH),
        device_origin=Equipments.DEVICE_ORIGIN_INSIDE,
        is_active=Equipments.IS_ACTIVE).order_by('wifi'),
                                         many=True,
                                         fields=['id', 'name', 'LANWifi', 'wifi', 'quantityWAN', 'wifi24Pow',
                                                 'wifi5Pow'])
    if not access_points.data:
        return result
    access_points = [dict(item) for item in access_points.data]
    total_rows_per_floor = data['rowsPerFloor']
    total_floors = data['floors']
    total_modem_have_wifi = 0
    total_modem_wifi = 0
    total_AP_model = 0
    total_AP_other = 0
    power_model_AP = 0
    power_other_AP = 0
    result_access_point_model = []
    result_access_point_other = []

    result = {
        'modelTotalAP': total_AP_model,
        'otherTotalAP': total_AP_other,
        'model': result_access_point_model,
        'other': result_access_point_other,
    }
    largest_AP = access_points[-1]

    # nếu không có modem thì return luôn vì không có giá trị để tính AP
    # chọn gói modem tốt nhất
    if len(modem) > 0:
        for item in modem:
            if item['wifi'] > 0:
                total_modem_have_wifi += 1 * item['quantity']
            total_modem_wifi += item['wifi'] * item['quantity']
    else:
        return result

    # nếu model == 'Khu nhà trọ, ktx, khách sạn, karaoke' ---> số dãy mặc định = 1
    # nếu model == 'Nhà trệt, căn hộ chung cư' ---> số tầng mặc định = 0
    if data['idType'] != 4:
        total_rows_per_floor = 1
    if data['idType'] == 1:
        total_floors = 0

    total_AP_model = math.ceil(((total_floors + 1) * data['houseLength'] *
                                data['houseWidth']) / model.covered_area - total_modem_have_wifi)

    if total_AP_model == 0:
        if total_modem_wifi >= data['userWifi'] * 1.5:
            total_AP_model = 0
        elif total_modem_wifi < data['userWifi'] * 1.5:  # modem['wifi'] < data['userWifi']
            total_AP_model = 1

    # check tổng số AP không phải là bội số của tổng số tầng [total_rows_per_floor * (total_floors + 1)]
    if (total_AP_model + total_modem_have_wifi) % (total_rows_per_floor * (total_floors + 1)) != 0:
        multiple = total_AP_model // (total_rows_per_floor * (total_floors + 1)) + 1
        total_AP_model = multiple * (total_rows_per_floor * (total_floors + 1)) - total_modem_have_wifi

    # tính năng lực AP theo mô hình
    if total_AP_model != 0:
        power_model_AP = (user_wifi * 1.5 - total_modem_wifi) / total_AP_model
        if power_model_AP > largest_AP['wifi']:
            total_AP_model = math.ceil((user_wifi * 1.5 - total_modem_wifi) / largest_AP['wifi'])

            # check tổng số AP không phải là bội số của tổng số tầng [total_rows_per_floor * (total_floors + 1)]
            if total_AP_model % (total_rows_per_floor * (total_floors + 1)) != 0:
                multiple = total_AP_model // (total_rows_per_floor * (total_floors + 1)) + 1
                total_AP_model = multiple * (total_rows_per_floor * (total_floors + 1)) - total_modem_have_wifi
            largest_AP['quantity'] = 1
            result_access_point_model.append(largest_AP)
        elif power_model_AP <= largest_AP['wifi']:
            closest_greater = None
            for item in access_points:
                if item['wifi'] >= power_model_AP:
                    if closest_greater is None or item['wifi'] < closest_greater['wifi']:
                        item['quantity'] = 1
                        closest_greater = item
            result_access_point_model.append(closest_greater)

    # nếu có phòng họp/ sảnh chờ
    # tính năng lực AP theo phòng khách/sảnh chờ/phòng họp
    if data['otherCheck'] == 1:
        total_AP_other = math.ceil(data['otherLength'] * data['otherWidth'] / other.covered_area)

        if total_AP_other != 0:
            power_other_AP = data['otherUserWifi'] * 1.5 / total_AP_other

            if power_other_AP > largest_AP['wifi']:
                total_AP_other = math.ceil((user_wifi * 1.5) / largest_AP['wifi'])
                largest_AP['quantity'] = 1
                result_access_point_other.append(largest_AP)
            elif power_other_AP <= largest_AP['wifi']:
                closest_greater = None
                for item in access_points:
                    if item['wifi'] >= power_other_AP:
                        if closest_greater is None or item['wifi'] < closest_greater['wifi']:
                            item['quantity'] = 1
                            closest_greater = item
                result_access_point_other.append(closest_greater)

    result['modelTotalAP'] = total_AP_model
    result['otherTotalAP'] = total_AP_other
    result['model'] = result_access_point_model
    result['other'] = result_access_point_other

    return result


def conclusion_calculate_model(net_present, net_result, bandwidth_require,
                               modem_present, modem_result, number_of_devices,
                               ap_present, ap_result,
                               total_ap_present):
    text_status = ['Đảm bảo', 'Không đảm bảo', 'Thiếu thông tin']
    data = Configs.objects.get(config_key='CONCLUSION_MODEL_CALCULATE')
    serializer = ConfigsSerializer(data, many=False)
    list_conclude = serializer.data['configValue']
    status_survey = []
    net_package = InternetPackages.objects.all()
    net_package = InternetPackagesSerializer(net_package, many=True, fields=['name', 'downloadSpeed', 'uploadSpeed'])
    speed_dict = {item['name'].lower(): item['downloadSpeed'] for item in net_package.data}
    # net_package = [dict(item) for item in net_package.data]

    modem_ap_package = Equipments.objects.all()
    modem_ap_package = EquipmentsSerializer(modem_ap_package, many=True, fields=['name', 'LANWifi', 'wifi', 'modemRule',
                                                                                 'quantityWAN', 'wifi24Pow',
                                                                                 'wifi5Pow'])
    modem_lan_wifi_dict = {}
    ap_lan_wifi_dict = {}
    for item in modem_ap_package.data:
        if item['modemRule'].lower() == 'modem':
            modem_lan_wifi_dict[item['name'].lower()] = {
                'LANWifi': item['LANWifi'],
                'wifi': item['wifi'],
                'quantityWAN': item['quantityWAN'],
                'wifi24Pow': item['wifi24Pow'],
                'wifi5Pow': item['wifi5Pow']
            }
        if item['modemRule'].lower() == 'access point':
            ap_lan_wifi_dict[item['name'].lower()] = {
                'LANWifi': item['LANWifi'],
                'wifi': item['wifi'],
                'quantityWAN': item['quantityWAN'],
                'wifi24Pow': item['wifi24Pow'],
                'wifi5Pow': item['wifi5Pow']
            }

    result_conclusion = []
    status_conclusion = text_status[1]
    total_bandwidth_present = 0
    total_power_modem = 0
    total_power_ap = 0

    # so sánh thiếu thông tin hiện trạng

    # so sánh internet_package
    if len(net_present) <= 0:
        result_conclusion.append(list_conclude['5'].format(items='gói cước'))
        status_survey.append(list_conclude['5'])
    else:
        for item in net_present:
            net_name = item.get('name').lower()
            if net_name in speed_dict:
                download_speed = speed_dict[net_name]
                total_bandwidth_present += download_speed * item['quantity']
        if total_bandwidth_present < bandwidth_require:
            items = ''
            for idx in range(len(net_result)):
                if idx == len(net_result) - 1:
                    items += net_result[idx]['name'] + 'x' + str(net_result[idx]['quantity'])
                else:
                    items += net_result[idx]['name'] + 'x' + str(net_result[idx]['quantity']) + ' và '
            result_conclusion.append(list_conclude['1'].format(items=items))

    # so sánh năng lực modem
    if len(modem_result) <= 0:
        result_conclusion.append(list_conclude['8'].format(items='ROUTER'))
        status_survey.append(list_conclude['8'])
    elif len(modem_present) <= 0:
        result_conclusion.append(list_conclude['5'].format(items='modem'))
        status_survey.append(list_conclude['5'])
    else:
        for item in modem_present:
            modem_name = item.get('name').lower()
            if modem_name in modem_lan_wifi_dict:
                lan_wifi = modem_lan_wifi_dict[modem_name]['LANWifi']
                total_power_modem += lan_wifi * item['quantity']
        if total_power_modem > number_of_devices:
            items = ''
            for idx in range(len(modem_result)):
                if idx == len(modem_result) - 1:
                    items += modem_result[idx]['name']
                else:
                    items += modem_result[idx]['name'] + '/'
            result_conclusion.append(list_conclude['2'].format(items=items))

    # so sánh: tổng số AP và loại AP
    if len(ap_result['model']) <= 0:
        pass
    if total_ap_present == 0 and len(ap_present) > 0:
        result_conclusion.append(list_conclude['5'].format(items='số AP'))
        status_survey.append(list_conclude['5'])
    elif len(ap_present) <= 0 < total_ap_present:
        result_conclusion.append(list_conclude['5'].format(items='loại AP'))
        status_survey.append(list_conclude['5'])
    if len(ap_result) > total_ap_present:
        for item in ap_present:
            ap_name = item.get('name').lower()
            if ap_name in ap_lan_wifi_dict:
                lan_wifi = ap_lan_wifi_dict[ap_name]['LANWifi']
                total_power_ap += lan_wifi * item['quantity']
        if number_of_devices > total_power_ap:
            items = ''
            items_other = ''
            for idx in range(len(ap_result['model'])):
                if idx == len(ap_result['model']) - 1:
                    items += ap_result['model'][idx]['name'] + 'x' + str(ap_result['modelTotalAP'])
                else:
                    items += ap_result['model'][idx]['name'] + 'x' + str(ap_result['modelTotalAP']) + '/'

            for idx in range(len(ap_result['other'])):
                if idx == len(ap_result['other']) - 1:
                    items_other += ap_result['other'][idx]['name'] + 'x' + str(ap_result['otherTotalAP'])
                else:
                    items_other += ap_result['other'][idx]['name'] + 'x' + str(ap_result['otherTotalAP']) + '/'

            if items_other != '':
                result_conclusion.append(list_conclude['3'].format(items=items + ' và ' + items_other))
            else:
                result_conclusion.append(list_conclude['3'].format(items=items))

        # so sánh tổng số AP
        if total_ap_present < ap_result['modelTotalAP'] + ap_result['otherTotalAP']:
            result_conclusion.append(
                list_conclude['4'].format(
                    items=(ap_result['modelTotalAP'] + ap_result['otherTotalAP']) - total_ap_present))

    if len(result_conclusion) <= 0:
        result_conclusion.append((list_conclude['0']))
        status_survey.append(list_conclude['0'])

    if len(status_survey) == len(result_conclusion) and list_conclude['0'] in status_survey:
        status_conclusion = text_status[0]
    elif list_conclude['8'] in status_survey or list_conclude['5'] in status_survey:
        status_conclusion = text_status[2]

    result = {
        'conclusion': result_conclusion,
        'status': status_conclusion
    }

    return result
